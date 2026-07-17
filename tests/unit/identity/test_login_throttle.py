import os
from datetime import UTC, datetime, timedelta

import pytest
from redis.asyncio import Redis

from packages.backend.identity.login_throttle import MemoryLoginThrottle, RedisLoginThrottle

NOW = datetime(2026, 7, 17, 1, 0, tzinfo=UTC)


def test_account_delay_starts_at_fifth_failure_and_is_exponential() -> None:
    throttle = MemoryLoginThrottle()
    decisions = [
        throttle.record_failure(account="teacher", source="203.0.113.7", now=NOW) for _ in range(7)
    ]
    assert [decision.delay_seconds for decision in decisions] == [0, 0, 0, 0, 1, 2, 4]


def test_source_is_rate_limited_after_thirty_failures_in_fifteen_minutes() -> None:
    throttle = MemoryLoginThrottle()
    decision = None
    for index in range(31):
        decision = throttle.record_failure(account=f"user-{index}", source="203.0.113.7", now=NOW)
    assert decision is not None and decision.source_limited
    assert throttle.check(account="new-account", source="203.0.113.7", now=NOW).source_limited


def test_window_and_success_reset_account_delay() -> None:
    throttle = MemoryLoginThrottle()
    for _ in range(5):
        throttle.record_failure(account="teacher", source="203.0.113.7", now=NOW)
    throttle.record_success(account="teacher", source="203.0.113.7", now=NOW)
    assert (
        throttle.record_failure(account="teacher", source="203.0.113.7", now=NOW).delay_seconds == 0
    )
    assert (
        throttle.record_failure(
            account="other", source="198.51.100.2", now=NOW + timedelta(minutes=16)
        ).delay_seconds
        == 0
    )


@pytest.mark.asyncio
async def test_redis_throttle_persists_source_limit_across_instances() -> None:
    redis_url = os.environ.get("CHILD_MANAGER_TEST_REDIS_URL")
    if not redis_url:
        pytest.fail("必须设置 CHILD_MANAGER_TEST_REDIS_URL 以验证真实 Redis 登录限流")
    prefix = f"child-manager:test:{os.getpid()}"
    client = Redis.from_url(redis_url)
    try:
        first = RedisLoginThrottle(client, prefix=prefix)
        second = RedisLoginThrottle(client, prefix=prefix)
        for index in range(31):
            await first.record_failure(account=f"user-{index}", source="203.0.113.8", now=NOW)
        decision = await second.check(account="valid-user", source="203.0.113.8", now=NOW)
        assert decision.source_limited
    finally:
        await client.delete(f"{prefix}:source:203.0.113.8")
        await client.aclose()
