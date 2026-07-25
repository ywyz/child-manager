# ruff: noqa: F811

import json
from datetime import UTC, datetime, timedelta
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import psycopg
import pytest
import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.dependencies import authenticated_session, identity_service
from packages.backend.identity.service import IdentityError, IdentityService
from packages.backend.identity.tokens import create_access_token
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def _native_url(isolated_database_url: str) -> str:
    return isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def _enable_backup(
    client: TestClient,
    *,
    password: str,
) -> str:
    totp = import_module("packages.backend.identity.totp")
    started = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert started.status_code == 201
    verified = client.post(
        f"/api/v1/auth/backup/enrollment/{started.json()['enrollment_id']}/verify",
        json={
            "password": password,
            "totp_code": totp.generate_totp(
                started.json()["totp_secret"],
                timestamp=datetime.now(UTC).timestamp(),
            ),
        },
        headers=csrf_headers(client),
    )
    assert verified.status_code == 200
    return cast(str, started.json()["totp_secret"])


def _login_with_backup(
    client: TestClient,
    *,
    password: str,
    totp_secret: str,
) -> str:
    totp = import_module("packages.backend.identity.totp")
    response = client.post(
        "/api/v1/auth/backup/authentication",
        json={
            "identifier": "admin",
            "password": password,
            "totp_code": totp.generate_totp(
                totp_secret,
                timestamp=datetime.now(UTC).timestamp() + 30,
            ),
        },
        headers=csrf_headers(client),
    )
    assert response.status_code == 204
    access_token = response.cookies.get("child_manager_access")
    assert access_token is not None
    return access_token


def _identity_service(client: TestClient) -> IdentityService:
    application = cast(FastAPI, client.app)
    dependency = application.dependency_overrides[identity_service]
    return cast(IdentityService, dependency())


def _webauthn_access_token(actor: ActorFixture) -> str:
    return create_access_token(
        user_id=str(actor.user_id),
        kindergarten_id=str(actor.kindergarten_id),
        token_family_id=str(actor.session_id),
        signing_key="test-jwt-signing-key-that-is-long",
        now=datetime.now(UTC),
    )


