from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from types import ModuleType
from typing import Any
from uuid import UUID

import pytest
from pytestqt.qtbot import QtBot

from tests.desktop.application.agent_runtime_harness import (
    AgentRuntimeHarness,
    build_agent_runtime_harness,
)
from tests.desktop.helpers import pending_module, pending_symbol


def _pending_symbol(module: ModuleType, symbol_name: str) -> Any:
    return pending_symbol(module, symbol_name, red_label="SLICE2B_RED")


def _runtime_module() -> ModuleType:
    return pending_module(
        "kindergarten_manager.application.agent_runtime",
        red_label="SLICE2B_RED",
    )


def _scope(module: ModuleType) -> Any:
    active_scope = _pending_symbol(module, "ActiveScope")
    return active_scope(
        class_id=7,
        semester_id=8,
        lesson_plan_id=9,
        plan_date=date(2026, 9, 7),
    )


def _context(module: ModuleType) -> Any:
    permission = _pending_symbol(module, "Permission")
    entity_revision = _pending_symbol(module, "EntityRevision")
    context_fact = _pending_symbol(module, "ContextFact")
    agent_context = _pending_symbol(module, "AgentContext")
    created = datetime(2026, 9, 7, 1, 0, tzinfo=UTC)
    return agent_context(
        context_id=UUID(int=1),
        session_id=UUID(int=2),
        turn_id=UUID(int=3),
        created_at_utc=created,
        expires_at_utc=created + timedelta(minutes=5),
        locale="zh-CN",
        active_scope=_scope(module),
        entity_revisions=(entity_revision(entity_type="lesson_plan", entity_id=9, revision=4),),
        facts=(
            context_fact(
                source_tool="lesson_plan.read_current",
                entity_type="lesson_plan",
                entity_id=9,
                field_path="lesson_plan.content.morning_talk.topic",
                value="春天里的种子",
            ),
        ),
        allowed_permissions=frozenset({permission.READ, permission.DRAFT}),
    )


def _descriptor(module: ModuleType, name: str, permission_name: str) -> Any:
    permission = _pending_symbol(module, "Permission")
    descriptor_type = _pending_symbol(module, "ToolDescriptor")
    schema = {
        "schema_version": 1,
        "type": "object",
        "additionalProperties": False,
        "properties": {},
        "required": [],
    }
    return descriptor_type(
        name=name,
        permission=getattr(permission, permission_name),
        input_schema=schema,
        output_schema=schema,
        redaction_policy="lesson_plan.minimum",
        timeout_ms=1_000,
    )


@dataclass
class ManualClock:
    value: float = 0.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


@dataclass
class ScriptedProvider:
    responses: list[Any]
    on_complete: Callable[[Any], None] | None = None
    requests: list[Any] = field(default_factory=list)

    def complete(self, request: Any) -> Any:
        self.requests.append(request)
        if self.on_complete is not None:
            self.on_complete(request)
        if not self.responses:
            raise AssertionError("Scripted Provider 响应已耗尽")
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


@dataclass
class ReadDraftRegistry:
    module: ModuleType
    state: dict[str, object]
    calls: list[tuple[str, Any]] = field(default_factory=list)

    def descriptors(self) -> tuple[Any, ...]:
        return (
            _descriptor(self.module, "lesson_plan.read_current", "READ"),
            _descriptor(self.module, "lesson_plan.draft_section_patch", "DRAFT"),
        )

    def execute(self, call: Any, context: Any) -> Any:
        permission = _pending_symbol(self.module, "Permission")
        result_type = _pending_symbol(self.module, "ToolResult")
        self.calls.append((call.tool_name, call.arguments))
        if call.tool_name == "lesson_plan.read_current":
            value: object = {
                "plan_id": 9,
                "content_revision": self.state["revision"],
                "morning_talk": {"topic": self.state["topic"]},
            }
            result_permission = permission.READ
        elif call.tool_name == "lesson_plan.draft_section_patch":
            value = {
                "schema_version": 1,
                "target": {"entity_type": "lesson_plan", "entity_id": 9},
                "base_revisions": ({"entity_type": "lesson_plan", "entity_id": 9, "revision": 4},),
                "operations": (
                    {
                        "field_path": "content.morning_talk.topic",
                        "before_sha256": "0" * 64,
                        "before_display": "春天里的种子",
                        "after_value": call.arguments["after_value"],
                        "after_display": call.arguments["after_value"],
                    },
                ),
                "warnings": (),
            }
            result_permission = permission.DRAFT
        else:
            raise AssertionError(f"测试 registry 不允许工具 {call.tool_name}")
        return result_type(
            call_id=call.call_id,
            tool_name=call.tool_name,
            permission=result_permission,
            status="ok",
            value=value,
            error_code=None,
            message="工具执行完成",
            retryable=False,
            observed_revisions=context.entity_revisions,
            redactions=(),
        )


