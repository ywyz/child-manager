import argparse
import os
from threading import Event, Thread

import dramatiq
from dramatiq import Worker
from dramatiq.broker import Broker

from apps.worker.broker import build_redis_broker
from apps.worker.scheduler import Scheduler


def serve(
    broker: Broker,
    *,
    threads: int,
    stop_event: Event | None = None,
) -> None:
    dramatiq.set_broker(broker)
    __import__("apps.worker.actors")

    worker = Worker(broker, worker_threads=threads)
    worker.start()

    scheduler = Scheduler()
    scheduler_thread = Thread(
        target=scheduler.run,
        args=(stop_event or Event(),),
    )
    scheduler_thread.daemon = True
    scheduler_thread.start()

    shutdown = stop_event or Event()
    try:
        shutdown.wait()
    except KeyboardInterrupt:
        pass
    finally:
        worker.stop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="启动 Child Manager Worker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--redis-url",
        default=os.environ.get("CHILD_MANAGER_REDIS_URL"),
    )
    parser.add_argument("--threads", default=4, type=int, help="工作线程数,首期默认 4")
    args = parser.parse_args()
    if not args.redis_url:
        parser.error("必须设置 CHILD_MANAGER_REDIS_URL 或显式传入 --redis-url")
    if args.threads <= 0:
        parser.error("--threads 必须大于 0")

    broker = build_redis_broker(args.redis_url)
    serve(broker, threads=args.threads)


if __name__ == "__main__":
    main()
