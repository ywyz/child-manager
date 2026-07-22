# ruff: noqa: F811

from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def test_user_creation_accepts_identity_metadata_without_any_password_field(
    passkey_client: TestClient,
) -> None:
    response = passkey_client.post(
        "/api/v1/users",
        json={
            "username": "teacher",
            "phone_e164": "+8613800138000",
            "display_name": "测试教师",
            "role_codes": ["teacher"],
        },
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 401
    assert "password" not in response.text.lower()


def test_user_identity_management_routes_require_an_admin(passkey_client: TestClient) -> None:
    user_id = "00000000-0000-7000-8000-000000000001"
    headers = csrf_headers(passkey_client)
    responses = [
        passkey_client.get("/api/v1/users"),
        passkey_client.get(f"/api/v1/users/{user_id}"),
        passkey_client.patch(
            f"/api/v1/users/{user_id}",
            json={"display_name": "更新后的教师"},
            headers=headers,
        ),
        passkey_client.put(
            f"/api/v1/users/{user_id}/roles",
            json={"role_codes": ["teacher"]},
            headers=headers,
        ),
        passkey_client.post(
            f"/api/v1/users/{user_id}/activate",
            json={"verification_confirmed": True},
            headers=headers,
        ),
        passkey_client.post(f"/api/v1/users/{user_id}/deactivate", headers=headers),
    ]

    assert [response.status_code for response in responses] == [401] * len(responses)


def test_admin_creates_pending_account_without_accepting_a_password(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    headers = csrf_headers(client)

    created = client.post(
        "/api/v1/users",
        json={
            "username": "teacher",
            "phone_e164": "+8613800138000",
            "display_name": "测试教师",
            "role_codes": ["teacher"],
        },
        headers=headers,
    )
    rejected_password = client.post(
        "/api/v1/users",
        json={
            "username": "legacy-teacher",
            "display_name": "旧密码教师",
            "role_codes": ["teacher"],
            "password": "must-not-be-accepted",
        },
        headers=headers,
    )

    assert created.status_code == 201
    assert created.json()["status"] == "pending_registration"
    assert created.json()["credential_count"] == 0
    assert "password" not in created.text.lower()
    assert rejected_password.status_code == 422


def test_legacy_password_reset_route_is_absent(passkey_client: TestClient) -> None:
    response = passkey_client.post(
        "/api/v1/users/00000000-0000-7000-8000-000000000001/reset-password",
        json={"new_password": "legacy-password"},
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 404


def test_last_admin_protection_is_exposed_as_stable_conflict_contract(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    headers = csrf_headers(client)
    role_response = client.put(
        f"/api/v1/users/{actor.user_id}/roles",
        json={"role_codes": ["teacher"]},
        headers=headers,
    )
    deactivate_response = client.post(
        f"/api/v1/users/{actor.user_id}/deactivate",
        headers=headers,
    )

    assert role_response.status_code == 409
    assert deactivate_response.status_code == 409
    assert role_response.json()["message"]
    assert deactivate_response.json()["message"]
