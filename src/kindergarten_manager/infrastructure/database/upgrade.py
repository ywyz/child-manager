"""独立桌面 Alembic 链入口。"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from kindergarten_manager.infrastructure.database.engine import create_sqlite_engine

DESKTOP_INITIAL_REVISION = "0001_desktop_initial"


def upgrade_database(database_path: Path) -> str:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    migrations = Path(__file__).with_name("migrations")
    config = Config()
    config.set_main_option("script_location", str(migrations))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{path}")
    command.upgrade(config, "head")

    with create_sqlite_engine(path).connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    if revision != DESKTOP_INITIAL_REVISION:
        raise RuntimeError("桌面数据库迁移未到达预期版本")
    return revision