def _change_actor_to_teacher(
    client: TestClient,
    actor: ActorFixture,
    isolated_database_url: str,
) -> None:
    application = cast(FastAPI, client.app)
    session = cast(SimpleNamespace, application.dependency_overrides[authenticated_session]())
    session.role_codes = ["teacher"]
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            "DELETE FROM user_roles WHERE kindergarten_id=%s AND user_id=%s",
            (actor.kindergarten_id, actor.user_id),
        )
        teacher_role = connection.execute("SELECT id FROM roles WHERE code='teacher'").fetchone()
        assert teacher_role is not None
        connection.execute(
            """INSERT INTO user_roles
            (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (
                actor.kindergarten_id,
                actor.user_id,
                teacher_role[0],
                actor.user_id,
                datetime.now(UTC),
            ),
        )


def test_backup_maintenance_and_security_events_require_authentication(
    passkey_client: TestClient,
) -> None:
    disabled = passkey_client.delete(
        "/api/v1/auth/backup",
        headers=csrf_headers(passkey_client),
    )
    events = passkey_client.get("/api/v1/auth/security-events")

    assert disabled.status_code == 401
    assert events.status_code == 401


def test_admin_cannot_disable_required_backup_authentication(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _enable_backup(client, password="管理员必须保留的备用密码 2026")
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        before = connection.execute(
            """SELECT u.backup_auth_version, bac.status
            FROM users u JOIN backup_auth_credentials bac
              ON bac.kindergarten_id=u.kindergarten_id AND bac.user_id=u.id
            WHERE u.kindergarten_id=%s AND u.id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
    assert before is not None

    response = client.delete(
        "/api/v1/auth/backup",
        headers=csrf_headers(client),
    )

    assert response.status_code == 403
    assert response.json()["code"] == "auth.backup_required_for_admin"
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        after = connection.execute(
            """SELECT u.backup_auth_version, bac.status
            FROM users u JOIN backup_auth_credentials bac
              ON bac.kindergarten_id=u.kindergarten_id AND bac.user_id=u.id
            WHERE u.kindergarten_id=%s AND u.id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
    assert after == before


def test_teacher_can_disable_backup_authentication_and_revoke_old_state(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    password = "教师可关闭的备用密码 2026"
    webauthn_access = _webauthn_access_token(actor)
    totp_secret = _enable_backup(client, password=password)
    old_backup_access = _login_with_backup(
        client,
        password=password,
        totp_secret=totp_secret,
    )
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        version_before = connection.execute(
            """SELECT backup_auth_version FROM users
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        proof = connection.execute(
            """UPDATE refresh_tokens SET backup_reauthenticated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method='password_totp' AND revoked_at IS NULL
            RETURNING id""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
    assert version_before is not None
    assert proof is not None
    _change_actor_to_teacher(client, actor, isolated_database_url)

    response = client.delete(
        "/api/v1/auth/backup",
        headers=csrf_headers(client),
    )

    assert response.status_code == 204
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        credential = connection.execute(
            """SELECT status, password_hash, totp_ciphertext, totp_nonce, totp_key_id
            FROM backup_auth_credentials
            WHERE kindergarten_id=%s AND user_id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        version_after = connection.execute(
            """SELECT backup_auth_version FROM users
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        backup_sessions = connection.execute(
            """SELECT revoked_at, backup_reauthenticated_at
            FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method='password_totp'""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchall()
        active_webauthn_sessions = connection.execute(
            """SELECT count(*) FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method='webauthn' AND revoked_at IS NULL""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        security_event_codes = connection.execute(
            """SELECT event_code FROM audit_events
            WHERE kindergarten_id=%s AND actor_user_id=%s
              AND event_code LIKE %s
            ORDER BY occurred_at""",
            (actor.kindergarten_id, actor.user_id, "auth.backup_%"),
        ).fetchall()
    assert credential == ("revoked", None, None, None, None)
    assert version_after == (version_before[0] + 1,)
    assert backup_sessions
    assert all(revoked_at is not None for revoked_at, _proof in backup_sessions)
    assert all(proof_at is None for _revoked_at, proof_at in backup_sessions)
    assert active_webauthn_sessions == (1,)
    assert [row[0] for row in security_event_codes] == [
        "auth.backup_enabled",
        "auth.backup_login_succeeded",
        "auth.backup_disabled",
    ]
    webauthn_session = _identity_service(client).authenticate_access(webauthn_access)
    assert webauthn_session.authentication_method == "webauthn"
    with pytest.raises(IdentityError) as exc_info:
        _identity_service(client).authenticate_access(old_backup_access)
    assert exc_info.value.status_code == 401


def test_backup_security_events_are_current_user_only_and_bounded(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    event_codes = [
        "auth.backup_enabled",
        "auth.backup_changed",
        "auth.backup_disabled",
        "auth.backup_login_succeeded",
        "auth.passkey_added_from_backup",
        "auth.backup_revoked_by_recovery",
    ]
    other_user_id = uuid4()
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             webauthn_user_handle, status, activated_at)
            VALUES (%s,%s,%s,%s,%s,%s,'active',%s)""",
            (
                other_user_id,
                actor.kindergarten_id,
                "other-security-event-user",
                "other-security-event-user",
                "其他安全事件用户",
                b"e" * 32,
                now,
            ),
        )
        for index in range(25):
            connection.execute(
                """INSERT INTO audit_events
                (id, kindergarten_id, event_code, actor_user_id, actor_role_codes,
                 resource_type, outcome, metadata, occurred_at)
                VALUES (%s,%s,%s,%s,%s::jsonb,'user','success',%s::jsonb,%s)""",
                (
                    uuid4(),
                    actor.kindergarten_id,
                    event_codes[index % len(event_codes)],
                    actor.user_id,
                    '["admin"]',
                    json.dumps(
                        {
                            "authentication_method": ("password_totp" if index % 2 else "webauthn"),
                            "client_hint": f"设备-{index}",
                        }
                    ),
                    now + timedelta(seconds=index),
                ),
            )
        connection.execute(
            """INSERT INTO audit_events
            (id, kindergarten_id, event_code, actor_user_id, actor_role_codes,
             resource_type, outcome, metadata, occurred_at)
            VALUES (%s,%s,'auth.backup_enabled',%s,%s::jsonb,'user','success',
                    %s::jsonb,%s)""",
            (
                uuid4(),
                actor.kindergarten_id,
                other_user_id,
                '["teacher"]',
                json.dumps({"client_hint": "其他用户设备"}),
                now + timedelta(minutes=1),
            ),
        )
        connection.execute(
            """INSERT INTO audit_events
            (id, kindergarten_id, event_code, actor_user_id, actor_role_codes,
             resource_type, outcome, metadata, occurred_at)
            VALUES (%s,%s,'identity.user_updated',%s,%s::jsonb,'user','success',
                    %s::jsonb,%s)""",
            (
                uuid4(),
                actor.kindergarten_id,
                actor.user_id,
                '["admin"]',
                json.dumps({"client_hint": "非白名单事件"}),
                now + timedelta(minutes=2),
            ),
        )

    response = client.get("/api/v1/auth/security-events")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 20
    assert [item["event_code"] for item in response.json()["items"]] == [
        event_codes[index % len(event_codes)] for index in range(24, 4, -1)
    ]
    assert [item["client_hint"] for item in response.json()["items"]] == [
        f"设备-{index}" for index in range(24, 4, -1)
    ]
    assert all(
        set(item)
        <= {
            "event_code",
            "occurred_at",
            "authentication_method",
            "client_hint",
        }
        for item in response.json()["items"]
    )


def test_replacing_factors_revokes_existing_password_totp_sessions(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    totp = import_module("packages.backend.identity.totp")
    webauthn_access = _webauthn_access_token(actor)
    first_password = "第一套合格备用密码 2026"
    first_secret = _enable_backup(
        client,
        password=first_password,
    )
    old_backup_access = _login_with_backup(
        client,
        password=first_password,
        totp_secret=first_secret,
    )
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        version_before = connection.execute(
            """SELECT backup_auth_version FROM users
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        proof = connection.execute(
            """UPDATE refresh_tokens SET backup_reauthenticated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method='password_totp' AND revoked_at IS NULL
            RETURNING id""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
    assert version_before is not None
    assert proof is not None

    replacement = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert replacement.status_code == 201
    replacement_code = totp.generate_totp(
        replacement.json()["totp_secret"],
        timestamp=datetime.now(UTC).timestamp(),
    )
    replaced = client.post(
        f"/api/v1/auth/backup/enrollment/{replacement.json()['enrollment_id']}/verify",
        json={
            "password": "第二套合格备用密码 2026",
            "totp_code": replacement_code,
        },
        headers=csrf_headers(client),
    )
    assert replaced.status_code == 200

    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        version_after = connection.execute(
            """SELECT backup_auth_version FROM users
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        backup_sessions = connection.execute(
            """SELECT revoked_at, backup_reauthenticated_at
            FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method='password_totp'""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchall()
        active_webauthn_sessions = connection.execute(
            """SELECT count(*) FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method='webauthn' AND revoked_at IS NULL""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        security_event_codes = connection.execute(
            """SELECT event_code FROM audit_events
            WHERE kindergarten_id=%s AND actor_user_id=%s
              AND event_code IN ('auth.backup_enabled','auth.backup_changed')
            ORDER BY occurred_at""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchall()
    assert version_after == (version_before[0] + 1,)
    assert backup_sessions
    assert all(revoked_at is not None for revoked_at, _proof in backup_sessions)
    assert all(proof_at is None for _revoked_at, proof_at in backup_sessions)
    assert active_webauthn_sessions == (1,)
    assert [row[0] for row in security_event_codes] == [
        "auth.backup_enabled",
        "auth.backup_changed",
    ]
    webauthn_session = _identity_service(client).authenticate_access(webauthn_access)
    assert webauthn_session.authentication_method == "webauthn"
    with pytest.raises(IdentityError) as exc_info:
        _identity_service(client).authenticate_access(old_backup_access)
    assert exc_info.value.status_code == 401


def test_backup_feature_does_not_weaken_emergency_recovery_contract() -> None:
    openapi = yaml.safe_load(
        Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
    )
    paths = set(openapi["paths"])

    assert {
        "/api/v1/auth/recovery/requests",
        "/api/v1/users/{user_id}/recovery-requests/{recovery_request_id}/approve",
        "/api/v1/auth/recovery/registration/options",
        "/api/v1/auth/recovery/registration/verify",
    } <= paths
    recovery = openapi["paths"]["/api/v1/auth/recovery/requests"]["post"]
    assert "password" not in str(recovery).lower()
    assert "totp" not in str(recovery).lower()
