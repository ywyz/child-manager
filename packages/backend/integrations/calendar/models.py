"""工作日缓存领域记录。"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkdayResult:
    calendar_date: date
    result_code: str
    source_code: str
    source_version: str
    detail: dict[str, Any]
    checked_at: datetime
    expires_at: datetime