def _tool_call(
    module: ModuleType,
    *,
    call_id: int,
    name: str,
    permission_name: str,
    arguments: dict[str, object],
) -> Any:
    permission = _pending_symbol(module, "Permission")
    call_type = _pending_symbol(module, "ProviderToolCall")
    return call_type(
        call_id=UUID(int=call_id),
        tool_name=name,
        permission=getattr(permission, permission_name),
        arguments=arguments,
    )


def _provider_result(
    module: ModuleType,
    *,
    tool_calls: tuple[Any, ...] = (),
    content: str | None = None,
    finish_reason: str | None = None,
) -> Any:
    result_type = _pending_symbol(module, "ProviderTurnResult")
    return result_type(
        assistant_content=content,
        tool_calls=tool_calls,
        finish_reason=finish_reason or ("tool_calls" if tool_calls else "completed"),
        provider_request_id="fixture-request",
    )


def _business_state() -> dict[str, object]:
    return {
        "topic": "春天里的种子",
        "revision": 4,
        "versions": 2,
        "previews": 1,
        "audits": 0,
    }


def _runtime(
    module: ModuleType,
    provider: ScriptedProvider,
    registry: ReadDraftRegistry,
    *,
    clock: ManualClock | None = None,
    max_tool_calls: int = 4,
    max_response_chars: int = 2_000,
    max_turn_seconds: float = 30.0,
) -> AgentRuntimeHarness:
    context = _context(module)
    return build_agent_runtime_harness(
        module,
        provider=provider,
        registry=registry,
        context_loader=lambda _request, _intent: context,
        monotonic_seconds=clock or ManualClock(),
        max_tool_calls=max_tool_calls,
        max_response_chars=max_response_chars,
        max_turn_seconds=max_turn_seconds,
    )


def _draft_script(module: ModuleType, *, reversed_arguments: bool = False) -> list[Any]:
    draft_arguments: dict[str, object] = (
        {"after_value": "观察种子发芽", "field_path": "content.morning_talk.topic"}
        if reversed_arguments
        else {"field_path": "content.morning_talk.topic", "after_value": "观察种子发芽"}
    )
    return [
        _provider_result(
            module,
            tool_calls=(
                _tool_call(
                    module,
                    call_id=11,
                    name="lesson_plan.read_current",
                    permission_name="READ",
                    arguments={},
                ),
            ),
        ),
        _provider_result(
            module,
            tool_calls=(
                _tool_call(
                    module,
                    call_id=12,
                    name="lesson_plan.draft_section_patch",
                    permission_name="DRAFT",
                    arguments=draft_arguments,
                ),
            ),
        ),
        _provider_result(module, content="已形成字段级修改草案"),
    ]


def _run_draft(
    qtbot: QtBot,
    *,
    reversed_arguments: bool = False,
) -> tuple[Any, dict[str, object]]:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    provider = ScriptedProvider(_draft_script(module, reversed_arguments=reversed_arguments))
    harness = _runtime(module, provider, registry)

    _accepted, emitted = harness.start_and_wait(
        qtbot,
        "请为晨间谈话提出修改草案",
        _scope(module),
    )

    assert [name for name, _arguments in registry.calls] == [
        "lesson_plan.read_current",
        "lesson_plan.draft_section_patch",
    ]
    assert len(provider.requests) == 3
    assert len(emitted) == 1 and emitted[0].ok
    return emitted[0].value, state


def test_read_draft_loop_returns_a_stable_patch_and_never_writes(qtbot: QtBot) -> None:
    before = _business_state()
    first, first_state = _run_draft(qtbot)
    second, second_state = _run_draft(qtbot, reversed_arguments=True)

    assert first.status == second.status == "succeeded"
    assert len(first.patches) == len(second.patches) == 1
    assert first.patches[0].operations[0].field_path == "content.morning_talk.topic"
    assert first.patches[0].operations[0].after_value == "观察种子发芽"
    assert first.patches[0].canonical_sha256 == second.patches[0].canonical_sha256
    assert first_state == second_state == before


def test_second_agent_turn_is_rejected_while_the_first_is_running(qtbot: QtBot) -> None:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    provider = ScriptedProvider([_provider_result(module, content="完成")])
    harness = _runtime(module, provider, registry)
    errors: list[str | None] = []

    def start_reentrant_turn(_request: Any) -> None:
        try:
            harness.runtime.start_turn("第二个 turn", _scope(module))
        except Exception as error:
            errors.append(getattr(error, "code", None))

    provider.on_complete = start_reentrant_turn
    _accepted, emitted = harness.start_and_wait(qtbot, "第一个 turn", _scope(module))

    assert errors == ["agent.operation_in_progress"]
    assert len(emitted) == 1 and emitted[0].ok
    assert state == _business_state()


