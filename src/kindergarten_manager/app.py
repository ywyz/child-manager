"""桌面应用唯一 composition root；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget

from kindergarten_manager.infrastructure.paths import DesktopPaths


def create_desktop_window(*, paths: DesktopPaths, template_path: Path) -> QWidget:
    raise NotImplementedError("T033 尚未实现桌面应用装配")
