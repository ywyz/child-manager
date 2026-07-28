"""非反思栏目 AI 任务的权威受理事务。"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, cast
from uuid import UUID, uuid7

import psycopg
from pydantic import ValidationError

from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.jobs.ai_results import (
    AiGenerationResultRecord,
    AiGenerationResultRepository,
)
from packages.backend.jobs.dispatcher import RedisJobDispatcher
from packages.backend.jobs.repository import AiJobRecord, JobRepository
from packages.backend.lesson_plans.ai_fingerprints import (
    JsonValue,
    generation_input_sha256,
    section_sha256,
)
from packages.backend.lesson_plans.ai_schemas import ai_result_model
from packages.backend.lesson_plans.repository import LessonPlanRepository, PlanRecord
from packages.backend.lesson_plans.service import LessonPlanService
from packages.backend.prompts.catalog import validate_prompt_variables
from packages.backend.prompts.repository import (
    PromptDefinitionRecord,
    PromptRepository,
    PromptVersionRecord,
)
from packages.backend.settings.repository import (
    AiModelProfileRecord,
    AiModelProfileRepository,
    AreaRecord,
    SettingsRepository,
)
from packages.contracts.common import canonical_request_fingerprint
from packages.contracts.lesson_plans import (
    AiBatchRequest,
    AiGenerationRequest,
    AiTaskCode,
    PlanContentV1,
)

logger = logging.getLogger(__name__)

_PREVIEW_RETENTION = timedelta(days=30)
_WEEKDAYS = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")


class Dispatcher(Protocol):
    def dispatch(self, job_id: UUID) -> None: ...


@dataclass(frozen=True, slots=True)
class AiGenerationAcceptance:
    job: AiJobRecord
    children: tuple[AiJobRecord, ...] = ()
    results: tuple[AiGenerationResultRecord, ...] = ()
    replayed: bool = False


@dataclass(frozen=True, slots=True)
class _TaskSpec:
    task_code: AiTaskCode
    job_type: str
    target_section: str
    prompt_code: str
    area_type: str | None = None


@dataclass(frozen=True, slots=True)
class _FrozenTask:
    spec: _TaskSpec
    input_context: dict[str, Any]
    input_sha256: str
    target_section_baseline_sha256: str
    profile: AiModelProfileRecord
    definition: PromptDefinitionRecord
    version: PromptVersionRecord


_BATCH_TASKS = (
    _TaskSpec(
        "morning_activity",
        "ai.morning_activity",
        "morning_activity",
        "daily_activity_plan.morning_activity",
    ),
    _TaskSpec(
        "morning_talk",
        "ai.morning_talk",
        "morning_talk",
        "daily_activity_plan.morning_talk",
    ),
    _TaskSpec(
        "indoor_area_game",
        "ai.indoor_area_game",
        "indoor_area_game",
        "daily_activity_plan.indoor_area_game",
        "indoor",
    ),
    _TaskSpec(
        "afternoon_outdoor_game",
        "ai.afternoon_outdoor_game",
        "afternoon_outdoor_game",
        "daily_activity_plan.afternoon_outdoor_game",
        "outdoor",
    ),
)
_TASKS = {spec.task_code: spec for spec in _BATCH_TASKS}


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def dispatch_after_commit(
    dispatcher: Dispatcher | None,
    job_ids: Iterable[UUID],
) -> tuple[UUID, ...]:
    """尽力投递已提交任务；单个 Redis 故障不得回滚或阻断其余子任务。"""

    if dispatcher is None:
        return ()
    dispatched: list[UUID] = []
    for job_id in job_ids:
        try:
            dispatcher.dispatch(job_id)
        except Exception:
            logger.error("AI 生成任务投递失败", extra={"job_id": str(job_id)})
        else:
            dispatched.append(job_id)
    return tuple(dispatched)


class AiGenerationService:
    def __init__(
        self,
        *,
        database_url: str,
        dispatcher: Dispatcher | None = None,
    ) -> None:
        self.database_url = database_url
        self.dispatcher = dispatcher

    @classmethod
    def from_environment(cls) -> AiGenerationService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        redis_url = os.environ.get("CHILD_MANAGER_REDIS_URL")
        dispatcher = (
            RedisJobDispatcher.from_url(redis_url, actor_name="ai_generation")
            if redis_url
            else None
        )
        return cls(database_url=database_url, dispatcher=dispatcher)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _kindergarten_id(session: SessionUser) -> UUID:
        kindergarten_id = session.user.kindergarten_id
        if kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        return kindergarten_id

    @staticmethod
    def _validate_idempotency_key(value: str) -> None:
        if not value or len(value) > 200:
            raise IdentityError(
                422,
                "request.invalid_idempotency_key",
                "Idempotency-Key 长度必须为 1 到 200 个字符。",
            )

    @staticmethod
    def _plan(
        session: SessionUser,
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan_id: UUID,
        expected_version: int,
    ) -> PlanRecord:
        plan = repository.get_plan(kindergarten_id, plan_id, for_update=True)
        if plan is None:
            raise IdentityError(404, "resource.not_found", "教案不存在。")
        LessonPlanService._require_edit(session, repository, kindergarten_id, plan)
        if plan.version != expected_version:
            raise IdentityError(
                409,
                "lesson_plan.version_conflict",
                "教案已被修改，请刷新后重试。",
            )
        return plan

    @staticmethod
    def _active_areas(
        settings: SettingsRepository,
        kindergarten_id: UUID,
        plan: PlanRecord,
        area_type: str,
    ) -> list[AreaRecord]:
        areas, _total = settings.list_class_areas(
            kindergarten_id,
            plan.class_id,
            area_type,
            page=1,
            page_size=100,
        )
        return [area for area in areas if area.is_active]

    @staticmethod
    def _profile(
        profiles: AiModelProfileRepository,
        kindergarten_id: UUID,
        definition: PromptDefinitionRecord,
    ) -> AiModelProfileRecord:
        profile = (
            profiles.get(kindergarten_id, definition.model_profile_id)
            if definition.model_profile_id is not None
            else profiles.get_default(kindergarten_id)
        )
        required = set(definition.required_capabilities)
        if (
            profile is None
            or not profile.is_active
            or profile.api_key_ciphertext is None
            or profile.api_key_nonce is None
            or profile.api_key_key_id is None
            or profile.api_key_encryption_version is None
            or profile.risk_confirmed_by is None
            or profile.risk_confirmed_at is None
            or not required <= set(profile.capability_codes)
        ):
            raise IdentityError(
                503,
                "configuration.unavailable",
                "可用的 AI 模型配置不存在或不完整。",
            )
        return profile

    @staticmethod
    def _frozen_task(
        *,
        spec: _TaskSpec,
        teacher_context: str,
        plan: PlanRecord,
        content: dict[str, Any],
        kindergarten_id: UUID,
        prompts: PromptRepository,
        profiles: AiModelProfileRepository,
        settings: SettingsRepository,
    ) -> _FrozenTask | None:
        variables: dict[str, Any] = {
            "plan_date": plan.plan_date,
            "weekday_text": _WEEKDAYS[plan.plan_date.weekday()],
            "teaching_week_text": plan.teaching_week_text,
            "season": plan.season_code,
            "class_name": plan.class_name_snapshot,
            "age_group_name": plan.age_group_name_snapshot,
            "teacher_context": teacher_context,
        }
        if spec.area_type is not None:
            areas = AiGenerationService._active_areas(
                settings,
                kindergarten_id,
                plan,
                spec.area_type,
            )
            if not areas:
                return None
            variables[f"{spec.area_type}_areas"] = [area.name for area in areas]

        definition = prompts.get_definition(
            kindergarten_id,
            spec.prompt_code,
            for_update=True,
        )
        if (
            definition is None
            or not definition.is_active
            or definition.effective_version_id is None
        ):
            raise IdentityError(
                503,
                "configuration.unavailable",
                "可用的提示词配置不存在或不完整。",
            )
        version = prompts.get_version(
            kindergarten_id,
            spec.prompt_code,
            definition.effective_version_id,
        )
        if version is None or version.lifecycle_state != "published":
            raise IdentityError(
                503,
                "configuration.unavailable",
                "可用的提示词版本不存在。",
            )
        profile = AiGenerationService._profile(profiles, kindergarten_id, definition)
        try:
            input_context = validate_prompt_variables(spec.prompt_code, variables)
            ai_result_model(definition.result_schema_code)
        except (LookupError, ValidationError) as exc:
            raise IdentityError(
                422,
                "ai.invalid_input",
                "当前教案无法形成有效的 AI 生成输入。",
            ) from exc
        server_input = dict(input_context)
        frozen_teacher_context = str(server_input.pop("teacher_context"))
        target_section = content[spec.target_section]
        return _FrozenTask(
            spec=spec,
            input_context=input_context,
            input_sha256=generation_input_sha256(
                task_code=spec.task_code,
                teacher_context=frozen_teacher_context,
                server_input=cast(Mapping[str, JsonValue], server_input),
            ),
            target_section_baseline_sha256=section_sha256(target_section),
            profile=profile,
            definition=definition,
            version=version,
        )

    @staticmethod
    def _content(plan: PlanRecord) -> dict[str, Any]:
        try:
            return PlanContentV1.model_validate(plan.content).model_dump(mode="json")
        except ValidationError as exc:
            raise IdentityError(
                409,
                "plan.schema_read_only",
                "教案内容版本暂不支持 AI 生成。",
            ) from exc

    @staticmethod
    def _pending_result(
        repository: AiGenerationResultRepository,
        kindergarten_id: UUID,
        *,
        job: AiJobRecord,
        frozen: _FrozenTask,
        expires_at: datetime,
    ) -> AiGenerationResultRecord:
        return repository.create_pending(
            kindergarten_id,
            result_id=uuid7(),
            job_id=job.id,
            plan_id=job.plan_id,
            target_section=frozen.spec.target_section,
            requested_resource_version=job.requested_resource_version,
            target_section_baseline_sha256=frozen.target_section_baseline_sha256,
            input_context=frozen.input_context,
            input_sha256=frozen.input_sha256,
            model_profile_id=frozen.profile.id,
            model_name_snapshot=frozen.profile.model_name,
            prompt_definition_id=frozen.definition.id,
            prompt_version_id=frozen.version.id,
            prompt_content_sha256=frozen.version.content_sha256,
            result_schema_code=frozen.definition.result_schema_code,
            result_schema_version=frozen.definition.result_schema_version,
            expires_at=expires_at,
        )

    @staticmethod
    def _replay(
        jobs: JobRepository,
        results: AiGenerationResultRepository,
        kindergarten_id: UUID,
        job: AiJobRecord,
    ) -> AiGenerationAcceptance:
        if job.job_type == "ai.batch":
            children = tuple(jobs.list_ai_children(kindergarten_id, job.id))
            frozen_results = tuple(
                result
                for child in children
                if (result := results.get_by_job(kindergarten_id, child.id)) is not None
            )
            return AiGenerationAcceptance(
                job,
                children,
                frozen_results,
                replayed=True,
            )
        result = results.get_by_job(kindergarten_id, job.id)
        return AiGenerationAcceptance(
            job,
            results=(result,) if result is not None else (),
            replayed=True,
        )

    @staticmethod
    def _check_existing(
        jobs: JobRepository,
        results: AiGenerationResultRepository,
        kindergarten_id: UUID,
        *,
        requested_by: UUID,
        scope: str,
        key: str,
        fingerprint: str,
    ) -> AiGenerationAcceptance | None:
        existing = jobs.find_idempotent_ai(
            kindergarten_id,
            requested_by=requested_by,
            scope=scope,
            key=key,
        )
        if existing is None:
            return None
        if existing.request_fingerprint_sha256 != fingerprint:
            raise IdentityError(
                409,
                "job.idempotency_conflict",
                "幂等键已用于不同请求。",
            )
        return AiGenerationService._replay(
            jobs,
            results,
            kindergarten_id,
            existing,
        )

    def _dispatch(
        self,
        kindergarten_id: UUID,
        job_ids: tuple[UUID, ...],
    ) -> None:
        try:
            dispatched = dispatch_after_commit(self.dispatcher, job_ids)
        except Exception:
            logger.error("AI 生成任务提交后投递失败")
            return
        if not dispatched:
            return
        try:
            with self._connect() as connection, connection.transaction():
                repository = JobRepository(connection)
                for job_id in dispatched:
                    repository.mark_queued(kindergarten_id, job_id)
        except Exception:
            logger.error("AI 生成任务 queued 状态回写失败")

    def create_single(
        self,
        session: SessionUser,
        plan_id: UUID,
        body: AiGenerationRequest,
        *,
        idempotency_key: str,
        request_id: UUID | None,
    ) -> AiGenerationAcceptance:
        self._validate_idempotency_key(idempotency_key)
        kindergarten_id = self._kindergarten_id(session)
        spec = _TASKS.get(body.task_code)
        if spec is None:
            raise IdentityError(
                422,
                "ai.task_unavailable",
                "当前里程碑不支持该 AI 生成任务。",
            )
        scope = "POST /api/v1/plans/{plan_id}/ai/generations"
        fingerprint = canonical_request_fingerprint(
            method="POST",
            route_template="/api/v1/plans/{plan_id}/ai/generations",
            path_params={"plan_id": plan_id},
            query_params=[],
            body=body.model_dump(mode="json"),
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
                replay = self._check_existing(
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
                plan_repository = LessonPlanRepository(connection)
                plan = self._plan(
                    session,
                    plan_repository,
                    kindergarten_id,
                    plan_id,
                    body.expected_version,
                )
                content = self._content(plan)
                prompts = PromptRepository(connection)
                prompts.ensure_defaults(kindergarten_id)
                teacher_context = cast(str, body.teacher_context)
                frozen = self._frozen_task(
                    spec=spec,
                    teacher_context=teacher_context,
                    plan=plan,
                    content=content,
                    kindergarten_id=kindergarten_id,
                    prompts=prompts,
                    profiles=AiModelProfileRepository(connection),
                    settings=SettingsRepository(connection),
                )
                if frozen is None:
                    raise IdentityError(
                        422,
                        "ai.area_required",
                        "请先为班级配置至少一个已启用的对应区域。",
                    )
                trace_id = uuid7()
                job = jobs.create_ai_executable(
                    kindergarten_id,
                    job_id=uuid7(),
                    parent_job_id=None,
                    job_type=spec.job_type,
                    plan_id=plan.id,
                    target_section=spec.target_section,
                    requested_resource_version=plan.version,
                    requested_by=session.user.id,
                    request_id=request_id,
                    trace_id=trace_id,
                    scope=scope,
                    key=idempotency_key,
                    fingerprint=fingerprint,
                )
                result = self._pending_result(
                    results,
                    kindergarten_id,
                    job=job,
                    frozen=frozen,
                    expires_at=datetime.now(UTC) + _PREVIEW_RETENTION,
                )
                acceptance = AiGenerationAcceptance(job, results=(result,))
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc
        self._dispatch(kindergarten_id, (acceptance.job.id,))
        return acceptance

    def create_batch(
        self,
        session: SessionUser,
        plan_id: UUID,
        body: AiBatchRequest,
        *,
        idempotency_key: str,
        request_id: UUID | None,
    ) -> AiGenerationAcceptance:
        self._validate_idempotency_key(idempotency_key)
        kindergarten_id = self._kindergarten_id(session)
        scope = "POST /api/v1/plans/{plan_id}/ai/batch"
        fingerprint = canonical_request_fingerprint(
            method="POST",
            route_template="/api/v1/plans/{plan_id}/ai/batch",
            path_params={"plan_id": plan_id},
            query_params=[],
            body=body.model_dump(mode="json"),
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
                replay = self._check_existing(
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
                plan = self._plan(
                    session,
                    LessonPlanRepository(connection),
                    kindergarten_id,
                    plan_id,
                    body.expected_version,
                )
                content = self._content(plan)
                prompts = PromptRepository(connection)
                prompts.ensure_defaults(kindergarten_id)
                profiles = AiModelProfileRepository(connection)
                settings = SettingsRepository(connection)
                teacher_context = cast(str, body.teacher_context)
                frozen_tasks = tuple(
                    self._frozen_task(
                        spec=spec,
                        teacher_context=teacher_context,
                        plan=plan,
                        content=content,
                        kindergarten_id=kindergarten_id,
                        prompts=prompts,
                        profiles=profiles,
                        settings=settings,
                    )
                    for spec in _BATCH_TASKS
                )
                trace_id = uuid7()
                parent = jobs.create_ai_batch(
                    kindergarten_id,
                    job_id=uuid7(),
                    plan_id=plan.id,
                    requested_resource_version=plan.version,
                    requested_by=session.user.id,
                    request_id=request_id,
                    trace_id=trace_id,
                    scope=scope,
                    key=idempotency_key,
                    fingerprint=fingerprint,
                )
                children: list[AiJobRecord] = []
                pending_results: list[AiGenerationResultRecord] = []
                dispatch_ids: list[UUID] = []
                expires_at = datetime.now(UTC) + _PREVIEW_RETENTION
                for spec, frozen in zip(_BATCH_TASKS, frozen_tasks, strict=True):
                    area_missing = frozen is None
                    child = jobs.create_ai_executable(
                        kindergarten_id,
                        job_id=uuid7(),
                        parent_job_id=parent.id,
                        job_type=spec.job_type,
                        plan_id=plan.id,
                        target_section=spec.target_section,
                        requested_resource_version=plan.version,
                        requested_by=session.user.id,
                        request_id=request_id,
                        trace_id=trace_id,
                        scope=None,
                        key=None,
                        fingerprint=None,
                        status="failed" if area_missing else "pending_dispatch",
                        finished_at=datetime.now(UTC) if area_missing else None,
                        error_code="ai.area_required" if area_missing else None,
                        error_summary=("班级缺少已启用的对应区域。" if area_missing else None),
                    )
                    children.append(child)
                    if frozen is not None:
                        pending_results.append(
                            self._pending_result(
                                results,
                                kindergarten_id,
                                job=child,
                                frozen=frozen,
                                expires_at=expires_at,
                            )
                        )
                        dispatch_ids.append(child.id)
                acceptance = AiGenerationAcceptance(
                    parent,
                    tuple(children),
                    tuple(pending_results),
                )
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc
        self._dispatch(kindergarten_id, tuple(dispatch_ids))
        return acceptance


__all__ = [
    "AiGenerationAcceptance",
    "AiGenerationService",
    "dispatch_after_commit",
]
