"""SQLite Session 工厂公共接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(database_path: Path) -> sessionmaker[Session]:
    raise NotImplementedError("T021 尚未实现 SQLite Session 工厂")
