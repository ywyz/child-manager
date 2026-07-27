from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import Any
from uuid import UUID, uuid4

import pytest


def _modules() -> tuple[Any, Any, Any]:
    try:
        service = import_module("packages.backend.jobs.service")
        leases = import_module("packages.backend.jobs.leases")
        actors = import_module("apps.worker.actors")
    except ModuleNotFoundError:
        pytest.fail("T082/T083 尚未提供提示词测试 Worker", pytrace=False)
    return service, leases, actors


@dataclass
class FakeStore:
    context: Any
    current_profile: Any
    claimed: bool = False
    failures: list[tuple[str, str]] = field(default_factory=list)
    successes: list[dict[str, object]] = field(default_factory=list)
    retry_errors: bool = False

    def kindergarten_id_for_job(self, job_id: UUID) -> UUID | None:
        assert job_id == self.context.job_id
        return self.context.kindergarten_id

    def recoverable_job_ids(self, *, now: datetime, limit: int) -> list[UUID]:
        del now, limit
        return []

    def claim_prompt_test(self, kindergarten_id: UUID, job_id: UUID, worker_id: str) -> bool:
        del kindergarten_id, job_id, worker_id
        if self.claimed:
            return False
        self.claimed = True
        return True

    def load_prompt_test_context(self, kindergarten_id: UUID, job_id: UUID) -> Any:
        assert kindergarten_id == self.context.kindergarten_id
        assert job_id == self.context.job_id
        return self.context

    def get_current_profile(self, kindergarten_id: UUID, profile_id: UUID) -> Any:
        assert kindergarten_id == self.context.kindergarten_id
        assert profile_id == self.context.model_profile_id
        return self.current_profile

    def finish_prompt_test_failure(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        code: str,
        summary: str,
    ) -> None:
        assert kindergarten_id == self.context.kindergarten_id
        assert job_id == self.context.job_id
        self.failures.append((code, summary))

    def finish_prompt_test_success(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        output: dict[str, object],
        elapsed_ms: int,
    ) -> None:
        assert kindergarten_id == self.context.kindergarten_id
        assert job_id == self.context.job_id
        assert elapsed_ms >= 0
        self.successes.append(output)

    def handle_prompt_test_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        code: str,
        summary: str,
        retryable: bool,
    ) -> bool:
        if retryable and self.retry_errors:
            return True
        self.finish_prompt_test_failure(
            kindergarten_id,
            job_id,
            code=code,
            summary=summary,
        )
        return False


