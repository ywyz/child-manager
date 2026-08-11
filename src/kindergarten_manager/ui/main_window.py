"""首次设置与当天教案的桌面主窗口。"""

from __future__ import annotations

from typing import cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QStackedWidget, QVBoxLayout, QWidget

from kindergarten_manager.ui.pages.daily_plan import DailyPlanPage
from kindergarten_manager.ui.pages.first_run import build_first_run_page
from kindergarten_manager.ui.pages.settings import SettingsPage
from kindergarten_manager.ui.ports import DesktopServices
from kindergarten_manager.ui.theme import (
    ThemePreference,
    desktop_stylesheet,
    resolve_theme,
)


class DesktopMainWindow(QWidget):
    def __init__(self, services: DesktopServices) -> None:
        super().__init__()
        self.setObjectName("desktop_shell")
        self.setWindowTitle("幼儿园管理助手")
        self.resize(1366, 768)
        self.setMinimumSize(1100, 680)
        self._services = services
        self._theme_preference: ThemePreference = "system"
        self._apply_theme(self._theme_preference)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self.stack.setObjectName("main_stack")
        self._editor = DailyPlanPage(services, on_open_settings=self._open_settings)
        self._settings_page = SettingsPage(
            services,
            on_theme_changed=self._settings_saved,
            on_back=self._back_to_plan,
        )
        self.stack.addWidget(build_first_run_page(self._complete_setup))
        self.stack.addWidget(self._editor)
        self.stack.addWidget(self._settings_page)
        layout.addWidget(self.stack)

        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.styleHints().colorSchemeChanged.connect(self._system_theme_changed)

        if _setup_complete(services):
            self._apply_theme(_validated_theme(services.load_settings().theme))
            self._editor.reload()
            self.stack.setCurrentIndex(1)

    def _complete_setup(self, values: dict[str, str]) -> None:
        self._services.complete_setup(values)
        self._apply_theme(_validated_theme(self._services.load_settings().theme))
        self._editor.reload()
        self.stack.setCurrentIndex(1)

    def _open_settings(self) -> None:
        self._settings_page.reload()
        self.stack.setCurrentWidget(self._settings_page)

    def _back_to_plan(self) -> None:
        self._editor.reload()
        self.stack.setCurrentWidget(self._editor)

    def _settings_saved(self, theme: str) -> None:
        self._apply_theme(_validated_theme(theme))
        self._editor.reload()

    def _system_theme_changed(self, _color_scheme: Qt.ColorScheme) -> None:
        if self._theme_preference == "system":
            self._apply_theme("system")

    def _apply_theme(self, preference: ThemePreference) -> None:
        self._theme_preference = preference
        app = QApplication.instance()
        system_is_dark = bool(
            isinstance(app, QApplication) and app.styleHints().colorScheme() == Qt.ColorScheme.Dark
        )
        theme = resolve_theme(preference, system_is_dark=system_is_dark)
        self.setStyleSheet(desktop_stylesheet(theme))


def _setup_complete(services: DesktopServices) -> bool:
    explicit = getattr(services, "setup_complete", None)
    if isinstance(explicit, bool):
        return explicit
    setup = getattr(services, "setup", None)
    return bool(setup)


def _validated_theme(value: str) -> ThemePreference:
    if value not in {"system", "light", "dark"}:
        return "system"
    return cast(ThemePreference, value)
