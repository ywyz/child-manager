from dataclasses import dataclass
from importlib import import_module
from typing import Any
from uuid import UUID, uuid4

import pytest


def _modules() -> tuple[Any, Any]:
    try:
        encryption = import_module("packages.backend.integrations.crypto.ai_keys")
        rotation = import_module("packages.backend.settings.ai_key_rotation")
    except ModuleNotFoundError:
        pytest.fail("T076 尚未提供 AI Key 轮换模块", pytrace=False)
    return encryption, rotation


@dataclass
class FakeStore:
    records: list[Any]
    fail_profile_id: UUID | None = None

    def __post_init__(self) -> None:
        self.writes: list[tuple[UUID, Any]] = []

    def scan_for_rotation(
        self,
        *,
        after_profile_id: UUID | None,
        limit: int,
    ) -> list[Any]:
        records = sorted(self.records, key=lambda item: item.profile_id)
        return [
            item
            for item in records
            if after_profile_id is None or item.profile_id > after_profile_id
        ][:limit]

    def replace_envelope(
        self,
        *,
        kindergarten_id: UUID,
        profile_id: UUID,
        expected_key_id: str,
        envelope: Any,
    ) -> bool:
        if profile_id == self.fail_profile_id:
            raise RuntimeError("single row write failed")
        for index, record in enumerate(self.records):
            if (
                record.kindergarten_id == kindergarten_id
                and record.profile_id == profile_id
                and record.envelope.key_id == expected_key_id
            ):
                self.records[index] = record.__class__(
                    kindergarten_id=record.kindergarten_id,
                    profile_id=record.profile_id,
                    envelope=envelope,
                    call_config_revision=record.call_config_revision,
                )
                self.writes.append((profile_id, envelope))
                return True
        return False

    def get_candidate(
        self,
        *,
        kindergarten_id: UUID,
        profile_id: UUID,
    ) -> Any | None:
        return next(
            (
                record
                for record in self.records
                if record.kindergarten_id == kindergarten_id and record.profile_id == profile_id
            ),
            None,
        )


def _candidate(encryption: Any, rotation: Any, profile_id: UUID, key_id: str) -> Any:
    kindergarten_id = uuid4()
    key = b"\x11" * 32 if key_id == "old" else b"\x22" * 32
    envelope = encryption.encrypt_api_key(
        "same-business-key",
        key=key,
        key_id=key_id,
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
        envelope_version=1,
    )
    return rotation.RotationCandidate(
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
        envelope=envelope,
        call_config_revision=7,
    )


def test_rotation_uses_stable_cursor_and_does_not_change_call_revision() -> None:
    encryption, rotation = _modules()
    profile_ids = sorted([uuid4(), uuid4(), uuid4()])
    store = FakeStore([_candidate(encryption, rotation, value, "old") for value in profile_ids])
    provider = encryption.StaticAiKeyProvider(
        {"old": b"\x11" * 32, "new": b"\x22" * 32},
        active_key_id="new",
    )

    first = rotation.rotate_ai_key_batch(
        store,
        key_provider=provider,
        target_key_id="new",
        batch_size=2,
    )
    second = rotation.rotate_ai_key_batch(
        store,
        key_provider=provider,
        target_key_id="new",
        batch_size=2,
        after_profile_id=first.next_cursor,
    )

    assert first.scanned == 2
    assert first.reencrypted == 2
    assert first.next_cursor == profile_ids[1]
    assert second.scanned == 1
    assert second.complete is True
    assert [record.call_config_revision for record in store.records] == [7, 7, 7]
    assert {record.envelope.key_id for record in store.records} == {"new"}


def test_rotation_dry_run_and_repeated_batch_are_zero_write() -> None:
    encryption, rotation = _modules()
    profile_id = uuid4()
    store = FakeStore([_candidate(encryption, rotation, profile_id, "old")])
    provider = encryption.StaticAiKeyProvider(
        {"old": b"\x11" * 32, "new": b"\x22" * 32},
        active_key_id="new",
    )

    dry_run = rotation.rotate_ai_key_batch(
        store,
        key_provider=provider,
        target_key_id="new",
        batch_size=10,
        dry_run=True,
    )
    assert dry_run.reencrypted == 1
    assert store.writes == []
    assert store.records[0].envelope.key_id == "old"

    rotation.rotate_ai_key_batch(
        store,
        key_provider=provider,
        target_key_id="new",
        batch_size=10,
    )
    repeated = rotation.rotate_ai_key_batch(
        store,
        key_provider=provider,
        target_key_id="new",
        batch_size=10,
    )
    assert repeated.reencrypted == 0
    assert len(store.writes) == 1


def test_single_rotation_failure_preserves_old_ciphertext_and_is_reported() -> None:
    encryption, rotation = _modules()
    profile_id = uuid4()
    original = _candidate(encryption, rotation, profile_id, "old")
    store = FakeStore([original], fail_profile_id=profile_id)
    provider = encryption.StaticAiKeyProvider(
        {"old": b"\x11" * 32, "new": b"\x22" * 32},
        active_key_id="new",
    )

    report = rotation.rotate_ai_key_batch(
        store,
        key_provider=provider,
        target_key_id="new",
        batch_size=10,
    )

    assert report.failed == 1
    assert report.complete is False
    assert store.records[0].envelope == original.envelope
    assert store.records[0].call_config_revision == 7


def test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it() -> None:
    encryption, rotation = _modules()
    profile_ids = sorted([uuid4(), uuid4(), uuid4()])
    store = FakeStore(
        [_candidate(encryption, rotation, profile_id, "old") for profile_id in profile_ids],
        fail_profile_id=profile_ids[1],
    )
    provider = encryption.StaticAiKeyProvider(
        {"old": b"\x11" * 32, "new": b"\x22" * 32},
        active_key_id="new",
    )

    report = rotation.rotate_ai_key_batch(
        store,
        key_provider=provider,
        target_key_id="new",
        batch_size=10,
    )

    assert report.failed == 1
    assert report.next_cursor == profile_ids[0]
    assert [profile_id for profile_id, _envelope in store.writes] == [profile_ids[0]]


def test_target_key_record_is_counted_verified_only_after_authenticated_decryption() -> None:
    encryption, rotation = _modules()
    profile_id = uuid4()
    candidate = _candidate(encryption, rotation, profile_id, "new")
    damaged = candidate.__class__(
        kindergarten_id=candidate.kindergarten_id,
        profile_id=candidate.profile_id,
        envelope=candidate.envelope.__class__(
            ciphertext=candidate.envelope.ciphertext[:-1]
            + bytes([candidate.envelope.ciphertext[-1] ^ 1]),
            nonce=candidate.envelope.nonce,
            key_id=candidate.envelope.key_id,
            envelope_version=candidate.envelope.envelope_version,
            last_four=candidate.envelope.last_four,
        ),
        call_config_revision=candidate.call_config_revision,
    )
    provider = encryption.StaticAiKeyProvider(
        {"new": b"\x22" * 32},
        active_key_id="new",
    )

    report = rotation.rotate_ai_key_batch(
        FakeStore([damaged]),
        key_provider=provider,
        target_key_id="new",
        batch_size=10,
    )

    assert report.verified == 0
    assert report.failed == 1
    assert report.complete is False
