"""后台任务权威状态、预览与教案任务历史查询用例。"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

import psycopg

from packages.backend.identity.service import IdentityError, IdentityService, SessionUser
from packages.backend.jobs.aggregation import BatchJobAggregationRepository
from packages.backend.jobs.ai_results import AiGenerationResultRepository
from packages.backend.jobs.repository import AiJobRecord, JobRecord, JobRepository
from packages.backend.lesson_plans.ai_schemas import ai_result_model
from packages.backend.lesson_plans.repository import LessonPlanRepository
from packages.backend.lesson_plans.service import LessonPlanService
from packages.contracts.jobs import Job, JobPreview


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _project_regular_job(record: JobRecord) -> Job:
    return Job.model_validate(
        {
            "id": record.id,
            "job_type": record.job_type,
            "status": record.status,
            "attempt_count": record.attempt_count,
            "max_attempts": record.max_attempts,
            "trace_id": record.trace_id,
            "created_at": record.created_at,
            "queued_at": record.queued_at,
            "started_at": record.started_at,
            "finished_at": record.finished_at,
            "error_code": record.error_code,
            "error_message": record.error_summary,
        }
    )


def _project_ai_job(record: AiJobRecord) -> Job:
    if record.status is None or record.attempt_count is None or record.max_attempts is None:
        raise ValueError("batch 必须由聚合 Repository 投影")
    return Job.model_validate(
        {
            "id": record.id,
            "job_type": record.job_type,
            "status": record.status,
            "parent_job_id": record.parent_job_id,
            "retry_of_job_id": record.retry_of_job_id,
            "plan_id": record.plan_id,
            "target_section": record.target_section,
            "requested_resource_version": record.requested_resource_version,
            "attempt_count": record.attempt_count,
            "max_attempts": record.max_attempts,
            "trace_id": record.trace_id,
            "created_at": record.created_at,
            "queued_at": record.queued_at,
            "started_at": record.started_at,
            "finished_at": record.finished_at,
            "error_code": record.error_code,
            "error_message": record.error_summary,
        }
    )


class JobQueryService:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    @classmethod
    def from_environment(cls) -> JobQueryService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url)

    @staticmethod
    def _kindergarten_id(session: SessionUser) -> UUID:
        kindergarten_id = session.user.kindergarten_id
        if kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        return kindergarten_id

    @staticmethod
    def _authorize_plan(
        session: SessionUser,
        plans: LessonPlanRepository,
        kindergarten_id: UUID,
        plan_id: UUID,
    ) -> None:
        plan = plans.get_plan(kindergarten_id, plan_id)
        if plan is None:
            raise IdentityError(404, "resource.not_found", "教案不存在。")
        LessonPlanService._require_view(session, plans, kindergarten_id, plan)

    @staticmethod
    def _project_ai(
        connection: psycopg.Connection[tuple[object, ...]],
        kindergarten_id: UUID,
        record: AiJobRecord,
    ) -> Job:
        if record.job_type == "ai.batch":
            projected = BatchJobAggregationRepository(connection).get(
                kindergarten_id,
                record.id,
            )
            if projected is None:
                raise IdentityError(404, "resource.not_found", "任务不存在。")
            return projected
        return _project_ai_job(record)

    def get(self, session: SessionUser, job_id: UUID) -> Job:
        kindergarten_id = self._kindergarten_id(session)
        with psycopg.connect(_native_url(self.database_url)) as connection:
            jobs = JobRepository(connection)
            ai_record = jobs.get_ai(kindergarten_id, job_id)
            if ai_record is not None:
                self._authorize_plan(
                    session,
                    LessonPlanRepository(connection),
                    kindergarten_id,
                    ai_record.plan_id,
                )
                return self._project_ai(connection, kindergarten_id, ai_record)
            record = jobs.get(kindergarten_id, job_id)
            if record is None:
                raise IdentityError(404, "resource.not_found", "任务不存在。")
            IdentityService.require_admin(session)
            return _project_regular_job(record)

    def list_plan(
        self,
        session: SessionUser,
        plan_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Job], int]:
        kindergarten_id = self._kindergarten_id(session)
        with psycopg.connect(_native_url(self.database_url)) as connection:
            plans = LessonPlanRepository(connection)
            self._authorize_plan(session, plans, kindergarten_id, plan_id)
            records, total = JobRepository(connection).list_ai_roots_for_plan(
                kindergarten_id,
                plan_id,
                page=page,
                page_size=page_size,
            )
            return (
                [self._project_ai(connection, kindergarten_id, record) for record in records],
                total,
            )

    def preview(self, session: SessionUser, job_id: UUID) -> JobPreview:
        kindergarten_id = self._kindergarten_id(session)
        now = datetime.now(UTC)
        with psycopg.connect(_native_url(self.database_url)) as connection:
            jobs = JobRepository(connection)
            job = jobs.get_ai(kindergarten_id, job_id)
            result = AiGenerationResultRepository(connection).get_by_job(
                kindergarten_id,
                job_id,
            )
            if job is None or result is None or job.job_type == "ai.batch":
                raise IdentityError(404, "resource.not_found", "AI 预览不存在。")
            self._authorize_plan(
                session,
                LessonPlanRepository(connection),
                kindergarten_id,
                result.plan_id,
            )
            if (
                job.status != "awaiting_confirmation"
                or result.output_content is None
                or result.content_cleared_at is not None
                or result.adopted_at is not None
                or result.rejected_at is not None
                or result.expires_at <= now
            ):
                raise IdentityError(
                    409,
                    "ai.preview_unavailable",
                    "AI 预览当前不可查看。",
                )
            output = ai_result_model(result.result_schema_code).model_validate(
                result.output_content
            )
            return JobPreview(
                job_id=job.id,
                target_section=result.target_section,
                result_schema_code=result.result_schema_code,
                result_schema_version=result.result_schema_version,
                output_content=cast(dict[str, object], output.model_dump(mode="json")),
                expires_at=result.expires_at,
            )


__all__ = ["JobQueryService"]
