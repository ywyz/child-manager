# ruff: noqa: F811

import json
from base64 import urlsafe_b64encode
from hashlib import sha256
from uuid import UUID

import psycopg
import pytest
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def _base64url(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _credential(*, credential_id: str, challenge: str) -> dict[str, object]:
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
            "signature": _base64url(b"invalid-signature"),
            "userHandle": None,
        },
        "clientExtensionResults": {},
    }


def test_authentication_options_are_username_less_and_browser_ready(
    passkey_client: TestClient,
) -> None:
    response = passkey_client.post(
        "/api/v1/auth/authentication/options",
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"ceremony_id", "expires_at", "publicKey"}
    assert body["publicKey"]["allowCredentials"] == []
    assert body["publicKey"]["userVerification"] == "required"
    assert body["publicKey"]["timeout"] == 300_000


def test_authentication_options_do_not_increment_failure_limit(
    passkey_client: TestClient,
) -> None:
    responses = [
        passkey_client.post(
            "/api/v1/auth/authentication/options",
            headers=csrf_headers(passkey_client),
        )
        for _index in range(3)
    ]

    assert [response.status_code for response in responses] == [200, 200, 200]


def test_failed_authentication_persists_challenge_failure_and_sanitized_audit(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, _actor = admin_client
    options = client.post(
        "/api/v1/auth/authentication/options",
        headers=csrf_headers(client),
    )
    assert options.status_code == 200
    unknown_credential_id = _base64url(b"failure-persistence-credential")

    failed = client.post(
        "/api/v1/auth/authentication/verify",
        json={
            "ceremony_id": options.json()["ceremony_id"],
            "credential": _credential(
                credential_id=unknown_credential_id,
                challenge=options.json()["publicKey"]["challenge"],
            ),
        },
        headers=csrf_headers(client),
    )

    assert failed.status_code == 401
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            "SELECT failure_count, consumed_at FROM webauthn_challenges WHERE id=%s",
            (options.json()["ceremony_id"],),
        ).fetchone() == (1, None)
        audit = connection.execute(
            """SELECT event_code, outcome, resource_type, resource_id, metadata::text
            FROM audit_events WHERE event_code='identity.authentication_failed'"""
        ).fetchone()
    assert audit is not None
    assert audit[:4] == (
        "identity.authentication_failed",
        "failure",
        "webauthn_challenge",
        UUID(options.json()["ceremony_id"]),
    )
    assert unknown_credential_id not in audit[4]


def test_invalid_authentication_is_generic_and_does_not_enumerate_account(
    passkey_client: TestClient,
) -> None:
    failures: list[dict[str, object]] = []
    credential_ids = ["dW5rbm93bi0x", "dW5rbm93bi0y"]
    for credential_id in credential_ids:
        headers = csrf_headers(passkey_client)
        options = passkey_client.post(
            "/api/v1/auth/authentication/options",
            headers=headers,
        )
        assert options.status_code == 200
        options_body = options.json()
        response = passkey_client.post(
            "/api/v1/auth/authentication/verify",
            json={
                "ceremony_id": options_body["ceremony_id"],
                "credential": _credential(
                    credential_id=credential_id,
                    challenge=options_body["publicKey"]["challenge"],
                ),
            },
            headers=headers,
        )

        assert response.status_code == 401
        body = response.json()
        assert credential_id not in response.text
        failures.append(
            {key: value for key, value in body.items() if key not in {"request_id", "trace_id"}}
        )

    assert failures[0] == failures[1]


def test_password_endpoints_are_removed_from_runtime(passkey_client: TestClient) -> None:
    headers = csrf_headers(passkey_client)
    responses = [
        passkey_client.post(
            "/api/v1/auth/login",
            json={"login": "admin", "password": "legacy"},
            headers=headers,
        ),
        passkey_client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "legacy", "new_password": "legacy-new"},
            headers=headers,
        ),
        passkey_client.post(
            "/api/v1/users/00000000-0000-7000-8000-000000000001/reset-password",
            json={"new_password": "legacy-new"},
            headers=headers,
        ),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404]


def test_forged_source_headers_cannot_partition_public_authentication_limit(
    passkey_client: TestClient,
) -> None:
    terminal_statuses: list[int] = []
    for index, forged_source in enumerate(
        ["198.51.100.1", "203.0.113.2", "192.0.2.3"],
        start=1,
    ):
        headers = csrf_headers(passkey_client)
        headers.update(
            {
                "X-Child-Manager-Client-IP": forged_source,
                "X-Forwarded-For": forged_source,
            }
        )
        options = passkey_client.post(
            "/api/v1/auth/authentication/options",
            headers=headers,
        )
        if options.status_code == 429:
            terminal_statuses.append(429)
            continue
        assert options.status_code == 200
        body = options.json()
        failed = passkey_client.post(
            "/api/v1/auth/authentication/verify",
            json={
                "ceremony_id": body["ceremony_id"],
                "credential": _credential(
                    credential_id=_base64url(f"unknown-{index}".encode()),
                    challenge=body["publicKey"]["challenge"],
                ),
            },
            headers=headers,
        )
        terminal_statuses.append(failed.status_code)

    assert terminal_statuses == [401, 401, 429]


def test_step_up_options_do_not_count_but_verify_failures_reach_the_same_limit(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    statuses: list[int] = []
    for index in range(3):
        headers = csrf_headers(client)
        options = client.post("/api/v1/auth/step-up/options", headers=headers)
        if options.status_code == 429:
            statuses.append(429)
            continue
        assert options.status_code == 200
        body = options.json()
        failed = client.post(
            "/api/v1/auth/step-up/verify",
            json={
                "ceremony_id": body["ceremony_id"],
                "credential": _credential(
                    credential_id=_base64url(f"unknown-step-up-{index}".encode()),
                    challenge=body["publicKey"]["challenge"],
                ),
            },
            headers=headers,
        )
        statuses.append(failed.status_code)

    assert statuses == [401, 401, 429]


@pytest.mark.parametrize(
    ("path", "field", "material"),
    [
        (
            "/api/v1/auth/bootstrap/registration/options",
            "bootstrap_token",
            "invalid-bootstrap-material",
        ),
        (
            "/api/v1/auth/invitation/registration/options",
            "invitation_token",
            "invalid-invitation-material",
        ),
        (
            "/api/v1/auth/recovery/registration/options",
            "enrollment_token",
            "invalid-recovery-enrollment",
        ),
    ],
)
def test_invalid_public_registration_material_is_throttled_by_trusted_source_and_digest(
    passkey_client: TestClient,
    path: str,
    field: str,
    material: str,
) -> None:
    statuses: list[int] = []
    for forged_source in ("198.51.100.1", "203.0.113.2", "192.0.2.3"):
        headers = csrf_headers(passkey_client)
        headers.update(
            {
                "X-Child-Manager-Client-IP": forged_source,
                "X-Forwarded-For": forged_source,
            }
        )
        response = passkey_client.post(path, json={field: material}, headers=headers)
        statuses.append(response.status_code)
        assert material not in response.text

    assert statuses == [410, 410, 429]
