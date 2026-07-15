import pytest

from packages.contracts.common import (
    IdempotencyKey,
    canonical_fingerprint,
    idempotency_key_from_fingerprint,
)


def test_idempotency_key_validation() -> None:
    data = {
        "key": "user-create-abc123",
        "scope": "user",
    }
    key = IdempotencyKey(**data)
    assert key.key == "user-create-abc123"
    assert key.scope == "user"


def test_idempotency_key_missing_scope() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        IdempotencyKey(key="test-key")  # pyright: ignore[reportCallIssue]


def test_idempotency_key_format() -> None:
    valid_keys = [
        "req-abc123",
        "user-create-uuid-1234",
        "plan-save-20240101-class-1",
    ]

    for key_value in valid_keys:
        key = IdempotencyKey(key=key_value, scope="test")
        assert key.key == key_value


def test_canonical_fingerprint_basic() -> None:
    fp1 = canonical_fingerprint(path="/api/v1/users", method="POST")
    fp2 = canonical_fingerprint(path="/api/v1/users", method="post")
    assert fp1 == fp2


def test_canonical_fingerprint_different_path() -> None:
    fp1 = canonical_fingerprint(path="/api/v1/users", method="POST")
    fp2 = canonical_fingerprint(path="/api/v1/plans", method="POST")
    assert fp1 != fp2


def test_canonical_fingerprint_different_method() -> None:
    fp1 = canonical_fingerprint(path="/api/v1/users", method="POST")
    fp2 = canonical_fingerprint(path="/api/v1/users", method="GET")
    assert fp1 != fp2


def test_canonical_fingerprint_query_order_insensitive() -> None:
    fp1 = canonical_fingerprint(
        path="/api/v1/users",
        method="GET",
        query_params=[("page", "1"), ("page_size", "20")],
    )
    fp2 = canonical_fingerprint(
        path="/api/v1/users",
        method="GET",
        query_params=[("page_size", "20"), ("page", "1")],
    )
    assert fp1 == fp2


def test_canonical_fingerprint_body_stable() -> None:
    body1 = {"name": "test", "value": 123}
    body2 = {"value": 123, "name": "test"}
    fp1 = canonical_fingerprint(
        path="/api/v1/users",
        method="POST",
        body=body1,
    )
    fp2 = canonical_fingerprint(
        path="/api/v1/users",
        method="POST",
        body=body2,
    )
    assert fp1 == fp2


def test_canonical_fingerprint_scope_matters() -> None:
    fp1 = canonical_fingerprint(
        path="/api/v1/users",
        method="POST",
        scope="kindergarten-1",
    )
    fp2 = canonical_fingerprint(
        path="/api/v1/users",
        method="POST",
        scope="kindergarten-2",
    )
    assert fp1 != fp2


def test_canonical_fingerprint_with_list_body() -> None:
    body1 = [1, 2, 3]
    body2 = [1, 2, 3]
    fp1 = canonical_fingerprint(
        path="/api/v1/batch",
        method="POST",
        body=body1,
    )
    fp2 = canonical_fingerprint(
        path="/api/v1/batch",
        method="POST",
        body=body2,
    )
    assert fp1 == fp2


def test_idempotency_key_from_fingerprint() -> None:
    fingerprint = "abc123"
    scope = "user"
    key = idempotency_key_from_fingerprint(fingerprint, scope)
    assert key.key == fingerprint
    assert key.scope == scope


def test_idempotency_key_max_length_200() -> None:
    """幂等键最长 200 字符，201 字符必须拒绝。"""
    from pydantic import ValidationError

    key_200 = "a" * 200
    assert IdempotencyKey(key=key_200, scope="s").key == key_200

    key_201 = "a" * 201
    with pytest.raises(ValidationError):
        IdempotencyKey(key=key_201, scope="s")


def test_idempotency_key_rejects_empty_string() -> None:
    """幂等键最小长度为 1，空字符串必须拒绝。"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        IdempotencyKey(key="", scope="s")


def test_canonical_fingerprint_duplicate_query_values() -> None:
    """重复 query 参数按 (name, value) 元组排序。"""
    fp1 = canonical_fingerprint(
        path="/api/v1/search",
        method="GET",
        query_params=[("tag", "a"), ("tag", "b")],
    )
    fp2 = canonical_fingerprint(
        path="/api/v1/search",
        method="GET",
        query_params=[("tag", "b"), ("tag", "a")],
    )
    # 相同 (name, value) 对，顺序不同，排序后应一致
    assert fp1 == fp2

    fp3 = canonical_fingerprint(
        path="/api/v1/search",
        method="GET",
        query_params=[("tag", "a"), ("tag", "c")],
    )
    # 值不同，指纹应不同
    assert fp1 != fp3