@dataclass
class FakeClient:
    result: dict[str, object]
    calls: list[dict[str, object]] = field(default_factory=list)

    def generate_structured(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(dict(kwargs))
        return self.result


class TimeoutClient:
    def generate_structured(self, **kwargs: object) -> dict[str, object]:
        del kwargs
        errors = import_module("packages.backend.integrations.ai.errors")
        raise errors.AiClientError("ai.timeout", "模型服务响应超时。")


@dataclass
class FakeAuthorizer:
    allowed: bool = True
    checks: int = 0

    def can_run_prompt_test(
        self,
        kindergarten_id: UUID,
        requested_by: UUID,
    ) -> bool:
        del kindergarten_id, requested_by
        self.checks += 1
        return self.allowed


def _context(service: Any, *, revision: int = 3) -> Any:
    return service.PromptTestExecutionContext(
        kindergarten_id=uuid4(),
        job_id=uuid4(),
        run_id=uuid4(),
        requested_by=uuid4(),
        model_profile_id=uuid4(),
        input_context={
            "plan_date": "2026-07-26",
            "class_name": "冻结班级",
            "teacher_context": {"notes": "冻结补充"},
        },
        prompt_content="班级：{{class_name}}；补充：{{teacher_context}}",
        result_schema_code="prompt.morning_talk.v1",
        result_schema_version=1,
        model_call_snapshot={
            "profile_id": "ignored-by-test",
            "base_url": "https://ai.example.test/v1",
            "model_name": "frozen-model",
            "capabilities": ["structured_output", "text"],
            "call_config_revision": revision,
        },
    )


def test_revision_mismatch_fails_without_reading_key_or_calling_model() -> None:
    service, _leases, _actors = _modules()
    context = _context(service, revision=3)
    profile = service.CurrentModelCallProfile(
        kindergarten_id=context.kindergarten_id,
        profile_id=context.model_profile_id,
        api_base_url="https://new.example.test/v1",
        model_name="new-model",
        capability_codes=frozenset({"text", "structured_output"}),
        call_config_revision=4,
        is_active=True,
        key_envelope=object(),
    )
    store = FakeStore(context, profile)
    client = FakeClient({"topic": "不应调用", "questions": []})
    authorizer = FakeAuthorizer()
    key_reads = 0

    def read_key(_profile: Any) -> str:
        nonlocal key_reads
        key_reads += 1
        return "secret"

    executor = service.PromptTestExecutor(
        store=store,
        client=client,
        authorizer=authorizer,
        read_api_key=read_key,
        validate_url=lambda value: value,
        validate_result=lambda _code, result: result,
    )
    executor.execute(context.kindergarten_id, context.job_id, worker_id="worker-1")

    assert store.failures == [("prompt.configuration_changed", "模型调用配置已变化，请重新测试。")]
    assert client.calls == []
    assert key_reads == 0


def test_matching_revision_uses_only_frozen_context_and_current_key() -> None:
    service, _leases, _actors = _modules()
    context = _context(service, revision=3)
    profile = service.CurrentModelCallProfile(
        kindergarten_id=context.kindergarten_id,
        profile_id=context.model_profile_id,
        api_base_url="https://ai.example.test/v1",
        model_name="frozen-model",
        capability_codes=frozenset({"text", "structured_output"}),
        call_config_revision=3,
        is_active=True,
        key_envelope=object(),
    )
    store = FakeStore(context, profile)
    client = FakeClient({"topic": "春天", "questions": ["有什么变化？"]})
    authorizer = FakeAuthorizer()
    executor = service.PromptTestExecutor(
        store=store,
        client=client,
        authorizer=authorizer,
        read_api_key=lambda _profile: "current-secret",
        validate_url=lambda value: value,
        validate_result=lambda _code, result: result,
    )

    executor.execute(context.kindergarten_id, context.job_id, worker_id="worker-1")
    executor.execute(context.kindergarten_id, context.job_id, worker_id="worker-1")

    assert authorizer.checks == 1
    assert len(client.calls) == 1
    assert client.calls[0]["base_url"] == "https://ai.example.test/v1"
    assert client.calls[0]["model_name"] == "frozen-model"
    assert client.calls[0]["api_key"] == "current-secret"
    assert "schema_code" not in client.calls[0]
    assert "冻结班级" in str(client.calls[0]["prompt"])
    assert store.successes == [{"topic": "春天", "questions": ["有什么变化？"]}]


def test_worker_rechecks_authorization_and_enabled_state_before_external_call() -> None:
    service, _leases, _actors = _modules()
    context = _context(service)
    profile = service.CurrentModelCallProfile(
        kindergarten_id=context.kindergarten_id,
        profile_id=context.model_profile_id,
        api_base_url="https://ai.example.test/v1",
        model_name="frozen-model",
        capability_codes=frozenset({"text", "structured_output"}),
        call_config_revision=3,
        is_active=False,
        key_envelope=object(),
    )
    store = FakeStore(context, profile)
    client = FakeClient({})
    executor = service.PromptTestExecutor(
        store=store,
        client=client,
        authorizer=FakeAuthorizer(allowed=True),
        read_api_key=lambda _profile: "secret",
        validate_url=lambda value: value,
        validate_result=lambda _code, result: result,
    )

    executor.execute(context.kindergarten_id, context.job_id, worker_id="worker-1")

    assert store.failures == [("prompt.model_unavailable", "模型档案当前不可用。")]
    assert client.calls == []


def test_retryable_provider_failure_returns_control_to_the_broker_retry_policy() -> None:
    service, _leases, _actors = _modules()
    context = _context(service)
    profile = service.CurrentModelCallProfile(
        kindergarten_id=context.kindergarten_id,
        profile_id=context.model_profile_id,
        api_base_url="https://ai.example.test/v1",
        model_name="frozen-model",
        capability_codes=frozenset({"text", "structured_output"}),
        call_config_revision=3,
        is_active=True,
        key_envelope=object(),
    )
    store = FakeStore(context, profile, retry_errors=True)
    executor = service.PromptTestExecutor(
        store=store,
        client=TimeoutClient(),
        authorizer=FakeAuthorizer(),
        read_api_key=lambda _profile: "secret",
        validate_url=lambda value: value,
        validate_result=lambda _code, result: result,
    )

    with pytest.raises(service.PromptTestRetry):
        executor.execute(context.kindergarten_id, context.job_id, worker_id="worker-1")

    assert store.failures == []


def test_lease_expiry_and_recovery_scan_are_deterministic() -> None:
    _service, leases, actors = _modules()
    now = datetime(2026, 7, 26, 12, 0, tzinfo=UTC)
    assert leases.lease_is_expired(now - timedelta(seconds=1), now=now) is True
    assert leases.lease_is_expired(now + timedelta(seconds=1), now=now) is False

    class SchedulerStore:
        def recoverable_job_ids(self, *, now: datetime, limit: int) -> list[UUID]:
            assert now == datetime(2026, 7, 26, 12, 0, tzinfo=UTC)
            assert limit == 100
            return [uuid4(), uuid4()]

    dispatched: list[UUID] = []
    count = actors.recover_prompt_test_jobs(
        SchedulerStore(),
        dispatch=dispatched.append,
        now=now,
        limit=100,
    )
    assert count == 2
    assert len(dispatched) == 2
