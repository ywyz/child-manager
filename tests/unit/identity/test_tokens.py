"""Access JWT 与 opaque Refresh 令牌测试。"""

import time
from uuid import uuid4

import pytest

from packages.backend.identity.tokens import (
    create_access_token,
    decode_access_token,
    generate_refresh_value,
    hash_refresh_value,
)


@pytest.fixture
def signing_key() -> str:
    return "test-signing-key-" + uuid4().hex


def test_access_token_roundtrip(signing_key: str) -> None:
    token = create_access_token(
        user_id="user-1",
        kindergarten_id="kg-1",
        roles=["admin"],
        signing_key=signing_key,
        expire_minutes=5,
    )
    assert token
    payload = decode_access_token(token, signing_key)
    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["kindergarten_id"] == "kg-1"
    assert payload["roles"] == ["admin"]
    assert "jti" in payload
    assert "exp" in payload


def test_decode_access_token_rejects_invalid_signature(signing_key: str) -> None:
    token = create_access_token(
        user_id="user-1",
        kindergarten_id="kg-1",
        roles=["admin"],
        signing_key=signing_key,
    )
    assert decode_access_token(token, "wrong-key") is None


def test_decode_access_token_rejects_expired(signing_key: str) -> None:
    token = create_access_token(
        user_id="user-1",
        kindergarten_id="kg-1",
        roles=["admin"],
        signing_key=signing_key,
        expire_minutes=-1,
    )
    time.sleep(0.01)
    assert decode_access_token(token, signing_key) is None


def test_refresh_value_is_random_and_hashed() -> None:
    value1 = generate_refresh_value(kindergarten_id="kg-1")
    value2 = generate_refresh_value(kindergarten_id="kg-1")
    assert value1 != value2
    assert len(value1) >= 32
    hashed = hash_refresh_value(value1)
    assert hashed != value1
    assert hash_refresh_value(value1) == hashed
