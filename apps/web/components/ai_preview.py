"""教案 AI 预览的稳定栏目、动作与展示数据。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AiSectionAction:
    task_code: str
    target_section: str
    button_label: str


AI_SECTION_ACTIONS = (
    AiSectionAction("morning_activity", "morning_activity", "生成晨间活动"),
    AiSectionAction("morning_talk", "morning_talk", "生成晨间谈话"),
    AiSectionAction("indoor_area_game", "indoor_area_game", "生成室内区域游戏"),
    AiSectionAction(
        "afternoon_outdoor_game",
        "afternoon_outdoor_game",
        "生成下午户外游戏",
    ),
)


def preview_title(target_section: str) -> str:
    del target_section
    return "AI 预览"


__all__ = ["AI_SECTION_ACTIONS", "AiSectionAction", "preview_title"]
