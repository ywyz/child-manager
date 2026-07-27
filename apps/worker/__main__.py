"""Dramatiq Worker 本地入口。"""

import argparse
import logging
import os
from threading import Event, Thread
from time import monotonic
from uuid import UUID

import dramatiq
from dramatiq import Worker
from dramatiq.broker import Broker

from apps.worker.actors import (
    build_prompt_test_executor,
    recover_prompt_test_jobs,
    register_actors,
)
from apps.worker.broker import build_redis_broker
from packages.backend.jobs.service import PromptTestExecutor
from packages.backend.observability import configure_logging

DEFAULT_THREADS = 4
RECOVERY_INTERVAL_SECONDS = 15
EXPIRED_SCAN_INTERVAL_SECONDS = 30
logger = logging.getLogger(__name__)


def serve(
    broker: Broker,
    *,
    threads: int,
    stop_event: Event | None = None,
    executor: PromptTestExecutor | None = None,
) -> None:
    """持续消费消息，直到收到显式停止信号。"""

    if executor is None and stop_event is None:
        executor = build_prompt_test_executor()
    dramatiq.set_broker(broker)
    actors = register_actors(broker, executor=executor)
    worker = Worker(broker, worker_threads=threads)
    worker.start()
    shutdown = stop_event or Event()
    recovery_thread: Thread | None = None
    if executor is not None:
        prompt_actor = actors[0]

        def recover() -> None:
            def dispatch(job_id: UUID) -> None:
                prompt_actor.send(str(job_id))

            last_expired_scan = float("-inf")
            while not shutdown.is_set():
                current = monotonic()
                include_expired = current - last_expired_scan >= EXPIRED_SCAN_INTERVAL_SECONDS
                try:
                    recover_prompt_test_jobs(
                        executor.store,
                        dispatch=dispatch,
                        include_expired=include_expired,
                    )
                    if include_expired:
                        last_expired_scan = current
                except Exception:
                    logger.error("提示词测试恢复扫描失败")
                shutdown.wait(RECOVERY_INTERVAL_SECONDS)

        recovery_thread = Thread(target=recover, name="prompt-test-recovery", daemon=True)
        recovery_thread.start()
    try:
        shutdown.wait()
    except KeyboardInterrupt:
        pass
    finally:
        shutdown.set()
        if recovery_thread is not None:
            recovery_thread.join(timeout=2)
        worker.stop()


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(
        description="启动 Child Manager Worker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--redis-url",
        default=os.environ.get("CHILD_MANAGER_REDIS_URL"),
    )
    parser.add_argument(
        "--threads", default=DEFAULT_THREADS, type=int, help="工作线程数，首期默认 4"
    )
    args = parser.parse_args()
    if not args.redis_url:
        parser.error("必须设置 CHILD_MANAGER_REDIS_URL 或显式传入 --redis-url")
    if args.threads <= 0:
        parser.error("--threads 必须大于 0")

    broker = build_redis_broker(args.redis_url)
    serve(broker, threads=args.threads)


if __name__ == "__main__":
    main()
