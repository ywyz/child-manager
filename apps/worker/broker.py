"""生产 Redis 与确定性测试消息代理装配。"""

from dramatiq.broker import Broker
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker


def build_redis_broker(redis_url: str) -> Broker:
    return RedisBroker(url=redis_url)


def build_test_broker() -> StubBroker:
    broker = StubBroker()
    broker.emit_after("process_boot")
    return broker
