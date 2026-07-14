import pytest

from packages.contracts.common import IdempotencyKey


def test_idempotency_key_validation():
    """IdempotencyKey 应该正确验证字段"""
    data = {
        "key": "user-create-abc123",
        "scope": "user",
    }
    key = IdempotencyKey(**data)
    assert key.key == "user-create-abc123"
    assert key.scope == "user"


def test_idempotency_key_missing_scope():
    """IdempotencyKey 缺少 scope 字段应该失败"""
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        IdempotencyKey(key="test-key")


def test_idempotency_key_format():
    """IdempotencyKey 的 key 应该有合理格式"""
    valid_keys = [
        "req-abc123",
        "user-create-uuid-1234",
        "plan-save-20240101-class-1",
    ]
    
    for key_value in valid_keys:
        key = IdempotencyKey(key=key_value, scope="test")
        assert key.key == key_value