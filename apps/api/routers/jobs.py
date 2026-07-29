"""后台任务查询、AI 预览决策与显式重试薄路由。"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Request, status

from apps.api.dependencies import (
    AiAdoptionServiceDependency,
    AiRetryServiceDependency,
    CurrentSessionDependency,
    JobQueryServiceDependency,
    LessonPlanServiceDependency,
)
from apps.api.routers.auth import require_csrf
from apps.api.routers.plans import _plan
from packages.contracts.jobs import Job, JobAccepted, JobPreview
from packages.contracts.lesson_plans import Plan, VersionRequest

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


@router.get("/{job_id}", response_model=Job)
def get_job(
    job_id: UUID,
    session: CurrentSessionDependency,
    service: JobQueryServiceDependency,
) -> Job:
    return service.get(session, job_id)


@router.get("/{job_id}/preview", response_model=JobPreview)
def get_ai_preview(
    job_id: UUID,
    session: CurrentSessionDependency,
    service: JobQueryServiceDependency,
) -> JobPreview:
    return service.preview(session, job_id)


@router.post("/{job_id}/adopt", response_model=Plan)
def adopt_ai_preview(
    job_id: UUID,
    body: VersionRequest,
    request: Request,
    session: CurrentSessionDependency,
    adoption: AiAdoptionServiceDependency,
    plans: LessonPlanServiceDependency,
) -> Plan:
    require_csrf(request)
    updated = adoption.adopt(
        session,
        job_id,
        expected_version=body.expected_version,
    )
    return _plan(plans.get_plan(session, updated.id))


@router.post("/{job_id}/reject", response_model=Job)
def reject_ai_preview(
    job_id: UUID,
    request: Request,
    session: CurrentSessionDependency,
    adoption: AiAdoptionServiceDependency,
    query: JobQueryServiceDependency,
) -> Job:
    require_csrf(request)
    adoption.reject(session, job_id)
    return query.get(session, job_id)


@router.post(
    "/{job_id}/retry",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def retry_ai_job(
    job_id: UUID,
    request: Request,
    session: CurrentSessionDependency,
    retry: AiRetryServiceDependency,
    query: JobQueryServiceDependency,
    idempotency_key: Annotated[
        str,
        Header(alias="Idempotency-Key", min_length=1, max_length=200),
    ],
) -> JobAccepted:
    require_csrf(request)
    accepted = retry.retry(
        session,
        job_id,
        idempotency_key=idempotency_key,
        request_id=_request_id(request),
    )
    return JobAccepted(
        job=query.get(session, accepted.job.id),
        related_resource_id=accepted.job.plan_id,
    )
