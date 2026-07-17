# ruff: noqa: F811

from datetime import UTC, datetime
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient

from tests.api.identity_helpers import csrf_headers, identity_client, login_admin  # noqa: F401


def test_admin_can_create_list_reset_and_deactivate_user(identity_client: TestClient) -> None:
    headers = login_admin(identity_client)
    created = identity_client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "username": "teacher",
            "phone_e164": "13800138000",
            "display_name": "测试教师",
            "password": "教师足够长的安全测试密码 2026",
            "role_codes": ["teacher"],
        },
    )
    assert created.status_code == 201
    assert "password" not in created.json()
    user_id = created.json()["id"]
    page = identity_client.get("/api/v1/users?page=1&page_size=20")
    assert page.status_code == 200 and page.json()["total"] == 2
    reset = identity_client.post(
        f"/api/v1/users/{user_id}/reset-password",
        headers=headers,
        json={"new_password": "教师重置后的足够长安全密码 2026"},
    )
    assert reset.status_code == 204
    assert (
        identity_client.post(f"/api/v1/users/{user_id}/deactivate", headers=headers).status_code
        == 200
    )


def test_last_active_admin_cannot_be_deactivated_or_lose_role(identity_client: TestClient) -> None:
    headers = login_admin(identity_client)
    admin_id = identity_client.get("/api/v1/auth/me").json()["id"]
    deactivated = identity_client.post(f"/api/v1/users/{admin_id}/deactivate", headers=headers)
    assert deactivated.status_code == 409
    roles = identity_client.put(
        f"/api/v1/users/{admin_id}/roles", headers=headers, json={"role_codes": ["teacher"]}
    )
    assert roles.status_code == 409


def test_user_list_rejects_unbounded_pagination(identity_client: TestClient) -> None:
    login_admin(identity_client)
    response = identity_client.get("/api/v1/users?page_size=101")
    assert response.status_code == 422
    assert response.json()["code"] == "request.invalid_pagination"


def test_deactivated_user_loses_access_on_next_request(identity_client: TestClient) -> None:
    admin_headers = login_admin(identity_client)
    created = identity_client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "username": "next-request-teacher",
            "display_name": "下一请求失权教师",
            "password": "教师足够长的安全测试密码 2026",
            "role_codes": ["teacher"],
        },
    )
    user_id = created.json()["id"]
    with TestClient(identity_client.app) as teacher_client:
        teacher_headers = csrf_headers(teacher_client)
        login = teacher_client.post(
            "/api/v1/auth/login",
            headers=teacher_headers,
            json={
                "login": "next-request-teacher",
                "password": "教师足够长的安全测试密码 2026",
            },
        )
        assert login.status_code == 200
        assert teacher_client.get("/api/v1/auth/me").status_code == 200
        deactivated = identity_client.post(
            f"/api/v1/users/{user_id}/deactivate", headers=admin_headers
        )
        assert deactivated.status_code == 200
        assert teacher_client.get("/api/v1/auth/me").status_code == 401


def test_create_user_rejects_weak_password(identity_client: TestClient) -> None:
    response = identity_client.post(
        "/api/v1/users",
        headers=login_admin(identity_client),
        json={
            "username": "weak-password-teacher",
            "display_name": "弱密码教师",
            "password": "password",
            "role_codes": ["teacher"],
        },
    )
    assert response.status_code == 422


def test_cross_kindergarten_user_is_not_visible_or_mutable(
    identity_client: TestClient, isolated_database_url: str
) -> None:
    headers = login_admin(identity_client)
    other_kindergarten_id = uuid4()
    other_user_id = uuid4()
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name, is_active) VALUES (%s, %s, false)",
            (other_kindergarten_id, "非当前园所"),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             password_hash, password_changed_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                other_user_id,
                other_kindergarten_id,
                "other-teacher",
                "other-teacher",
                "其他园所教师",
                "$argon2id$test",
                datetime.now(UTC),
            ),
        )

    responses = [
        identity_client.get(f"/api/v1/users/{other_user_id}"),
        identity_client.patch(
            f"/api/v1/users/{other_user_id}",
            headers=headers,
            json={"display_name": "越权修改"},
        ),
        identity_client.put(
            f"/api/v1/users/{other_user_id}/roles",
            headers=headers,
            json={"role_codes": ["admin"]},
        ),
        identity_client.post(f"/api/v1/users/{other_user_id}/deactivate", headers=headers),
        identity_client.post(
            f"/api/v1/users/{other_user_id}/reset-password",
            headers=headers,
            json={"new_password": "越权重置后的足够长安全密码 2026"},
        ),
    ]
    assert [response.status_code for response in responses] == [404, 404, 404, 404, 404]
    assert {response.json()["code"] for response in responses} == {"resource.not_found"}
    with psycopg.connect(native_url) as connection:
        row = connection.execute(
            "SELECT display_name, is_active FROM users WHERE kindergarten_id=%s AND id=%s",
            (other_kindergarten_id, other_user_id),
        ).fetchone()
    assert row == ("其他园所教师", True)
