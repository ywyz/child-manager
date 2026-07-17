"""密码政策与 Argon2id 哈希测试。"""

import pytest

from packages.backend.identity.passwords import hash_password, validate_password, verify_password


@pytest.mark.parametrize(
    "password",
    [
        "a" * 15,
        "A" * 128,
        "Short!2024#LongEnough",
    ],
)
def test_valid_password_length(password: str) -> None:
    validate_password(password)


@pytest.mark.parametrize(
    "password",
    [
        "a" * 14,
        "A" * 129,
        "short",
    ],
)
def test_invalid_password_length(password: str) -> None:
    with pytest.raises(ValueError):
        validate_password(password)


def test_hash_and_verify_roundtrip() -> None:
    password = "ValidPassword2024!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_hash_is_argon2id_format() -> None:
    hashed = hash_password("ValidPassword2024!")
    assert hashed.startswith("$argon2id$")


def test_weak_password_is_rejected() -> None:
    with pytest.raises(ValueError):
        validate_password("password")


def test_non_common_password_is_accepted() -> None:
    validate_password("ValidPassword2024!")
