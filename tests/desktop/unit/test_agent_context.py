from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import UTC, date, datetime, timedelta
from types import ModuleType
from typing import Any
from uuid import UUID

import pytest

from kindergarten_manager.observability import REDACTED, redact_for_log
from tests.desktop.helpers import pending_module, pending_symbol


def _pending_symbol(module: ModuleType, symbol_name: str) -> Any:
    return pending_symbol(module, symbol_name, red_label="SLICE2B_RED")


def _runtime_module() -> ModuleType:
    return pending_module(
        "kindergarten_manager.application.agent_runtime",
        red_label="SLICE2B_RED",
    )


def _scope(
    module: ModuleType,
    *,
    class_id: int = 7,
    semester_id: int = 8,
    lesson_plan_id: int = 9,
    plan_date: date = date(2026, 9, 7),
) -> Any:
    active_scope = _pending_symbol(module, "ActiveScope")
    return active_scope(
        class_id=class_id,
        semester_id=semester_id,
        lesson_plan_id=lesson_plan_id,
        plan_date=plan_date,
    )


def _revision(
    module: ModuleType,
    *,
    entity_type: str = "lesson_plan",
    entity_id: int | None = None,
    revision: int = 4,
) -> Any:
    entity_revision = _pending_symbol(module, "EntityRevision")
    resolved_entity_id = (
        entity_id if entity_id is not None else (9 if entity_type == "lesson_plan" else 7)
    )
    return entity_revision(
        entity_type=entity_type,
        entity_id=resolved_entity_id,
        revision=revision,
    )


def _fact(
    module: ModuleType,
    *,
    field_path: str = "lesson_plan.content.morning_talk.topic",
    value: object = "春天里的种子",
    entity_type: str = "lesson_plan",
    entity_id: int = 9,
    source_tool: str = "lesson_plan.read_current",
) -> Any:
    context_fact = _pending_symbol(module, "ContextFact")
    return context_fact(
        source_tool=source_tool,
        entity_type=entity_type,
        entity_id=entity_id,
        field_path=field_path,
        value=value,
    )


def _context(
    module: ModuleType,
    *,
    active_scope: Any | None = None,
    entity_revisions: tuple[Any, ...] | None = None,
    facts: tuple[Any, ...] | None = None,
) -> Any:
    permission = _pending_symbol(module, "Permission")
    agent_context = _pending_symbol(module, "AgentContext")
    created = datetime(2026, 9, 7, 1, 0, tzinfo=UTC)
    return agent_context(
        context_id=UUID(int=1),
        session_id=UUID(int=2),
        turn_id=UUID(int=3),
        created_at_utc=created,
        expires_at_utc=created + timedelta(minutes=5),
        locale="zh-CN",
        active_scope=active_scope if active_scope is not None else _scope(module),
        entity_revisions=(
            entity_revisions if entity_revisions is not None else (_revision(module),)
        ),
        facts=facts if facts is not None else (_fact(module),),
        allowed_permissions=frozenset({permission.READ, permission.DRAFT}),
    )


def test_agent_context_has_only_the_frozen_minimum_contract_fields() -> None:
    module = _runtime_module()
    agent_context = _pending_symbol(module, "AgentContext")
    context = _context(module)

    assert {item.name for item in fields(agent_context)} == {
        "context_id",
        "session_id",
        "turn_id",
        "created_at_utc",
        "expires_at_utc",
        "locale",
        "active_scope",
        "entity_revisions",
        "facts",
        "allowed_permissions",
    }
    assert context.locale == "zh-CN"
    assert {permission.value for permission in context.allowed_permissions} == {"read", "draft"}
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        context.locale = "provider-controlled"  # type: ignore[misc]
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        context.active_scope.class_id = 99  # type: ignore[misc]
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        context.facts[0].value = "provider-controlled"  # type: ignore[misc]


def test_context_facts_require_matching_positive_entity_revisions() -> None:
    module = _runtime_module()
    revision = _revision(module)
    context = _context(module, entity_revisions=(revision,))

    assert context.entity_revisions == (revision,)
    assert revision.revision == 4
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        revision.revision = 5  # type: ignore[misc]
    with pytest.raises(ValueError):
        _context(module, entity_revisions=())
    with pytest.raises(ValueError):
        _revision(module, revision=0)
    with pytest.raises(ValueError):
        _context(module, facts=(_fact(module, entity_id=10),))


