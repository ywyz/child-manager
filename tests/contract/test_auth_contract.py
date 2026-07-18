"""Auth 契约测试。"""

import pytest
from pydantic import BaseModel, ValidationError

from packages.contracts.identity import (
    ChangePasswordRequest,
    CsrfResponse,
    CurrentUser,
    KindergartenSnapshot,
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


def test_login_request_rejects_empty_login() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(login="", password="ValidPassword2024!")


def test_login_request_rejects_empty_password() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(login="admin", password="")


def test_login_request_rejects_too_long_login() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(login="a" * 121, password="ValidPassword2024!")


def test_change_password_request_rejects_short_new_password() -> None:
    with pytest.raises(ValidationError):
        ChangePasswordRequest(current_password="ValidPassword2024!", new_password="short")


def test_csrf_response_requires_min_length() -> None:
    with pytest.raises(ValidationError):
        CsrfResponse(csrf_token="short")


def test_csrf_response_rejects_too_long_token() -> None:
    with pytest.raises(ValidationError):
        CsrfResponse(csrf_token="x" * 513)


def test_kindergarten_snapshot_requires_asia_shanghai() -> None:
    with pytest.raises(ValidationError):
        KindergartenSnapshot(
            id="11111111-1111-1111-1111-111111111111",
            name="实验幼儿园",
            timezone="UTC",
        )


def test_current_user_rejects_duplicate_role_codes() -> None:
    with pytest.raises(ValidationError):
        CurrentUser(
            id="11111111-1111-1111-1111-111111111111",
            username="teacher-a",
            display_name="王老师",
            kindergarten=KindergartenSnapshot(
                id="22222222-2222-2222-2222-222222222222",
                name="实验幼儿园",
            ),
            role_codes=["admin", "admin"],
        )


def test_current_user_rejects_unknown_role_codes() -> None:
    with pytest.raises(ValidationError):
        CurrentUser(
            id="11111111-1111-1111-1111-111111111111",
            username="teacher-a",
            display_name="王老师",
            kindergarten=KindergartenSnapshot(
                id="22222222-2222-2222-2222-222222222222",
                name="实验幼儿园",
            ),
            role_codes=["superadmin"],
        )


def test_current_user_rejects_duplicate_capabilities() -> None:
    with pytest.raises(ValidationError):
        CurrentUser(
            id="11111111-1111-1111-1111-111111111111",
            username="teacher-a",
            display_name="王老师",
            kindergarten=KindergartenSnapshot(
                id="22222222-2222-2222-2222-222222222222",
                name="实验幼儿园",
            ),
            capabilities=["read", "read"],
        )
