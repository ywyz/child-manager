"""一日活动计划读取、保存、归档与历史版本端点。"""

from datetime import date
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, File, Header, Query, Request, Response, UploadFile, status

from apps.api.dependencies import (
    AiGenerationServiceDependency,
    CurrentSessionDependency,
    JobQueryServiceDependency,
    LessonPlanServiceDependency,
    LessonPlanSourceServiceDependency,
    ReflectionGenerationServiceDependency,
)
from apps.api.routers.auth import require_csrf
from packages.backend.integrations.files.docx import ARCHIVE_LIMIT_BYTES
from packages.backend.lesson_plans.repository import SnapshotRecord
from packages.backend.lesson_plans.schemas import readable_content
from packages.backend.lesson_plans.service import PlanView
from packages.backend.lesson_plans.sources import LessonPlanSourceRecord
from packages.contracts.jobs import JobAccepted, JobPage
from packages.contracts.lesson_plans import (
    AiBatchRequest,
    AiGenerationRequest,
    Author,
    LessonPlanSource,
    LessonPlanSourceDocxPreview,
    LessonPlanSourcePage,
    LessonPlanSourceTextWrite,
    LessonPlanSourceType,
    Plan,
    PlanOpenRequest,
    PlanPage,
    PlanSaveRequest,
    PlanSnapshot,
    PlanSnapshotContext,
    PlanSnapshotPage,
    SeasonCode,
    SnapshotReason,
    VersionRequest,
)

router = APIRouter(prefix="/api/v1/plans", tags=["Plans"])


def _plan(view: PlanView) -> Plan:
    record = view.record
    return Plan(
        id=record.id,
        class_id=record.class_id,
        semester_id=record.semester_id,
        plan_date=record.plan_date,
        kindergarten_name_snapshot=record.kindergarten_name_snapshot,
        class_name_snapshot=record.class_name_snapshot,
        age_group_name_snapshot=record.age_group_name_snapshot,
        semester_name_snapshot=record.semester_name_snapshot,
        semester_start_date_snapshot=record.semester_start_date_snapshot,
        semester_end_date_snapshot=record.semester_end_date_snapshot,
        teaching_week_number=record.teaching_week_number,
        teaching_week_text=record.teaching_week_text,
        activity_date_text=record.activity_date_text,
        season=cast(SeasonCode, record.season_code),
        content=readable_content(record.content, record.content_schema_version),
        content_schema_version=record.content_schema_version,
        version=record.version,
        authors=[
            Author(
                user_id=author.user_id,
                sort_order=author.sort_order,
                display_name_snapshot=author.display_name_snapshot,
            )
            for author in view.authors
        ],
        soft_warnings=view.soft_warnings,
        capabilities=view.capabilities,
        archived_at=record.archived_at,
    )


def _snapshot(record: SnapshotRecord) -> PlanSnapshot:
    return PlanSnapshot(
        id=record.id,
        plan_id=record.plan_id,
        plan_version=record.plan_version,
        reason_code=cast(SnapshotReason, record.reason_code),
        context_snapshot=PlanSnapshotContext.model_validate(record.context_snapshot),
        content=readable_content(record.content, record.content_schema_version),
        content_schema_version=record.content_schema_version,
        content_sha256=record.content_sha256,
        created_by=record.created_by,
        created_at=record.created_at,
    )


def _source(record: LessonPlanSourceRecord) -> LessonPlanSource:
    return LessonPlanSource(
        id=record.id,
        plan_id=record.plan_id,
        source_type=cast(LessonPlanSourceType, record.source_type),
        original_filename=record.original_filename,
        source_sha256=record.source_sha256,
        extracted_character_count=record.extracted_character_count,
        uploaded_by=record.uploaded_by,
        created_at=record.created_at,
    )


