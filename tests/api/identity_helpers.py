from __future__ import annotations

from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from apps.api.app import create_app
from packages.backend.bootstrap.init_admin import initialize_admin


@pytest.fixture
def identity_client(
    isolated_database_url: str, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    monkeypatch.setenv("CHILD_MANAGER_JWT_SIGNING_KEY", "test-jwt-signing-key-that-is-long")
    monkeypatch.setenv("CHILD_MANAGER_CSRF_SIGNING_KEY", "test-csrf-signing-key-that-is-long")
    monkeypatch.setenv("CHILD_MANAGER_COOKIE_SECURE", "false")
    monkeypatch.setenv("CHILD_MANAGER_ENV", "development")
    monkeypatch.setenv("CHILD_MANAGER_BIND_HOST", "127.0.0.1")
    monkeypatch.setenv("CHILD_MANAGER_LOGIN_THROTTLE_BACKEND", "memory")
    command.upgrade(Config("alembic.ini"), "head")
    initialize_admin(
        database_url=isolated_database_url,
        kindergarten_name="测试幼儿园",
        username="admin",
        display_name="测试管理员",
        password="管理员足够长的安全测试密码 2026",
    )
    with TestClient(create_app()) as client:
        yield client


def csrf_headers(client: TestClient) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf")
    assert response.status_code == 200
    return {"Origin": "http://testserver", "X-CSRF-Token": response.json()["csrf_token"]}


def login_admin(client: TestClient) -> dict[str, str]:
    headers = csrf_headers(client)
    response = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers=headers,
    )
    assert response.status_code == 200
    return headers
