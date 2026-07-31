# ruff: noqa: F811

"""M6 预览拒绝、过期、撤权与显式重试 RED 验收。"""

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from importlib import import_module
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from packages.backend.prompts.catalog import validate_prompt_result_schema
from tests.api.ai_helpers import create_completed_ai_preview, provision_enabled_ai_model
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401

PREVIEW = {
    "topic": "春日观察",
    "questions": ["看到了什么？", "听到了什么？", "想到了什么？"],
}
FROZEN_RESULT_COLUMNS = """
target_section,target_section_baseline_sha256,input_context,input_sha256,
model_profile_id,model_name_snapshot,prompt_definition_id,prompt_version_id,
prompt_content_sha256,result_schema_code,result_schema_version
"""


def _native_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def _snapshot_count(
    connection: psycopg.Connection[tuple[object, ...]],
    kindergarten_id: UUID,
    plan_id: str,
) -> int:
    row = connection.execute(
        """SELECT count(*) FROM daily_activity_plan_snapshots
        WHERE kindergarten_id=%s AND plan_id=%s AND reason_code='ai_adopted'""",
        (kindergarten_id, plan_id),
    ).fetchone()
    assert row is not None
    count = row[0]
    assert isinstance(count, int)
    return count


def test_reject_is_idempotent_and_never_mutates_plan_or_creates_snapshot(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    job_id, _expected_version = create_completed_ai_preview(
        client,
        database_url=isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        plan_id=plan_id,
        task_code="morning_talk",
        teacher_context="拒绝后仍保留正文",
        output_content=PREVIEW,
    )
    before = client.get(f"/api/v1/plans/{plan_id}").json()

    first = client.post(f"/api/v1/jobs/{job_id}/reject", headers=csrf_headers(client))
    repeated = client.post(f"/api/v1/jobs/{job_id}/reject", headers=csrf_headers(client))

    assert first.status_code == repeated.status_code == 200
    assert first.json()["status"] == repeated.json()["status"] == "rejected"
    after = client.get(f"/api/v1/plans/{plan_id}").json()
    assert after["content"] == before["content"]
    assert after["version"] == before["version"]
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert _snapshot_count(connection, actor.kindergarten_id, plan_id) == 0
        row = connection.execute(
            """SELECT j.execution_status,r.rejected_by,r.rejected_at,r.adopted_at
            FROM background_jobs j
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            WHERE j.kindergarten_id=%s AND j.id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone()
    assert row is not None
    assert row[0] == "rejected"
    assert row[1] == actor.user_id
    assert row[2] is not None
    assert row[3] is None


def test_expiration_scheduler_transitions_due_previews_once(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    job_id, _expected_version = create_completed_ai_preview(
        client,
        database_url=isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        plan_id=plan_id,
        task_code="morning_talk",
        teacher_context="即将过期",
        output_content=PREVIEW,
    )
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """UPDATE ai_generation_results SET expires_at=%s
            WHERE kindergarten_id=%s AND job_id=%s""",
            (now - timedelta(seconds=1), actor.kindergarten_id, job_id),
        )

    adoption = import_module("packages.backend.lesson_plans.ai_adoption")
    service = adoption.AiAdoptionService(isolated_database_url)
    assert service.expire_due_results(now=now, limit=100) == 1
    assert service.expire_due_results(now=now, limit=100) == 0

    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        row = connection.execute(
            """SELECT j.execution_status,j.finished_at,r.adopted_at,r.rejected_at
            FROM background_jobs j
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            WHERE j.kindergarten_id=%s AND j.id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone()
        assert _snapshot_count(connection, actor.kindergarten_id, plan_id) == 0
    assert row is not None
    assert row[0] == "expired"
    assert row[1] is not None
    assert row[2:] == (None, None)


def test_explicit_retry_creates_new_root_and_clones_frozen_result_not_current_state(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    profile_id = provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    accepted = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_talk",
            "expected_version": plan["version"],
            "teacher_context": "必须由失败任务冻结",
        },
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )
    assert accepted.status_code == 202
    source_job_id = accepted.json()["job"]["id"]

    native_url = _native_url(isolated_database_url)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='failed',attempt_count=3,finished_at=now(),
                error_code='ai.timeout',error_summary='调用超时'
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, source_job_id),
        )
        source_frozen = connection.execute(
            f"""SELECT {FROZEN_RESULT_COLUMNS} FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.kindergarten_id, source_job_id),
        ).fetchone()
    assert source_frozen is not None

    current = client.get(f"/api/v1/plans/{plan_id}").json()
    changed = deepcopy(current["content"])
    changed["morning_talk"] = {
        "topic": "失败后教师修改",
        "questions": ["修改了吗？", "为什么改？", "保留什么？"],
    }
    saved = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json={
            "expected_version": current["version"],
            "content": changed,
            "authors": [
                {"user_id": author["user_id"], "sort_order": author["sort_order"]}
                for author in current["authors"]
            ],
        },
        headers=csrf_headers(client),
    )
    assert saved.status_code == 200
    changed_model = client.patch(
        f"/api/v1/settings/ai-model-profiles/{profile_id}",
        json={
            "name": "M6 API 测试模型",
            "api_base_url": "https://ai.example.test/v1",
            "model_name": "changed-after-failure",
            "api_key": None,
            "capability_codes": ["text", "structured_output"],
            "max_concurrency": 2,
            "rate_limit_per_minute": None,
            "is_default": True,
        },
        headers=csrf_headers(client),
    )
    assert changed_model.status_code == 200

    retried = client.post(
        f"/api/v1/jobs/{source_job_id}/retry",
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )

    assert retried.status_code == 202
    retry_job_id = retried.json()["job"]["id"]
    assert retry_job_id != source_job_id
    with psycopg.connect(native_url) as connection:
        retry_job = connection.execute(
            """SELECT parent_job_id,retry_of_job_id,execution_status
            FROM background_jobs WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, retry_job_id),
        ).fetchone()
        clone = connection.execute(
            f"""SELECT {FROZEN_RESULT_COLUMNS},output_content,output_sha256,
                       adopted_at,rejected_at
            FROM ai_generation_results WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.kindergarten_id, retry_job_id),
        ).fetchone()
    assert retry_job == (None, UUID(source_job_id), "pending_dispatch")
    assert clone is not None
    assert clone[: len(source_frozen)] == source_frozen
    assert clone[len(source_frozen) :] == (None, None, None, None)


def test_batch_and_nonfailed_ai_jobs_reject_explicit_retry(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    headers = csrf_headers(client) | {"Idempotency-Key": str(uuid4())}
    batch = client.post(
        f"/api/v1/plans/{plan_id}/ai/batch",
        json={"expected_version": plan["version"], "teacher_context": "不可重试父任务"},
        headers=headers,
    )
    assert batch.status_code == 202
    child_id = batch.json()["job"]["children"][0]["id"]

    parent_retry = client.post(
        f"/api/v1/jobs/{batch.json()['job']['id']}/retry",
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )
    child_retry = client.post(
        f"/api/v1/jobs/{child_id}/retry",
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )

    assert parent_retry.status_code == child_retry.status_code == 409
    assert parent_retry.json()["code"] == child_retry.json()["code"] == "job.retry_not_allowed"


@pytest.mark.parametrize("job_type", ["prompt.test", "word.export"])
def test_non_ai_failed_jobs_reject_explicit_retry_without_creating_child(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    job_type: str,
) -> None:
    client, actor = ai_admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    job_id = uuid4()
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """INSERT INTO background_jobs
            (id,kindergarten_id,job_type,execution_status,plan_id,attempt_count,max_attempts,
             requested_by,trace_id,finished_at,error_code,error_summary)
            VALUES (%s,%s,%s,'failed',%s,3,3,%s,%s,now(),'job.test_failure','测试失败')""",
            (
                job_id,
                actor.kindergarten_id,
                job_type,
                UUID(plan_id) if job_type == "word.export" else None,
                actor.user_id,
                uuid4(),
            ),
        )

    response = client.post(
        f"/api/v1/jobs/{job_id}/retry",
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "job.retry_not_allowed"
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND retry_of_job_id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone() == (0,)


def test_cross_tenant_failed_job_is_hidden_from_retry(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, _actor = ai_admin_client
    other_kindergarten_id = uuid4()
    other_user_id = uuid4()
    other_job_id = uuid4()
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """INSERT INTO kindergartens (id,name,timezone,is_active)
            VALUES (%s,'不可见测试园','Asia/Shanghai',true)""",
            (other_kindergarten_id,),
        )
        connection.execute(
            """INSERT INTO users
            (id,kindergarten_id,username,username_normalized,display_name,
             webauthn_user_handle,status,backup_auth_version)
            VALUES (%s,%s,'other-worker','other-worker','其他园教师',%s,'active',1)""",
            (
                other_user_id,
                other_kindergarten_id,
                uuid4().bytes + uuid4().bytes,
            ),
        )
        connection.execute(
            """INSERT INTO background_jobs
            (id,kindergarten_id,job_type,execution_status,attempt_count,max_attempts,
             requested_by,trace_id,finished_at,error_code,error_summary)
            VALUES (%s,%s,'prompt.test','failed',3,3,%s,%s,now(),
                    'job.test_failure','测试失败')""",
            (other_job_id, other_kindergarten_id, other_user_id, uuid4()),
        )

    response = client.post(
        f"/api/v1/jobs/{other_job_id}/retry",
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 404


class NoCallExpectedClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate_structured(self, **_kwargs: object) -> dict[str, object]:
        self.calls += 1
        return {"objectives": ["不应调用。", "不应调用。", "不应调用。"]}


@pytest.mark.parametrize(
    ("invalidated_gate", "expected_key_reads"),
    [
        ("account_active", 0),
        ("class_permission", 0),
        ("plan_archived", 0),
        ("model_active", 0),
        ("model_capabilities", 0),
        ("key_available", 1),
    ],
)
def test_worker_rechecks_live_gate_before_reading_key_or_calling_provider(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    invalidated_gate: str,
    expected_key_reads: int,
) -> None:
    client, actor = ai_admin_client
    profile_id = provision_enabled_ai_model(client)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    accepted = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "morning_activity",
            "expected_version": plan["version"],
            "teacher_context": "排队后重新校验",
        },
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )
    assert accepted.status_code == 202
    job_id = accepted.json()["job"]["id"]
    native_url = _native_url(isolated_database_url)
    provider = NoCallExpectedClient()
    key_reads = 0

    def read_key(_profile: object) -> str:
        nonlocal key_reads
        key_reads += 1
        if invalidated_gate == "key_available":
            raise LookupError("test key unavailable")
        return "test-key"

    with psycopg.connect(native_url, autocommit=True) as connection:
        connection.execute(
            """UPDATE background_jobs SET execution_status='queued',queued_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, job_id),
        )
        if invalidated_gate == "account_active":
            connection.execute(
                """UPDATE users SET status='suspended',updated_at=now()
                WHERE kindergarten_id=%s AND id=%s""",
                (actor.kindergarten_id, actor.user_id),
            )
        elif invalidated_gate == "class_permission":
            connection.execute(
                """DELETE FROM user_roles AS ur USING roles AS r
                WHERE ur.role_id=r.id AND ur.kindergarten_id=%s AND ur.user_id=%s
                  AND r.code='admin'""",
                (actor.kindergarten_id, actor.user_id),
            )
            connection.execute(
                """DELETE FROM class_teachers
                WHERE kindergarten_id=%s AND class_id=%s AND user_id=%s""",
                (actor.kindergarten_id, class_id, actor.user_id),
            )
        elif invalidated_gate == "plan_archived":
            connection.execute(
                """UPDATE daily_activity_plans
                SET archived_at=now(),archived_by=%s,updated_at=now()
                WHERE kindergarten_id=%s AND id=%s""",
                (actor.user_id, actor.kindergarten_id, plan_id),
            )
        elif invalidated_gate == "model_active":
            connection.execute(
                """UPDATE ai_model_profiles SET is_active=false,updated_at=now()
                WHERE kindergarten_id=%s AND id=%s""",
                (actor.kindergarten_id, profile_id),
            )
        elif invalidated_gate == "model_capabilities":
            connection.execute(
                """DELETE FROM ai_model_profile_capabilities
                WHERE kindergarten_id=%s AND model_profile_id=%s
                  AND capability_code='structured_output'""",
                (actor.kindergarten_id, profile_id),
            )

        runner = import_module("packages.backend.jobs.ai_runner")
        store = runner.AiJobStore(connection)
        executor = runner.AiJobRunner(
            store=store,
            client=provider,
            authorizer=store,
            read_api_key=read_key,
            validate_url=lambda value: value,
            validate_result=lambda code, result, input_context: validate_prompt_result_schema(
                code,
                result,
                input_context=input_context,
            ),
        )
        executor.execute(
            actor.kindergarten_id,
            UUID(job_id),
            worker_id="worker-live-gate",
        )
        row = connection.execute(
            """SELECT j.execution_status,j.error_code,r.output_content,r.output_sha256
            FROM background_jobs j
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            WHERE j.kindergarten_id=%s AND j.id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone()

    assert provider.calls == 0
    assert key_reads == expected_key_reads
    assert row is not None
    assert row[0] == "failed"
    assert row[1] is not None
    assert row[2:] == (None, None)
