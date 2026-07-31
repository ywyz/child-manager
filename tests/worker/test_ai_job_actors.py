"""T104 AI Dramatiq actor 的最小消息与执行委派验收。"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from dramatiq import Retry

from apps.worker import scheduler as scheduler_module
from apps.worker.actors import register_actors
from apps.worker.broker import build_test_broker
from apps.worker.scheduler import run_ai_recovery_scan
from packages.backend.jobs.ai_runner import AiJobRetry


@dataclass
class FakeScopeResolver:
    kindergarten_id: UUID | None
    looked_up: list[UUID] = field(default_factory=list)

    def kindergarten_id_for_ai_job(self, job_id: UUID) -> UUID | None:
        self.looked_up.append(job_id)
        return self.kindergarten_id


@dataclass
class FakeRunner:
    retry_seconds: int | None = None
    calls: list[tuple[UUID, UUID, str]] = field(default_factory=list)

    def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None:
        self.calls.append((kindergarten_id, job_id, worker_id))
        if self.retry_seconds is not None:
            raise AiJobRetry(self.retry_seconds)


@dataclass
class PartiallyFailingRecoveryStore:
    failing_kindergarten_id: UUID
    job_ids: list[UUID]
    visited: list[UUID] = field(default_factory=list)

    def reserve_recoverable_jobs(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]:
        del now, limit, include_expired
        self.visited.append(kindergarten_id)
        if kindergarten_id == self.failing_kindergarten_id:
            raise RuntimeError("不得记录此恢复诊断正文")
        return self.job_ids


def _ai_actor(runner: FakeRunner, scope_resolver: FakeScopeResolver):
    actors = register_actors(
        build_test_broker(),
        ai_runner=runner,
        ai_job_scope_resolver=scope_resolver,
    )
    assert [actor.actor_name for actor in actors] == ["prompt_test", "ai_job"]
    return actors[1]


def test_ai_actor_resolves_tenant_from_job_id_and_delegates_to_shared_runner() -> None:
    kindergarten_id = uuid4()
    job_id = uuid4()
    scope_resolver = FakeScopeResolver(kindergarten_id)
    runner = FakeRunner()

    returned = _ai_actor(runner, scope_resolver).fn(str(job_id))

    assert returned == str(job_id)
    assert scope_resolver.looked_up == [job_id]
    assert len(runner.calls) == 1
    assert runner.calls[0][:2] == (kindergarten_id, job_id)
    assert runner.calls[0][2]


def test_ai_actor_ignores_unknown_or_non_executable_job_id() -> None:
    job_id = uuid4()
    scope_resolver = FakeScopeResolver(None)
    runner = FakeRunner()

    assert _ai_actor(runner, scope_resolver).fn(str(job_id)) == str(job_id)
    assert scope_resolver.looked_up == [job_id]
    assert runner.calls == []


def test_ai_actor_maps_authoritative_retry_delay_to_dramatiq_retry() -> None:
    runner = FakeRunner(retry_seconds=17)

    with pytest.raises(Retry) as raised:
        _ai_actor(runner, FakeScopeResolver(uuid4())).fn(str(uuid4()))

    assert raised.value.delay == 17_000


def test_ai_recovery_isolates_tenant_and_dispatch_failures(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failing_kindergarten_id = uuid4()
    succeeding_kindergarten_id = uuid4()
    job_ids = [uuid4(), uuid4()]
    store = PartiallyFailingRecoveryStore(failing_kindergarten_id, job_ids)
    attempted: list[UUID] = []

    def dispatch(job_id: UUID) -> None:
        attempted.append(job_id)
        if job_id == job_ids[0]:
            raise RuntimeError("不得记录此投递诊断正文")

    monkeypatch.setattr(scheduler_module.logger, "disabled", False)
    with caplog.at_level(logging.ERROR, logger=scheduler_module.__name__):
        count = run_ai_recovery_scan(
            store=store,
            dispatch=dispatch,
            kindergarten_ids=[failing_kindergarten_id, succeeding_kindergarten_id],
            now=datetime(2026, 7, 29, tzinfo=UTC),
        )

    assert store.visited == [failing_kindergarten_id, succeeding_kindergarten_id]
    assert attempted == job_ids
    assert count == 1
    assert any(record.__dict__.get("exception_type") == "RuntimeError" for record in caplog.records)
    assert "不得记录此恢复诊断正文" not in caplog.text
    assert "不得记录此投递诊断正文" not in caplog.text
