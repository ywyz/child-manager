"""T037 可收集测试所需的设置规则签名骨架。"""

from collections.abc import Sequence
from datetime import date
from uuid import UUID


def semester_ranges_overlap(
    start_date: date,
    end_date: date,
    other_start_date: date,
    other_end_date: date,
) -> bool:
    """判断两个闭区间学期是否重叠。"""

    _ = (start_date, end_date, other_start_date, other_end_date)
    return False


def current_semester_selection_is_valid(states: Sequence[tuple[bool, bool]]) -> bool:
    """判断 ``(is_current, is_active)`` 集合是否满足当前学期规则。"""

    _ = states
    return False


def lead_teacher_selection_is_valid(teacher_ids: Sequence[UUID]) -> bool:
    """判断班级主班教师集合是否满足唯一性规则。"""

    _ = teacher_ids
    return False


def normalize_class_areas(names: Sequence[str]) -> tuple[str, ...]:
    """规范化并保留班级区域的输入顺序。"""

    _ = names
    return ()
