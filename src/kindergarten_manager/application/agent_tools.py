"""Slice 2B 固定 READ/DRAFT Tool registry。"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from kindergarten_manager.application.agent_runtime import (
    AgentContext,
    Permission,
    ProviderToolCall,
    ToolDescriptor,
    ToolResult,
)

APPROVED_TOOL_NAMES = (
    "lesson_plan.read_current",
    "lesson_plan.read_context",
    "calendar.read_evaluation",
    "settings.read_class_areas",
    "lesson_plan.draft_section_patch",
    "lesson_plan.draft_reflection_patch",
)

REGISTERED_PLAN_FIELD_PATHS = (
    "content.morning_activity.physical_cycle",
    "content.morning_activity.group_game",
    "content.morning_activity.free_game",
    "content.morning_activity.focus_guidance",
    "content.morning_activity.objectives",
    "content.morning_activity.guidance_points",
    "content.morning_talk.topic",
    "content.morning_talk.questions",
    "content.indoor_area_game.areas",
    "content.indoor_area_game.focus_guidance",
    "content.indoor_area_game.objectives",
    "content.indoor_area_game.guidance_points",
    "content.indoor_area_game.support_strategies",
    "content.afternoon_outdoor_game.areas",
    "content.afternoon_outdoor_game.focus_guidance",
    "content.afternoon_outdoor_game.objectives",
    "content.afternoon_outdoor_game.guidance_points",
    "content.afternoon_outdoor_game.support_strategies",
    "content.group_activity.theme",
    "content.group_activity.objectives",
    "content.group_activity.preparation",
    "content.group_activity.focus",
    "content.group_activity.difficulty",
    "content.group_activity.process",
    "content.daily_reflection.highlights",
    "content.daily_reflection.issues",
    "content.daily_reflection.adjustments",
)
_TEXT_PLAN_FIELD_PATHS = frozenset(
    path
    for path in REGISTERED_PLAN_FIELD_PATHS
    if not path.endswith(
        (
            ".objectives",
            ".guidance_points",
            ".questions",
            ".areas",
            ".preparation",
            ".process",
            ".support_strategies",
        )
    )
)


class ToolRegistryError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class AgentToolHandler(Protocol):
    def __call__(
        self,
        call: ProviderToolCall,
        context: AgentContext,
    ) -> ToolResult[object]: ...


@dataclass(frozen=True, slots=True)
class RegisteredTool:
    descriptor: ToolDescriptor
    handler: AgentToolHandler


class ToolRegistry:
    def __init__(
        self,
        tools: tuple[ToolDescriptor | RegisteredTool, ...],
        *,
        allowed_permissions: frozenset[Permission],
    ) -> None:
        if not allowed_permissions or Permission.WRITE in allowed_permissions:
            raise ToolRegistryError("agent.tool_not_allowed", "Slice 2B 只允许 READ/DRAFT Tool")
        registered: dict[str, RegisteredTool] = {}
        descriptors: dict[str, ToolDescriptor] = {}
        for item in tools:
            descriptor = item.descriptor if isinstance(item, RegisteredTool) else item
            if (
                descriptor.name not in APPROVED_TOOL_NAMES
                or descriptor.permission not in allowed_permissions
                or descriptor.permission is Permission.WRITE
                or descriptor.name in descriptors
            ):
                raise ToolRegistryError("agent.tool_not_allowed", "该工具未获批准")
            descriptors[descriptor.name] = descriptor
            if isinstance(item, RegisteredTool):
                registered[descriptor.name] = item
        self._allowed_permissions = allowed_permissions
        self._descriptors = descriptors
        self._registered = registered

    def descriptors(self) -> tuple[ToolDescriptor, ...]:
        return tuple(
            self._descriptors[name] for name in APPROVED_TOOL_NAMES if name in self._descriptors
        )

    def require(self, tool_name: str, claimed_permission: Permission) -> ToolDescriptor:
        descriptor = self._descriptors.get(tool_name)
        if (
            descriptor is None
            or descriptor.permission is not claimed_permission
            or descriptor.permission not in self._allowed_permissions
        ):
            raise ToolRegistryError("agent.tool_not_allowed", "该工具未获批准")
        return descriptor

    def execute(self, call: ProviderToolCall, context: AgentContext) -> ToolResult[object]:
        descriptor = self.require(call.tool_name, call.permission)
        if not schema_matches(descriptor.input_schema, call.arguments):
            raise ToolRegistryError("agent.tool_not_allowed", "Tool 参数不符合关闭 Schema")
        if call.permission is Permission.DRAFT and not _draft_arguments_match(call.arguments):
            raise ToolRegistryError("agent.tool_not_allowed", "草案字段值不符合注册类型")
        registered = self._registered.get(call.tool_name)
        if registered is None:
            raise ToolRegistryError("agent.tool_not_allowed", "该工具没有执行实现")
        result = registered.handler(call, context)
        if result.status == "ok" and not schema_matches(descriptor.output_schema, result.value):
            raise ToolRegistryError("agent.tool_not_allowed", "Tool 结果不符合关闭 Schema")
        return result


def build_read_draft_registry(
    handlers: Mapping[str, AgentToolHandler],
) -> ToolRegistry:
    expected = frozenset(APPROVED_TOOL_NAMES)
    if frozenset(handlers) != expected:
        raise ToolRegistryError("agent.tool_not_allowed", "Tool handler 必须精确匹配批准清单")
    return ToolRegistry(
        tuple(RegisteredTool(_descriptor(name), handlers[name]) for name in APPROVED_TOOL_NAMES),
        allowed_permissions=frozenset({Permission.READ, Permission.DRAFT}),
    )


def _descriptor(name: str) -> ToolDescriptor:
    permission = Permission.DRAFT if ".draft_" in name else Permission.READ
    return ToolDescriptor(
        name=name,
        permission=permission,
        input_schema=_schema_for(name),
        output_schema=_output_schema_for(name),
        redaction_policy="agent.minimum",
        timeout_ms=2_000,
    )


def _schema_for(name: str) -> dict[str, object]:
    if name.startswith("lesson_plan.read_"):
        return _closed_schema({"plan_id": {"type": "integer", "minimum": 1}})
    if name == "calendar.read_evaluation":
        return _closed_schema({"plan_date": {"type": "string", "format": "date"}})
    if name == "settings.read_class_areas":
        return _closed_schema({"class_id": {"type": "integer", "minimum": 1}})
    return _closed_schema(
        {
            "field_path": {
                "type": "string",
                "enum": list(REGISTERED_PLAN_FIELD_PATHS),
            },
            "after_value": {
                "oneOf": (
                    {"type": "string", "maxLength": 8_000},
                    {"type": "array", "maxItems": 100},
                )
            },
        }
    )


def _output_schema_for(name: str) -> dict[str, object]:
    if name == "lesson_plan.read_current":
        return _closed_schema(
            {
                "plan_id": {"type": "integer", "minimum": 1},
                "class_id": {"type": "integer", "minimum": 1},
                "semester_id": {"type": "integer", "minimum": 1},
                "plan_date": {"type": "string", "format": "date"},
                "content_revision": {"type": "integer", "minimum": 1},
                "content": {"type": "object"},
            }
        )
    if name == "lesson_plan.read_context":
        return _closed_schema(
            {
                "plan_id": {"type": "integer", "minimum": 1},
                "plan_date": {"type": "string", "format": "date"},
                "content_revision": {"type": "integer", "minimum": 1},
                "class_id": {"type": "integer", "minimum": 1},
                "class_name": {"type": "string", "maxLength": 120},
                "age_group": {"type": "string", "maxLength": 40},
                "semester_id": {"type": "integer", "minimum": 1},
                "semester_name": {"type": "string", "maxLength": 120},
                "start_date": {"type": "string", "format": "date"},
                "end_date": {"type": "string", "format": "date"},
            }
        )
    if name == "calendar.read_evaluation":
        return _closed_schema(
            {
                "plan_date": {"type": "string", "format": "date"},
                "warnings": {"type": "array", "maxItems": 20},
            }
        )
    if name == "settings.read_class_areas":
        return _closed_schema({"areas": {"type": "array", "maxItems": 100}})
    return _closed_schema(
        {
            "schema_version": {"type": "integer", "minimum": 1, "maximum": 1},
            "target": {"type": "object"},
            "base_revisions": {"type": "array", "maxItems": 20},
            "operations": {"type": "array", "maxItems": 50},
            "warnings": {"type": "array", "maxItems": 20},
        }
    )


def _closed_schema(properties: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties),
    }


def schema_matches(schema: Mapping[str, object], value: object) -> bool:
    alternatives = schema.get("oneOf")
    if isinstance(alternatives, tuple | list):
        return (
            sum(
                schema_matches(option, value)
                for option in alternatives
                if isinstance(option, Mapping)
            )
            == 1
        )
    expected = schema.get("type")
    if expected == "object":
        if not isinstance(value, Mapping):
            return False
        properties = schema.get("properties", {})
        required = schema.get("required", ())
        if not isinstance(properties, Mapping) or not isinstance(required, tuple | list):
            return False
        if schema.get("additionalProperties") is False and not set(value) <= set(properties):
            return False
        if not set(required) <= set(value):
            return False
        return all(
            key not in value or schema_matches(child, value[key])
            for key, child in properties.items()
            if isinstance(child, Mapping)
        )
    if expected == "array":
        if not isinstance(value, tuple | list):
            return False
        maximum = schema.get("maxItems")
        return not isinstance(maximum, int) or len(value) <= maximum
    if expected == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        return (not isinstance(minimum, int) or value >= minimum) and (
            not isinstance(maximum, int) or value <= maximum
        )
    if expected == "string":
        if not isinstance(value, str):
            return False
        enum = schema.get("enum")
        if isinstance(enum, list | tuple) and value not in enum:
            return False
        minimum_length = schema.get("minLength")
        maximum_length = schema.get("maxLength")
        if isinstance(minimum_length, int) and len(value) < minimum_length:
            return False
        if isinstance(maximum_length, int) and len(value) > maximum_length:
            return False
        if schema.get("format") == "date":
            from datetime import date

            try:
                date.fromisoformat(value)
            except ValueError:
                return False
    return True


def _draft_arguments_match(arguments: Mapping[str, object]) -> bool:
    field_path = arguments.get("field_path")
    value = arguments.get("after_value")
    if not isinstance(field_path, str) or field_path not in REGISTERED_PLAN_FIELD_PATHS:
        return False
    if field_path in _TEXT_PLAN_FIELD_PATHS:
        return isinstance(value, str) and len(value) <= 8_000
    if field_path.endswith(".process"):
        return (
            isinstance(value, tuple | list)
            and len(value) <= 50
            and all(isinstance(item, Mapping) for item in value)
        )
    return (
        isinstance(value, tuple | list)
        and len(value) <= 100
        and all(isinstance(item, str) and len(item) <= 2_000 for item in value)
    )
