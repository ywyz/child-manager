# ruff: noqa: F811

"""M6 batch 只读聚合与页面恢复轮询 RED 验收。"""

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


def _headers(client: TestClient) -> dict[str, str]:
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


def test_plan_job_history_restores_batch_with_exactly_four_children(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    _configure_batch_areas(client, class_id)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    created = client.post(
        f"/api/v1/plans/{plan_id}/ai/batch",
        json={"expected_version": plan["version"], "teacher_context": "恢复测试"},
        headers=_headers(client),
    )
    assert created.status_code == 202

    reloaded = client.get(f"/api/v1/plans/{plan_id}/jobs?page=1&page_size=20")

    assert reloaded.status_code == 200
    parent = next(
        item for item in reloaded.json()["items"] if item["id"] == created.json()["job"]["id"]
    )
    assert parent["attempt_count"] == parent["max_attempts"] == 0
    assert len(parent["children"]) == 4
    assert parent["poll_after_ms"] == 1500


def test_each_get_rederives_parent_projection_without_writing_parent_state(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    _configure_batch_areas(client, class_id)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    created = client.post(
        f"/api/v1/plans/{plan_id}/ai/batch",
        json={"expected_version": plan["version"], "teacher_context": "派生测试"},
        headers=_headers(client),
    )
    assert created.status_code == 202
    parent_id = created.json()["job"]["id"]
    child_ids = [child["id"] for child in created.json()["job"]["children"]]
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    with psycopg.connect(native_url) as connection:
        with (
            pytest.raises(psycopg.errors.CheckViolation),
            connection.transaction(),
        ):
            connection.execute(
                """UPDATE background_jobs
                SET execution_status='running',attempt_count=1,max_attempts=3
                WHERE kindergarten_id=%s AND id=%s""",
                (actor.kindergarten_id, parent_id),
            )
        connection.execute(
            """UPDATE background_jobs SET execution_status='running'
            WHERE kindergarten_id=%s AND id=ANY(%s)""",
            (actor.kindergarten_id, child_ids),
        )
    running = client.get(f"/api/v1/jobs/{parent_id}")
    assert running.status_code == 200
    assert running.json()["status"] == "running"

    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='queued',lease_owner=NULL,lease_expires_at=NULL,
                last_heartbeat_at=NULL
            WHERE kindergarten_id=%s AND id=ANY(%s)""",
            (actor.kindergarten_id, child_ids),
        )
    queued_again = client.get(f"/api/v1/jobs/{parent_id}")
    assert queued_again.status_code == 200
    assert queued_again.json()["status"] == "queued"

    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='awaiting_confirmation'
            WHERE kindergarten_id=%s AND id=ANY(%s)""",
            (actor.kindergarten_id, child_ids),
        )
    complete = client.get(f"/api/v1/jobs/{parent_id}")

    assert complete.status_code == 200
    assert complete.json()["status"] == "succeeded"
    assert complete.json()["has_partial_failure"] is False

    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='failed',finished_at=now(),error_code='ai.timeout'
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, child_ids[0]),
        )
    partial = client.get(f"/api/v1/jobs/{parent_id}")

    assert partial.status_code == 200
    assert partial.json()["status"] == "succeeded"
    assert partial.json()["has_partial_failure"] is True

    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='failed',finished_at=now(),error_code='ai.timeout'
            WHERE kindergarten_id=%s AND id=ANY(%s)""",
            (actor.kindergarten_id, child_ids),
        )
        parent_row = connection.execute(
            """SELECT execution_status,attempt_count,max_attempts,lease_owner
            FROM background_jobs WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, parent_id),
        ).fetchone()
    failed = client.get(f"/api/v1/jobs/{parent_id}")

    assert failed.status_code == 200
    assert failed.json()["status"] == "failed"
    assert failed.json()["has_partial_failure"] is False
    assert parent_row == (None, None, None, None)


def test_poll_interval_stays_between_one_and_two_seconds(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/batch",
        json={"expected_version": plan["version"], "teacher_context": "轮询测试"},
        headers=_headers(client),
    )

    assert response.status_code == 202
    assert 1000 <= response.json()["job"]["poll_after_ms"] <= 2000
