# ruff: noqa: F811

"""T123 集体活动两阶段采用 API RED。"""

import json
from collections.abc import Mapping
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
from typing import Any
from uuid import UUID, uuid4

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

GROUP_SPLIT = {
    "theme": "春天",
    "objectives": ["观察变化"],
    "preparation": ["图片"],
    "focus": "表达发现",
    "difficulty": "连续描述",
    "process": [{"heading": "观察", "lines": ["观察图片"]}],
}
ADD_STEP = {
    "step": {"heading": "延伸", "lines": ["绘制春天"]},
    "suggested_insert_index": 1,
}


def _native_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def _headers(client: TestClient) -> dict[str, str]:
    return csrf_headers(client) | {"Idempotency-Key": str(uuid4())}


def _request_generation(
    client: TestClient,
    plan_id: str,
    *,
    task_code: str,
    expected_version: int,
    source_id: str | None = None,
) -> Any:
    payload: dict[str, object] = {
        "task_code": task_code,
        "expected_version": expected_version,
        "teacher_context": "围绕春季观察",
    }
    if source_id is not None:
        payload["source_id"] = source_id
    return client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json=payload,
        headers=_headers(client),
    )


def _complete_preview(
    database_url: str,
    *,
    kindergarten_id: UUID,
    job_id: str,
    output_content: Mapping[str, object],
) -> None:
    repository_type = import_module("packages.backend.jobs.ai_results").AiGenerationResultRepository
    output_sha256 = sha256(
        json.dumps(
            output_content, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    with psycopg.connect(_native_url(database_url)) as connection:
        repository = repository_type(connection)
        assert repository.complete_pending(
            kindergarten_id,
            UUID(job_id),
            output_content=dict(output_content),
            output_sha256=output_sha256,
        )
        connection.execute(
            """UPDATE background_jobs SET execution_status='awaiting_confirmation'
            WHERE kindergarten_id=%s AND id=%s""",
            (kindergarten_id, UUID(job_id)),
        )


def _snapshot_count(database_url: str, *, kindergarten_id: UUID, plan_id: str) -> int:
    with psycopg.connect(_native_url(database_url)) as connection:
        row = connection.execute(
            """SELECT count(*) FROM daily_activity_plan_snapshots
            WHERE kindergarten_id=%s AND plan_id=%s AND reason_code='ai_adopted'""",
            (kindergarten_id, UUID(plan_id)),
        ).fetchone()
    assert row is not None
    return int(row[0])


def _prepare_adopted_split(
    client: TestClient,
    actor: ActorFixture,
    database_url: str,
) -> tuple[str, dict[str, Any]]:
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    source = client.post(
        f"/api/v1/plans/{plan_id}/group-activity-sources/text",
        json={"text": "教师确认的集体活动原文。"},
        headers=csrf_headers(client),
    )
    assert source.status_code == 201
    split = _request_generation(
        client,
        plan_id,
        task_code="group_activity_split",
        expected_version=plan["version"],
        source_id=source.json()["id"],
    )
    assert split.status_code == 202
    split_job_id = split.json()["job"]["id"]
    _complete_preview(
        database_url,
        kindergarten_id=actor.kindergarten_id,
        job_id=split_job_id,
        output_content=GROUP_SPLIT,
    )
    adopted = client.post(
        f"/api/v1/jobs/{split_job_id}/adopt",
        json={"expected_version": plan["version"]},
        headers=csrf_headers(client),
    )
    assert adopted.status_code == 200
    return plan_id, adopted.json()


def test_add_step_request_is_rejected_until_split_preview_is_adopted_and_saved(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()

    response = _request_generation(
        client,
        plan_id,
        task_code="group_activity_add_step",
        expected_version=plan["version"],
    )

    assert response.status_code == 409
    assert response.json()["code"] == "group_activity.split_not_adopted"


def test_adopted_saved_split_creates_tail_add_preview_and_two_adoption_snapshots(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    plan_id, split = _prepare_adopted_split(client, actor, isolated_database_url)
    split_steps = split["content"]["group_activity"]["process"]
    assert [step["is_ai_added"] for step in split_steps] == [False]
    assert (
        _snapshot_count(
            isolated_database_url, kindergarten_id=actor.kindergarten_id, plan_id=plan_id
        )
        == 1
    )

    accepted = _request_generation(
        client,
        plan_id,
        task_code="group_activity_add_step",
        expected_version=split["version"],
    )
    assert accepted.status_code == 202
    add_job_id = accepted.json()["job"]["id"]
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        frozen = connection.execute(
            """SELECT input_context FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.kindergarten_id, UUID(add_job_id)),
        ).fetchone()
    assert frozen is not None
    assert frozen[0]["group_activity"]["process"] == split_steps
    _complete_preview(
        isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        job_id=add_job_id,
        output_content=ADD_STEP,
    )
    adopted = client.post(
        f"/api/v1/jobs/{add_job_id}/adopt",
        json={"expected_version": split["version"]},
        headers=csrf_headers(client),
    )

    assert adopted.status_code == 200
    assert [
        step["is_ai_added"] for step in adopted.json()["content"]["group_activity"]["process"]
    ] == [
        False,
        True,
    ]
    assert (
        _snapshot_count(
            isolated_database_url, kindergarten_id=actor.kindergarten_id, plan_id=plan_id
        )
        == 2
    )
    retained_content = deepcopy(adopted.json()["content"])
    retained_content["group_activity"]["focus"] = "教师补充观察重点"
    retained = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json={
            "expected_version": adopted.json()["version"],
            "content": retained_content,
            "authors": [
                {"user_id": author["user_id"], "sort_order": author["sort_order"]}
                for author in adopted.json()["authors"]
            ],
        },
        headers=csrf_headers(client),
    )
    assert retained.status_code == 200
    assert retained.json()["content"]["group_activity"]["process"][-1]["is_ai_added"] is True

    cleared_content = deepcopy(retained.json()["content"])
    cleared_content["group_activity"]["process"][-1]["is_ai_added"] = False
    cleared = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json={
            "expected_version": retained.json()["version"],
            "content": cleared_content,
            "authors": [
                {"user_id": author["user_id"], "sort_order": author["sort_order"]}
                for author in retained.json()["authors"]
            ],
        },
        headers=csrf_headers(client),
    )
    assert cleared.status_code == 200
    assert cleared.json()["content"]["group_activity"]["process"][-1]["is_ai_added"] is False


@pytest.mark.parametrize("suggested_insert_index", [-1, 2])
def test_invalid_add_preview_index_is_not_adopted_and_never_rolls_back_split(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    suggested_insert_index: int,
) -> None:
    client, actor = ai_admin_client
    plan_id, split = _prepare_adopted_split(client, actor, isolated_database_url)
    accepted = _request_generation(
        client,
        plan_id,
        task_code="group_activity_add_step",
        expected_version=split["version"],
    )
    assert accepted.status_code == 202
    add_job_id = accepted.json()["job"]["id"]
    _complete_preview(
        isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        job_id=add_job_id,
        output_content=ADD_STEP | {"suggested_insert_index": suggested_insert_index},
    )
    rejected = client.post(
        f"/api/v1/jobs/{add_job_id}/adopt",
        json={"expected_version": split["version"]},
        headers=csrf_headers(client),
    )

    assert rejected.status_code == 409
    current = client.get(f"/api/v1/plans/{plan_id}").json()
    assert (
        current["content"]["group_activity"]["process"]
        == split["content"]["group_activity"]["process"]
    )
    assert (
        _snapshot_count(
            isolated_database_url, kindergarten_id=actor.kindergarten_id, plan_id=plan_id
        )
        == 1
    )


def test_current_group_activity_edit_makes_pending_add_preview_stale_without_new_snapshot(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    plan_id, split = _prepare_adopted_split(client, actor, isolated_database_url)
    accepted = _request_generation(
        client,
        plan_id,
        task_code="group_activity_add_step",
        expected_version=split["version"],
    )
    assert accepted.status_code == 202
    add_job_id = accepted.json()["job"]["id"]
    _complete_preview(
        isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        job_id=add_job_id,
        output_content=ADD_STEP,
    )
    before_edit = client.get(f"/api/v1/plans/{plan_id}").json()
    manually_edited = deepcopy(before_edit["content"])
    manually_edited["group_activity"]["focus"] = "教师已手动更新重点"
    saved = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json={
            "expected_version": before_edit["version"],
            "content": manually_edited,
            "authors": [
                {"user_id": author["user_id"], "sort_order": author["sort_order"]}
                for author in before_edit["authors"]
            ],
        },
        headers=csrf_headers(client),
    )
    assert saved.status_code == 200

    stale = client.post(
        f"/api/v1/jobs/{add_job_id}/adopt",
        json={"expected_version": saved.json()["version"]},
        headers=csrf_headers(client),
    )

    assert stale.status_code == 409
    assert stale.json()["code"] == "ai.preview_stale"
    assert (
        client.get(f"/api/v1/plans/{plan_id}").json()["content"]["group_activity"]
        == (manually_edited["group_activity"])
    )
    assert (
        _snapshot_count(
            isolated_database_url, kindergarten_id=actor.kindergarten_id, plan_id=plan_id
        )
        == 1
    )


def test_failed_add_job_preserves_adopted_split_and_only_retries_that_addition(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    plan_id, split = _prepare_adopted_split(client, actor, isolated_database_url)
    accepted = _request_generation(
        client,
        plan_id,
        task_code="group_activity_add_step",
        expected_version=split["version"],
    )
    assert accepted.status_code == 202
    add_job_id = accepted.json()["job"]["id"]
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='failed',attempt_count=3,
                finished_at='2026-03-02T08:00:00Z',error_code='ai.timeout'
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, UUID(add_job_id)),
        )

    retry = client.post(f"/api/v1/jobs/{add_job_id}/retry", headers=csrf_headers(client))

    assert retry.status_code == 202
    assert retry.json()["job"]["id"] != add_job_id
    current = client.get(f"/api/v1/plans/{plan_id}").json()
    assert current["content"]["group_activity"] == split["content"]["group_activity"]
    assert (
        _snapshot_count(
            isolated_database_url, kindergarten_id=actor.kindergarten_id, plan_id=plan_id
        )
        == 1
    )
