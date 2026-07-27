"""稳定游标、可恢复且不改变业务 revision 的 AI Key 轮换。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

import psycopg

from packages.backend.integrations.crypto.ai_keys import (
    AiKeyEnvelope,
    FileAiKeyProvider,
    StaticAiKeyProvider,
    decrypt_api_key_with_provider,
    encrypt_api_key,
)


@dataclass(frozen=True, slots=True)
class RotationCandidate:
    kindergarten_id: UUID
    profile_id: UUID
    envelope: AiKeyEnvelope
    call_config_revision: int


class AiKeyRotationStore(Protocol):
    def scan_for_rotation(
        self,
        *,
        after_profile_id: UUID | None,
        limit: int,
    ) -> list[RotationCandidate]: ...

    def replace_envelope(
        self,
        *,
        kindergarten_id: UUID,
        profile_id: UUID,
        expected_key_id: str,
        envelope: AiKeyEnvelope,
    ) -> bool: ...


@dataclass(frozen=True, slots=True)
class RotationReport:
    scanned: int
    reencrypted: int
    verified: int
    failed: int
    next_cursor: UUID | None
    complete: bool
    dry_run: bool


class PostgresAiKeyRotationStore:
    """维护 CLI 使用的跨园扫描；每条写入仍同时绑定园所与档案 ID。"""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    def scan_for_rotation(
        self,
        *,
        after_profile_id: UUID | None,
        limit: int,
    ) -> list[RotationCandidate]:
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute(
                """SELECT kindergarten_id,id,api_key_ciphertext,api_key_nonce,
                api_key_key_id,api_key_encryption_version,api_key_last_four,
                call_config_revision
                FROM ai_model_profiles
                WHERE api_key_ciphertext IS NOT NULL AND (%s::uuid IS NULL OR id>%s)
                ORDER BY id LIMIT %s""",
                (after_profile_id, after_profile_id, limit),
            ).fetchall()
        return [
            RotationCandidate(
                kindergarten_id=UUID(str(row[0])),
                profile_id=UUID(str(row[1])),
                envelope=AiKeyEnvelope(
                    ciphertext=bytes(row[2]),
                    nonce=bytes(row[3]),
                    key_id=str(row[4]),
                    envelope_version=int(row[5]),
                    last_four=str(row[6]),
                ),
                call_config_revision=int(row[7]),
            )
            for row in rows
        ]

    def replace_envelope(
        self,
        *,
        kindergarten_id: UUID,
        profile_id: UUID,
        expected_key_id: str,
        envelope: AiKeyEnvelope,
    ) -> bool:
        with psycopg.connect(self.database_url) as connection, connection.transaction():
            result = connection.execute(
                """UPDATE ai_model_profiles SET
                api_key_ciphertext=%s,api_key_nonce=%s,api_key_key_id=%s,
                api_key_encryption_version=%s,api_key_last_four=%s,updated_at=now()
                WHERE kindergarten_id=%s AND id=%s AND api_key_key_id=%s""",
                (
                    envelope.ciphertext,
                    envelope.nonce,
                    envelope.key_id,
                    envelope.envelope_version,
                    envelope.last_four,
                    kindergarten_id,
                    profile_id,
                    expected_key_id,
                ),
            )
            return result.rowcount == 1


def rotate_ai_key_batch(
    store: AiKeyRotationStore,
    *,
    key_provider: StaticAiKeyProvider | FileAiKeyProvider,
    target_key_id: str,
    batch_size: int,
    after_profile_id: UUID | None = None,
    dry_run: bool = False,
) -> RotationReport:
    if batch_size < 1:
        raise ValueError("批量大小必须大于零")
    target_key = key_provider.get_key(target_key_id)
    candidates = store.scan_for_rotation(after_profile_id=after_profile_id, limit=batch_size)
    reencrypted = verified = failed = 0
    scanned = 0
    next_cursor = after_profile_id
    for candidate in candidates:
        scanned += 1
        if candidate.envelope.key_id == target_key_id:
            verified += 1
            next_cursor = candidate.profile_id
            continue
        try:
            plaintext = decrypt_api_key_with_provider(
                candidate.envelope,
                key_provider=key_provider,
                kindergarten_id=candidate.kindergarten_id,
                profile_id=candidate.profile_id,
            )
            replacement = encrypt_api_key(
                plaintext,
                key=target_key,
                key_id=target_key_id,
                kindergarten_id=candidate.kindergarten_id,
                profile_id=candidate.profile_id,
                envelope_version=candidate.envelope.envelope_version,
            )
            if not dry_run and not store.replace_envelope(
                kindergarten_id=candidate.kindergarten_id,
                profile_id=candidate.profile_id,
                expected_key_id=candidate.envelope.key_id,
                envelope=replacement,
            ):
                failed += 1
                break
            reencrypted += 1
            verified += 1
            next_cursor = candidate.profile_id
        except Exception:
            failed += 1
            break
    complete = len(candidates) < batch_size and failed == 0
    return RotationReport(
        scanned=scanned,
        reencrypted=reencrypted,
        verified=verified,
        failed=failed,
        next_cursor=next_cursor,
        complete=complete,
        dry_run=dry_run,
    )
