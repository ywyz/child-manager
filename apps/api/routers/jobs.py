"""PostgreSQL 权威任务查询端点。"""

import os
from uuid import UUID

import psycopg
from fastapi import APIRouter

from apps.api.dependencies import AdminSessionDependency
from packages.backend.identity.service import IdentityError
from packages.backend.jobs.repository import JobRepository
from packages.contracts.jobs import Job

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: UUID, session: AdminSessionDependency) -> Job:
    database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    kindergarten_id = session.user.kindergarten_id
    if not database_url:
        raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
    if kindergarten_id is None:
        raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
    with psycopg.connect(
        database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    ) as connection:
        record = JobRepository(connection).get(kindergarten_id, job_id)
    if record is None:
        raise IdentityError(404, "resource.not_found", "任务不存在。")
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
