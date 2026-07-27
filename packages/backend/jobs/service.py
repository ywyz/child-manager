"""提示词测试执行与公开任务查询。"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from threading import Condition, Event, Thread
from time import monotonic
from typing import Protocol
from uuid import UUID

from pydantic import ValidationError

from packages.backend.integrations.ai.errors import AiClientError
from packages.backend.prompts.renderer import render_prompt

logger = logging.getLogger(__name__)


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
    max_concurrency: int
    rate_limit_per_minute: int | None
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
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        elapsed_ms: int,
    ) -> None: ...
    def finish_prompt_test_success(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        output: dict[str, object],
        elapsed_ms: int,
    ) -> None: ...
    def handle_prompt_test_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        retryable: bool,
        retry_after_seconds: int | None,
        elapsed_ms: int | None,
    ) -> int | None: ...
    def heartbeat_prompt_test(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
    ) -> bool: ...
    def mark_prompt_test_dispatched(self, kindergarten_id: UUID, job_id: UUID) -> None: ...
    def recoverable_job_ids(
        self,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]: ...


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

    def __init__(self, delay_seconds: int) -> None:
        super().__init__("提示词测试将按固定策略重试")
        self.delay_seconds = delay_seconds


class ProfileCallLimiter:
    """单 Worker 进程内按模型档案执行并发和每分钟调用上限。"""

    def __init__(self) -> None:
        self._condition = Condition()
        self._active: dict[UUID, int] = defaultdict(int)
        self._calls: dict[UUID, deque[float]] = defaultdict(deque)

    @contextmanager
    def slot(self, profile: CurrentModelCallProfile) -> Iterator[None]:
        with self._condition:
            while True:
                now = monotonic()
                calls = self._calls[profile.profile_id]
                while calls and calls[0] <= now - 60:
                    calls.popleft()
                concurrency_ready = self._active[profile.profile_id] < profile.max_concurrency
                rate_ready = (
                    profile.rate_limit_per_minute is None
                    or len(calls) < profile.rate_limit_per_minute
                )
                if concurrency_ready and rate_ready:
                    self._active[profile.profile_id] += 1
                    calls.append(now)
                    break
                rate_wait = max(0.05, 60 - (now - calls[0])) if calls else 0.05
                self._condition.wait(timeout=min(1.0, rate_wait))
        try:
            yield
        finally:
            with self._condition:
                self._active[profile.profile_id] -= 1
                self._condition.notify_all()


class PromptTestExecutor:
    def __init__(
        self,
        *,
        store: PromptTestStore,
        client: StructuredAiClient,
        authorizer: PromptTestAuthorizer,
        read_api_key: Callable[[CurrentModelCallProfile], str],
        validate_url: Callable[[str], object],
        validate_result: Callable[
            [str, dict[str, object], dict[str, object]],
            dict[str, object],
        ],
        limiter: ProfileCallLimiter | None = None,
        heartbeat_interval_seconds: float = 30,
    ) -> None:
        self.store = store
        self.client = client
        self.authorizer = authorizer
        self.read_api_key = read_api_key
        self.validate_url = validate_url
        self.validate_result = validate_result
        self.limiter = limiter or ProfileCallLimiter()
        self.heartbeat_interval_seconds = heartbeat_interval_seconds

    def execute_job(self, job_id: UUID, *, worker_id: str) -> None:
        kindergarten_id = self.store.kindergarten_id_for_job(job_id)
        if kindergarten_id is not None:
            self.execute(kindergarten_id, job_id, worker_id=worker_id)

    def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None:
        if not self.store.claim_prompt_test(kindergarten_id, job_id, worker_id):
            return
        heartbeat_stop = Event()

        def heartbeat() -> None:
            while not heartbeat_stop.wait(self.heartbeat_interval_seconds):
                try:
                    renewed = self.store.heartbeat_prompt_test(
                        kindergarten_id,
                        job_id,
                        worker_id=worker_id,
                    )
                except Exception:
                    logger.error("提示词测试心跳更新失败", extra={"job_id": str(job_id)})
                    continue
                if not renewed:
                    return

        heartbeat_thread = Thread(
            target=heartbeat,
            name=f"prompt-test-heartbeat-{job_id}",
            daemon=True,
        )
        heartbeat_thread.start()
        started = monotonic()

        def attempt_elapsed_ms() -> int:
            return max(0, int((monotonic() - started) * 1000))

        try:
            try:
                context = self.store.load_prompt_test_context(kindergarten_id, job_id)
                profile = self.store.get_current_profile(kindergarten_id, context.model_profile_id)
                frozen_revision = int(str(context.model_call_snapshot["call_config_revision"]))
                if profile.call_config_revision != frozen_revision:
                    self.store.finish_prompt_test_failure(
                        kindergarten_id,
                        job_id,
                        worker_id=worker_id,
                        code="prompt.configuration_changed",
                        summary="模型调用配置已变化，请重新测试。",
                        elapsed_ms=attempt_elapsed_ms(),
                    )
                    return
                if not profile.is_active or not self.authorizer.can_run_prompt_test(
                    kindergarten_id, context.requested_by
                ):
                    self.store.finish_prompt_test_failure(
                        kindergarten_id,
                        job_id,
                        worker_id=worker_id,
                        code="prompt.model_unavailable",
                        summary="模型档案当前不可用。",
                        elapsed_ms=attempt_elapsed_ms(),
                    )
                    return
                self.validate_url(profile.api_base_url)
                api_key = self.read_api_key(profile)
                prompt = render_prompt(
                    context.prompt_content,
                    context.input_context,
                    set(context.input_context),
                )
                with self.limiter.slot(profile):
                    raw = self.client.generate_structured(
                        base_url=str(context.model_call_snapshot["base_url"]),
                        model_name=str(context.model_call_snapshot["model_name"]),
                        api_key=api_key,
                        prompt=prompt,
                    )
                output = self.validate_result(
                    context.result_schema_code,
                    raw,
                    context.input_context,
                )
                self.store.finish_prompt_test_success(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    output=output,
                    elapsed_ms=max(0, int((monotonic() - started) * 1000)),
                )
            except AiClientError as exc:
                self._handle_error(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
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
                    retry_after_seconds=exc.retry_after_seconds,
                    elapsed_ms=attempt_elapsed_ms(),
                )
            except ValidationError:
                self._handle_error(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="ai.invalid_response",
                    summary="模型响应结构无效。",
                    retryable=True,
                    retry_after_seconds=None,
                    elapsed_ms=attempt_elapsed_ms(),
                )
            except Exception:
                self._handle_error(
                    kindergarten_id,
                    job_id,
                    worker_id=worker_id,
                    code="prompt.execution_failed",
                    summary="提示词测试执行失败。",
                    retryable=False,
                    retry_after_seconds=None,
                    elapsed_ms=attempt_elapsed_ms(),
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
        elapsed_ms: int | None,
    ) -> None:
        retry_delay = self.store.handle_prompt_test_error(
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
            raise PromptTestRetry(retry_delay)
