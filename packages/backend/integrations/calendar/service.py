"""本地优先、在线补充且始终软降级的工作日服务。"""

from datetime import date, datetime, timedelta
from uuid import UUID

from chinese_calendar import is_workday

from packages.backend.integrations.calendar.client import TimorWorkdayClient
from packages.backend.integrations.calendar.models import WorkdayResult
from packages.backend.integrations.calendar.repository import WorkdayCacheRepository


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


class WorkdayService:
    def __init__(
        self,
        *,
        connection: object,
        online_client: TimorWorkdayClient | None = None,
    ) -> None:
        self._connection = connection
        self._online_client = online_client or TimorWorkdayClient()

    def check(
        self,
        kindergarten_id: UUID,
        calendar_date: date,
        *,
        now: datetime,
    ) -> WorkdayResult:
        repository = WorkdayCacheRepository(self._connection)
        cached = repository.get(kindergarten_id, calendar_date, now)
        if cached is not None:
            return cached
        try:
            local_result = "workday" if is_workday(calendar_date) else "non_workday"
        except KeyError, ValueError:
            local_result = None
        online_result = self._online_client.check(calendar_date)
        result = combine_workday_results(
            calendar_date=calendar_date,
            local_result=local_result,
            online_result=online_result,
            checked_at=now,
        )
        repository.put(
            kindergarten_id,
            calendar_date=result.calendar_date,
            result_code=result.result_code,
            source_code=result.source_code,
            source_version=result.source_version,
            detail=result.detail,
            checked_at=result.checked_at,
            expires_at=result.expires_at,
        )
        return result
