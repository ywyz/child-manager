"""仅投递 job_id 的提示词测试分发边界。"""

from __future__ import annotations

from uuid import UUID

from dramatiq import Message
from dramatiq.broker import Broker
from dramatiq.brokers.redis import RedisBroker


class RedisJobDispatcher:
    def __init__(self, broker: Broker, *, actor_name: str = "prompt_test") -> None:
        self.broker = broker
        self.actor_name = actor_name

    @classmethod
    def from_url(cls, redis_url: str) -> RedisJobDispatcher:
        return cls(RedisBroker(url=redis_url))

    def dispatch(self, job_id: UUID) -> None:
        self.broker.enqueue(
            Message(
                queue_name="default",
                actor_name=self.actor_name,
                args=(str(job_id),),
                kwargs={},
                options={},
            )
        )
