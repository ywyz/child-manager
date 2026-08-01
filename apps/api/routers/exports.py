"""Word 导出创建、历史、详情和受保护下载 HTTP 映射。"""

from typing import Annotated, cast
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request, status
from fastapi.responses import FileResponse

from apps.api.dependencies import CurrentSessionDependency, ExportServiceDependency
from apps.api.routers.auth import require_csrf
from packages.backend.exports.repository import ExportRecord
from packages.backend.exports.service import DOCX_MEDIA_TYPE, ExportAcceptance
from packages.backend.jobs.repository import JobRecord
from packages.contracts.exports import (
    Export,
    ExportAccepted,
    ExportContentSchemaVersion,
    ExportPage,
    ExportRequest,
    ExportStatus,
    ExportTemplateSha256,
)
from packages.contracts.jobs import Job, JobStatus, JobType

router = APIRouter(tags=["Exports"])


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


def _export(record: ExportRecord) -> Export:
    return Export(
        id=record.id,
        plan_id=record.plan_id,
        plan_version=record.plan_version,
        content_schema_version=cast(ExportContentSchemaVersion, record.content_schema_version),
        content_sha256=record.content_sha256,
        job_id=record.job_id,
        status=cast(ExportStatus, record.status),
        display_filename=record.display_filename,
        file_size=record.file_size,
        file_sha256=record.file_sha256,
        template_sha256=cast(ExportTemplateSha256, record.template_sha256),
        exported_at=record.exported_at,
        file_missing_at=record.file_missing_at,
        error_code=record.error_code,
        error_summary=record.error_summary,
        created_at=record.created_at,
    )


def _job(record: JobRecord, export: ExportRecord) -> Job:
    return Job(
        id=record.id,
        job_type=cast(JobType, record.job_type),
        status=cast(JobStatus, record.status),
        plan_id=export.plan_id,
        requested_resource_version=export.plan_version,
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


def _accepted(value: ExportAcceptance) -> ExportAccepted:
    return ExportAccepted(job=_job(value.job, value.export), export=_export(value.export))


@router.post(
    "/api/v1/plans/{plan_id}/exports",
    response_model=ExportAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_export(
    plan_id: UUID,
    body: ExportRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: ExportServiceDependency,
    idempotency_key: Annotated[
        str,
        Header(alias="Idempotency-Key", min_length=1, max_length=200),
    ],
) -> ExportAccepted:
    require_csrf(request)
    return _accepted(
        service.create(
            session,
            plan_id,
            body,
            idempotency_key=idempotency_key,
            request_id=_request_id(request),
        )
    )


@router.get("/api/v1/plans/{plan_id}/exports", response_model=ExportPage)
def list_exports(
    plan_id: UUID,
    session: CurrentSessionDependency,
    service: ExportServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ExportPage:
    records, total = service.list_for_plan(
        session,
        plan_id,
        page=page,
        page_size=page_size,
    )
    return ExportPage(
        items=[_export(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/api/v1/exports/{export_id}", response_model=Export)
def get_export(
    export_id: UUID,
    session: CurrentSessionDependency,
    service: ExportServiceDependency,
) -> Export:
    return _export(service.get(session, export_id))


@router.get("/api/v1/exports/{export_id}/download", response_class=FileResponse)
def download_export(
    export_id: UUID,
    session: CurrentSessionDependency,
    service: ExportServiceDependency,
) -> FileResponse:
    download = service.download(session, export_id)
    encoded_filename = quote(download.record.display_filename, safe="")
    return FileResponse(
        download.path,
        media_type=DOCX_MEDIA_TYPE,
        headers={
            "Content-Disposition": (
                'attachment; filename="daily_activity_plan.docx"; '
                f"filename*=UTF-8''{encoded_filename}"
            )
        },
    )
