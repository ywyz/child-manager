from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from types import SimpleNamespace
from uuid import UUID

import pytest

from kindergarten_manager.domain.content import PlanContentV1
from tests.desktop.helpers import pending_module, pending_symbol


@dataclass
class ScriptedRuntime:
    submitted: list[tuple[UUID, object]] = field(default_factory=list)
    cancelled: list[UUID] = field(default_factory=list)

    def submit(self, operation_id: UUID, work: object) -> None:
        self.submitted.append((operation_id, work))

    def cancel(self, operation_id: UUID) -> bool:
        self.cancelled.append(operation_id)
        return True


@dataclass
class PreviewStore:
    content: dict[str, object] = field(default_factory=lambda: PlanContentV1.empty().model_dump())
    previews: dict[int, dict[str, object]] = field(default_factory=dict)
    snapshots: list[dict[str, object]] = field(default_factory=list)

    def content_for_plan(self, plan_id: int) -> dict[str, object]:
        del plan_id
        return deepcopy(self.content)

    def create_preview(self, **values: object) -> object:
        preview_id = len(self.previews) + 1
        self.previews[preview_id] = dict(values)
        return SimpleNamespace(id=preview_id, result=values["result"])

    def reject_preview(self, preview_id: int, *, now_utc_ms: int) -> object:
        del now_utc_ms
        self.previews[preview_id]["status"] = "rejected"
        return SimpleNamespace(id=preview_id)

    @contextmanager
    def adoption_transaction(self, preview_id: int, *, now_utc_ms: int) -> Iterator[object]:
        del now_utc_ms
        stored = self.previews[preview_id]
        candidate = SimpleNamespace(
            plan_id=int(str(stored["lesson_plan_id"])),
            section_code=str(stored["section_code"]),
            result=stored["result"],
            target_section_sha256=str(stored["target_section_sha256"]),
            author_name="测试教师",
            content_schema_version=1,
            content=deepcopy(self.content),
            content_revision=1,
            archived=False,
        )

        def save_snapshot() -> None:
            self.snapshots.append(deepcopy(self.content))

        def update_content(content: dict[str, object]) -> int:
            self.content = deepcopy(content)
            return 2

        yield SimpleNamespace(
            load_candidate=lambda: candidate,
            invalidate=lambda: stored.update(status="invalidated"),
            save_snapshot=save_snapshot,
            update_content=update_content,
            mark_adopted=lambda: stored.update(status="adopted"),
        )


def _module():
    return pending_module("kindergarten_manager.application.ai_generation")


def _coordinator(runtime: ScriptedRuntime | None = None, store: PreviewStore | None = None):
    module = _module()
    coordinator_type = pending_symbol(module, "AiGenerationCoordinator")
    return coordinator_type(runtime=runtime or ScriptedRuntime(), store=store or PreviewStore())


def test_only_one_generation_operation_can_run() -> None:
    coordinator = _coordinator()

    accepted = coordinator.start_single(1, "morning_talk", "春季观察")
    assert accepted.operation_id
    with pytest.raises(Exception) as captured:
        coordinator.start_batch(1, "春季观察")
    assert getattr(captured.value, "code", None) == "ai.operation_in_progress"


def test_batch_keeps_successful_previews_when_one_section_fails() -> None:
    coordinator = _coordinator()
    operation = coordinator.start_batch(1, "春季观察")

    coordinator.accept_result(operation.operation_id, "morning_talk", {"topic": "春天"})
    coordinator.accept_failure(operation.operation_id, "morning_activity", "ai.invalid_output")
    coordinator.accept_result(operation.operation_id, "indoor_area_game", {"areas": ["阅读区"]})

    state = coordinator.state()
    assert set(state.ready_sections) == {"morning_talk", "indoor_area_game"}
    assert state.failed_sections == {"morning_activity": "ai.invalid_output"}


def test_retry_failed_section_preserves_other_successful_previews() -> None:
    coordinator = _coordinator()
    operation = coordinator.start_batch(1, "春季观察")
    coordinator.accept_result(operation.operation_id, "morning_talk", {"topic": "春天"})
    coordinator.accept_failure(operation.operation_id, "morning_activity", "ai.invalid_output")
    coordinator.accept_failure(operation.operation_id, "indoor_area_game", "ai.invalid_output")
    coordinator.accept_failure(
        operation.operation_id, "afternoon_outdoor_game", "ai.invalid_output"
    )

    coordinator.start_single(1, "morning_activity", "重试晨间活动")

    state = coordinator.state()
    assert state.ready_sections == ("morning_talk",)
    assert "morning_activity" not in state.failed_sections
    assert set(state.failed_sections) == {"indoor_area_game", "afternoon_outdoor_game"}


