"""公开身份 ceremony 的来源限流公共 seam。"""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class ThrottleDecision:
    allowed: bool
    retry_after_seconds: int = 0


class MemoryAuthThrottle:
    """T030 将实现与 Redis 语义一致的确定性测试替身。"""

    def __init__(self, *, failure_limit: int, window: timedelta) -> None:
        del failure_limit, window

    def check(self, *, source: str, purpose: str, now: datetime) -> ThrottleDecision:
        del source, purpose, now
        return ThrottleDecision(allowed=True)

    def record_failure(self, *, source: str, purpose: str, now: datetime) -> None:
        del source, purpose, now

    def record_success(self, *, source: str, purpose: str, now: datetime) -> None:
        del source, purpose, now
