from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
import yaml
from fastapi.routing import APIRoute

from apps.api.routers.users import router as users_router
from packages.contracts import identity as identity_contracts

OPENAPI = yaml.safe_load(
    Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
)


def _runtime_routes() -> set[tuple[str, str]]:
    return {
        (route.path, method)
        for route in users_router.routes
        if isinstance(route, APIRoute) and route.methods is not None
        for method in route.methods
    }


def test_create_user_uses_roles_without_accepting_password_or_kindergarten() -> None:
    create_user = identity_contracts.CreateUserRequest.model_validate(
        {
            "username": " teacher ",
            "display_name": "测试教师",
            "phone_e164": "+8613800138000",
            "role_codes": ["teacher"],
        }
    )

    assert create_user.model_dump()["role_codes"] == ["teacher"]
    with pytest.raises(ValueError):
        identity_contracts.CreateUserRequest.model_validate(
            {
                "username": "teacher",
                "display_name": "测试教师",
                "role_codes": ["teacher"],
                "password": "不得存在的密码",
            }
        )
    with pytest.raises(ValueError):
        identity_contracts.CreateUserRequest.model_validate(
            {
                "username": "teacher",
                "display_name": "测试教师",
                "role_codes": ["teacher"],
                "kindergarten_id": "00000000-0000-7000-8000-000000000001",
            }
        )


def test_user_contract_exposes_account_status_and_credential_count_without_password() -> None:
    user_model = identity_contracts.__dict__["User"]
    now = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)
    user = user_model(
        id=UUID("00000000-0000-7000-8000-000000000001"),
        username="teacher",
        phone_e164=None,
        display_name="测试教师",
        role_codes=["teacher"],
        status="pending_registration",
        credential_count=0,
        activated_at=None,
        created_at=now,
        updated_at=now,
    )

    assert user.model_dump()["status"] == "pending_registration"
    assert {"password", "password_hash", "password_changed_at"}.isdisjoint(user.model_fields)


def test_users_openapi_covers_invitation_credentials_recovery_and_session_revocation() -> None:
    paths = set(OPENAPI["paths"])
    required = {
        "/api/v1/users/{user_id}/activate",
        "/api/v1/users/{user_id}/deactivate",
        "/api/v1/users/{user_id}/invitations",
        "/api/v1/users/{user_id}/invitations/{invitation_id}/revoke",
        "/api/v1/users/{user_id}/credentials",
        "/api/v1/users/{user_id}/credentials/{credential_id}",
        "/api/v1/users/{user_id}/sessions/revoke",
        "/api/v1/users/{user_id}/recovery-requests",
        "/api/v1/users/{user_id}/recovery-requests/{recovery_request_id}/approve",
    }

    assert required <= paths
    assert "/api/v1/users/{user_id}/reset-password" not in paths


def test_runtime_users_router_matches_frozen_identity_management_paths() -> None:
    routes = _runtime_routes()
    required = {
        ("/api/v1/users/{user_id}/invitations", "GET"),
        ("/api/v1/users/{user_id}/invitations", "POST"),
        ("/api/v1/users/{user_id}/credentials", "GET"),
        ("/api/v1/users/{user_id}/credentials/{credential_id}", "DELETE"),
        ("/api/v1/users/{user_id}/sessions/revoke", "POST"),
        ("/api/v1/users/{user_id}/recovery-requests", "GET"),
    }

    assert required <= routes
    assert ("/api/v1/users/{user_id}/reset-password", "POST") not in routes
