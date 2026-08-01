# ruff: noqa: F811

"""M6 AI 结果占位迁移的 PostgreSQL RED 验收。"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import psycopg
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.types.json import Jsonb

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401

REVISION = "0008_ai_generation_results"
PROMPT_CODE = "daily_activity_plan.morning_activity"
REQUIRED_COLUMNS = {
    "id",
    "kindergarten_id",
    "job_id",
    "plan_id",
    "target_section",
    "requested_resource_version",
    "target_section_baseline_sha256",
    "input_context",
    "input_sha256",
    "model_profile_id",
    "model_name_snapshot",
    "prompt_definition_id",
    "prompt_version_id",
    "prompt_content_sha256",
    "result_schema_code",
    "result_schema_version",
    "output_content",
    "output_sha256",
    "expires_at",
    "adopted_at",
    "adopted_by",
    "rejected_at",
    "rejected_by",
    "content_cleared_at",
    "created_at",
    "updated_at",
}


@dataclass(frozen=True)
class ResultDependencies:
    kindergarten_id: UUID
    requested_by: UUID
    plan_id: UUID
    model_profile_id: UUID
    prompt_definition_id: UUID
    prompt_version_id: UUID


def _native_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def _provision_dependencies(
    client: TestClient,
    actor: ActorFixture,
) -> ResultDependencies:
    _class_id, plan_id_text = provision_editable_plan_context(client, actor)
    profile = client.post(
        "/api/v1/settings/ai-model-profiles",
        json={
            "name": "M6 迁移测试模型",
            "api_base_url": "https://ai.example.test/v1",
            "model_name": "structured-test-model",
            "api_key": "test-secret-value",
            "capability_codes": ["text", "structured_output"],
            "max_concurrency": 2,
            "rate_limit_per_minute": None,
            "is_default": True,
        },
        headers=csrf_headers(client),
    )
    assert profile.status_code == 201
    definition = client.get(f"/api/v1/prompts/{PROMPT_CODE}")
    assert definition.status_code == 200
    body = definition.json()
    assert body["effective_version_id"] is not None
    return ResultDependencies(
        kindergarten_id=actor.kindergarten_id,
        requested_by=actor.user_id,
        plan_id=UUID(plan_id_text),
        model_profile_id=UUID(profile.json()["id"]),
        prompt_definition_id=UUID(body["id"]),
        prompt_version_id=UUID(body["effective_version_id"]),
    )


def _insert_job(
    connection: psycopg.Connection[tuple[object, ...]],
    dependencies: ResultDependencies,
    *,
    job_type: str = "ai.morning_activity",
    target_section: str = "morning_activity",
) -> UUID:
    job_id = uuid4()
    connection.execute(
        """INSERT INTO background_jobs
        (id,kindergarten_id,job_type,execution_status,plan_id,target_section,
         requested_resource_version,attempt_count,max_attempts,requested_by,trace_id)
        VALUES (%s,%s,%s,'pending_dispatch',%s,%s,1,0,3,%s,%s)""",
        (
            job_id,
            dependencies.kindergarten_id,
            job_type,
            dependencies.plan_id,
            target_section,
            dependencies.requested_by,
            uuid4(),
        ),
    )
    return job_id


def _result_values(
    dependencies: ResultDependencies,
    job_id: UUID,
    **changes: object,
) -> dict[str, object]:
    values: dict[str, object] = {
        "id": uuid4(),
        "kindergarten_id": dependencies.kindergarten_id,
        "job_id": job_id,
        "plan_id": dependencies.plan_id,
        "target_section": "morning_activity",
        "requested_resource_version": 1,
        "target_section_baseline_sha256": "1" * 64,
        "input_context": Jsonb({"teacher_context": "冻结输入"}),
        "input_sha256": "2" * 64,
        "model_profile_id": dependencies.model_profile_id,
        "model_name_snapshot": "structured-test-model",
        "prompt_definition_id": dependencies.prompt_definition_id,
        "prompt_version_id": dependencies.prompt_version_id,
        "prompt_content_sha256": "3" * 64,
        "result_schema_code": "prompt.morning_activity.v1",
        "result_schema_version": 1,
        "output_content": None,
        "output_sha256": None,
        "expires_at": datetime.now(UTC) + timedelta(days=30),
        "adopted_at": None,
        "adopted_by": None,
        "rejected_at": None,
        "rejected_by": None,
        "content_cleared_at": None,
    }
    values.update(changes)
    return values


def _insert_result(
    connection: psycopg.Connection[tuple[object, ...]],
    values: dict[str, object],
) -> None:
    columns = list(values)
    statement = sql.SQL("INSERT INTO ai_generation_results ({}) VALUES ({})").format(
        sql.SQL(",").join(map(sql.Identifier, columns)),
        sql.SQL(",").join(sql.Placeholder() for _column in columns),
    )
    connection.execute(statement, [values[column] for column in columns])


def _insert_other_tenant_plan(
    connection: psycopg.Connection[tuple[object, ...]],
    source: ResultDependencies,
) -> tuple[UUID, UUID]:
    kindergarten_id = uuid4()
    user_id = uuid4()
    age_group_id = uuid4()
    class_id = uuid4()
    semester_id = uuid4()
    plan_id = uuid4()
    connection.execute(
        """INSERT INTO kindergartens (id,name,timezone,is_active)
        VALUES (%s,'第二测试园','Asia/Shanghai',true)""",
        (kindergarten_id,),
    )
    connection.execute(
        """INSERT INTO users
        (id,kindergarten_id,username,username_normalized,display_name,
         webauthn_user_handle,status,backup_auth_version)
        VALUES (%s,%s,'other-admin','other-admin','第二园管理员',%s,'active',1)""",
        (user_id, kindergarten_id, uuid4().bytes + uuid4().bytes),
    )
    connection.execute(
        """INSERT INTO age_groups
        (id,kindergarten_id,code,name,sort_order,is_active)
        VALUES (%s,%s,'middle','中班',2,true)""",
        (age_group_id, kindergarten_id),
    )
    connection.execute(
        """INSERT INTO classes
        (id,kindergarten_id,name,name_normalized,age_group_id,is_active,created_by,updated_by)
        VALUES (%s,%s,'第二园向日葵班','第二园向日葵班',%s,true,%s,%s)""",
        (class_id, kindergarten_id, age_group_id, user_id, user_id),
    )
    connection.execute(
        """INSERT INTO semesters
        (id,kindergarten_id,name,start_date,end_date,is_current,is_active,created_by,updated_by)
        VALUES (%s,%s,'第二园春季学期','2026-02-04','2026-06-30',true,true,%s,%s)""",
        (semester_id, kindergarten_id, user_id, user_id),
    )
    connection.execute(
        """INSERT INTO daily_activity_plans
        (id,kindergarten_id,class_id,semester_id,plan_date,
         kindergarten_name_snapshot,class_name_snapshot,age_group_name_snapshot,
         semester_name_snapshot,semester_start_date_snapshot,semester_end_date_snapshot,
         teaching_week_number,teaching_week_text,activity_date_text,season_code,
         content,content_schema_version,version,archived_at,archived_by,created_by,updated_by)
        SELECT %s,%s,%s,%s,plan_date,
               '第二测试园','第二园向日葵班','中班','第二园春季学期',
               semester_start_date_snapshot,semester_end_date_snapshot,
               teaching_week_number,teaching_week_text,activity_date_text,season_code,
               content,content_schema_version,version,NULL,NULL,%s,%s
        FROM daily_activity_plans
        WHERE kindergarten_id=%s AND id=%s""",
        (
            plan_id,
            kindergarten_id,
            class_id,
            semester_id,
            user_id,
            user_id,
            source.kindergarten_id,
            source.plan_id,
        ),
    )
    return kindergarten_id, plan_id


def test_0008_follows_ai_prompts_jobs_and_precedes_current_head() -> None:
    script = ScriptDirectory.from_config(Config("alembic.ini"))
    revisions = {revision.revision: revision.down_revision for revision in script.walk_revisions()}

    assert revisions.get(REVISION) == "0007_ai_prompts_jobs"
    assert revisions.get("0009_group_activity_sources") == REVISION
    assert revisions.get("0010_word_exports") == "0009_group_activity_sources"
    assert script.get_heads() == ["0010_word_exports"]


def test_0008_creates_the_frozen_result_shape(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        columns = {
            str(row[0])
            for row in connection.execute(
                """SELECT column_name FROM information_schema.columns
                WHERE table_schema=current_schema()
                  AND table_name='ai_generation_results'"""
            ).fetchall()
        }

    assert columns >= REQUIRED_COLUMNS


def test_result_job_reference_is_one_tenant_plan_job_composite_foreign_key(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        definitions = {
            " ".join(str(row[0]).lower().split())
            for row in connection.execute(
                """SELECT pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE conrelid='ai_generation_results'::regclass
                  AND contype='f'"""
            ).fetchall()
        }

    assert any(
        definition.startswith("foreign key (kindergarten_id, plan_id, job_id)")
        and "references background_jobs(kindergarten_id, plan_id, id)" in definition
        for definition in definitions
    )


def test_pending_placeholder_is_unique_and_tenant_plan_scoped(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(connection, dependencies)
        values = _result_values(dependencies, job_id)
        _insert_result(connection, values)

        with (
            pytest.raises(psycopg.errors.UniqueViolation),
            connection.transaction(),
        ):
            _insert_result(
                connection,
                values | {"id": uuid4()},
            )

        _other_kindergarten_id, other_plan_id = _insert_other_tenant_plan(
            connection,
            dependencies,
        )
        other_job_id = _insert_job(connection, dependencies)
        with (
            pytest.raises(psycopg.errors.ForeignKeyViolation),
            connection.transaction(),
        ):
            _insert_result(
                connection,
                _result_values(
                    dependencies,
                    other_job_id,
                    plan_id=other_plan_id,
                ),
            )


@pytest.mark.parametrize(
    ("job_type", "target_section"),
    [
        ("ai.morning_activity", "morning_activity"),
        ("ai.morning_talk", "morning_talk"),
        ("ai.group_activity_split", "group_activity"),
        ("ai.group_activity_add_step", "group_activity"),
        ("ai.indoor_area_game", "indoor_area_game"),
        ("ai.afternoon_outdoor_game", "afternoon_outdoor_game"),
        ("ai.daily_reflection", "daily_reflection"),
    ],
)
def test_every_executable_ai_type_can_create_one_frozen_pending_result(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    job_type: str,
    target_section: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(
            connection,
            dependencies,
            job_type=job_type,
            target_section=target_section,
        )
        _insert_result(
            connection,
            _result_values(
                dependencies,
                job_id,
                target_section=target_section,
                result_schema_code=f"prompt.{target_section}.v1",
            ),
        )
        stored = connection.execute(
            """SELECT target_section,input_context,input_sha256,output_content,output_sha256
            FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (dependencies.kindergarten_id, job_id),
        ).fetchone()

    assert stored is not None
    assert stored[:3] == (
        target_section,
        {"teacher_context": "冻结输入"},
        "2" * 64,
    )
    assert stored[3:] == (None, None)


