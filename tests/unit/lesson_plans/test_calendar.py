from datetime import date
from importlib import import_module


def _calendar():
    return import_module("packages.backend.lesson_plans.calendar")


def test_semester_start_week_is_week_one_and_increments_each_monday() -> None:
    calendar = _calendar()

    assert calendar.teaching_week(date(2026, 2, 4), date(2026, 2, 4), date(2026, 6, 30)) == (
        1,
        "第一周",
    )
    assert calendar.teaching_week(date(2026, 2, 9), date(2026, 2, 4), date(2026, 6, 30)) == (
        2,
        "第二周",
    )


def test_out_of_semester_week_number_and_text_are_both_empty() -> None:
    assert _calendar().teaching_week(date(2026, 2, 3), date(2026, 2, 4), date(2026, 6, 30)) == (
        None,
        None,
    )


def test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic() -> None:
    calendar = _calendar()

    assert calendar.activity_date_text(date(2026, 3, 2)) == "2026年3月2日 星期一"
    assert calendar.season_for(date(2026, 2, 28)) == "winter"
    assert calendar.season_for(date(2026, 3, 1)) == "spring"
    assert calendar.season_for(date(2026, 6, 1)) == "summer"
    assert calendar.season_for(date(2026, 9, 1)) == "autumn"
