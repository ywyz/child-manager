# ruff: noqa: F811

"""M6 AI Worker 租约、恢复、并发和去重 RED 验收。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from importlib import import_module
from inspect import signature
from threading import Event
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from packages.contracts.jobs import JobMessage
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    passkey_client,
)
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401
from tests.migrations.test_0008_ai_generation_results import (
    _insert_job,
    _insert_result,
    _native_url,
    _provision_dependencies,
    _result_values,
)


def _runner() -> Any:
    return import_module("packages.backend.jobs.ai_runner")


def test_ai_actor_message_schema_contains_only_job_id() -> None:
    job_id = uuid4()

    assert JobMessage(job_id=job_id).model_dump() == {"job_id": job_id}
    with pytest.raises(ValidationError):
        JobMessage.model_validate({"job_id": str(job_id), "input_context": {"secret": "不得投递"}})


def test_runner_and_scheduler_defaults_freeze_lease_heartbeat_and_scan_intervals() -> None:
    runner = _runner()
    scheduler = import_module("apps.worker.scheduler")
    parameters = signature(runner.AiJobRunner).parameters

    assert parameters["lease_seconds"].default == 120
    assert parameters["heartbeat_interval_seconds"].default == 30
    assert scheduler.EXPIRED_LEASE_SCAN_SECONDS == 30


def test_postgres_lease_recovery_and_completion_are_conditional_and_idempotent(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(connection, dependencies)
        _insert_result(connection, _result_values(dependencies, job_id))
        connection.execute(
            """UPDATE background_jobs SET execution_status='queued',queued_at=%s
            WHERE kindergarten_id=%s AND id=%s""",
            (now, actor.kindergarten_id, job_id),
        )
        store = _runner().AiJobStore(connection)
        assert store.claim(
            actor.kindergarten_id,
            job_id,
            worker_id="worker-before-crash",
            lease_expires_at=now + timedelta(seconds=120),
        )
        assert not store.claim(
            actor.kindergarten_id,
            job_id,
            worker_id="duplicate-delivery",
            lease_expires_at=now + timedelta(seconds=120),
        )
        connection.execute(
            """UPDATE background_jobs
            SET lease_expires_at=%s,last_heartbeat_at=%s
            WHERE kindergarten_id=%s AND id=%s""",
            (
                now - timedelta(seconds=1),
                now - timedelta(seconds=31),
                actor.kindergarten_id,
                job_id,
            ),
        )
        recovered = store.recoverable_job_ids(now=now, limit=100, include_expired=True)
        assert recovered == [job_id]
        assert store.claim(
            actor.kindergarten_id,
            job_id,
            worker_id="worker-after-crash",
            lease_expires_at=now + timedelta(seconds=120),
        )
        assert store.complete_result_once(
            actor.kindergarten_id,
            job_id,
            worker_id="worker-after-crash",
            output_content={"objectives": ["目标一。", "目标二。", "目标三。"]},
            output_sha256="4" * 64,
        )
        assert not store.complete_result_once(
            actor.kindergarten_id,
            job_id,
            worker_id="late-duplicate",
            output_content={"objectives": ["不得覆盖。", "不得覆盖。", "不得覆盖。"]},
            output_sha256="5" * 64,
        )
        row = connection.execute(
            """SELECT j.execution_status,j.attempt_count,j.lease_owner,j.lease_expires_at,
                      r.output_content,r.output_sha256
            FROM background_jobs j
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            WHERE j.kindergarten_id=%s AND j.id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone()

    assert row is not None
    assert row[0] == "awaiting_confirmation"
    assert row[1] == 2
    assert row[2:4] == (None, None)
    assert row[4] == {"objectives": ["目标一。", "目标二。", "目标三。"]}
    assert row[5] == "4" * 64