def test_context_expires_and_is_invalid_after_business_scope_switch() -> None:
    module = _runtime_module()
    scope = _scope(module)
    context = _context(module, active_scope=scope)

    assert context.is_valid(
        at_utc=datetime(2026, 9, 7, 1, 4, 59, tzinfo=UTC),
        active_scope=scope,
    )
    assert not context.is_valid(
        at_utc=datetime(2026, 9, 7, 1, 5, tzinfo=UTC),
        active_scope=scope,
    )
    switched_scopes = (
        _scope(module, class_id=99),
        _scope(module, semester_id=99),
        _scope(module, lesson_plan_id=99),
        _scope(module, plan_date=date(2026, 9, 8)),
    )
    assert all(
        not context.is_valid(
            at_utc=datetime(2026, 9, 7, 1, 1, tzinfo=UTC),
            active_scope=switched_scope,
        )
        for switched_scope in switched_scopes
    )


@pytest.mark.parametrize(
    "fact_kwargs",
    [
        {"field_path": "ai.api_key", "value": "fixture-api-key"},
        {"field_path": "application.data_path", "value": "/home/tester/private.sqlite3"},
        {
            "field_path": "class.name",
            "value": "无关班级",
            "entity_type": "class",
            "entity_id": 99,
            "source_tool": "settings.read_class_areas",
        },
        {
            "field_path": "lesson_plan.history",
            "value": ("完整历史正文一", "完整历史正文二"),
            "source_tool": "lesson_plan.read_history",
        },
    ],
)
def test_context_rejects_secrets_paths_unrelated_classes_and_full_history(
    fact_kwargs: dict[str, Any],
) -> None:
    module = _runtime_module()
    revisions = (_revision(module),)
    if fact_kwargs.get("entity_type") == "class":
        revisions += (_revision(module, entity_type="class", entity_id=99),)

    with pytest.raises(ValueError):
        _context(
            module,
            entity_revisions=revisions,
            facts=(_fact(module, **fact_kwargs),),
        )


def test_context_repr_and_structured_logging_exclude_fact_values() -> None:
    module = _runtime_module()
    context = _context(module)

    assert "春天里的种子" not in repr(context)
    assert redact_for_log({"agent_context": context}) == {"agent_context": REDACTED}


@pytest.mark.parametrize(
    "mutable_value",
    [
        {"topics": ("可变映射",)},
        ["可变列表"],
        {"可变集合"},
        bytearray(b"mutable"),
    ],
)
def test_context_rejects_mutable_nested_fact_values(mutable_value: object) -> None:
    module = _runtime_module()

    with pytest.raises(TypeError):
        _context(
            module,
            facts=(_fact(module, value=mutable_value),),
        )


def test_plan_context_projection_contains_only_fields_named_by_the_current_intent() -> None:
    from kindergarten_manager.application.agent_context import project_plan_content_for_intent
    from kindergarten_manager.domain.content import PlanContentV1

    content = PlanContentV1.empty()
    projected = dict(project_plan_content_for_intent(content, "只读取晨间谈话并提出草案"))

    assert set(projected) == {
        "content.morning_talk.questions",
        "content.morning_talk.topic",
    }
    assert all("daily_reflection" not in path for path in projected)
    assert project_plan_content_for_intent(content, "查看当前范围") == ()


def test_current_plan_tool_result_cannot_restore_content_outside_the_intent_projection() -> None:
    from kindergarten_manager.application.agent_context import minimize_current_plan_result

    module = _runtime_module()
    context = _context(
        module,
        facts=(
            _fact(
                module,
                field_path="content.morning_talk.topic",
                value='"春天里的种子"',
            ),
        ),
    )
    minimized = minimize_current_plan_result(
        {
            "plan_id": 3,
            "content": {
                "morning_talk": {"topic": "不得绕过投影"},
                "daily_reflection": {"highlights": "无关正文"},
            },
        },
        context,
    )

    assert minimized["content"] == {"content.morning_talk.topic": "春天里的种子"}
    assert "无关正文" not in repr(minimized)
