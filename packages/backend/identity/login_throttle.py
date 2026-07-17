"""登录限流的确定性公共接缝。"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from redis.asyncio import Redis


@dataclass(frozen=True, slots=True)
class ThrottleDecision:
    delay_seconds: int = 0
    source_limited: bool = False


class MemoryLoginThrottle:
    def __init__(self) -> None:
        self._account_failures: dict[str, list[datetime]] = {}
        self._source_failures: dict[str, list[datetime]] = {}

    @staticmethod
    def _prune(values: list[datetime], now: datetime) -> list[datetime]:
        cutoff = now - timedelta(minutes=15)
        return [value for value in values if value >= cutoff]

    def record_failure(self, *, account: str, source: str, now: datetime) -> ThrottleDecision:
        account_values = self._prune(self._account_failures.get(account, []), now)
        source_values = self._prune(self._source_failures.get(source, []), now)
        account_values.append(now)
        source_values.append(now)
        self._account_failures[account] = account_values
        self._source_failures[source] = source_values
        delay = 0 if len(account_values) < 5 else min(60, 2 ** (len(account_values) - 5))
        return ThrottleDecision(delay_seconds=delay, source_limited=len(source_values) > 30)

    def check(self, *, account: str, source: str, now: datetime) -> ThrottleDecision:
        del account
        source_values = self._prune(self._source_failures.get(source, []), now)
        self._source_failures[source] = source_values
        return ThrottleDecision(source_limited=len(source_values) > 30)

    def record_success(self, *, account: str, source: str, now: datetime) -> None:
        self._account_failures.pop(account, None)


class RedisLoginThrottle:
    """Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。"""

    def __init__(self, redis: Redis, *, prefix: str = "child-manager:login") -> None:
        self._redis = redis
        self._prefix = prefix

    async def record_failure(self, *, account: str, source: str, now: datetime) -> ThrottleDecision:
        timestamp = now.timestamp()
        cutoff = timestamp - 15 * 60
        account_key = f"{self._prefix}:account:{account}"
        source_key = f"{self._prefix}:source:{source}"
        member = f"{timestamp}:{secrets.token_hex(8)}"
        pipeline = self._redis.pipeline(transaction=True)
        for key in (account_key, source_key):
            pipeline.zremrangebyscore(key, "-inf", cutoff)
            pipeline.zadd(key, {member: timestamp})
            pipeline.zcard(key)
            pipeline.expire(key, 15 * 60)
        results = await pipeline.execute()
        account_count = int(results[2])
        source_count = int(results[6])
        delay = 0 if account_count < 5 else min(60, 2 ** (account_count - 5))
        return ThrottleDecision(delay_seconds=delay, source_limited=source_count > 30)

    async def check(self, *, account: str, source: str, now: datetime) -> ThrottleDecision:
        del account
        source_key = f"{self._prefix}:source:{source}"
        pipeline = self._redis.pipeline(transaction=True)
        pipeline.zremrangebyscore(source_key, "-inf", now.timestamp() - 15 * 60)
        pipeline.zcard(source_key)
        results = await pipeline.execute()
        return ThrottleDecision(source_limited=int(results[1]) > 30)

    async def record_success(self, *, account: str, source: str, now: datetime) -> None:
        await self._redis.delete(f"{self._prefix}:account:{account}")
