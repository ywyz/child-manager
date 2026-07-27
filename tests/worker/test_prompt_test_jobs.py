from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from importlib import import_module
from time import sleep
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
    heartbeats: int = 0
    heartbeat_failures_remaining: int = 0

    def kindergarten_id_for_job(self, job_id: UUID) -> UUID | None:
        assert job_id == self.context.job_id
        return self.context.kindergarten_id

    def recoverable_job_ids(
        self,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]:
        del now, limit, include_expired
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
        worker_id: str,
        code: str,
        summary: str,
        elapsed_ms: int,
    ) -> None:
        assert worker_id == "worker-1"
        assert kindergarten_id == self.context.kindergarten_id
        assert job_id == self.context.job_id
        assert elapsed_ms >= 0
        self.failures.append((code, summary))

    def finish_prompt_test_success(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        output: dict[str, object],
        elapsed_ms: int,
    ) -> None:
        assert worker_id == "worker-1"
        assert kindergarten_id == self.context.kindergarten_id
        assert job_id == self.context.job_id
        assert elapsed_ms >= 0
        self.successes.append(output)

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
    ) -> int | None:
        del retry_after_seconds
        if retryable and self.retry_errors:
            return 5
        self.finish_prompt_test_failure(
            kindergarten_id,
            job_id,
            worker_id=worker_id,
            code=code,
            summary=summary,
            elapsed_ms=elapsed_ms or 0,
        )
        return None

    def heartbeat_prompt_test(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
    ) -> bool:
        assert kindergarten_id == self.context.kindergarten_id
        assert job_id == self.context.job_id
        assert worker_id == "worker-1"
        if self.heartbeat_failures_remaining:
            self.heartbeat_failures_remaining -= 1
            raise RuntimeError("transient database error")
        self.heartbeats += 1
        return True


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


class SlowClient(FakeClient):
    def generate_structured(self, **kwargs: object) -> dict[str, object]:
        sleep(0.03)
        return super().generate_structured(**kwargs)


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
            "teacher_context": "冻结补充",
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
        max_concurrency=2,
        rate_limit_per_minute=None,
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
        validate_result=lambda _code, result, _input: result,
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
        max_concurrency=2,
        rate_limit_per_minute=None,
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
        validate_result=lambda _code, result, _input: result,
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
        max_concurrency=2,
        rate_limit_per_minute=None,
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
        validate_result=lambda _code, result, _input: result,
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
        max_concurrency=2,
        rate_limit_per_minute=None,
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
        validate_result=lambda _code, result, _input: result,
    )

    with pytest.raises(service.PromptTestRetry) as raised:
        executor.execute(context.kindergarten_id, context.job_id, worker_id="worker-1")

    assert store.failures == []
    assert raised.value.delay_seconds == 5


def test_long_model_call_renews_the_worker_owned_lease() -> None:
    service, _leases, _actors = _modules()
    context = _context(service)
    profile = service.CurrentModelCallProfile(
        kindergarten_id=context.kindergarten_id,
        profile_id=context.model_profile_id,
        api_base_url="https://ai.example.test/v1",
        model_name="frozen-model",
        capability_codes=frozenset({"text", "structured_output"}),
        call_config_revision=3,
        max_concurrency=1,
        rate_limit_per_minute=10,
        is_active=True,
        key_envelope=object(),
    )
    store = FakeStore(context, profile)
    executor = service.PromptTestExecutor(
        store=store,
        client=SlowClient({"topic": "春天", "questions": []}),
        authorizer=FakeAuthorizer(),
        read_api_key=lambda _profile: "secret",
        validate_url=lambda value: value,
        validate_result=lambda _code, result, _input: result,
        heartbeat_interval_seconds=0.01,
    )

    executor.execute(context.kindergarten_id, context.job_id, worker_id="worker-1")

    assert store.heartbeats >= 1
    assert len(store.successes) == 1


