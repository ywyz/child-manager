from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from kindergarten_manager.application.lesson_plans import (
    LessonPlanEditorState,
    LessonPlanError,
    LessonPlanService,
    SaveResult,
)
from kindergarten_manager.domain.content import PlanContentV1
from tests.desktop.conftest import FixedClock
from tests.desktop.helpers import implemented


class RecordingLessonPlanRepository:
    def __init__(self) -> None:
        self._plans: dict[tuple[int, date], LessonPlanEditorState] = {}
        self.open_calls = 0

    def open_or_create(
        self,
        *,
        class_id: int,
        semester_id: int,
        plan_date: date,
        author_name: str,
        now_utc_ms: int,
    ) -> LessonPlanEditorState:
        self.open_calls += 1
        key = (class_id, plan_date)
        if key not in self._plans:
            self._plans[key] = LessonPlanEditorState(
                id=len(self._plans) + 1,
                class_id=class_id,
                semester_id=semester_id,
                plan_date=plan_date,
                author_name=author_name,
                content_revision=1,
                content=PlanContentV1(),
            )
        return self._plans[key]

    def save_content(
        self,
        *,
        plan_id: int,
        base_revision: int,
        content: PlanContentV1,
        now_utc_ms: int,
    ) -> SaveResult:
        state = next(plan for plan in self._plans.values() if plan.id == plan_id)
        if state.content_revision != base_revision:
            raise LessonPlanError("plan.stale_editor_state", "教案已发生变化，请重新加载")
        updated = replace(state, content_revision=base_revision + 1, content=content)
        self._plans[(state.class_id, state.plan_date)] = updated
        return SaveResult(
            plan_id=plan_id, content_revision=updated.content_revision, saved_at_utc_ms=now_utc_ms
        )


def test_open_or_create_is_stable_for_same_class_and_date(fixed_clock: FixedClock) -> None:
    repository = RecordingLessonPlanRepository()
    service = LessonPlanService(
        repository,
        now_utc_ms=fixed_clock.now_utc_ms,
        author_name=lambda: "测试教师",
    )

    first = implemented(lambda: service.open_or_create(1, date(2026, 9, 7), 2))
    second = implemented(lambda: service.open_or_create(1, date(2026, 9, 7), 2))

    assert first.id == second.id
    assert first.content_revision == 1
    assert repository.open_calls == 2


def test_save_increments_revision_and_stale_base_is_rejected(fixed_clock: FixedClock) -> None:
    repository = RecordingLessonPlanRepository()
    service = LessonPlanService(
        repository,
        now_utc_ms=fixed_clock.now_utc_ms,
        author_name=lambda: "测试教师",
    )
    state = repository.open_or_create(
        class_id=1,
        semester_id=2,
        plan_date=date(2026, 9, 7),
        author_name="测试教师",
        now_utc_ms=fixed_clock.now_utc_ms(),
    )
    content = PlanContentV1()

    saved = implemented(lambda: service.save_version(state.id, state.content_revision, content))

    assert saved.content_revision == 2
    with pytest.raises(LessonPlanError) as captured:
        implemented(lambda: service.save_version(state.id, state.content_revision, content))
    assert captured.value.error_code == "plan.stale_editor_state"
