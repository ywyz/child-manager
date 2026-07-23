# ruff: noqa: F811

import json
from base64 import urlsafe_b64encode
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.dependencies import current_session
from packages.backend.identity.tokens import hash_refresh_token
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _base64url(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _registration_credential(*, credential_id: str, challenge: str) -> dict[str, object]:
    client_data = json.dumps(
        {
            "type": "webauthn.create",
            "challenge": challenge,
            "origin": "http://testserver",
            "crossOrigin": False,
        },
        separators=(",", ":"),
    ).encode()
    return {
        "id": credential_id,
        "rawId": credential_id,
        "type": "public-key",
        "response": {
            "clientDataJSON": _base64url(client_data),
            "attestationObject": _base64url(b"stub-attestation"),
            "transports": ["internal"],
        },
        "clientExtensionResults": {},
    }


def _insert_credential(
    connection: psycopg.Connection[tuple[object, ...]],
    *,
    kindergarten_id: UUID,
    user_id: UUID,
    label: str,
) -> UUID:
    credential_id = uuid4()
    connection.execute(
        """INSERT INTO webauthn_credentials
        (id, kindergarten_id, user_id, credential_id, public_key_cose, sign_count,
         transports, backup_eligible, backup_state, label, created_via)
        VALUES (%s,%s,%s,%s,%s,0,%s,false,false,%s,%s)""",
        (
            credential_id,
            kindergarten_id,
            user_id,
            uuid4().bytes,
            b"test-cose-key",
            '["internal"]',
            label,
            "self_add",
        ),
    )
    return credential_id


def test_credential_management_requires_authenticated_recent_verification(
    passkey_client: TestClient,
) -> None:
    credential_id = "00000000-0000-7000-8000-000000000001"
    headers = csrf_headers(passkey_client)

    responses = [
        passkey_client.get("/api/v1/auth/credentials"),
        passkey_client.post(
            "/api/v1/auth/credentials/registration/options",
            headers=headers,
        ),
        passkey_client.patch(
            f"/api/v1/auth/credentials/{credential_id}",
            json={"label": "备用安全密钥"},
            headers=headers,
        ),
        passkey_client.delete(
            f"/api/v1/auth/credentials/{credential_id}",
            headers=headers,
        ),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401]


def test_user_can_list_name_and_revoke_only_a_non_last_credential_after_step_up(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"
            ).fetchall()
        }
        assert "webauthn_credentials" in tables
        first_id = _insert_credential(
            connection,
            kindergarten_id=actor.kindergarten_id,
            user_id=actor.user_id,
            label="内置通行密钥",
        )
        second_id = _insert_credential(
            connection,
            kindergarten_id=actor.kindergarten_id,
            user_id=actor.user_id,
            label="备用安全密钥",
        )

    listed = client.get("/api/v1/auth/credentials")
    renamed = client.patch(
        f"/api/v1/auth/credentials/{first_id}",
        json={"label": "办公电脑"},
        headers=csrf_headers(client),
    )
    revoked = client.delete(
        f"/api/v1/auth/credentials/{first_id}",
        headers=csrf_headers(client),
    )
    last = client.delete(
        f"/api/v1/auth/credentials/{second_id}",
        headers=csrf_headers(client),
    )

    assert listed.status_code == 200
    assert {item["id"] for item in listed.json()["items"]} == {str(first_id), str(second_id)}
    assert renamed.status_code == 200
    assert renamed.json()["label"] == "办公电脑"
    assert revoked.status_code == 204
    assert last.status_code == 409


