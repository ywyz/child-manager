"""仅投递 job_id 的提示词测试分发边界。"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID


class JobDispatcher(Protocol):
    def dispatch(self, job_id: UUID) -> None: ...


class NullDispatcher:
    def dispatch(self, job_id: UUID) -> None:
        del job_id
