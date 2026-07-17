"""Users 契约测试。"""

from pydantic import BaseModel

from packages.contracts.identity import (
    ResetPasswordRequest,
    UserCreateRequest,
    UserResponse,
)


def _schema_fields(model: type[BaseModel]) -> set[str]:
    return set(model.model_fields)


def test_user_create_request_has_identity_fields() -> None:
    fields = _schema_fields(UserCreateRequest)
    required = {"username", "display_name", "phone", "roles", "initial_password"}
    assert required <= fields


def test_user_response_matches_database_shape() -> None:
    fields = _schema_fields(UserResponse)
    required = {"id", "username", "display_name", "phone", "roles", "is_active"}
    assert required <= fields


def test_reset_password_request_has_new_password() -> None:
    fields = _schema_fields(ResetPasswordRequest)
    assert "new_password" in fields
