from __future__ import annotations

import inspect
import json
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, timedelta
from types import ModuleType
from typing import Any, get_type_hints
from uuid import UUID

import httpx
import pytest

from tests.desktop.helpers import pending_module, pending_symbol


def _pending_symbol(module: ModuleType, symbol_name: str) -> Any:
    return pending_symbol(module, symbol_name, red_label="SLICE2B_RED")


def _runtime_module() -> ModuleType:
    return pending_module(
        "kindergarten_manager.application.agent_runtime",
        red_label="SLICE2B_RED",
    )


def _closed_schema() -> dict[str, object]:
    return {
        "schema_version": 1,
        "type": "object",
        "additionalProperties": False,
        "properties": {"plan_id": {"type": "integer", "minimum": 1}},
        "required": ["plan_id"],
    }


def _descriptor(
    module: ModuleType,
    *,
    name: str = "lesson_plan.read_current",
    permission_name: str = "READ",
    input_schema: dict[str, object] | None = None,
    output_schema: dict[str, object] | None = None,
) -> object:
    permission = _pending_symbol(module, "Permission")
    descriptor_type = _pending_symbol(module, "ToolDescriptor")
    return descriptor_type(
        name=name,
        permission=getattr(permission, permission_name),
        input_schema=_closed_schema() if input_schema is None else input_schema,
        output_schema=_closed_schema() if output_schema is None else output_schema,
        redaction_policy="lesson_plan.minimum",
        timeout_ms=1_000,
    )


def _assert_tool_not_allowed(call: Any) -> None:
    with pytest.raises(Exception) as captured:
        call()
    assert getattr(captured.value, "code", None) == "agent.tool_not_allowed"


def test_permission_is_a_closed_local_enum_with_explicit_write_stage() -> None:
    module = _runtime_module()
    permission = _pending_symbol(module, "Permission")

    assert {item.name for item in permission} == {"READ", "DRAFT", "WRITE"}
    assert {item.value for item in permission} == {"read", "draft", "write"}
    with pytest.raises(ValueError):
        permission("permission supplied by provider")


@pytest.mark.parametrize(
    ("schema_field", "schema"),
    [
        (schema_field, schema)
        for schema_field in ("input_schema", "output_schema")
        for schema in (
            {
                "schema_version": 1,
                "type": "object",
                "additionalProperties": True,
                "properties": {},
                "required": [],
            },
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {},
                "required": [],
            },
            {
                "schema_version": 2,
                "type": "object",
                "additionalProperties": False,
                "properties": {},
                "required": [],
            },
        )
    ],
)
def test_tool_descriptor_rejects_open_or_unversioned_schema(
    schema_field: str,
    schema: dict[str, object],
) -> None:
    module = _runtime_module()

    with pytest.raises(ValueError):
        if schema_field == "input_schema":
            _descriptor(module, input_schema=schema)
        else:
            _descriptor(module, output_schema=schema)


def test_tool_result_is_frozen_typed_and_has_stable_rejection_fields() -> None:
    module = _runtime_module()
    permission = _pending_symbol(module, "Permission")
    result_type = _pending_symbol(module, "ToolResult")
    result = result_type(
        call_id=UUID(int=7),
        tool_name="unknown.tool",
        permission=permission.READ,
        status="rejected",
        value=None,
        error_code="agent.tool_not_allowed",
        message="该工具不可用",
        retryable=False,
        observed_revisions=(),
        redactions=(),
    )

    assert result.status == "rejected"
    assert result.value is None
    assert result.error_code == "agent.tool_not_allowed"
    assert result.retryable is False
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        result.message = "provider forged success"


def test_provider_port_uses_only_application_owned_request_and_result_types() -> None:
    module = _runtime_module()
    port = _pending_symbol(module, "AgentProviderPort")
    request_type = _pending_symbol(module, "ProviderTurnRequest")
    result_type = _pending_symbol(module, "ProviderTurnResult")
    signature = inspect.signature(port.complete)
    hints = get_type_hints(port.complete, vars(module), vars(module))

    assert tuple(signature.parameters) == ("self", "request")
    assert hints["request"] is request_type
    assert hints["return"] is result_type
    assert request_type.__module__ == "kindergarten_manager.application.agent_runtime"
    assert result_type.__module__ == "kindergarten_manager.application.agent_runtime"


