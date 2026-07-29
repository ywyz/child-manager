"""显式一日活动反思的预保存与 AI 任务受理事务。"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID, uuid7

import psycopg

from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.jobs.ai_results import AiGenerationResultRepository
from packages.backend.jobs.repository import JobRepository
from packages.backend.lesson_plans.ai_fingerprints import (
    JsonValue,
    generation_input_sha256,
    section_sha256,
)
from packages.backend.lesson_plans.ai_generation import (
    AiGenerationAcceptance,
    AiGenerationService,
    Dispatcher,
)
from packages.backend.lesson_plans.repository import LessonPlanRepository
from packages.backend.lesson_plans.schemas import content_completeness
from packages.backend.prompts.catalog import validate_prompt_variables
from packages.backend.prompts.repository import PromptRepository
from packages.backend.settings.repository import AiModelProfileRepository
from packages.contracts.common import canonical_request_fingerprint
from packages.contracts.lesson_plans import AiGenerationRequest

_PROMPT_CODE = "daily_activity_plan.daily_reflection"
_PREVIEW_RETENTION = timedelta(days=30)
_UPSTREAM_SECTIONS = (
    "morning_activity",
    "morning_talk",
    "group_activity",
    "indoor_area_game",
    "afternoon_outdoor_game",
)


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


class ReflectionGenerationService:
    def __init__(
        self,
        database_url: str,
        *,
        dispatcher: Dispatcher | None = None,
    ) -> None:
        self.database_url = database_url
        self.dispatcher = dispatcher

    @classmethod
    def from_environment(cls) -> ReflectionGenerationService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    def create(
        self,
        session: SessionUser,
        plan_id: UUID,
        body: AiGenerationRequest,
        *,
        idempotency_key: str,
        request_id: UUID | None,
    ) -> AiGenerationAcceptance:
        AiGenerationService._validate_idempotency_key(idempotency_key)
        if body.task_code != "daily_reflection" or body.content is None:
            raise IdentityError(
                422,
                "ai.task_unavailable",
                "该服务只受理一日活动反思生成。",
            )
        kindergarten_id = AiGenerationService._kindergarten_id(session)
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

                plans = LessonPlanRepository(connection)
                current = AiGenerationService._plan(
                    session,
                    plans,
                    kindergarten_id,
                    plan_id,
                    body.expected_version,
                )
                completeness = content_completeness(body.content)
                if not all(completeness[section] for section in _UPSTREAM_SECTIONS):
                    raise IdentityError(
                        409,
                        "ai.reflection_incomplete",
                        "请先完整填写前五个栏目，再生成一日活动反思。",
                    )
                updated = plans.update_content(
                    kindergarten_id,
                    plan_id,
                    expected_version=current.version,
                    content=body.content.model_dump(mode="json"),
                    actor_id=session.user.id,
                )
                if updated is None:
                    raise IdentityError(
                        409,
                        "lesson_plan.version_conflict",
                        "教案已被修改，请刷新后重试。",
                    )

                content = body.content.model_dump(mode="json")
                input_context = validate_prompt_variables(
                    _PROMPT_CODE,
                    {
                        "plan_date": updated.plan_date,
                        "class_name": updated.class_name_snapshot,
                        "age_group_name": updated.age_group_name_snapshot,
                        "current_plan": {
                            section: content[section] for section in _UPSTREAM_SECTIONS
                        },
                    },
                )
                prompts = PromptRepository(connection)
                prompts.ensure_defaults(kindergarten_id)
                definition = prompts.get_definition(
                    kindergarten_id,
                    _PROMPT_CODE,
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
                    _PROMPT_CODE,
                    definition.effective_version_id,
                )
                if version is None or version.lifecycle_state != "published":
                    raise IdentityError(
                        503,
                        "configuration.unavailable",
                        "可用的提示词版本不存在。",
                    )
                profile = AiGenerationService._profile(
                    AiModelProfileRepository(connection),
                    kindergarten_id,
                    definition,
                )
                trace_id = uuid7()
                job = jobs.create_ai_executable(
                    kindergarten_id,
                    job_id=uuid7(),
                    parent_job_id=None,
                    job_type="ai.daily_reflection",
                    plan_id=plan_id,
                    target_section="daily_reflection",
                    requested_resource_version=updated.version,
                    requested_by=session.user.id,
                    request_id=request_id,
                    trace_id=trace_id,
                    scope=scope,
                    key=idempotency_key,
                    fingerprint=fingerprint,
                )
                result = results.create_pending(
                    kindergarten_id,
                    result_id=uuid7(),
                    job_id=job.id,
                    plan_id=plan_id,
                    target_section="daily_reflection",
                    requested_resource_version=updated.version,
                    target_section_baseline_sha256=section_sha256(
                        cast(dict[str, JsonValue], content["daily_reflection"])
                    ),
                    input_context=input_context,
                    input_sha256=generation_input_sha256(
                        task_code="daily_reflection",
                        teacher_context=None,
                        server_input=cast(dict[str, JsonValue], input_context),
                    ),
                    model_profile_id=profile.id,
                    model_name_snapshot=profile.model_name,
                    prompt_definition_id=definition.id,
                    prompt_version_id=version.id,
                    prompt_content_sha256=version.content_sha256,
                    result_schema_code=definition.result_schema_code,
                    result_schema_version=definition.result_schema_version,
                    expires_at=datetime.now(UTC) + _PREVIEW_RETENTION,
                )
                acceptance = AiGenerationAcceptance(job, results=(result,))
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc

        AiGenerationService(
            database_url=self.database_url,
            dispatcher=self.dispatcher,
        )._dispatch(kindergarten_id, (acceptance.job.id,))
        return acceptance


__all__ = ["ReflectionGenerationService"]
