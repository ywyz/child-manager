"""M6 AI 固定结果与输入最小化 RED 验收。"""

from datetime import date
from types import ModuleType
from typing import Any

import pytest
from pydantic import ValidationError

from packages.backend.prompts.catalog import validate_prompt_result_schema
from packages.contracts import lesson_plans as lesson_plan_contracts
from packages.contracts import prompts as prompt_contracts


def _contract(module: ModuleType, name: str) -> Any:
    value = getattr(module, name, None)
    assert value is not None, f"M6 schema missing: {module.__name__}.{name}"
    return value


def _three(prefix: str, punctuation: str = "。") -> list[str]:
    return [f"{prefix}{index}{punctuation}" for index in range(1, 4)]


def test_morning_activity_requires_three_nonempty_chinese_statements() -> None:
    result_type = _contract(lesson_plan_contracts, "AiMorningActivity")
    valid = {
        "physical_cycle": "体能大循环",
        "group_game": "接力游戏",
        "free_game": "自主选择器械",
        "focus_guidance": "关注合作",
        "objectives": _three("目标"),
        "guidance_points": _three("指导"),
    }

    assert result_type(**valid).objectives == _three("目标")
    with pytest.raises(ValidationError):
        result_type(**(valid | {"objectives": _three("目标")[:2]}))
    with pytest.raises(ValidationError):
        result_type(**(valid | {"guidance_points": _three("指导", "？")}))
    with pytest.raises(ValidationError):
        result_type(**(valid | {"group_game": "   "}))
    with pytest.raises(ValidationError):
        validate_prompt_result_schema(
            "prompt.morning_activity.v1",
            valid | {"group_game": "   "},
        )


def test_morning_talk_requires_exactly_three_chinese_questions() -> None:
    result_type = _contract(lesson_plan_contracts, "AiMorningTalk")

    assert result_type(topic="春天", questions=_three("问题", "？")).topic == "春天"
    with pytest.raises(ValidationError):
        result_type(topic="春天", questions=_three("问题", "。"))
    with pytest.raises(ValidationError):
        result_type(topic="春天", questions=["问题一？", "问题二？"])


def test_area_result_cannot_own_areas_and_adoption_reuses_validated_input() -> None:
    result_type = _contract(lesson_plan_contracts, "AiAreaGame")
    apply_result = _contract(lesson_plan_contracts, "apply_ai_area_result")
    result = result_type(
        focus_guidance="建构区",
        objectives=_three("目标"),
        guidance_points=_three("指导"),
        support_strategies=_three("支持"),
    )

    adopted = apply_result(result, input_areas=["建构区", "美工区"])
    assert adopted.areas == ["建构区", "美工区"]
    assert adopted.focus_guidance == "建构区"
    with pytest.raises(ValidationError):
        result_type(
            focus_guidance="建构区",
            objectives=_three("目标"),
            guidance_points=_three("指导"),
            support_strategies=_three("支持"),
            areas=["模型伪造区域"],
        )
    with pytest.raises(ValueError, match="输入区域"):
        apply_result(result.model_copy(update={"focus_guidance": "未知区"}), input_areas=["建构区"])


def test_daily_reflection_is_nonempty_nfkc_and_limited_by_unicode_code_points() -> None:
    result_type = _contract(lesson_plan_contracts, "AiDailyReflection")

    normalized = result_type(highlights="Ａ", issues="问题", adjustments="调整")
    assert normalized.highlights == "A"
    assert len(normalized.highlights + normalized.issues + normalized.adjustments) == 5
    assert result_type(highlights="😀" * 198, issues="问", adjustments="调")
    with pytest.raises(ValidationError):
        result_type(highlights="😀" * 199, issues="问", adjustments="调")
    with pytest.raises(ValidationError):
        result_type(highlights="", issues="问题", adjustments="调整")


def test_group_activity_results_are_closed_and_add_step_index_is_not_clamped() -> None:
    split_type = _contract(lesson_plan_contracts, "AiGroupActivity")
    add_step_type = _contract(lesson_plan_contracts, "GroupActivityAddStepResult")
    validate_index = _contract(lesson_plan_contracts, "validate_group_add_step_result")
    split = {
        "theme": "春天",
        "objectives": ["观察变化"],
        "preparation": ["图片"],
        "focus": "表达发现",
        "difficulty": "连续描述",
        "process": [{"heading": "观察", "lines": ["观察图片"]}],
    }

    assert split_type(**split).theme == "春天"
    with pytest.raises(ValidationError):
        split_type(**(split | {"process": [{**split["process"][0], "is_ai_added": True}]}))
    result = add_step_type(
        step={"heading": "延伸", "lines": ["绘制春天"]},
        suggested_insert_index=1,
    )
    assert validate_index(result, process_length=1) == result
    with pytest.raises(ValueError, match="索引"):
        validate_index(result.model_copy(update={"suggested_insert_index": 2}), process_length=1)
    with pytest.raises(ValidationError):
        add_step_type(
            step={"heading": "延伸", "lines": ["绘制春天"], "is_ai_added": True},
            suggested_insert_index=1,
        )
    with pytest.raises(ValidationError, match="索引"):
        validate_prompt_result_schema(
            "prompt.group_activity_add_step.v1",
            {
                "step": {"heading": "延伸", "lines": ["绘制春天"]},
                "suggested_insert_index": 2,
            },
            input_context={
                "group_activity": split,
                "age_group_name": "大班",
                "teacher_context": "春季",
            },
        )


def test_reflection_input_excludes_identity_and_previous_reflection() -> None:
    current: Any = {
        "morning_activity": {},
        "morning_talk": {},
        "group_activity": {},
        "indoor_area_game": {},
        "afternoon_outdoor_game": {},
    }
    variables = prompt_contracts.ReflectionPromptVariables(
        plan_date=date(2026, 3, 2),
        class_name="向日葵班",
        age_group_name="大班",
        current_plan=current,
    )

    assert "daily_reflection" not in variables.current_plan.model_dump()
    with pytest.raises(ValidationError):
        prompt_contracts.ReflectionPromptVariables.model_validate(
            {
                "plan_date": "2026-03-02",
                "class_name": "向日葵班",
                "age_group_name": "大班",
                "current_plan": current,
                "teacher_account": "admin",
            }
        )
    with pytest.raises(ValidationError):
        prompt_contracts.ReflectionPromptVariables.model_validate(
            {
                "plan_date": "2026-03-02",
                "class_name": "向日葵班",
                "age_group_name": "大班",
                "current_plan": current | {"daily_reflection": {"highlights": "旧反思"}},
            }
        )
