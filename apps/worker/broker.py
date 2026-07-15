from dramatiq.broker import Broker
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker


def build_redis_broker(redis_url: str) -> Broker:
    return RedisBroker(url=redis_url)


def build_deterministic_test_broker() -> Broker:
    return StubBroker()
