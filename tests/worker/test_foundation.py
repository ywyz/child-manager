"""Worker 最小消息与测试代理。"""

from threading import Event, Thread
from uuid import UUID

import pytest

from apps.worker import __main__ as worker_main
from apps.worker.__main__ import serve
from apps.worker.actors import register_actors
from apps.worker.broker import build_test_broker
from packages.contracts.jobs import JobMessage


def test_job_message_only_contains_job_id() -> None:
    message = JobMessage(job_id=UUID("01900000-0000-7000-8000-000000000001"))

    assert message.model_dump(mode="json") == {"job_id": "01900000-0000-7000-8000-000000000001"}
    assert set(JobMessage.model_fields) == {"job_id"}


def test_test_broker_registers_minimal_actor_without_redis() -> None:
    broker = build_test_broker()

    actors = register_actors(broker)

    assert [actor.actor_name for actor in actors] == ["load_job"]


def test_worker_keeps_running_until_stop_is_requested() -> None:
    broker = build_test_broker()
    stop_event = Event()
    worker_thread = Thread(
        target=serve,
        kwargs={"broker": broker, "threads": 1, "stop_event": stop_event},
        daemon=True,
    )

    worker_thread.start()
    assert stop_event.wait(0.05) is False
    assert worker_thread.is_alive()

    stop_event.set()
    worker_thread.join(timeout=2)
    assert worker_thread.is_alive() is False


def test_worker_uses_profile_redis_url_by_default(monkeypatch) -> None:
    captured: dict[str, str] = {}

    monkeypatch.setenv("CHILD_MANAGER_REDIS_URL", "redis://127.0.0.1:16379/0")
    monkeypatch.setattr(
        worker_main,
        "build_redis_broker",
        lambda redis_url: captured.setdefault("redis_url", redis_url),
    )
    monkeypatch.setattr(worker_main, "serve", lambda broker, *, threads: None)
    monkeypatch.setattr("sys.argv", ["python -m apps.worker"])

    worker_main.main()

    assert captured == {"redis_url": "redis://127.0.0.1:16379/0"}


def test_worker_rejects_missing_profile_redis_url(monkeypatch) -> None:
    monkeypatch.delenv("CHILD_MANAGER_REDIS_URL", raising=False)
    monkeypatch.setattr("sys.argv", ["python -m apps.worker"])

    with pytest.raises(SystemExit) as raised:
        worker_main.main()

    assert raised.value.code == 2


def test_worker_rejects_non_positive_thread_count(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv", ["python -m apps.worker", "--redis-url", "redis://localhost", "--threads", "0"]
    )

    with pytest.raises(SystemExit) as raised:
        worker_main.main()

    assert raised.value.code == 2
