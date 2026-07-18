"""Users 契约测试。"""

import pytest
from pydantic import BaseModel, ValidationError

from packages.contracts.identity import (
    ResetPasswordRequest,
    UserCreateRequest,
    UserPatch,
    UserResponse,
)


def _schema_fields(model: type[BaseModel]) -> set[str]:
    return set(model.model_fields)


def test_user_create_request_has_identity_fields() -> None:
    fields = _schema_fields(UserCreateRequest)
    required = {"username", "display_name", "phone_e164", "role_codes", "password"}
    assert required <= fields


def test_user_response_matches_database_shape() -> None:
    fields = _schema_fields(UserResponse)
    required = {
        "id",
        "username",
        "display_name",
        "phone_e164",
        "role_codes",
        "is_active",
        "created_at",
        "updated_at",
    }
    assert required <= fields


def test_reset_password_request_has_new_password() -> None:
    fields = _schema_fields(ResetPasswordRequest)
    assert "new_password" in fields


def test_user_create_request_requires_at_least_one_role() -> None:
    with pytest.raises(ValidationError):
        UserCreateRequest(
            username="teacher",
            display_name="教师",
            phone_e164=None,
            password="ValidPassword2024!",
            role_codes=[],
        )


def test_user_create_request_rejects_unknown_roles() -> None:
    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate(
            {
                "username": "teacher",
                "display_name": "教师",
                "phone_e164": None,
                "password": "ValidPassword2024!",
                "role_codes": ["admin", "unknown"],
            }
        )


def test_user_create_request_rejects_duplicate_roles() -> None:
    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate(
            {
                "username": "teacher",
                "display_name": "教师",
                "phone_e164": None,
                "password": "ValidPassword2024!",
                "role_codes": ["admin", "admin"],
            }
        )


def test_user_patch_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError):
        UserPatch.model_validate({})


def test_user_patch_accepts_phone_e164_null() -> None:
    patch = UserPatch(phone_e164=None)
    assert patch.phone_e164 is None
    assert patch.phone_e164_is_set is True


def test_user_patch_rejects_username_null() -> None:
    with pytest.raises(ValidationError):
        UserPatch.model_validate({"username": None})


def test_user_patch_rejects_display_name_null() -> None:
    with pytest.raises(ValidationError):
        UserPatch.model_validate({"display_name": None})


def test_user_create_request_requires_role_codes() -> None:
    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate(
            {
                "username": "teacher",
                "display_name": "教师",
                "phone_e164": None,
                "password": "ValidPassword2024!",
            }
        )


def test_user_create_request_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        UserCreateRequest(
            username="teacher",
            display_name="教师",
            phone_e164=None,
            password="short",
            role_codes=["teacher"],
        )


def test_reset_password_request_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        ResetPasswordRequest(new_password="short")


def test_user_response_rejects_duplicate_role_codes() -> None:
    from datetime import UTC, datetime

    with pytest.raises(ValidationError):
        UserResponse(
            id="11111111-1111-1111-1111-111111111111",
            username="teacher",
            display_name="教师",
            phone_e164=None,
            role_codes=["teacher", "teacher"],
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )


def test_user_response_rejects_unknown_role_codes() -> None:
    from datetime import UTC, datetime

    with pytest.raises(ValidationError):
        UserResponse(
            id="11111111-1111-1111-1111-111111111111",
            username="teacher",
            display_name="教师",
            phone_e164=None,
            role_codes=["superadmin"],
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