@pytest.mark.parametrize(
    "changes",
    [
        {"input_context": None},
        {"target_section_baseline_sha256": None},
        {"output_content": Jsonb({"objectives": ["目标一。"]})},
        {"output_sha256": "4" * 64},
        {"adopted_at": datetime.now(UTC)},
        {"rejected_by": uuid4()},
        {
            "output_content": Jsonb({"objectives": ["目标一。"]}),
            "output_sha256": "4" * 64,
            "adopted_at": datetime.now(UTC),
            "adopted_by": uuid4(),
            "rejected_at": datetime.now(UTC),
            "rejected_by": uuid4(),
        },
    ],
)
def test_invalid_pending_output_and_decision_shapes_are_rejected(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    changes: dict[str, object],
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(connection, dependencies)
        with pytest.raises(psycopg.errors.CheckViolation):
            _insert_result(
                connection,
                _result_values(dependencies, job_id, **changes),
            )


def test_decision_and_cleanup_require_preexisting_output_and_are_final(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(connection, dependencies)
        _insert_result(connection, _result_values(dependencies, job_id))
        output = Jsonb({"objectives": ["目标一。", "目标二。", "目标三。"]})

        with (
            pytest.raises(psycopg.errors.RaiseException),
            connection.transaction(),
        ):
            connection.execute(
                """UPDATE ai_generation_results
                SET output_content=%s,output_sha256=%s,adopted_at=now(),adopted_by=%s
                WHERE kindergarten_id=%s AND job_id=%s""",
                (
                    output,
                    "4" * 64,
                    actor.user_id,
                    dependencies.kindergarten_id,
                    job_id,
                ),
            )

        with (
            pytest.raises(psycopg.errors.RaiseException),
            connection.transaction(),
        ):
            connection.execute(
                """UPDATE ai_generation_results
                SET input_context=NULL,output_sha256=%s,content_cleared_at=now()
                WHERE kindergarten_id=%s AND job_id=%s""",
                ("4" * 64, dependencies.kindergarten_id, job_id),
            )

        connection.execute(
            """UPDATE ai_generation_results
            SET output_content=%s,output_sha256=%s
            WHERE kindergarten_id=%s AND job_id=%s""",
            (output, "4" * 64, dependencies.kindergarten_id, job_id),
        )
        connection.execute(
            """UPDATE ai_generation_results
            SET adopted_at=now(),adopted_by=%s
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.user_id, dependencies.kindergarten_id, job_id),
        )

        with (
            pytest.raises(psycopg.errors.RaiseException),
            connection.transaction(),
        ):
            connection.execute(
                """UPDATE ai_generation_results
                SET adopted_at=adopted_at + interval '1 second'
                WHERE kindergarten_id=%s AND job_id=%s""",
                (dependencies.kindergarten_id, job_id),
            )


def test_frozen_fields_output_once_and_cleanup_are_database_enforced(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(connection, dependencies)
        _insert_result(connection, _result_values(dependencies, job_id))

        with (
            pytest.raises(psycopg.errors.RaiseException),
            connection.transaction(),
        ):
            connection.execute(
                """UPDATE ai_generation_results
                SET input_context=%s
                WHERE kindergarten_id=%s AND job_id=%s""",
                (
                    Jsonb({"teacher_context": "不得覆盖"}),
                    dependencies.kindergarten_id,
                    job_id,
                ),
            )

        output = Jsonb({"objectives": ["目标一。", "目标二。", "目标三。"]})
        updated = connection.execute(
            """UPDATE ai_generation_results
            SET output_content=%s,output_sha256=%s
            WHERE kindergarten_id=%s AND job_id=%s""",
            (output, "4" * 64, dependencies.kindergarten_id, job_id),
        )
        assert updated.rowcount == 1

        with (
            pytest.raises(psycopg.errors.RaiseException),
            connection.transaction(),
        ):
            connection.execute(
                """UPDATE ai_generation_results
                SET output_content=%s,output_sha256=%s
                WHERE kindergarten_id=%s AND job_id=%s""",
                (
                    Jsonb({"objectives": ["覆盖。"]}),
                    "5" * 64,
                    dependencies.kindergarten_id,
                    job_id,
                ),
            )

        connection.execute(
            """UPDATE ai_generation_results
            SET adopted_at=now(),adopted_by=%s
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.user_id, dependencies.kindergarten_id, job_id),
        )
        connection.execute(
            """UPDATE ai_generation_results
            SET input_context=NULL,output_content=NULL,content_cleared_at=now()
            WHERE kindergarten_id=%s AND job_id=%s""",
            (dependencies.kindergarten_id, job_id),
        )
        cleaned = connection.execute(
            """SELECT input_context,input_sha256,output_content,output_sha256,
                      content_cleared_at
            FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (dependencies.kindergarten_id, job_id),
        ).fetchone()

    assert cleaned is not None
    assert cleaned[:4] == (None, "2" * 64, None, "4" * 64)
    assert cleaned[4] is not None
