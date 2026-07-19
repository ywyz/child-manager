"""登录限流：账号失败计数指数退避与来源级硬频控。

T030 规格：
- 账号 5 次/15 分钟后执行 1～60 秒指数延迟（不返回 429，阻塞请求）。
- 可信来源 30 次/15 分钟才返回 429 + Retry-After。
- 失败计数持续演进；成功只清账号退避，不清来源级窗口。
"""

from collections import deque
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol


class _ThrottleBackend(Protocol):
    async def increment(self, key: str, window_seconds: int) -> int: ...

    async def get_count(self, key: str, window_seconds: int) -> int: ...

    async def reset(self, key: str) -> None: ...


class LoginThrottle:
    """登录限流器：账号级指数退避 + 来源级硬频控。"""

    _ACCOUNT_THRESHOLD = 5
    _SOURCE_THRESHOLD = 30
    _WINDOW_SECONDS = 900  # 15 分钟

    def __init__(self, backend: _ThrottleBackend) -> None:
        self._backend = backend

    def _account_key(self, account_key: str) -> str:
        return f"login:account:{account_key}"

    def _source_key(self, source_ip: str) -> str:
        return f"login:source:{source_ip}"

    async def record_failure(self, *, account_key: str, source_ip: str) -> None:
        """记录一次登录失败；账号与来源计数均递增。"""
        await self._backend.increment(self._account_key(account_key), self._WINDOW_SECONDS)
        await self._backend.increment(self._source_key(source_ip), self._WINDOW_SECONDS)

    async def is_source_blocked(self, *, source_ip: str) -> bool:
        """判断来源是否触发硬频控（>= 30 次/15 分钟），触发时返回 429。"""
        source_count = await self._backend.get_count(
            self._source_key(source_ip), self._WINDOW_SECONDS
        )
        return source_count >= self._SOURCE_THRESHOLD

    async def source_retry_after_seconds(self) -> int:
        """来源被硬频控时的 Retry-After（固定 15 分钟窗口）。"""
        return self._WINDOW_SECONDS

    async def account_backoff_seconds(self, *, account_key: str) -> int:
        """返回账号级指数退避秒数（0 或 1–60）。

        账号失败 >= 5 次后，按 2^(n-5) 指数增长，上限 60 秒。
        退避期间请求被阻塞，但不返回 429，失败计数继续演进。
        """
        account_count = await self._backend.get_count(
            self._account_key(account_key), self._WINDOW_SECONDS
        )
        if account_count < self._ACCOUNT_THRESHOLD:
            return 0
        return min(max(2 ** (account_count - self._ACCOUNT_THRESHOLD), 1), 60)

    async def record_success(self, *, account_key: str, source_ip: str) -> None:
        """成功登录后只清账号退避，不清来源级窗口。

        来源级窗口用于防止单 IP 暴力尝试，一次成功登录不应重置来源计数。
        """
        del source_ip  # 来源计数不清空
        await self._backend.reset(self._account_key(account_key))


class InMemoryThrottleBackend:
    """用于单元测试的确定性内存后端，按滑动窗口维护时间戳。"""

    def __init__(self) -> None:
        self.storage: dict[str, deque[datetime]] = {}

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def _prune(self, key: str, window_seconds: int) -> deque[datetime]:
        cutoff = self._now() - timedelta(seconds=window_seconds)
        queue = self.storage.setdefault(key, deque())
        while queue and queue[0] < cutoff:
            queue.popleft()
        return queue

    async def increment(self, key: str, window_seconds: int) -> int:
        queue = self._prune(key, window_seconds)
        queue.append(self._now())
        return len(queue)

    async def get_count(self, key: str, window_seconds: int) -> int:
        return len(self._prune(key, window_seconds))

    async def reset(self, key: str) -> None:
        self.storage.pop(key, None)


class RedisThrottleBackend:
    """基于 Redis 的限流后端。"""

    def __init__(self, redis_client: Any) -> None:
        self._client = redis_client

    async def increment(self, key: str, window_seconds: int) -> int:
        count = await self._client.incr(key)
        if count == 1:
            await self._client.expire(key, window_seconds)
        return int(count)

    async def get_count(self, key: str, window_seconds: int) -> int:
        del window_seconds  # Redis TTL 已体现窗口
        value = await self._client.get(key)
        return int(value) if value is not None else 0

    async def reset(self, key: str) -> None:
        await self._client.delete(key)
