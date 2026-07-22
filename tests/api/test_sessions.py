# ruff: noqa: F811

import psycopg
from fastapi.testclient import TestClient

from packages.backend.identity.tokens import hash_refresh_token
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def test_session_listing_and_revocation_require_authentication(passkey_client: TestClient) -> None:
    headers = csrf_headers(passkey_client)
    listed = passkey_client.get("/api/v1/auth/sessions")
    revoked = passkey_client.delete(
        "/api/v1/auth/sessions/00000000-0000-7000-8000-000000000001",
        headers=headers,
    )

    assert listed.status_code == 401
    assert revoked.status_code == 401


def test_refresh_without_valid_family_is_rejected_without_new_cookies(
    passkey_client: TestClient,
) -> None:
    response = passkey_client.post(
        "/api/v1/auth/refresh",
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 401
    assert response.headers.get_list("set-cookie") == []


def test_invalid_access_token_is_rejected(passkey_client: TestClient) -> None:
    passkey_client.cookies.set("child_manager_access", "not-a-jwt")

    response = passkey_client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_logout_is_idempotent_and_clears_two_auth_cookies(passkey_client: TestClient) -> None:
    response = passkey_client.post(
        "/api/v1/auth/logout",
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 204
    cookies = response.headers.get_list("set-cookie")
    assert len(cookies) == 2
    assert cookies[0].startswith("child_manager_access=")
    assert cookies[1].startswith("child_manager_refresh=")
    assert all("Max-Age=0" in cookie for cookie in cookies)


def test_user_can_list_and_revoke_current_session_with_immediate_effect(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client

    listed = client.get("/api/v1/auth/sessions")
    revoked = client.delete(
        f"/api/v1/auth/sessions/{actor.session_id}",
        headers=csrf_headers(client),
    )

    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [str(actor.session_id)]
    assert revoked.status_code == 204
    cleared = revoked.headers.get_list("set-cookie")
    assert len(cleared) == 2
    assert all("Max-Age=0" in value for value in cleared)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT count(*), count(revoked_at) FROM refresh_tokens
            WHERE kindergarten_id=%s AND token_family_id=%s""",
            (actor.kindergarten_id, actor.session_id),
        ).fetchone() == (1, 1)


def test_refresh_rotation_preserves_absolute_expiry_and_replay_revokes_entire_family(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    raw_refresh = "admin-test-refresh"
    client.cookies.set("child_manager_refresh", raw_refresh)
    headers = csrf_headers(client)

    rotated = client.post("/api/v1/auth/refresh", headers=headers)
    assert rotated.status_code == 200
    assert len(rotated.headers.get_list("set-cookie")) == 2
    assert rotated.cookies["child_manager_refresh"] != raw_refresh

    client.cookies.delete("child_manager_refresh")
    client.cookies.set("child_manager_refresh", raw_refresh)
    replay = client.post("/api/v1/auth/refresh", headers=headers)

    assert replay.status_code == 401
    assert replay.headers.get_list("set-cookie") == []
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        rows = connection.execute(
            """SELECT token_hash, expires_at, revoked_at FROM refresh_tokens
            WHERE kindergarten_id=%s AND token_family_id=%s ORDER BY issued_at""",
            (actor.kindergarten_id, actor.session_id),
        ).fetchall()
    assert len(rows) == 2
    assert rows[0][0] == hash_refresh_token(raw_refresh)
    assert rows[0][1] == rows[1][1]
    assert all(row[2] is not None for row in rows)


def test_expired_refresh_family_is_rejected_without_extending_it(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE refresh_tokens
            SET issued_at=now() - interval '2 days', expires_at=now() - interval '1 day'
            WHERE kindergarten_id=%s AND token_family_id=%s""",
            (actor.kindergarten_id, actor.session_id),
        )
    client.cookies.set("child_manager_refresh", "admin-test-refresh")

    response = client.post("/api/v1/auth/refresh", headers=csrf_headers(client))

    assert response.status_code == 401
    assert response.headers.get_list("set-cookie") == []
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT count(*) FROM refresh_tokens
            WHERE kindergarten_id=%s AND token_family_id=%s""",
            (actor.kindergarten_id, actor.session_id),
        ).fetchone() == (1,)
