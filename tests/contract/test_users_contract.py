from datetime import UTC, datetime
from uuid import uuid4

import pytest

from packages.contracts.identity import (
    CreateUserRequest,
    RoleUpdate,
    UserPage,
    UserPatch,
    UserResponse,
)


def test_create_user_contract_never_accepts_kindergarten_or_password_response() -> None:
    with pytest.raises(ValueError):
        CreateUserRequest.model_validate(
            {
                "username": "teacher",
                "display_name": "教师",
                "password": "足够长的安全密码 2026",
                "role_codes": ["teacher"],
                "kindergarten_id": str(uuid4()),
            }
        )
    assert "password" not in UserResponse.model_fields


def test_user_page_uses_bounded_standard_envelope() -> None:
    now = datetime.now(UTC)
    user = UserResponse(
        id=uuid4(),
        username="teacher",
        phone_e164=None,
        display_name="教师",
        role_codes=["teacher"],
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    page = UserPage(items=[user], page=1, page_size=20, total=1)
    assert page.model_dump()["page_size"] == 20
    with pytest.raises(ValueError):
        UserPage(items=[], page=1, page_size=101, total=0)


def test_user_write_models_match_openapi_non_empty_and_unique_constraints() -> None:
    with pytest.raises(ValueError):
        CreateUserRequest(
            username="teacher",
            display_name="",
            password="足够长的安全密码 2026",
            role_codes=["teacher"],
        )
    with pytest.raises(ValueError):
        UserPatch()
    with pytest.raises(ValueError):
        RoleUpdate(role_codes=["teacher", "teacher"])
