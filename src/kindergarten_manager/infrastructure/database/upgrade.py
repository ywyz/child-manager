"""独立桌面 Alembic 链公共接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from pathlib import Path

DESKTOP_INITIAL_REVISION = "0001_desktop_initial"


def upgrade_database(database_path: Path) -> str:
    raise NotImplementedError("T023/T024 尚未实现桌面 SQLite 迁移")
