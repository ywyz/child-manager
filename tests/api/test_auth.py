# ruff: noqa: F811

from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import uuid4

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.app import create_app
from packages.backend.identity.login_throttle import ThrottleDecision
from packages.backend.identity.service import IdentityError, IdentityService
from packages.backend.identity.tokens import generate_refresh_token, hash_refresh_token
from tests.api.identity_helpers import csrf_headers, identity_client, login_admin  # noqa: F401


def _auth_cookies(response: object) -> list[str]:
    return response.headers.get_list("set-cookie")  # type: ignore[attr-defined]


def test_login_normalizes_username_and_sets_two_independent_httponly_cookies(
    identity_client: TestClient,
) -> None:
    headers = csrf_headers(identity_client)
    response = identity_client.post(
        "/api/v1/auth/login",
        json={"login": " ＡＤＭＩＮ ", "password": "管理员足够长的安全测试密码 2026"},
        headers=headers,
    )
    assert response.status_code == 200
    cookies = _auth_cookies(response)
    assert len(cookies) == 2
    assert cookies[0].startswith("child_manager_access=")
    assert cookies[1].startswith("child_manager_refresh=")
    assert all("HttpOnly" in value and "SameSite=lax" in value for value in cookies)
    assert all("," not in value for value in cookies)


def test_login_failure_is_generic_for_missing_wrong_and_inactive_accounts(
    identity_client: TestClient,
) -> None:
    headers = login_admin(identity_client)
    created = identity_client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "username": "inactive-user",
            "display_name": "停用教师",
            "password": "教师足够长的安全测试密码 2026",
            "role_codes": ["teacher"],
        },
    )
    identity_client.post(f"/api/v1/users/{created.json()['id']}/deactivate", headers=headers)
    identity_client.cookies.clear()
    headers = csrf_headers(identity_client)
    payloads = [
        {"login": "missing", "password": "错误但足够长的密码 2026"},
        {"login": "admin", "password": "错误但足够长的密码 2026"},
        {"login": "inactive-user", "password": "教师足够长的安全测试密码 2026"},
    ]
    responses = [
        identity_client.post("/api/v1/auth/login", json=payload, headers=headers)
        for payload in payloads
    ]
    assert [response.status_code for response in responses] == [401, 401, 401]
    assert {response.json()["code"] for response in responses} == {"auth.login_failed"}
    assert len({response.json()["message"] for response in responses}) == 1


def test_invalid_access_token_returns_unauthenticated(identity_client: TestClient) -> None:
    identity_client.cookies.set("child_manager_access", "not-a-jwt")

    response = identity_client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["code"] == "auth.unauthenticated"


def test_refresh_rotates_then_replay_revokes_family(identity_client: TestClient) -> None:
    headers = csrf_headers(identity_client)
    login = identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers=headers,
    )
    old_refresh = login.cookies["child_manager_refresh"]
    refreshed = identity_client.post("/api/v1/auth/refresh", headers=headers)
    assert refreshed.status_code == 200
    assert len(_auth_cookies(refreshed)) == 2
    new_refresh = refreshed.cookies["child_manager_refresh"]
    family_access = refreshed.cookies["child_manager_access"]
    assert new_refresh != old_refresh
    identity_client.cookies.set("child_manager_refresh", old_refresh)
    replay = identity_client.post("/api/v1/auth/refresh", headers=headers)
    assert replay.status_code == 401
    identity_client.cookies.set("child_manager_access", family_access)
    assert identity_client.get("/api/v1/auth/me").status_code == 401
    identity_client.cookies.set("child_manager_refresh", new_refresh)
    assert identity_client.post("/api/v1/auth/refresh", headers=headers).status_code == 401


