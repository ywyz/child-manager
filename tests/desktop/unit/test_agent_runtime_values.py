from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from types import ModuleType
from typing import Any
from uuid import UUID

import pytest

from tests.desktop.helpers import pending_module, pending_symbol


def _module() -> ModuleType:
    return pending_module(
        "kindergarten_manager.application.agent_runtime",
        red_label="T054_RED",
    )


def _patch(module: ModuleType, after_value: dict[str, object]) -> Any:
    entity_ref = pending_symbol(module, "EntityRef", red_label="T054_RED")
    entity_revision = pending_symbol(module, "EntityRevision", red_label="T054_RED")
    operation_type = pending_symbol(module, "PatchOperation", red_label="T054_RED")
    patch_type = pending_symbol(module, "PlanPatch", red_label="T054_RED")
    created = datetime(2026, 9, 7, 1, 0, tzinfo=UTC)
    return patch_type(
        patch_id=UUID(int=1),
        schema_version=1,
        created_at_utc=created,
        expires_at_utc=created + timedelta(minutes=5),
        context_id=UUID(int=2),
        turn_id=UUID(int=3),
        tool_name="lesson_plan.draft_section_patch",
        target=entity_ref(entity_type="lesson_plan", entity_id=9),
        base_revisions=(entity_revision(entity_type="lesson_plan", entity_id=9, revision=4),),
        operations=(
            operation_type(
                field_path="content.morning_talk.topic",
                before_sha256="0" * 64,
                before_display="春天里的种子",
                after_value=after_value,
                after_display="观察种子发芽",
            ),
        ),
        warnings=("这只是草案，不会修改教案",),
    )


def test_plan_patch_freezes_structured_values_and_has_a_stable_canonical_hash() -> None:
    module = _module()
    first_value = {"topic": "观察种子发芽", "questions": ("有什么变化？",)}
    second_value = {"questions": ("有什么变化？",), "topic": "观察种子发芽"}

    first = _patch(module, first_value)
    second = _patch(module, second_value)
    first_value["topic"] = "调用方后续修改"

    assert first.canonical_sha256 == second.canonical_sha256
    assert len(first.canonical_sha256) == 64
    assert first.canonical_sha256 == first.canonical_sha256.lower()
    assert first.operations[0].after_value["topic"] == "观察种子发芽"
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        first.operations = ()


def test_slice2b_runtime_interface_has_no_write_confirmation_method() -> None:
    module = _module()
    runtime_type = pending_symbol(module, "AgentRuntime", red_label="T054_RED")

    public_methods = {
        name
        for name, value in vars(runtime_type).items()
        if not name.startswith("_") and callable(value)
    }
    assert public_methods == {"start_turn", "cancel", "reject"}
    assert tuple(inspect.signature(runtime_type.start_turn).parameters) == (
        "self",
        "intent",
        "context_request",
    )
