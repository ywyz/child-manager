"""提示词测试执行与公开任务查询。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from time import monotonic
from typing import Protocol
from uuid import UUID

from pydantic import ValidationError

from packages.backend.integrations.ai.errors import AiClientError
from packages.backend.prompts.renderer import render_prompt


@dataclass(frozen=True, slots=True)
class PromptTestExecutionContext:
    kindergarten_id: UUID
    job_id: UUID
    run_id: UUID
    requested_by: UUID
    model_profile_id: UUID
    input_context: dict[str, object]
    prompt_content: str
    result_schema_code: str
    result_schema_version: int
    model_call_snapshot: dict[str, object]


@dataclass(frozen=True, slots=True)
class CurrentModelCallProfile:
    kindergarten_id: UUID
    profile_id: UUID
    api_base_url: str
    model_name: str
    capability_codes: frozenset[str]
    call_config_revision: int
    is_active: bool
    key_envelope: object


class PromptTestStore(Protocol):
    def kindergarten_id_for_job(self, job_id: UUID) -> UUID | None: ...
    def claim_prompt_test(self, kindergarten_id: UUID, job_id: UUID, worker_id: str) -> bool: ...
    def load_prompt_test_context(
        self, kindergarten_id: UUID, job_id: UUID
    ) -> PromptTestExecutionContext: ...
    def get_current_profile(
        self, kindergarten_id: UUID, profile_id: UUID
    ) -> CurrentModelCallProfile: ...
    def finish_prompt_test_failure(
        self, kindergarten_id: UUID, job_id: UUID, *, code: str, summary: str
    ) -> None: ...
    def finish_prompt_test_success(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        output: dict[str, object],
        elapsed_ms: int,
    ) -> None: ...
    def handle_prompt_test_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        code: str,
        summary: str,
        retryable: bool,
    ) -> bool: ...
    def recoverable_job_ids(self, *, now: datetime, limit: int) -> list[UUID]: ...


class PromptTestAuthorizer(Protocol):
    def can_run_prompt_test(self, kindergarten_id: UUID, requested_by: UUID) -> bool: ...


class StructuredAiClient(Protocol):
    def generate_structured(
        self,
        *,
        base_url: str,
        api_key: str,
        model_name: str,
        prompt: str,
    ) -> dict[str, object]: ...


class PromptTestRetry(RuntimeError):
    """通知消息代理按固定退避重投，不携带供应商异常正文。"""


class PromptTestExecutor:
    def __init__(
        self,
        *,
        store: PromptTestStore,
        client: StructuredAiClient,
        authorizer: PromptTestAuthorizer,
        read_api_key: Callable[[CurrentModelCallProfile], str],
        validate_url: Callable[[str], object],
        validate_result: Callable[[str, dict[str, object]], dict[str, object]],
    ) -> None:
        self.store = store
        self.client = client
        self.authorizer = authorizer
        self.read_api_key = read_api_key
        self.validate_url = validate_url
        self.validate_result = validate_result

    def execute_job(self, job_id: UUID, *, worker_id: str) -> None:
        kindergarten_id = self.store.kindergarten_id_for_job(job_id)
        if kindergarten_id is not None:
            self.execute(kindergarten_id, job_id, worker_id=worker_id)

    def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None:
        if not self.store.claim_prompt_test(kindergarten_id, job_id, worker_id):
            return
        try:
            context = self.store.load_prompt_test_context(kindergarten_id, job_id)
            profile = self.store.get_current_profile(kindergarten_id, context.model_profile_id)
            frozen_revision = int(str(context.model_call_snapshot["call_config_revision"]))
            if profile.call_config_revision != frozen_revision:
                self.store.finish_prompt_test_failure(
                    kindergarten_id,
                    job_id,
                    code="prompt.configuration_changed",
                    summary="模型调用配置已变化，请重新测试。",
                )
                return
            if not profile.is_active or not self.authorizer.can_run_prompt_test(
                kindergarten_id, context.requested_by
            ):
                self.store.finish_prompt_test_failure(
                    kindergarten_id,
                    job_id,
                    code="prompt.model_unavailable",
                    summary="模型档案当前不可用。",
                )
                return
            self.validate_url(profile.api_base_url)
            api_key = self.read_api_key(profile)
            prompt = render_prompt(
                context.prompt_content,
                context.input_context,
                set(context.input_context),
            )
            started = monotonic()
            raw = self.client.generate_structured(
                base_url=str(context.model_call_snapshot["base_url"]),
                model_name=str(context.model_call_snapshot["model_name"]),
                api_key=api_key,
                prompt=prompt,
            )
            output = self.validate_result(context.result_schema_code, raw)
            self.store.finish_prompt_test_success(
                kindergarten_id,
                job_id,
                output=output,
                elapsed_ms=max(0, int((monotonic() - started) * 1000)),
            )
        except AiClientError as exc:
            self._handle_error(
                kindergarten_id,
                job_id,
                code=exc.code,
                summary=str(exc),
                retryable=exc.code
                in {
                    "ai.timeout",
                    "ai.unavailable",
                    "ai.rate_limited",
                    "ai.provider_error",
                    "ai.invalid_response",
                    "ai.response_too_large",
                },
            )
        except ValidationError:
            self._handle_error(
                kindergarten_id,
                job_id,
                code="ai.invalid_response",
                summary="模型响应结构无效。",
                retryable=True,
            )
        except Exception:
            self._handle_error(
                kindergarten_id,
                job_id,
                code="prompt.execution_failed",
                summary="提示词测试执行失败。",
                retryable=False,
            )

    def _handle_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        code: str,
        summary: str,
        retryable: bool,
    ) -> None:
        should_retry = self.store.handle_prompt_test_error(
            kindergarten_id,
            job_id,
            code=code,
            summary=summary,
            retryable=retryable,
        )
        if should_retry:
            raise PromptTestRetry("提示词测试将按固定策略重试")
