"""Access JWT 与 opaque Refresh 令牌测试。"""

import time
from uuid import uuid4

import pytest

from packages.backend.identity.tokens import (
    create_access_token,
    decode_access_token,
    generate_refresh_value,
    hash_refresh_value,
    parse_refresh_kindergarten_id,
)


@pytest.fixture
def signing_key() -> str:
    return "test-signing-key-" + uuid4().hex


def test_access_token_roundtrip(signing_key: str) -> None:
    token = create_access_token(
        user_id="user-1",
        kindergarten_id="kg-1",
        roles=["admin"],
        family_id=str(uuid4()),
        signing_key=signing_key,
        expire_minutes=5,
    )
    assert token
    payload = decode_access_token(token, signing_key)
    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["kindergarten_id"] == "kg-1"
    assert payload["roles"] == ["admin"]
    assert "family_id" in payload
    assert "jti" in payload
    assert "exp" in payload


def test_decode_access_token_rejects_invalid_signature(signing_key: str) -> None:
    token = create_access_token(
        user_id="user-1",
        kindergarten_id="kg-1",
        roles=["admin"],
        family_id=str(uuid4()),
        signing_key=signing_key,
    )
    assert decode_access_token(token, "wrong-key") is None


def test_decode_access_token_rejects_expired(signing_key: str) -> None:
    token = create_access_token(
        user_id="user-1",
        kindergarten_id="kg-1",
        roles=["admin"],
        family_id=str(uuid4()),
        signing_key=signing_key,
        expire_minutes=-1,
    )
    time.sleep(0.01)
    assert decode_access_token(token, signing_key) is None


def test_decode_access_token_rejects_malformed(signing_key: str) -> None:
    """非 JWT 字符串、空串、None、段数错误均稳定返回 None，不抛异常。"""
    assert decode_access_token("not-a-jwt", signing_key) is None
    assert decode_access_token("", signing_key) is None
    assert decode_access_token("a.b", signing_key) is None
    assert decode_access_token("a.b.c.d", signing_key) is None


def test_refresh_value_is_random_and_hashed() -> None:
    value1 = generate_refresh_value(kindergarten_id="kg-1")
    value2 = generate_refresh_value(kindergarten_id="kg-1")
    assert value1 != value2
    assert len(value1) >= 32
    hashed = hash_refresh_value(value1)
    assert hashed != value1
    assert hash_refresh_value(value1) == hashed


def test_parse_refresh_kindergarten_id_extracts_uuid() -> None:
    """合法 UUID 园所前缀的 Refresh 明文能正确解析。"""
    kg_id = "00000000-0000-7000-8000-000000000001"
    value = f"kg:{kg_id}:somerandomtoken"
    assert parse_refresh_kindergarten_id(value) == kg_id


def test_parse_refresh_kindergarten_id_rejects_non_uuid_prefix() -> None:
    """带 kg: 前缀但园所 ID 非 UUID 必须返回 None，避免 PostgreSQL DataError。

    父 Issue #4 要求对无效 Refresh 稳定拒绝为未认证结果，不得进入数据库
    类型错误。`kg:not-a-uuid:*` 必须在 token 边界被拒绝。
    """
    assert parse_refresh_kindergarten_id("kg:not-a-uuid:anything") is None
    assert parse_refresh_kindergarten_id("kg:abc:anything") is None
    assert parse_refresh_kindergarten_id("kg:12345:anything") is None
    # UUID 大小写混合不合法（应用层生成的是小写 uuid7）
    assert parse_refresh_kindergarten_id("kg:ABCDEF00-0000-7000-8000-000000000001:x") is None


def test_parse_refresh_kindergarten_id_rejects_malformed() -> None:
    """缺前缀、缺段、空串等 malformed 输入均返回 None。"""
    assert parse_refresh_kindergarten_id("not-a-refresh") is None
    assert parse_refresh_kindergarten_id("") is None
    assert parse_refresh_kindergarten_id("kg:") is None
    assert parse_refresh_kindergarten_id("kg:abc") is None
    # 前缀不匹配
    assert parse_refresh_kindergarten_id("kgr:abc:def") is None
