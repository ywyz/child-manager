"""登录限流：账号失败计数与来源频控。"""

from collections import deque
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol


class _ThrottleBackend(Protocol):
    async def increment(self, key: str, window_seconds: int) -> int: ...

    async def get_count(self, key: str, window_seconds: int) -> int: ...

    async def reset(self, key: str) -> None: ...


class LoginThrottle:
    """登录限流器接口。"""

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
        """记录一次登录失败。"""
        await self._backend.increment(self._account_key(account_key), self._WINDOW_SECONDS)
        await self._backend.increment(self._source_key(source_ip), self._WINDOW_SECONDS)

    async def is_blocked(self, *, account_key: str, source_ip: str) -> bool:
        """判断是否应拦截当前请求。"""
        account_count = await self._backend.get_count(
            self._account_key(account_key), self._WINDOW_SECONDS
        )
        source_count = await self._backend.get_count(
            self._source_key(source_ip), self._WINDOW_SECONDS
        )
        return account_count >= self._ACCOUNT_THRESHOLD or source_count >= self._SOURCE_THRESHOLD

    async def delay_seconds(self, *, account_key: str, source_ip: str) -> int:
        """返回当前应等待的秒数（0 或 1–60）。"""
        if not await self.is_blocked(account_key=account_key, source_ip=source_ip):
            return 0
        account_count = await self._backend.get_count(
            self._account_key(account_key), self._WINDOW_SECONDS
        )
        source_count = await self._backend.get_count(
            self._source_key(source_ip), self._WINDOW_SECONDS
        )
        count = max(account_count, source_count)
        threshold = min(self._ACCOUNT_THRESHOLD, self._SOURCE_THRESHOLD)
        return min(max(2 ** (count - threshold), 1), 60)

    async def record_success(self, *, account_key: str, source_ip: str) -> None:
        """成功登录后清理失败计数。"""
        await self._backend.reset(self._account_key(account_key))
        await self._backend.reset(self._source_key(source_ip))


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
