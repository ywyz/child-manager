"""AI 预览采用、拒绝与有效性校验事务。"""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

import psycopg
from pydantic import ValidationError

from packages.backend.audit.events import append_ai_event
from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.jobs.ai_results import (
    AiGenerationResultRecord,
    AiGenerationResultRepository,
)
from packages.backend.jobs.repository import AiJobRecord, JobRepository
from packages.backend.lesson_plans.ai_fingerprints import (
    JsonValue,
    canonical_json_sha256,
    generation_input_sha256,
    section_sha256,
)
from packages.backend.lesson_plans.ai_schemas import ai_result_model
from packages.backend.lesson_plans.repository import LessonPlanRepository, PlanRecord
from packages.backend.lesson_plans.service import LessonPlanService
from packages.backend.settings.repository import SettingsRepository
from packages.contracts.audit import IdentityAuditEventCode
from packages.contracts.lesson_plans import (
    AiAreaGame,
    AiDailyReflection,
    AiGroupActivity,
    AiMorningActivity,
    AiMorningTalk,
    AiTaskCode,
    DailyReflection,
    GroupActivity,
    GroupActivityAddStepResult,
    GroupActivityStep,
    MorningActivity,
    MorningTalk,
    PlanContentV1,
    apply_ai_area_result,
    validate_group_add_step_result,
)

_TASK_CODES: dict[str, AiTaskCode] = {
    "ai.morning_activity": "morning_activity",
    "ai.morning_talk": "morning_talk",
    "ai.group_activity_split": "group_activity_split",
    "ai.group_activity_add_step": "group_activity_add_step",
    "ai.indoor_area_game": "indoor_area_game",
    "ai.afternoon_outdoor_game": "afternoon_outdoor_game",
    "ai.daily_reflection": "daily_reflection",
}
_TARGET_SECTIONS = {
    "morning_activity": "morning_activity",
    "morning_talk": "morning_talk",
    "group_activity_split": "group_activity",
    "group_activity_add_step": "group_activity",
    "indoor_area_game": "indoor_area_game",
    "afternoon_outdoor_game": "afternoon_outdoor_game",
    "daily_reflection": "daily_reflection",
}


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def preview_is_current(
    *,
    frozen_section: Mapping[str, JsonValue],
    current_section: Mapping[str, JsonValue],
    frozen_server_input: Mapping[str, JsonValue],
    current_server_input: Mapping[str, JsonValue],
    teacher_context: str | None,
) -> bool:
    """比较预览的目标栏目与实际输入，不依赖全局教案版本。"""

    return section_sha256(frozen_section) == section_sha256(
        current_section
    ) and canonical_json_sha256(
        {
            "server_input": dict(frozen_server_input),
            "teacher_context": teacher_context,
        }
    ) == canonical_json_sha256(
        {
            "server_input": dict(current_server_input),
            "teacher_context": teacher_context,
        }
    )