def test_scheduler_tick_redispatches_expired_ai_job_and_ignores_batch_parent(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    dependencies = _provision_dependencies(client, actor)
    now = datetime.now(UTC)
    dispatched: list[UUID] = []
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        job_id = _insert_job(connection, dependencies)
        _insert_result(connection, _result_values(dependencies, job_id))
        connection.execute(
            """UPDATE background_jobs
            SET execution_status='running',attempt_count=1,started_at=%s,
                lease_owner='crashed-worker',lease_expires_at=%s,last_heartbeat_at=%s
            WHERE kindergarten_id=%s AND id=%s""",
            (
                now - timedelta(seconds=90),
                now - timedelta(seconds=1),
                now - timedelta(seconds=31),
                actor.kindergarten_id,
                job_id,
            ),
        )
        batch_id = uuid4()
        connection.execute(
            """INSERT INTO background_jobs
            (id,kindergarten_id,job_type,execution_status,plan_id,attempt_count,max_attempts,
             requested_by,trace_id)
            VALUES (%s,%s,'ai.batch',NULL,%s,NULL,NULL,%s,%s)""",
            (
                batch_id,
                actor.kindergarten_id,
                dependencies.plan_id,
                actor.user_id,
                uuid4(),
            ),
        )
        store = _runner().AiJobStore(connection)
        scheduler = import_module("apps.worker.scheduler")

        recovered = scheduler.run_ai_recovery_scan(
            store=store,
            dispatch=dispatched.append,
            now=now,
            limit=100,
        )
        states = connection.execute(
            """SELECT id,execution_status FROM background_jobs
            WHERE kindergarten_id=%s AND id=ANY(%s)
            ORDER BY id""",
            (actor.kindergarten_id, [job_id, batch_id]),
        ).fetchall()

    assert scheduler.EXPIRED_LEASE_SCAN_SECONDS == 30
    assert recovered == 1
    assert dispatched == [job_id]
    assert (batch_id, None) in states
    assert (job_id, "queued") in states


@dataclass
class StatefulStore:
    kindergarten_id: UUID = field(default_factory=uuid4)
    job_id: UUID = field(default_factory=uuid4)
    profile_id: UUID = field(default_factory=uuid4)
    requested_by: UUID = field(default_factory=uuid4)
    claimed: bool = False
    terminal: bool = False
    heartbeats: int = 0
    successes: list[dict[str, object]] = field(default_factory=list)
    failures: list[tuple[str, str]] = field(default_factory=list)
    heartbeat_seen: Event = field(default_factory=Event, repr=False)

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
        if self.claimed or self.terminal:
            return False
        self.claimed = True
        return True

    def load_execution_context(self, kindergarten_id: UUID, job_id: UUID) -> Any:
        assert kindergarten_id == self.kindergarten_id
        assert job_id == self.job_id
        return SimpleNamespace(
            kindergarten_id=self.kindergarten_id,
            job_id=self.job_id,
            requested_by=self.requested_by,
            model_profile_id=self.profile_id,
            model_name_snapshot="structured-test-model",
            input_context={"teacher_context": "冻结输入"},
            prompt_content="补充：{{teacher_context}}",
            result_schema_code="prompt.morning_activity.v1",
            result_schema_version=1,
        )

    def get_current_profile(self, kindergarten_id: UUID, profile_id: UUID) -> Any:
        assert kindergarten_id == self.kindergarten_id
        assert profile_id == self.profile_id
        return SimpleNamespace(
            kindergarten_id=self.kindergarten_id,
            profile_id=self.profile_id,
            api_base_url="https://ai.example.test/v1",
            model_name="structured-test-model",
            capability_codes=frozenset({"text", "structured_output"}),
            max_concurrency=2,
            rate_limit_per_minute=None,
            is_active=True,
            key_envelope=object(),
        )

    def heartbeat(
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
        self.heartbeats += 1
        self.heartbeat_seen.set()
        return True

    def complete_result_once(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        output_content: dict[str, object],
        output_sha256: str,
    ) -> bool:
        del worker_id, output_sha256
        assert kindergarten_id == self.kindergarten_id
        assert job_id == self.job_id
        if self.terminal:
            return False
        self.successes.append(output_content)
        self.terminal = True
        return True

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
        del worker_id, elapsed_ms
        assert kindergarten_id == self.kindergarten_id
        assert job_id == self.job_id
        self.failures.append((code, summary))
        self.terminal = True


@dataclass
class CountingClient:
    before_return: Callable[[], None] | None = None
    calls: int = 0

    def generate_structured(self, **_kwargs: object) -> dict[str, object]:
        self.calls += 1
        if self.before_return is not None:
            self.before_return()
        return {"objectives": ["目标一。", "目标二。", "目标三。"]}


def _executor(
    module: Any,
    store: StatefulStore,
    client: Any,
    *,
    authorizer: Any | None = None,
    validate_result: Callable[[str, dict[str, object], dict[str, object]], dict[str, object]]
    | None = None,
    **changes: object,
) -> Any:
    return module.AiJobRunner(
        store=store,
        client=client,
        authorizer=authorizer or SimpleNamespace(can_execute=lambda _context: True),
        read_api_key=lambda _profile: "test-key",
        validate_url=lambda value: value,
        validate_result=validate_result or (lambda _code, result, _input: result),
        **changes,
    )


class ScriptedHeartbeatEvent:
    def __init__(self) -> None:
        self.wait_intervals: list[float] = []
        self._stopped = Event()

    def wait(self, timeout: float) -> bool:
        self.wait_intervals.append(timeout)
        if len(self.wait_intervals) == 1:
            return False
        return self._stopped.wait(timeout=1)

    def set(self) -> None:
        self._stopped.set()


def test_duplicate_actor_delivery_calls_model_once_and_default_heartbeat_renews_lease(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _runner()
    store = StatefulStore()
    heartbeat_events: list[ScriptedHeartbeatEvent] = []

    def event_factory() -> ScriptedHeartbeatEvent:
        event = ScriptedHeartbeatEvent()
        heartbeat_events.append(event)
        return event

    def await_heartbeat() -> None:
        assert store.heartbeat_seen.wait(timeout=1)

    monkeypatch.setattr(module, "Event", event_factory)
    client = CountingClient(before_return=await_heartbeat)
    executor = _executor(module, store, client)

    executor.execute(
        store.kindergarten_id,
        store.job_id,
        worker_id="worker-1",
    )
    executor.execute(
        store.kindergarten_id,
        store.job_id,
        worker_id="worker-duplicate",
    )

    assert client.calls == 1
    assert len(store.successes) == 1
    assert store.heartbeats == 1
    assert heartbeat_events[0].wait_intervals[0] == 30


def test_model_profile_concurrency_slot_blocks_third_call_until_release() -> None:
    gate = _runner().AiModelConcurrencyGate()
    profile_id = uuid4()

    assert gate.acquire(profile_id, limit=2, blocking=False)
    assert gate.acquire(profile_id, limit=2, blocking=False)
    assert gate.in_use(profile_id) == 2
    assert not gate.acquire(profile_id, limit=2, blocking=False)
    gate.release(profile_id)
    assert gate.acquire(profile_id, limit=2, blocking=False)
    assert gate.in_use(profile_id) == 2
