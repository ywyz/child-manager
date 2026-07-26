"""只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。"""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

import dramatiq
from dramatiq.actor import Actor
from dramatiq.broker import Broker


def load_job(job_id: str) -> str:
    """验证最小消息；后续里程碑将从 PostgreSQL 加载权威上下文。"""

    return str(UUID(job_id))


class RecoveryStore(Protocol):
    def recoverable_job_ids(self, *, now: datetime, limit: int) -> list[UUID]: ...


def recover_prompt_test_jobs(
    store: RecoveryStore,
    *,
    dispatch: Callable[[UUID], None],
    now: datetime | None = None,
    limit: int = 100,
) -> int:
    """按 PostgreSQL 权威状态重投 pending/过期租约任务。"""

    job_ids = store.recoverable_job_ids(now=now or datetime.now(UTC), limit=limit)
    for job_id in job_ids:
        dispatch(job_id)
    return len(job_ids)


def register_actors(broker: Broker) -> tuple[Actor[..., str], ...]:
    actor = dramatiq.actor(actor_name="load_job", broker=broker)(load_job)
    return (actor,)