def test_cancel_and_close_discard_late_results() -> None:
    runtime = ScriptedRuntime()
    coordinator = _coordinator(runtime=runtime)
    operation = coordinator.start_single(1, "morning_talk", "春季观察")

    assert coordinator.cancel(operation.operation_id).ok
    coordinator.accept_result(operation.operation_id, "morning_talk", {"topic": "迟到"})
    assert coordinator.state().ready_sections == ()

    missing = coordinator.cancel(UUID(int=999))
    assert missing.ok is False
    assert missing.error_code == "ai.operation_not_found"
    assert missing.message

    second = coordinator.start_single(1, "morning_talk", "春季观察")
    coordinator.close()
    coordinator.accept_result(second.operation_id, "morning_talk", {"topic": "关闭后迟到"})
    assert second.operation_id in runtime.cancelled
    assert coordinator.state().ready_sections == ()


def test_reject_changes_only_preview_and_stale_target_cannot_be_adopted() -> None:
    coordinator = _coordinator()
    operation = coordinator.start_single(1, "morning_talk", "春季观察")
    preview = coordinator.accept_result(
        operation.operation_id,
        "morning_talk",
        {"topic": "春天", "questions": ["你看到了什么？"]},
    )

    rejected = coordinator.reject(preview.preview_id)
    assert rejected.status == "rejected"

    second = coordinator.start_single(1, "morning_talk", "春季观察")
    stale_preview = coordinator.accept_result(
        second.operation_id,
        "morning_talk",
        {"topic": "第二次", "questions": ["为什么？"]},
    )
    coordinator.store.content["morning_talk"] = {"topic": "教师已修改", "questions": []}
    with pytest.raises(Exception) as captured:
        coordinator.adopt(stale_preview.preview_id)
    assert getattr(captured.value, "code", None) == "ai.preview_stale"


def test_adoption_snapshots_before_mutating_current_content() -> None:
    store = PreviewStore()
    before = deepcopy(store.content)
    coordinator = _coordinator(store=store)
    operation = coordinator.start_single(1, "morning_talk", "春季观察")
    preview = coordinator.accept_result(
        operation.operation_id,
        "morning_talk",
        {"topic": "采用内容", "questions": ["看到了什么？"]},
    )

    adopted = coordinator.adopt(preview.preview_id)

    assert store.snapshots == [before]
    assert adopted.content["morning_talk"]["topic"] == "采用内容"


@dataclass
class PersistentPreviewStore(PreviewStore):
    events: list[str] = field(default_factory=list)

    def create_preview(self, **values: object) -> object:
        return SimpleNamespace(id=1, result=values["result"])

    @contextmanager
    def adoption_transaction(self, preview_id: int, *, now_utc_ms: int) -> Iterator[object]:
        del preview_id, now_utc_ms
        self.events.append("transaction")
        candidate = SimpleNamespace(
            plan_id=1,
            section_code="morning_talk",
            result={"schema_version": 1, "topic": "AI 结果", "questions": []},
            target_section_sha256="0" * 64,
            author_name="测试教师",
            content_schema_version=1,
            content=deepcopy(self.content),
            content_revision=1,
            archived=False,
        )
        transaction = SimpleNamespace(
            load_candidate=lambda: candidate,
            invalidate=lambda: self.events.append("invalidated"),
            save_snapshot=lambda: self.events.append("snapshot"),
            update_content=lambda _content: self.events.append("updated") or 2,
            mark_adopted=lambda: self.events.append("adopted"),
        )
        yield transaction


def test_persistent_stale_preview_is_invalidated_inside_application_transaction() -> None:
    store = PersistentPreviewStore()
    coordinator = _coordinator(store=store)
    operation = coordinator.start_single(1, "morning_talk", "春季观察")
    preview = coordinator.accept_result(
        operation.operation_id,
        "morning_talk",
        {"topic": "AI 结果", "questions": []},
    )
    store.content["morning_talk"] = {"topic": "教师已修改", "questions": []}

    with pytest.raises(Exception) as captured:
        coordinator.adopt(preview.preview_id)

    assert getattr(captured.value, "code", None) == "ai.preview_stale"
    assert store.events == ["transaction", "invalidated"]
