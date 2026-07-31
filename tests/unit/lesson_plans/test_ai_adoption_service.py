# ruff: noqa: F811

"""T105 AI 预览采用/拒绝事务的直连服务门禁。"""

from importlib import import_module
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.lesson_plans.ai_adoption import AiAdoptionService
from packages.backend.lesson_plans.ai_generation import AiGenerationService
from packages.contracts.lesson_plans import AiGenerationRequest
from tests.api.ai_helpers import provision_enabled_ai_model
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401

PREVIEW = {
    "topic": "春日观察",
    "questions": ["你看到了什么？", "你听到了什么？", "你想到了什么？"],
}


def _native_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def _session(actor: ActorFixture) -> SessionUser:
    return cast(
        SessionUser,
        SimpleNamespace(
            user=SimpleNamespace(
                id=actor.user_id,
                kindergarten_id=actor.kindergarten_id,
                display_name="测试管理员",
            ),
            role_codes=("admin", "teacher"),
            request_id=None,
        ),
    )


def _completed_preview(
    database_url: str,
    actor: ActorFixture,
    plan_id: str,
) -> tuple[UUID, int]:
    session = _session(actor)
    with psycopg.connect(_native_url(database_url)) as connection:
        row = connection.execute(
            """SELECT version FROM daily_activity_plans
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, plan_id),
        ).fetchone()
    assert row is not None
    expected_version = int(row[0])
    accepted = AiGenerationService(database_url=database_url).create_single(
        session,
        UUID(plan_id),
        AiGenerationRequest(
            task_code="morning_talk",
            expected_version=expected_version,
            teacher_context="围绕春日观察",
        ),
        idempotency_key=str(uuid4()),
        request_id=None,
    )
    job_id = accepted.job.id
    result_repository_type = import_module(
        "packages.backend.jobs.ai_results"
    ).AiGenerationResultRepository
    fingerprint = import_module(
        "packages.backend.lesson_plans.ai_fingerprints"
    ).canonical_json_sha256(PREVIEW)
    with psycopg.connect(_native_url(database_url)) as connection:
        assert result_repository_type(connection).complete_pending(
            actor.kindergarten_id,
            job_id,
            output_content=PREVIEW,
            output_sha256=fingerprint,
        )
        connection.execute(
            """UPDATE background_jobs SET execution_status='awaiting_confirmation'
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, job_id),
        )
    return job_id, expected_version


def _service(database_url: str) -> AiAdoptionService:
    return AiAdoptionService(database_url)


def test_adopt_is_atomic_and_idempotent(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    job_id, expected_version = _completed_preview(
        isolated_database_url,
        actor,
        plan_id,
    )

    first = _service(isolated_database_url).adopt(
        _session(actor),
        job_id,
        expected_version=expected_version,
    )
    repeated = _service(isolated_database_url).adopt(
        _session(actor),
        job_id,
        expected_version=expected_version,
    )

    assert first.version == expected_version + 1
    assert repeated.version == first.version
    assert first.content["morning_talk"] == PREVIEW
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        row = connection.execute(
            """SELECT j.execution_status,r.adopted_by,r.rejected_at,
                      count(s.id) FILTER (WHERE s.reason_code='ai_adopted')
            FROM background_jobs j
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            LEFT JOIN daily_activity_plan_snapshots s
              ON s.kindergarten_id=j.kindergarten_id AND s.plan_id=j.plan_id
            WHERE j.kindergarten_id=%s AND j.id=%s
            GROUP BY j.execution_status,r.adopted_by,r.rejected_at""",
            (actor.kindergarten_id, job_id),
        ).fetchone()
    assert row == ("adopted", actor.user_id, None, 1)


def test_reject_is_atomic_and_idempotent_without_plan_change(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    job_id, expected_version = _completed_preview(
        isolated_database_url,
        actor,
        plan_id,
    )

    first = _service(isolated_database_url).reject(_session(actor), job_id)
    repeated = _service(isolated_database_url).reject(_session(actor), job_id)

    assert first.status == repeated.status == "rejected"
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        row = connection.execute(
            """SELECT p.version,p.content,j.execution_status,r.rejected_by,r.adopted_at,
                      count(s.id) FILTER (WHERE s.reason_code='ai_adopted')
            FROM daily_activity_plans p
            JOIN background_jobs j
              ON j.kindergarten_id=p.kindergarten_id AND j.plan_id=p.id
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            LEFT JOIN daily_activity_plan_snapshots s
              ON s.kindergarten_id=p.kindergarten_id AND s.plan_id=p.id
            WHERE p.kindergarten_id=%s AND p.id=%s AND j.id=%s
            GROUP BY p.version,p.content,j.execution_status,r.rejected_by,r.adopted_at""",
            (actor.kindergarten_id, plan_id, job_id),
        ).fetchone()
    assert row is not None
    assert row[0] == expected_version
    assert row[2:] == ("rejected", actor.user_id, None, 0)


def test_target_change_and_version_conflict_roll_back_everything(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    job_id, expected_version = _completed_preview(
        isolated_database_url,
        actor,
        plan_id,
    )
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """UPDATE daily_activity_plans
            SET content=jsonb_set(
                content,
                '{morning_talk,topic}',
                to_jsonb(%s::text)
            ),version=version+1
            WHERE kindergarten_id=%s AND id=%s""",
            ("教师已经修改", actor.kindergarten_id, plan_id),
        )

    with pytest.raises(IdentityError) as conflict:
        _service(isolated_database_url).adopt(
            _session(actor),
            job_id,
            expected_version=expected_version,
        )
    assert conflict.value.code == "lesson_plan.version_conflict"
    with pytest.raises(IdentityError) as stale:
        _service(isolated_database_url).adopt(
            _session(actor),
            job_id,
            expected_version=expected_version + 1,
        )
    assert stale.value.code == "ai.preview_stale"

    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        row = connection.execute(
            """SELECT j.execution_status,r.adopted_at,r.rejected_at,
                      count(s.id) FILTER (WHERE s.reason_code='ai_adopted')
            FROM background_jobs j
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            LEFT JOIN daily_activity_plan_snapshots s
              ON s.kindergarten_id=j.kindergarten_id AND s.plan_id=j.plan_id
            WHERE j.kindergarten_id=%s AND j.id=%s
            GROUP BY j.execution_status,r.adopted_at,r.rejected_at""",
            (actor.kindergarten_id, job_id),
        ).fetchone()
    assert row == ("awaiting_confirmation", None, None, 0)
