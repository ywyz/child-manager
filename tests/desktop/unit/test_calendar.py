from __future__ import annotations

from datetime import date

from kindergarten_manager.domain.calendar import (
    activity_date_text,
    evaluate_calendar,
    season_for,
    teaching_week,
)
from tests.desktop.helpers import implemented


def test_semester_start_week_is_week_one_and_increments_each_monday() -> None:
    start = date(2026, 9, 2)
    end = date(2027, 1, 31)

    first = implemented(lambda: teaching_week(start, start, end))
    second = implemented(lambda: teaching_week(date(2026, 9, 7), start, end))
    outside = implemented(lambda: teaching_week(date(2026, 8, 31), start, end))

    assert (first.number, first.text) == (1, "第（一）周")
    assert (second.number, second.text) == (2, "第（二）周")
    assert (outside.number, outside.text) == (None, None)


def test_date_and_season_text_are_deterministic() -> None:
    value = date(2026, 9, 7)
    assert implemented(lambda: activity_date_text(value)) == "周（一）9月7日"
    assert implemented(lambda: season_for(value)) == "autumn"


def test_non_workday_outside_semester_and_unknown_calendar_are_soft_warnings() -> None:
    weekend = implemented(
        lambda: evaluate_calendar(
            date(2026, 9, 6),
            semester_start=date(2026, 9, 1),
            semester_end=date(2027, 1, 31),
        )
    )
    outside_coverage = implemented(
        lambda: evaluate_calendar(
            date(2100, 9, 6),
            semester_start=date(2100, 9, 1),
            semester_end=date(2101, 1, 31),
        )
    )
    manual = implemented(
        lambda: evaluate_calendar(
            date(2026, 9, 6),
            semester_start=date(2026, 9, 1),
            semester_end=date(2027, 1, 31),
            manual_override="workday",
        )
    )

    assert weekend.workday_status == "non_workday" and weekend.warnings
    assert outside_coverage.workday_status == "unknown" and outside_coverage.warnings
    assert manual.workday_status == "workday" and manual.source == "manual"
