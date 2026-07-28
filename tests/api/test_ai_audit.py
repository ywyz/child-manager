# ruff: noqa: F811

"""M6 AI 审计事件与脱敏重试谱系 RED 验收。"""

import json
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient

from packages.contracts import audit as audit_contracts
from tests.api.ai_helpers import create_completed_ai_preview, provision_enabled_ai_model
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401


def _event(name: str) -> audit_contracts.IdentityAuditEventCode:
    value = audit_contracts.IdentityAuditEventCode.__members__.get(name)
    assert value is not None, f"M6 audit event missing: {name}"
    return value


def test_ai_audit_event_codes_cover_creation_retries_result_reject_and_adopt() -> None:
    assert _event("AI_GENERATION_CREATED").value == "ai.generation_created"
    assert _event("AI_AUTOMATIC_RETRY_SCHEDULED").value == "ai.automatic_retry_scheduled"
    assert _event("AI_GENERATION_RETRIED").value == "ai.generation_retried"
    assert _event("AI_GENERATION_SUCCEEDED").value == "ai.generation_succeeded"
    assert _event("AI_GENERATION_FAILED").value == "ai.generation_failed"
    assert _event("AI_PREVIEW_REJECTED").value == "ai.preview_rejected"
    assert _event("AI_PREVIEW_ADOPTED").value == "ai.preview_adopted"


def test_explicit_retry_audit_metadata_contains_ids_but_no_body_or_frozen_input() -> None:
    metadata_type = getattr(audit_contracts, "AiGenerationAuditMetadata", None)
    assert metadata_type is not None, "M6 audit missing: AiGenerationAuditMetadata"
    fields = set(metadata_type.model_fields)

    assert {"job_id", "retry_of_job_id", "attempt_count", "error_code"} <= fields
    assert {
        "input_context",
        "output_content",
        "plan_content",
        "prompt_content",
        "api_key",
    }.isdisjoint(fields)


def test_generation_reject_adopt_and_retry_write_sanitized_audit_rows(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    rejected_job_id, _version = create_completed_ai_preview(
        client,
        database_url=isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        plan_id=plan_id,
        task_code="morning_talk",
        teacher_context="审计不得复制此冻结输入",
        output_content={
            "topic": "审计不得复制此预览正文",
            "questions": ["问题一？", "问题二？", "问题三？"],
        },
    )
    rejected = client.post(
        f"/api/v1/jobs/{rejected_job_id}/reject",
        headers=csrf_headers(client),
    )
    assert rejected.status_code == 200

    adopted_job_id, expected_version = create_completed_ai_preview(
        client,
        database_url=isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        plan_id=plan_id,
        task_code="morning_talk",
        teacher_context="采用审计的冻结输入",
        output_content={
            "topic": "可采用预览",
            "questions": ["看到了什么？", "听到了什么？", "想到了什么？"],
        },
    )
    adopted = client.post(
        f"/api/v1/jobs/{adopted_job_id}/adopt",
        json={"expected_version": expected_version},
        headers=csrf_headers(client),
    )
    assert adopted.status_code == 200

    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    failed = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_activity",
            "expected_version": plan["version"],
            "teacher_context": "重试审计不得复制此冻结输入",
        },
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )
    assert failed.status_code == 202
    failed_job_id = failed.json()["job"]["id"]
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='failed',attempt_count=3,finished_at=now(),
                error_code='ai.timeout',error_summary='调用超时'
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, failed_job_id),
        )
    retried = client.post(
        f"/api/v1/jobs/{failed_job_id}/retry",
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )
    assert retried.status_code == 202
    retry_job_id = retried.json()["job"]["id"]

    with psycopg.connect(native_url) as connection:
        rows = connection.execute(
            """SELECT event_code,job_id,metadata FROM audit_events
            WHERE kindergarten_id=%s AND event_code LIKE 'ai.%%'
            ORDER BY occurred_at,id""",
            (actor.kindergarten_id,),
        ).fetchall()
    event_codes = [str(row[0]) for row in rows]
    assert {
        "ai.generation_created",
        "ai.generation_retried",
        "ai.preview_rejected",
        "ai.preview_adopted",
    } <= set(event_codes)
    retry_rows = [row for row in rows if row[0] == "ai.generation_retried"]
    assert len(retry_rows) == 1
    retry_metadata = retry_rows[0][2]
    assert str(retry_rows[0][1]) == retry_job_id
    assert retry_metadata["job_id"] == retry_job_id
    assert retry_metadata["retry_of_job_id"] == failed_job_id

    serialized = json.dumps(rows, ensure_ascii=False, default=str)
    for secret in (
        "审计不得复制此冻结输入",
        "审计不得复制此预览正文",
        "采用审计的冻结输入",
        "重试审计不得复制此冻结输入",
        "test-secret-value",
    ):
        assert secret not in serialized
