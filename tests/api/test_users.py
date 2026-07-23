# ruff: noqa: F811

from datetime import UTC, datetime
from uuid import UUID, uuid4

import psycopg
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


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


def test_activation_requires_registered_pending_account_and_persists_verification_evidence(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    incomplete = client.post(
        "/api/v1/users",
        json={
            "username": "incomplete-teacher",
            "display_name": "未登记教师",
            "role_codes": ["teacher"],
        },
        headers=csrf_headers(client),
    )
    assert incomplete.status_code == 201
    incomplete_id = UUID(incomplete.json()["id"])

    rejected = client.post(
        f"/api/v1/users/{incomplete_id}/activate",
        json={"verification_confirmed": True, "verification_note": "不应绕过登记"},
        headers=csrf_headers(client),
    )

    assert rejected.status_code == 409
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            "SELECT status FROM users WHERE id=%s",
            (incomplete_id,),
        ).fetchone() == ("pending_registration",)
        assert connection.execute(
            """SELECT count(*) FROM identity_verification_approvals
            WHERE user_id=%s""",
            (incomplete_id,),
        ).fetchone() == (0,)

    ready = client.post(
        "/api/v1/users",
        json={
            "username": "verified-teacher",
            "display_name": "已登记教师",
            "role_codes": ["teacher"],
        },
        headers=csrf_headers(client),
    )
    assert ready.status_code == 201
    ready_id = UUID(ready.json()["id"])
    invitation = client.post(
        f"/api/v1/users/{ready_id}/invitations",
        json={"expires_in_hours": 24},
        headers=csrf_headers(client),
    )
    assert invitation.status_code == 201
    invitation_id = UUID(invitation.json()["id"])
    credential_id = uuid4()
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """INSERT INTO webauthn_credentials
            (id, kindergarten_id, user_id, credential_id, public_key_cose, sign_count,
             transports, backup_eligible, backup_state, label, created_via)
            VALUES (%s,%s,%s,%s,%s,0,%s,false,false,%s,'invitation')""",
            (
                credential_id,
                actor.kindergarten_id,
                ready_id,
                b"activation-credential",
                b"activation-cose",
                '["internal"]',
                "登记凭据",
            ),
        )
        connection.execute(
            """UPDATE account_invitations SET consumed_at=%s, registered_credential_id=%s
            WHERE id=%s""",
            (now, credential_id, invitation_id),
        )
        connection.execute(
            "UPDATE users SET status='pending_verification' WHERE id=%s",
            (ready_id,),
        )

    activated = client.post(
        f"/api/v1/users/{ready_id}/activate",
        json={"verification_confirmed": True, "verification_note": "已完成带外电话核验"},
        headers=csrf_headers(client),
    )

    assert activated.status_code == 200
    assert activated.json()["status"] == "active"
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            """SELECT context_type, context_id, user_id, approver_user_id, approver_kind,
                      approver_reference, decision, note
            FROM identity_verification_approvals WHERE user_id=%s""",
            (ready_id,),
        ).fetchall() == [
            (
                "invitation",
                invitation_id,
                ready_id,
                actor.user_id,
                "admin",
                str(actor.user_id),
                "approved",
                "已完成带外电话核验",
            )
        ]


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
