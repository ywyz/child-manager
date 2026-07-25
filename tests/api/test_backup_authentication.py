# ruff: noqa: F811

import json
from base64 import urlsafe_b64encode
from datetime import UTC, datetime
from importlib import import_module
from types import SimpleNamespace
from uuid import UUID

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx2 import Response

from apps.api.dependencies import identity_service
from packages.backend.identity.auth_throttle import subject_throttle_source
from packages.backend.identity.repository import IdentityRepository
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)

GENERIC_FAILURE = {
    "code": "auth.backup_authentication_failed",
    "message": "账号、密码或动态验证码不正确。",
    "field_errors": [],
}


def _generic_failure_payload(response: Response) -> dict[str, object]:
    payload = response.json()
    UUID(payload.pop("request_id"))
    return payload


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


def _request(
    client: TestClient,
    *,
    identifier: str,
    password: str,
    totp_code: str,
):
    return client.post(
        "/api/v1/auth/backup/authentication",
        json={
            "identifier": identifier,
            "password": password,
            "totp_code": totp_code,
        },
        headers=csrf_headers(client),
    )


def _enable_backup(client: TestClient) -> tuple[str, str]:
    started = client.post(
        "/api/v1/auth/backup/enrollment",
        headers=csrf_headers(client),
    )
    assert started.status_code == 201
    secret = started.json()["totp_secret"]
    totp = import_module("packages.backend.identity.totp")
    # 先消费前一时间步, 给当前与下一时间步分别留给登录和重新验证。
    code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp() - 30)
    verified = client.post(
        f"/api/v1/auth/backup/enrollment/{started.json()['enrollment_id']}/verify",
        json={
            "password": "合格的备用登录密码 2026",
            "totp_code": code,
        },
        headers=csrf_headers(client),
    )
    assert verified.status_code == 200
    return secret, code


def test_backup_authentication_requires_both_factors_in_one_request(
    passkey_client: TestClient,
) -> None:
    headers = csrf_headers(passkey_client)
    password_only = passkey_client.post(
        "/api/v1/auth/backup/authentication",
        json={"identifier": "admin", "password": "password-only"},
        headers=headers,
    )
    totp_only = passkey_client.post(
        "/api/v1/auth/backup/authentication",
        json={"identifier": "admin", "totp_code": "000000"},
        headers=headers,
    )

    assert password_only.status_code == 422
    assert totp_only.status_code == 422
    assert password_only.headers.get_list("set-cookie") == []
    assert totp_only.headers.get_list("set-cookie") == []


def test_unknown_password_totp_and_unconfigured_failures_are_indistinguishable(
    passkey_client: TestClient,
) -> None:
    responses = [
        _request(
            passkey_client,
            identifier="unknown-account",
            password="wrong-password",
            totp_code="000000",
        ),
        _request(
            passkey_client,
            identifier="admin",
            password="wrong-password",
            totp_code="000000",
        ),
    ]

    assert [response.status_code for response in responses] == [401, 401]
    assert [_generic_failure_payload(response) for response in responses] == [
        GENERIC_FAILURE,
        GENERIC_FAILURE,
    ]
    assert all(response.headers.get_list("set-cookie") == [] for response in responses)


