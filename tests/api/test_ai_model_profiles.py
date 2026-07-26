# ruff: noqa: F811

import socket
from collections.abc import Iterator
from importlib import import_module
from typing import Any, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api import dependencies as api_dependencies
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def _resolver(_host: str, port: int, **_kwargs: object) -> list[tuple[object, ...]]:
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]


@pytest.fixture
def ai_admin_client(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> Iterator[tuple[TestClient, ActorFixture]]:
    client, actor = admin_client
    try:
        module = import_module("packages.backend.settings.ai_models")
        encryption = import_module("packages.backend.integrations.crypto.ai_keys")
    except ModuleNotFoundError:
        yield client, actor
        return
    service = module.AiModelService(
        database_url=isolated_database_url,
        key_provider=encryption.StaticAiKeyProvider(
            {"test-key": b"\x42" * 32},
            active_key_id="test-key",
        ),
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )
    app = cast(FastAPI, client.app)
    dependency = getattr(api_dependencies, "ai_model_service", None)
    if dependency is None:
        yield client, actor
        return
    app.dependency_overrides[dependency] = lambda: service
    yield client, actor


def _profile_payload(**changes: Any) -> dict[str, Any]:
    return {
        "name": "教学模型",
        "api_base_url": "https://ai.example.test/v1",
        "model_name": "structured-test-model",
        "api_key": "test-secret-value",
        "capability_codes": ["text", "structured_output"],
        "max_concurrency": 2,
        "rate_limit_per_minute": 60,
        "is_default": True,
        **changes,
    }


def test_admin_creates_write_only_masked_profile_and_cannot_read_key(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = ai_admin_client
    created = client.post(
        "/api/v1/settings/ai-model-profiles",
        json=_profile_payload(),
        headers=csrf_headers(client),
    )

    assert created.status_code == 201
    body = created.json()
    assert body["api_key_masked"] == "••••alue"
    assert body["call_config_revision"] == 1
    assert "api_key" not in body
    assert "ciphertext" not in str(body).lower()
    fetched = client.get(f"/api/v1/settings/ai-model-profiles/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_call_fields_increment_revision_but_display_and_limits_do_not(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = ai_admin_client
    created = client.post(
        "/api/v1/settings/ai-model-profiles",
        json=_profile_payload(),
        headers=csrf_headers(client),
    ).json()
    profile_id = created["id"]
    display_change = client.patch(
        f"/api/v1/settings/ai-model-profiles/{profile_id}",
        json=_profile_payload(name="教学模型二", api_key=None, max_concurrency=3),
        headers=csrf_headers(client),
    )
    model_change = client.patch(
        f"/api/v1/settings/ai-model-profiles/{profile_id}",
        json=_profile_payload(
            name="教学模型二",
            api_key=None,
            max_concurrency=3,
            model_name="changed-model",
        ),
        headers=csrf_headers(client),
    )
    key_change = client.patch(
        f"/api/v1/settings/ai-model-profiles/{profile_id}",
        json=_profile_payload(
            name="教学模型二",
            api_key="another-secret",
            max_concurrency=3,
            model_name="changed-model",
        ),
        headers=csrf_headers(client),
    )

    assert display_change.status_code == 200
    assert display_change.json()["call_config_revision"] == 1
    assert model_change.json()["call_config_revision"] == 2
    assert key_change.json()["call_config_revision"] == 3


def test_enable_requires_key_capabilities_and_explicit_risk_confirmation(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    created = client.post(
        "/api/v1/settings/ai-model-profiles",
        json=_profile_payload(api_key=None, capability_codes=["text"]),
        headers=csrf_headers(client),
    ).json()
    profile_id = created["id"]

    missing_confirmation = client.post(
        f"/api/v1/settings/ai-model-profiles/{profile_id}/enable",
        json={"confirm_external_data_risk": False},
        headers=csrf_headers(client),
    )
    missing_key = client.post(
        f"/api/v1/settings/ai-model-profiles/{profile_id}/enable",
        json={"confirm_external_data_risk": True},
        headers=csrf_headers(client),
    )
    configured = client.patch(
        f"/api/v1/settings/ai-model-profiles/{profile_id}",
        json=_profile_payload(is_default=False),
        headers=csrf_headers(client),
    )
    enabled = client.post(
        f"/api/v1/settings/ai-model-profiles/{profile_id}/enable",
        json={"confirm_external_data_risk": True},
        headers=csrf_headers(client),
    )

    assert missing_confirmation.status_code == 422
    assert missing_key.status_code == 422
    assert configured.status_code == 200
    assert enabled.status_code == 200
    assert enabled.json()["is_active"] is True
    assert enabled.json()["risk_confirmed_at"] is not None
    assert enabled.json()["risk_confirmed_by"] == str(actor.user_id)


def test_disable_preserves_profile_and_default_switch_is_tenant_local(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = ai_admin_client
    first = client.post(
        "/api/v1/settings/ai-model-profiles",
        json=_profile_payload(name="模型一"),
        headers=csrf_headers(client),
    ).json()
    second = client.post(
        "/api/v1/settings/ai-model-profiles",
        json=_profile_payload(name="模型二"),
        headers=csrf_headers(client),
    ).json()

    listed = client.get("/api/v1/settings/ai-model-profiles").json()
    defaults = [item["name"] for item in listed["items"] if item["is_default"]]
    assert defaults == ["模型二"]

    disabled = client.post(
        f"/api/v1/settings/ai-model-profiles/{second['id']}/disable",
        headers=csrf_headers(client),
    )
    fetched_first = client.get(f"/api/v1/settings/ai-model-profiles/{first['id']}")
    fetched_second = client.get(f"/api/v1/settings/ai-model-profiles/{second['id']}")
    assert disabled.status_code == 200
    assert disabled.json()["is_active"] is False
    assert fetched_first.status_code == 200
    assert fetched_second.status_code == 200
