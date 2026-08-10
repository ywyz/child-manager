"""首次设置与当天教案的桌面主窗口。"""

from __future__ import annotations

from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from kindergarten_manager.ui.pages.daily_plan import DailyPlanPage
from kindergarten_manager.ui.pages.first_run import build_first_run_page
from kindergarten_manager.ui.ports import DesktopServices
from kindergarten_manager.ui.theme import desktop_stylesheet


class DesktopMainWindow(QWidget):
    def __init__(self, services: DesktopServices) -> None:
        super().__init__()
        self.setObjectName("desktop_shell")
        self.setWindowTitle("幼儿园一日活动计划")
        self.resize(1366, 768)
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(desktop_stylesheet())
        self._services = services

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self.stack.setObjectName("main_stack")
        self._editor = DailyPlanPage(services)
        self.stack.addWidget(build_first_run_page(self._complete_setup))
        self.stack.addWidget(self._editor)
        layout.addWidget(self.stack)

        if _setup_complete(services):
            self._editor.reload()
            self.stack.setCurrentIndex(1)

    def _complete_setup(self, values: dict[str, str]) -> None:
        self._services.complete_setup(values)
        self._editor.reload()
        self.stack.setCurrentIndex(1)


def _setup_complete(services: DesktopServices) -> bool:
    explicit = getattr(services, "setup_complete", None)
    if isinstance(explicit, bool):
        return explicit
    setup = getattr(services, "setup", None)
    return bool(setup)
