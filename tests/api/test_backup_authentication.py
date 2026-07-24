# ruff: noqa: F811

from datetime import UTC, datetime
from importlib import import_module

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)

GENERIC_FAILURE = {
    "code": "auth.backup_authentication_failed",
    "message": "账号、密码或动态验证码不正确。",
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
    code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp())
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
    assert [response.json() for response in responses] == [GENERIC_FAILURE, GENERIC_FAILURE]
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


def test_totp_replay_cannot_create_a_second_backup_session(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    _secret, code = _enable_backup(client)
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
    assert replayed.json() == GENERIC_FAILURE


def test_backup_reauthentication_only_grants_add_passkey_proof(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    secret, _initial_code = _enable_backup(client)
    totp = import_module("packages.backend.identity.totp")
    login_code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp() + 30)
    authenticated = _request(
        client,
        identifier="admin",
        password="合格的备用登录密码 2026",
        totp_code=login_code,
    )
    assert authenticated.status_code == 204
    application = client.app
    assert isinstance(application, FastAPI)
    application.dependency_overrides.clear()
    reauth_code = totp.generate_totp(secret, timestamp=datetime.now(UTC).timestamp() + 60)

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
