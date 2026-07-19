"""登录限流测试。

T030 规格：
- 账号 5 次/15 分钟后执行 1～60 秒指数延迟（不返回 429）。
- 可信来源 30 次/15 分钟才返回 429 + Retry-After。
- 成功只清账号退避，不清来源级窗口。
"""

import pytest

from packages.backend.identity.login_throttle import InMemoryThrottleBackend, LoginThrottle


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
    assert await throttle.source_retry_after_seconds() == 900


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
