"""后台任务查询薄路由。"""

from uuid import UUID

from fastapi import APIRouter

from apps.api.dependencies import AdminSessionDependency, JobQueryServiceDependency
from packages.contracts.jobs import Job

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=Job)
def get_job(
    job_id: UUID,
    session: AdminSessionDependency,
    service: JobQueryServiceDependency,
) -> Job:
    record = service.get(session, job_id)
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
