"""登录限流测试。

T030 规格：
- 账号 5 次/15 分钟后执行 1～60 秒指数延迟（不返回 429）。
- 可信来源 30 次/15 分钟才返回 429 + Retry-After。
- 成功只清账号退避，不清来源级窗口。
"""

import asyncio
import os
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
async def test_redis_backend_lua_script_checks_ttl_not_current_count() -> None:
    """Lua 脚本必须用 TTL==-1 判断是否需要设置 EXPIRE，而非 current==1。

    Codex 第十五轮审阅发现：旧脚本 `if current == 1` 只在新键时设置 TTL，
    无法修复遗留无 TTL 键（current > 1 但 TTL == -1）。修复后脚本必须
    检查 TTL，TTL==-1 时无论 current 是多少都设置 EXPIRE。
    """
    redis_client = AsyncMock()
    redis_client.eval = AsyncMock(return_value=1)
    backend = RedisThrottleBackend(redis_client)
    await backend.increment("login:source:1.2.3.4", 900)
    script = redis_client.eval.call_args.args[0]
    # 脚本必须检查 TTL，且 TTL==-1 时设置 EXPIRE
    assert "TTL" in script or "ttl" in script
    assert "== -1" in script
    # 不得使用 current == 1 判断（无法修复遗留无 TTL 键）
    assert "current == 1" not in script


@pytest.mark.asyncio
async def test_redis_backend_repairs_legacy_no_ttl_key() -> None:
    """Lua 脚本必须修复遗留无 TTL 键，确保任何被计数的键都一定有过期时间。

    Codex 第十五轮审阅发现：旧脚本只在 current==1 时设置 TTL，遗留无 TTL
    键（由旧版本代码或人工操作留下）INCR 后 current>1，脚本不会设置 TTL，
    键仍然永久存在。修复后脚本必须检查 TTL，TTL==-1 时设置 EXPIRE。
    """
    redis_client = AsyncMock()
    # 模拟遗留键：INCR 返回 5（current > 1），但 TTL == -1（无 TTL）
    redis_client.eval = AsyncMock(return_value=5)
    backend = RedisThrottleBackend(redis_client)
    count = await backend.increment("login:source:1.2.3.4", 900)
    assert count == 5
    script = redis_client.eval.call_args.args[0]
    # 脚本必须包含 TTL 检查，能在 current > 1 时也设置 EXPIRE
    assert "TTL" in script or "ttl" in script
    assert "== -1" in script
    assert "EXPIRE" in script


@pytest.mark.asyncio
async def test_redis_backend_get_count_uses_atomic_lua_script() -> None:
    """get_count 必须用单条 Lua 脚本原子读取并修复缺失 TTL。

    Codex 第十六轮审阅发现：旧 get_count 用裸 GET 读取计数，不修复 TTL。
    is_source_blocked 读取遗留无 TTL 键后直接 429，永远不进入 increment 的
    补 TTL Lua，导致来源被永久锁定。修复后 get_count 必须用 Lua 原子读取
    并在 TTL==-1 时设置 EXPIRE。
    """
    redis_client = AsyncMock()
    redis_client.eval = AsyncMock(return_value=30)
    backend = RedisThrottleBackend(redis_client)
    count = await backend.get_count("login:source:1.2.3.4", 900)
    assert count == 30
    # 必须调用 eval（Lua 脚本），不得调用裸 get
    assert redis_client.eval.await_count == 1
    redis_client.get.assert_not_called()
    script = redis_client.eval.call_args.args[0]
    assert "GET" in script
    assert "TTL" in script or "ttl" in script
    assert "== -1" in script
    assert "EXPIRE" in script


@pytest.mark.asyncio
async def test_redis_backend_get_count_returns_zero_for_missing_key() -> None:
    """键不存在时 get_count 必须返回 0，不触发 TTL 修复。"""
    redis_client = AsyncMock()
    # Lua 脚本对不存在的键返回 0
    redis_client.eval = AsyncMock(return_value=0)
    backend = RedisThrottleBackend(redis_client)
    count = await backend.get_count("login:source:missing", 900)
    assert count == 0


