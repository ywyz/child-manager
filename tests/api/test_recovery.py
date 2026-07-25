# ruff: noqa: F811

import json
from base64 import b32encode, urlsafe_b64decode, urlsafe_b64encode
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.dependencies import identity_service
from packages.backend.identity.auth_throttle import subject_throttle_source
from packages.backend.identity.passwords import hash_password
from packages.backend.identity.secret_encryption import encrypt_totp_secret
from packages.backend.identity.secret_tokens import SecretPurpose, issue_secret
from packages.backend.identity.service import IdentityError, IdentityService
from packages.backend.identity.tokens import hash_refresh_token
from packages.backend.identity.totp import generate_totp
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


def _base64url(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _identity_service(client: TestClient) -> IdentityService:
    application = cast(FastAPI, client.app)
    dependency = application.dependency_overrides[identity_service]
    return cast(IdentityService, dependency())


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


def _authentication_credential(*, credential_id: str, challenge: str) -> dict[str, object]:
    client_data = json.dumps(
        {
            "type": "webauthn.get",
            "challenge": challenge,
            "origin": "http://testserver",
            "crossOrigin": False,
        },
        separators=(",", ":"),
    ).encode()
    authenticator_data = sha256(b"testserver").digest() + bytes([0x05]) + (0).to_bytes(4)
    return {
        "id": credential_id,
        "rawId": credential_id,
        "type": "public-key",
        "response": {
            "clientDataJSON": _base64url(client_data),
            "authenticatorData": _base64url(authenticator_data),
            "signature": _base64url(b"stub-signature"),
            "userHandle": None,
        },
        "clientExtensionResults": {},
    }


def test_recovery_request_is_generic_for_unknown_and_invalid_material(
    passkey_client: TestClient,
) -> None:
    response = passkey_client.post(
        "/api/v1/auth/recovery/requests",
        json={"login": "unknown", "recovery_code": "invalid-recovery-code-material"},
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 202
    assert response.json() == {"message": GENERIC_RECOVERY_MESSAGE}
    assert response.headers.get_list("set-cookie") == []


def test_invalid_recovery_request_material_is_rate_limited_without_enumeration(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    passkey_client, _actor = admin_client
    payload = {"login": "unknown", "recovery_code": "invalid-recovery-code-material"}
    statuses: list[int] = []
    for forged_source in ("198.51.100.1", "203.0.113.2", "192.0.2.3"):
        headers = csrf_headers(passkey_client)
        headers.update(
            {
                "X-Child-Manager-Client-IP": forged_source,
                "X-Forwarded-For": forged_source,
            }
        )
        response = passkey_client.post(
            "/api/v1/auth/recovery/requests",
            json=payload,
            headers=headers,
        )
        statuses.append(response.status_code)
        if response.status_code == 202:
            assert response.json() == {"message": GENERIC_RECOVERY_MESSAGE}
            assert payload["login"] not in response.text
            assert payload["recovery_code"] not in response.text

    assert statuses == [202, 202, 429]
    native_url = _native_url(isolated_database_url)
    with psycopg.connect(native_url) as connection:
        audits = connection.execute(
            """SELECT event_code, outcome, resource_type, resource_id, metadata::text
            FROM audit_events WHERE outcome='failure' ORDER BY occurred_at"""
        ).fetchall()
    assert len(audits) == 2
    assert all(
        row[:4] == ("identity.recovery_requested", "failure", "authorization", None)
        for row in audits
    )
    assert all(payload["login"] not in row[4] for row in audits)
    assert all(payload["recovery_code"] not in row[4] for row in audits)


def test_recovery_account_bucket_applies_across_recovery_code_guesses(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    app = cast(FastAPI, client.app)
    throttle = app.state.auth_throttle
    now = app.state.clock()
    subject_source = subject_throttle_source(purpose="recovery_request", subject="unknown")
    for _attempt in range(2):
        throttle.record_failure(
            source=subject_source,
            purpose="recovery_request",
            now=now,
        )

    response = client.post(
        "/api/v1/auth/recovery/requests",
        json={
            "login": "unknown",
            "recovery_code": "different-invalid-recovery-code",
        },
        headers=csrf_headers(client),
    )

    assert response.status_code == 429


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


@pytest.mark.parametrize(
    ("role_code", "username", "display_name"),
    [
        ("teacher", "recovery-teacher", "恢复教师"),
        ("admin", "recovery-admin", "恢复管理员"),
    ],
)
def test_valid_recovery_code_still_requires_admin_approval_before_registration(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    role_code: str,
    username: str,
    display_name: str,
) -> None:
    client, actor = admin_client
    created = client.post(
        "/api/v1/users",
        json={
            "username": username,
            "display_name": display_name,
            "role_codes": [role_code],
        },
        headers=csrf_headers(client),
    )
    assert created.status_code == 201
    recovered_user_id = UUID(created.json()["id"])
    invitation = client.post(
        f"/api/v1/users/{recovered_user_id}/invitations",
        json={"expires_in_hours": 24},
        headers=csrf_headers(client),
    )
    assert invitation.status_code == 201
    old_invitation_token = invitation.json()["invitation_token"]
    recovery = issue_secret(SecretPurpose.RECOVERY_CODE, random_bytes=lambda size: b"r" * size)
    old_credential_raw_id = b"old-recovery-credential"
    old_credential_id = uuid4()
    old_refresh = "old-recovery-refresh"
    old_refresh_id = uuid4()
    old_backup_refresh = "old-recovery-backup-refresh"
    old_backup_refresh_id = uuid4()
    old_backup_credential_id = uuid4()
    old_backup_password = "恢复前仍然有效的备用密码 2026"
    old_totp_secret_bytes = b"t" * 20
    old_totp_secret = b32encode(old_totp_secret_bytes).decode("ascii")
    old_totp_envelope = encrypt_totp_secret(
        old_totp_secret_bytes,
        key=b"\x17" * 32,
        key_id="test-key",
        kindergarten_id=actor.kindergarten_id,
        user_id=recovered_user_id,
        subject_id=old_backup_credential_id,
        subject_kind="credential",
        envelope_version=1,
    )
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            "UPDATE users SET status='active', activated_at=%s WHERE id=%s",
            (now, recovered_user_id),
        )
        connection.execute(
            """INSERT INTO recovery_codes
            (id, kindergarten_id, user_id, code_hash, issued_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (
                uuid4(),
                actor.kindergarten_id,
                recovered_user_id,
                recovery.record.digest,
                now,
            ),
        )
        connection.execute(
            """INSERT INTO webauthn_credentials
            (id, kindergarten_id, user_id, credential_id, public_key_cose, sign_count,
             transports, backup_eligible, backup_state, label, created_via)
            VALUES (%s,%s,%s,%s,%s,0,%s,false,false,%s,%s)""",
            (
                old_credential_id,
                actor.kindergarten_id,
                recovered_user_id,
                old_credential_raw_id,
                b"old-cose-key",
                '["internal"]',
                "旧通行密钥",
                "self_add",
            ),
        )
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                old_refresh_id,
                actor.kindergarten_id,
                recovered_user_id,
                uuid4(),
                hash_refresh_token(old_refresh),
                now,
                now + timedelta(days=7),
            ),
        )
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at,
             authentication_method, backup_verified_at, backup_auth_version)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'password_totp',%s,1)""",
            (
                old_backup_refresh_id,
                actor.kindergarten_id,
                recovered_user_id,
                uuid4(),
                hash_refresh_token(old_backup_refresh),
                now,
                now + timedelta(days=7),
                now,
            ),
        )
        connection.execute(
            """INSERT INTO backup_auth_credentials
            (id, kindergarten_id, user_id, status, password_hash, password_changed_at,
             totp_ciphertext, totp_nonce, totp_key_id, totp_envelope_version,
             last_accepted_counter, enabled_at)
            VALUES (%s,%s,%s,'enabled',%s,%s,%s,%s,%s,%s,NULL,%s)""",
            (
                old_backup_credential_id,
                actor.kindergarten_id,
                recovered_user_id,
                hash_password(old_backup_password),
                now,
                old_totp_envelope.ciphertext,
                old_totp_envelope.nonce,
                old_totp_envelope.key_id,
                old_totp_envelope.envelope_version,
                now,
            ),
        )

    submitted = client.post(
        "/api/v1/auth/recovery/requests",
        json={"login": username, "recovery_code": recovery.secret},
        headers=csrf_headers(client),
    )
    assert submitted.status_code == 202
    assert submitted.json() == {"message": GENERIC_RECOVERY_MESSAGE}
    assert submitted.headers.get_list("set-cookie") == []

    pending = client.get(f"/api/v1/users/{recovered_user_id}/recovery-requests")
    assert pending.status_code == 200
    assert len(pending.json()["items"]) == 1
    recovery_request_id = pending.json()["items"][0]["id"]
    approved = client.post(
        f"/api/v1/users/{recovered_user_id}/recovery-requests/{recovery_request_id}/approve",
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
    assert options.json()["publicKey"]["authenticatorSelection"]["userVerification"] == "required"
    assert options.headers.get_list("set-cookie") == []

    new_credential_raw_id = b"new-recovery-credential"
    monkeypatch.setattr(
        "packages.backend.identity.service.verify_registration",
        lambda **_kwargs: SimpleNamespace(
            credential_id=new_credential_raw_id,
            credential_public_key=b"new-cose-key",
            sign_count=0,
            aaguid=None,
            credential_device_type=SimpleNamespace(value="single_device"),
            credential_backed_up=False,
        ),
    )
    completed = client.post(
        "/api/v1/auth/recovery/registration/verify",
        json={
            "ceremony_id": options.json()["ceremony_id"],
            "credential": _registration_credential(
                credential_id=_base64url(new_credential_raw_id),
                challenge=options.json()["publicKey"]["challenge"],
            ),
            "label": "恢复后的通行密钥",
        },
        headers=csrf_headers(client),
    )

    assert completed.status_code == 200
    assert completed.json()["sessions_revoked"] == 2
    assert len(_secret_bytes(completed.json()["recovery_code"])) >= 16
    assert completed.headers.get_list("set-cookie") == []
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            """SELECT count(*) FILTER (WHERE revoked_at IS NULL),
                      count(*) FILTER (WHERE revoked_at IS NOT NULL)
            FROM webauthn_credentials WHERE kindergarten_id=%s AND user_id=%s""",
            (actor.kindergarten_id, recovered_user_id),
        ).fetchone() == (1, 1)
        assert connection.execute(
            """SELECT count(*), count(*) FILTER (WHERE revoked_at IS NOT NULL)
            FROM refresh_tokens WHERE kindergarten_id=%s AND user_id=%s""",
            (actor.kindergarten_id, recovered_user_id),
        ).fetchone() == (2, 2)
        assert connection.execute(
            """SELECT status, password_hash, totp_ciphertext, totp_nonce, totp_key_id,
                      totp_envelope_version, last_accepted_counter,
                      revoked_at IS NOT NULL
            FROM backup_auth_credentials
            WHERE kindergarten_id=%s AND user_id=%s""",
            (actor.kindergarten_id, recovered_user_id),
        ).fetchone() == ("revoked", None, None, None, None, None, None, True)
        assert connection.execute(
            """SELECT count(*) FILTER (WHERE revoked_at IS NULL AND consumed_at IS NULL),
                      count(*) FILTER (WHERE revoked_at IS NOT NULL)
            FROM account_invitations WHERE kindergarten_id=%s AND user_id=%s""",
            (actor.kindergarten_id, recovered_user_id),
        ).fetchone() == (0, 1)
        recovery_rows = connection.execute(
            """SELECT id, consumed_at, revoked_at, replaced_by_id
            FROM recovery_codes WHERE kindergarten_id=%s AND user_id=%s ORDER BY issued_at""",
            (actor.kindergarten_id, recovered_user_id),
        ).fetchall()
        assert len(recovery_rows) == 2
        assert recovery_rows[0][1] is not None
        assert recovery_rows[0][2] is not None
        assert recovery_rows[0][3] == recovery_rows[1][0]
        assert recovery_rows[1][1:] == (None, None, None)
        revoked_audits = connection.execute(
            """SELECT event_code, resource_id, metadata->>'reason'
            FROM audit_events
            WHERE kindergarten_id=%s
              AND event_code IN ('identity.credential_revoked','identity.invitation_revoked')
              AND metadata->>'reason'='account_recovered'
            ORDER BY event_code""",
            (actor.kindergarten_id,),
        ).fetchall()
        assert revoked_audits == [
            ("identity.credential_revoked", old_credential_id, "account_recovered"),
            (
                "identity.invitation_revoked",
                UUID(invitation.json()["id"]),
                "account_recovered",
            ),
        ]
        assert connection.execute(
            """SELECT count(*) FROM audit_events
            WHERE kindergarten_id=%s AND actor_user_id=%s
              AND event_code='auth.backup_revoked_by_recovery'""",
            (actor.kindergarten_id, recovered_user_id),
        ).fetchone() == (1,)

    old_invitation = client.post(
        "/api/v1/auth/invitation/registration/options",
        json={"invitation_token": old_invitation_token},
        headers=csrf_headers(client),
    )
    assert old_invitation.status_code == 410

    client.cookies.set("child_manager_refresh", old_refresh)
    old_refresh_attempt = client.post("/api/v1/auth/refresh", headers=csrf_headers(client))
    assert old_refresh_attempt.status_code == 401
    client.cookies.delete("child_manager_refresh")

    old_auth_options = client.post(
        "/api/v1/auth/authentication/options",
        headers=csrf_headers(client),
    )
    assert old_auth_options.status_code == 200
    monkeypatch.setattr(
        "packages.backend.identity.service.verify_authentication",
        lambda **_kwargs: SimpleNamespace(new_sign_count=1),
    )
    old_credential = client.post(
        "/api/v1/auth/authentication/verify",
        json={
            "ceremony_id": old_auth_options.json()["ceremony_id"],
            "credential": _authentication_credential(
                credential_id=_base64url(old_credential_raw_id),
                challenge=old_auth_options.json()["publicKey"]["challenge"],
            ),
        },
        headers=csrf_headers(client),
    )
    assert old_credential.status_code == 401

    old_backup_login = client.post(
        "/api/v1/auth/backup/authentication",
        json={
            "identifier": username,
            "password": old_backup_password,
            "totp_code": generate_totp(
                old_totp_secret,
                timestamp=datetime.now(UTC).timestamp(),
            ),
        },
        headers=csrf_headers(client),
    )
    assert old_backup_login.status_code == 401
    assert old_backup_login.json()["code"] == "auth.backup_authentication_failed"

    old_recovery = client.post(
        "/api/v1/auth/recovery/requests",
        json={"login": username, "recovery_code": recovery.secret},
        headers=csrf_headers(client),
    )
    assert old_recovery.status_code == 202
    requests = client.get(f"/api/v1/users/{recovered_user_id}/recovery-requests")
    assert requests.status_code == 200
    assert [item["status"] for item in requests.json()["items"]] == ["completed"]

    restored_options = client.post(
        "/api/v1/auth/authentication/options",
        headers=csrf_headers(client),
    )
    assert restored_options.status_code == 200
    monkeypatch.setattr(
        "packages.backend.identity.service.verify_authentication",
        lambda **_kwargs: SimpleNamespace(new_sign_count=1),
    )
    restored_login = client.post(
        "/api/v1/auth/authentication/verify",
        json={
            "ceremony_id": restored_options.json()["ceremony_id"],
            "credential": _authentication_credential(
                credential_id=_base64url(new_credential_raw_id),
                challenge=restored_options.json()["publicKey"]["challenge"],
            ),
        },
        headers=csrf_headers(client),
    )
    assert restored_login.status_code == 200
    restored_access = restored_login.cookies.get("child_manager_access")
    assert restored_access is not None
    restored_session = _identity_service(client).authenticate_access(restored_access)
    expected_method = "restricted_enrollment" if role_code == "admin" else "webauthn"
    assert restored_session.authentication_method == expected_method
    if role_code == "admin":
        with pytest.raises(IdentityError) as exc_info:
            IdentityService.require_business_access(restored_session)
        assert exc_info.value.code == "auth.backup_enrollment_required"
    else:
        IdentityService.require_business_access(restored_session)


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


def test_last_admin_recovery_web_approval_requires_cli_without_state_change(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    recovery = issue_secret(SecretPurpose.RECOVERY_CODE, random_bytes=lambda size: b"l" * size)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """INSERT INTO recovery_codes
            (id, kindergarten_id, user_id, code_hash, issued_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (
                uuid4(),
                actor.kindergarten_id,
                actor.user_id,
                recovery.record.digest,
                datetime.now(UTC),
            ),
        )

    submitted = client.post(
        "/api/v1/auth/recovery/requests",
        json={"login": "admin", "recovery_code": recovery.secret},
        headers=csrf_headers(client),
    )
    assert submitted.status_code == 202
    pending = client.get(f"/api/v1/users/{actor.user_id}/recovery-requests")
    assert pending.status_code == 200
    recovery_request_id = pending.json()["items"][0]["id"]

    approved = client.post(
        f"/api/v1/users/{actor.user_id}/recovery-requests/{recovery_request_id}/approve",
        json={"verification_confirmed": True, "verification_note": "普通 Web 管理员核验"},
        headers=csrf_headers(client),
    )

    assert approved.status_code == 409
    assert approved.json()["code"] == "identity.last_admin_recovery_requires_cli"
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            """SELECT status, approved_at, enrollment_token_hash, enrollment_expires_at
            FROM account_recovery_requests WHERE id=%s""",
            (recovery_request_id,),
        ).fetchone() == ("pending_verification", None, None, None)
        assert connection.execute(
            """SELECT count(*) FROM identity_verification_approvals
            WHERE context_type='recovery' AND context_id=%s""",
            (recovery_request_id,),
        ).fetchone() == (0,)
