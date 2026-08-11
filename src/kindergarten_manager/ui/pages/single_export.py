"""单日 Word 导出页面动作。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox, QWidget

from kindergarten_manager.ui.errors import user_error_message
from kindergarten_manager.ui.ports import DesktopServices


def export_current_day(
    *,
    parent: QWidget,
    services: DesktopServices,
    status: QLabel,
) -> None:
    documents = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    initial = str(Path(documents) / services.suggested_export_filename()) if documents else ""
    selected, _filter = QFileDialog.getSaveFileName(
        parent,
        "导出当天 Word",
        initial,
        "Word 文档 (*.docx)",
    )
    destination = Path(selected) if selected else None
    if destination is None:
        status.setText("已取消导出")
        return
    if destination.exists():
        answer = QMessageBox.question(
            parent,
            "确认覆盖",
            "目标文件已存在，是否覆盖？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            status.setText("已取消导出")
            return
    try:
        services.export_current_day(destination)
    except Exception as error:
        status.setText(user_error_message(error, "导出失败，请检查目标文件后重试"))
        return
    status.setText(f"已导出：{destination.name}")
