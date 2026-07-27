# ruff: noqa: F811

import socket
from collections.abc import Iterator
from importlib import import_module
from typing import Any, cast
from uuid import UUID

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api import dependencies as api_dependencies
from packages.backend.integrations.crypto.ai_keys import (
    AiKeyEnvelope,
    StaticAiKeyProvider,
    decrypt_api_key_with_provider,
)
from packages.backend.jobs.prompt_test_store import PostgresPromptTestStore
from packages.backend.jobs.service import CurrentModelCallProfile, PromptTestExecutor
from packages.backend.prompts.catalog import validate_prompt_result_schema
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


def test_postgres_worker_rebuilds_frozen_context_and_finishes_the_public_job(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
    isolated_database_url: str,
) -> None:
    client, _actor, _dispatcher = prompt_job_client
    profile_id, version_id = _provision_model_and_version(client)
    accepted = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/tests",
        json={
            "version_id": version_id,
            "model_profile_id": profile_id,
            "variables": _variables(),
        },
        headers={**csrf_headers(client), "Idempotency-Key": "worker-chain"},
    )
    assert accepted.status_code == 202

    class StructuredClient:
        def generate_structured(
            self,
            *,
            base_url: str,
            api_key: str,
            model_name: str,
            prompt: str,
        ) -> dict[str, object]:
            assert base_url == "https://ai.example.test/v1"
            assert api_key == "test-secret-value"
            assert model_name == "structured-test-model"
            assert "向日葵班" in prompt
            return {
                "topic": "自然变化",
                "questions": ["你发现了什么？", "为什么会变化？", "我们怎样记录？"],
            }

    provider = StaticAiKeyProvider({"test-key": b"\x42" * 32}, active_key_id="test-key")
    store = PostgresPromptTestStore(isolated_database_url)

    def read_key(profile: CurrentModelCallProfile) -> str:
        assert isinstance(profile.key_envelope, AiKeyEnvelope)
        return decrypt_api_key_with_provider(
            profile.key_envelope,
            key_provider=provider,
            kindergarten_id=profile.kindergarten_id,
            profile_id=profile.profile_id,
        )

    executor = PromptTestExecutor(
        store=store,
        client=StructuredClient(),
        authorizer=store,
        read_api_key=read_key,
        validate_url=lambda value: value,
        validate_result=validate_prompt_result_schema,
    )
    executor.execute_job(UUID(accepted.json()["job"]["id"]), worker_id="integration-worker")

    job = client.get(f"/api/v1/jobs/{accepted.json()['job']['id']}")
    run = client.get(
        f"/api/v1/prompts/{PROMPT_CODE}/tests/{accepted.json()['related_resource_id']}"
    )
    assert job.status_code == 200
    assert job.json()["status"] == "succeeded"
    assert job.json()["attempt_count"] == 1
    assert run.status_code == 200
    assert run.json()["status"] == "succeeded"
    assert run.json()["output_content"]["topic"] == "自然变化"


def test_expired_worker_lease_cannot_commit_after_a_new_worker_reclaims_the_job(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
    isolated_database_url: str,
) -> None:
    client, actor, _dispatcher = prompt_job_client
    profile_id, version_id = _provision_model_and_version(client)
    accepted = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/tests",
        json={
            "version_id": version_id,
            "model_profile_id": profile_id,
            "variables": _variables(),
        },
        headers={**csrf_headers(client), "Idempotency-Key": "lease-owner"},
    )
    job_id = UUID(accepted.json()["job"]["id"])
    store = PostgresPromptTestStore(isolated_database_url)
    assert store.claim_prompt_test(actor.kindergarten_id, job_id, "worker-old") is True

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs SET lease_expires_at=now()-interval '1 second'
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, job_id),
        )
    assert store.claim_prompt_test(actor.kindergarten_id, job_id, "worker-new") is True
    assert store.heartbeat_prompt_test(
        actor.kindergarten_id,
        job_id,
        worker_id="worker-new",
    )
    output = {
        "topic": "租约测试",
        "questions": ["谁拥有租约？", "旧任务能提交吗？", "怎样避免覆盖？"],
    }
    store.finish_prompt_test_success(
        actor.kindergarten_id,
        job_id,
        worker_id="worker-old",
        output=output,
        elapsed_ms=1,
    )
    assert client.get(f"/api/v1/jobs/{job_id}").json()["status"] == "running"

    store.finish_prompt_test_success(
        actor.kindergarten_id,
        job_id,
        worker_id="worker-new",
        output=output,
        elapsed_ms=2,
    )
    assert client.get(f"/api/v1/jobs/{job_id}").json()["status"] == "succeeded"


