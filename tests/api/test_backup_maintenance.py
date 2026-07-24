# ruff: noqa: F811

from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path

import psycopg
import yaml
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
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
) -> None:
    client, _actor = admin_client
    response = client.delete(
        "/api/v1/auth/backup",
        headers=csrf_headers(client),
    )

    assert response.status_code == 403
    assert response.json()["code"] == "auth.backup_required_for_admin"


def test_backup_security_events_are_current_user_only_and_bounded(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    response = client.get("/api/v1/auth/security-events")

    assert response.status_code == 200
    assert len(response.json()["items"]) <= 20
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
    client, _actor = admin_client
    totp = import_module("packages.backend.identity.totp")
    first = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert first.status_code == 201
    first_code = totp.generate_totp(
        first.json()["totp_secret"],
        timestamp=datetime.now(UTC).timestamp(),
    )
    enabled = client.post(
        f"/api/v1/auth/backup/enrollment/{first.json()['enrollment_id']}/verify",
        json={
            "password": "第一套合格备用密码 2026",
            "totp_code": first_code,
        },
        headers=csrf_headers(client),
    )
    assert enabled.status_code == 200
    login_code = totp.generate_totp(
        first.json()["totp_secret"],
        timestamp=datetime.now(UTC).timestamp() + 30,
    )
    logged_in = client.post(
        "/api/v1/auth/backup/authentication",
        json={
            "identifier": "admin",
            "password": "第一套合格备用密码 2026",
            "totp_code": login_code,
        },
        headers=csrf_headers(client),
    )
    assert logged_in.status_code == 204

    replacement = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert replacement.status_code == 201
    replacement_code = totp.generate_totp(
        replacement.json()["totp_secret"],
        timestamp=datetime.now(UTC).timestamp() + 60,
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

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        active_backup_sessions = connection.execute(
            """SELECT count(*) FROM refresh_tokens
            WHERE authentication_method='password_totp' AND revoked_at IS NULL"""
        ).fetchone()
    assert active_backup_sessions == (0,)


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
