# ruff: noqa: F811

from datetime import UTC, datetime, timedelta
from importlib import import_module
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient

from packages.backend.identity.tokens import hash_refresh_token
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def test_backup_status_and_enrollment_require_authentication(
    passkey_client: TestClient,
) -> None:
    status = passkey_client.get("/api/v1/auth/backup")
    enrollment = passkey_client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(passkey_client),
    )

    assert status.status_code == 401
    assert enrollment.status_code == 401


def test_admin_is_restricted_until_complete_backup_enrollment(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    status = client.get("/api/v1/auth/backup")
    enrollment = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )

    assert status.status_code == 200
    assert status.json() == {
        "enabled": False,
        "required": True,
        "changed_at": None,
        "enrollment_required": True,
    }
    assert enrollment.status_code == 201
    assert {
        "enrollment_id",
        "totp_secret",
        "otpauth_uri",
        "expires_at",
    } == set(enrollment.json())
    assert enrollment.json()["otpauth_uri"].startswith("otpauth://totp/")


def test_enrollment_requires_password_and_totp_together_and_is_single_use(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    started = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert started.status_code == 201
    body = started.json()
    totp = import_module("packages.backend.identity.totp")
    code = totp.generate_totp(body["totp_secret"], timestamp=datetime.now(UTC).timestamp())
    payload = {
        "password": "合格的备用登录密码 2026",
        "totp_code": code,
    }

    verified = client.post(
        f"/api/v1/auth/backup/enrollment/{body['enrollment_id']}/verify",
        json=payload,
        headers=csrf_headers(client),
    )
    repeated = client.post(
        f"/api/v1/auth/backup/enrollment/{body['enrollment_id']}/verify",
        json=payload,
        headers=csrf_headers(client),
    )

    assert verified.status_code == 200
    assert verified.json()["enabled"] is True
    assert "totp_secret" not in verified.text
    assert "otpauth://" not in verified.text
    assert repeated.status_code in {409, 410}


def test_expired_enrollment_cannot_enable_backup_auth(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, _actor = admin_client
    started = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert started.status_code == 201
    body = started.json()
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE backup_auth_enrollments
            SET expires_at=%s WHERE id=%s""",
            (datetime.now(UTC) - timedelta(seconds=1), body["enrollment_id"]),
        )
    response = client.post(
        f"/api/v1/auth/backup/enrollment/{body['enrollment_id']}/verify",
        json={"password": "合格的备用登录密码 2026", "totp_code": "000000"},
        headers=csrf_headers(client),
    )

    assert response.status_code == 410


def test_new_enrollment_invalidates_the_previous_pending_enrollment(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    first = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    second = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["enrollment_id"] != second.json()["enrollment_id"]
    rejected = client.post(
        f"/api/v1/auth/backup/enrollment/{first.json()['enrollment_id']}/verify",
        json={"password": "合格的备用登录密码 2026", "totp_code": "000000"},
        headers=csrf_headers(client),
    )
    assert rejected.status_code == 410


def test_replacing_enabled_material_revokes_only_related_backup_sessions(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    totp = import_module("packages.backend.identity.totp")

    first = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert first.status_code == 201
    first_body = first.json()
    first_code = totp.generate_totp(
        first_body["totp_secret"],
        timestamp=datetime.now(UTC).timestamp(),
    )
    first_verified = client.post(
        f"/api/v1/auth/backup/enrollment/{first_body['enrollment_id']}/verify",
        json={
            "password": "第一组安全备用密码 2026",
            "totp_code": first_code,
        },
        headers=csrf_headers(client),
    )
    assert first_verified.status_code == 200

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    backup_session_id = uuid4()
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        first_credential = connection.execute(
            """SELECT id FROM backup_auth_credentials
            WHERE kindergarten_id=%s AND user_id=%s AND status='enabled'""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        version = connection.execute(
            """SELECT backup_auth_version FROM users
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        assert first_credential is not None and version is not None
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at,
             expires_at, authentication_method, backup_verified_at, backup_auth_version)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'password_totp',%s,%s)""",
            (
                backup_session_id,
                actor.kindergarten_id,
                actor.user_id,
                uuid4(),
                hash_refresh_token("replaced-backup-session"),
                now,
                now + timedelta(days=7),
                now,
                version[0],
            ),
        )

    second = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert second.status_code == 201
    second_body = second.json()
    second_code = totp.generate_totp(
        second_body["totp_secret"],
        timestamp=datetime.now(UTC).timestamp(),
    )
    second_verified = client.post(
        f"/api/v1/auth/backup/enrollment/{second_body['enrollment_id']}/verify",
        json={
            "password": "第二组安全备用密码 2026",
            "totp_code": second_code,
        },
        headers=csrf_headers(client),
    )
    assert second_verified.status_code == 200

    with psycopg.connect(native_url) as connection:
        replacement = connection.execute(
            """SELECT id FROM backup_auth_credentials
            WHERE kindergarten_id=%s AND user_id=%s AND status='enabled'""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        backup_session = connection.execute(
            """SELECT revoked_at FROM refresh_tokens
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, backup_session_id),
        ).fetchone()
        current_session = connection.execute(
            """SELECT authentication_method, revoked_at FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s AND token_family_id=%s""",
            (actor.kindergarten_id, actor.user_id, actor.session_id),
        ).fetchone()

    assert replacement is not None
    assert replacement[0] != first_credential[0]
    assert backup_session is not None and backup_session[0] is not None
    assert current_session == ("webauthn", None)
