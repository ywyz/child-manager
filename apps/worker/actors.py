"""只接收 job_id 的 M1 Dramatiq actor。"""

from uuid import UUID

import dramatiq
from dramatiq.actor import Actor
from dramatiq.broker import Broker


def load_job(job_id: str) -> str:
    """验证最小消息；后续里程碑将从 PostgreSQL 加载权威上下文。"""

    return str(UUID(job_id))


def register_actors(broker: Broker) -> tuple[Actor[..., str], ...]:
    actor = dramatiq.actor(actor_name="load_job", broker=broker)(load_job)
    return (actor,)
