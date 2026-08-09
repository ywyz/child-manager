"""单日教案应用服务接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

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


class LessonPlanService:
    def __init__(
        self,
        repository: object,
        *,
        now_utc_ms: object,
        author_name: object,
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
        raise NotImplementedError("T027 尚未实现教案打开或创建")

    def save_version(
        self,
        plan_id: int,
        base_revision: int,
        content: PlanContentV1,
        description: str | None = None,
    ) -> SaveResult:
        raise NotImplementedError("T027 尚未实现教案正文保存")
