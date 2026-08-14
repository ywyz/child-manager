from __future__ import annotations

from importlib.resources import files

_PROMPT_CODES = frozenset(
    {
        "morning_activity",
        "morning_talk",
        "indoor_area_game",
        "afternoon_outdoor_game",
        "daily_reflection",
        "group_activity",
    }
)

_LEGACY_DEFAULT_PROMPTS = {
    "morning_activity": frozenset(
        {
            (
                "请根据教师提供的最小上下文生成晨间活动。"
                "只返回符合 morning_activity Schema 的 JSON，不得补充幼儿身份信息。"
            ),
            """你是一名熟悉幼儿年龄特点和幼儿园一日活动组织的教师。请根据教师提供的日期、年龄段、主题和已有内容，设计可直接执行的晨间活动。

要求：
1. 体能大循环、集体游戏和自主游戏要相互衔接，运动强度由低到高再平稳过渡。
2. 目标和指导要点必须具体、可观察、适合该年龄段，避免空泛表述。
3. 不得补充幼儿姓名、教师账号等身份信息，不得虚构输入中没有的设施。
4. 只输出一个合法 JSON 对象，不要输出 Markdown、代码围栏、解释或额外字段。

严格使用以下结构，schema_version 固定为 1：
{"schema_version":1,"physical_cycle":"体能大循环安排","group_game":"集体游戏","free_game":"自主游戏","focus_guidance":"重点指导","objectives":["目标1","目标2"],"guidance_points":["指导要点1","指导要点2"]}""",
        }
    )
}


def load_default_prompt(prompt_code: str) -> str:
    if prompt_code not in _PROMPT_CODES:
        raise ValueError(f"不支持的默认提示词：{prompt_code}")
    return files(__package__).joinpath(f"{prompt_code}.txt").read_text(encoding="utf-8")


def resolve_prompt(prompt_code: str, override: str | None) -> str:
    default = load_default_prompt(prompt_code)
    if override is None:
        return default
    normalized = override.replace("\r\n", "\n").strip()
    if normalized in _LEGACY_DEFAULT_PROMPTS.get(prompt_code, ()):
        return default
    return override