def test_model_profile_concurrency_and_rate_limits_gate_database_claims(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
    isolated_database_url: str,
) -> None:
    client, actor, _dispatcher = prompt_job_client
    profile_id, version_id = _provision_model_and_version(client)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE ai_model_profiles SET max_concurrency=1,rate_limit_per_minute=1
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, profile_id),
        )

    jobs: list[UUID] = []
    for index in range(2):
        accepted = client.post(
            f"/api/v1/prompts/{PROMPT_CODE}/tests",
            json={
                "version_id": version_id,
                "model_profile_id": profile_id,
                "variables": _variables(class_name=f"限流班级 {index}"),
            },
            headers={**csrf_headers(client), "Idempotency-Key": f"limit-{index}"},
        )
        assert accepted.status_code == 202
        jobs.append(UUID(accepted.json()["job"]["id"]))

    store = PostgresPromptTestStore(isolated_database_url)
    assert store.claim_prompt_test(actor.kindergarten_id, jobs[0], "worker-1") is True
    assert store.claim_prompt_test(actor.kindergarten_id, jobs[1], "worker-2") is False
    store.finish_prompt_test_success(
        actor.kindergarten_id,
        jobs[0],
        worker_id="worker-1",
        output={
            "topic": "限制",
            "questions": ["并发是多少？", "限流是多少？", "何时重试？"],
        },
        elapsed_ms=1,
    )
    assert store.claim_prompt_test(actor.kindergarten_id, jobs[1], "worker-2") is False

    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs SET updated_at=now()-interval '61 seconds'
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, jobs[0]),
        )
    assert store.claim_prompt_test(actor.kindergarten_id, jobs[1], "worker-2") is True
    assert (
        store.handle_prompt_test_error(
            actor.kindergarten_id,
            jobs[1],
            worker_id="worker-2",
            code="ai.rate_limited",
            summary="模型服务请求过于频繁。",
            retryable=True,
            retry_after_seconds=120,
        )
        == 60
    )


def test_idempotency_replay_precedes_retention_and_cross_prompt_fingerprint_conflicts(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
    isolated_database_url: str,
) -> None:
    client, actor, _dispatcher = prompt_job_client
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

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "DELETE FROM prompt_test_runs WHERE kindergarten_id=%s AND job_id=%s",
            (actor.kindergarten_id, first.json()["job"]["id"]),
        )
    replay_after_cleanup = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/tests", json=request, headers=headers
    )
    assert replay_after_cleanup.status_code == 202
    assert replay_after_cleanup.json()["job"]["id"] == first.json()["job"]["id"]
    assert replay_after_cleanup.json()["related_resource_id"] is None


def test_draft_version_can_be_tested_before_publication(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
) -> None:
    client, _actor, _dispatcher = prompt_job_client
    profile_id, version_id = _provision_model_and_version(client)
    current = client.get(f"/api/v1/prompts/{PROMPT_CODE}/versions/{version_id}")
    assert current.status_code == 200
    draft = client.put(
        f"/api/v1/prompts/{PROMPT_CODE}/draft",
        json={"content": current.json()["content"], "based_on_version_id": version_id},
        headers=csrf_headers(client),
    )
    assert draft.status_code == 200

    accepted = client.post(
        f"/api/v1/prompts/{PROMPT_CODE}/tests",
        json={
            "version_id": draft.json()["id"],
            "model_profile_id": profile_id,
            "variables": _variables(),
        },
        headers={**csrf_headers(client), "Idempotency-Key": "draft-prompt-test"},
    )
    assert accepted.status_code == 202


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


def test_new_prompt_test_prunes_only_finished_runs_to_the_recent_twenty(
    prompt_job_client: tuple[TestClient, ActorFixture, FailingDispatcher],
    isolated_database_url: str,
) -> None:
    client, actor, _dispatcher = prompt_job_client
    profile_id, version_id = _provision_model_and_version(client)
    run_ids: list[str] = []
    for index in range(19):
        response = client.post(
            f"/api/v1/prompts/{PROMPT_CODE}/tests",
            json={
                "version_id": version_id,
                "model_profile_id": profile_id,
                "variables": _variables(class_name=f"已完成班级 {index}"),
            },
            headers={**csrf_headers(client), "Idempotency-Key": f"finished-{index}"},
        )
        assert response.status_code == 202
        run_ids.append(response.json()["related_resource_id"])

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs SET execution_status='succeeded',finished_at=now()
            WHERE kindergarten_id=%s AND idempotency_key LIKE 'finished-%%'""",
            (actor.kindergarten_id,),
        )
        connection.execute(
            """UPDATE prompt_test_runs
            SET status='succeeded',output_content='{}'::jsonb,elapsed_ms=0
            WHERE kindergarten_id=%s""",
            (actor.kindergarten_id,),
        )

    newest_run_id = ""
    for index in range(19, 24):
        newest = client.post(
            f"/api/v1/prompts/{PROMPT_CODE}/tests",
            json={
                "version_id": version_id,
                "model_profile_id": profile_id,
                "variables": _variables(class_name=f"未完成班级 {index}"),
            },
            headers={**csrf_headers(client), "Idempotency-Key": f"pending-{index}"},
        )
        assert newest.status_code == 202
        newest_run_id = newest.json()["related_resource_id"]
    page = client.get(f"/api/v1/prompts/{PROMPT_CODE}/tests?page=1&page_size=20")
    assert page.status_code == 200
    assert page.json()["total"] == 20
    assert client.get(f"/api/v1/prompts/{PROMPT_CODE}/tests/{run_ids[0]}").status_code == 404
    assert client.get(f"/api/v1/prompts/{PROMPT_CODE}/tests/{newest_run_id}").status_code == 200