def test_provider_port_public_annotations_do_not_leak_concrete_sdk_types() -> None:
    module = _runtime_module()
    names = (
        "AgentProviderPort",
        "ProviderTurnRequest",
        "ProviderTurnResult",
        "ProviderToolCall",
    )
    surface: list[str] = []
    for name in names:
        symbol = _pending_symbol(module, name)
        target = symbol.complete if name == "AgentProviderPort" else symbol
        surface.append(repr(get_type_hints(target, vars(module), vars(module))))

    annotations = " ".join(surface).lower()
    for forbidden in ("openai", "anthropic", "httpx", "chatcompletion", "stream"):
        assert forbidden not in annotations


def test_provider_adapter_cannot_receive_or_execute_tools() -> None:
    adapter_module = pending_module(
        "kindergarten_manager.infrastructure.ai.agent_provider",
        red_label="SLICE2B_RED",
    )
    adapter = _pending_symbol(adapter_module, "OpenAICompatibleAgentProvider")

    constructor_parameters = set(inspect.signature(adapter).parameters)
    assert constructor_parameters == {
        "base_url",
        "api_key",
        "model_name",
        "transport",
        "max_response_bytes",
    }
    implementation = inspect.getsource(adapter).casefold()
    for forbidden in ("registry", "executor", ".execute(", "toolresult"):
        assert forbidden not in implementation


def test_provider_adapter_uses_valid_tool_continuation_messages_and_practical_timeout() -> None:
    runtime = _runtime_module()
    adapter_module = pending_module("kindergarten_manager.infrastructure.ai.agent_provider")
    adapter_type = _pending_symbol(adapter_module, "OpenAICompatibleAgentProvider")
    context_type = _pending_symbol(runtime, "AgentContext")
    scope_type = _pending_symbol(runtime, "ActiveScope")
    revision_type = _pending_symbol(runtime, "EntityRevision")
    request_type = _pending_symbol(runtime, "ProviderTurnRequest")
    captured: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "id": "fixture-response",
                "choices": [{"finish_reason": "stop", "message": {"content": "完成"}}],
            },
        )

    created = datetime(2026, 9, 7, tzinfo=UTC)
    context = context_type(
        context_id=UUID(int=1),
        session_id=UUID(int=2),
        turn_id=UUID(int=3),
        created_at_utc=created,
        expires_at_utc=created + timedelta(minutes=10),
        locale="zh-CN",
        active_scope=scope_type(1, 2, 3, date(2026, 9, 7)),
        entity_revisions=(revision_type("lesson_plan", 3, 4),),
        facts=(),
        allowed_permissions=frozenset(),
    )
    adapter = adapter_type(
        base_url="https://ai.example.test/v1",
        api_key="fixture-secret",
        model_name="fixture-model",
        transport=httpx.MockTransport(handler),
    )
    request = request_type(
        operation_id=UUID(int=4),
        system_policy="只允许 READ/DRAFT",
        context=context,
        messages=(
            {"role": "user", "content": "读取后形成草案"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": (
                    {
                        "call_id": str(UUID(int=5)),
                        "tool_name": "lesson_plan.read_current",
                        "arguments": {},
                    },
                ),
            },
            {
                "role": "tool",
                "results": (
                    {
                        "call_id": str(UUID(int=5)),
                        "tool_name": "lesson_plan.read_current",
                        "status": "ok",
                        "value": {"topic": "春天"},
                    },
                ),
            },
        ),
        tools=(_descriptor(runtime),),
        response_limit=2_000,
    )

    adapter.complete(request)

    assert adapter.timeout.read == 180
    messages = captured[0]["messages"]
    assert isinstance(messages, list)
    assert '"plan_id":3' in messages[0]["content"]
    assert '"class_id":1' in messages[0]["content"]
    assert '"plan_date":"2026-09-07"' in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "tool"
    assert messages[3]["tool_call_id"] == str(UUID(int=5))


