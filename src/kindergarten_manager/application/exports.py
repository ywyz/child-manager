"""单日 Word 导出公共接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from kindergarten_manager.application.dto import CancellationToken
from kindergarten_manager.domain.content import PlanContentV1


class ExportError(RuntimeError):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass(frozen=True, slots=True)
class DailyPlanExportSnapshot:
    plan_id: int
    content_revision: int
    plan_date: date
    teaching_week_text: str
    activity_date_text: str
    semester_name: str
    semester_start_date: date
    semester_end_date: date
    kindergarten_name: str
    class_name: str
    age_group: str
    author_name: str
    content: PlanContentV1
    content_sha256: str


@dataclass(frozen=True, slots=True)
class ExportResult:
    destination: Path
    exported_dates: tuple[date, ...]
    skipped: tuple[object, ...] = ()


class ExportService:
    def __init__(self, renderer: object, *, snapshot_reader: object | None = None) -> None:
        self.renderer = renderer
        self.snapshot_reader = snapshot_reader

    def prepare_single(self, plan_id: int) -> DailyPlanExportSnapshot:
        raise NotImplementedError("T029 尚未实现单日 Word 冻结快照")

    def export_single(
        self,
        snapshot: DailyPlanExportSnapshot,
        destination: Path,
        cancellation: CancellationToken,
    ) -> ExportResult:
        raise NotImplementedError("T029 尚未实现单日 Word 原子发布")
