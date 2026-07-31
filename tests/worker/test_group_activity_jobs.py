"""T122 集体活动新增环节的真实输入校验。"""

from copy import deepcopy

import pytest

from packages.backend.lesson_plans.group_activity_ai import require_complete_saved_group_activity

SPLIT_RESULT = {
    "theme": "春天",
    "objectives": ["观察变化"],
    "preparation": ["图片"],
    "focus": "表达发现",
    "difficulty": "连续描述",
    "process": [{"heading": "观察", "lines": ["观察图片"], "is_ai_added": False}],
}


def test_add_step_input_requires_complete_saved_group_activity() -> None:
    frozen = require_complete_saved_group_activity(SPLIT_RESULT)

    assert frozen["theme"] == "春天"
    assert frozen["process"] == SPLIT_RESULT["process"]
    incomplete = deepcopy(SPLIT_RESULT)
    incomplete["focus"] = ""
    with pytest.raises(ValueError, match="已采用并保存"):
        require_complete_saved_group_activity(incomplete)
