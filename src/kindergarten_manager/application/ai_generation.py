"""Slice 2A AI 单任务协调与预览采用边界。"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol, cast
from uuid import UUID, uuid4

from kindergarten_manager.domain.ai import (
    build_generation_input,
    canonical_json_sha256,
    preview_is_stale,
    section_sha256,
)

_BATCH_SECTIONS = (
    "morning_activity",
    "morning_talk",
    "indoor_area_game",
    "afternoon_outdoor_game",
)


class AiGenerationError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class GenerationRuntime(Protocol):
    def submit(self, operation_id: UUID, work: object) -> None: ...

    def cancel(self, operation_id: UUID) -> bool: ...


@dataclass(frozen=True, slots=True)
class FrozenGenerationInput:
    section_code: str
    payload_json: str


@dataclass(frozen=True, slots=True)
class GenerationWork:
    operation_id: UUID
    plan_id: int
    sections: tuple[str, ...]
    teacher_context: str
    frozen_inputs: tuple[FrozenGenerationInput, ...]


@dataclass(frozen=True, slots=True)
class OperationAccepted:
    operation_id: UUID


@dataclass(frozen=True, slots=True)
class CommandResult:
    ok: bool


@dataclass(frozen=True, slots=True)
class PreviewView:
    preview_id: object
    plan_id: int
    section_code: str
    output: object
    target_section_sha256: str
    status: str


@dataclass(frozen=True, slots=True)
class CoordinatorState:
    running_operation_id: UUID | None
    ready_sections: tuple[str, ...]
    failed_sections: dict[str, str]


@dataclass(slots=True)
class _Operation:
    operation_id: UUID
    plan_id: int
    sections: tuple[str, ...]
    target_hashes: dict[str, str]
    frozen_input_hashes: dict[str, str]
    terminal_sections: set[str]


class AiGenerationCoordinator:
    def __init__(
        self,
        *,
        runtime: GenerationRuntime,
        store: object,
        clock_utc_ms: Callable[[], int] | None = None,
    ) -> None:
        self.runtime = runtime
        self.store = store
        self._clock_utc_ms = clock_utc_ms or (lambda: time.time_ns() // 1_000_000)
        self._current: _Operation | None = None
        self._previews: dict[object, PreviewView] = {}
        self._ready_by_section: dict[str, object] = {}
        self._failed: dict[str, str] = {}
        self._discarded: set[UUID] = set()
        self._closed = False

    def start_single(
        self,
        plan_id: int,
        section_code: str,
        teacher_context: str,
    ) -> OperationAccepted:
        return self._start(plan_id, (section_code,), teacher_context)

    def start_batch(self, plan_id: int, teacher_context: str) -> OperationAccepted:
        return self._start(plan_id, _BATCH_SECTIONS, teacher_context)

    def start_reflection(self, plan_id: int, teacher_context: str) -> OperationAccepted:
        return self._start(plan_id, ("daily_reflection",), teacher_context)

    def cancel(self, operation_id: UUID) -> CommandResult:
        if self._current is None or self._current.operation_id != operation_id:
            return CommandResult(ok=False)
        self.runtime.cancel(operation_id)
        self._discarded.add(operation_id)
        self._current = None
        return CommandResult(ok=True)

    def close(self) -> None:
        self._closed = True
        if self._current is not None:
            operation_id = self._current.operation_id
            self.runtime.cancel(operation_id)
            self._discarded.add(operation_id)
            self._current = None

    def accept_result(
        self,
        operation_id: UUID,
        section_code: str,
        output: object,
    ) -> PreviewView | None:
        operation = self._active_operation(operation_id, section_code)
        if operation is None:
            return None

        preview_id: object = uuid4()
        create_preview = getattr(self.store, "create_preview", None)
        if callable(create_preview):
            stored = cast(Any, create_preview)(
                lesson_plan_id=operation.plan_id,
                operation_id=str(operation_id),
                section_code=section_code,
                result=output,
                frozen_input_sha256=operation.frozen_input_hashes[section_code],
                target_section_sha256=operation.target_hashes[section_code],
                now_utc_ms=self._clock_utc_ms(),
            )
            preview_id = stored.id
            output = stored.result

        preview = PreviewView(
            preview_id=preview_id,
            plan_id=operation.plan_id,
            section_code=section_code,
            output=output,
            target_section_sha256=operation.target_hashes[section_code],
            status="ready",
        )
        self._previews[preview_id] = preview
        self._ready_by_section[section_code] = preview_id
        self._mark_terminal(operation, section_code)
        return preview

    def accept_failure(self, operation_id: UUID, section_code: str, error_code: str) -> None:
        operation = self._active_operation(operation_id, section_code)
        if operation is None:
            return
        self._failed[section_code] = error_code
        self._mark_terminal(operation, section_code)

    def reject(self, preview_id: object) -> PreviewView:
        preview = self._require_ready_preview(preview_id)
        reject_preview = getattr(self.store, "reject_preview", None)
        if callable(reject_preview) and isinstance(preview_id, int):
            reject_preview(preview_id, now_utc_ms=self._clock_utc_ms())
        rejected = PreviewView(
            preview_id=preview.preview_id,
            plan_id=preview.plan_id,
            section_code=preview.section_code,
            output=preview.output,
            target_section_sha256=preview.target_section_sha256,
            status="rejected",
        )
        self._previews[preview_id] = rejected
        self._ready_by_section.pop(preview.section_code, None)
        return rejected

    def adopt(self, preview_id: object) -> object:
        preview = self._require_ready_preview(preview_id)
        content = self._content_for_plan(preview.plan_id)
        if preview_is_stale(
            preview.target_section_sha256,
            content,
            preview.section_code,
        ):
            self._replace_preview_status(preview_id, "invalidated")
            raise AiGenerationError("ai.preview_stale", "教案目标栏目已变化，预览不可采用")

        adopt_preview = getattr(self.store, "adopt_preview", None)
        if callable(adopt_preview) and isinstance(preview_id, int):
            adopted = adopt_preview(preview_id, now_utc_ms=self._clock_utc_ms())
        else:
            adopt = getattr(self.store, "transactionally_adopt", None)
            if not callable(adopt):
                raise AiGenerationError("ai.store_unsupported", "AI 预览存储不支持采用")
            content = cast(dict[str, Any], adopt(preview.section_code, preview.output))
            adopted = _AdoptedContent(content=content)
        self._replace_preview_status(preview_id, "adopted")
        self._ready_by_section.pop(preview.section_code, None)
        return adopted

    def state(self) -> CoordinatorState:
        return CoordinatorState(
            running_operation_id=(
                self._current.operation_id if self._current is not None else None
            ),
            ready_sections=tuple(self._ready_by_section),
            failed_sections=dict(self._failed),
        )

    def _start(
        self,
        plan_id: int,
        sections: tuple[str, ...],
        teacher_context: str,
    ) -> OperationAccepted:
        if self._closed:
            raise AiGenerationError("ai.coordinator_closed", "AI 生成功能已关闭")
        if self._current is not None:
            raise AiGenerationError("ai.operation_in_progress", "已有 AI 生成正在进行")

        content = self._content_for_plan(plan_id)
        frozen_inputs = {
            section: build_generation_input(
                section_code=section,
                content=content,
                teacher_context=teacher_context,
            )
            for section in sections
        }
        operation_id = uuid4()
        operation = _Operation(
            operation_id=operation_id,
            plan_id=plan_id,
            sections=sections,
            target_hashes={section: section_sha256(content, section) for section in sections},
            frozen_input_hashes={
                section: canonical_json_sha256(frozen_input)
                for section, frozen_input in frozen_inputs.items()
            },
            terminal_sections=set(),
        )
        self._current = operation
        self._ready_by_section.clear()
        self._failed.clear()
        self.runtime.submit(
            operation_id,
            GenerationWork(
                operation_id=operation_id,
                plan_id=plan_id,
                sections=sections,
                teacher_context=teacher_context,
                frozen_inputs=tuple(
                    FrozenGenerationInput(
                        section_code=section,
                        payload_json=_canonical_json(frozen_inputs[section]),
                    )
                    for section in sections
                ),
            ),
        )
        return OperationAccepted(operation_id=operation_id)

    def _content_for_plan(self, plan_id: int | None) -> Mapping[str, object]:
        loader = getattr(self.store, "content_for_plan", None)
        if callable(loader) and plan_id is not None:
            return cast(Mapping[str, object], loader(plan_id))
        content = getattr(self.store, "content", None)
        if not isinstance(content, Mapping):
            raise AiGenerationError("ai.plan_content_unavailable", "无法读取当前教案内容")
        return content

    def _active_operation(
        self,
        operation_id: UUID,
        section_code: str,
    ) -> _Operation | None:
        if operation_id in self._discarded or self._closed:
            return None
        operation = self._current
        if (
            operation is None
            or operation.operation_id != operation_id
            or section_code not in operation.sections
            or section_code in operation.terminal_sections
        ):
            return None
        return operation

    def _mark_terminal(self, operation: _Operation, section_code: str) -> None:
        operation.terminal_sections.add(section_code)
        if operation.terminal_sections == set(operation.sections):
            self._current = None

    def _require_ready_preview(self, preview_id: object) -> PreviewView:
        preview = self._previews.get(preview_id)
        if preview is None:
            raise AiGenerationError("ai.preview_not_found", "AI 预览不存在")
        if preview.status != "ready":
            raise AiGenerationError("ai.preview_not_ready", "AI 预览已处理")
        return preview

    def _replace_preview_status(self, preview_id: object, status: str) -> None:
        preview = self._previews[preview_id]
        self._previews[preview_id] = PreviewView(
            preview_id=preview.preview_id,
            plan_id=preview.plan_id,
            section_code=preview.section_code,
            output=preview.output,
            target_section_sha256=preview.target_section_sha256,
            status=status,
        )


@dataclass(frozen=True, slots=True)
class _AdoptedContent:
    content: dict[str, Any]


def _canonical_json(value: object) -> str:
    import json

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
