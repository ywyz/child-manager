import dramatiq
from dramatiq.brokers.redis import RedisBroker

from packages.backend.bootstrap.config import settings

broker = RedisBroker(url=settings.resolved_redis_url)
dramatiq.set_broker(broker)


@dramatiq.actor(max_retries=2)
def ai_generation_task(job_id: str):
    pass


@dramatiq.actor(max_retries=2)
def prompt_test_task(job_id: str):
    pass


@dramatiq.actor(max_retries=2)
def word_export_task(job_id: str):
    pass


if __name__ == "__main__":
    dramatiq.runner.Worker(broker).run()
