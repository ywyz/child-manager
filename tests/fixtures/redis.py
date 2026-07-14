"""零 Redis 消息代理替身。"""

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class FakeJobBroker:
    job_ids: list[UUID] = field(default_factory=list)

    def enqueue(self, job_id: UUID) -> None:
        self.job_ids.append(job_id)
