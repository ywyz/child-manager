from datetime import UTC, datetime, timedelta

import pytest

from packages.backend.identity.tokens import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
)

NOW = datetime(2026, 7, 17, 1, 0, tzinfo=UTC)
SIGNING_KEY = "test-signing-key-that-is-at-least-32-bytes"


def test_access_token_contains_minimal_identity_and_fifteen_minute_expiry() -> None:
    token = create_access_token(
        user_id="user-1",
        kindergarten_id="kg-1",
        token_family_id="family-1",
        signing_key=SIGNING_KEY,
        now=NOW,
    )
    claims = decode_access_token(token, signing_key=SIGNING_KEY, now=NOW)
    assert claims["sub"] == "user-1"
    assert claims["kid"] == "kg-1"
    assert claims["fid"] == "family-1"
    assert claims["exp"] - claims["iat"] == 15 * 60
    assert "roles" not in claims


def test_access_token_expires() -> None:
    token = create_access_token(
        user_id="user-1",
        kindergarten_id="kg-1",
        token_family_id="family-1",
        signing_key=SIGNING_KEY,
        now=NOW,
    )
    with pytest.raises(ValueError, match="过期"):
        decode_access_token(token, signing_key=SIGNING_KEY, now=NOW + timedelta(minutes=16))


def test_refresh_token_is_opaque_random_and_only_strong_hash_is_stored() -> None:
    first = generate_refresh_token()
    second = generate_refresh_token()
    assert first != second
    assert len(first) >= 43
    assert hash_refresh_token(first) != first
    assert hash_refresh_token(first) == hash_refresh_token(first)
