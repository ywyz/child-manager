"""Slice 2A 的结构化 AI 结果与预览指纹规则。"""

from __future__ import annotations

import json
from collections.abc import Mapping
from hashlib import sha256
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError


class _ClosedResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1


class MorningActivityResult(_ClosedResult):
    physical_cycle: str
    group_game: str
    free_game: str
    focus_guidance: str
    objectives: list[str]
    guidance_points: list[str]


class MorningTalkResult(_ClosedResult):
    topic: str
    questions: list[str]


class AreaGameResult(_ClosedResult):
    focus_guidance: str
    objectives: list[str]
    guidance_points: list[str]
    support_strategies: list[str]


class DailyReflectionResult(_ClosedResult):
    highlights: str
    issues: str
    adjustments: str


class AiOutputValidationError(ValueError):
    """向应用层暴露稳定分类，不泄漏供应商原始结果。"""

    def __init__(self, category: str) -> None:
        super().__init__("AI 返回内容不符合预期结构")
        self.category = category


_SCHEMAS: Mapping[str, type[BaseModel]] = {
    "morning_activity": MorningActivityResult,
    "morning_talk": MorningTalkResult,
    "indoor_area_game": AreaGameResult,
    "afternoon_outdoor_game": AreaGameResult,
    "daily_reflection": DailyReflectionResult,
}


def schema_for(section_code: str) -> type[BaseModel]:
    try:
        return _SCHEMAS[section_code]
    except KeyError:
        raise ValueError(f"不支持的 AI 栏目：{section_code}") from None


def canonical_json(value: object) -> str:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as error:
        raise ValueError("值不是规范 JSON") from error


def canonical_json_sha256(value: object) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def build_generation_input(
    *,
    section_code: str,
    content: Mapping[str, object],
    teacher_context: str,
) -> dict[str, object]:
    schema_for(section_code)
    target = content.get(section_code)
    if not isinstance(target, Mapping):
        raise ValueError("目标栏目不是结构化对象")
    return {
        "schema_code": section_code,
        "target": dict(target),
        "teacher_context": teacher_context,
    }


def section_sha256(content: Mapping[str, object], section_code: str) -> str:
    target = content.get(section_code)
    if not isinstance(target, Mapping):
        raise ValueError("目标栏目不是结构化对象")
    return canonical_json_sha256(dict(target))


def preview_is_stale(
    expected_target_sha256: str,
    content: Mapping[str, object],
    section_code: str,
) -> bool:
    return section_sha256(content, section_code) != expected_target_sha256


def validate_section_output(section_code: str, payload: object) -> dict[str, Any]:
    model = schema_for(section_code)
    try:
        return model.model_validate(payload).model_dump(mode="json")
    except ValidationError as error:
        error_types = {str(item["type"]) for item in error.errors()}
        category = _validation_category(error_types)
        raise AiOutputValidationError(category) from None


def section_content_from_result(result: Mapping[str, object]) -> dict[str, object]:
    """移除只属于 AI 结果信封的版本字段，再写入教案栏目。"""
    return {key: value for key, value in result.items() if key != "schema_version"}


def merge_section_result(
    current_section: Mapping[str, object],
    result: Mapping[str, object],
) -> dict[str, object]:
    """只覆盖 AI Schema 声明的字段，保留区域等教师维护字段。"""
    merged = dict(current_section)
    merged.update(section_content_from_result(result))
    return merged


def _validation_category(error_types: set[str]) -> str:
    priorities = (
        ("extra_forbidden", "unknown_field"),
        ("missing", "missing_field"),
    )
    for error_type, category in priorities:
        if error_type in error_types:
            return category
    return "wrong_type"
