"""受控单 Agent 的冻结值对象与最小 Application Layer 接口。"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import date, datetime, timedelta
from enum import Enum, StrEnum
from hashlib import sha256
from threading import Lock
from types import MappingProxyType
from typing import Any, Protocol, runtime_checkable
from uuid import UUID, uuid4

from kindergarten_manager.application.dto import (
    CancellationToken,
    CommandResult,
    OperationAccepted,
)

_MAPPING_PROXY_TYPE = type(MappingProxyType({}))
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_SENSITIVE_FACT_PARTS = frozenset(
    {
        "api_key",
        "credential",
        "data_path",
        "database_path",
        "file_path",
        "history",
        "log",
        "password",
        "prompt",
        "recovery_code",
        "secret",
        "token",
    }
)


def _require_positive(value: int, field_name: str) -> None:
    if isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field_name} 必须是正整数")


def _require_nonempty(value: str, field_name: str) -> None:
    if not value or value != value.strip():
        raise ValueError(f"{field_name} 不能为空或包含首尾空白")


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} 必须是 UTC 时间")


def _require_frozen_value(value: object) -> None:
    if isinstance(value, str | bytes | int | float | bool | UUID | date | Enum | type(None)):
        return
    if isinstance(value, tuple | frozenset):
        for item in value:
            _require_frozen_value(item)
        return
    if isinstance(value, _MAPPING_PROXY_TYPE):
        for key, item in value.items():
            _require_frozen_value(key)
            _require_frozen_value(item)
        return
    if is_dataclass(value) and not isinstance(value, type):
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen:
            raise TypeError("Agent 冻结值不能包含可变 dataclass")
        for item in fields(value):
            _require_frozen_value(getattr(value, item.name))
        return
    raise TypeError("Agent 冻结值不能包含可变或不透明对象")


def _freeze_structured_value(value: object) -> object:
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("结构化对象的键必须是字符串")
            frozen[key] = _freeze_structured_value(item)
        return MappingProxyType(frozen)
    if isinstance(value, list | tuple):
        return tuple(_freeze_structured_value(item) for item in value)
    if isinstance(value, str | int | float | bool | UUID | date | Enum | type(None)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        _require_frozen_value(value)
        return value
    raise TypeError("结构化值只能包含冻结 DTO 或 JSON 值")


def _canonical_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _canonical_value(item) for key, item in sorted(value.items())}
    if isinstance(value, tuple):
        return [_canonical_value(item) for item in value]
    if isinstance(value, frozenset):
        canonical_items = (_canonical_value(item) for item in value)
        return sorted(canonical_items, key=lambda item: json.dumps(item, sort_keys=True))
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _canonical_value(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


class Permission(StrEnum):
    READ = "read"
    DRAFT = "draft"
    WRITE = "write"


@dataclass(frozen=True, slots=True)
class ActiveScope:
    class_id: int | None
    semester_id: int | None
    lesson_plan_id: int | None
    plan_date: date | None

    def __post_init__(self) -> None:
        for field_name in ("class_id", "semester_id", "lesson_plan_id"):
            value = getattr(self, field_name)
            if value is not None:
                _require_positive(value, field_name)
        if isinstance(self.plan_date, datetime):
            raise TypeError("plan_date 必须是日期而不是时间")


@dataclass(frozen=True, slots=True)
class EntityRevision:
    entity_type: str
    entity_id: int
    revision: int

    def __post_init__(self) -> None:
        _require_nonempty(self.entity_type, "entity_type")
        _require_positive(self.entity_id, "entity_id")
        _require_positive(self.revision, "revision")


@dataclass(frozen=True, slots=True)
class ContextFact:
    source_tool: str
    entity_type: str
    entity_id: int
    field_path: str
    value: object = field(repr=False)

    def __post_init__(self) -> None:
        _require_nonempty(self.source_tool, "source_tool")
        _require_nonempty(self.entity_type, "entity_type")
        _require_positive(self.entity_id, "entity_id")
        _require_nonempty(self.field_path, "field_path")
        _require_frozen_value(self.value)


@dataclass(frozen=True, slots=True)
class AgentContext:
    context_id: UUID
    session_id: UUID
    turn_id: UUID
    created_at_utc: datetime
    expires_at_utc: datetime
    locale: str
    active_scope: ActiveScope
    entity_revisions: tuple[EntityRevision, ...]
    facts: tuple[ContextFact, ...]
    allowed_permissions: frozenset[Permission]

    def __post_init__(self) -> None:
        _require_utc(self.created_at_utc, "created_at_utc")
        _require_utc(self.expires_at_utc, "expires_at_utc")
        if self.expires_at_utc <= self.created_at_utc:
            raise ValueError("AgentContext 到期时间必须晚于创建时间")
        if self.locale != "zh-CN":
            raise ValueError("AgentContext locale 必须是 zh-CN")
        if not isinstance(self.entity_revisions, tuple) or not self.entity_revisions:
            raise ValueError("AgentContext 必须携带实体 revision")
        if not isinstance(self.facts, tuple):
            raise TypeError("AgentContext facts 必须是 tuple")
        if not isinstance(self.allowed_permissions, frozenset):
            raise TypeError("AgentContext permissions 必须是 frozenset")

        revisions: dict[tuple[str, int], int] = {}
        for revision in self.entity_revisions:
            key = (revision.entity_type, revision.entity_id)
            if key in revisions:
                raise ValueError("AgentContext 不能包含重复实体 revision")
            revisions[key] = revision.revision

        scope_ids = {
            "class": self.active_scope.class_id,
            "semester": self.active_scope.semester_id,
            "lesson_plan": self.active_scope.lesson_plan_id,
        }
        for fact in self.facts:
            key = (fact.entity_type, fact.entity_id)
            if key not in revisions:
                raise ValueError("ContextFact 必须匹配实体 revision")
            scoped_id = scope_ids.get(fact.entity_type)
            if scoped_id is not None and scoped_id != fact.entity_id:
                raise ValueError("ContextFact 不能读取当前 scope 之外的实体")
            path_parts = frozenset(fact.field_path.casefold().split("."))
            if path_parts & _SENSITIVE_FACT_PARTS:
                raise ValueError("ContextFact 包含禁止进入 AgentContext 的字段")
            if fact.source_tool.casefold().endswith(".read_history"):
                raise ValueError("AgentContext 不能包含完整历史")

        _require_frozen_value(self.active_scope)
        _require_frozen_value(self.entity_revisions)
        _require_frozen_value(self.facts)
        _require_frozen_value(self.allowed_permissions)

    def is_valid(self, *, at_utc: datetime, active_scope: ActiveScope) -> bool:
        return (
            at_utc.tzinfo is not None
            and at_utc.utcoffset() == timedelta(0)
            and self.created_at_utc <= at_utc < self.expires_at_utc
            and active_scope == self.active_scope
        )


def _validated_schema(schema: Mapping[str, object], field_name: str) -> Mapping[str, object]:
    version = schema.get("schema_version")
    if isinstance(version, bool) or version != 1:
        raise ValueError(f"{field_name} 必须声明 schema_version=1")
    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        raise ValueError(f"{field_name} 必须是顶层关闭的 object schema")
    if not isinstance(schema.get("properties"), Mapping):
        raise ValueError(f"{field_name}.properties 必须是 object")
    if not isinstance(schema.get("required"), list | tuple):
        raise ValueError(f"{field_name}.required 必须是字段列表")
    frozen = _freeze_structured_value(schema)
    if not isinstance(frozen, Mapping):
        raise AssertionError("冻结后的 schema 必须保持映射语义")
    return frozen


@dataclass(frozen=True, slots=True)
class ToolDescriptor:
    name: str
    permission: Permission
    input_schema: Mapping[str, object]
    output_schema: Mapping[str, object]
    redaction_policy: str
    timeout_ms: int

    def __post_init__(self) -> None:
        _require_nonempty(self.name, "Tool name")
        _require_nonempty(self.redaction_policy, "redaction_policy")
        _require_positive(self.timeout_ms, "timeout_ms")
        object.__setattr__(
            self,
            "input_schema",
            _validated_schema(self.input_schema, "input_schema"),
        )
        object.__setattr__(
            self,
            "output_schema",
            _validated_schema(self.output_schema, "output_schema"),
        )


@dataclass(frozen=True, slots=True)
class ToolResult[T]:
    call_id: UUID
    tool_name: str
    permission: Permission
    status: str
    value: T | None = field(repr=False)
    error_code: str | None
    message: str
    retryable: bool
    observed_revisions: tuple[EntityRevision, ...]
    redactions: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_nonempty(self.tool_name, "tool_name")
        if self.status not in {"ok", "rejected", "failed", "cancelled", "stale"}:
            raise ValueError("ToolResult status 无效")
        if self.status == "ok" and self.error_code is not None:
            raise ValueError("成功 ToolResult 不能包含错误码")
        if self.status != "ok" and self.value is not None:
            raise ValueError("非成功 ToolResult 不能包含 value")
        if not isinstance(self.observed_revisions, tuple):
            raise TypeError("observed_revisions 必须是 tuple")
        if not isinstance(self.redactions, tuple):
            raise TypeError("redactions 必须是 tuple")
        if self.value is not None:
            object.__setattr__(self, "value", _freeze_structured_value(self.value))
        _require_frozen_value(self.observed_revisions)


@dataclass(frozen=True, slots=True)
class EntityRef:
    entity_type: str
    entity_id: int

    def __post_init__(self) -> None:
        _require_nonempty(self.entity_type, "entity_type")
        _require_positive(self.entity_id, "entity_id")


@dataclass(frozen=True, slots=True)
class PatchOperation:
    field_path: str
    before_sha256: str
    before_display: str = field(repr=False)
    after_value: object = field(repr=False)
    after_display: str = field(repr=False)

    def __post_init__(self) -> None:
        _require_nonempty(self.field_path, "field_path")
        if self.field_path.startswith("/") or ".." in self.field_path.split("."):
            raise ValueError("PlanPatch field_path 必须是注册字段路径")
        if _SHA256_PATTERN.fullmatch(self.before_sha256) is None:
            raise ValueError("before_sha256 必须是小写 SHA-256")
        if len(self.before_display) > 2_000 or len(self.after_display) > 2_000:
            raise ValueError("PlanPatch 展示文本过长")
        object.__setattr__(self, "after_value", _freeze_structured_value(self.after_value))


@dataclass(frozen=True, slots=True)
class PlanPatch:
    patch_id: UUID
    schema_version: int
    created_at_utc: datetime
    expires_at_utc: datetime
    context_id: UUID
    turn_id: UUID
    tool_name: str
    target: EntityRef
    base_revisions: tuple[EntityRevision, ...]
    operations: tuple[PatchOperation, ...]
    warnings: tuple[str, ...]
    canonical_sha256: str = ""

    def __post_init__(self) -> None:
        if self.schema_version != 1 or isinstance(self.schema_version, bool):
            raise ValueError("PlanPatch schema_version 必须是 1")
        _require_utc(self.created_at_utc, "created_at_utc")
        _require_utc(self.expires_at_utc, "expires_at_utc")
        if self.expires_at_utc <= self.created_at_utc:
            raise ValueError("PlanPatch 到期时间必须晚于创建时间")
        _require_nonempty(self.tool_name, "tool_name")
        if self.target.entity_type != "lesson_plan":
            raise ValueError("Slice 2B PlanPatch 只允许 lesson_plan 目标")
        if not isinstance(self.base_revisions, tuple) or not self.base_revisions:
            raise ValueError("PlanPatch 必须携带 base revision")
        if not isinstance(self.operations, tuple) or not self.operations:
            raise ValueError("PlanPatch 必须包含字段操作")
        if not isinstance(self.warnings, tuple):
            raise TypeError("PlanPatch warnings 必须是 tuple")
        ordered_revisions = tuple(
            sorted(
                self.base_revisions,
                key=lambda revision: (revision.entity_type, revision.entity_id),
            )
        )
        ordered_operations = tuple(
            sorted(self.operations, key=lambda operation: operation.field_path)
        )
        object.__setattr__(self, "base_revisions", ordered_revisions)
        object.__setattr__(self, "operations", ordered_operations)
        if not any(
            revision.entity_type == self.target.entity_type
            and revision.entity_id == self.target.entity_id
            for revision in self.base_revisions
        ):
            raise ValueError("PlanPatch target 必须匹配 base revision")

        paths = [operation.field_path for operation in self.operations]
        for index, path in enumerate(paths):
            for other in paths[index + 1 :]:
                if path == other or path.startswith(f"{other}.") or other.startswith(f"{path}."):
                    raise ValueError("PlanPatch operations 不能重复或重叠")

        payload = {
            "schema_version": self.schema_version,
            "tool_name": self.tool_name,
            "target": self.target,
            "base_revisions": self.base_revisions,
            "operations": self.operations,
            "warnings": self.warnings,
        }
        encoded = json.dumps(
            _canonical_value(payload),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        canonical = sha256(encoded).hexdigest()
        if self.canonical_sha256 and self.canonical_sha256 != canonical:
            raise ValueError("canonical_sha256 与规范 Patch 不匹配")
        object.__setattr__(self, "canonical_sha256", canonical)
        _require_frozen_value(self.base_revisions)
        _require_frozen_value(self.operations)


@dataclass(frozen=True, slots=True)
class ProviderToolCall:
    call_id: UUID
    tool_name: str
    permission: Permission
    arguments: Mapping[str, object]

    def __post_init__(self) -> None:
        _require_nonempty(self.tool_name, "tool_name")
        frozen = _freeze_structured_value(self.arguments)
        if not isinstance(frozen, Mapping):
            raise TypeError("Tool call arguments 必须是 object")
        object.__setattr__(self, "arguments", frozen)


@dataclass(frozen=True, slots=True)
class ProviderTurnRequest:
    operation_id: UUID
    system_policy: str
    context: AgentContext
    messages: tuple[Mapping[str, object], ...]
    tools: tuple[ToolDescriptor, ...]
    response_limit: int

    def __post_init__(self) -> None:
        _require_nonempty(self.system_policy, "system_policy")
        _require_positive(self.response_limit, "response_limit")
        if not isinstance(self.messages, tuple):
            raise TypeError("Provider messages 必须是 tuple")
        if not isinstance(self.tools, tuple):
            raise TypeError("Provider tools 必须是 tuple")
        frozen_messages: list[Mapping[str, object]] = []
        for message in self.messages:
            frozen = _freeze_structured_value(message)
            if not isinstance(frozen, Mapping):
                raise TypeError("Provider message 必须是 object")
            frozen_messages.append(frozen)
        object.__setattr__(self, "messages", tuple(frozen_messages))
        _require_frozen_value(self.context)
        _require_frozen_value(self.tools)


@dataclass(frozen=True, slots=True)
class ProviderTurnResult:
    assistant_content: str | None = field(repr=False)
    tool_calls: tuple[ProviderToolCall, ...]
    finish_reason: str
    provider_request_id: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.finish_reason not in {
            "completed",
            "tool_calls",
            "length",
            "refused",
            "cancelled",
        }:
            raise ValueError("Provider finish_reason 无效")
        if not isinstance(self.tool_calls, tuple):
            raise TypeError("Provider tool_calls 必须是 tuple")
        if self.assistant_content is not None and not isinstance(self.assistant_content, str):
            raise TypeError("Provider assistant_content 必须是文本")
        _require_frozen_value(self.tool_calls)


@runtime_checkable
class AgentProviderPort(Protocol):
    def complete(self, request: ProviderTurnRequest) -> ProviderTurnResult: ...


@dataclass(frozen=True, slots=True)
class AgentTurnOutcome:
    status: str
    assistant_content: str | None = field(default=None, repr=False)
    patches: tuple[PlanPatch, ...] = field(default=(), repr=False)


class AgentRuntimeError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class _RuntimeBridgePort(Protocol):
    finished: Any

    def submit(
        self,
        operation_id: UUID,
        task: Callable[[object, CancellationToken, Any], CommandResult[object]],
        frozen_input: object,
    ) -> CancellationToken: ...

    def cancel(self, operation_id: UUID) -> bool: ...


class _RegistryPort(Protocol):
    def descriptors(self) -> tuple[ToolDescriptor, ...]: ...

    def execute(self, call: ProviderToolCall, context: AgentContext) -> ToolResult[object]: ...


@dataclass(frozen=True, slots=True)
class _TurnInput:
    operation_id: UUID
    epoch: int
    intent: str = field(repr=False)
    scope: ActiveScope


class AgentRuntime:
    def __init__(
        self,
        *,
        provider: AgentProviderPort,
        registry: _RegistryPort,
        context_loader: Callable[[ActiveScope, str], AgentContext],
        runtime_bridge: _RuntimeBridgePort,
        monotonic_seconds: Callable[[], float],
        max_tool_calls: int,
        max_response_chars: int,
        max_turn_seconds: float,
    ) -> None:
        _require_positive(max_tool_calls, "max_tool_calls")
        _require_positive(max_response_chars, "max_response_chars")
        if max_turn_seconds <= 0:
            raise ValueError("max_turn_seconds 必须大于零")
        self._provider = provider
        self._registry = registry
        self._context_loader = context_loader
        self._bridge = runtime_bridge
        self._monotonic_seconds = monotonic_seconds
        self._max_tool_calls = max_tool_calls
        self._max_response_chars = max_response_chars
        self._max_turn_seconds = max_turn_seconds
        self._active_operation_id: UUID | None = None
        self._patches: dict[UUID, PlanPatch] = {}
        self._epoch = 0
        self._lock = Lock()
        runtime_bridge.finished.connect(self._on_finished)

    def start_turn(self, intent: str, context_request: ActiveScope) -> OperationAccepted:
        _require_nonempty(intent, "intent")
        with self._lock:
            if self._active_operation_id is not None:
                raise AgentRuntimeError("agent.operation_in_progress", "已有 Agent 任务正在运行")
            operation_id = uuid4()
            self._active_operation_id = operation_id
            epoch = self._epoch
        try:
            self._bridge.submit(
                operation_id,
                self._run_turn,
                _TurnInput(
                    operation_id=operation_id,
                    epoch=epoch,
                    intent=intent,
                    scope=context_request,
                ),
            )
        except Exception:
            with self._lock:
                self._active_operation_id = None
            raise
        return OperationAccepted(operation_id)

    def cancel(self, operation_id: UUID) -> ToolResult[None]:
        cancelled = self._bridge.cancel(operation_id)
        return ToolResult(
            call_id=uuid4(),
            tool_name="agent.runtime.cancel",
            permission=Permission.READ,
            status="cancelled" if cancelled else "stale",
            value=None,
            error_code="operation.cancelled" if cancelled else "agent.operation_stale",
            message="Agent 操作已取消" if cancelled else "Agent 操作已失效",
            retryable=False,
            observed_revisions=(),
            redactions=(),
        )

    def reject(self, patch_id: UUID) -> ToolResult[None]:
        removed = self._patches.pop(patch_id, None)
        return ToolResult(
            call_id=uuid4(),
            tool_name="agent.runtime.reject",
            permission=Permission.DRAFT,
            status="ok" if removed is not None else "stale",
            value=None,
            error_code=None if removed is not None else "agent.patch_stale",
            message="草案已丢弃" if removed is not None else "草案已失效",
            retryable=False,
            observed_revisions=(),
            redactions=(),
        )

    def _invalidate(self) -> None:
        with self._lock:
            self._epoch += 1
            self._patches.clear()

    def _is_current(self, turn: _TurnInput) -> bool:
        with self._lock:
            return self._epoch == turn.epoch and self._active_operation_id == turn.operation_id

    def _run_turn(
        self,
        frozen_input: object,
        cancellation: CancellationToken,
        _progress: Any,
    ) -> CommandResult[object]:
        if not isinstance(frozen_input, _TurnInput):
            return _failure("agent.context_invalid", "Agent Context 请求无效")
        started = self._monotonic_seconds()
        if not self._is_current(frozen_input):
            return _failure("agent.operation_stale", "Agent 操作已失效")
        context = self._context_loader(frozen_input.scope, frozen_input.intent)
        descriptors = self._registry.descriptors()
        messages: tuple[Mapping[str, object], ...] = (
            MappingProxyType({"role": "user", "content": frozen_input.intent}),
        )
        patches: list[PlanPatch] = []
        tool_count = 0

        while True:
            if cancellation.cancel_requested:
                return _failure("operation.cancelled", "Agent 操作已取消")
            if self._elapsed(started):
                return _failure("agent.turn_timeout", "Agent 操作超时")
            request = ProviderTurnRequest(
                operation_id=frozen_input.operation_id,
                system_policy=_READ_DRAFT_SYSTEM_POLICY,
                context=context,
                messages=messages,
                tools=descriptors,
                response_limit=self._max_response_chars,
            )
            try:
                response = self._provider.complete(request)
            except Exception:
                return _failure("agent.provider_failed", "Agent Provider 调用失败")
            if cancellation.cancel_requested:
                return _failure("operation.cancelled", "Agent 操作已取消")
            if not self._is_current(frozen_input):
                return _failure("agent.operation_stale", "Agent 操作已失效")
            if self._elapsed(started):
                return _failure("agent.turn_timeout", "Agent 操作超时")
            if not isinstance(response, ProviderTurnResult):
                return _failure("agent.provider_invalid_response", "Agent Provider 响应无效")
            if response.finish_reason == "refused":
                return _failure("agent.provider_refused", "Agent Provider 拒绝了本次请求")
            if len(response.assistant_content or "") > self._max_response_chars:
                return _failure("agent.response_too_large", "Agent Provider 响应超过允许上限")
            if not response.tool_calls:
                outcome = AgentTurnOutcome(
                    status="succeeded",
                    assistant_content=response.assistant_content,
                    patches=tuple(patches),
                )
                with self._lock:
                    if (
                        self._epoch != frozen_input.epoch
                        or self._active_operation_id != frozen_input.operation_id
                    ):
                        return _failure("agent.operation_stale", "Agent 操作已失效")
                    for patch in patches:
                        self._patches[patch.patch_id] = patch
                return CommandResult.success(outcome, message="Agent 草案已生成")
            if tool_count + len(response.tool_calls) > self._max_tool_calls:
                return _failure("agent.tool_call_limit", "Agent Tool 调用达到上限")

            results: list[ToolResult[object]] = []
            for call in response.tool_calls:
                if not self._is_current(frozen_input):
                    return _failure("agent.operation_stale", "Agent 操作已失效")
                descriptor = _require_call(descriptors, call)
                if descriptor is None or not _arguments_match(descriptor, call.arguments):
                    return _failure("agent.tool_not_allowed", "Agent Tool 请求未获批准")
                try:
                    result = self._registry.execute(call, context)
                except Exception:
                    return _failure("agent.tool_not_allowed", "Agent Tool 请求未获批准")
                if (
                    result.call_id != call.call_id
                    or result.tool_name != call.tool_name
                    or result.permission is not call.permission
                ):
                    return _failure("agent.tool_result_invalid", "Agent Tool 结果无效")
                results.append(result)
                tool_count += 1
                if call.permission is Permission.DRAFT and result.status == "ok":
                    try:
                        patches.append(_patch_from_result(result, context))
                    except KeyError, TypeError, ValueError:
                        return _failure("agent.tool_result_invalid", "Agent 草案结果无效")
            messages = (
                *messages,
                _assistant_tool_calls_message(response),
                _tool_results_message(results),
            )

    def _elapsed(self, started: float) -> bool:
        return self._monotonic_seconds() - started > self._max_turn_seconds

    def _on_finished(self, operation_id: UUID) -> None:
        with self._lock:
            if self._active_operation_id == operation_id:
                self._active_operation_id = None


def _failure(error_code: str, message: str) -> CommandResult[object]:
    return CommandResult.failure(error_code, message=message)


_READ_DRAFT_SYSTEM_POLICY = """你是一名幼儿园一日活动计划助理。
你只能读取当前上下文并形成草案，绝不能直接写入、保存、归档或导出数据。
需要事实时先调用 READ 工具；需要提出修改时只调用 DRAFT 工具。
不得臆造未由上下文或工具返回的信息，不得请求幼儿身份信息。
完成后用简体中文简要说明草案；所有草案都必须等待教师明确确认。"""


def _require_call(
    descriptors: tuple[ToolDescriptor, ...],
    call: ProviderToolCall,
) -> ToolDescriptor | None:
    return next(
        (
            descriptor
            for descriptor in descriptors
            if descriptor.name == call.tool_name and descriptor.permission is call.permission
        ),
        None,
    )


def _arguments_match(
    descriptor: ToolDescriptor,
    arguments: Mapping[str, object],
) -> bool:
    properties = descriptor.input_schema.get("properties")
    required = descriptor.input_schema.get("required")
    if not isinstance(properties, Mapping) or not isinstance(required, tuple):
        return False
    if not properties and not required:
        return True
    keys = frozenset(arguments)
    return keys <= frozenset(properties) and frozenset(required) <= keys


def _tool_results_message(results: list[ToolResult[object]]) -> Mapping[str, object]:
    return MappingProxyType(
        {
            "role": "tool",
            "results": tuple(
                MappingProxyType(
                    {
                        "call_id": str(result.call_id),
                        "tool_name": result.tool_name,
                        "status": result.status,
                        "value": result.value,
                    }
                )
                for result in results
            ),
        }
    )


def _assistant_tool_calls_message(
    response: ProviderTurnResult,
) -> Mapping[str, object]:
    return MappingProxyType(
        {
            "role": "assistant",
            "content": response.assistant_content,
            "tool_calls": tuple(
                MappingProxyType(
                    {
                        "call_id": str(call.call_id),
                        "tool_name": call.tool_name,
                        "arguments": call.arguments,
                    }
                )
                for call in response.tool_calls
            ),
        }
    )


def _patch_from_result(result: ToolResult[object], context: AgentContext) -> PlanPatch:
    if not isinstance(result.value, Mapping):
        raise TypeError
    target = result.value["target"]
    revisions = result.value["base_revisions"]
    operations = result.value["operations"]
    if not isinstance(target, Mapping) or not isinstance(revisions, tuple):
        raise TypeError
    if not isinstance(operations, tuple):
        raise TypeError
    return PlanPatch(
        patch_id=uuid4(),
        schema_version=int(result.value["schema_version"]),
        created_at_utc=context.created_at_utc,
        expires_at_utc=context.expires_at_utc,
        context_id=context.context_id,
        turn_id=context.turn_id,
        tool_name=result.tool_name,
        target=EntityRef(
            entity_type=str(target["entity_type"]),
            entity_id=int(target["entity_id"]),
        ),
        base_revisions=tuple(
            EntityRevision(
                entity_type=str(revision["entity_type"]),
                entity_id=int(revision["entity_id"]),
                revision=int(revision["revision"]),
            )
            for revision in revisions
            if isinstance(revision, Mapping)
        ),
        operations=tuple(
            PatchOperation(
                field_path=str(operation["field_path"]),
                before_sha256=str(operation["before_sha256"]),
                before_display=str(operation["before_display"]),
                after_value=operation["after_value"],
                after_display=str(operation["after_display"]),
            )
            for operation in operations
            if isinstance(operation, Mapping)
        ),
        warnings=tuple(str(item) for item in result.value.get("warnings", ())),
    )
