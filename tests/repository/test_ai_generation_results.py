# ruff: noqa: F811

"""M6 AI 结果 Repository 隔离、冻结与幂等 RED 验收。"""

from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    passkey_client,
)
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401
from tests.migrations.test_0008_ai_generation_results import (
    ResultDependencies,
    _insert_job,
    _native_url,
    _provision_dependencies,
)


def _repository(connection: psycopg.Connection[tuple[object, ...]]) -> Any:
    module = import_module("packages.backend.jobs.ai_results")
    return module.AiGenerationResultRepository(connection)


def _create_pending(
    repository: Any,
    dependencies: ResultDependencies,
    job_id: UUID,
    *,
    kindergarten_id: UUID | None = None,
) -> Any:
    return repository.create_pending(
        kindergarten_id or dependencies.kindergarten_id,
        result_id=uuid4(),
        job_id=job_id,
        plan_id=dependencies.plan_id,
        target_section="morning_activity",
        requested_resource_version=1,
        target_section_baseline_sha256="1" * 64,
        input_context={"teacher_context": "冻结输入", "class_name": "向日葵班"},
        input_sha256="2" * 64,
        model_profile_id=dependencies.model_profile_id,
        model_name_snapshot="structured-test-model",
        prompt_definition_id=dependencies.prompt_definition_id,
        prompt_version_id=dependencies.prompt_version_id,
        prompt_content_sha256="3" * 64,
        result_schema_code="prompt.morning_activity.v1",
        result_schema_version=1,
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )


def _frozen(record: Any) -> tuple[object, ...]:
    return tuple(
        getattr(record, field)
        for field in (
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
        )
    )


def test_repository_create_and_read_are_tenant_scoped(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(connection, dependencies)
        repository = _repository(connection)
        created = _create_pending(repository, dependencies, job_id)

        assert repository.get_by_job(dependencies.kindergarten_id, job_id) == created
        assert repository.get_by_job(uuid4(), job_id) is None
        cross_tenant_job_id = _insert_job(connection, dependencies)
        with (
            pytest.raises(psycopg.errors.ForeignKeyViolation),
            connection.transaction(),
        ):
            _create_pending(
                repository,
                dependencies,
                cross_tenant_job_id,
                kindergarten_id=uuid4(),
            )
        assert created.output_content is None  # type: ignore[attr-defined]
        assert created.output_sha256 is None  # type: ignore[attr-defined]


def test_worker_completion_and_decisions_are_conditional_and_idempotent(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(connection, dependencies)
        repository = _repository(connection)
        _create_pending(repository, dependencies, job_id)
        output = {"objectives": ["目标一。", "目标二。", "目标三。"]}
        other_kindergarten_id = uuid4()

        assert not repository.complete_pending(
            other_kindergarten_id,
            job_id,
            output_content={"objectives": ["跨园不得写入。"]},
            output_sha256="9" * 64,
        )
        assert not repository.mark_rejected(
            other_kindergarten_id,
            job_id,
            actor_id=actor.user_id,
            rejected_at=datetime.now(UTC),
        )
        assert not repository.mark_adopted(
            other_kindergarten_id,
            job_id,
            actor_id=actor.user_id,
            adopted_at=datetime.now(UTC),
        )
        assert repository.complete_pending(
            dependencies.kindergarten_id,
            job_id,
            output_content=output,
            output_sha256="4" * 64,
        )
        assert not repository.complete_pending(
            dependencies.kindergarten_id,
            job_id,
            output_content={"objectives": ["不得覆盖。"]},
            output_sha256="5" * 64,
        )
        assert repository.mark_rejected(
            dependencies.kindergarten_id,
            job_id,
            actor_id=actor.user_id,
            rejected_at=datetime.now(UTC),
        )
        assert not repository.mark_adopted(
            dependencies.kindergarten_id,
            job_id,
            actor_id=actor.user_id,
            adopted_at=datetime.now(UTC),
        )
        stored = repository.get_by_job(dependencies.kindergarten_id, job_id)

    assert stored is not None
    assert stored.output_content == output
    assert stored.output_sha256 == "4" * 64
    assert stored.rejected_by == actor.user_id
    assert stored.adopted_at is None


def test_explicit_retry_clones_frozen_fields_not_current_state(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        source_job_id = _insert_job(connection, dependencies)
        repository = _repository(connection)
        source = _create_pending(repository, dependencies, source_job_id)
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='failed',finished_at=now(),error_code='ai.timeout'
            WHERE kindergarten_id=%s AND id=%s""",
            (dependencies.kindergarten_id, source_job_id),
        )
        connection.execute(
            """UPDATE daily_activity_plans
            SET content=%s,version=version+1,updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (
                Jsonb({"morning_activity": {"group_game": "后来修改"}}),
                dependencies.kindergarten_id,
                dependencies.plan_id,
            ),
        )
        connection.execute(
            """UPDATE ai_model_profiles
            SET model_name='model-changed-after-failure',
                call_config_revision=call_config_revision+1,
                updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (dependencies.kindergarten_id, dependencies.model_profile_id),
        )
        retry_job_id = _insert_job(connection, dependencies)
        connection.execute(
            """UPDATE background_jobs SET retry_of_job_id=%s
            WHERE kindergarten_id=%s AND id=%s""",
            (source_job_id, dependencies.kindergarten_id, retry_job_id),
        )

        assert (
            repository.clone_failed_to_pending(
                uuid4(),
                source_job_id=source_job_id,
                target_result_id=uuid4(),
                target_job_id=retry_job_id,
                expires_at=datetime.now(UTC) + timedelta(days=30),
            )
            is None
        )
        clone = repository.clone_failed_to_pending(
            dependencies.kindergarten_id,
            source_job_id=source_job_id,
            target_result_id=uuid4(),
            target_job_id=retry_job_id,
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )

    assert clone.job_id == retry_job_id
    assert _frozen(clone) == _frozen(source)
    assert clone.output_content is None
    assert clone.output_sha256 is None
    assert clone.adopted_at is None
    assert clone.rejected_at is None