def test_unknown_account_runs_both_virtual_factor_paths(
    passkey_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service_module = import_module("packages.backend.identity.service")
    calls: list[tuple[str, str]] = []

    def verify_virtual_password(password: str, password_hash: str) -> bool:
        calls.append(("password", password_hash))
        assert password == "wrong-password"
        assert password_hash.startswith("$argon2id$")
        return False

    def verify_virtual_totp(
        secret: str,
        code: str,
        *,
        timestamp: float,
        last_accepted_counter: int | None,
    ) -> None:
        del timestamp
        calls.append(("totp", secret))
        assert code == "000000"
        assert last_accepted_counter is None
        return None

    monkeypatch.setattr(service_module, "verify_password", verify_virtual_password)
    monkeypatch.setattr(service_module, "verify_totp", verify_virtual_totp)

    response = _request(
        passkey_client,
        identifier="unknown-account",
        password="wrong-password",
        totp_code="000000",
    )

    assert response.status_code == 401
    assert [name for name, _material in calls] == ["password", "totp"]


def test_configured_wrong_password_and_wrong_totp_share_generic_failure(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    secret, _initial_code = _enable_backup(client)
    totp = import_module("packages.backend.identity.totp")
    valid_code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp())
    invalid_code = "000000" if valid_code != "000000" else "999999"

    responses = [
        _request(
            client,
            identifier="admin",
            password="wrong-password",
            totp_code=valid_code,
        ),
        _request(
            client,
            identifier="admin",
            password="合格的备用登录密码 2026",
            totp_code=invalid_code,
        ),
    ]

    assert [response.status_code for response in responses] == [401, 401]
    assert [_generic_failure_payload(response) for response in responses] == [
        GENERIC_FAILURE,
        GENERIC_FAILURE,
    ]
    assert all(response.headers.get_list("set-cookie") == [] for response in responses)


def test_backup_authentication_uses_independent_three_layer_rate_limits(
    passkey_client: TestClient,
) -> None:
    statuses = [
        _request(
            passkey_client,
            identifier="unknown-account",
            password="wrong-password",
            totp_code="000000",
        ).status_code
        for _attempt in range(3)
    ]

    assert statuses == [401, 401, 429]


def test_backup_account_bucket_uses_normalized_digest_and_does_not_block_passkeys(
    passkey_client: TestClient,
) -> None:
    application = passkey_client.app
    assert isinstance(application, FastAPI)
    throttle = application.state.auth_throttle
    now = application.state.clock()
    account_bucket = subject_throttle_source(
        purpose="backup_authentication",
        subject="admin",
    )
    for _attempt in range(2):
        throttle.record_failure(
            source=account_bucket,
            purpose="backup_authentication",
            now=now,
        )

    blocked = _request(
        passkey_client,
        identifier=" ADMIN ",
        password="wrong-password",
        totp_code="000000",
    )
    passkey_still_available = passkey_client.post(
        "/api/v1/auth/authentication/options",
        headers=csrf_headers(passkey_client),
    )

    assert blocked.status_code == 429
    assert passkey_still_available.status_code == 200


def test_totp_replay_cannot_create_a_second_backup_session(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    secret, _initial_code = _enable_backup(client)
    totp = import_module("packages.backend.identity.totp")
    code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp())
    first = _request(
        client,
        identifier="admin",
        password="合格的备用登录密码 2026",
        totp_code=code,
    )
    replayed = _request(
        client,
        identifier="admin",
        password="合格的备用登录密码 2026",
        totp_code=code,
    )

    assert first.status_code == 204
    assert len(first.headers.get_list("set-cookie")) >= 2
    assert replayed.status_code == 401
    assert _generic_failure_payload(replayed) == GENERIC_FAILURE


def test_backup_login_creates_versioned_ordinary_session_and_version_change_invalidates_it(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    secret, _initial_code = _enable_backup(client)
    totp = import_module("packages.backend.identity.totp")
    code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp())

    authenticated = _request(
        client,
        identifier="admin",
        password="合格的备用登录密码 2026",
        totp_code=code,
    )
    assert authenticated.status_code == 204
    application = client.app
    assert isinstance(application, FastAPI)
    service_override = application.dependency_overrides[identity_service]
    application.dependency_overrides.clear()
    application.dependency_overrides[identity_service] = service_override

    assert client.get("/api/v1/auth/me").status_code == 200
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        row = connection.execute(
            """SELECT rt.authentication_method, rt.backup_verified_at,
                      rt.backup_reauthenticated_at, rt.backup_auth_version,
                      u.backup_auth_version
               FROM refresh_tokens rt
               JOIN users u ON u.kindergarten_id=rt.kindergarten_id AND u.id=rt.user_id
               WHERE rt.kindergarten_id=%s AND rt.user_id=%s
                 AND rt.authentication_method='password_totp'
                 AND rt.revoked_at IS NULL
               ORDER BY rt.issued_at DESC LIMIT 1""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone()
        assert row is not None
        assert row[0] == "password_totp"
        assert row[1] is not None
        assert row[2] is None
        assert row[3] == row[4]
        connection.execute(
            """UPDATE users SET backup_auth_version=backup_auth_version+1
               WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, actor.user_id),
        )

    assert client.get("/api/v1/auth/me").status_code == 401


