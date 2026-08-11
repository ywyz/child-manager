"""桌面应用唯一 composition root。"""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import date
from pathlib import Path

from PySide6.QtWidgets import QWidget

from kindergarten_manager.application.bootstrap import BootstrapService
from kindergarten_manager.application.lesson_plans import LessonPlanService
from kindergarten_manager.application.settings import SettingsService
from kindergarten_manager.application.workspace import DailyPlanWorkspace
from kindergarten_manager.infrastructure.database.engine import create_session_factory
from kindergarten_manager.infrastructure.database.repositories import (
    LessonPlanRepository,
    SettingsRepository,
    WorkspaceRepository,
)
from kindergarten_manager.infrastructure.exports.teacherplan_renderer import TeacherplanRenderer
from kindergarten_manager.infrastructure.paths import DesktopPaths
from kindergarten_manager.ui.main_window import DesktopMainWindow

TEMPLATE_SHA256 = "72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043"


def _now_utc_ms() -> int:
    return time.time_ns() // 1_000_000


def create_desktop_window(
    *,
    paths: DesktopPaths,
    template_path: Path,
    today: Callable[[], date] = date.today,
) -> QWidget:
    startup = BootstrapService(paths).start()
    session_factory = create_session_factory(paths.database)
    workspace_repository = WorkspaceRepository(session_factory)
    services = DailyPlanWorkspace(
        settings=SettingsService(
            SettingsRepository(session_factory),
            now_utc_ms=_now_utc_ms,
        ),
        plans=LessonPlanService(
            LessonPlanRepository(session_factory),
            now_utc_ms=_now_utc_ms,
            author_name=workspace_repository.get_author_name,
        ),
        repository=workspace_repository,
        renderer=TeacherplanRenderer(template_path, expected_sha256=TEMPLATE_SHA256),
        today=today,
        setup_complete=startup.setup_complete,
    )
    return DesktopMainWindow(services)
