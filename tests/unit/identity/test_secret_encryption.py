from dataclasses import replace
from importlib import import_module
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