def test_totp_counter_and_session_creation_roll_back_together(
    admin_client: tuple[TestClient, ActorFixture],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _actor = admin_client
    secret, _initial_code = _enable_backup(client)
    totp = import_module("packages.backend.identity.totp")
    code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp())
    original_create_refresh = IdentityRepository.create_refresh

    def fail_session_creation(self: IdentityRepository, **_kwargs: object) -> None:
        del self
        raise RuntimeError("test transaction rollback")

    monkeypatch.setattr(IdentityRepository, "create_refresh", fail_session_creation)
    with pytest.raises(RuntimeError, match="test transaction rollback"):
        _request(
            client,
            identifier="admin",
            password="合格的备用登录密码 2026",
            totp_code=code,
        )
    monkeypatch.setattr(IdentityRepository, "create_refresh", original_create_refresh)
    retried = _request(
        client,
        identifier="admin",
        password="合格的备用登录密码 2026",
        totp_code=code,
    )

    assert retried.status_code == 204


def test_backup_reauthentication_only_grants_add_passkey_proof(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, actor = admin_client
    secret, _initial_code = _enable_backup(client)
    totp = import_module("packages.backend.identity.totp")
    login_code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp())
    authenticated = _request(
        client,
        identifier="admin",
        password="合格的备用登录密码 2026",
        totp_code=login_code,
    )
    assert authenticated.status_code == 204
    application = client.app
    assert isinstance(application, FastAPI)
    service_override = application.dependency_overrides[identity_service]
    application.dependency_overrides.clear()
    application.dependency_overrides[identity_service] = service_override
    reauth_code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp() + 30)

    reauthenticated = client.post(
        "/api/v1/auth/backup/reauthentication",
        json={
            "password": "合格的备用登录密码 2026",
            "totp_code": reauth_code,
        },
        headers=csrf_headers(client),
    )

    assert reauthenticated.status_code == 204
    assert (
        client.delete(
            "/api/v1/auth/backup",
            headers=csrf_headers(client),
        ).status_code
        == 403
    )
    protected_responses = {
        "rename_credential": client.patch(
            f"/api/v1/auth/credentials/{UUID(int=1)}",
            json={"label": "不得修改"},
            headers=csrf_headers(client),
        ),
        "rotate_recovery_code": client.post(
            "/api/v1/auth/recovery-code/rotate",
            headers=csrf_headers(client),
        ),
        "create_account": client.post(
            "/api/v1/users",
            json={
                "username": "proof-matrix-teacher",
                "display_name": "证明矩阵教师",
                "role_codes": ["teacher"],
            },
            headers=csrf_headers(client),
        ),
        "change_roles": client.put(
            f"/api/v1/users/{actor.user_id}/roles",
            json={"role_codes": ["admin"]},
            headers=csrf_headers(client),
        ),
        "issue_invitation": client.post(
            f"/api/v1/users/{actor.user_id}/invitations",
            json={"expires_in_hours": 24},
            headers=csrf_headers(client),
        ),
        "approve_recovery": client.post(
            f"/api/v1/users/{actor.user_id}/recovery-requests/{UUID(int=2)}/approve",
            json={
                "verification_confirmed": True,
                "verification_note": "不得批准",
            },
            headers=csrf_headers(client),
        ),
    }
    assert {
        operation: (response.status_code, response.json().get("code"))
        for operation, response in protected_responses.items()
    } == {operation: (403, "auth.step_up_required") for operation in protected_responses}

    options = client.post(
        "/api/v1/auth/credentials/registration/options",
        headers=csrf_headers(client),
    )
    assert options.status_code == 200
    credential_raw_id = b"backup-proof-single-use"
    monkeypatch.setattr(
        "packages.backend.identity.service.verify_registration",
        lambda **_kwargs: SimpleNamespace(
            credential_id=credential_raw_id,
            credential_public_key=b"backup-proof-cose",
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
                credential_id=_base64url(credential_raw_id),
                challenge=options.json()["publicKey"]["challenge"],
            ),
            "label": "新设备通行密钥",
        },
        headers=csrf_headers(client),
    )

    assert verified.status_code == 201
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT backup_reauthenticated_at FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method='password_totp' AND revoked_at IS NULL
            ORDER BY issued_at DESC LIMIT 1""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone() == (None,)
        assert connection.execute(
            """SELECT count(*) FROM audit_events
            WHERE kindergarten_id=%s AND actor_user_id=%s
              AND event_code='auth.passkey_added_from_backup'""",
            (actor.kindergarten_id, actor.user_id),
        ).fetchone() == (1,)

    reused = client.post(
        "/api/v1/auth/credentials/registration/options",
        headers=csrf_headers(client),
    )
    assert reused.status_code == 403
    assert reused.json()["code"] == "auth.backup_reauthentication_required"
