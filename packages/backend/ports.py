"""M1 外部边界所需的最小 Protocol。"""

from collections.abc import Mapping
from datetime import date, datetime
from typing import Protocol
from uuid import UUID


class Clock(Protocol):
    def now(self) -> datetime: ...


class WorkdayCalendar(Protocol):
    def is_workday(self, value: date) -> bool | None: ...


class AiClient(Protocol):
    async def generate(self, payload: Mapping[str, object]) -> Mapping[str, object]: ...


class JobBroker(Protocol):
    def enqueue(self, job_id: UUID) -> None: ...


class DependencyCheck(Protocol):
    async def check(self) -> bool: ...
