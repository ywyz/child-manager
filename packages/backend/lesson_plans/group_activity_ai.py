"""集体活动新增环节的已采用内容校验。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from packages.contracts.lesson_plans import GroupActivity

_SPLIT_FIELDS = (
    "theme",
    "objectives",
    "preparation",
    "focus",
    "difficulty",
    "process",
)


def require_complete_saved_group_activity(value: Mapping[str, Any]) -> dict[str, Any]:
    """新增环节只基于教师已采用并保存的完整当前集体活动。"""

    try:
        activity = GroupActivity.model_validate(value)
    except ValidationError as exc:
        raise ValueError("集体活动必须已采用并保存") from exc
    dumped = activity.model_dump(mode="json")
    if any(not dumped[field] for field in _SPLIT_FIELDS):
        raise ValueError("集体活动必须已采用并保存")
    if any(not step.heading or not step.lines for step in activity.process):
        raise ValueError("集体活动必须已采用并保存")
    return dumped
