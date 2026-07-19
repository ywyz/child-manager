"""登录限流：账号失败计数指数退避与来源级硬频控。

T030 规格：
- 账号 5 次/15 分钟后执行 1～60 秒指数延迟（不返回 429，阻塞请求）。
- 可信来源 30 次/15 分钟才返回 429 + Retry-After。
- 失败计数持续演进；成功只清账号退避，不清来源级窗口。
"""

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
    # 冻结 openapi.yaml#TooManyRequests.Retry-After maximum: 60；来源级 429
    # 必须返回 1～60 秒，不得返回整个窗口（900 秒）。
    _SOURCE_RETRY_AFTER_MAX = 60

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
        """来源被硬频控时的 Retry-After 秒数。

        冻结 OpenAPI 契约规定 Retry-After ∈ [1, 60]；返回整个窗口（900 秒）
        会违反契约。这里返回契约上限 60，既保证客户端有明确退避指示，又不
        超出冻结 schema 允许范围。
        """
        return self._SOURCE_RETRY_AFTER_MAX

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
    """用于单元测试的确定性内存后端，与 Redis 后端窗口语义等价。

    T030 要求“确定性替身”，替身语义必须与生产 Redis 后端等价。
    RedisThrottleBackend 的窗口语义是“自首次 INCR 时刻起的固定窗口”：
    首次 INCR 时设置 EXPIRE=window_seconds，窗口内后续 INCR 只递增不续期，
    键过期后下次 INCR 创建新窗口。本类采用完全相同的语义：首次 increment
    记录 window_start=now，窗口内后续 increment 只递增，窗口过期后下次
    increment 创建新窗口。

    之前的实现按 epoch 边界对齐窗口（window_start = epoch // window_seconds
    * window_seconds），与 Redis 的“自首次请求起”语义不等价：同一时刻首次
    请求，Redis 窗口会在 now+window_seconds 过期，而 epoch 对齐窗口会在
    下一个 epoch 边界过期，两者可能相差最多 window_seconds 秒。
    """

    def __init__(self) -> None:
        # 每个键维护 (window_start, count) 固定窗口元组。
        self.storage: dict[str, tuple[datetime, int]] = {}

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def _is_within_window(self, window_start: datetime, window_seconds: int) -> bool:
        """判断当前时刻是否仍在窗口内（与 Redis TTL 语义等价）。"""
        return self._now() < window_start + timedelta(seconds=window_seconds)

    async def increment(self, key: str, window_seconds: int) -> int:
        if key in self.storage:
            window_start, count = self.storage[key]
            if self._is_within_window(window_start, window_seconds):
                count += 1
                self.storage[key] = (window_start, count)
                return count
        # 新窗口：从当前时刻开始（与 Redis 首次 INCR 设置 EXPIRE 等价）。
        self.storage[key] = (self._now(), 1)
        return 1

    async def get_count(self, key: str, window_seconds: int) -> int:
        if key in self.storage:
            window_start, count = self.storage[key]
            if self._is_within_window(window_start, window_seconds):
                return count
        return 0

    async def reset(self, key: str) -> None:
        self.storage.pop(key, None)


class RedisThrottleBackend:
    """基于 Redis 的限流后端。

    使用单条 Lua 脚本原子完成 INCR + EXPIRE，避免在两步之间进程中断或
    Redis 错误留下无 TTL 键导致 FR-069“不得自动永久锁定”被违反。
    与 InMemoryThrottleBackend 一样采用“自首次请求起的固定窗口”语义：
    首次 INCR 时设置 TTL=window_seconds，窗口内后续 INCR 只递增不续期。

    Lua 脚本还修复遗留无 TTL 键：如果 INCR 后发现键无 TTL（TTL == -1，
    可能由旧版本代码或人工操作留下），立即设置 EXPIRE，确保任何被计数的
    键都一定有过期时间。
    """

    # Lua 脚本在 Redis 服务端原子执行：
    # 1. INCR 递增计数；
    # 2. TTL 检查：-1 表示键存在但无 TTL（遗留键），需要设置 EXPIRE；
    #    新键（INCR 后 current==1）的 TTL 也会是 -1，因此统一用 TTL==-1 判断；
    #    -2 表示键不存在（INCR 后不可能），>=0 表示已有 TTL（窗口内后续递增）。
    _INCREMENT_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
local ttl = redis.call('TTL', KEYS[1])
if ttl == -1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""

    def __init__(self, redis_client: Any) -> None:
        self._client = redis_client

    async def increment(self, key: str, window_seconds: int) -> int:
        count = await self._client.eval(self._INCREMENT_SCRIPT, 1, key, window_seconds)
        return int(count)

    async def get_count(self, key: str, window_seconds: int) -> int:
        del window_seconds  # Redis TTL 已体现窗口
        value = await self._client.get(key)
        return int(value) if value is not None else 0

    async def reset(self, key: str) -> None:
        await self._client.delete(key)