class AiAdoptionService:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    @classmethod
    def from_environment(cls) -> AiAdoptionService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _kindergarten_id(session: SessionUser) -> UUID:
        kindergarten_id = session.user.kindergarten_id
        if kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        return kindergarten_id

    @staticmethod
    def _not_found() -> IdentityError:
        return IdentityError(404, "resource.not_found", "AI 任务不存在。")

    @staticmethod
    def _unavailable() -> IdentityError:
        return IdentityError(409, "ai.preview_unavailable", "AI 预览当前不可操作。")

    @staticmethod
    def _locked_records(
        jobs: JobRepository,
        results: AiGenerationResultRepository,
        kindergarten_id: UUID,
        job_id: UUID,
    ) -> tuple[AiJobRecord, AiGenerationResultRecord]:
        job = jobs.get_ai(kindergarten_id, job_id, for_update=True)
        result = results.get_by_job(kindergarten_id, job_id, for_update=True)
        if (
            job is None
            or result is None
            or job.job_type == "ai.batch"
            or job.plan_id != result.plan_id
            or job.target_section != result.target_section
        ):
            raise AiAdoptionService._not_found()
        return job, result

    @staticmethod
    def _plan_and_permission(
        session: SessionUser,
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan_id: UUID,
    ) -> PlanRecord:
        plan = repository.get_plan(kindergarten_id, plan_id, for_update=True)
        if plan is None:
            raise AiAdoptionService._not_found()
        LessonPlanService._require_edit(session, repository, kindergarten_id, plan)
        return plan

    @staticmethod
    def _current_server_input(
        result: AiGenerationResultRecord,
        *,
        task_code: AiTaskCode,
        plan: PlanRecord,
        settings: SettingsRepository,
        kindergarten_id: UUID,
        current_content: dict[str, Any],
    ) -> tuple[str | None, dict[str, JsonValue]]:
        if result.input_context is None:
            raise AiAdoptionService._unavailable()
        current = cast(dict[str, JsonValue], dict(result.input_context))
        teacher_context_value = current.pop("teacher_context", None)
        teacher_context = str(teacher_context_value) if teacher_context_value is not None else None
        if task_code in {"indoor_area_game", "afternoon_outdoor_game"}:
            area_type = "indoor" if task_code == "indoor_area_game" else "outdoor"
            areas, _total = settings.list_class_areas(
                kindergarten_id,
                plan.class_id,
                area_type,
                page=1,
                page_size=100,
            )
            current[f"{area_type}_areas"] = [area.name for area in areas if area.is_active]
        elif task_code == "group_activity_add_step":
            current["group_activity"] = cast(
                dict[str, JsonValue],
                current_content["group_activity"],
            )
        elif task_code == "daily_reflection":
            current["current_plan"] = cast(
                dict[str, JsonValue],
                {
                    key: current_content[key]
                    for key in (
                        "morning_activity",
                        "morning_talk",
                        "group_activity",
                        "indoor_area_game",
                        "afternoon_outdoor_game",
                    )
                },
            )
        return teacher_context, current

    @staticmethod
    def _merge_output(
        *,
        task_code: AiTaskCode,
        result: AiGenerationResultRecord,
        content: PlanContentV1,
    ) -> PlanContentV1:
        if result.output_content is None or result.output_sha256 is None:
            raise AiAdoptionService._unavailable()
        if (
            canonical_json_sha256(cast(dict[str, JsonValue], result.output_content))
            != result.output_sha256
        ):
            raise AiAdoptionService._unavailable()
        try:
            parsed = ai_result_model(result.result_schema_code).model_validate(
                result.output_content
            )
            if task_code == "morning_activity":
                assert isinstance(parsed, AiMorningActivity)
                content.morning_activity = MorningActivity.model_validate(
                    parsed.model_dump(mode="json")
                )
            elif task_code == "morning_talk":
                assert isinstance(parsed, AiMorningTalk)
                content.morning_talk = MorningTalk.model_validate(parsed.model_dump(mode="json"))
            elif task_code in {"indoor_area_game", "afternoon_outdoor_game"}:
                assert isinstance(parsed, AiAreaGame)
                assert result.input_context is not None
                area_key = "indoor_areas" if task_code == "indoor_area_game" else "outdoor_areas"
                input_areas = cast(list[str], result.input_context[area_key])
                area = apply_ai_area_result(parsed, input_areas=input_areas)
                if task_code == "indoor_area_game":
                    content.indoor_area_game = area
                else:
                    content.afternoon_outdoor_game = area
            elif task_code == "daily_reflection":
                assert isinstance(parsed, AiDailyReflection)
                content.daily_reflection = DailyReflection.model_validate(
                    parsed.model_dump(mode="json")
                )
            elif task_code == "group_activity_split":
                assert isinstance(parsed, AiGroupActivity)
                content.group_activity = GroupActivity(
                    theme=parsed.theme,
                    objectives=list(parsed.objectives),
                    preparation=list(parsed.preparation),
                    focus=parsed.focus,
                    difficulty=parsed.difficulty,
                    process=[
                        GroupActivityStep(
                            heading=step.heading,
                            lines=list(step.lines),
                            is_ai_added=False,
                        )
                        for step in parsed.process
                    ],
                )
            else:
                assert isinstance(parsed, GroupActivityAddStepResult)
                validate_group_add_step_result(
                    parsed,
                    process_length=len(content.group_activity.process),
                )
                process = list(content.group_activity.process)
                process.insert(
                    parsed.suggested_insert_index,
                    GroupActivityStep(
                        heading=parsed.step.heading,
                        lines=list(parsed.step.lines),
                        is_ai_added=True,
                    ),
                )
                content.group_activity.process = process
        except (AssertionError, KeyError, LookupError, ValidationError, ValueError) as exc:
            raise AiAdoptionService._unavailable() from exc
        return content

    @staticmethod
    def _task_code(job: AiJobRecord, result: AiGenerationResultRecord) -> AiTaskCode:
        task_code = _TASK_CODES.get(job.job_type)
        if task_code is None or _TARGET_SECTIONS[task_code] != result.target_section:
            raise AiAdoptionService._unavailable()
        return task_code

    def adopt(
        self,
        session: SessionUser,
        job_id: UUID,
        *,
        expected_version: int,
    ) -> PlanRecord:
        kindergarten_id = self._kindergarten_id(session)
        now = datetime.now(UTC)
        with self._connect() as connection, connection.transaction():
            jobs = JobRepository(connection)
            results = AiGenerationResultRepository(connection)
            job, result = self._locked_records(
                jobs,
                results,
                kindergarten_id,
                job_id,
            )
            plans = LessonPlanRepository(connection)
            plan = self._plan_and_permission(
                session,
                plans,
                kindergarten_id,
                result.plan_id,
            )
            if job.status == "adopted" and result.adopted_at is not None:
                return plan
            if (
                job.status != "awaiting_confirmation"
                or result.adopted_at is not None
                or result.rejected_at is not None
                or result.content_cleared_at is not None
                or result.expires_at <= now
            ):
                raise self._unavailable()
            if plan.version != expected_version:
                raise IdentityError(
                    409,
                    "lesson_plan.version_conflict",
                    "教案已被修改，请刷新后重试。",
                )
            try:
                content = PlanContentV1.model_validate(plan.content)
            except ValidationError as exc:
                raise IdentityError(
                    409,
                    "plan.schema_read_only",
                    "教案内容版本暂不支持编辑。",
                ) from exc
            task_code = self._task_code(job, result)
            current_content = content.model_dump(mode="json")
            current_section = cast(
                dict[str, JsonValue],
                current_content[result.target_section],
            )
            teacher_context, current_server_input = self._current_server_input(
                result,
                task_code=task_code,
                plan=plan,
                settings=SettingsRepository(connection),
                kindergarten_id=kindergarten_id,
                current_content=current_content,
            )
            if (
                section_sha256(current_section) != result.target_section_baseline_sha256
                or generation_input_sha256(
                    task_code=task_code,
                    teacher_context=teacher_context,
                    server_input=current_server_input,
                )
                != result.input_sha256
            ):
                raise IdentityError(
                    409,
                    "ai.preview_stale",
                    "教案相关内容已变化，请重新生成预览。",
                )
            merged = self._merge_output(
                task_code=task_code,
                result=result,
                content=content,
            )
            updated = plans.update_content(
                kindergarten_id,
                plan.id,
                expected_version=expected_version,
                content=merged.model_dump(mode="json"),
                actor_id=session.user.id,
            )
            if updated is None:
                raise IdentityError(
                    409,
                    "lesson_plan.version_conflict",
                    "教案已被修改，请刷新后重试。",
                )
            LessonPlanService._snapshot(
                plans,
                kindergarten_id,
                updated,
                reason="ai_adopted",
                actor_id=session.user.id,
            )
            if not results.mark_adopted(
                kindergarten_id,
                job_id,
                actor_id=session.user.id,
                adopted_at=now,
            ) or not jobs.mark_ai_preview_decided(
                kindergarten_id,
                job_id,
                status="adopted",
                decided_at=now,
            ):
                raise self._unavailable()
            append_ai_event(
                connection,
                kindergarten_id,
                event_code=IdentityAuditEventCode.AI_PREVIEW_ADOPTED,
                job_id=job_id,
                actor_user_id=session.user.id,
                actor_role_codes=list(session.role_codes),
                outcome="success",
                request_id=getattr(session, "request_id", None),
                trace_id=job.trace_id,
                attempt_count=job.attempt_count,
                target_section=job.target_section,
            )
            return updated

    def reject(self, session: SessionUser, job_id: UUID) -> AiJobRecord:
        kindergarten_id = self._kindergarten_id(session)
        now = datetime.now(UTC)
        with self._connect() as connection, connection.transaction():
            jobs = JobRepository(connection)
            results = AiGenerationResultRepository(connection)
            job, result = self._locked_records(
                jobs,
                results,
                kindergarten_id,
                job_id,
            )
            self._plan_and_permission(
                session,
                LessonPlanRepository(connection),
                kindergarten_id,
                result.plan_id,
            )
            if job.status == "rejected" and result.rejected_at is not None:
                return job
            if (
                job.status != "awaiting_confirmation"
                or result.adopted_at is not None
                or result.rejected_at is not None
                or result.content_cleared_at is not None
                or result.expires_at <= now
            ):
                raise self._unavailable()
            if not results.mark_rejected(
                kindergarten_id,
                job_id,
                actor_id=session.user.id,
                rejected_at=now,
            ) or not jobs.mark_ai_preview_decided(
                kindergarten_id,
                job_id,
                status="rejected",
                decided_at=now,
            ):
                raise self._unavailable()
            append_ai_event(
                connection,
                kindergarten_id,
                event_code=IdentityAuditEventCode.AI_PREVIEW_REJECTED,
                job_id=job_id,
                actor_user_id=session.user.id,
                actor_role_codes=list(session.role_codes),
                outcome="success",
                request_id=getattr(session, "request_id", None),
                trace_id=job.trace_id,
                attempt_count=job.attempt_count,
                target_section=job.target_section,
            )
            decided = jobs.get_ai(kindergarten_id, job_id)
            assert decided is not None
            return decided

    def expire_due_results(self, *, now: datetime, limit: int) -> int:
        if limit <= 0:
            return 0
        with self._connect() as connection, connection.transaction():
            kindergarten_rows = connection.execute(
                """SELECT DISTINCT kindergarten_id
                FROM background_jobs
                WHERE job_type LIKE 'ai.%%'
                  AND execution_status='awaiting_confirmation'
                ORDER BY kindergarten_id"""
            ).fetchall()
            repository = AiGenerationResultRepository(connection)
            expired = 0
            for row in kindergarten_rows:
                if expired >= limit:
                    break
                expired += repository.expire_due_previews(
                    UUID(str(row[0])),
                    now=now,
                    limit=limit - expired,
                )
            return expired


__all__ = ["AiAdoptionService", "preview_is_current"]