@pytest.mark.asyncio
async def test_in_memory_backend_fixed_window_semantics_matches_redis() -> None:
    """内存替身必须与 Redis 后端语义等价（自首次请求起的固定窗口）。

    T030 要求“确定性替身”语义等价。Codex 第十五轮审阅发现：旧内存版按
    epoch 边界对齐窗口，与 Redis 的“自首次 INCR 时刻起”语义不等价。
    修复后内存版必须采用“自首次 increment 时刻起的固定窗口”：首次 increment
    记录 window_start=now，窗口内后续 increment 只递增，窗口过期后下次
    increment 创建新窗口。

    本测试通过冻结时间验证：
    1. 首次 increment 在 t0 创建窗口，计数为 1；
    2. t0 + window_seconds - 1（窗口内）increment 计数递增为 2；
    3. t0 + window_seconds（窗口刚过期）increment 创建新窗口，计数为 1。
    """
    from datetime import UTC, datetime, timedelta
    from unittest.mock import patch

    backend = InMemoryThrottleBackend()
    t0 = datetime(2026, 7, 19, 12, 0, 0, tzinfo=UTC)
    window_seconds = 900  # 15 分钟

    # 首次 increment 在 t0 创建窗口
    with patch.object(backend, "_now", return_value=t0):
        count1 = await backend.increment("key", window_seconds)
    assert count1 == 1
    stored_start, stored_count = backend.storage["key"]
    assert stored_start == t0
    assert stored_count == 1

    # t0 + 899s（窗口内）increment 计数递增为 2，window_start 不变
    t1 = t0 + timedelta(seconds=window_seconds - 1)
    with patch.object(backend, "_now", return_value=t1):
        count2 = await backend.increment("key", window_seconds)
    assert count2 == 2
    assert backend.storage["key"][0] == t0  # window_start 不变

    # t0 + 900s（窗口刚过期）increment 创建新窗口，计数为 1
    t2 = t0 + timedelta(seconds=window_seconds)
    with patch.object(backend, "_now", return_value=t2):
        count3 = await backend.increment("key", window_seconds)
    assert count3 == 1
    assert backend.storage["key"][0] == t2  # 新窗口起点

    # get_count 在窗口过期后返回 0
    t3 = t2 + timedelta(seconds=window_seconds + 1)
    with patch.object(backend, "_now", return_value=t3):
        assert await backend.get_count("key", window_seconds) == 0


# ---------------------------------------------------------------------------
# 真实 Redis 集成测试
#
# Codex 第十六轮审阅要求：补真实 Redis 的 count>=30 无 TTL 调用链 RED 测试。
# 这类测试无法用 mock 复现 Lua 脚本在 Redis 服务端的原子语义，必须连真实
# Redis。通过 ``CHILD_MANAGER_TEST_REDIS_URL`` 显式启用；未配置时跳过，不
# 影响标准门禁在无 Redis 环境下的可用性。
# ---------------------------------------------------------------------------

_REDIS_URL = os.environ.get("CHILD_MANAGER_TEST_REDIS_URL", "")


def _redis_available() -> bool:
    if not _REDIS_URL:
        return False
    try:
        from redis.asyncio import Redis

        async def _ping() -> bool:
            client = Redis.from_url(_REDIS_URL)
            try:
                return bool(await client.ping())
            finally:
                await client.aclose()

        return bool(asyncio.run(_ping()))
    except Exception:
        return False


_SKIP_REASON = "需要 CHILD_MANAGER_TEST_REDIS_URL 指向可用 Redis 才运行"


@pytest.mark.skipif(not _redis_available(), reason=_SKIP_REASON)
@pytest.mark.asyncio
async def test_real_redis_get_count_repairs_legacy_no_ttl_key() -> None:
    """真实 Redis：预置 count=30/TTL=-1 的遗留键，get_count 必须原子补 TTL。

    Codex 第十六轮探针复现：预置 count=30/TTL=-1 后调用 is_source_blocked，
    结果 ``blocked=True, ttl_after_check=-1``--键永久锁定来源。修复后
    get_count 的 Lua 脚本必须在读取时补 TTL，使键最终能过期解锁。
    """
    import secrets

    from redis.asyncio import Redis

    client = Redis.from_url(_REDIS_URL)
    # 唯一来源 IP 避免与其他测试或并行运行冲突。
    source_ip = f"10.99.99.{secrets.token_hex(2)}"
    key = f"login:source:{source_ip}"
    try:
        # 预置遗留键：count=30，无 TTL（PERSIST 确保 TTL=-1）。
        await client.set(key, 30)
        await client.persist(key)
        assert await client.ttl(key) == -1, "预置键应有 TTL==-1"

        backend = RedisThrottleBackend(client)
        throttle = LoginThrottle(backend)

        # is_source_blocked 调用 get_count，应返回 True 并修复 TTL。
        blocked = await throttle.is_source_blocked(source_ip=source_ip)
        assert blocked is True

        # 关键断言：TTL 必须不再是 -1（已被 get_count 的 Lua 原子修复）。
        ttl_after = await client.ttl(key)
        assert ttl_after > 0, f"遗留无 TTL 键应被修复，实际 TTL={ttl_after}"
    finally:
        await client.delete(key)
        await client.aclose()
