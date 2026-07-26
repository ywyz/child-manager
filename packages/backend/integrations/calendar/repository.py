"""园所范围工作日缓存 Repository。"""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb

from packages.backend.integrations.calendar.models import WorkdayResult


class WorkdayCacheRepository:
    def __init__(self, connection: object) -> None:
        self._connection = connection

    def get(
        self,
        kindergarten_id: UUID,
        calendar_date: date,
        now: datetime,
    ) -> WorkdayResult | None:
        row = self._connection.execute(  # type: ignore[attr-defined]
            """SELECT calendar_date, result_code, source_code, source_version,
                      detail, checked_at, expires_at
            FROM workday_cache
            WHERE kindergarten_id=%s AND calendar_date=%s AND expires_at>%s""",
            (kindergarten_id, calendar_date, now),
        ).fetchone()
        if row is None:
            return None
        return WorkdayResult(
            calendar_date=row[0],
            result_code=str(row[1]),
            source_code=str(row[2]),
            source_version=str(row[3]),
            detail=dict(row[4]),
            checked_at=row[5],
            expires_at=row[6],
        )

    def put(
        self,
        kindergarten_id: UUID,
        *,
        calendar_date: date,
        result_code: str,
        source_code: str,
        source_version: str,
        detail: dict[str, Any],
        checked_at: datetime,
        expires_at: datetime,
    ) -> None:
        self._connection.execute(  # type: ignore[attr-defined]
            """INSERT INTO workday_cache
            (kindergarten_id, calendar_date, result_code, source_code, source_version,
             detail, checked_at, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (kindergarten_id, calendar_date) DO UPDATE
            SET result_code=EXCLUDED.result_code,
                source_code=EXCLUDED.source_code,
                source_version=EXCLUDED.source_version,
                detail=EXCLUDED.detail,
                checked_at=EXCLUDED.checked_at,
                expires_at=EXCLUDED.expires_at,
                updated_at=now()""",
            (
                kindergarten_id,
                calendar_date,
                result_code,
                source_code,
                source_version,
                Jsonb(detail),
                checked_at,
                expires_at,
            ),
        )
