"""认证 API 测试。"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from apps.api.app import create_app
from apps.api.dependencies import HealthDependencies


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


_CSRF_COOKIE = {"child_manager_csrf": "test-csrf"}
_CSRF_HEADERS = {
    "origin": "http://127.0.0.1:28080",
    "x-csrf-token": "test-csrf",
}


def _cookies(response: Any) -> list[str]:
    return response.headers.get_list("set-cookie")


def _auth_cookies(response: Any) -> list[str]:
    return [c for c in _cookies(response) if "HttpOnly" in c]


def test_login_sets_two_http_only_cookies(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "ValidPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 200
    cookies = _auth_cookies(response)
    assert len(cookies) == 2
    assert all("HttpOnly" in c for c in cookies)
    assert any(c.startswith("child_manager_access=") for c in cookies)
    assert any(c.startswith("child_manager_refresh=") for c in cookies)


def test_login_failure_returns_generic_message(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong-password"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 401
    data = response.json()
    assert "账号或密码错误" in data["message"]


def test_disabled_user_cannot_login(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "disabled", "password": "ValidPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 401


def test_refresh_returns_two_new_cookies(client: TestClient) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "ValidPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert login.status_code == 200
    refresh_cookie = login.cookies.get("child_manager_refresh")
    assert refresh_cookie is not None
    response = client.post(
        "/api/v1/auth/refresh",
        cookies={"child_manager_refresh": refresh_cookie},
    )
    assert response.status_code == 200
    cookies = _auth_cookies(response)
    assert len(cookies) == 2


def test_logout_clears_two_cookies(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/logout",
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 200
    cookies = _auth_cookies(response)
    assert len(cookies) == 2
    assert all("Max-Age=0" in c for c in cookies)


def test_login_rate_limit_after_repeated_failures(client: TestClient) -> None:
    for _ in range(5):
        client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong"},
            headers=_CSRF_HEADERS,
            cookies=_CSRF_COOKIE,
        )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 429
