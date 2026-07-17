"""用户管理 API 测试。"""

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


_CSRF_HEADERS = {
    "origin": "http://127.0.0.1:28080",
    "x-csrf-token": "test-csrf",
}
_CSRF_COOKIE = {"child_manager_csrf": "test-csrf"}


def test_create_user_requires_admin(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users",
        json={
            "username": "teacher",
            "display_name": "教师",
            "phone": None,
            "roles": ["teacher"],
        },
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 401


def test_reset_password_requires_admin(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/user-1/reset-password",
        json={"new_password": "NewPassword2024!"},
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code == 401


def test_deactivate_last_admin_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/sole-admin/deactivate",
        headers=_CSRF_HEADERS,
        cookies=_CSRF_COOKIE,
    )
    assert response.status_code in {401, 409}