def test_refresh_and_logout_do_not_resolve_token_outside_active_kindergarten(
    identity_client: TestClient, isolated_database_url: str
) -> None:
    raw_refresh = generate_refresh_token()
    now = datetime.now(UTC)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        kindergarten_id = uuid4()
        user_id = uuid4()
        connection.execute(
            "INSERT INTO kindergartens (id, name, is_active) VALUES (%s, %s, false)",
            (kindergarten_id, "非当前园所"),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             password_hash, password_changed_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                user_id,
                kindergarten_id,
                "other-admin",
                "other-admin",
                "其他园所管理员",
                "$argon2id$test",
                now,
            ),
        )
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                uuid4(),
                kindergarten_id,
                user_id,
                uuid4(),
                hash_refresh_token(raw_refresh),
                now,
                now + timedelta(days=7),
            ),
        )
    service = IdentityService.from_environment()
    with pytest.raises(IdentityError) as raised:
        service.refresh(raw_refresh, request_id=None)

    assert raised.value.status_code == 401
    assert raised.value.code == "auth.unauthenticated"
    service.logout(raw_refresh, request_id=None)
    with psycopg.connect(native_url) as connection:
        row = connection.execute(
            "SELECT revoked_at FROM refresh_tokens WHERE token_hash=%s",
            (hash_refresh_token(raw_refresh),),
        ).fetchone()
    assert row == (None,)


def test_logout_clears_two_independent_cookies(identity_client: TestClient) -> None:
    headers = csrf_headers(identity_client)
    login = identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers=headers,
    )
    access = login.cookies["child_manager_access"]
    response = identity_client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 204
    cookies = _auth_cookies(response)
    assert len(cookies) == 2
    assert all("Max-Age=0" in value for value in cookies)
    identity_client.cookies.set("child_manager_access", access)
    assert identity_client.get("/api/v1/auth/me").status_code == 401


def test_logout_revokes_access_family_when_refresh_cookie_is_missing(
    identity_client: TestClient,
) -> None:
    headers = csrf_headers(identity_client)
    login = identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers=headers,
    )
    access = login.cookies["child_manager_access"]
    identity_client.cookies.delete("child_manager_refresh")

    response = identity_client.post("/api/v1/auth/logout", headers=headers)

    assert response.status_code == 204
    identity_client.cookies.set("child_manager_access", access)
    assert identity_client.get("/api/v1/auth/me").status_code == 401


def test_change_password_revokes_all_sessions(identity_client: TestClient) -> None:
    headers = csrf_headers(identity_client)
    identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers=headers,
    )
    response = identity_client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "管理员足够长的安全测试密码 2026",
            "new_password": "管理员足够长的新安全密码 2026",
        },
        headers=headers,
    )
    assert response.status_code == 204
    assert identity_client.get("/api/v1/auth/me").status_code == 401


def test_expired_refresh_is_rejected(
    identity_client: TestClient, isolated_database_url: str
) -> None:
    headers = csrf_headers(identity_client)
    login = identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers=headers,
    )
    refresh_hash = hash_refresh_token(login.cookies["child_manager_refresh"])
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE refresh_tokens SET issued_at=%s, expires_at=%s
            WHERE token_hash=%s""",
            (now - timedelta(days=2), now - timedelta(days=1), refresh_hash),
        )
    assert identity_client.post("/api/v1/auth/refresh", headers=headers).status_code == 401


def test_source_rate_limit_returns_429_and_is_audited(
    identity_client: TestClient, isolated_database_url: str
) -> None:
    class LimitedThrottle:
        def check(self, **_arguments: object) -> ThrottleDecision:
            return ThrottleDecision(source_limited=True)

        def record_failure(self, **_arguments: object) -> ThrottleDecision:
            raise AssertionError("达到来源阈值后不得继续验密或记录本次失败")

        def record_success(self, **_arguments: object) -> None:
            return None

    cast(FastAPI, identity_client.app).state.login_throttle = LimitedThrottle()
    response = identity_client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        headers=csrf_headers(identity_client),
    )
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        row = connection.execute(
            "SELECT count(*) FROM audit_events WHERE event_code='identity.login_rate_limited'"
        ).fetchone()
    assert row is not None and row[0] == 1


def test_redis_mode_without_url_fails_closed_for_login(
    identity_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_LOGIN_THROTTLE_BACKEND", "redis")
    monkeypatch.delenv("CHILD_MANAGER_REDIS_URL", raising=False)
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/auth/login",
            headers=csrf_headers(client),
            json={"login": "admin", "password": "管理员足够长的安全测试密码 2026"},
        )
    assert response.status_code == 503
    assert response.json()["code"] == "configuration.unavailable"