def test_admin_cannot_revoke_last_active_admin_last_credential(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        credential_id = _insert_credential(
            connection,
            kindergarten_id=actor.kindergarten_id,
            user_id=actor.user_id,
            label="最后管理员唯一凭据",
        )

    response = client.delete(
        f"/api/v1/users/{actor.user_id}/credentials/{credential_id}",
        headers=csrf_headers(client),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "auth.last_credential"
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            "SELECT revoked_at FROM webauthn_credentials WHERE id=%s",
            (credential_id,),
        ).fetchone() == (None,)
        assert connection.execute(
            """SELECT revoked_at FROM refresh_tokens
            WHERE kindergarten_id=%s AND token_family_id=%s""",
            (actor.kindergarten_id, actor.session_id),
        ).fetchone() == (None,)
        assert connection.execute(
            """SELECT count(*) FROM account_invitations
            WHERE kindergarten_id=%s AND user_id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone() == (0,)


def test_self_add_registration_is_bound_to_issuing_refresh_family(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, actor = admin_client
    options = client.post(
        "/api/v1/auth/credentials/registration/options",
        headers=csrf_headers(client),
    )
    assert options.status_code == 200
    other_family_id = uuid4()
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at,
             expires_at, last_reauthenticated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                uuid4(),
                actor.kindergarten_id,
                actor.user_id,
                other_family_id,
                hash_refresh_token("other-family-refresh"),
                now,
                now + timedelta(days=7),
                now,
            ),
        )
    other_session = SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=actor.kindergarten_id,
            status="active",
            is_active=True,
        ),
        role_codes=["admin"],
        token_family_id=other_family_id,
        session_id=other_family_id,
        last_reauthenticated_at=now,
    )
    app = cast(FastAPI, client.app)
    app.dependency_overrides[current_session] = lambda: other_session
    new_credential_raw_id = b"family-bound-credential"
    monkeypatch.setattr(
        "packages.backend.identity.service.verify_registration",
        lambda **_kwargs: SimpleNamespace(
            credential_id=new_credential_raw_id,
            credential_public_key=b"family-bound-cose",
            sign_count=0,
            aaguid=None,
            credential_device_type=SimpleNamespace(value="single_device"),
            credential_backed_up=False,
        ),
    )

    verified = client.post(
        "/api/v1/auth/credentials/registration/verify",
        json={
            "ceremony_id": options.json()["ceremony_id"],
            "credential": _registration_credential(
                credential_id=_base64url(new_credential_raw_id),
                challenge=options.json()["publicKey"]["challenge"],
            ),
        },
        headers=csrf_headers(client),
    )

    assert verified.status_code == 410
    assert verified.json()["code"] == "identity.material_unavailable"
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            """SELECT count(*) FROM webauthn_credentials
            WHERE kindergarten_id=%s AND user_id=%s""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT consumed_at FROM webauthn_challenges WHERE id=%s",
            (options.json()["ceremony_id"],),
        ).fetchone() == (None,)

    original_session = SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=actor.kindergarten_id,
            status="active",
            is_active=True,
        ),
        role_codes=["admin"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=now,
    )
    app.dependency_overrides[current_session] = lambda: original_session
    accepted = client.post(
        "/api/v1/auth/credentials/registration/verify",
        json={
            "ceremony_id": options.json()["ceremony_id"],
            "credential": _registration_credential(
                credential_id=_base64url(new_credential_raw_id),
                challenge=options.json()["publicKey"]["challenge"],
            ),
        },
        headers=csrf_headers(client),
    )
    assert accepted.status_code == 201


def test_admin_revoking_teacher_last_credential_revokes_sessions_and_reinvites_atomically(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    created = client.post(
        "/api/v1/users",
        json={
            "username": "credential-teacher",
            "display_name": "凭据教师",
            "role_codes": ["teacher"],
        },
        headers=csrf_headers(client),
    )
    assert created.status_code == 201
    teacher_id = UUID(created.json()["id"])
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            "UPDATE users SET status='active', activated_at=%s WHERE id=%s",
            (now, teacher_id),
        )
        credential_id = _insert_credential(
            connection,
            kindergarten_id=actor.kindergarten_id,
            user_id=teacher_id,
            label="教师唯一凭据",
        )
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                uuid4(),
                actor.kindergarten_id,
                teacher_id,
                uuid4(),
                hash_refresh_token("teacher-refresh"),
                now,
                now + timedelta(days=7),
            ),
        )

    response = client.delete(
        f"/api/v1/users/{teacher_id}/credentials/{credential_id}",
        headers=csrf_headers(client),
    )

    assert response.status_code == 200
    assert response.json()["credential_id"] == str(credential_id)
    assert response.json()["sessions_revoked"] == 1
    reinvitation = response.json()["reinvitation"]
    assert reinvitation["invitation_token"]
    assert response.headers.get_list("set-cookie") == []
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        state = connection.execute(
            """SELECT u.status, c.revoked_at IS NOT NULL,
            count(rt.revoked_at), count(ai.id)
            FROM users u
            JOIN webauthn_credentials c
              ON c.kindergarten_id=u.kindergarten_id AND c.user_id=u.id
            LEFT JOIN refresh_tokens rt
              ON rt.kindergarten_id=u.kindergarten_id AND rt.user_id=u.id
            LEFT JOIN account_invitations ai
              ON ai.kindergarten_id=u.kindergarten_id AND ai.user_id=u.id
             AND ai.revoked_at IS NULL AND ai.consumed_at IS NULL
            WHERE u.kindergarten_id=%s AND u.id=%s AND c.id=%s
            GROUP BY u.status, c.revoked_at""",
            (actor.kindergarten_id, teacher_id, credential_id),
        ).fetchone()
    assert state == ("pending_registration", True, 1, 1)
