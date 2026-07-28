"""AI 生成任务的冻结上下文执行器与 PostgreSQL 状态适配器。"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from threading import Event, Thread
from time import monotonic
from typing import Any, Protocol, cast
from uuid import UUID

from psycopg.types.json import Jsonb
from pydantic import ValidationError

from packages.backend.integrations.ai.errors import AiClientError
from packages.backend.integrations.crypto.ai_keys import AiKeyEnvelope
from packages.backend.jobs.retry_policy import (
    cap_retry_after_seconds,
    is_retryable_ai_error,
    retry_delay_seconds,
)
from packages.backend.jobs.service import (
    CurrentModelCallProfile,
    ProfileCallLimiter,
    StructuredAiClient,
)
from packages.backend.lesson_plans.ai_fingerprints import JsonValue, canonical_json_sha256
from packages.backend.prompts.catalog import validate_prompt_result_schema
from packages.backend.prompts.renderer import PromptTemplateError, render_prompt

logger = logging.getLogger(__name__)

_REQUIRED_CAPABILITIES = frozenset({"text", "structured_output"})


@dataclass(frozen=True, slots=True)
class AiExecutionContext:
    kindergarten_id: UUID
    job_id: UUID
    requested_by: UUID
    plan_id: UUID
    class_id: UUID
    model_profile_id: UUID
    model_name_snapshot: str
    input_context: dict[str, object]
    prompt_content: str
    result_schema_code: str
    result_schema_version: int


class AiJobStoreProtocol(Protocol):
    def claim(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        lease_expires_at: datetime,
    ) -> bool: ...

    def load_execution_context(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
    ) -> AiExecutionContext: ...

    def get_current_profile(
        self,
        kindergarten_id: UUID,
        profile_id: UUID,
    ) -> CurrentModelCallProfile: ...

    def heartbeat(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        lease_expires_at: datetime,
    ) -> bool: ...

    def begin_model_call(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
    ) -> bool: ...

    def complete_result_once(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        output_content: dict[str, object],
        output_sha256: str,
    ) -> bool: ...

    def finish_failure(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        elapsed_ms: int,
    ) -> None: ...

    def handle_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        retryable: bool,
        retry_after_seconds: int | None,
        elapsed_ms: int,
    ) -> int | None: ...


class AiJobAuthorizer(Protocol):
    def can_execute(self, context: AiExecutionContext) -> bool: ...


class AiJobRetry(RuntimeError):
    """通知消息代理按权威任务给出的退避时间重投。"""

    def __init__(self, delay_seconds: int) -> None:
        super().__init__("AI 生成任务将按固定策略重试")
        self.delay_seconds = delay_seconds


class AiJobStore:
    """以独立提交的 SQL 执行 AI Worker 状态迁移。"""

    def __init__(self, connection: Any) -> None:
        if not bool(getattr(connection, "autocommit", False)):
            raise ValueError("AiJobStore requires an autocommit connection")
        self.connection = connection

    def claim(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        lease_expires_at: datetime,
    ) -> bool:
        result = self.connection.execute(
            """UPDATE background_jobs AS job
            SET execution_status='running',
                lease_owner=%s,lease_expires_at=%s,last_heartbeat_at=now(),
                started_at=COALESCE(started_at,now()),updated_at=now()
            WHERE job.kindergarten_id=%s AND job.id=%s
              AND job.job_type LIKE 'ai.%%' AND job.job_type<>'ai.batch'
              AND job.attempt_count<job.max_attempts
              AND (
                job.execution_status IN ('pending_dispatch','queued')
                OR (job.execution_status='retrying' AND job.queued_at<=now())
                OR (job.execution_status='running' AND job.lease_expires_at<now())
              )
              AND EXISTS (
                SELECT 1 FROM ai_generation_results AS result
                WHERE result.kindergarten_id=job.kindergarten_id
                  AND result.job_id=job.id
                  AND result.input_context IS NOT NULL
                  AND result.output_content IS NULL
                  AND result.output_sha256 IS NULL
                  AND result.content_cleared_at IS NULL
                  AND result.adopted_at IS NULL
                  AND result.rejected_at IS NULL
              )""",
            (worker_id, lease_expires_at, kindergarten_id, job_id),
        )
        return bool(getattr(result, "rowcount", 0))

    def begin_model_call(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
    ) -> bool:
        result = self.connection.execute(
            """UPDATE background_jobs
            SET attempt_count=attempt_count+1,updated_at=now()
            WHERE kindergarten_id=%s AND id=%s
              AND job_type LIKE 'ai.%%' AND job_type<>'ai.batch'
              AND execution_status='running' AND lease_owner=%s
              AND attempt_count<max_attempts""",
            (kindergarten_id, job_id, worker_id),
        )
        return bool(getattr(result, "rowcount", 0))

    def load_execution_context(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
    ) -> AiExecutionContext:
        row = self.connection.execute(
            """SELECT job.requested_by,result.plan_id,plan.class_id,
                      result.model_profile_id,result.model_name_snapshot,
                      result.input_context,version.content,
                      result.prompt_content_sha256,version.content_sha256,
                      result.result_schema_code,result.result_schema_version
            FROM background_jobs AS job
            JOIN ai_generation_results AS result
              ON result.kindergarten_id=job.kindergarten_id AND result.job_id=job.id
            JOIN daily_activity_plans AS plan
              ON plan.kindergarten_id=result.kindergarten_id AND plan.id=result.plan_id
            JOIN prompt_versions AS version
              ON version.kindergarten_id=result.kindergarten_id
             AND version.prompt_definition_id=result.prompt_definition_id
             AND version.id=result.prompt_version_id
            WHERE job.kindergarten_id=%s AND job.id=%s
              AND job.job_type LIKE 'ai.%%' AND job.job_type<>'ai.batch'
              AND job.execution_status='running'
              AND result.output_content IS NULL AND result.output_sha256 IS NULL
              AND result.content_cleared_at IS NULL""",
            (kindergarten_id, job_id),
        ).fetchone()
        if row is None or row[5] is None:
            raise LookupError("AI 任务冻结上下文不存在")
        prompt_content = str(row[6])
        prompt_sha256 = sha256(prompt_content.encode()).hexdigest()
        if str(row[7]) != str(row[8]) or str(row[7]) != prompt_sha256:
            raise LookupError("AI 任务提示词快照无效")
        if int(cast(Any, row[10])) != 1:
            raise LookupError("AI 任务结果 Schema 版本无效")
        return AiExecutionContext(
            kindergarten_id=kindergarten_id,
            job_id=job_id,
            requested_by=UUID(str(row[0])),
            plan_id=UUID(str(row[1])),
            class_id=UUID(str(row[2])),
            model_profile_id=UUID(str(row[3])),
            model_name_snapshot=str(row[4]),
            input_context=cast(dict[str, object], row[5]),
            prompt_content=prompt_content,
            result_schema_code=str(row[9]),
            result_schema_version=int(cast(Any, row[10])),
        )

    def get_current_profile(
        self,
        kindergarten_id: UUID,
        profile_id: UUID,
    ) -> CurrentModelCallProfile:
        row = self.connection.execute(
            """SELECT profile.api_base_url,profile.model_name,
                      profile.call_config_revision,profile.max_concurrency,
                      profile.rate_limit_per_minute,profile.is_active,
                      profile.api_key_ciphertext,profile.api_key_nonce,
                      profile.api_key_key_id,profile.api_key_encryption_version,
                      profile.api_key_last_four,
                      COALESCE(
                        array_agg(capability.capability_code ORDER BY capability.capability_code)
                        FILTER (WHERE capability.capability_code IS NOT NULL),
                        ARRAY[]::varchar[]
                      )
            FROM ai_model_profiles AS profile
            LEFT JOIN ai_model_profile_capabilities AS capability
              ON capability.kindergarten_id=profile.kindergarten_id
             AND capability.model_profile_id=profile.id
            WHERE profile.kindergarten_id=%s AND profile.id=%s
            GROUP BY profile.id""",
            (kindergarten_id, profile_id),
        ).fetchone()
        if row is None:
            raise LookupError("模型档案不存在")
        envelope = (
            AiKeyEnvelope(
                ciphertext=bytes(cast(Any, row[6])),
                nonce=bytes(cast(Any, row[7])),
                key_id=str(row[8]),
                envelope_version=int(cast(Any, row[9])),
                last_four=str(row[10] or ""),
            )
            if all(row[index] is not None for index in (6, 7, 8, 9))
            else None
        )
        return CurrentModelCallProfile(
            kindergarten_id=kindergarten_id,
            profile_id=profile_id,
            api_base_url=str(row[0]),
            model_name=str(row[1]),
            capability_codes=frozenset(str(value) for value in cast(list[object], row[11])),
            call_config_revision=int(cast(Any, row[2])),
            max_concurrency=int(cast(Any, row[3])),
            rate_limit_per_minute=int(cast(Any, row[4])) if row[4] is not None else None,
            is_active=bool(row[5]),
            key_envelope=envelope,
        )

    def can_execute(self, context: AiExecutionContext) -> bool:
        row = self.connection.execute(
            """SELECT EXISTS (
                SELECT 1
                FROM daily_activity_plans AS plan
                JOIN classes AS class_record
                  ON class_record.kindergarten_id=plan.kindergarten_id
                 AND class_record.id=plan.class_id
                JOIN class_teachers AS relation
                  ON relation.kindergarten_id=plan.kindergarten_id
                 AND relation.class_id=plan.class_id
                 AND relation.user_id=%s
                JOIN users AS user_record
                  ON user_record.kindergarten_id=plan.kindergarten_id
                 AND user_record.id=relation.user_id
                JOIN user_roles AS user_role
                  ON user_role.kindergarten_id=user_record.kindergarten_id
                 AND user_role.user_id=user_record.id
                JOIN roles AS role
                  ON role.id=user_role.role_id AND role.code='teacher'
                WHERE plan.kindergarten_id=%s AND plan.id=%s
                  AND plan.class_id=%s
                  AND plan.archived_at IS NULL
                  AND class_record.is_active
                  AND user_record.status='active'
            )""",
            (
                context.requested_by,
                context.kindergarten_id,
                context.plan_id,
                context.class_id,
            ),
        ).fetchone()
        return bool(row and row[0])

    def heartbeat(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        lease_expires_at: datetime,
    ) -> bool:
        result = self.connection.execute(
            """UPDATE background_jobs
            SET lease_expires_at=%s,last_heartbeat_at=now(),updated_at=now()
            WHERE kindergarten_id=%s AND id=%s
              AND job_type LIKE 'ai.%%' AND job_type<>'ai.batch'
              AND execution_status='running' AND lease_owner=%s""",
            (lease_expires_at, kindergarten_id, job_id, worker_id),
        )
        return bool(getattr(result, "rowcount", 0))

    def complete_result_once(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        output_content: dict[str, object],
        output_sha256: str,
    ) -> bool:
        result = self.connection.execute(
            """WITH completed_result AS (
                UPDATE ai_generation_results AS ai_result
                SET output_content=%s,output_sha256=%s,updated_at=now()
                FROM background_jobs AS job
                WHERE job.kindergarten_id=%s AND job.id=%s
                  AND job.job_type LIKE 'ai.%%' AND job.job_type<>'ai.batch'
                  AND job.execution_status='running' AND job.lease_owner=%s
                  AND ai_result.kindergarten_id=job.kindergarten_id
                  AND ai_result.job_id=job.id
                  AND ai_result.output_content IS NULL
                  AND ai_result.output_sha256 IS NULL
                  AND ai_result.content_cleared_at IS NULL
                  AND ai_result.adopted_at IS NULL
                  AND ai_result.rejected_at IS NULL
                RETURNING ai_result.job_id
            )
            UPDATE background_jobs AS job
            SET execution_status='awaiting_confirmation',
                lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,
                updated_at=now()
            WHERE job.kindergarten_id=%s AND job.id=%s
              AND job.execution_status='running' AND job.lease_owner=%s
              AND EXISTS (
                SELECT 1 FROM completed_result WHERE completed_result.job_id=job.id
              )""",
            (
                Jsonb(output_content),
                output_sha256,
                kindergarten_id,
                job_id,
                worker_id,
                kindergarten_id,
                job_id,
                worker_id,
            ),
        )
        return bool(getattr(result, "rowcount", 0))

    def finish_failure(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        elapsed_ms: int,
    ) -> None:
        del elapsed_ms
        self.connection.execute(
            """UPDATE background_jobs
            SET execution_status='failed',finished_at=now(),
                error_code=%s,error_summary=%s,
                lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,
                updated_at=now()
            WHERE kindergarten_id=%s AND id=%s
              AND job_type LIKE 'ai.%%' AND job_type<>'ai.batch'
              AND execution_status='running' AND lease_owner=%s""",
            (code, summary[:1000], kindergarten_id, job_id, worker_id),
        )

    def handle_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        retryable: bool,
        retry_after_seconds: int | None,
        elapsed_ms: int,
    ) -> int | None:
        del elapsed_ms
        with self.connection.transaction():
            row = self.connection.execute(
                """SELECT attempt_count,max_attempts FROM background_jobs
                WHERE kindergarten_id=%s AND id=%s
                  AND job_type LIKE 'ai.%%' AND job_type<>'ai.batch'
                  AND execution_status='running' AND lease_owner=%s
                FOR UPDATE""",
                (kindergarten_id, job_id, worker_id),
            ).fetchone()
            if row is None:
                return None
            attempt_count = int(cast(Any, row[0]))
            max_attempts = int(cast(Any, row[1]))
            if retryable and attempt_count < max_attempts:
                delay = cap_retry_after_seconds(retry_after_seconds)
                if delay is None:
                    delay = retry_delay_seconds(job_id, attempt_count=attempt_count)
                result = self.connection.execute(
                    """UPDATE background_jobs
                    SET execution_status='retrying',
                        queued_at=now()+(%s * interval '1 second'),
                        lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,
                        updated_at=now()
                    WHERE kindergarten_id=%s AND id=%s
                      AND execution_status='running' AND lease_owner=%s""",
                    (delay, kindergarten_id, job_id, worker_id),
                )
                return delay if getattr(result, "rowcount", 0) else None
            self.finish_failure(
                kindergarten_id,
                job_id,
                worker_id=worker_id,
                code=code,
                summary=summary,
                elapsed_ms=0,
            )
            return None

    def recoverable_job_ids(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]:
        result = self.connection.execute(
            """SELECT id FROM background_jobs
            WHERE kindergarten_id=%s
              AND job_type LIKE 'ai.%%' AND job_type<>'ai.batch'
              AND attempt_count<max_attempts
              AND (
                execution_status='pending_dispatch'
                OR (execution_status='retrying' AND queued_at<=%s)
                OR (%s AND execution_status='running' AND lease_expires_at<%s)
            )
            ORDER BY created_at,id LIMIT %s""",
            (kindergarten_id, now, include_expired, now, limit),
        )
        return [UUID(str(row[0])) for row in result.fetchall()]


class AiJobRunner:
    def __init__(
        self,
        *,
        store: AiJobStoreProtocol,
        client: StructuredAiClient,
        authorizer: AiJobAuthorizer,
        read_api_key: Callable[[CurrentModelCallProfile], str],
        validate_url: Callable[[str], object],
        validate_result: Callable[
            [str, dict[str, object], dict[str, object]],
            dict[str, object],
        ]
        | None = None,
        limiter: ProfileCallLimiter | None = None,
        lease_seconds: int = 120,
        heartbeat_interval_seconds: float = 30,
    ) -> None:
        self.store = store
        self.client = client
        self.authorizer = authorizer
        self.read_api_key = read_api_key
        self.validate_url = validate_url
        self.validate_result = validate_result or (
            lambda code, result, input_context: validate_prompt_result_schema(
                code,
                result,
                input_context=input_context,
            )
        )
        self.limiter = limiter or ProfileCallLimiter()
        self.lease_seconds = lease_seconds
        self.heartbeat_interval_seconds = heartbeat_interval_seconds

    def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None:
        if not self.store.claim(
            kindergarten_id,
            job_id,
            worker_id=worker_id,
            lease_expires_at=datetime.now(UTC) + timedelta(seconds=self.lease_seconds),
        ):
            return
        heartbeat_stop = Event()

        def heartbeat() -> None:
            while not heartbeat_stop.wait(self.heartbeat_interval_seconds):
                try:
                    renewed = self.store.heartbeat(
                        kindergarten_id,
                        job_id,
                        worker_id=worker_id,
                        lease_expires_at=datetime.now(UTC) + timedelta(seconds=self.lease_seconds),
                    )
                except Exception:
                    logger.error("AI 任务心跳更新失败", extra={"job_id": str(job_id)})
                    continue
                if not renewed:
                    return

        heartbeat_thread = Thread(
            target=heartbeat,
            name=f"ai-job-heartbeat-{job_id}",
            daemon=True,
        )
        heartbeat_thread.start()
        started = monotonic()

        def elapsed_ms() -> int:
            return max(0, int((monotonic() - started) * 1000))

        try:
            try:
                context = self.store.load_execution_context(kindergarten_id, job_id)
            except Exception:
                self.store.finish_failure(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="ai.frozen_context_invalid",
                    summary="AI 任务冻结上下文无效。",
                    elapsed_ms=elapsed_ms(),
                )
                return
            if not self.authorizer.can_execute(context):
                self.store.finish_failure(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="ai.permission_revoked",
                    summary="当前账号或教案权限已失效。",
                    elapsed_ms=elapsed_ms(),
                )
                return
            try:
                profile = self.store.get_current_profile(
                    kindergarten_id,
                    context.model_profile_id,
                )
            except Exception:
                self.store.finish_failure(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="ai.model_unavailable",
                    summary="模型档案当前不可用。",
                    elapsed_ms=elapsed_ms(),
                )
                return
            if (
                not profile.is_active
                or profile.key_envelope is None
                or not _REQUIRED_CAPABILITIES.issubset(profile.capability_codes)
            ):
                self.store.finish_failure(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="ai.model_unavailable",
                    summary="模型档案当前不可用。",
                    elapsed_ms=elapsed_ms(),
                )
                return
            try:
                prompt = render_prompt(
                    context.prompt_content,
                    context.input_context,
                    set(context.input_context),
                )
            except PromptTemplateError as exc:
                self.store.finish_failure(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code=exc.code,
                    summary="AI 任务提示词变量无效。",
                    elapsed_ms=elapsed_ms(),
                )
                return
            try:
                self.validate_url(profile.api_base_url)
                api_key = self.read_api_key(profile)
            except Exception:
                self.store.finish_failure(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="ai.model_unavailable",
                    summary="模型地址或密钥当前不可用。",
                    elapsed_ms=elapsed_ms(),
                )
                return
            try:
                with self.limiter.slot(profile):
                    if not self.store.begin_model_call(
                        kindergarten_id,
                        job_id,
                        worker_id=worker_id,
                    ):
                        return
                    raw = self.client.generate_structured(
                        base_url=profile.api_base_url,
                        model_name=context.model_name_snapshot,
                        api_key=api_key,
                        prompt=prompt,
                    )
                output = self.validate_result(
                    context.result_schema_code,
                    raw,
                    context.input_context,
                )
                output_sha256 = canonical_json_sha256(cast(dict[str, JsonValue], output))
                self.store.complete_result_once(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    output_content=output,
                    output_sha256=output_sha256,
                )
            except AiClientError as exc:
                self._handle_error(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code=exc.code,
                    summary=str(exc),
                    retryable=is_retryable_ai_error(exc.code),
                    retry_after_seconds=exc.retry_after_seconds,
                    elapsed_ms=elapsed_ms(),
                )
            except ValidationError:
                self._handle_error(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="ai.invalid_response",
                    summary="模型响应结构无效。",
                    retryable=is_retryable_ai_error("ai.invalid_response"),
                    retry_after_seconds=None,
                    elapsed_ms=elapsed_ms(),
                )
            except Exception:
                self._handle_error(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="ai.execution_failed",
                    summary="AI 生成任务执行失败。",
                    retryable=False,
                    retry_after_seconds=None,
                    elapsed_ms=elapsed_ms(),
                )
        finally:
            heartbeat_stop.set()
            heartbeat_thread.join(timeout=1)

    def _handle_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        retryable: bool,
        retry_after_seconds: int | None,
        elapsed_ms: int,
    ) -> None:
        handle_error = getattr(self.store, "handle_error", None)
        if handle_error is None:
            self.store.finish_failure(
                kindergarten_id,
                job_id,
                worker_id=worker_id,
                code=code,
                summary=summary,
                elapsed_ms=elapsed_ms,
            )
            return
        retry_delay = handle_error(
            kindergarten_id,
            job_id,
            worker_id=worker_id,
            code=code,
            summary=summary,
            retryable=retryable,
            retry_after_seconds=retry_after_seconds,
            elapsed_ms=elapsed_ms,
        )
        if retry_delay is not None:
            raise AiJobRetry(retry_delay)
