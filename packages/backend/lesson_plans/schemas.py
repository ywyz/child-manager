"""教案正文版本解析与独立完整性规则。"""

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from packages.contracts.lesson_plans import (
    AreaGame,
    GroupActivity,
    MorningActivity,
    MorningTalk,
    PlanContentV1,
)


@dataclass(frozen=True, slots=True)
class EditableContent:
    content: PlanContentV1 | None
    editable: bool


def _three_statements(values: list[str]) -> bool:
    return len(values) == 3 and all(
        bool(value.strip()) and value.endswith("。") for value in values
    )


def _three_questions(values: list[str]) -> bool:
    return len(values) == 3 and all(
        bool(value.strip()) and value.endswith("？") for value in values
    )


def _morning_activity_complete(value: MorningActivity) -> bool:
    return all(
        (
            value.physical_cycle == "体能大循环",
            bool(value.group_game.strip()),
            bool(value.free_game.strip()),
            bool(value.focus_guidance.strip()),
            _three_statements(value.objectives),
            _three_statements(value.guidance_points),
        )
    )


def _morning_talk_complete(value: MorningTalk) -> bool:
    return bool(value.topic.strip()) and _three_questions(value.questions)


def _group_activity_complete(value: GroupActivity) -> bool:
    return all(
        (
            bool(value.theme.strip()),
            bool(value.objectives) and all(item.strip() for item in value.objectives),
            bool(value.preparation) and all(item.strip() for item in value.preparation),
            bool(value.focus.strip()),
            bool(value.difficulty.strip()),
            bool(value.process)
            and all(
                step.heading.strip() and step.lines and all(line.strip() for line in step.lines)
                for step in value.process
            ),
        )
    )


def _area_complete(value: AreaGame) -> bool:
    return all(
        (
            bool(value.areas),
            bool(value.focus_guidance.strip()),
            _three_statements(value.objectives),
            _three_statements(value.guidance_points),
            _three_statements(value.support_strategies),
        )
    )


def content_completeness(content: PlanContentV1) -> dict[str, bool]:
    return {
        "morning_activity": _morning_activity_complete(content.morning_activity),
        "morning_talk": _morning_talk_complete(content.morning_talk),
        "group_activity": _group_activity_complete(content.group_activity),
        "indoor_area_game": _area_complete(content.indoor_area_game),
        "afternoon_outdoor_game": _area_complete(content.afternoon_outdoor_game),
        "daily_reflection": all(
            value.strip()
            for value in (
                content.daily_reflection.highlights,
                content.daily_reflection.issues,
                content.daily_reflection.adjustments,
            )
        ),
    }


def parse_content_for_editing(
    value: dict[str, Any],
    *,
    schema_version: int,
) -> EditableContent:
    if schema_version != 1:
        return EditableContent(content=None, editable=False)
    try:
        return EditableContent(content=PlanContentV1.model_validate(value), editable=True)
    except ValidationError:
        return EditableContent(content=None, editable=False)


def readable_content(
    value: dict[str, Any],
    schema_version: int,
) -> PlanContentV1 | dict[str, Any]:
    """已知且有效的版本返回强类型内容，未知版本保持原始数据只读。"""

    parsed = parse_content_for_editing(value, schema_version=schema_version)
    return parsed.content if parsed.content is not None else value
