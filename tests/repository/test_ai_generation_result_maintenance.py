# ruff: noqa: F811

"""T104 AI 预览过期和正文保留策略的 PostgreSQL 验收。"""

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb

from apps.worker import scheduler as scheduler_module
from apps.worker.scheduler import run_ai_result_maintenance
from packages.backend.jobs.ai_results import AiGenerationResultRepository
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    passkey_client,
)
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401
from tests.migrations.test_0008_ai_generation_results import (
    ResultDependencies,
    _insert_job,
    _insert_result,
    _native_url,
    _provision_dependencies,
    _result_values,
)

_OUTPUT = {"objectives": ["目标一。", "目标二。", "目标三。"]}


class _PartiallyFailingMaintenanceRepository:
    def __init__(self, failing_kindergarten_id: UUID) -> None:
        self.failing_kindergarten_id = failing_kindergarten_id
        self.visited: list[UUID] = []

    def expire_due_previews(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
    ) -> int:
        del now, limit
        self.visited.append(kindergarten_id)
        if kindergarten_id == self.failing_kindergarten_id:
            raise RuntimeError("不得记录此诊断正文")
        return 1

    def clear_retained_content(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
    ) -> int:
        del kindergarten_id, now, limit
        return 2


def _completed_preview(
    connection: psycopg.Connection[tuple[object, ...]],
    dependencies: ResultDependencies,
    *,
    status: str,
    created_at: datetime,
    expires_at: datetime,
    actor_id: UUID,
) -> UUID:
    job_id = _insert_job(connection, dependencies)
    terminal = status in {"failed", "adopted", "rejected", "expired"}
    connection.execute(
        """UPDATE background_jobs
        SET execution_status=%s,finished_at=CASE WHEN %s THEN %s ELSE NULL END,
            error_code=CASE WHEN %s='failed' THEN 'ai.invalid_response' ELSE NULL END
        WHERE kindergarten_id=%s AND id=%s""",
        (
            status,
            terminal,
            created_at,
            status,
            dependencies.kindergarten_id,
            job_id,
        ),
    )
    changes: dict[str, object] = {
        "output_content": Jsonb(_OUTPUT),
        "output_sha256": "4" * 64,
        "expires_at": expires_at,
        "created_at": created_at,
        "updated_at": created_at,
    }
    if status == "adopted":
        changes |= {"adopted_at": created_at, "adopted_by": actor_id}
    if status == "rejected":
        changes |= {"rejected_at": created_at, "rejected_by": actor_id}
    _insert_result(connection, _result_values(dependencies, job_id, **changes))
    return job_id


def test_expire_due_previews_is_tenant_scoped_conditional_and_idempotent(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _completed_preview(
            connection,
            dependencies,
            status="awaiting_confirmation",
            created_at=now - timedelta(days=1),
            expires_at=now - timedelta(seconds=1),
            actor_id=actor.user_id,
        )
        repository = AiGenerationResultRepository(connection)

        assert repository.expire_due_previews(UUID(int=0), now=now, limit=100) == 0
        counts = run_ai_result_maintenance(
            repository=repository,
            kindergarten_ids=[actor.kindergarten_id],
            now=now,
        )
        repeated = run_ai_result_maintenance(
            repository=repository,
            kindergarten_ids=[actor.kindergarten_id],
            now=now,
        )
        row = connection.execute(
            """SELECT j.execution_status,j.finished_at,r.adopted_at,r.rejected_at,
                      r.output_content
            FROM background_jobs j
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            WHERE j.kindergarten_id=%s AND j.id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone()
        snapshots = connection.execute(
            """SELECT count(*) FROM daily_activity_plan_snapshots
            WHERE kindergarten_id=%s AND plan_id=%s""",
            (actor.kindergarten_id, dependencies.plan_id),
        ).fetchone()

    assert row is not None
    assert counts.expired == 1
    assert counts.content_cleared == 0
    assert repeated.expired == repeated.content_cleared == 0
    assert row[:4] == ("expired", now, None, None)
    assert row[4] == _OUTPUT
    assert snapshots == (0,)


def test_cleanup_clears_adopted_immediately_and_terminal_content_after_thirty_days(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    now = datetime.now(UTC)
    old = now - timedelta(days=31)
    young = now - timedelta(days=1)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        adopted_id = _completed_preview(
            connection,
            dependencies,
            status="adopted",
            created_at=young,
            expires_at=now + timedelta(days=29),
            actor_id=actor.user_id,
        )
        expired_old_id = _completed_preview(
            connection,
            dependencies,
            status="expired",
            created_at=old,
            expires_at=old + timedelta(days=30),
            actor_id=actor.user_id,
        )
        rejected_old_id = _completed_preview(
            connection,
            dependencies,
            status="rejected",
            created_at=old,
            expires_at=old + timedelta(days=30),
            actor_id=actor.user_id,
        )
        failed_old_id = _completed_preview(
            connection,
            dependencies,
            status="failed",
            created_at=old,
            expires_at=old + timedelta(days=30),
            actor_id=actor.user_id,
        )
        rejected_young_id = _completed_preview(
            connection,
            dependencies,
            status="rejected",
            created_at=young,
            expires_at=now + timedelta(days=29),
            actor_id=actor.user_id,
        )
        repository = AiGenerationResultRepository(connection)

        assert repository.clear_retained_content(UUID(int=0), now=now, limit=100) == 0
        assert repository.clear_retained_content(actor.kindergarten_id, now=now, limit=100) == 4
        assert repository.clear_retained_content(actor.kindergarten_id, now=now, limit=100) == 0
        rows = connection.execute(
            """SELECT job_id,input_context,input_sha256,output_content,output_sha256,
                      content_cleared_at,model_profile_id,prompt_version_id
            FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=ANY(%s)
            ORDER BY job_id""",
            (
                actor.kindergarten_id,
                [
                    adopted_id,
                    expired_old_id,
                    rejected_old_id,
                    failed_old_id,
                    rejected_young_id,
                ],
            ),
        ).fetchall()

    by_job = {row[0]: row[1:] for row in rows}
    for job_id in (adopted_id, expired_old_id, rejected_old_id, failed_old_id):
        cleaned = by_job[job_id]
        assert cleaned[:4] == (None, "2" * 64, None, "4" * 64)
        assert cleaned[4] == now
        assert cleaned[5:] == (
            dependencies.model_profile_id,
            dependencies.prompt_version_id,
        )
    assert by_job[rejected_young_id][0] == {"teacher_context": "冻结输入"}
    assert by_job[rejected_young_id][2] == _OUTPUT
    assert by_job[rejected_young_id][4] is None


def test_maintenance_isolates_tenant_failures_and_logs_only_sanitized_diagnostics(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failing_kindergarten_id = UUID(int=1)
    succeeding_kindergarten_id = UUID(int=2)
    repository = _PartiallyFailingMaintenanceRepository(failing_kindergarten_id)

    monkeypatch.setattr(scheduler_module.logger, "disabled", False)
    with caplog.at_level(logging.ERROR, logger=scheduler_module.__name__):
        counts = run_ai_result_maintenance(
            repository=repository,
            kindergarten_ids=[failing_kindergarten_id, succeeding_kindergarten_id],
            now=datetime(2026, 7, 29, tzinfo=UTC),
        )

    assert repository.visited == [failing_kindergarten_id, succeeding_kindergarten_id]
    assert counts.expired == 1
    assert counts.content_cleared == 2
    assert any(record.__dict__.get("exception_type") == "RuntimeError" for record in caplog.records)
    assert "不得记录此诊断正文" not in caplog.text
