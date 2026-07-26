# ruff: noqa: F811

from collections.abc import Iterator
from importlib import import_module
from typing import cast

import psycopg
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

PROMPT_CODE = "daily_activity_plan.morning_talk"


@pytest.fixture
def prompt_admin_client(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> Iterator[tuple[TestClient, ActorFixture]]:
    client, actor = admin_client
    try:
        module = import_module("packages.backend.prompts.service")
    except ModuleNotFoundError:
        yield client, actor
        return
    app = cast(FastAPI, client.app)
    dependency = getattr(api_dependencies, "prompt_service", None)
    if dependency is None:
        yield client, actor
        return
    app.dependency_overrides[dependency] = lambda: module.PromptService(
        database_url=isolated_database_url
    )
    yield client, actor


def test_system_catalog_is_seeded_read_only_and_business_effective(
    prompt_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = prompt_admin_client
    listed = client.get("/api/v1/prompts")
    definition = client.get(f"/api/v1/prompts/{PROMPT_CODE}")

    assert listed.status_code == 200
    assert listed.json()["total"] == 7
    assert len(listed.json()["items"]) == 7
    assert definition.status_code == 200
    body = definition.json()
    assert body["code"] == PROMPT_CODE
    assert body["effective_version_id"] is not None
    assert body["draft_version_id"] is None


@pytest.mark.parametrize(
    "invalid",
    [
        "{{unknown}}",
        "{{\nplan_date}}",
        "{{PlanDate}}",
        "{{plan.date}}",
        "{{plan_date|upper}}",
        "{{plan_date",
    ],
)
def test_draft_save_and_publish_use_the_same_strict_parser(
    prompt_admin_client: tuple[TestClient, ActorFixture],
    invalid: str,
) -> None:
    client, _actor = prompt_admin_client
    draft = client.put(
        f"/api/v1/prompts/{PROMPT_CODE}/draft",
        json={"content": invalid, "based_on_version_id": None},
        headers=csrf_headers(client),
    )
    assert draft.status_code == 422
    assert draft.json()["code"] == "prompt.invalid_template"


def test_admin_creates_updates_publishes_and_restores_without_mutating_history(
    prompt_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, _actor = prompt_admin_client
    valid = "日期：{{ plan_date }}；班级：{{class_name}}；教师补充：{{teacher_context}}"
    draft = client.put(
        f"/api/v1/prompts/{PROMPT_CODE}/draft",
        json={"content": valid, "based_on_version_id": None},
        headers=csrf_headers(client),
    )
    published = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/publish",
        headers=csrf_headers(client),
    )
    versions_before = client.get(f"/api/v1/prompts/{PROMPT_CODE}/versions").json()
    restored = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/versions/{published.json()['id']}/restore",
        headers=csrf_headers(client),
    )
    versions_after = client.get(f"/api/v1/prompts/{PROMPT_CODE}/versions").json()

    assert draft.status_code == 200
    assert draft.json()["lifecycle_state"] == "draft"
    assert published.status_code == 201
    assert published.json()["lifecycle_state"] == "published"
    assert restored.status_code == 201
    assert restored.json()["id"] != published.json()["id"]
    assert restored.json()["content"] == published.json()["content"]
    assert versions_after["total"] == versions_before["total"] + 1
    original = client.get(f"/api/v1/prompts/{PROMPT_CODE}/versions/{published.json()['id']}")
    assert original.json() == published.json()

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        event_codes = {
            str(row[0])
            for row in connection.execute(
                """SELECT event_code FROM audit_events
                WHERE event_code IN ('prompt.published','prompt.restored')"""
            ).fetchall()
        }
    assert event_codes == {"prompt.published", "prompt.restored"}
