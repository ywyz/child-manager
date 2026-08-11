"""`python -m kindergarten_manager` 桌面入口。"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from kindergarten_manager.app import create_desktop_window
from kindergarten_manager.application.bootstrap import StartupError
from kindergarten_manager.infrastructure.paths import resolve_desktop_paths


def main() -> int:
    application = QApplication.instance() or QApplication(sys.argv)
    try:
        paths = resolve_desktop_paths()
    except OSError as error:
        raise StartupError(
            "startup.path_unavailable",
            "本地数据目录不可用，无法安全启动",
        ) from error
    template = (
        Path(__file__).resolve().parents[2] / "templates" / "teacherplan" / "teacherplan.docx"
    )
    window = create_desktop_window(paths=paths, template_path=template)
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
