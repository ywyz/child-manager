"""固定 Word 模板渲染接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from pathlib import Path

from kindergarten_manager.application.exports import DailyPlanExportSnapshot


class TeacherplanRenderer:
    def __init__(self, template_path: Path, *, expected_sha256: str) -> None:
        self.template_path = template_path
        self.expected_sha256 = expected_sha256

    def render_day(self, snapshot: DailyPlanExportSnapshot) -> bytes:
        raise NotImplementedError("T028 尚未实现单日 Word 渲染")
