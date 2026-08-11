from __future__ import annotations

from importlib.resources import files

_PROMPT_CODES = frozenset(
    {
        "morning_activity",
        "morning_talk",
        "indoor_area_game",
        "afternoon_outdoor_game",
        "daily_reflection",
    }
)


def load_default_prompt(prompt_code: str) -> str:
    if prompt_code not in _PROMPT_CODES:
        raise ValueError(f"不支持的默认提示词：{prompt_code}")
    return files(__package__).joinpath(f"{prompt_code}.txt").read_text(encoding="utf-8")
