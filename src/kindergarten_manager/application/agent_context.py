"""按当前意图构建最小 Agent 教案投影。"""

from __future__ import annotations

import json
from collections.abc import Mapping

from kindergarten_manager.application.agent_runtime import AgentContext
from kindergarten_manager.domain.content import PlanContentV1

_INTENT_SECTIONS = {
    "morning_activity": ("晨间活动", "morning activity"),
    "morning_talk": ("晨间谈话", "morning talk"),
    "indoor_area_game": ("室内", "区域游戏", "indoor"),
    "afternoon_outdoor_game": ("户外", "afternoon outdoor"),
    "group_activity": ("集体活动", "group activity"),
    "daily_reflection": ("反思", "reflection"),
}


def project_plan_content_for_intent(
    content: PlanContentV1,
    intent: str,
) -> tuple[tuple[str, str], ...]:
    """仅返回意图明确指向的注册栏目字段，值使用稳定 JSON。"""

    normalized = intent.casefold()
    selected = {
        section
        for section, keywords in _INTENT_SECTIONS.items()
        if any(keyword in normalized for keyword in keywords)
    }
    payload = content.model_dump(mode="json")
    facts: list[tuple[str, str]] = []
    for section in sorted(selected):
        section_value = payload.get(section)
        if not isinstance(section_value, Mapping):
            continue
        for field_name, value in sorted(section_value.items()):
            facts.append(
                (
                    f"content.{section}.{field_name}",
                    json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
                )
            )
    return tuple(facts)


def minimize_current_plan_result(
    record: Mapping[str, object],
    context: AgentContext,
) -> dict[str, object]:
    """把权威教案读取结果裁剪为当前 Context 已批准的正文事实。"""

    minimized = dict(record)
    minimized["content"] = {
        fact.field_path: json.loads(str(fact.value))
        for fact in context.facts
        if fact.field_path.startswith("content.")
    }
    return minimized
