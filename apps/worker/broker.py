from dramatiq.broker import Broker
from dramatiq.brokers.redis import RedisBroker


def build_redis_broker(redis_url: str) -> Broker:
    return RedisBroker(url=redis_url)


def build_test_broker() -> Broker:
    return RedisBroker(url="redis://127.0.0.1:6379/15")
