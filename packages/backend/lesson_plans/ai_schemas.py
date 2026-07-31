"""固定 AI 结果 Schema 注册表。"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from pydantic import BaseModel

from packages.contracts.lesson_plans import (
    AiAreaGame,
    AiDailyReflection,
    AiGroupActivity,
    AiMorningActivity,
    AiMorningTalk,
    GroupActivityAddStepResult,
)

AI_RESULT_SCHEMA_MODELS: Final[Mapping[str, type[BaseModel]]] = MappingProxyType(
    {
        "prompt.morning_activity.v1": AiMorningActivity,
        "prompt.morning_talk.v1": AiMorningTalk,
        "prompt.group_activity_split.v1": AiGroupActivity,
        "prompt.group_activity_add_step.v1": GroupActivityAddStepResult,
        "prompt.indoor_area_game.v1": AiAreaGame,
        "prompt.afternoon_outdoor_game.v1": AiAreaGame,
        "prompt.daily_reflection.v1": AiDailyReflection,
    }
)


def ai_result_model(schema_code: str) -> type[BaseModel]:
    """按冻结的 Schema 代码取得结果模型。"""

    try:
        return AI_RESULT_SCHEMA_MODELS[schema_code]
    except KeyError:
        raise LookupError("AI 结果 Schema 不存在") from None


__all__ = [
    "AI_RESULT_SCHEMA_MODELS",
    "AiAreaGame",
    "AiDailyReflection",
    "AiGroupActivity",
    "AiMorningActivity",
    "AiMorningTalk",
    "GroupActivityAddStepResult",
    "ai_result_model",
]
