from datetime import date
from uuid import uuid4

import pytest

from packages.backend.settings.service import (
    current_semester_selection_is_valid,
    lead_teacher_selection_is_valid,
    normalize_class_areas,
    semester_ranges_overlap,
)


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        ((date(2026, 2, 1), date(2026, 6, 30)), (date(2026, 6, 30), date(2026, 8, 1)), True),
        ((date(2026, 2, 1), date(2026, 6, 30)), (date(2026, 7, 1), date(2026, 8, 1)), False),
    ],
)
def test_semester_overlap_uses_inclusive_date_ranges(
    first: tuple[date, date],
    second: tuple[date, date],
    expected: bool,
) -> None:
    assert semester_ranges_overlap(*first, *second) is expected


@pytest.mark.parametrize(
    ("states", "expected"),
    [
        ([], True),
        ([(False, True)], True),
        ([(True, True)], True),
        ([(False, True), (True, True)], True),
        ([(True, True), (True, True)], False),
        ([(True, False)], False),
    ],
)
def test_only_one_active_semester_can_be_current(
    states: list[tuple[bool, bool]],
    expected: bool,
) -> None:
    assert current_semester_selection_is_valid(states) is expected


@pytest.mark.parametrize(
    ("lead_teacher_count", "expected"),
    [(0, True), (1, True), (2, False)],
)
def test_each_class_has_at_most_one_lead_teacher(
    lead_teacher_count: int,
    expected: bool,
) -> None:
    assert lead_teacher_selection_is_valid([uuid4() for _ in range(lead_teacher_count)]) is expected


def test_empty_area_configuration_is_valid() -> None:
    assert normalize_class_areas([]) == ()


def test_areas_preserve_input_order_and_normalize_names() -> None:
    assert normalize_class_areas(["  阅读  区 ", "建构区"]) == ("阅读 区", "建构区")


def test_duplicate_names_within_one_area_type_are_rejected() -> None:
    with pytest.raises(ValueError, match="区域名称"):
        normalize_class_areas(["阅读区", " 阅读区 "])
