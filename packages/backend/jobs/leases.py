"""任务租约的确定性时间规则。"""

from datetime import UTC, datetime


def lease_is_expired(expires_at: datetime | None, *, now: datetime | None = None) -> bool:
    return expires_at is not None and expires_at <= (now or datetime.now(UTC))
