"""M6 AI Worker 重试与超时策略 RED 验收。"""

from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from typing import Any
from uuid import UUID

import pytest

from packages.backend.integrations.ai.client import ProviderNeutralAiClient
from packages.backend.integrations.ai.errors import AiClientError
from packages.backend.jobs import retry_policy
from packages.backend.prompts.catalog import validate_prompt_result_schema
from tests.worker.test_ai_job_recovery import StatefulStore, _executor


def test_ai_generation_uses_ten_second_connect_and_120_second_read_timeout() -> None:
    client = ProviderNeutralAiClient(allowed_hosts=set())

    assert client.timeout.connect == 10
    assert client.timeout.read == 120


def test_retry_delays_use_five_and_thirty_second_jitter_windows() -> None:
    job_id = UUID("01900000-0000-7000-8000-000000000001")

    assert 4 <= retry_policy.retry_delay_seconds(job_id, attempt_count=1) <= 6
    assert 24 <= retry_policy.retry_delay_seconds(job_id, attempt_count=2) <= 36


def test_retry_after_is_capped_at_sixty_seconds() -> None:
    cap = getattr(retry_policy, "cap_retry_after_seconds", None)
    assert cap is not None, "M6 retry classifier missing: cap_retry_after_seconds"

    assert cap(None) is None
    assert cap(3) == 3
    assert cap(120) == 60


@pytest.mark.parametrize(
    ("code", "retryable"),
    [
        ("ai.timeout", True),
        ("ai.unavailable", True),
        ("ai.rate_limited", True),
        ("ai.provider_error", True),
        ("ai.invalid_response", True),
        ("ai.response_too_large", True),
        ("ai.authentication_failed", False),
        ("ai.balance_unavailable", False),
        ("ai.model_not_found", False),
        ("ai.request_rejected", False),
        ("ai.address_rejected", False),
    ],
)
def test_error_classification_is_stable(code: str, retryable: bool) -> None:
    classify = getattr(retry_policy, "is_retryable_ai_error", None)
    assert classify is not None, "M6 retry classifier missing: is_retryable_ai_error"

    assert classify(code) is retryable


@dataclass
class RetryingStore(StatefulStore):
    attempts: int = 0
    failure: tuple[str, int] | None = None

    def claim(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        lease_expires_at: datetime,
    ) -> bool:
        del worker_id, lease_expires_at
        assert kindergarten_id == self.kindergarten_id
        assert job_id == self.job_id
        if self.terminal:
            return False
        self.claimed = True
        return True

    def begin_model_call(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
    ) -> bool:
        assert super().begin_model_call(
            kindergarten_id,
            job_id,
            worker_id=worker_id,
        )
        self.attempts += 1
        return True

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
        del worker_id, summary, retry_after_seconds, elapsed_ms
        assert kindergarten_id == self.kindergarten_id
        assert job_id == self.job_id
        self.claimed = False
        if retryable and self.attempts < retry_policy.MAX_AI_ATTEMPTS:
            return retry_policy.retry_delay_seconds(job_id, attempt_count=self.attempts)
        self.terminal = True
        self.failure = (code, self.attempts)
        return None


class AlwaysTimeoutClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate_structured(self, **_kwargs: object) -> dict[str, object]:
        self.calls += 1
        raise AiClientError("ai.timeout", "模型服务响应超时。")


class AddStepStore(RetryingStore):
    def load_execution_context(self, kindergarten_id: UUID, job_id: UUID) -> Any:
        context = super().load_execution_context(kindergarten_id, job_id)
        context.input_context = {
            "group_activity": {
                "theme": "春天",
                "objectives": ["观察变化"],
                "preparation": ["图片"],
                "focus": "表达发现",
                "difficulty": "连续描述",
                "process": [{"heading": "观察", "lines": ["观察图片"]}],
            },
            "age_group_name": "大班",
            "teacher_context": "春季",
        }
        context.result_schema_code = "prompt.group_activity_add_step.v1"
        return context


class InvalidAddStepClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate_structured(self, **_kwargs: object) -> dict[str, object]:
        self.calls += 1
        return {
            "step": {"heading": "延伸", "lines": ["绘制春天"]},
            "suggested_insert_index": 2,
        }


def test_runner_returns_two_backoffs_then_stops_after_three_real_calls() -> None:
    module: Any = import_module("packages.backend.jobs.ai_runner")
    store = RetryingStore()
    client = AlwaysTimeoutClient()
    executor = _executor(module, store, client)
    delays: list[int] = []

    for _attempt in range(3):
        try:
            executor.execute(
                store.kindergarten_id,
                store.job_id,
                worker_id="worker-retry",
            )
        except module.AiJobRetry as exc:
            delays.append(exc.delay_seconds)

    executor.execute(
        store.kindergarten_id,
        store.job_id,
        worker_id="late-duplicate",
    )

    assert client.calls == 3
    assert len(delays) == 2
    assert 4 <= delays[0] <= 6
    assert 24 <= delays[1] <= 36
    assert store.failure == ("ai.timeout", 3)


def test_out_of_range_add_step_is_not_clamped_and_retries_exactly_twice() -> None:
    module: Any = import_module("packages.backend.jobs.ai_runner")
    store = AddStepStore()
    client = InvalidAddStepClient()
    executor = _executor(
        module,
        store,
        client,
        validate_result=lambda code, result, input_context: validate_prompt_result_schema(
            code,
            result,
            input_context=input_context,
        ),
    )
    delays: list[int] = []

    for _attempt in range(3):
        try:
            executor.execute(
                store.kindergarten_id,
                store.job_id,
                worker_id="worker-add-step",
            )
        except module.AiJobRetry as exc:
            delays.append(exc.delay_seconds)

    assert client.calls == 3
    assert len(delays) == 2
    assert store.successes == []
    assert store.failure == ("ai.invalid_response", 3)
