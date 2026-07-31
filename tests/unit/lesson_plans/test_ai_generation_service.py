# ruff: noqa: F811

"""直接调用 AI 生成服务验证受理事务，不经过 FastAPI 路由。"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from packages.backend.identity.repository import IdentityRepository
from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.lesson_plans.ai_fingerprints import (
    generation_input_sha256,
    section_sha256,
)
from packages.backend.lesson_plans.ai_generation import AiGenerationService
from packages.contracts.lesson_plans import AiBatchRequest, AiGenerationRequest
from tests.api.ai_helpers import provision_enabled_ai_model
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _session(database_url: str, actor: ActorFixture) -> SessionUser:
    with psycopg.connect(_native_url(database_url)) as connection:
        user = IdentityRepository(connection, actor.kindergarten_id).get_user(actor.user_id)
    assert user is not None
    return SessionUser(
        user=user,
        role_codes=["admin", "teacher"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=None,
    )


@dataclass
class RecordingDispatcher:
    job_ids: list[UUID] = field(default_factory=list)

    def dispatch(self, job_id: UUID) -> None:
        self.job_ids.append(job_id)


def _replace_areas(
    client: TestClient,
    class_id: str,
    area_type: str,
    names: list[str],
) -> None:
    response = client.put(
        f"/api/v1/settings/classes/{class_id}/areas/{area_type}",
        json={
            "areas": [
                {"name": name, "sort_order": index, "is_active": True}
                for index, name in enumerate(names)
            ]
        },
        headers=csrf_headers(client),
    )
    assert response.status_code == 204


def test_single_generation_freezes_saved_inputs_without_mutating_plan(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id_text = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id_text}").json()
    plan_id = UUID(plan_id_text)
    dispatcher = RecordingDispatcher()
    service = AiGenerationService(
        database_url=isolated_database_url,
        dispatcher=dispatcher,
    )

    accepted = service.create_single(
        _session(isolated_database_url, actor),
        plan_id,
        AiGenerationRequest(
            task_code="morning_activity",
            expected_version=before["version"],
            teacher_context="冻结的教师补充",
        ),
        idempotency_key=str(uuid4()),
        request_id=uuid4(),
    )

    assert accepted.job.job_type == "ai.morning_activity"
    assert accepted.job.requested_resource_version == before["version"]
    assert accepted.children == ()
    assert len(accepted.results) == 1
    result = accepted.results[0]
    assert result.job_id == accepted.job.id
    input_context = result.input_context
    assert input_context is not None
    assert input_context == {
        "age_group_name": before["age_group_name_snapshot"],
        "class_name": before["class_name_snapshot"],
        "plan_date": before["plan_date"],
        "season": before["season"],
        "teacher_context": "冻结的教师补充",
        "teaching_week_text": before["teaching_week_text"],
        "weekday_text": "星期一",
    }
    server_input = dict(input_context)
    teacher_context = str(server_input.pop("teacher_context"))
    assert result.input_sha256 == generation_input_sha256(
        task_code="morning_activity",
        teacher_context=teacher_context,
        server_input=server_input,
    )
    assert result.target_section_baseline_sha256 == section_sha256(
        before["content"]["morning_activity"]
    )
    assert result.output_content is None
    assert result.output_sha256 is None
    assert dispatcher.job_ids == [accepted.job.id]

    after = client.get(f"/api/v1/plans/{plan_id_text}").json()
    assert after["version"] == before["version"]
    assert after["content"] == before["content"]


def test_batch_creates_non_executable_parent_and_exactly_four_dispatched_children(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    class_id, plan_id_text = provision_editable_plan_context(client, actor)
    _replace_areas(client, class_id, "indoor", ["建构区", "阅读区"])
    _replace_areas(client, class_id, "outdoor", ["攀爬区"])
    plan = client.get(f"/api/v1/plans/{plan_id_text}").json()
    dispatcher = RecordingDispatcher()
    service = AiGenerationService(
        database_url=isolated_database_url,
        dispatcher=dispatcher,
    )

    accepted = service.create_batch(
        _session(isolated_database_url, actor),
        UUID(plan_id_text),
        AiBatchRequest(
            expected_version=plan["version"],
            teacher_context="关注春季与合作",
        ),
        idempotency_key=str(uuid4()),
        request_id=uuid4(),
    )

    assert accepted.job.job_type == "ai.batch"
    assert accepted.job.status is None
    assert accepted.job.attempt_count is None
    assert accepted.job.max_attempts is None
    assert accepted.job.idempotency_scope == "POST /api/v1/plans/{plan_id}/ai/batch"
    assert accepted.job.idempotency_key is not None
    assert accepted.job.request_fingerprint_sha256 is not None
    assert len(accepted.job.request_fingerprint_sha256) == 64
    assert len(accepted.children) == 4
    assert {child.job_type for child in accepted.children} == {
        "ai.morning_activity",
        "ai.morning_talk",
        "ai.indoor_area_game",
        "ai.afternoon_outdoor_game",
    }
    assert {child.parent_job_id for child in accepted.children} == {accepted.job.id}
    assert {child.target_section for child in accepted.children} == {
        "morning_activity",
        "morning_talk",
        "indoor_area_game",
        "afternoon_outdoor_game",
    }
    assert all(child.idempotency_scope is None for child in accepted.children)
    assert all(child.idempotency_key is None for child in accepted.children)
    assert all(child.request_fingerprint_sha256 is None for child in accepted.children)
    assert len(accepted.results) == 4
    assert accepted.job.id not in dispatcher.job_ids
    assert set(dispatcher.job_ids) == {child.id for child in accepted.children}

    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        parent_shape = connection.execute(
            """SELECT execution_status,attempt_count,max_attempts,lease_owner,
                      lease_expires_at,last_heartbeat_at,queued_at,started_at,
                      finished_at,error_code,error_summary
            FROM background_jobs WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, accepted.job.id),
        ).fetchone()
        parent_result_count = connection.execute(
            """SELECT count(*) FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.kindergarten_id, accepted.job.id),
        ).fetchone()
    assert parent_shape == (None,) * 11
    assert parent_result_count == (0,)


def test_batch_missing_indoor_area_only_fails_indoor_child_and_single_is_rejected(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    class_id, plan_id_text = provision_editable_plan_context(client, actor)
    _replace_areas(client, class_id, "outdoor", ["沙水区"])
    plan = client.get(f"/api/v1/plans/{plan_id_text}").json()
    dispatcher = RecordingDispatcher()
    service = AiGenerationService(
        database_url=isolated_database_url,
        dispatcher=dispatcher,
    )
    session = _session(isolated_database_url, actor)

    accepted = service.create_batch(
        session,
        UUID(plan_id_text),
        AiBatchRequest(
            expected_version=plan["version"],
            teacher_context="保持其他栏目继续",
        ),
        idempotency_key=str(uuid4()),
        request_id=uuid4(),
    )

    indoor = next(child for child in accepted.children if child.job_type == "ai.indoor_area_game")
    assert indoor.status == "failed"
    assert indoor.error_code == "ai.area_required"
    assert indoor.id not in dispatcher.job_ids
    assert {result.job_id for result in accepted.results} == {
        child.id for child in accepted.children if child.id != indoor.id
    }
    assert len(accepted.results) == 3

    with pytest.raises(IdentityError) as caught:
        service.create_single(
            session,
            UUID(plan_id_text),
            AiGenerationRequest(
                task_code="indoor_area_game",
                expected_version=plan["version"],
                teacher_context="仍缺少室内区域",
            ),
            idempotency_key=str(uuid4()),
            request_id=uuid4(),
        )
    assert caught.value.status_code == 422
    assert caught.value.code == "ai.area_required"


def test_idempotency_replays_same_request_and_fingerprint_includes_actual_plan_path(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    class_id, plan_id_text = provision_editable_plan_context(client, actor)
    first_plan = client.get(f"/api/v1/plans/{plan_id_text}").json()
    second_open = client.post(
        "/api/v1/plans/open",
        json={"class_id": class_id, "plan_date": "2026-03-03"},
        headers=csrf_headers(client),
    )
    assert second_open.status_code == 201
    second_plan = second_open.json()
    dispatcher = RecordingDispatcher()
    service = AiGenerationService(
        database_url=isolated_database_url,
        dispatcher=dispatcher,
    )
    session = _session(isolated_database_url, actor)
    key = str(uuid4())
    body = AiGenerationRequest(
        task_code="morning_talk",
        expected_version=first_plan["version"],
        teacher_context="同一请求",
    )

    first = service.create_single(
        session,
        UUID(plan_id_text),
        body,
        idempotency_key=key,
        request_id=uuid4(),
    )
    replay = service.create_single(
        session,
        UUID(plan_id_text),
        body,
        idempotency_key=key,
        request_id=uuid4(),
    )

    assert replay.replayed
    assert replay.job.id == first.job.id
    assert dispatcher.job_ids == [first.job.id]

    with pytest.raises(IdentityError) as changed_body:
        service.create_single(
            session,
            UUID(plan_id_text),
            body.model_copy(update={"teacher_context": "改变输入"}),
            idempotency_key=key,
            request_id=uuid4(),
        )
    assert changed_body.value.status_code == 409
    assert changed_body.value.code == "job.idempotency_conflict"

    with pytest.raises(IdentityError) as changed_path:
        service.create_single(
            session,
            UUID(second_plan["id"]),
            body,
            idempotency_key=key,
            request_id=uuid4(),
        )
    assert changed_path.value.status_code == 409
    assert changed_path.value.code == "job.idempotency_conflict"
