"""Dramatiq Worker 本地入口。"""

import argparse
import logging
import os
from threading import Event, Thread
from time import monotonic
from typing import cast
from uuid import UUID

import dramatiq
from dramatiq import Worker
from dramatiq.broker import Broker

from apps.worker.actors import (
    build_ai_job_runner,
    build_ai_result_repository,
    build_prompt_test_executor,
    build_word_export_runner,
    build_worker_scope_resolver,
    recover_prompt_test_jobs,
    register_actors,
)
from apps.worker.broker import build_redis_broker
from apps.worker.scheduler import (
    AiRecoveryStore,
    AiResultMaintenanceRepository,
    WordRecoveryStore,
    run_ai_recovery_scan,
    run_ai_result_maintenance,
    run_word_recovery_scan,
)
from packages.backend.exports.runner import WordExportRunner
from packages.backend.jobs.ai_results import AiGenerationResultRepository
from packages.backend.jobs.ai_runner import AiJobRunner
from packages.backend.jobs.scope_resolver import WorkerScopeResolver
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
    ai_runner: AiJobRunner | None = None,
    word_runner: WordExportRunner | None = None,
    ai_result_repository: AiGenerationResultRepository | None = None,
    worker_scope_resolver: WorkerScopeResolver | None = None,
) -> None:
    """持续消费消息，直到收到显式停止信号。"""

    if executor is None and stop_event is None:
        executor = build_prompt_test_executor()
    if ai_runner is None and stop_event is None:
        ai_runner = build_ai_job_runner()
    if word_runner is None and stop_event is None:
        word_runner = build_word_export_runner()
    if ai_result_repository is None and stop_event is None:
        ai_result_repository = build_ai_result_repository()
    if worker_scope_resolver is None and stop_event is None:
        worker_scope_resolver = build_worker_scope_resolver()
    dramatiq.set_broker(broker)
    actors = register_actors(
        broker,
        executor=executor,
        ai_runner=ai_runner,
        ai_job_scope_resolver=worker_scope_resolver,
        word_runner=word_runner,
        word_job_scope_resolver=worker_scope_resolver,
    )
    worker = Worker(broker, worker_threads=threads)
    worker.start()
    shutdown = stop_event or Event()
    recovery_thread: Thread | None = None
    if executor is not None or ai_runner is not None or word_runner is not None:
        prompt_actor = actors[0]
        ai_actor = actors[1]
        word_actor = next((actor for actor in actors if actor.actor_name == "word_export"), None)

        def recover() -> None:
            def dispatch_prompt_test(job_id: UUID) -> None:
                prompt_actor.send(str(job_id))

            def dispatch_ai_job(job_id: UUID) -> None:
                ai_actor.send(str(job_id))

            def dispatch_word_export(job_id: UUID) -> None:
                assert word_actor is not None
                word_actor.send(str(job_id))

            last_expired_scan = float("-inf")
            while not shutdown.is_set():
                current = monotonic()
                include_expired = current - last_expired_scan >= EXPIRED_SCAN_INTERVAL_SECONDS
                kindergarten_ids: list[UUID] = []
                if worker_scope_resolver is not None:
                    try:
                        kindergarten_ids = worker_scope_resolver.active_kindergarten_ids()
                    except Exception as exc:
                        logger.error(
                            "Worker 园所范围解析失败",
                            extra={"exception_type": type(exc).__name__},
                        )
                if executor is not None:
                    try:
                        recover_prompt_test_jobs(
                            executor.store,
                            dispatch=dispatch_prompt_test,
                            include_expired=include_expired,
                        )
                    except Exception as exc:
                        logger.error(
                            "提示词测试恢复扫描失败",
                            extra={"exception_type": type(exc).__name__},
                        )
                if ai_runner is not None and worker_scope_resolver is not None:
                    try:
                        run_ai_recovery_scan(
                            store=cast(AiRecoveryStore, ai_runner.store),
                            dispatch=dispatch_ai_job,
                            kindergarten_ids=kindergarten_ids,
                            include_expired=include_expired,
                        )
                    except Exception as exc:
                        logger.error(
                            "AI 任务恢复扫描失败",
                            extra={"exception_type": type(exc).__name__},
                        )
                if (
                    word_runner is not None
                    and worker_scope_resolver is not None
                    and word_actor is not None
                ):
                    try:
                        run_word_recovery_scan(
                            store=cast(WordRecoveryStore, word_runner.store),
                            dispatch=dispatch_word_export,
                            kindergarten_ids=kindergarten_ids,
                            include_expired=include_expired,
                        )
                    except Exception as exc:
                        logger.error(
                            "Word 导出恢复扫描失败",
                            extra={"exception_type": type(exc).__name__},
                        )
                if (
                    include_expired
                    and ai_result_repository is not None
                    and worker_scope_resolver is not None
                ):
                    try:
                        run_ai_result_maintenance(
                            repository=cast(
                                AiResultMaintenanceRepository,
                                ai_result_repository,
                            ),
                            kindergarten_ids=kindergarten_ids,
                        )
                    except Exception as exc:
                        logger.error(
                            "AI 结果维护失败",
                            extra={"exception_type": type(exc).__name__},
                        )
                if include_expired:
                    last_expired_scan = current
                shutdown.wait(RECOVERY_INTERVAL_SECONDS)

        recovery_thread = Thread(target=recover, name="job-recovery", daemon=True)
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
