"""教案编辑器的稳定栏目与无障碍约束。"""

from typing import Any

AUTOSAVE_DELAY_SECONDS = 3

SECTION_LABELS = {
    "morning_activity": "晨间活动",
    "morning_talk": "晨间谈话",
    "group_activity": "集体活动",
    "indoor_area_game": "室内区域游戏",
    "afternoon_outdoor_game": "下午户外游戏",
    "daily_reflection": "一日活动反思",
}


def accessibility_contract() -> dict[str, Any]:
    return {
        "keyboard_order": (
            "班级",
            "活动日期",
            "六栏目编辑器",
            "保存",
            "归档",
            "历史版本",
        ),
        "errors_are_labelled": True,
        "status_uses_text": True,
        "minimum_touch_target_px": 44,
    }
