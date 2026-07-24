from __future__ import annotations

import base64
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from packages.backend.identity.secret_encryption import (
    StaticIdentitySecretKeyProvider,
    TotpSecretEnvelope,
    decrypt_totp_secret_with_provider,
)


class _Transaction:
    def __enter__(self) -> _Transaction:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


class _Connection(_Transaction):
    def transaction(self) -> _Transaction:
        return _Transaction()


def test_service_generates_persisted_enrollment_id_before_encrypting_totp_aad(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service_module = __import__(
        "packages.backend.identity.service",
        fromlist=["IdentityService"],
    )
    kindergarten_id = uuid4()
    user_id = uuid4()
    session_id = uuid4()
    persisted: dict[str, object] = {}
    provider = StaticIdentitySecretKeyProvider(
        {"test-key": b"\x19" * 32},
        active_key_id="test-key",
    )

    class RecordingRepository:
        def __init__(self, _connection: object, scoped_kindergarten_id: UUID) -> None:
            assert scoped_kindergarten_id == kindergarten_id
            self.kindergarten_id = scoped_kindergarten_id

        def start_backup_enrollment(
            self,
            *,
            enrollment_id: UUID,
            user_id: UUID,
            session_token_id: UUID,
            totp_ciphertext: bytes,
            totp_nonce: bytes,
            totp_key_id: str,
            totp_envelope_version: int,
            expires_at: datetime,
        ) -> SimpleNamespace:
            persisted.update(
                enrollment_id=enrollment_id,
                user_id=user_id,
                session_token_id=session_token_id,
                expires_at=expires_at,
            )
            envelope = TotpSecretEnvelope(
                ciphertext=totp_ciphertext,
                nonce=totp_nonce,
                key_id=totp_key_id,
                envelope_version=totp_envelope_version,
            )
            persisted["secret_bytes"] = decrypt_totp_secret_with_provider(
                envelope,
                key_provider=provider,
                kindergarten_id=kindergarten_id,
                user_id=user_id,
                subject_id=enrollment_id,
                subject_kind="enrollment",
            )
            return SimpleNamespace(id=enrollment_id, expires_at=expires_at)

        def get_family_session(
            self,
            scoped_user_id: UUID,
            family_id: UUID,
        ) -> SimpleNamespace:
            assert scoped_user_id == user_id
            assert family_id == session_id
            return SimpleNamespace(
                id=session_id,
                revoked_at=None,
                expires_at=datetime.max.replace(tzinfo=UTC),
            )

    monkeypatch.setattr(service_module, "IdentityRepository", RecordingRepository)
    service = service_module.IdentityService(
        database_url="postgresql+psycopg://unused",
        jwt_signing_key="test-jwt-signing-key-that-is-long",
        rp_id="testserver",
        rp_name="Child Manager Tests",
        identity_secret_key_provider=provider,
    )
    monkeypatch.setattr(service, "_connect", _Connection)
    session = SimpleNamespace(
        user=SimpleNamespace(
            id=user_id,
            kindergarten_id=kindergarten_id,
            username="admin",
            display_name="测试管理员",
        ),
        role_codes=["admin"],
        token_family_id=session_id,
        session_id=session_id,
        authentication_method="restricted_enrollment",
        webauthn_verified_at=datetime.now(UTC),
    )

    started_at = datetime.now(UTC)
    result = service.start_backup_enrollment(session)

    assert isinstance(result.enrollment_id, UUID)
    assert persisted["enrollment_id"] == result.enrollment_id
    assert persisted["user_id"] == user_id
    assert persisted["session_token_id"] == session_id
    assert persisted["secret_bytes"] == base64.b32decode(result.totp_secret)
    assert 599 <= (result.expires_at - started_at).total_seconds() <= 601
