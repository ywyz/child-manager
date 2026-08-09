"""不依赖系统时钟的教案日期规则。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from chinese_calendar import is_workday


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
    if plan_date < semester_start or plan_date > semester_end:
        return TeachingWeek(number=None, text=None)
    first_monday = semester_start - timedelta(days=semester_start.weekday())
    current_monday = plan_date - timedelta(days=plan_date.weekday())
    number = (current_monday - first_monday).days // 7 + 1
    return TeachingWeek(number=number, text=f"第（{_chinese_number(number)}）周")


def activity_date_text(value: date) -> str:
    weekday = "一二三四五六日"[value.weekday()]
    return f"周（{weekday}）{value.month}月{value.day}日"


def season_for(value: date) -> str:
    if 3 <= value.month <= 5:
        return "spring"
    if 6 <= value.month <= 8:
        return "summer"
    if 9 <= value.month <= 11:
        return "autumn"
    return "winter"


def evaluate_calendar(
    value: date,
    *,
    semester_start: date,
    semester_end: date,
    manual_override: str | None = None,
) -> CalendarEvaluation:
    semester_status = "inside" if semester_start <= value <= semester_end else "outside"
    warnings: list[str] = []
    if semester_status == "outside":
        warnings.append("所选日期不在当前学期内")

    if manual_override is not None:
        if manual_override not in {"workday", "non_workday"}:
            raise ValueError("无效的人工日历覆盖")
        workday_status = manual_override
        source = "manual"
    else:
        try:
            workday_status = "workday" if is_workday(value) else "non_workday"
            source = "chinesecalendar"
        except NotImplementedError:
            workday_status = "unknown"
            source = "unavailable"

    if workday_status == "non_workday":
        warnings.append("所选日期不是工作日")
    elif workday_status == "unknown":
        warnings.append("所选日期的工作日状态待确认")
    return CalendarEvaluation(
        date=value,
        semester_status=semester_status,
        workday_status=workday_status,
        source=source,
        warnings=tuple(warnings),
    )


def _chinese_number(value: int) -> str:
    digits = "零一二三四五六七八九"
    if value < 10:
        return digits[value]
    if value < 20:
        return "十" + (digits[value % 10] if value % 10 else "")
    tens, ones = divmod(value, 10)
    return digits[tens] + "十" + (digits[ones] if ones else "")
