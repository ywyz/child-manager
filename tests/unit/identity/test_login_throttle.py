"""登录限流测试。"""

import pytest

from packages.backend.identity.login_throttle import InMemoryThrottleBackend, LoginThrottle


@pytest.fixture
def throttle() -> LoginThrottle:
    return LoginThrottle(InMemoryThrottleBackend())


@pytest.mark.asyncio
async def test_not_blocked_initially(throttle: LoginThrottle) -> None:
    assert await throttle.is_blocked(account_key="acc", source_ip="127.0.0.1") is False
    assert await throttle.delay_seconds(account_key="acc", source_ip="127.0.0.1") == 0


@pytest.mark.asyncio
async def test_account_blocked_after_five_failures(throttle: LoginThrottle) -> None:
    for _ in range(5):
        await throttle.record_failure(account_key="acc", source_ip="127.0.0.1")
    assert await throttle.is_blocked(account_key="acc", source_ip="127.0.0.1") is True
    delay = await throttle.delay_seconds(account_key="acc", source_ip="127.0.0.1")
    assert 1 <= delay <= 60


@pytest.mark.asyncio
async def test_source_blocked_after_thirty_failures(throttle: LoginThrottle) -> None:
    for i in range(30):
        await throttle.record_failure(account_key=f"acc-{i}", source_ip="10.0.0.1")
    assert await throttle.is_blocked(account_key="other", source_ip="10.0.0.1") is True


@pytest.mark.asyncio
async def test_success_resets_account_failures(throttle: LoginThrottle) -> None:
    for _ in range(4):
        await throttle.record_failure(account_key="acc", source_ip="127.0.0.1")
    await throttle.record_success(account_key="acc", source_ip="127.0.0.1")
    assert await throttle.is_blocked(account_key="acc", source_ip="127.0.0.1") is False


@pytest.mark.asyncio
async def test_failures_do_not_leak_across_accounts(throttle: LoginThrottle) -> None:
    for _ in range(5):
        await throttle.record_failure(account_key="acc-a", source_ip="127.0.0.1")
    assert await throttle.is_blocked(account_key="acc-b", source_ip="127.0.0.1") is False
