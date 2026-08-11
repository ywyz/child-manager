from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
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
    previews: dict[str, object] = field(default_factory=dict)
    snapshots: list[dict[str, object]] = field(default_factory=list)

    def transactionally_adopt(self, section_code: str, output: object) -> dict[str, object]:
        self.snapshots.append(deepcopy(self.content))
        self.content[section_code] = deepcopy(output)
        return deepcopy(self.content)


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


def test_cancel_and_close_discard_late_results() -> None:
    runtime = ScriptedRuntime()
    coordinator = _coordinator(runtime=runtime)
    operation = coordinator.start_single(1, "morning_talk", "春季观察")

    assert coordinator.cancel(operation.operation_id).ok
    coordinator.accept_result(operation.operation_id, "morning_talk", {"topic": "迟到"})
    assert coordinator.state().ready_sections == ()

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
