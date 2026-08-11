"""单日教案应用用例。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from kindergarten_manager.domain.content import PlanContentV1


class LessonPlanError(RuntimeError):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass(frozen=True, slots=True)
class LessonPlanEditorState:
    id: int
    class_id: int
    semester_id: int
    plan_date: date
    author_name: str
    content_revision: int
    content: PlanContentV1
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SaveResult:
    plan_id: int
    content_revision: int
    saved_at_utc_ms: int


class LessonPlanRepositoryPort(Protocol):
    def open_or_create(
        self,
        *,
        class_id: int,
        semester_id: int,
        plan_date: date,
        author_name: str,
        now_utc_ms: int,
    ) -> LessonPlanEditorState: ...

    def save_content(
        self,
        *,
        plan_id: int,
        base_revision: int,
        content: PlanContentV1,
        now_utc_ms: int,
    ) -> SaveResult: ...


class LessonPlanService:
    def __init__(
        self,
        repository: LessonPlanRepositoryPort,
        *,
        now_utc_ms: Callable[[], int],
        author_name: Callable[[], str],
    ) -> None:
        self.repository = repository
        self.now_utc_ms = now_utc_ms
        self.author_name = author_name

    def open_or_create(
        self,
        class_id: int,
        plan_date: date,
        semester_id: int,
    ) -> LessonPlanEditorState:
        if class_id <= 0 or semester_id <= 0:
            raise LessonPlanError("plan.invalid_context", "班级或学期无效")
        author_name = self.author_name().strip()
        if not author_name:
            raise LessonPlanError("plan.author_missing", "请先设置编写教师")
        return self.repository.open_or_create(
            class_id=class_id,
            semester_id=semester_id,
            plan_date=plan_date,
            author_name=author_name,
            now_utc_ms=self.now_utc_ms(),
        )

    def save_version(
        self,
        plan_id: int,
        base_revision: int,
        content: PlanContentV1,
        description: str | None = None,
    ) -> SaveResult:
        if description is not None and len(description.strip()) > 200:
            raise LessonPlanError("plan.description_too_long", "版本说明不能超过 200 字")
        return self.repository.save_content(
            plan_id=plan_id,
            base_revision=base_revision,
            content=content,
            now_utc_ms=self.now_utc_ms(),
        )