def test_tool_call_limit_stops_a_repeating_provider_without_writes(qtbot: QtBot) -> None:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    repeated = _provider_result(
        module,
        tool_calls=(
            _tool_call(
                module,
                call_id=21,
                name="lesson_plan.read_current",
                permission_name="READ",
                arguments={},
            ),
        ),
    )
    provider = ScriptedProvider([repeated, repeated, repeated])
    harness = _runtime(module, provider, registry, max_tool_calls=2)

    _accepted, emitted = harness.start_and_wait(qtbot, "循环读取", _scope(module))

    assert len(emitted) == 1 and not emitted[0].ok
    assert emitted[0].error_code == "agent.tool_call_limit"
    assert len(registry.calls) == 2
    assert state == _business_state()


def test_response_limit_rejects_oversized_provider_content_without_writes(
    qtbot: QtBot,
) -> None:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    provider = ScriptedProvider([_provider_result(module, content="超" * 11)])
    harness = _runtime(module, provider, registry, max_response_chars=10)

    _accepted, emitted = harness.start_and_wait(qtbot, "生成简短建议", _scope(module))

    assert len(emitted) == 1 and not emitted[0].ok
    assert emitted[0].error_code == "agent.response_too_large"
    assert state == _business_state()


def test_total_time_limit_stops_the_turn_without_writes(qtbot: QtBot) -> None:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    clock = ManualClock()
    provider = ScriptedProvider(
        [_provider_result(module, content="迟到")],
        on_complete=lambda _request: clock.advance(2.0),
    )
    harness = _runtime(module, provider, registry, clock=clock, max_turn_seconds=1.0)

    _accepted, emitted = harness.start_and_wait(qtbot, "超时请求", _scope(module))

    assert len(emitted) == 1 and not emitted[0].ok
    assert emitted[0].error_code == "agent.turn_timeout"
    assert state == _business_state()


@pytest.mark.parametrize(
    ("response_factory", "error_code"),
    [
        (
            lambda module: _provider_result(module, finish_reason="refused"),
            "agent.provider_refused",
        ),
        (lambda _module: {"tool_calls": "not-a-tuple"}, "agent.provider_invalid_response"),
    ],
)
def test_provider_refusal_and_invalid_structure_are_sanitized_and_write_nothing(
    qtbot: QtBot,
    response_factory: Callable[[ModuleType], Any],
    error_code: str,
) -> None:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    provider = ScriptedProvider([response_factory(module)])
    harness = _runtime(module, provider, registry)

    _accepted, emitted = harness.start_and_wait(qtbot, "请求草案", _scope(module))

    assert len(emitted) == 1 and not emitted[0].ok
    assert emitted[0].error_code == error_code
    assert "fixture-request" not in repr(emitted[0])
    assert state == _business_state()


def test_cancelled_turn_discards_the_provider_result_before_any_tool_call(
    qtbot: QtBot,
) -> None:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    provider = ScriptedProvider(
        [
            _provider_result(
                module,
                tool_calls=(
                    _tool_call(
                        module,
                        call_id=31,
                        name="lesson_plan.read_current",
                        permission_name="READ",
                        arguments={},
                    ),
                ),
            )
        ]
    )
    harness = _runtime(module, provider, registry)
    cancellation_results: list[Any] = []
    provider.on_complete = lambda request: cancellation_results.append(
        harness.runtime.cancel(request.operation_id)
    )

    _accepted, emitted = harness.start_and_wait(qtbot, "读取后取消", _scope(module))

    assert cancellation_results[0].status == "cancelled"
    assert emitted == ()
    assert registry.calls == []
    assert state == deepcopy(_business_state())


def test_invalidated_turn_discards_a_late_draft_even_when_bridge_cancel_is_too_late(
    qtbot: QtBot,
) -> None:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    provider = ScriptedProvider(_draft_script(module))
    harness = _runtime(module, provider, registry)

    def invalidate_after_final_provider_call(_request: Any) -> None:
        if len(provider.requests) == 3:
            harness.runtime._invalidate()

    provider.on_complete = invalidate_after_final_provider_call
    _accepted, emitted = harness.start_and_wait(qtbot, "请为晨间谈话提出修改草案", _scope(module))

    assert len(emitted) == 1 and not emitted[0].ok
    assert emitted[0].error_code == "agent.operation_stale"
    assert harness.runtime._patches == {}
    assert state == _business_state()


def test_context_loader_receives_the_current_turn_intent(qtbot: QtBot) -> None:
    module = _runtime_module()
    state = _business_state()
    registry = ReadDraftRegistry(module, state)
    provider = ScriptedProvider([_provider_result(module, content="完成")])
    captured: list[str] = []
    context = _context(module)
    harness = build_agent_runtime_harness(
        module,
        provider=provider,
        registry=registry,
        context_loader=lambda _scope, intent: (captured.append(intent), context)[1],
        monotonic_seconds=ManualClock(),
        max_tool_calls=4,
        max_response_chars=2_000,
        max_turn_seconds=30.0,
    )

    harness.start_and_wait(qtbot, "只读取晨间谈话主题", _scope(module))

    assert captured == ["只读取晨间谈话主题"]
