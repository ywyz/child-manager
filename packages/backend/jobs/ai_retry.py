"""最终失败 AI 任务的显式重试受理事务。"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import psycopg

from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.jobs.ai_results import AiGenerationResultRepository
from packages.backend.jobs.repository import JobRepository
from packages.backend.lesson_plans.ai_generation import (
    AiGenerationAcceptance,
    AiGenerationService,
    Dispatcher,
)
from packages.backend.lesson_plans.repository import LessonPlanRepository
from packages.backend.lesson_plans.service import LessonPlanService
from packages.contracts.common import canonical_request_fingerprint
from packages.contracts.jobs import JOB_RETRY_NOT_ALLOWED, is_explicit_ai_retry_allowed

_PREVIEW_RETENTION = timedelta(days=30)


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


class AiRetryService:
    def __init__(
        self,
        database_url: str,
        *,
        dispatcher: Dispatcher | None = None,
    ) -> None:
        self.database_url = database_url
        self.dispatcher = dispatcher

    @classmethod
    def from_environment(cls) -> AiRetryService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _not_allowed() -> IdentityError:
        return IdentityError(409, JOB_RETRY_NOT_ALLOWED, "当前任务不允许显式重试。")

    def retry(
        self,
        session: SessionUser,
        job_id: UUID,
        *,
        idempotency_key: str,
        request_id: UUID | None,
    ) -> AiGenerationAcceptance:
        AiGenerationService._validate_idempotency_key(idempotency_key)
        kindergarten_id = AiGenerationService._kindergarten_id(session)
        scope = "POST /api/v1/jobs/{job_id}/retry"
        fingerprint = canonical_request_fingerprint(
            method="POST",
            route_template="/api/v1/jobs/{job_id}/retry",
            path_params={"job_id": job_id},
            query_params=[],
            body=None,
        )
        try:
            with self._connect() as connection, connection.transaction():
                jobs = JobRepository(connection)
                results = AiGenerationResultRepository(connection)
                jobs.lock_idempotency(
                    kindergarten_id,
                    requested_by=session.user.id,
                    scope=scope,
                    key=idempotency_key,
                )
                replay = AiGenerationService._check_existing(
                    jobs,
                    results,
                    kindergarten_id,
                    requested_by=session.user.id,
                    scope=scope,
                    key=idempotency_key,
                    fingerprint=fingerprint,
                )
                if replay is not None:
                    return replay

                any_job = jobs.get(kindergarten_id, job_id)
                if any_job is None:
                    raise IdentityError(404, "resource.not_found", "任务不存在。")
                source = jobs.get_ai(kindergarten_id, job_id, for_update=True)
                source_result = results.get_by_job(
                    kindergarten_id,
                    job_id,
                    for_update=True,
                )
                if (
                    source is None
                    or source_result is None
                    or not is_explicit_ai_retry_allowed(
                        job_type=source.job_type,
                        status=source.status or "",
                        has_ai_result=True,
                    )
                ):
                    raise self._not_allowed()
                plan_repository = LessonPlanRepository(connection)
                plan = plan_repository.get_plan(
                    kindergarten_id,
                    source.plan_id,
                    for_update=True,
                )
                if plan is None:
                    raise IdentityError(404, "resource.not_found", "教案不存在。")
                LessonPlanService._require_edit(
                    session,
                    plan_repository,
                    kindergarten_id,
                    plan,
                )
                retry_job = jobs.create_ai_executable(
                    kindergarten_id,
                    job_id=uuid7(),
                    parent_job_id=None,
                    retry_of_job_id=source.id,
                    job_type=source.job_type,
                    plan_id=source.plan_id,
                    target_section=source.target_section or source_result.target_section,
                    requested_resource_version=source.requested_resource_version,
                    requested_by=session.user.id,
                    request_id=request_id,
                    trace_id=uuid7(),
                    scope=scope,
                    key=idempotency_key,
                    fingerprint=fingerprint,
                )
                cloned = results.clone_failed_to_pending(
                    kindergarten_id,
                    source_job_id=source.id,
                    target_result_id=uuid7(),
                    target_job_id=retry_job.id,
                    expires_at=datetime.now(UTC) + _PREVIEW_RETENTION,
                )
                if cloned is None:
                    raise self._not_allowed()
                acceptance = AiGenerationAcceptance(
                    retry_job,
                    results=(cloned,),
                )
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc
        AiGenerationService(
            database_url=self.database_url,
            dispatcher=self.dispatcher,
        )._dispatch(kindergarten_id, (acceptance.job.id,))
        return acceptance


__all__ = ["AiRetryService"]
