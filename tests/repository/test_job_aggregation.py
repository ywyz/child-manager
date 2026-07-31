# ruff: noqa: F811

"""T104 batch 只读状态投影的 PostgreSQL 验收。"""

from importlib import import_module
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    passkey_client,
)
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401
from tests.migrations.test_0008_ai_generation_results import (
    ResultDependencies,
    _native_url,
    _provision_dependencies,
)

_CHILDREN = (
    ("ai.morning_activity", "morning_activity"),
    ("ai.morning_talk", "morning_talk"),
    ("ai.indoor_area_game", "indoor_area_game"),
    ("ai.afternoon_outdoor_game", "afternoon_outdoor_game"),
)


def _repository(connection: psycopg.Connection[tuple[object, ...]]) -> Any:
    module = import_module("packages.backend.jobs.aggregation")
    return module.BatchJobAggregationRepository(connection)


def _insert_batch(
    connection: psycopg.Connection[tuple[object, ...]],
    dependencies: ResultDependencies,
    *,
    statuses: tuple[str, str, str, str],
) -> tuple[UUID, list[UUID]]:
    parent_id = uuid4()
    connection.execute(
        """INSERT INTO background_jobs
        (id,kindergarten_id,job_type,plan_id,requested_resource_version,
         idempotency_scope,idempotency_key,request_fingerprint_sha256,
         requested_by,trace_id)
        VALUES (%s,%s,'ai.batch',%s,1,'POST /plans/{plan_id}/ai/batch',%s,%s,%s,%s)""",
        (
            parent_id,
            dependencies.kindergarten_id,
            dependencies.plan_id,
            str(uuid4()),
            "a" * 64,
            dependencies.requested_by,
            uuid4(),
        ),
    )
    child_ids: list[UUID] = []
    for (job_type, target_section), status in zip(_CHILDREN, statuses, strict=True):
        child_id = uuid4()
        child_ids.append(child_id)
        terminal = status in {"failed", "adopted", "rejected", "expired"}
        connection.execute(
            """INSERT INTO background_jobs
            (id,kindergarten_id,parent_job_id,job_type,execution_status,plan_id,
             target_section,requested_resource_version,attempt_count,max_attempts,
             requested_by,trace_id,finished_at,error_code)
            VALUES (%s,%s,%s,%s,%s,%s,%s,1,0,3,%s,%s,
                    CASE WHEN %s THEN now() ELSE NULL END,
                    CASE WHEN %s='failed' THEN 'ai.timeout' ELSE NULL END)""",
            (
                child_id,
                dependencies.kindergarten_id,
                parent_id,
                job_type,
                status,
                dependencies.plan_id,
                target_section,
                dependencies.requested_by,
                uuid4(),
                terminal,
                status,
            ),
        )
    return parent_id, child_ids


def test_batch_projection_is_derived_from_exactly_four_children_without_parent_write(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        parent_id, child_ids = _insert_batch(
            connection,
            dependencies,
            statuses=("awaiting_confirmation", "failed", "queued", "adopted"),
        )
        before = connection.execute(
            """SELECT execution_status,attempt_count,max_attempts,queued_at,started_at,finished_at
            FROM background_jobs WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, parent_id),
        ).fetchone()

        repository = _repository(connection)
        projection = repository.get(actor.kindergarten_id, parent_id)
        after = connection.execute(
            """SELECT execution_status,attempt_count,max_attempts,queued_at,started_at,finished_at
            FROM background_jobs WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, parent_id),
        ).fetchone()

    assert projection is not None
    assert projection.id == parent_id
    assert projection.status == "queued"
    assert projection.has_partial_failure is True
    assert projection.attempt_count == projection.max_attempts == 0
    assert [child.id for child in projection.children] == child_ids
    assert before == after == (None, None, None, None, None, None)


def test_batch_projection_is_tenant_scoped_and_requires_the_frozen_four_child_shape(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        parent_id, child_ids = _insert_batch(
            connection,
            dependencies,
            statuses=(
                "awaiting_confirmation",
                "awaiting_confirmation",
                "awaiting_confirmation",
                "awaiting_confirmation",
            ),
        )
        repository = _repository(connection)

        assert repository.get(uuid4(), parent_id) is None
        connection.execute(
            "DELETE FROM background_jobs WHERE kindergarten_id=%s AND id=%s",
            (actor.kindergarten_id, child_ids[-1]),
        )
        with pytest.raises(ValueError, match="恰好包含四个子任务"):
            repository.get(actor.kindergarten_id, parent_id)
