# ruff: noqa: F811

"""M6 一键四栏受理与非执行父任务 RED 验收。"""

from uuid import uuid4

import psycopg
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

EXPECTED_CHILD_TYPES = {
    "ai.morning_activity",
    "ai.morning_talk",
    "ai.indoor_area_game",
    "ai.afternoon_outdoor_game",
}


def _idempotent_headers(client: TestClient) -> dict[str, str]:
    return csrf_headers(client) | {"Idempotency-Key": str(uuid4())}


def _configure_batch_areas(client: TestClient, class_id: str) -> None:
    for area_type, name in (("indoor", "建构区"), ("outdoor", "沙水区")):
        response = client.put(
            f"/api/v1/settings/classes/{class_id}/areas/{area_type}",
            json={
                "areas": [
                    {
                        "name": name,
                        "sort_order": 0,
                        "is_active": True,
                    }
                ]
            },
            headers=csrf_headers(client),
        )
        assert response.status_code == 204


def test_batch_accepts_exactly_four_independent_children_and_derives_parent(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    _configure_batch_areas(client, class_id)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()

    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/batch",
        json={"expected_version": plan["version"], "teacher_context": "关注春季与合作"},
        headers=_idempotent_headers(client),
    )

    assert response.status_code == 202
    parent = response.json()["job"]
    assert parent["job_type"] == "ai.batch"
    assert parent["attempt_count"] == 0
    assert parent["max_attempts"] == 0
    assert len(parent["children"]) == 4
    assert {child["job_type"] for child in parent["children"]} == EXPECTED_CHILD_TYPES
    assert {"ai.group_activity_split", "ai.daily_reflection"}.isdisjoint(
        {child["job_type"] for child in parent["children"]}
    )


def test_batch_database_parent_is_never_executable_or_dispatched(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    _configure_batch_areas(client, class_id)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()

    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/batch",
        json={"expected_version": plan["version"], "teacher_context": "冻结输入"},
        headers=_idempotent_headers(client),
    )

    assert response.status_code == 202
    parent_id = response.json()["job"]["id"]
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        parent = connection.execute(
            """SELECT execution_status,attempt_count,max_attempts,lease_owner,lease_expires_at,
                      last_heartbeat_at,queued_at,started_at,finished_at,error_code,error_summary,
                      idempotency_scope,idempotency_key,request_fingerprint_sha256
            FROM background_jobs WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, parent_id),
        ).fetchone()
        children = connection.execute(
            """SELECT id,target_section,execution_status,idempotency_scope,idempotency_key,
                      request_fingerprint_sha256,queued_at
            FROM background_jobs WHERE kindergarten_id=%s AND parent_job_id=%s""",
            (actor.kindergarten_id, parent_id),
        ).fetchall()
        results = connection.execute(
            """SELECT job_id,target_section,target_section_baseline_sha256,input_context,
                      input_sha256,output_content,output_sha256
            FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=ANY(%s)""",
            (actor.kindergarten_id, [row[0] for row in children]),
        ).fetchall()
        parent_result_count = connection.execute(
            """SELECT count(*) FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.kindergarten_id, parent_id),
        ).fetchone()
    assert parent is not None
    assert parent[:11] == (None,) * 11
    assert all(value is not None for value in parent[11:])
    assert parent_result_count == (0,)
    assert len(children) == 4
    assert len({str(row[1]) for row in children}) == 4
    assert all(row[2] == "pending_dispatch" for row in children)
    assert all(row[3:6] == (None, None, None) for row in children)
    assert all(row[6] is None for row in children)
    assert len(results) == 4
    assert all(all(value is not None for value in row[2:5]) for row in results)
    assert all(row[5:] == (None, None) for row in results)


def test_batch_idempotency_replays_original_parent_and_rejects_changed_body(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    headers = _idempotent_headers(client)
    body = {"expected_version": plan["version"], "teacher_context": "同一请求"}

    first = client.post(f"/api/v1/plans/{plan_id}/ai/batch", json=body, headers=headers)
    replay = client.post(f"/api/v1/plans/{plan_id}/ai/batch", json=body, headers=headers)
    conflict = client.post(
        f"/api/v1/plans/{plan_id}/ai/batch",
        json=body | {"teacher_context": "改变输入"},
        headers=headers,
    )

    assert first.status_code == replay.status_code == 202
    assert first.json()["job"]["id"] == replay.json()["job"]["id"]
    assert conflict.status_code == 409