def test_transient_heartbeat_failure_does_not_abandon_the_active_lease() -> None:
    service, _leases, _actors = _modules()
    context = _context(service)
    profile = service.CurrentModelCallProfile(
        kindergarten_id=context.kindergarten_id,
        profile_id=context.model_profile_id,
        api_base_url="https://ai.example.test/v1",
        model_name="frozen-model",
        capability_codes=frozenset({"text", "structured_output"}),
        call_config_revision=3,
        max_concurrency=1,
        rate_limit_per_minute=10,
        is_active=True,
        key_envelope=object(),
    )
    store = FakeStore(context, profile, heartbeat_failures_remaining=1)
    executor = service.PromptTestExecutor(
        store=store,
        client=SlowClient({"topic": "春天", "questions": []}),
        authorizer=FakeAuthorizer(),
        read_api_key=lambda _profile: "secret",
        validate_url=lambda value: value,
        validate_result=lambda _code, result, _input: result,
        heartbeat_interval_seconds=0.01,
    )

    executor.execute(context.kindergarten_id, context.job_id, worker_id="worker-1")

    assert store.heartbeat_failures_remaining == 0
    assert store.heartbeats >= 1
    assert len(store.successes) == 1


def test_each_actor_delivery_uses_a_unique_lease_owner_token() -> None:
    _service, _leases, actors = _modules()

    first = actors._worker_id()
    second = actors._worker_id()

    assert first != second
    assert first.rsplit(":", 1)[0] == second.rsplit(":", 1)[0]


def test_retry_delays_use_deterministic_bounded_jitter() -> None:
    policy = import_module("packages.backend.jobs.retry_policy")
    job_id = UUID("01900000-0000-7000-8000-000000000001")

    first = policy.retry_delay_seconds(job_id, attempt_count=1)
    second = policy.retry_delay_seconds(job_id, attempt_count=2)

    assert first in range(4, 7)
    assert second in range(24, 37)
    assert policy.retry_delay_seconds(job_id, attempt_count=1) == first


def test_lease_expiry_and_recovery_scan_are_deterministic() -> None:
    _service, leases, actors = _modules()
    now = datetime(2026, 7, 26, 12, 0, tzinfo=UTC)
    assert leases.lease_is_expired(now - timedelta(seconds=1), now=now) is True
    assert leases.lease_is_expired(now + timedelta(seconds=1), now=now) is False

    class SchedulerStore:
        def __init__(self) -> None:
            self.marked: list[UUID] = []
            self.kindergarten_id = uuid4()

        def recoverable_job_ids(
            self,
            *,
            now: datetime,
            limit: int,
            include_expired: bool,
        ) -> list[UUID]:
            assert now == datetime(2026, 7, 26, 12, 0, tzinfo=UTC)
            assert limit == 100
            assert include_expired is True
            return [uuid4(), uuid4()]

        def kindergarten_id_for_job(self, job_id: UUID) -> UUID | None:
            del job_id
            return self.kindergarten_id

        def mark_prompt_test_dispatched(self, kindergarten_id: UUID, job_id: UUID) -> None:
            assert kindergarten_id == self.kindergarten_id
            self.marked.append(job_id)

    dispatched: list[UUID] = []
    store = SchedulerStore()
    count = actors.recover_prompt_test_jobs(
        store,
        dispatch=dispatched.append,
        now=now,
        limit=100,
    )
    assert count == 2
    assert len(dispatched) == 2
    assert store.marked == dispatched


def test_recovery_dispatch_failure_does_not_skip_later_reserved_jobs() -> None:
    _service, _leases, actors = _modules()
    job_ids = [uuid4(), uuid4()]

    class SchedulerStore:
        def __init__(self) -> None:
            self.marked: list[UUID] = []
            self.kindergarten_id = uuid4()

        def recoverable_job_ids(
            self,
            *,
            now: datetime,
            limit: int,
            include_expired: bool,
        ) -> list[UUID]:
            del now, limit, include_expired
            return job_ids

        def kindergarten_id_for_job(self, job_id: UUID) -> UUID | None:
            del job_id
            return self.kindergarten_id

        def mark_prompt_test_dispatched(self, kindergarten_id: UUID, job_id: UUID) -> None:
            assert kindergarten_id == self.kindergarten_id
            self.marked.append(job_id)

    attempted: list[UUID] = []

    def dispatch(job_id: UUID) -> None:
        attempted.append(job_id)
        if job_id == job_ids[0]:
            raise RuntimeError("Redis unavailable")

    store = SchedulerStore()
    count = actors.recover_prompt_test_jobs(store, dispatch=dispatch)

    assert attempted == job_ids
    assert count == 1
    assert store.marked == [job_ids[1]]
