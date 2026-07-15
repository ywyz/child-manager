import pytest

from packages.contracts.common import (
    IdempotencyKey,
    canonical_fingerprint,
    idempotency_key_from_fingerprint,
)


def test_idempotency_key_validation():
    data = {
        "key": "user-create-abc123",
        "scope": "user",
    }
    key = IdempotencyKey(**data)
    assert key.key == "user-create-abc123"
    assert key.scope == "user"


def test_idempotency_key_missing_scope():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        IdempotencyKey(key="test-key")


def test_idempotency_key_format():
    valid_keys = [
        "req-abc123",
        "user-create-uuid-1234",
        "plan-save-20240101-class-1",
    ]

    for key_value in valid_keys:
        key = IdempotencyKey(key=key_value, scope="test")
        assert key.key == key_value


def test_canonical_fingerprint_basic():
    fp1 = canonical_fingerprint(path="/api/v1/users", method="POST")
    fp2 = canonical_fingerprint(path="/api/v1/users", method="post")
    assert fp1 == fp2


def test_canonical_fingerprint_different_path():
    fp1 = canonical_fingerprint(path="/api/v1/users", method="POST")
    fp2 = canonical_fingerprint(path="/api/v1/plans", method="POST")
    assert fp1 != fp2


def test_canonical_fingerprint_different_method():
    fp1 = canonical_fingerprint(path="/api/v1/users", method="POST")
    fp2 = canonical_fingerprint(path="/api/v1/users", method="GET")
    assert fp1 != fp2


def test_canonical_fingerprint_query_order_insensitive():
    fp1 = canonical_fingerprint(
        path="/api/v1/users",
        method="GET",
        query_params={"page": 1, "page_size": 20},
    )
    fp2 = canonical_fingerprint(
        path="/api/v1/users",
        method="GET",
        query_params={"page_size": 20, "page": 1},
    )
    assert fp1 == fp2


def test_canonical_fingerprint_body_stable():
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


def test_canonical_fingerprint_scope_matters():
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


def test_canonical_fingerprint_with_list_body():
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


def test_idempotency_key_from_fingerprint():
    fingerprint = "abc123"
    scope = "user"
    key = idempotency_key_from_fingerprint(fingerprint, scope)
    assert key.key == fingerprint
    assert key.scope == scope
