from importlib import import_module
from typing import Any

import pytest
from pydantic import ValidationError


def _module() -> Any:
    try:
        return import_module("packages.backend.prompts.catalog")
    except ModuleNotFoundError:
        pytest.fail("T075 尚未提供七个固定提示词资源", pytrace=False)


EXPECTED_CODES = {
    "daily_activity_plan.morning_activity",
    "daily_activity_plan.morning_talk",
    "daily_activity_plan.group_activity_split",
    "daily_activity_plan.group_activity_add_step",
    "daily_activity_plan.indoor_area_game",
    "daily_activity_plan.afternoon_outdoor_game",
    "daily_activity_plan.daily_reflection",
}


def test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes() -> None:
    module = _module()
    assert set(module.PROMPT_SPECS) == EXPECTED_CODES
    assert len(module.PROMPT_SPECS) == 7
    for code, spec in module.PROMPT_SPECS.items():
        assert spec.code == code
        assert spec.content
        assert len(spec.content_sha256) == 64
        assert spec.result_schema_version == 1
        assert spec.required_capabilities >= frozenset({"text", "structured_output"})
        assert "account" not in spec.variable_whitelist
        assert "phone" not in spec.variable_whitelist


def test_catalog_assigns_task_specific_minimum_variable_whitelists() -> None:
    module = _module()
    assert module.prompt_spec(
        "daily_activity_plan.morning_activity"
    ).variable_whitelist == frozenset(
        {
            "plan_date",
            "weekday_text",
            "teaching_week_text",
            "season",
            "class_name",
            "age_group_name",
            "teacher_context",
        }
    )
    assert module.prompt_spec(
        "daily_activity_plan.indoor_area_game"
    ).variable_whitelist - module.prompt_spec(
        "daily_activity_plan.morning_activity"
    ).variable_whitelist == {"indoor_areas"}
    assert module.prompt_spec(
        "daily_activity_plan.daily_reflection"
    ).variable_whitelist == frozenset({"plan_date", "class_name", "age_group_name", "current_plan"})


def test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields() -> None:
    module = _module()
    variables = {
        "plan_date": "2026-07-26",
        "weekday_text": "星期日",
        "teaching_week_text": None,
        "season": "summer",
        "class_name": "向日葵班",
        "age_group_name": "中班",
        "teacher_context": "关注轮流表达",
    }
    validated = module.validate_prompt_variables(
        "daily_activity_plan.morning_activity",
        variables,
    )
    assert validated["teacher_context"] == "关注轮流表达"

    with pytest.raises(ValidationError):
        module.validate_prompt_variables(
            "daily_activity_plan.morning_activity",
            {**variables, "teacher_account": "teacher@example.test"},
        )
    with pytest.raises(ValidationError):
        module.validate_prompt_variables(
            "daily_activity_plan.morning_activity",
            {**variables, "teacher_context": {"notes": "错误对象格式"}},
        )
    with pytest.raises(ValidationError):
        module.validate_prompt_variables(
            "daily_activity_plan.indoor_area_game",
            {**variables, "indoor_areas": ["建构区", "建构区"]},
        )


def test_catalog_result_schemas_are_strict() -> None:
    module = _module()
    valid = {
        "topic": "春天的变化",
        "questions": ["你发现了什么？", "为什么会这样？", "还可以怎么观察？"],
    }
    assert module.validate_prompt_result("daily_activity_plan.morning_talk", valid) == valid
    with pytest.raises(ValidationError):
        module.validate_prompt_result(
            "daily_activity_plan.morning_talk",
            {**valid, "unexpected": "不能接受"},
        )


def test_catalog_result_schemas_match_the_frozen_openapi_shapes() -> None:
    module = _module()

    with pytest.raises(ValidationError):
        module.validate_prompt_result(
            "daily_activity_plan.morning_talk",
            {"topic": "春天的变化", "questions": ["少于三项？"]},
        )
    with pytest.raises(ValidationError):
        module.validate_prompt_result(
            "daily_activity_plan.morning_talk",
            {
                "topic": "春天的变化",
                "questions": ["第一问？", "第二问？", "缺少中文问号"],
            },
        )

    area_result = {
        "focus_guidance": "观察协作过程。",
        "objectives": ["目标一。", "目标二。", "目标三。"],
        "guidance_points": ["指导一。", "指导二。", "指导三。"],
        "support_strategies": ["支持一。", "支持二。", "支持三。"],
    }
    assert (
        module.validate_prompt_result("daily_activity_plan.indoor_area_game", area_result)
        == area_result
    )
    with pytest.raises(ValidationError):
        module.validate_prompt_result(
            "daily_activity_plan.indoor_area_game",
            {**area_result, "areas": ["建构区"]},
        )

    group_result = {
        "theme": "春天",
        "objectives": ["观察春天。"],
        "preparation": ["春天图片"],
        "focus": "主动观察",
        "difficulty": "表达发现",
        "process": [{"heading": "观察", "lines": ["看一看。"]}],
    }
    assert (
        module.validate_prompt_result(
            "daily_activity_plan.group_activity_split",
            group_result,
        )
        == group_result
    )

    added_step = {
        "step": {"heading": "迁移经验", "lines": ["说一说新的发现。"]},
        "suggested_insert_index": 1,
    }
    assert (
        module.validate_prompt_result(
            "daily_activity_plan.group_activity_add_step",
            added_step,
        )
        == added_step
    )
    with pytest.raises(ValidationError):
        module.validate_prompt_result_schema(
            "prompt.group_activity_add_step.v1",
            {**added_step, "suggested_insert_index": 2},
            input_context={
                "group_activity": group_result,
                "age_group_name": "中班",
                "teacher_context": "",
            },
        )
