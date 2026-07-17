"""CSRF 与来源校验 API 测试。"""

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


def test_state_change_without_csrf_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "ValidPassword2024!"},
        headers={"origin": "http://127.0.0.1:28080"},
    )
    assert response.status_code == 403


def test_csrf_with_forged_origin_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "ValidPassword2024!"},
        headers={
            "origin": "http://evil.example.com",
            "x-csrf-token": "token",
        },
        cookies={"child_manager_csrf": "token"},
    )
    assert response.status_code == 403


def test_missing_origin_header_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/logout",
        headers={"x-csrf-token": "token"},
        cookies={"child_manager_csrf": "token"},
    )
    assert response.status_code == 403


def test_valid_signed_csrf_token_is_accepted(client: TestClient) -> None:
    from packages.backend.config import settings
    from packages.backend.identity.csrf import generate_csrf_token

    token = generate_csrf_token(settings.csrf_signing_key)
    response = client.post(
        "/api/v1/auth/logout",
        headers={"origin": "http://127.0.0.1:28080", "x-csrf-token": token},
        cookies={"child_manager_csrf": token},
    )
    assert response.status_code == 204


def test_signed_cookie_and_header_mismatch_is_rejected(client: TestClient) -> None:
    from packages.backend.config import settings
    from packages.backend.identity.csrf import generate_csrf_token

    cookie_token = generate_csrf_token(settings.csrf_signing_key)
    header_token = generate_csrf_token(settings.csrf_signing_key)
    response = client.post(
        "/api/v1/auth/logout",
        headers={"origin": "http://127.0.0.1:28080", "x-csrf-token": header_token},
        cookies={"child_manager_csrf": cookie_token},
    )
    assert response.status_code == 403
