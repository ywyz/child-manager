# ruff: noqa: F811

from base64 import urlsafe_b64decode
from datetime import UTC, datetime
from uuid import UUID, uuid4

import psycopg
from fastapi.testclient import TestClient

from packages.backend.identity.secret_tokens import SecretPurpose, issue_secret
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)

GENERIC_RECOVERY_MESSAGE = "如果账号和恢复材料有效，我们会按既定带外方式继续核验。"


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _secret_bytes(value: object) -> bytes:
    text = str(value)
    return urlsafe_b64decode(text + "=" * (-len(text) % 4))


def test_recovery_request_is_generic_for_unknown_and_invalid_material(
    passkey_client: TestClient,
) -> None:
    response = passkey_client.post(
        "/api/v1/auth/recovery/requests",
        json={"login": "unknown", "recovery_code": "invalid-recovery-code"},
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 202
    assert response.json() == {"message": GENERIC_RECOVERY_MESSAGE}
    assert response.headers.get_list("set-cookie") == []


def test_recovery_registration_never_establishes_a_session(passkey_client: TestClient) -> None:
    response = passkey_client.post(
        "/api/v1/auth/recovery/registration/options",
        json={"enrollment_token": "expired-or-invalid-enrollment"},
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 410
    assert response.headers.get_list("set-cookie") == []


def test_recovery_code_rotation_requires_authenticated_step_up(passkey_client: TestClient) -> None:
    response = passkey_client.post(
        "/api/v1/auth/recovery-code/rotate",
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 401


def test_valid_recovery_code_still_requires_admin_approval_before_registration(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    created = client.post(
        "/api/v1/users",
        json={
            "username": "recovery-teacher",
            "display_name": "恢复教师",
            "role_codes": ["teacher"],
        },
        headers=csrf_headers(client),
    )
    assert created.status_code == 201
    teacher_id = UUID(created.json()["id"])
    recovery = issue_secret(SecretPurpose.RECOVERY_CODE, random_bytes=lambda size: b"r" * size)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            "UPDATE users SET status='active', activated_at=%s WHERE id=%s",
            (datetime.now(UTC), teacher_id),
        )
        connection.execute(
            """INSERT INTO recovery_codes
            (id, kindergarten_id, user_id, code_hash, issued_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (
                uuid4(),
                actor.kindergarten_id,
                teacher_id,
                recovery.record.digest,
                datetime.now(UTC),
            ),
        )

    submitted = client.post(
        "/api/v1/auth/recovery/requests",
        json={"login": "recovery-teacher", "recovery_code": recovery.secret},
        headers=csrf_headers(client),
    )
    assert submitted.status_code == 202
    assert submitted.json() == {"message": GENERIC_RECOVERY_MESSAGE}
    assert submitted.headers.get_list("set-cookie") == []

    pending = client.get(f"/api/v1/users/{teacher_id}/recovery-requests")
    assert pending.status_code == 200
    assert len(pending.json()["items"]) == 1
    recovery_request_id = pending.json()["items"][0]["id"]
    approved = client.post(
        f"/api/v1/users/{teacher_id}/recovery-requests/{recovery_request_id}/approve",
        json={"verification_confirmed": True, "verification_note": "已电话核验"},
        headers=csrf_headers(client),
    )
    assert approved.status_code == 200
    assert len(_secret_bytes(approved.json()["enrollment_token"])) >= 16
    assert approved.headers.get_list("set-cookie") == []

    options = client.post(
        "/api/v1/auth/recovery/registration/options",
        json={"enrollment_token": approved.json()["enrollment_token"]},
        headers=csrf_headers(client),
    )
    assert options.status_code == 200
    assert options.json()["publicKey"]["userVerification"] == "required"
    assert options.headers.get_list("set-cookie") == []


def test_authenticated_step_up_rotation_revokes_old_code_and_returns_new_code_once(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    old = issue_secret(SecretPurpose.RECOVERY_CODE, random_bytes=lambda size: b"o" * size)
    old_id = uuid4()
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"
            ).fetchall()
        }
        assert "recovery_codes" in tables
        connection.execute(
            """INSERT INTO recovery_codes
            (id, kindergarten_id, user_id, code_hash, issued_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (
                old_id,
                actor.kindergarten_id,
                actor.user_id,
                old.record.digest,
                datetime.now(UTC),
            ),
        )

    response = client.post(
        "/api/v1/auth/recovery-code/rotate",
        headers=csrf_headers(client),
    )

    assert response.status_code == 200
    assert len(_secret_bytes(response.json()["recovery_code"])) >= 16
    assert response.headers.get_list("set-cookie") == []
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        rows = connection.execute(
            """SELECT id, revoked_at, replaced_by_id FROM recovery_codes
            WHERE kindergarten_id=%s AND user_id=%s ORDER BY issued_at""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchall()
    assert len(rows) == 2
    assert rows[0][0] == old_id
    assert rows[0][1] is not None
    assert rows[0][2] == rows[1][0]
    assert rows[1][1] is None
