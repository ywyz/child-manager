"""首期结构化教案正文。"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, ClassVar, Self


class PlanContentV1:
    __slots__ = ("_data",)

    _SECTION_FIELDS: ClassVar[dict[str, frozenset[str]]] = {
        "morning_activity": frozenset(
            {
                "physical_cycle",
                "group_game",
                "free_game",
                "focus_guidance",
                "objectives",
                "guidance_points",
            }
        ),
        "morning_talk": frozenset({"topic", "questions"}),
        "group_activity": frozenset(
            {
                "source_text",
                "theme",
                "objectives",
                "preparation",
                "focus",
                "difficulty",
                "process",
            }
        ),
        "indoor_area_game": frozenset(
            {
                "areas",
                "focus_guidance",
                "objectives",
                "guidance_points",
                "support_strategies",
            }
        ),
        "afternoon_outdoor_game": frozenset(
            {
                "areas",
                "focus_guidance",
                "objectives",
                "guidance_points",
                "support_strategies",
            }
        ),
        "daily_reflection": frozenset({"highlights", "issues", "adjustments"}),
    }

    def __init__(self, value: dict[str, Any] | None = None) -> None:
        self._data = self._validated(value or self._empty_data())

    @classmethod
    def empty(cls) -> Self:
        return cls()

    @classmethod
    def model_validate(cls, value: Any) -> Self:
        if isinstance(value, cls):
            return cls(value.model_dump())
        if not isinstance(value, dict):
            raise ValueError("教案正文必须是对象")
        return cls(value)

    def model_dump(self, *, mode: str = "python") -> dict[str, Any]:
        if mode not in {"python", "json"}:
            raise ValueError("不支持的序列化模式")
        return deepcopy(self._data)

    def canonical_json(self) -> str:
        return json.dumps(
            self._data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def __repr__(self) -> str:
        return "PlanContentV1(schema_version=1)"

    @classmethod
    def _validated(cls, value: dict[str, Any]) -> dict[str, Any]:
        allowed = {"schema_version", *cls._SECTION_FIELDS}
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"教案正文包含未知字段：{sorted(unknown)}")
        if value.get("schema_version", 1) != 1:
            raise ValueError("不支持的教案正文版本")

        normalized = cls._empty_data()
        for section, fields in cls._SECTION_FIELDS.items():
            supplied = value.get(section, {})
            if not isinstance(supplied, dict):
                raise ValueError(f"{section} 必须是对象")
            nested_unknown = set(supplied) - fields
            if nested_unknown:
                raise ValueError(f"{section} 包含未知字段：{sorted(nested_unknown)}")
            normalized[section].update(deepcopy(supplied))

        for section in ("indoor_area_game", "afternoon_outdoor_game"):
            areas = normalized[section]["areas"]
            if not isinstance(areas, list) or not all(isinstance(item, str) for item in areas):
                raise ValueError("班级区域必须是文本数组")
            folded = [item.strip().casefold() for item in areas]
            if any(not item for item in folded):
                raise ValueError("班级区域不能为空")
            if len(folded) != len(set(folded)):
                raise ValueError("班级区域不能重复")
        if not isinstance(normalized["group_activity"]["source_text"], str):
            raise ValueError("集体活动原稿必须是文本")
        return normalized

    @staticmethod
    def _empty_data() -> dict[str, Any]:
        return {
            "schema_version": 1,
            "morning_activity": {
                "physical_cycle": "体能大循环",
                "group_game": "",
                "free_game": "",
                "focus_guidance": "",
                "objectives": [],
                "guidance_points": [],
            },
            "morning_talk": {"topic": "", "questions": []},
            "group_activity": {
                "source_text": "",
                "theme": "",
                "objectives": [],
                "preparation": [],
                "focus": "",
                "difficulty": "",
                "process": [],
            },
            "indoor_area_game": {
                "areas": [],
                "focus_guidance": "",
                "objectives": [],
                "guidance_points": [],
                "support_strategies": [],
            },
            "afternoon_outdoor_game": {
                "areas": [],
                "focus_guidance": "",
                "objectives": [],
                "guidance_points": [],
                "support_strategies": [],
            },
            "daily_reflection": {"highlights": "", "issues": "", "adjustments": ""},
        }
