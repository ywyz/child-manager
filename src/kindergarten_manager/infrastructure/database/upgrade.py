"""独立桌面 Alembic 链入口。"""

from __future__ import annotations

import os
import sqlite3
import uuid
from contextlib import suppress
from hashlib import sha256
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from kindergarten_manager.infrastructure.database.engine import create_sqlite_engine

DESKTOP_INITIAL_REVISION = "0001_desktop_initial"
DESKTOP_HEAD_REVISION = "0002_desktop_ai"


class MigrationProtectionError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def upgrade_database(
    database_path: Path,
    *,
    pre_migration_directory: Path | None = None,
) -> str:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    current_revision = _read_current_revision(path)
    if current_revision not in {None, DESKTOP_INITIAL_REVISION, DESKTOP_HEAD_REVISION}:
        raise RuntimeError("桌面数据库版本高于当前应用")
    if current_revision == DESKTOP_INITIAL_REVISION:
        if pre_migration_directory is None:
            raise MigrationProtectionError(
                "migration.protective_backup_failed",
                "迁移前保护副本目录未配置",
            )
        _create_verified_protective_copy(path, Path(pre_migration_directory))

    migrations = Path(__file__).with_name("migrations")
    config = Config()
    config.set_main_option("script_location", str(migrations))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{path}")
    command.upgrade(config, "head")

    with create_sqlite_engine(path).connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    if revision != DESKTOP_HEAD_REVISION:
        raise RuntimeError("桌面数据库迁移未到达预期版本")
    return revision


def _read_current_revision(path: Path) -> str | None:
    if not path.exists():
        return None
    with sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True) as connection:
        has_version_table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'alembic_version'"
        ).fetchone()
        if has_version_table is None:
            return None
        row = connection.execute("SELECT version_num FROM alembic_version").fetchone()
        return str(row[0]) if row is not None else None


def _create_verified_protective_copy(database: Path, directory: Path) -> Path:
    suffix = uuid.uuid4().hex
    target = directory / f"pre-migration-{suffix}.sqlite3"
    partial = directory / f".pre-migration-{suffix}.partial"
    try:
        directory.mkdir(parents=True, exist_ok=True)
        with (
            sqlite3.connect(f"file:{database.resolve()}?mode=ro", uri=True) as source,
            sqlite3.connect(partial) as destination,
        ):
            source.backup(destination)
        with sqlite3.connect(f"file:{partial.resolve()}?mode=ro", uri=True) as verification:
            if verification.execute("PRAGMA integrity_check").fetchone() != ("ok",):
                raise sqlite3.DatabaseError("protective copy integrity check failed")
            if verification.execute("PRAGMA foreign_key_check").fetchall():
                raise sqlite3.DatabaseError("protective copy foreign key check failed")
            revision = verification.execute("SELECT version_num FROM alembic_version").fetchone()
            if revision != (DESKTOP_INITIAL_REVISION,):
                raise sqlite3.DatabaseError("protective copy revision check failed")
        with partial.open("r+b") as handle:
            os.fsync(handle.fileno())
        expected_sha256 = _sha256_file(partial)
        partial.replace(target)
        if _sha256_file(target) != expected_sha256:
            raise OSError("protective copy checksum mismatch")
        return target
    except (OSError, sqlite3.Error) as error:
        with suppress(OSError):
            partial.unlink(missing_ok=True)
        with suppress(OSError):
            target.unlink(missing_ok=True)
        raise MigrationProtectionError(
            "migration.protective_backup_failed",
            "迁移前保护副本创建或校验失败",
        ) from error


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
