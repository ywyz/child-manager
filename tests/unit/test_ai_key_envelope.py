from dataclasses import replace
from importlib import import_module
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from cryptography.exceptions import InvalidTag


def _module() -> Any:
    try:
        return import_module("packages.backend.integrations.crypto.ai_keys")
    except ModuleNotFoundError:
        pytest.fail("T076 尚未提供 AI Key envelope 模块", pytrace=False)


def test_ai_key_envelope_round_trips_with_random_96_bit_nonce() -> None:
    module = _module()
    key = bytes(range(32))
    kindergarten_id = uuid4()
    profile_id = uuid4()

    first = module.encrypt_api_key(
        "sk-test-secret",
        key=key,
        key_id="key-v1",
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
        envelope_version=1,
    )
    second = module.encrypt_api_key(
        "sk-test-secret",
        key=key,
        key_id="key-v1",
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
        envelope_version=1,
    )

    assert len(first.nonce) == 12
    assert first.nonce != second.nonce
    assert first.ciphertext != second.ciphertext
    assert first.last_four == "cret"
    assert (
        module.decrypt_api_key(
            first,
            key=key,
            kindergarten_id=kindergarten_id,
            profile_id=profile_id,
            envelope_version=1,
        )
        == "sk-test-secret"
    )


def test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution() -> None:
    module = _module()
    key = bytes(reversed(range(32)))
    kindergarten_id = uuid4()
    profile_id = uuid4()
    envelope = module.encrypt_api_key(
        "replace-me",
        key=key,
        key_id="key-v1",
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
        envelope_version=1,
    )

    with pytest.raises(InvalidTag):
        module.decrypt_api_key(
            replace(envelope, ciphertext=envelope.ciphertext[:-1] + b"\x00"),
            key=key,
            kindergarten_id=kindergarten_id,
            profile_id=profile_id,
            envelope_version=1,
        )
    with pytest.raises(InvalidTag):
        module.decrypt_api_key(
            envelope,
            key=key,
            kindergarten_id=kindergarten_id,
            profile_id=uuid4(),
            envelope_version=1,
        )
    with pytest.raises(InvalidTag):
        module.decrypt_api_key(
            envelope,
            key=key,
            kindergarten_id=uuid4(),
            profile_id=profile_id,
            envelope_version=1,
        )


def test_static_key_provider_reads_old_key_but_writes_with_active_key() -> None:
    module = _module()
    provider = module.StaticAiKeyProvider(
        {"old": b"\x11" * 32, "new": b"\x22" * 32},
        active_key_id="new",
    )
    kindergarten_id = uuid4()
    profile_id = uuid4()
    old = module.encrypt_api_key(
        "same-secret",
        key=b"\x11" * 32,
        key_id="old",
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
        envelope_version=1,
    )

    assert provider.active_key() == ("new", b"\x22" * 32)
    assert (
        module.decrypt_api_key_with_provider(
            old,
            key_provider=provider,
            kindergarten_id=kindergarten_id,
            profile_id=profile_id,
        )
        == "same-secret"
    )
    current = module.encrypt_api_key_with_provider(
        "same-secret",
        key_provider=provider,
        kindergarten_id=kindergarten_id,
        profile_id=profile_id,
    )
    assert current.key_id == "new"


def test_file_key_provider_requires_owner_only_files_outside_repository(tmp_path: Path) -> None:
    module = _module()
    key_path = tmp_path / "ai.key"
    key_path.write_bytes(b"\x23" * 32)
    key_path.chmod(0o600)
    provider = module.FileAiKeyProvider(
        {"current": key_path},
        active_key_id="current",
        repository_root=Path.cwd(),
    )

    assert provider.active_key() == ("current", b"\x23" * 32)
    key_path.chmod(0o640)
    with pytest.raises(PermissionError):
        provider.get_key("current")
    with pytest.raises(ValueError):
        module.FileAiKeyProvider(
            {"current": Path("pyproject.toml")},
            active_key_id="current",
            repository_root=Path.cwd(),
        )
