"""本地优先、在线补充且始终软降级的工作日服务。"""

from datetime import date, datetime, timedelta

from chinese_calendar import is_workday

from packages.backend.integrations.calendar.client import TimorWorkdayClient
from packages.backend.integrations.calendar.models import WorkdayResult


def combine_workday_results(
    *,
    calendar_date: date,
    local_result: str | None,
    online_result: str | None,
    checked_at: datetime,
) -> WorkdayResult:
    if local_result is None and online_result is None:
        return WorkdayResult(
            calendar_date=calendar_date,
            result_code="unknown",
            source_code="unavailable",
            source_version="local+timor-v1",
            detail={},
            checked_at=checked_at,
            expires_at=checked_at + timedelta(minutes=5),
        )
    if local_result is not None and online_result is not None and local_result != online_result:
        return WorkdayResult(
            calendar_date=calendar_date,
            result_code=local_result,
            source_code="combined",
            source_version="local+timor-v1",
            detail={"local_result": local_result, "online_result": online_result},
            checked_at=checked_at,
            expires_at=checked_at + timedelta(hours=1),
        )
    result = local_result or online_result
    assert result is not None
    return WorkdayResult(
        calendar_date=calendar_date,
        result_code=result,
        source_code="local" if local_result is not None else "online",
        source_version="local+timor-v1",
        detail={},
        checked_at=checked_at,
        expires_at=checked_at + timedelta(hours=24),
    )


def resolve_uncached_workday(
    calendar_date: date,
    *,
    now: datetime,
    online_client: TimorWorkdayClient | None = None,
) -> WorkdayResult:
    """在无数据库连接存活时解析工作日，确保外网延迟不会扩大事务。"""

    try:
        local_result = "workday" if is_workday(calendar_date) else "non_workday"
    except KeyError, NotImplementedError, ValueError:
        local_result = None
    online_result = (online_client or TimorWorkdayClient()).check(calendar_date)
    return combine_workday_results(
        calendar_date=calendar_date,
        local_result=local_result,
        online_result=online_result,
        checked_at=now,
    )


def resolve_local_workday(calendar_date: date, *, now: datetime) -> WorkdayResult:
    """为列表冷缓存提供无外网的即时结论；单条用例再补充在线来源。"""

    try:
        local_result = "workday" if is_workday(calendar_date) else "non_workday"
    except KeyError, NotImplementedError, ValueError:
        local_result = None
    return combine_workday_results(
        calendar_date=calendar_date,
        local_result=local_result,
        online_result=None,
        checked_at=now,
    )
