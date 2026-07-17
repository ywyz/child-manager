"""Auth 契约测试。"""

from pydantic import BaseModel

from packages.contracts.identity import (
    ChangePasswordRequest,
    CurrentUser,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
)


def _schema_fields(model: type[BaseModel]) -> set[str]:
    return set(model.model_fields)


def test_current_user_has_required_fields() -> None:
    fields = _schema_fields(CurrentUser)
    assert {"id", "username", "display_name", "roles"} <= fields


def test_login_request_has_username_and_password() -> None:
    fields = _schema_fields(LoginRequest)
    assert "username" in fields
    assert "password" in fields


def test_login_response_includes_user() -> None:
    fields = _schema_fields(LoginResponse)
    assert "user" in fields


def test_refresh_request_has_token_field() -> None:
    fields = _schema_fields(RefreshRequest)
    assert "refresh_token" in fields


def test_change_password_request_has_both_passwords() -> None:
    fields = _schema_fields(ChangePasswordRequest)
    assert "old_password" in fields
    assert "new_password" in fields
