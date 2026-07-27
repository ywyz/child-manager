"""固定提示词目录、输入与结果 Schema 路由。"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from pydantic import BaseModel

from packages.backend.prompts.renderer import validate_prompt_template
from packages.backend.prompts.system_defaults import SYSTEM_DEFAULTS
from packages.contracts.prompts import (
    AiAreaGame,
    AiDailyReflection,
    AiGroupActivity,
    AiMorningActivity,
    AiMorningTalk,
    CommonPlanPromptVariables,
    GroupActivityAddStepResult,
    GroupAddStepPromptVariables,
    GroupSplitPromptVariables,
    IndoorAreaPromptVariables,
    OutdoorAreaPromptVariables,
    ReflectionPromptVariables,
)


@dataclass(frozen=True, slots=True)
class PromptSpec:
    code: str
    name: str
    variable_whitelist: frozenset[str]
    required_capabilities: frozenset[str]
    result_schema_code: str
    result_schema_version: int
    content: str
    content_sha256: str
    input_model: type[BaseModel]
    result_model: type[BaseModel]


COMMON = frozenset(
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
CAPABILITIES = frozenset({"text", "structured_output"})


def _spec(
    code: str,
    name: str,
    variables: frozenset[str],
    schema_code: str,
    input_model: type[BaseModel],
    result_model: type[BaseModel],
) -> PromptSpec:
    content = SYSTEM_DEFAULTS[code]
    validate_prompt_template(content, variables)
    return PromptSpec(
        code=code,
        name=name,
        variable_whitelist=variables,
        required_capabilities=CAPABILITIES,
        result_schema_code=schema_code,
        result_schema_version=1,
        content=content,
        content_sha256=sha256(content.encode()).hexdigest(),
        input_model=input_model,
        result_model=result_model,
    )


PROMPT_SPECS = {
    item.code: item
    for item in (
        _spec(
            "daily_activity_plan.morning_activity",
            "晨间活动",
            COMMON,
            "prompt.morning_activity.v1",
            CommonPlanPromptVariables,
            AiMorningActivity,
        ),
        _spec(
            "daily_activity_plan.morning_talk",
            "晨间谈话",
            COMMON,
            "prompt.morning_talk.v1",
            CommonPlanPromptVariables,
            AiMorningTalk,
        ),
        _spec(
            "daily_activity_plan.group_activity_split",
            "集体活动拆分",
            frozenset({"source_text", "age_group_name", "teacher_context"}),
            "prompt.group_activity_split.v1",
            GroupSplitPromptVariables,
            AiGroupActivity,
        ),
        _spec(
            "daily_activity_plan.group_activity_add_step",
            "集体活动新增环节",
            frozenset({"group_activity", "age_group_name", "teacher_context"}),
            "prompt.group_activity_add_step.v1",
            GroupAddStepPromptVariables,
            GroupActivityAddStepResult,
        ),
        _spec(
            "daily_activity_plan.indoor_area_game",
            "室内区域游戏",
            COMMON | {"indoor_areas"},
            "prompt.indoor_area_game.v1",
            IndoorAreaPromptVariables,
            AiAreaGame,
        ),
        _spec(
            "daily_activity_plan.afternoon_outdoor_game",
            "下午户外游戏",
            COMMON | {"outdoor_areas"},
            "prompt.afternoon_outdoor_game.v1",
            OutdoorAreaPromptVariables,
            AiAreaGame,
        ),
        _spec(
            "daily_activity_plan.daily_reflection",
            "一日活动反思",
            frozenset({"plan_date", "class_name", "age_group_name", "current_plan"}),
            "prompt.daily_reflection.v1",
            ReflectionPromptVariables,
            AiDailyReflection,
        ),
    )
}


def prompt_spec(code: str) -> PromptSpec:
    try:
        return PROMPT_SPECS[code]
    except KeyError:
        raise LookupError("提示词定义不存在") from None


def validate_prompt_variables(code: str, variables: dict[str, Any]) -> dict[str, Any]:
    return prompt_spec(code).input_model.model_validate(variables).model_dump(mode="json")


def validate_prompt_result(code: str, result: dict[str, Any]) -> dict[str, Any]:
    return prompt_spec(code).result_model.model_validate(result).model_dump(mode="json")


def validate_prompt_result_schema(
    schema_code: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    for spec in PROMPT_SPECS.values():
        if spec.result_schema_code == schema_code:
            return spec.result_model.model_validate(result).model_dump(mode="json")
    raise LookupError("提示词结果 Schema 不存在")
