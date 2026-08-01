# ruff: noqa: F811

"""T129 Word 导出 Repository 园所隔离与不可变输入 RED。"""

from importlib import import_module
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context

TEMPLATE_SHA256 = "72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043"


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _repository(connection: psycopg.Connection[tuple[object, ...]]) -> Any:
    try:
        module = import_module("packages.backend.exports.repository")
    except ModuleNotFoundError:
        pytest.fail("T129 ExportRepository 尚未实现")
    repository_type = getattr(module, "ExportRepository", None)
    if repository_type is None:
        pytest.fail("T129 ExportRepository 尚未实现")
    return repository_type(connection)


def _insert_word_job(
    connection: psycopg.Connection[tuple[object, ...]],
    *,
    kindergarten_id: UUID,
    plan_id: UUID,
    requested_by: UUID,
) -> UUID:
    job_id = uuid4()
    connection.execute(
        """INSERT INTO background_jobs
        (id,kindergarten_id,job_type,execution_status,plan_id,requested_resource_version,
         idempotency_scope,idempotency_key,request_fingerprint_sha256,attempt_count,max_attempts,
         requested_by,trace_id)
        VALUES (%s,%s,'word.export','pending_dispatch',%s,1,
                'POST /api/v1/plans/{plan_id}/exports',%s,%s,0,3,%s,%s)""",
        (
            job_id,
            kindergarten_id,
            plan_id,
            str(uuid4()),
            uuid4().hex + uuid4().hex,
            requested_by,
            uuid4(),
        ),
    )
    return job_id


def _create_pending(
    repository: Any,
    *,
    kindergarten_id: UUID,
    plan: dict[str, object],
    exported_by: UUID,
    job_id: UUID,
    export_id: UUID | None = None,
) -> Any:
    context_snapshot = {
        "kindergarten_name": plan["kindergarten_name_snapshot"],
        "class_name": plan["class_name_snapshot"],
        "age_group_name": plan["age_group_name_snapshot"],
        "semester_name": plan["semester_name_snapshot"],
        "semester_start_date": plan["semester_start_date_snapshot"],
        "semester_end_date": plan["semester_end_date_snapshot"],
        "teaching_week_number": plan["teaching_week_number"],
        "teaching_week_text": plan["teaching_week_text"],
        "activity_date_text": plan["activity_date_text"],
        "season": plan["season"],
        "authors": plan["authors"],
    }
    return repository.create_pending(
        kindergarten_id,
        export_id=export_id or uuid4(),
        plan_id=UUID(str(plan["id"])),
        plan_version=int(str(plan["version"])),
        snapshot_id=None,
        job_id=job_id,
        display_filename="一日活动计划_向日葵班_2026-03-02.docx",
        storage_key=f"{uuid4()}.docx",
        context_snapshot=context_snapshot,
        content_snapshot=plan["content"],
        content_schema_version=int(str(plan["content_schema_version"])),
        content_sha256="1" * 64,
        template_code="daily_activity_plan.v1",
        template_filename="teacherplan.docx",
        template_sha256=TEMPLATE_SHA256,
        exported_by=exported_by,
    )


def test_repository_create_read_list_and_status_transitions_are_tenant_scoped(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _class_id, plan_id_text = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id_text}").json()
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        repository = _repository(connection)
        job_id = _insert_word_job(
            connection,
            kindergarten_id=actor.kindergarten_id,
            plan_id=UUID(plan_id_text),
            requested_by=actor.user_id,
        )
        created = _create_pending(
            repository,
            kindergarten_id=actor.kindergarten_id,
            plan=plan,
            exported_by=actor.user_id,
            job_id=job_id,
        )
        assert repository.get(actor.kindergarten_id, created.id) == created
        assert repository.get(uuid4(), created.id) is None
        items, total = repository.list_for_plan(
            actor.kindergarten_id,
            UUID(plan_id_text),
            page=1,
            page_size=20,
        )
        assert total == 1 and [item.id for item in items] == [created.id]
        assert repository.list_for_plan(uuid4(), UUID(plan_id_text), page=1, page_size=20) == (
            [],
            0,
        )

        completed = repository.mark_succeeded(
            actor.kindergarten_id,
            created.id,
            file_size=1024,
            file_sha256="2" * 64,
        )
        assert completed is not None and completed.status == "succeeded"
        assert (
            repository.mark_failed(
                actor.kindergarten_id,
                created.id,
                error_code="export.storage_failed",
                error_summary="不得覆盖成功记录。",
            )
            is None
        )


def test_repository_keeps_each_export_and_storage_key_unique(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _class_id, plan_id_text = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id_text}").json()
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        repository = _repository(connection)
        first_job = _insert_word_job(
            connection,
            kindergarten_id=actor.kindergarten_id,
            plan_id=UUID(plan_id_text),
            requested_by=actor.user_id,
        )
        first = _create_pending(
            repository,
            kindergarten_id=actor.kindergarten_id,
            plan=plan,
            exported_by=actor.user_id,
            job_id=first_job,
        )
        second_job = _insert_word_job(
            connection,
            kindergarten_id=actor.kindergarten_id,
            plan_id=UUID(plan_id_text),
            requested_by=actor.user_id,
        )
        second = _create_pending(
            repository,
            kindergarten_id=actor.kindergarten_id,
            plan=plan,
            exported_by=actor.user_id,
            job_id=second_job,
        )

    assert first.id != second.id
    assert first.job_id != second.job_id
    assert first.storage_key != second.storage_key


def test_frozen_context_and_content_cannot_be_updated_after_creation(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _class_id, plan_id_text = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id_text}").json()
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        repository = _repository(connection)
        job_id = _insert_word_job(
            connection,
            kindergarten_id=actor.kindergarten_id,
            plan_id=UUID(plan_id_text),
            requested_by=actor.user_id,
        )
        created = _create_pending(
            repository,
            kindergarten_id=actor.kindergarten_id,
            plan=plan,
            exported_by=actor.user_id,
            job_id=job_id,
        )
        with pytest.raises(psycopg.DatabaseError):
            connection.execute(
                """UPDATE daily_activity_plan_exports
                SET content_snapshot='{}'::jsonb
                WHERE kindergarten_id=%s AND id=%s""",
                (actor.kindergarten_id, created.id),
            )
