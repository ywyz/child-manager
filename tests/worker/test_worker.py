"""Worker 自动化测试。

使用 StubBroker 验证 broker 工厂、Scheduler 停止语义和
消息只传 job_id 的边界约束。
"""

import inspect
from threading import Event, Thread
from unittest.mock import patch

import dramatiq
from dramatiq import Message
from dramatiq.brokers.stub import StubBroker

from apps.worker.actors import (
    process_export_job,
    process_generation_job,
    process_retry_job,
)
from apps.worker.broker import build_deterministic_test_broker
from apps.worker.scheduler import Scheduler
from packages.contracts.jobs import WorkerMessage


def test_build_deterministic_test_broker_returns_stub_broker() -> None:
    broker = build_deterministic_test_broker()

    assert isinstance(broker, StubBroker)


def test_stub_broker_can_be_set_as_global() -> None:
    broker = build_deterministic_test_broker()
    dramatiq.set_broker(broker)
    broker.emit_after("process_boot")

    assert dramatiq.get_broker() is broker


def test_scheduler_register_and_tick() -> None:
    scheduler = Scheduler()
    called: list[str] = []

    scheduler.register("cleanup", lambda: called.append("cleanup"))
    scheduler._tick()

    assert called == ["cleanup"]


def test_scheduler_tick_continues_after_callback_exception() -> None:
    scheduler = Scheduler()

    def failing() -> None:
        raise RuntimeError("boom")

    def healthy() -> None:
        called.append("ok")

    called: list[str] = []
    scheduler.register("failing", failing)
    scheduler.register("healthy", healthy)
    scheduler._tick()

    assert called == ["ok"]


def test_scheduler_run_exits_when_stop_event_already_set() -> None:
    stop_event = Event()
    stop_event.set()
    scheduler = Scheduler()

    scheduler.run(stop_event)


def test_scheduler_run_stops_when_event_set_from_another_thread() -> None:
    stop_event = Event()
    scheduler = Scheduler()

    def stop_soon() -> None:
        stop_event.wait(0.05)
        stop_event.set()

    Thread(target=stop_soon, daemon=True).start()
    scheduler.run(stop_event)

    assert stop_event.is_set()


_REAL_ACTORS = [
    process_generation_job,
    process_export_job,
    process_retry_job,
]


def test_real_actors_accept_only_job_id() -> None:
    """真实 actor 函数签名必须只有 job_id 一个参数。"""
    for actor in _REAL_ACTORS:
        fn = actor.fn
        sig = inspect.signature(fn)
        params = [
            p
            for p in sig.parameters.values()
            if p.kind
            not in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            )
        ]
        assert len(params) == 1, f"{fn.__name__} 参数过多: {[p.name for p in params]}"
        assert params[0].name == "job_id"


def test_real_actor_message_envelope_matches_contract() -> None:
    """真实 actor 消息信封必须匹配 WorkerMessage 契约。"""
    broker = build_deterministic_test_broker()
    dramatiq.set_broker(broker)

    for actor in _REAL_ACTORS:
        message = actor.message("test-job-id")
        assert isinstance(message, Message)
        assert message.args == ("test-job-id",)
        assert message.kwargs == {}

        # 验证 WorkerMessage 契约
        envelope = WorkerMessage(job_id=message.args[0])
        assert envelope.job_id == "test-job-id"


def test_worker_message_schema_rejects_extra_fields() -> None:
    """WorkerMessage 不允许额外字段。"""
    from pydantic import ValidationError

    WorkerMessage(job_id="ok")
    with __import__("pytest").raises(ValidationError):
        WorkerMessage(job_id="x", api_key="secret")  # type: ignore


def test_serve_function_accepts_stub_broker_and_stops() -> None:
    from apps.worker.main import serve

    broker = build_deterministic_test_broker()
    stop_event = Event()
    stop_event.set()

    with patch("apps.worker.main.Worker") as mock_worker_class:
        mock_worker = mock_worker_class.return_value
        serve(broker, threads=1, stop_event=stop_event)
        mock_worker.start.assert_called_once()
        mock_worker.stop.assert_called_once()
