from collections.abc import Callable
from datetime import UTC, datetime
from threading import Event

import structlog

LOGGER = structlog.get_logger(__name__)


class Scheduler:
    def __init__(self) -> None:
        self._callbacks: list[tuple[str, Callable[[], None]]] = []

    def register(self, name: str, callback: Callable[[], None]) -> None:
        self._callbacks.append((name, callback))

    def run(self, stop_event: Event) -> None:
        LOGGER.info("scheduler_started")
        while not stop_event.is_set():
            stop_event.wait(60)
            if not stop_event.is_set():
                self._tick()

    def _tick(self) -> None:
        now = datetime.now(UTC)
        LOGGER.debug("scheduler_tick", timestamp=now.isoformat())
        for name, callback in self._callbacks:
            try:
                callback()
            except Exception as exc:
                LOGGER.error(
                    "scheduler_callback_failed",
                    callback=name,
                    error_type=type(exc).__name__,
                )
