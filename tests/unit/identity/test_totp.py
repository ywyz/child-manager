from base64 import b32decode, b32encode
from importlib import import_module
from typing import Any


def _totp_module() -> Any:
    return import_module("packages.backend.identity.totp")


def test_totp_secret_is_unique_high_entropy_base32() -> None:
    module = _totp_module()

    first = module.generate_totp_secret()
    second = module.generate_totp_secret()

    assert first != second
    assert len(b32decode(first)) == 20
    assert len(b32decode(second)) == 20


def test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps() -> None:
    module = _totp_module()
    secret = b32encode(b"12345678901234567890").decode("ascii")
    current = module.generate_totp(secret, timestamp=59)

    assert current == "287082"
    assert module.candidate_totp_counters(timestamp=59) == (0, 1, 2)
    assert module.verify_totp(secret, current, timestamp=59, last_accepted_counter=None) == 1


def test_totp_rejects_the_same_or_earlier_counter_after_success() -> None:
    module = _totp_module()
    secret = b32encode(bytes(range(20))).decode("ascii")
    code = module.generate_totp(secret, timestamp=90)

    accepted = module.verify_totp(
        secret,
        code,
        timestamp=90,
        last_accepted_counter=None,
    )

    assert accepted == 3
    assert (
        module.verify_totp(
            secret,
            code,
            timestamp=90,
            last_accepted_counter=accepted,
        )
        is None
    )
