"""用户管理 API 测试。"""

import pytest
from fastapi.testclient import TestClient

from apps.api.app import create_app
from apps.api.dependencies import HealthDependencies
from packages.backend.identity.csrf import generate_csrf_token


@pytest.fixture
def client(migrated_database_url: str) -> TestClient:
    async def _true() -> bool:
        return True

    return TestClient(
        create_app(
            dependencies=HealthDependencies(
                database=_true,
                redis=_true,
                ai=_true,
                calendar=_true,
                template=_true,
                export_storage=_true,
                security_ready=True,
            )
        )
    )


@pytest.fixture(autouse=True)
def _set_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    from packages.backend.config import settings

    monkeypatch.setattr(
        settings,
        "jwt_signing_key",
        "test-jwt-signing-key-32bytes-long-12345",
        raising=False,
    )
    monkeypatch.setattr(
        settings,
        "csrf_signing_key",
        "test-csrf-signing-key-32bytes-long-1234",
        raising=False,
    )


_CSRF_TOKEN = generate_csrf_token("test-csrf-signing-key-32bytes-long-1234")
_CSRF_HEADERS = {
    "origin": "http://127.0.0.1:28080",
    "x-csrf-token": _CSRF_TOKEN,
}
_CSRF_COOKIE = {"child_manager_csrf": _CSRF_TOKEN}


def _admin_session(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert login.status_code == 200
    access = login.cookies.get("child_manager_access")
    assert access is not None
    return {"child_manager_access": access, **_CSRF_COOKIE}


def test_create_user_requires_admin(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "username": "teacher",
            "display_name": "教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 401


def test_create_user_returns_201_and_user(client: TestClient) -> None:
    cookies = _admin_session(client)
    response = client.post(
        "/api/v1/users",
        json={
            "username": "teacher1",
            "display_name": "教师一",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "teacher1"
    assert data["role_codes"] == ["teacher"]
    assert "created_at" in data


def test_list_users_returns_pagination(client: TestClient) -> None:
    cookies = _admin_session(client)
    response = client.get("/api/v1/users", headers=_CSRF_HEADERS, cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data


def test_get_user_by_id(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher2",
            "display_name": "教师二",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}", headers=_CSRF_HEADERS, cookies=cookies)
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_update_user(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher3",
            "display_name": "教师三",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"display_name": "更新后的名称"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "更新后的名称"


def test_set_user_roles(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher4",
            "display_name": "教师四",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.put(
        f"/api/v1/users/{user_id}/roles",
        json={"role_codes": ["teacher", "admin"]},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 200
    assert set(response.json()["role_codes"]) == {"teacher", "admin"}


def test_deactivate_and_activate_user(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher5",
            "display_name": "教师五",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    deactivate = client.post(
        f"/api/v1/users/{user_id}/deactivate",
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False

    get_response = client.get(f"/api/v1/users/{user_id}", headers=_CSRF_HEADERS, cookies=cookies)
    assert get_response.json()["is_active"] is False

    activate = client.post(
        f"/api/v1/users/{user_id}/activate",
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert activate.status_code == 200
    assert activate.json()["is_active"] is True


def test_reset_password_returns_204(client: TestClient) -> None:
    cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher6",
            "display_name": "教师六",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    user_id = create.json()["id"]

    response = client.post(
        f"/api/v1/users/{user_id}/reset-password",
        json={"new_password": "NewPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 204


def test_reset_password_revokes_target_access_token_on_next_request(client: TestClient) -> None:
    """管理员重置密码后，目标用户旧 Access Token 下一请求必须返回 401。"""
    admin_cookies = _admin_session(client)
    create = client.post(
        "/api/v1/users",
        json={
            "username": "teacher_reset_target",
            "display_name": "重置目标教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "ValidPassword2024!",
        },
        headers=_CSRF_HEADERS,
        cookies=admin_cookies,
    )
    assert create.status_code == 201
    user_id = create.json()["id"]

    teacher_login = client.post(
        "/api/v1/auth/login",
        json={"login": "teacher_reset_target", "password": "ValidPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert teacher_login.status_code == 200
    teacher_access = teacher_login.cookies.get("child_manager_access")
    assert teacher_access is not None

    me_before = client.get(
        "/api/v1/auth/me",
        headers=_CSRF_HEADERS,
        cookies={"child_manager_access": teacher_access, **_CSRF_COOKIE},
    )
    assert me_before.status_code == 200

    reset = client.post(
        f"/api/v1/users/{user_id}/reset-password",
        json={"new_password": "NewPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=admin_cookies,
    )
    assert reset.status_code == 204

    me_after = client.get(
        "/api/v1/auth/me",
        headers=_CSRF_HEADERS,
        cookies={"child_manager_access": teacher_access, **_CSRF_COOKIE},
    )
    assert me_after.status_code == 401
    assert me_after.json()["code"] == "auth.unauthenticated"


def test_deactivate_last_admin_is_rejected(client: TestClient) -> None:
    cookies = _admin_session(client)
    me = client.get("/api/v1/auth/me", headers=_CSRF_HEADERS, cookies=cookies)
    admin_id = me.json()["id"]

    response = client.post(
        f"/api/v1/users/{admin_id}/deactivate",
        headers=_CSRF_HEADERS,
        cookies=cookies,
    )
    assert response.status_code == 409


def test_reset_password_requires_admin(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/user-1/reset-password",
        json={"new_password": "NewPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 401
