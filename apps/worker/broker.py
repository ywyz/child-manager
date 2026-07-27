"""生产 Redis 与确定性测试消息代理装配。"""

from typing import Any

from dramatiq.broker import Broker
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker


class RedisJobDispatcher:
    """向已注册 actor 投递唯一的 job_id。"""

    def __init__(self, actor: Any) -> None:
        self.actor = actor

    def dispatch(self, job_id: object) -> None:
        self.actor.send(str(job_id))


def build_redis_broker(redis_url: str) -> Broker:
    return RedisBroker(url=redis_url)


def build_test_broker() -> StubBroker:
    broker = StubBroker()
    broker.emit_after("process_boot")
    return broker
