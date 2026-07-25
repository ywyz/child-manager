"""登录限流的确定性公共接缝。"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256

from redis.asyncio import Redis


@dataclass(frozen=True, slots=True)
class ThrottleDecision:
    delay_seconds: int = 0
    account_limited: bool = False
    source_limited: bool = False
    global_limited: bool = False

    @property
    def limited(self) -> bool:
        return self.account_limited or self.source_limited or self.global_limited


def _digest(*, purpose: str, scope: str, value: str) -> str:
    return sha256(f"child-manager:{purpose}:{scope}:{value}".encode()).hexdigest()


class MemoryLoginThrottle:
    def __init__(
        self,
        *,
        account_failure_limit: int = 5,
        source_failure_limit: int = 30,
        global_failure_limit: int = 100,
        window: timedelta = timedelta(minutes=15),
    ) -> None:
        if min(account_failure_limit, source_failure_limit, global_failure_limit) < 1:
            raise ValueError("登录限流阈值必须为正整数")
        self._account_failure_limit = account_failure_limit
        self._source_failure_limit = source_failure_limit
        self._global_failure_limit = global_failure_limit
        self._window = window
        self._account_failures: dict[tuple[str, str], list[datetime]] = {}
        self._source_failures: dict[tuple[str, str], list[datetime]] = {}
        self._global_failures: dict[str, list[datetime]] = {}

    def _prune(self, values: list[datetime], now: datetime) -> list[datetime]:
        cutoff = now - self._window
        return [value for value in values if value >= cutoff]

    @staticmethod
    def _account_key(*, purpose: str, account: str) -> tuple[str, str]:
        return purpose, _digest(purpose=purpose, scope="account", value=account)

    @staticmethod
    def _source_key(*, purpose: str, source: str) -> tuple[str, str]:
        return purpose, _digest(purpose=purpose, scope="source", value=source)

    def _decision(
        self,
        *,
        account_count: int,
        source_count: int,
        global_count: int,
    ) -> ThrottleDecision:
        delay = (
            0
            if account_count < self._account_failure_limit
            else min(60, 2 ** (account_count - self._account_failure_limit))
        )
        return ThrottleDecision(
            delay_seconds=delay,
            account_limited=account_count >= self._account_failure_limit,
            source_limited=source_count >= self._source_failure_limit,
            global_limited=global_count >= self._global_failure_limit,
        )

    def record_failure(
        self,
        *,
        account: str,
        source: str,
        now: datetime,
        purpose: str = "login",
    ) -> ThrottleDecision:
        account_key = self._account_key(purpose=purpose, account=account)
        source_key = self._source_key(purpose=purpose, source=source)
        account_values = self._prune(self._account_failures.get(account_key, []), now)
        source_values = self._prune(self._source_failures.get(source_key, []), now)
        global_values = self._prune(self._global_failures.get(purpose, []), now)
        account_values.append(now)
        source_values.append(now)
        global_values.append(now)
        self._account_failures[account_key] = account_values
        self._source_failures[source_key] = source_values
        self._global_failures[purpose] = global_values
        return self._decision(
            account_count=len(account_values),
            source_count=len(source_values),
            global_count=len(global_values),
        )

    def check(
        self,
        *,
        account: str,
        source: str,
        now: datetime,
        purpose: str = "login",
    ) -> ThrottleDecision:
        account_key = self._account_key(purpose=purpose, account=account)
        source_key = self._source_key(purpose=purpose, source=source)
        account_values = self._prune(self._account_failures.get(account_key, []), now)
        source_values = self._prune(self._source_failures.get(source_key, []), now)
        global_values = self._prune(self._global_failures.get(purpose, []), now)
        self._account_failures[account_key] = account_values
        self._source_failures[source_key] = source_values
        self._global_failures[purpose] = global_values
        return self._decision(
            account_count=len(account_values),
            source_count=len(source_values),
            global_count=len(global_values),
        )

    def record_success(
        self,
        *,
        account: str,
        source: str,
        now: datetime,
        purpose: str = "login",
    ) -> None:
        del source, now
        self._account_failures.pop(
            self._account_key(purpose=purpose, account=account),
            None,
        )


class RedisLoginThrottle:
    """Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。"""

    def __init__(
        self,
        redis: Redis,
        *,
        prefix: str = "child-manager:login",
        account_failure_limit: int = 5,
        source_failure_limit: int = 30,
        global_failure_limit: int = 100,
        window: timedelta = timedelta(minutes=15),
    ) -> None:
        if min(account_failure_limit, source_failure_limit, global_failure_limit) < 1:
            raise ValueError("登录限流阈值必须为正整数")
        self._redis = redis
        self._prefix = prefix
        self._account_failure_limit = account_failure_limit
        self._source_failure_limit = source_failure_limit
        self._global_failure_limit = global_failure_limit
        self._window_seconds = max(1, int(window.total_seconds()))

    def _keys(self, *, account: str, source: str, purpose: str) -> tuple[str, str, str]:
        account_digest = _digest(purpose=purpose, scope="account", value=account)
        source_digest = _digest(purpose=purpose, scope="source", value=source)
        return (
            f"{self._prefix}:{purpose}:account:{account_digest}",
            f"{self._prefix}:{purpose}:source:{source_digest}",
            f"{self._prefix}:{purpose}:global",
        )

    def _decision(
        self,
        *,
        account_count: int,
        source_count: int,
        global_count: int,
    ) -> ThrottleDecision:
        delay = (
            0
            if account_count < self._account_failure_limit
            else min(60, 2 ** (account_count - self._account_failure_limit))
        )
        return ThrottleDecision(
            delay_seconds=delay,
            account_limited=account_count >= self._account_failure_limit,
            source_limited=source_count >= self._source_failure_limit,
            global_limited=global_count >= self._global_failure_limit,
        )

    async def record_failure(
        self,
        *,
        account: str,
        source: str,
        now: datetime,
        purpose: str = "login",
    ) -> ThrottleDecision:
        timestamp = now.timestamp()
        cutoff = timestamp - self._window_seconds
        account_key, source_key, global_key = self._keys(
            account=account,
            source=source,
            purpose=purpose,
        )
        member = f"{timestamp}:{secrets.token_hex(8)}"
        pipeline = self._redis.pipeline(transaction=True)
        for key in (account_key, source_key, global_key):
            pipeline.zremrangebyscore(key, "-inf", cutoff)
            pipeline.zadd(key, {member: timestamp})
            pipeline.zcard(key)
            pipeline.expire(key, self._window_seconds)
        results = await pipeline.execute()
        return self._decision(
            account_count=int(results[2]),
            source_count=int(results[6]),
            global_count=int(results[10]),
        )

    async def check(
        self,
        *,
        account: str,
        source: str,
        now: datetime,
        purpose: str = "login",
    ) -> ThrottleDecision:
        keys = self._keys(account=account, source=source, purpose=purpose)
        pipeline = self._redis.pipeline(transaction=True)
        for key in keys:
            pipeline.zremrangebyscore(key, "-inf", now.timestamp() - self._window_seconds)
            pipeline.zcard(key)
        results = await pipeline.execute()
        return self._decision(
            account_count=int(results[1]),
            source_count=int(results[3]),
            global_count=int(results[5]),
        )

    async def record_success(
        self,
        *,
        account: str,
        source: str,
        now: datetime,
        purpose: str = "login",
    ) -> None:
        del now
        account_key, _source_key, _global_key = self._keys(
            account=account,
            source=source,
            purpose=purpose,
        )
        await self._redis.delete(account_key)
