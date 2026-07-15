"""Worker 自动化测试。

使用 StubBroker 验证 broker 工厂、Scheduler 停止语义和
消息只传 job_id 的边界约束。
"""

from threading import Event, Thread
from unittest.mock import patch

import dramatiq
from dramatiq import Message
from dramatiq.brokers.stub import StubBroker

from apps.worker.broker import build_deterministic_test_broker
from apps.worker.scheduler import Scheduler


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


def test_worker_message_only_carries_job_id() -> None:
    broker = build_deterministic_test_broker()
    dramatiq.set_broker(broker)

    @dramatiq.actor
    def process_job(job_id: str) -> str:
        return job_id

    message = process_job.message("job-abc-123")
    assert isinstance(message, Message)
    assert message.args == ("job-abc-123",)
    assert message.kwargs == {}


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
