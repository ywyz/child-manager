"""单日 Word 冻结快照与原子发布。"""

from __future__ import annotations

import errno
import os
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

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


class DayRenderer(Protocol):
    def render_day(self, snapshot: DailyPlanExportSnapshot, /) -> bytes: ...

    def validate_day(self, path: Path, snapshot: DailyPlanExportSnapshot, /) -> None: ...


class SnapshotReader(Protocol):
    def load_export_snapshot(self, plan_id: int) -> DailyPlanExportSnapshot | None: ...


class ExportService:
    def __init__(
        self,
        renderer: DayRenderer,
        *,
        snapshot_reader: SnapshotReader | None = None,
    ) -> None:
        self.renderer = renderer
        self.snapshot_reader = snapshot_reader

    def prepare_single(self, plan_id: int) -> DailyPlanExportSnapshot:
        if self.snapshot_reader is None:
            raise ExportError("export.snapshot_reader_missing", "导出数据读取器未配置")
        snapshot = self.snapshot_reader.load_export_snapshot(plan_id)
        if snapshot is None:
            raise ExportError("plan.not_found", "教案不存在")
        return snapshot

    def export_single(
        self,
        snapshot: DailyPlanExportSnapshot,
        destination: Path,
        cancellation: CancellationToken,
    ) -> ExportResult:
        if cancellation.cancel_requested:
            raise ExportError("export.cancelled", "导出已取消")
        try:
            payload = self.renderer.render_day(snapshot)
        except OSError as error:
            if error.errno == errno.ENOSPC:
                raise ExportError("export.no_space", "磁盘空间不足，无法导出") from error
            raise ExportError("export.render_failed", "生成 Word 文档失败") from error
        except Exception as error:
            error_code = getattr(error, "error_code", None)
            if isinstance(error_code, str):
                raise ExportError(error_code, str(error)) from error
            raise ExportError("export.render_failed", "生成 Word 文档失败") from error

        destination = Path(destination)
        temporary: Path | None = None
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{destination.name}.",
                suffix=".tmp",
                dir=destination.parent,
            )
            temporary = Path(temporary_name)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                self.renderer.validate_day(temporary, snapshot)
            except ExportError:
                raise
            except Exception as error:
                error_code = getattr(error, "error_code", None)
                if isinstance(error_code, str):
                    raise ExportError(error_code, str(error)) from error
                raise ExportError(
                    "export.validation_failed",
                    "Word 文档重新打开校验失败",
                ) from error
            if cancellation.cancel_requested:
                raise ExportError("export.cancelled", "导出已取消")
            try:
                os.replace(temporary, destination)
            except PermissionError as error:
                raise ExportError("export.destination_locked", "目标文件正被占用") from error
            except OSError as error:
                if error.errno == errno.ENOSPC:
                    raise ExportError("export.no_space", "磁盘空间不足，无法导出") from error
                raise ExportError("export.publish_failed", "发布 Word 文件失败") from error
            temporary = None
        except ExportError:
            raise
        except OSError as error:
            if error.errno == errno.ENOSPC:
                raise ExportError("export.no_space", "磁盘空间不足，无法导出") from error
            raise ExportError("export.publish_failed", "写入 Word 文件失败") from error
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        return ExportResult(destination=destination, exported_dates=(snapshot.plan_date,))
