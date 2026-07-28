# ruff: noqa: F811

"""M6 非反思生成必须基于已保存版本的 RED 验收。"""

from copy import deepcopy
from importlib import import_module
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from tests.api.ai_helpers import provision_enabled_ai_model
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401


def _generation_headers(client: TestClient) -> dict[str, str]:
    return csrf_headers(client) | {"Idempotency-Key": str(uuid4())}


def test_single_generation_freezes_the_saved_version_without_mutating_plan(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    content = deepcopy(before["content"])
    content["morning_talk"] = {
        "topic": "已保存话题",
        "questions": ["看到什么？", "听到什么？", "想到什么？"],
    }
    saved = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json={
            "expected_version": before["version"],
            "content": content,
            "authors": [{"user_id": str(actor.user_id), "sort_order": 0}],
        },
        headers=csrf_headers(client),
    )
    assert saved.status_code == 200

    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_talk",
            "expected_version": saved.json()["version"],
            "teacher_context": "围绕春季",
        },
        headers=_generation_headers(client),
    )

    assert response.status_code == 202
    assert response.json()["job"]["requested_resource_version"] == saved.json()["version"]
    after = client.get(f"/api/v1/plans/{plan_id}").json()
    assert after["version"] == saved.json()["version"]
    assert after["content"] == content


def test_stale_presave_version_creates_no_job_or_result(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()

    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_activity",
            "expected_version": plan["version"] + 1,
            "teacher_context": "不应受理",
        },
        headers=_generation_headers(client),
    )

    assert response.status_code == 409
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND plan_id=%s
              AND job_type LIKE 'ai.%%'""",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)
        assert connection.execute(
            """SELECT count(*) FROM ai_generation_results
            WHERE kindergarten_id=%s AND plan_id=%s""",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)


def test_generation_acceptance_creates_pending_result_with_frozen_input(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_activity",
            "expected_version": plan["version"],
            "teacher_context": "冻结的教师补充",
        },
        headers=_generation_headers(client),
    )

    assert response.status_code == 202
    job_id = response.json()["job"]["id"]
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        row = connection.execute(
            """SELECT target_section_baseline_sha256,input_context,input_sha256,
                      model_profile_id,prompt_version_id,result_schema_code,
                      output_content,output_sha256
            FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone()
    assert row is not None
    assert all(value is not None for value in row[:6])
    assert row[6:] == (None, None)


def test_missing_model_configuration_returns_503_and_creates_nothing(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()

    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_activity",
            "expected_version": plan["version"],
            "teacher_context": "缺少模型配置",
        },
        headers=_generation_headers(client),
    )

    assert response.status_code == 503
    assert response.json()["code"] == "configuration.unavailable"
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND plan_id=%s AND job_type LIKE 'ai.%%'""",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)
        assert connection.execute(
            """SELECT count(*) FROM ai_generation_results
            WHERE kindergarten_id=%s AND plan_id=%s""",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)


def test_database_unavailable_returns_503_then_leaves_no_job_or_result(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    original_connect = psycopg.connect

    def unavailable(*_args: object, **_kwargs: object) -> None:
        raise psycopg.OperationalError("test database unavailable")

    monkeypatch.setattr(psycopg, "connect", unavailable)
    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_activity",
            "expected_version": plan["version"],
            "teacher_context": "数据库失败不得受理",
        },
        headers=_generation_headers(client),
    )
    monkeypatch.setattr(psycopg, "connect", original_connect)

    assert response.status_code == 503
    assert response.json()["code"] == "database.unavailable"
    with original_connect(
        isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    ) as connection:
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND plan_id=%s AND job_type LIKE 'ai.%%'""",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)
        assert connection.execute(
            """SELECT count(*) FROM ai_generation_results
            WHERE kindergarten_id=%s AND plan_id=%s""",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)


def test_dispatch_failure_after_commit_keeps_202_pending_result(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    generation = import_module("packages.backend.lesson_plans.ai_generation")

    def fail_dispatch(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("Redis unavailable after commit")

    monkeypatch.setattr(generation, "dispatch_after_commit", fail_dispatch)
    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_activity",
            "expected_version": plan["version"],
            "teacher_context": "提交后投递失败",
        },
        headers=_generation_headers(client),
    )

    assert response.status_code == 202
    assert response.json()["job"]["status"] == "pending_dispatch"
    job_id = response.json()["job"]["id"]
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT execution_status FROM background_jobs
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone() == ("pending_dispatch",)
        assert connection.execute(
            """SELECT count(*) FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone() == (1,)
