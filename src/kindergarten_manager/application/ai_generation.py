"""Slice 2A AI 单任务协调与预览采用边界。"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID, uuid4

from kindergarten_manager.application.dto import CommandResult, OperationAccepted
from kindergarten_manager.domain.ai import (
    build_generation_input,
    canonical_json,
    canonical_json_sha256,
    preview_is_stale,
    section_content_from_result,
    section_sha256,
    validate_section_output,
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
class PreviewView:
    preview_id: int
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
    previews: tuple[PreviewView, ...]


@dataclass(frozen=True, slots=True)
class AdoptionCandidate:
    plan_id: int
    section_code: str
    result: dict[str, Any]
    target_section_sha256: str
    author_name: str
    content_schema_version: int
    content: dict[str, Any]
    content_revision: int
    archived: bool


class AdoptionTransaction(Protocol):
    def load_candidate(self) -> AdoptionCandidate: ...

    def invalidate(self) -> None: ...

    def save_snapshot(self) -> None: ...

    def update_content(self, content: Mapping[str, object]) -> int: ...

    def mark_adopted(self) -> None: ...


class StoredPreview(Protocol):
    @property
    def id(self) -> int: ...

    @property
    def result(self) -> dict[str, Any]: ...


class AiPreviewStore(Protocol):
    def content_for_plan(self, plan_id: int) -> Mapping[str, object]: ...

    def create_preview(
        self,
        *,
        lesson_plan_id: int,
        operation_id: str,
        section_code: str,
        result: object,
        frozen_input_sha256: str,
        target_section_sha256: str,
        now_utc_ms: int,
    ) -> StoredPreview: ...

    def reject_preview(self, preview_id: int, *, now_utc_ms: int) -> object: ...

    def adoption_transaction(
        self,
        preview_id: int,
        *,
        now_utc_ms: int,
    ) -> AbstractContextManager[AdoptionTransaction]: ...


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
        store: AiPreviewStore,
        clock_utc_ms: Callable[[], int] | None = None,
    ) -> None:
        self.runtime = runtime
        self.store = store
        self._clock_utc_ms = clock_utc_ms or (lambda: time.time_ns() // 1_000_000)
        self._current: _Operation | None = None
        self._previews: dict[int, PreviewView] = {}
        self._ready_by_section: dict[str, int] = {}
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
            return CommandResult.failure(
                "ai.operation_not_found",
                message="AI 生成任务不存在或已结束",
            )
        self.runtime.cancel(operation_id)
        self._discarded.add(operation_id)
        self._current = None
        return CommandResult.success(None, message="AI 生成已取消")

    def close(self) -> None:
        self._closed = True
        if self._current is not None:
            operation_id = self._current.operation_id
            self.runtime.cancel(operation_id)
            self._discarded.add(operation_id)
            self._current = None

    def clear_view(self) -> None:
        """切换教案时丢弃当前 UI 会话，持久化预览记录不受影响。"""
        if self._current is not None:
            self.cancel(self._current.operation_id)
        self._previews.clear()
        self._ready_by_section.clear()
        self._failed.clear()

    def accept_result(
        self,
        operation_id: UUID,
        section_code: str,
        output: object,
    ) -> PreviewView | None:
        operation = self._active_operation(operation_id, section_code)
        if operation is None:
            return None

        stored = self.store.create_preview(
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

    def reject(self, preview_id: int) -> PreviewView:
        preview = self._require_ready_preview(preview_id)
        self.store.reject_preview(preview_id, now_utc_ms=self._clock_utc_ms())
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

    def adopt(self, preview_id: int) -> AdoptedContent:
        preview = self._require_ready_preview(preview_id)
        stale = False
        with self.store.adoption_transaction(
            preview_id,
            now_utc_ms=self._clock_utc_ms(),
        ) as transaction:
            candidate = transaction.load_candidate()
            if candidate.archived:
                raise AiGenerationError("plan.archived_read_only", "归档教案不可采用 AI 预览")
            if preview_is_stale(
                candidate.target_section_sha256,
                candidate.content,
                candidate.section_code,
            ):
                transaction.invalidate()
                stale = True
                adopted = None
            else:
                validated = validate_section_output(candidate.section_code, candidate.result)
                updated = dict(candidate.content)
                updated[candidate.section_code] = section_content_from_result(validated)
                transaction.save_snapshot()
                revision = transaction.update_content(updated)
                transaction.mark_adopted()
                adopted = AdoptedContent(content=updated, content_revision=revision)
        if stale:
            self._replace_preview_status(preview_id, "invalidated")
            raise AiGenerationError("ai.preview_stale", "教案目标栏目已变化，预览不可采用")
        assert adopted is not None
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
            previews=tuple(
                self._previews[preview_id] for preview_id in self._ready_by_section.values()
            ),
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
                        payload_json=canonical_json(frozen_inputs[section]),
                    )
                    for section in sections
                ),
            ),
        )
        return OperationAccepted(operation_id=operation_id)

    def _content_for_plan(self, plan_id: int | None) -> Mapping[str, object]:
        if plan_id is None:
            raise AiGenerationError("ai.plan_content_unavailable", "无法读取当前教案内容")
        return self.store.content_for_plan(plan_id)

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

    def _require_ready_preview(self, preview_id: int) -> PreviewView:
        preview = self._previews.get(preview_id)
        if preview is None:
            raise AiGenerationError("ai.preview_not_found", "AI 预览不存在")
        if preview.status != "ready":
            raise AiGenerationError("ai.preview_not_ready", "AI 预览已处理")
        return preview

    def _replace_preview_status(self, preview_id: int, status: str) -> None:
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
class AdoptedContent:
    content: dict[str, Any]
    content_revision: int