@pytest.mark.parametrize(
    ("tool_name", "descriptor_permission", "claimed_permission"),
    [
        ("unknown.tool", "READ", "READ"),
        ("lesson_plan.write_current", "WRITE", "WRITE"),
        ("lesson_plan.read_current", "READ", "DRAFT"),
    ],
)
def test_registry_rejects_unknown_write_and_forged_permission(
    tool_name: str,
    descriptor_permission: str,
    claimed_permission: str,
) -> None:
    runtime_module = _runtime_module()
    tools_module = pending_module(
        "kindergarten_manager.application.agent_tools",
        red_label="SLICE2B_RED",
    )
    permission = _pending_symbol(runtime_module, "Permission")
    registry_type = _pending_symbol(tools_module, "ToolRegistry")
    read_descriptor = _descriptor(runtime_module)

    if descriptor_permission == "WRITE":
        write_descriptor = _descriptor(
            runtime_module,
            name=tool_name,
            permission_name="WRITE",
        )
        _assert_tool_not_allowed(
            lambda: registry_type(
                (read_descriptor, write_descriptor),
                allowed_permissions=frozenset({permission.READ, permission.DRAFT}),
            )
        )
        return

    registry = registry_type(
        (read_descriptor,),
        allowed_permissions=frozenset({permission.READ, permission.DRAFT}),
    )
    _assert_tool_not_allowed(
        lambda: registry.require(tool_name, getattr(permission, claimed_permission))
    )


@pytest.mark.parametrize(
    "arguments",
    [
        {"plan_id": "1"},
        {"plan_id": 0},
        {"plan_id": 1, "extra": True},
    ],
)
def test_registry_rejects_tool_arguments_that_violate_the_closed_schema(
    arguments: dict[str, object],
) -> None:
    runtime_module = _runtime_module()
    tools_module = pending_module(
        "kindergarten_manager.application.agent_tools",
        red_label="SLICE2B_RED",
    )
    permission = _pending_symbol(runtime_module, "Permission")
    call_type = _pending_symbol(runtime_module, "ProviderToolCall")
    registry_type = _pending_symbol(tools_module, "ToolRegistry")
    registered_type = _pending_symbol(tools_module, "RegisteredTool")
    result_type = _pending_symbol(runtime_module, "ToolResult")
    descriptor = _descriptor(runtime_module)

    def handler(call: Any, _context: object) -> object:
        return result_type(
            call_id=call.call_id,
            tool_name=call.tool_name,
            permission=call.permission,
            status="ok",
            value={"plan_id": 1},
            error_code=None,
            message="读取完成",
            retryable=False,
            observed_revisions=(),
            redactions=(),
        )

    registry = registry_type(
        (registered_type(descriptor, handler),),
        allowed_permissions=frozenset({permission.READ, permission.DRAFT}),
    )
    call = call_type(
        call_id=UUID(int=81),
        tool_name="lesson_plan.read_current",
        permission=permission.READ,
        arguments=arguments,
    )

    _assert_tool_not_allowed(lambda: registry.execute(call, object()))


@pytest.mark.parametrize(
    ("field_path", "after_value"),
    [
        ("content.morning_talk.topic", {"not": "text"}),
        ("content.morning_talk.questions", "not-a-list"),
        ("content.unknown.field", "越界字段"),
    ],
)
def test_draft_registry_rejects_unregistered_or_wrongly_typed_field_values(
    field_path: str,
    after_value: object,
) -> None:
    runtime_module = _runtime_module()
    tools_module = pending_module(
        "kindergarten_manager.application.agent_tools",
        red_label="SLICE2B_RED",
    )
    permission = _pending_symbol(runtime_module, "Permission")
    call_type = _pending_symbol(runtime_module, "ProviderToolCall")
    registry = _pending_symbol(tools_module, "build_read_draft_registry")(
        {name: lambda _call, _context: None for name in tools_module.APPROVED_TOOL_NAMES}
    )
    call = call_type(
        call_id=UUID(int=82),
        tool_name="lesson_plan.draft_section_patch",
        permission=permission.DRAFT,
        arguments={"field_path": field_path, "after_value": after_value},
    )

    _assert_tool_not_allowed(lambda: registry.execute(call, object()))
