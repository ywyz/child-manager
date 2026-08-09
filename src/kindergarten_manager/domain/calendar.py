"""教案日期公共接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class TeachingWeek:
    number: int | None
    text: str | None


@dataclass(frozen=True, slots=True)
class CalendarEvaluation:
    date: date
    semester_status: str
    workday_status: str
    source: str
    warnings: tuple[str, ...]


def teaching_week(plan_date: date, semester_start: date, semester_end: date) -> TeachingWeek:
    raise NotImplementedError("T020 尚未实现教学周计算")


def activity_date_text(value: date) -> str:
    raise NotImplementedError("T020 尚未实现活动日期文本")


def season_for(value: date) -> str:
    raise NotImplementedError("T020 尚未实现季节文本")


def evaluate_calendar(
    value: date,
    *,
    semester_start: date,
    semester_end: date,
    manual_override: str | None = None,
) -> CalendarEvaluation:
    raise NotImplementedError("T020 尚未实现工作日软提示")
