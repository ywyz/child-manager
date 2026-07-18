"""Auth 契约测试。"""

from pydantic import BaseModel

from packages.contracts.identity import (
    ChangePasswordRequest,
    CurrentUser,
    LoginRequest,
)


def _schema_fields(model: type[BaseModel]) -> set[str]:
    return set(model.model_fields)


def test_current_user_has_required_fields() -> None:
    fields = _schema_fields(CurrentUser)
    assert {
        "id",
        "username",
        "display_name",
        "kindergarten",
        "role_codes",
        "capabilities",
    } <= fields


def test_login_request_has_login_and_password() -> None:
    fields = _schema_fields(LoginRequest)
    assert "login" in fields
    assert "password" in fields


def test_login_response_is_current_user() -> None:
    """登录直接返回 CurrentUser，不再嵌套在 LoginResponse 中。"""
    fields = _schema_fields(CurrentUser)
    assert "kindergarten" in fields
    assert "role_codes" in fields


def test_change_password_request_has_both_passwords() -> None:
    fields = _schema_fields(ChangePasswordRequest)
    assert "current_password" in fields
    assert "new_password" in fields
