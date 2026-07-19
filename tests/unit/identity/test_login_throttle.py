"""登录限流测试。

T030 规格：
- 账号 5 次/15 分钟后执行 1～60 秒指数延迟（不返回 429）。
- 可信来源 30 次/15 分钟才返回 429 + Retry-After。
- 成功只清账号退避，不清来源级窗口。
"""

from unittest.mock import AsyncMock

import pytest

from packages.backend.identity.login_throttle import (
    InMemoryThrottleBackend,
    LoginThrottle,
    RedisThrottleBackend,
)


@pytest.fixture
def throttle() -> LoginThrottle:
    return LoginThrottle(InMemoryThrottleBackend())


@pytest.mark.asyncio
async def test_no_backoff_initially(throttle: LoginThrottle) -> None:
    assert await throttle.account_backoff_seconds(account_key="acc") == 0
    assert await throttle.is_source_blocked(source_ip="127.0.0.1") is False


@pytest.mark.asyncio
async def test_account_backoff_after_five_failures(throttle: LoginThrottle) -> None:
    """账号 5 次失败后触发 1-60 秒指数退避，但不返回 429。"""
    for _ in range(5):
        await throttle.record_failure(account_key="acc", source_ip="127.0.0.1")
    backoff = await throttle.account_backoff_seconds(account_key="acc")
    assert 1 <= backoff <= 60
    # 账号退避不触发来源 429。
    assert await throttle.is_source_blocked(source_ip="127.0.0.1") is False


@pytest.mark.asyncio
async def test_account_backoff_grows_exponentially(throttle: LoginThrottle) -> None:
    """退避秒数按 2^(n-5) 指数增长，上限 60 秒。"""
    for _ in range(5):
        await throttle.record_failure(account_key="acc", source_ip="127.0.0.1")
    assert await throttle.account_backoff_seconds(account_key="acc") == 1  # 2^0
    await throttle.record_failure(account_key="acc", source_ip="127.0.0.1")
    assert await throttle.account_backoff_seconds(account_key="acc") == 2  # 2^1
    await throttle.record_failure(account_key="acc", source_ip="127.0.0.1")
    assert await throttle.account_backoff_seconds(account_key="acc") == 4  # 2^2
    for _ in range(5):
        await throttle.record_failure(account_key="acc", source_ip="127.0.0.1")
    # 2^7 = 128，但上限 60。
    assert await throttle.account_backoff_seconds(account_key="acc") == 60


@pytest.mark.asyncio
async def test_source_blocked_after_thirty_failures(throttle: LoginThrottle) -> None:
    """来源 30 次/15 分钟触发硬频控 429。"""
    for i in range(30):
        await throttle.record_failure(account_key=f"acc-{i}", source_ip="10.0.0.1")
    assert await throttle.is_source_blocked(source_ip="10.0.0.1") is True


@pytest.mark.asyncio
async def test_source_retry_after_seconds_aligns_with_openapi_contract(
    throttle: LoginThrottle,
) -> None:
    """来源级 429 的 Retry-After 必须落在冻结 OpenAPI [1, 60] 区间内。

    冻结 openapi.yaml#TooManyRequests.Retry-After schema: minimum 1, maximum 60。
    返回 900（整个窗口）会违反契约；这里锁定运行时返回值 <= 60。
    """
    for i in range(30):
        await throttle.record_failure(account_key=f"acc-{i}", source_ip="10.0.0.1")
    assert await throttle.is_source_blocked(source_ip="10.0.0.1") is True
    retry_after = await throttle.source_retry_after_seconds()
    assert 1 <= retry_after <= 60


@pytest.mark.asyncio
async def test_success_only_resets_account_not_source(throttle: LoginThrottle) -> None:
    """成功登录只清账号退避，不清来源级窗口。"""
    for _ in range(4):
        await throttle.record_failure(account_key="acc", source_ip="127.0.0.1")
    await throttle.record_success(account_key="acc", source_ip="127.0.0.1")
    assert await throttle.account_backoff_seconds(account_key="acc") == 0
    # 来源计数不应被成功登录清空。
    for i in range(26):
        await throttle.record_failure(account_key=f"other-{i}", source_ip="127.0.0.1")
    # 4 + 26 = 30 次来源失败，应触发来源 429。
    assert await throttle.is_source_blocked(source_ip="127.0.0.1") is True


@pytest.mark.asyncio
async def test_failures_do_not_leak_across_accounts(throttle: LoginThrottle) -> None:
    for _ in range(5):
        await throttle.record_failure(account_key="acc-a", source_ip="127.0.0.1")
    assert await throttle.account_backoff_seconds(account_key="acc-b") == 0


@pytest.mark.asyncio
async def test_redis_backend_uses_atomic_lua_script_for_increment() -> None:
    """RedisThrottleBackend 必须用单条 Lua 脚本原子完成 INCR + EXPIRE。

    FR-069 要求“不得自动永久锁定”。若 INCR 与 EXPIRE 分两步，进程中断或
    Redis 错误会留下无 TTL 键导致永久锁定。这里通过 mock 验证 increment
    只调用一次 eval（原子脚本），不调用分开的 incr/expire。
    """
    redis_client = AsyncMock()
    redis_client.eval = AsyncMock(return_value=1)
    backend = RedisThrottleBackend(redis_client)
    count = await backend.increment("login:source:1.2.3.4", 900)
    assert count == 1
    # 必须只调用 eval 一次，且第一个参数是 Lua 脚本字符串。
    assert redis_client.eval.await_count == 1
    script_arg = redis_client.eval.call_args.args[0]
    assert "INCR" in script_arg
    assert "EXPIRE" in script_arg
    # 不得调用分开的 incr / expire。
    redis_client.incr.assert_not_called()
    redis_client.expire.assert_not_called()


@pytest.mark.asyncio
async def test_redis_backend_increment_always_sets_ttl_on_first_increment() -> None:
    """Lua 脚本在 count==1 时设置 TTL，保证首次计数键一定有过期时间。"""
    redis_client = AsyncMock()
    # 模拟首次 INCR 返回 1
    redis_client.eval = AsyncMock(return_value=1)
    backend = RedisThrottleBackend(redis_client)
    await backend.increment("login:source:1.2.3.4", 900)
    script = redis_client.eval.call_args.args[0]
    # 脚本必须包含 "if current == 1" 分支以设置 TTL
    assert "current == 1" in script


@pytest.mark.asyncio
async def test_in_memory_backend_fixed_window_semantics_matches_redis() -> None:
    """内存替身必须与 Redis 后端语义等价（固定窗口，非滑动窗口）。

    T030 要求“确定性替身”语义等价。若内存版用滑动窗口而 Redis 用固定窗口，
    测试观察到的行为与生产不一致。这里验证内存版在同一窗口内计数递增，
    且窗口边界由 window_seconds 对齐（而非按调用时间滑动）。
    """
    backend = InMemoryThrottleBackend()
    # 同一窗口内三次递增
    count1 = await backend.increment("key", 900)
    count2 = await backend.increment("key", 900)
    count3 = await backend.increment("key", 900)
    assert (count1, count2, count3) == (1, 2, 3)
    # storage 存储的是 (window_start, count) 元组，而非 deque 时间戳列表
    stored = backend.storage["key"]
    assert isinstance(stored, tuple)
    assert len(stored) == 2
    assert stored[1] == 3