@router.get("", response_model=PlanPage)
def list_plans(
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
    class_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    author_id: UUID | None = None,
    archived: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PlanPage:
    views, total = service.list_plans(
        session,
        class_id=class_id,
        date_from=date_from,
        date_to=date_to,
        author_id=author_id,
        archived=archived,
        page=page,
        page_size=page_size,
    )
    return PlanPage(
        items=[_plan(view) for view in views],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post(
    "/open",
    response_model=Plan,
    responses={201: {"model": Plan, "description": "已创建"}},
)
def open_plan(
    body: PlanOpenRequest,
    request: Request,
    response: Response,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
) -> Plan:
    require_csrf(request)
    result = service.open_plan(session, class_id=body.class_id, plan_date=body.plan_date)
    if result.created:
        response.status_code = 201
    return _plan(result.view)


@router.get("/{plan_id}", response_model=Plan)
def get_plan(
    plan_id: UUID,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
) -> Plan:
    return _plan(service.get_plan(session, plan_id))


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


@router.get("/{plan_id}/group-activity-sources", response_model=LessonPlanSourcePage)
def list_group_activity_sources(
    plan_id: UUID,
    session: CurrentSessionDependency,
    service: LessonPlanSourceServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> LessonPlanSourcePage:
    records, total = service.list_history(
        session,
        plan_id=plan_id,
        page=page,
        page_size=page_size,
    )
    return LessonPlanSourcePage(
        items=[_source(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post(
    "/{plan_id}/group-activity-sources/text",
    response_model=LessonPlanSource,
    status_code=status.HTTP_201_CREATED,
)
def confirm_group_activity_text_source(
    plan_id: UUID,
    body: LessonPlanSourceTextWrite,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanSourceServiceDependency,
) -> LessonPlanSource:
    require_csrf(request)
    return _source(service.confirm_text(session, plan_id=plan_id, text=body.text))


@router.post(
    "/{plan_id}/group-activity-sources/docx",
    response_model=LessonPlanSourceDocxPreview,
)
async def preview_group_activity_docx_source(
    plan_id: UUID,
    file: Annotated[UploadFile, File()],
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanSourceServiceDependency,
) -> LessonPlanSourceDocxPreview:
    require_csrf(request)
    try:
        payload = await file.read(ARCHIVE_LIMIT_BYTES + 1)
    finally:
        await file.close()
    preview = service.preview_docx(
        session,
        plan_id=plan_id,
        filename=file.filename or "",
        content_type=file.content_type or "",
        payload=payload,
    )
    return LessonPlanSourceDocxPreview(
        original_filename=preview.original_filename,
        extracted_text=preview.extracted_text,
    )


@router.post(
    "/{plan_id}/group-activity-sources/docx/confirm",
    response_model=LessonPlanSource,
    status_code=status.HTTP_201_CREATED,
)
def confirm_group_activity_docx_source(
    plan_id: UUID,
    body: LessonPlanSourceDocxPreview,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanSourceServiceDependency,
) -> LessonPlanSource:
    require_csrf(request)
    return _source(
        service.confirm_docx(
            session,
            plan_id=plan_id,
            filename=body.original_filename,
            text=body.extracted_text,
        )
    )


@router.post(
    "/{plan_id}/ai/batch",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_ai_batch(
    plan_id: UUID,
    body: AiBatchRequest,
    request: Request,
    session: CurrentSessionDependency,
    generation: AiGenerationServiceDependency,
    query: JobQueryServiceDependency,
    idempotency_key: Annotated[
        str,
        Header(alias="Idempotency-Key", min_length=1, max_length=200),
    ],
) -> JobAccepted:
    require_csrf(request)
    accepted = generation.create_batch(
        session,
        plan_id,
        body,
        idempotency_key=idempotency_key,
        request_id=_request_id(request),
    )
    return JobAccepted(
        job=query.get(session, accepted.job.id),
        related_resource_id=plan_id,
    )


@router.post(
    "/{plan_id}/ai/generations",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_ai_generation(
    plan_id: UUID,
    body: AiGenerationRequest,
    request: Request,
    session: CurrentSessionDependency,
    generation: AiGenerationServiceDependency,
    reflection: ReflectionGenerationServiceDependency,
    query: JobQueryServiceDependency,
    idempotency_key: Annotated[
        str,
        Header(alias="Idempotency-Key", min_length=1, max_length=200),
    ],
) -> JobAccepted:
    require_csrf(request)
    if body.task_code == "daily_reflection":
        accepted = reflection.create(
            session,
            plan_id,
            body,
            idempotency_key=idempotency_key,
            request_id=_request_id(request),
        )
    else:
        accepted = generation.create_single(
            session,
            plan_id,
            body,
            idempotency_key=idempotency_key,
            request_id=_request_id(request),
        )
    return JobAccepted(
        job=query.get(session, accepted.job.id),
        related_resource_id=plan_id,
    )


@router.get("/{plan_id}/jobs", response_model=JobPage)
def list_plan_jobs(
    plan_id: UUID,
    session: CurrentSessionDependency,
    query: JobQueryServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> JobPage:
    items, total, has_adopted_group_activity_split = query.list_plan(
        session,
        plan_id,
        page=page,
        page_size=page_size,
    )
    return JobPage(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        has_adopted_group_activity_split=has_adopted_group_activity_split,
    )


def _save(
    *,
    plan_id: UUID,
    body: PlanSaveRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
    create_snapshot: bool,
) -> Plan:
    require_csrf(request)
    view = service.save(
        session,
        plan_id,
        expected_version=body.expected_version,
        content=body.content,
        authors=body.authors,
        create_snapshot=create_snapshot,
    )
    return _plan(view)


@router.put("/{plan_id}/autosave", response_model=Plan)
def autosave_plan(
    plan_id: UUID,
    body: PlanSaveRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
) -> Plan:
    return _save(
        plan_id=plan_id,
        body=body,
        request=request,
        session=session,
        service=service,
        create_snapshot=False,
    )


@router.put("/{plan_id}/save", response_model=Plan)
def save_plan(
    plan_id: UUID,
    body: PlanSaveRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
) -> Plan:
    return _save(
        plan_id=plan_id,
        body=body,
        request=request,
        session=session,
        service=service,
        create_snapshot=True,
    )


def _set_archived(
    *,
    plan_id: UUID,
    body: VersionRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
    archived: bool,
) -> Plan:
    require_csrf(request)
    view = service.set_archived(
        session,
        plan_id,
        expected_version=body.expected_version,
        archived=archived,
    )
    return _plan(view)


@router.post("/{plan_id}/archive", response_model=Plan)
def archive_plan(
    plan_id: UUID,
    body: VersionRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
) -> Plan:
    return _set_archived(
        plan_id=plan_id,
        body=body,
        request=request,
        session=session,
        service=service,
        archived=True,
    )


@router.post("/{plan_id}/unarchive", response_model=Plan)
def unarchive_plan(
    plan_id: UUID,
    body: VersionRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
) -> Plan:
    return _set_archived(
        plan_id=plan_id,
        body=body,
        request=request,
        session=session,
        service=service,
        archived=False,
    )


@router.get("/{plan_id}/snapshots", response_model=PlanSnapshotPage)
def list_snapshots(
    plan_id: UUID,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PlanSnapshotPage:
    records, total = service.list_snapshots(session, plan_id, page=page, page_size=page_size)
    return PlanSnapshotPage(
        items=[_snapshot(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post(
    "/{plan_id}/snapshots/{snapshot_id}/restore",
    response_model=Plan,
)
def restore_snapshot(
    plan_id: UUID,
    snapshot_id: UUID,
    body: VersionRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: LessonPlanServiceDependency,
) -> Plan:
    require_csrf(request)
    view = service.restore_snapshot(
        session,
        plan_id,
        snapshot_id,
        expected_version=body.expected_version,
    )
    return _plan(view)
