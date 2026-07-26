# ruff: noqa: F811

import socket
from collections.abc import Iterator
from importlib import import_module
from typing import Any, cast

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


def _resolver(_host: str, port: int, **_kwargs: object) -> list[tuple[object, ...]]:
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]


class FailingDispatcher:
    def __init__(self) -> None:
        self.job_ids: list[str] = []

    def dispatch(self, job_id: object) -> None:
        self.job_ids.append(str(job_id))
        raise RuntimeError("Redis unavailable after commit")


@pytest.fixture
def prompt_job_client(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> Iterator[tuple[TestClient, ActorFixture, FailingDispatcher]]:
    client, actor = admin_client
    dispatcher = FailingDispatcher()
    try:
        models = import_module("packages.backend.settings.ai_models")
        prompts = import_module("packages.backend.prompts.service")
        encryption = import_module("packages.backend.integrations.crypto.ai_keys")
    except ModuleNotFoundError:
        yield client, actor, dispatcher
        return
    provider = encryption.StaticAiKeyProvider(
        {"test-key": b"\x42" * 32},
        active_key_id="test-key",
    )
    app = cast(FastAPI, client.app)
    ai_dependency = getattr(api_dependencies, "ai_model_service", None)
    prompt_dependency = getattr(api_dependencies, "prompt_service", None)
    if ai_dependency is None or prompt_dependency is None:
        yield client, actor, dispatcher
        return
    app.dependency_overrides[ai_dependency] = lambda: models.AiModelService(
        database_url=isolated_database_url,
        key_provider=provider,
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )
    app.dependency_overrides[prompt_dependency] = lambda: prompts.PromptService(
        database_url=isolated_database_url,
        dispatcher=dispatcher,
    )
    yield client, actor, dispatcher


def _variables(**changes: Any) -> dict[str, Any]:
    return {
        "plan_date": "2026-07-26",
        "weekday_text": "星期日",
        "teaching_week_text": None,
        "season": "summer",
        "class_name": "向日葵班",
        "age_group_name": "中班",
        "teacher_context": {"notes": "只讨论自然变化"},
        **changes,
    }


def _provision_model_and_version(client: TestClient) -> tuple[str, str]:
    model = client.post(
        "/api/v1/settings/ai-model-profiles",
        json={
            "name": "测试模型",
            "api_base_url": "https://ai.example.test/v1",
            "model_name": "structured-test-model",
            "api_key": "test-secret-value",
            "capability_codes": ["text", "structured_output"],
            "max_concurrency": 2,
            "rate_limit_per_minute": None,
            "is_default": True,
        },
        headers=csrf_headers(client),
    )
    assert model.status_code == 201
    enabled = client.post(
        f"/api/v1/settings/ai-model-profiles/{model.json()['id']}/enable",
        json={"confirm_external_data_risk": True},
        headers=csrf_headers(client),
    )
    assert enabled.status_code == 200
    definition = client.get(f"/api/v1/prompts/{PROMPT_CODE}")
    assert definition.status_code == 200
    return model.json()["id"], definition.json()["effective_version_id"]


def test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
    isolated_database_url: str,
) -> None:
    client, actor, dispatcher = prompt_job_client
    profile_id, version_id = _provision_model_and_version(client)
    accepted = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/tests",
        json={
            "version_id": version_id,
            "model_profile_id": profile_id,
            "variables": _variables(),
        },
        headers={**csrf_headers(client), "Idempotency-Key": "prompt-test-1"},
    )

    assert accepted.status_code == 202
    assert accepted.json()["job"]["status"] == "pending_dispatch"
    assert dispatcher.job_ids == [accepted.json()["job"]["id"]]
    run_id = accepted.json()["related_resource_id"]
    public_run = client.get(f"/api/v1/prompts/{PROMPT_CODE}/tests/{run_id}")
    assert public_run.status_code == 200
    assert public_run.json()["input_summary"] == {
        "provided_variable_names": sorted(_variables()),
        "all_values_redacted": True,
    }
    public_text = str(public_run.json())
    assert "向日葵班" not in public_text
    assert "只讨论自然变化" not in public_text
    assert "ai.example.test" not in public_text

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        frozen = connection.execute(
            """SELECT input_context, input_sha256, prompt_content, prompt_content_sha256,
                      result_schema_code, result_schema_version, model_call_snapshot,
                      input_summary
            FROM prompt_test_runs WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, run_id),
        ).fetchone()
    assert frozen is not None
    assert frozen[0]["class_name"] == "向日葵班"
    assert len(frozen[1]) == 64
    assert frozen[2]
    assert len(frozen[3]) == 64
    assert frozen[5] == 1
    assert frozen[6]["call_config_revision"] == 1
    assert "api_key" not in str(frozen[6]).lower()
    assert "ciphertext" not in str(frozen[6]).lower()


def test_idempotency_replay_precedes_retention_and_cross_prompt_fingerprint_conflicts(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
) -> None:
    client, _actor, _dispatcher = prompt_job_client
    profile_id, version_id = _provision_model_and_version(client)
    request = {
        "version_id": version_id,
        "model_profile_id": profile_id,
        "variables": _variables(),
    }
    headers = {**csrf_headers(client), "Idempotency-Key": "same-prompt-request"}
    first = client.post(f"/api/v1/prompts/{PROMPT_CODE}/tests", json=request, headers=headers)
    replay = client.post(f"/api/v1/prompts/{PROMPT_CODE}/tests", json=request, headers=headers)
    conflict = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/tests",
        json={**request, "variables": _variables(class_name="另一班")},
        headers=headers,
    )

    assert first.status_code == 202
    assert replay.status_code == 202
    assert replay.json() == first.json()
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "job.idempotency_conflict"


def test_twenty_unfinished_runs_reject_new_work_without_partial_job(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
    isolated_database_url: str,
) -> None:
    client, actor, _dispatcher = prompt_job_client
    profile_id, version_id = _provision_model_and_version(client)
    for index in range(20):
        response = client.post(
            f"/api/v1/prompts/{PROMPT_CODE}/tests",
            json={
                "version_id": version_id,
                "model_profile_id": profile_id,
                "variables": _variables(class_name=f"班级 {index}"),
            },
            headers={**csrf_headers(client), "Idempotency-Key": f"active-{index}"},
        )
        assert response.status_code == 202

    rejected = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/tests",
        json={
            "version_id": version_id,
            "model_profile_id": profile_id,
            "variables": _variables(class_name="第二十一班"),
        },
        headers={**csrf_headers(client), "Idempotency-Key": "active-20"},
    )
    assert rejected.status_code == 409
    assert rejected.json()["code"] == "prompt.too_many_active_tests"

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND idempotency_key='active-20'""",
            (actor.kindergarten_id,),
        ).fetchone() == (0,)
