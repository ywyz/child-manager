"""管理员提示词生命周期与异步测试薄路由。"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request, Response

from apps.api.dependencies import AdminSessionDependency, PromptServiceDependency
from apps.api.routers.auth import require_csrf
from packages.backend.jobs.repository import JobRecord
from packages.backend.prompts.repository import (
    PromptDefinitionRecord,
    PromptTestRunRecord,
    PromptVersionRecord,
)
from packages.contracts.jobs import Job, JobAccepted
from packages.contracts.prompts import (
    PromptDefinition,
    PromptDefinitionPage,
    PromptDraftWrite,
    PromptTestPage,
    PromptTestRequest,
    PromptTestRun,
    PromptVersion,
    PromptVersionPage,
)

router = APIRouter(prefix="/api/v1/prompts", tags=["Prompts"])


def _definition(record: PromptDefinitionRecord) -> PromptDefinition:
    return PromptDefinition(
        id=record.id,
        code=record.code,  # type: ignore[arg-type]
        name=record.name,
        variable_whitelist=list(record.variable_whitelist),
        required_capabilities=list(record.required_capabilities),  # type: ignore[arg-type]
        result_schema_code=record.result_schema_code,
        result_schema_version=1,
        model_profile_id=record.model_profile_id,
        effective_version_id=record.effective_version_id,
        draft_version_id=record.draft_version_id,
        is_active=record.is_active,
    )


def _version(record: PromptVersionRecord) -> PromptVersion:
    return PromptVersion(
        id=record.id,
        prompt_definition_id=record.prompt_definition_id,
        prompt_code=record.prompt_code,  # type: ignore[arg-type]
        version_number=record.version_number,
        source_type=record.source_type,  # type: ignore[arg-type]
        lifecycle_state=record.lifecycle_state,  # type: ignore[arg-type]
        content=record.content,
        content_sha256=record.content_sha256,
        based_on_version_id=record.based_on_version_id,
        created_by=record.created_by,
        created_at=record.created_at,
        published_by=record.published_by,
        published_at=record.published_at,
    )


def _run(record: PromptTestRunRecord) -> PromptTestRun:
    return PromptTestRun(
        id=record.id,
        job_id=record.job_id,
        prompt_code=record.prompt_code,  # type: ignore[arg-type]
        input_summary=record.input_summary,  # type: ignore[arg-type]
        status=record.status,  # type: ignore[arg-type]
        output_content=record.output_content,
        elapsed_ms=record.elapsed_ms,
        error_code=record.error_code,
        error_summary=record.error_summary,
        created_at=record.created_at,
    )


def _job(record: JobRecord) -> Job:
    return Job(
        id=record.id,
        job_type=record.job_type,  # type: ignore[arg-type]
        status=record.status,  # type: ignore[arg-type]
        attempt_count=record.attempt_count,
        max_attempts=record.max_attempts,
        trace_id=record.trace_id,
        created_at=record.created_at,
        queued_at=record.queued_at,
        started_at=record.started_at,
        finished_at=record.finished_at,
        error_code=record.error_code,
        error_message=record.error_summary,
    )


@router.get("", response_model=PromptDefinitionPage)
def list_prompts(
    session: AdminSessionDependency,
    service: PromptServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PromptDefinitionPage:
    records, total = service.list_definitions(session, page=page, page_size=page_size)
    return PromptDefinitionPage(
        items=[_definition(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{code}", response_model=PromptDefinition)
def get_prompt(
    code: str,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
) -> PromptDefinition:
    return _definition(service.get_definition(session, code))


@router.put("/{code}/draft", response_model=PromptVersion)
def save_prompt_draft(
    code: str,
    body: PromptDraftWrite,
    request: Request,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
) -> PromptVersion:
    require_csrf(request)
    return _version(
        service.save_draft(
            session,
            code,
            content=body.content,
            based_on_version_id=body.based_on_version_id,
        )
    )


@router.post("/{code}/publish", response_model=PromptVersion, status_code=201)
def publish_prompt(
    code: str,
    request: Request,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
) -> PromptVersion:
    require_csrf(request)
    return _version(service.publish(session, code))


@router.get("/{code}/versions", response_model=PromptVersionPage)
def list_prompt_versions(
    code: str,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PromptVersionPage:
    records, total = service.list_versions(session, code, page=page, page_size=page_size)
    return PromptVersionPage(
        items=[_version(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{code}/versions/{version_id}", response_model=PromptVersion)
def get_prompt_version(
    code: str,
    version_id: UUID,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
) -> PromptVersion:
    return _version(service.get_version(session, code, version_id))


@router.post("/{code}/versions/{version_id}/restore", response_model=PromptVersion, status_code=201)
def restore_prompt_version(
    code: str,
    version_id: UUID,
    request: Request,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
) -> PromptVersion:
    require_csrf(request)
    return _version(service.restore(session, code, version_id))


@router.get("/{code}/tests", response_model=PromptTestPage)
def list_prompt_tests(
    code: str,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=20)] = 20,
) -> PromptTestPage:
    records, total = service.list_tests(session, code, page=page, page_size=page_size)
    return PromptTestPage(
        items=[_run(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("/{code}/tests", response_model=JobAccepted, status_code=202)
def create_prompt_test(
    code: str,
    body: PromptTestRequest,
    request: Request,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=200)],
) -> JobAccepted:
    require_csrf(request)
    job, run = service.create_test(
        session,
        code,
        body,
        idempotency_key=idempotency_key,
        request_id=UUID(str(request.state.request_id)),
    )
    return JobAccepted(job=_job(job), related_resource_id=run.id if run is not None else None)


@router.delete("/{code}/tests", status_code=204)
def clear_prompt_tests(
    code: str,
    request: Request,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
) -> Response:
    require_csrf(request)
    service.clear_tests(session, code)
    return Response(status_code=204)


@router.get("/{code}/tests/{run_id}", response_model=PromptTestRun)
def get_prompt_test(
    code: str,
    run_id: UUID,
    session: AdminSessionDependency,
    service: PromptServiceDependency,
) -> PromptTestRun:
    return _run(service.get_test(session, code, run_id))
