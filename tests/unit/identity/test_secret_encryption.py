from dataclasses import replace
from importlib import import_module
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from cryptography.exceptions import InvalidTag


def _encryption_module() -> Any:
    return import_module("packages.backend.identity.secret_encryption")


def _context() -> dict[str, object]:
    return {
        "kindergarten_id": uuid4(),
        "user_id": uuid4(),
        "subject_id": uuid4(),
        "subject_kind": "enrollment",
        "envelope_version": 1,
    }


def test_totp_secret_envelope_round_trips_with_random_96_bit_nonce() -> None:
    module = _encryption_module()
    key = bytes(range(32))
    context = _context()

    first = module.encrypt_totp_secret(
        bytes(range(20)),
        key=key,
        key_id="test-key",
        **context,
    )
    second = module.encrypt_totp_secret(
        bytes(range(20)),
        key=key,
        key_id="test-key",
        **context,
    )

    assert len(first.nonce) == 12
    assert first.nonce != second.nonce
    assert first.ciphertext != second.ciphertext
    assert module.decrypt_totp_secret(first, key=key, **context) == bytes(range(20))


def test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution() -> None:
    module = _encryption_module()
    key = bytes(reversed(range(32)))
    context = _context()
    envelope = module.encrypt_totp_secret(
        bytes(range(20)),
        key=key,
        key_id="test-key",
        **context,
    )

    with pytest.raises(InvalidTag):
        module.decrypt_totp_secret(
            replace(envelope, ciphertext=envelope.ciphertext[:-1] + b"\x00"),
            key=key,
            **context,
        )
    with pytest.raises(InvalidTag):
        module.decrypt_totp_secret(
            envelope,
            key=key,
            **{**context, "user_id": uuid4()},
        )


def test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce() -> None:
    module = _encryption_module()
    provider = module.StaticIdentitySecretKeyProvider(
        {"current": bytes(range(32))},
        active_key_id="current",
    )
    kindergarten_id = uuid4()
    user_id = uuid4()
    enrollment_id = uuid4()
    credential_id = uuid4()
    enrollment = module.encrypt_totp_secret_with_provider(
        bytes(range(20)),
        key_provider=provider,
        kindergarten_id=kindergarten_id,
        user_id=user_id,
        subject_id=enrollment_id,
        subject_kind="enrollment",
    )

    credential = module.rebind_totp_secret_with_provider(
        enrollment,
        key_provider=provider,
        kindergarten_id=kindergarten_id,
        user_id=user_id,
        enrollment_id=enrollment_id,
        credential_id=credential_id,
    )

    assert credential.nonce != enrollment.nonce
    assert credential.ciphertext != enrollment.ciphertext
    assert module.decrypt_totp_secret_with_provider(
        credential,
        key_provider=provider,
        kindergarten_id=kindergarten_id,
        user_id=user_id,
        subject_id=credential_id,
        subject_kind="credential",
    ) == bytes(range(20))
    with pytest.raises(InvalidTag):
        module.decrypt_totp_secret_with_provider(
            credential,
            key_provider=provider,
            kindergarten_id=kindergarten_id,
            user_id=user_id,
            subject_id=enrollment_id,
            subject_kind="enrollment",
        )


def test_development_key_provider_requires_owner_only_file_outside_repository(
    tmp_path: Path,
) -> None:
    module = _encryption_module()
    key_path = tmp_path / "identity.key"
    key_path.write_bytes(bytes(range(32)))
    key_path.chmod(0o600)
    provider = module.FileIdentitySecretKeyProvider(
        {"current": key_path},
        active_key_id="current",
        repository_root=Path.cwd(),
    )

    assert provider.active_key() == ("current", bytes(range(32)))

    key_path.chmod(0o640)
    with pytest.raises(PermissionError):
        provider.get_key("current")

    with pytest.raises(ValueError):
        module.FileIdentitySecretKeyProvider(
            {"current": Path("pyproject.toml")},
            active_key_id="current",
            repository_root=Path.cwd(),
        )
