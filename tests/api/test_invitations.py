# ruff: noqa: F811

import json
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import UTC, datetime, timedelta
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


def _create_teacher(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/users",
        json={
            "username": "invited-teacher",
            "display_name": "受邀教师",
            "role_codes": ["teacher"],
        },
        headers=csrf_headers(client),
    )
    assert response.status_code == 201
    return response.json()


def _issue(client: TestClient, user_id: object) -> dict[str, object]:
    response = client.post(
        f"/api/v1/users/{user_id}/invitations",
        json={"expires_in_hours": 24},
        headers=csrf_headers(client),
    )
    assert response.status_code == 201
    return response.json()


def _secret_bytes(value: object) -> bytes:
    text = str(value)
    return urlsafe_b64decode(text + "=" * (-len(text) % 4))


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


def test_invitation_management_requires_an_authenticated_admin(passkey_client: TestClient) -> None:
    user_id = "00000000-0000-7000-8000-000000000001"
    headers = csrf_headers(passkey_client)

    listed = passkey_client.get(f"/api/v1/users/{user_id}/invitations")
    issued = passkey_client.post(
        f"/api/v1/users/{user_id}/invitations",
        json={"expires_in_hours": 24},
        headers=headers,
    )

    assert listed.status_code == 401
    assert issued.status_code == 401


def test_invitation_is_single_use_reissuable_and_revocable(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    teacher = _create_teacher(client)
    first = _issue(client, teacher["id"])
    second = _issue(client, teacher["id"])

    assert len(_secret_bytes(first["invitation_token"])) >= 16
    assert "http://" not in str(first["invitation_token"])
    assert "https://" not in str(first["invitation_token"])
    listed = client.get(f"/api/v1/users/{teacher['id']}/invitations")
    assert listed.status_code == 200
    status_by_id = {item["id"]: item["status"] for item in listed.json()["items"]}
    assert status_by_id[first["id"]] == "revoked"
    assert status_by_id[second["id"]] == "pending"

    revoke_path = f"/api/v1/users/{teacher['id']}/invitations/{second['id']}/revoke"
    headers = csrf_headers(client)
    assert client.post(revoke_path, headers=headers).status_code == 204
    assert client.post(revoke_path, headers=headers).status_code == 204


def test_unknown_expired_revoked_and_consumed_invitation_share_one_public_failure(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, _actor = admin_client
    teacher = _create_teacher(client)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    cases: list[str] = ["unknown-invitation"]

    expired = _issue(client, teacher["id"])
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "UPDATE account_invitations SET expires_at=%s WHERE id=%s",
            (datetime.now(UTC) - timedelta(seconds=1), UUID(str(expired["id"]))),
        )
    cases.append(str(expired["invitation_token"]))

    revoked = _issue(client, teacher["id"])
    client.post(
        f"/api/v1/users/{teacher['id']}/invitations/{revoked['id']}/revoke",
        headers=csrf_headers(client),
    )
    cases.append(str(revoked["invitation_token"]))

    consumed = _issue(client, teacher["id"])
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "UPDATE account_invitations SET consumed_at=%s WHERE id=%s",
            (datetime.now(UTC), UUID(str(consumed["id"]))),
        )
    cases.append(str(consumed["invitation_token"]))

    failures: list[dict[str, object]] = []
    for token in cases:
        response = client.post(
            "/api/v1/auth/invitation/registration/options",
            json={"invitation_token": token},
            headers=csrf_headers(client),
        )
        assert response.status_code == 410
        assert token not in response.text
        failures.append(
            {
                key: value
                for key, value in response.json().items()
                if key not in {"request_id", "trace_id"}
            }
        )

    assert all(failure == failures[0] for failure in failures[1:])


def test_unknown_invitation_has_no_session_side_effect(passkey_client: TestClient) -> None:
    response = passkey_client.post(
        "/api/v1/auth/invitation/registration/options",
        json={"invitation_token": "unknown-or-expired-invitation"},
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 410
    assert "unknown-or-expired-invitation" not in response.text


def test_invitation_registration_verify_never_creates_a_session(passkey_client: TestClient) -> None:
    response = passkey_client.post(
        "/api/v1/auth/invitation/registration/verify",
        json={
            "ceremony_id": "00000000-0000-7000-8000-000000000001",
            "credential": {
                "id": "aW52aXRlZA",
                "rawId": "aW52aXRlZA",
                "type": "public-key",
                "response": {"clientDataJSON": "e30", "attestationObject": "e30"},
                "clientExtensionResults": {},
            },
        },
        headers=csrf_headers(passkey_client),
    )

    assert response.status_code == 410
    assert response.headers.get_list("set-cookie") == []


def test_registration_verify_failure_persists_challenge_count_and_sanitized_audit(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _actor = admin_client
    teacher = _create_teacher(client)
    invitation = _issue(client, teacher["id"])
    options = client.post(
        "/api/v1/auth/invitation/registration/options",
        json={"invitation_token": invitation["invitation_token"]},
        headers=csrf_headers(client),
    )
    assert options.status_code == 200
    monkeypatch.setattr(
        "packages.backend.identity.service.verify_registration",
        lambda **_kwargs: (_ for _ in ()).throw(ValueError("sensitive verifier detail")),
    )

    failed = client.post(
        "/api/v1/auth/invitation/registration/verify",
        json={
            "ceremony_id": options.json()["ceremony_id"],
            "credential": _registration_credential(
                credential_id=_base64url(b"failed-registration-credential"),
                challenge=options.json()["publicKey"]["challenge"],
            ),
        },
        headers=csrf_headers(client),
    )

    assert failed.status_code == 410
    assert "sensitive verifier detail" not in failed.text
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            "SELECT failure_count, consumed_at FROM webauthn_challenges WHERE id=%s",
            (options.json()["ceremony_id"],),
        ).fetchone() == (1, None)
        audit = connection.execute(
            """SELECT event_code, outcome, resource_type, resource_id, metadata::text
            FROM audit_events
            WHERE event_code='identity.credential_registered' AND outcome='failure'"""
        ).fetchone()
    assert audit is not None
    assert audit[:4] == (
        "identity.credential_registered",
        "failure",
        "webauthn_challenge",
        UUID(options.json()["ceremony_id"]),
    )
    assert "sensitive verifier detail" not in audit[4]
