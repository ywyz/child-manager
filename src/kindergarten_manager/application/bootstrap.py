"""桌面启动与 SQLite 状态门禁。"""

from __future__ import annotations

import sqlite3
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

from kindergarten_manager.infrastructure.database.engine import connect_sqlite
from kindergarten_manager.infrastructure.database.upgrade import (
    DESKTOP_HEAD_REVISION,
    DESKTOP_INITIAL_REVISION,
    MigrationProtectionError,
    upgrade_database,
)
from kindergarten_manager.infrastructure.paths import DesktopPaths


class StartupError(RuntimeError):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass(frozen=True, slots=True)
class StartupState:
    data_root: Path
    schema_revision: str
    first_run: bool
    setup_complete: bool
    daily_backup: str
    warnings: tuple[str, ...] = ()


class BootstrapService:
    def __init__(self, paths: DesktopPaths) -> None:
        self.paths = paths

    def start(self) -> StartupState:
        self._check_paths()
        existed = self.paths.database.exists()
        if existed and not self._is_writable_file():
            raise StartupError("startup.database_read_only", "本地数据库为只读，无法安全启动")

        try:
            revision = self._read_revision() if existed else None
        except sqlite3.DatabaseError as error:
            raise StartupError(
                "startup.database_corrupt", "本地数据库已损坏，无法安全启动"
            ) from error

        if existed:
            self._verify_database()

        if revision not in {None, DESKTOP_INITIAL_REVISION, DESKTOP_HEAD_REVISION}:
            raise StartupError("startup.future_schema", "本地数据库版本高于当前应用")

        try:
            revision = upgrade_database(
                self.paths.database,
                pre_migration_directory=self.paths.pre_migration_backups,
            )
            setup_complete = self._setup_complete()
            self._verify_database()
        except MigrationProtectionError as error:
            raise StartupError(
                "startup.backup_failed",
                "迁移前保护副本创建失败，数据库未升级",
            ) from error
        except sqlite3.DatabaseError as error:
            raise StartupError(
                "startup.database_corrupt", "本地数据库已损坏，无法安全启动"
            ) from error
        except StartupError:
            raise
        except Exception as error:
            raise StartupError("startup.migration_failed", "本地数据库升级失败") from error

        return StartupState(
            data_root=self.paths.root,
            schema_revision=revision,
            first_run=not setup_complete,
            setup_complete=setup_complete,
            daily_backup="not_due",
        )

    def _check_paths(self) -> None:
        try:
            self.paths.ensure_directories()
            for directory in self.paths.directories:
                mode = directory.stat().st_mode
                if not mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
                    raise PermissionError(directory)
            with tempfile.NamedTemporaryFile(dir=self.paths.data):
                pass
        except OSError as error:
            raise StartupError(
                "startup.path_unavailable",
                "本地数据目录不可写或空间不足",
            ) from error

    def _is_writable_file(self) -> bool:
        mode = self.paths.database.stat().st_mode
        return bool(mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))

    def _read_revision(self) -> str | None:
        with connect_sqlite(self.paths.database, read_only=True) as connection:
            row = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'alembic_version'"
            ).fetchone()
            if row is None:
                return None
            revision = connection.execute("SELECT version_num FROM alembic_version").fetchone()
            return str(revision[0]) if revision is not None else None

    def _setup_complete(self) -> bool:
        with connect_sqlite(self.paths.database) as connection:
            required = (
                "app_profile",
                "kindergarten_settings",
                "class_groups",
                "semesters",
            )
            return all(
                connection.execute(f"SELECT EXISTS(SELECT 1 FROM {table})").fetchone()[0]
                for table in required
            )

    def _verify_database(self) -> None:
        with connect_sqlite(self.paths.database) as connection:
            if connection.execute("PRAGMA quick_check").fetchone() != ("ok",):
                raise StartupError("startup.database_corrupt", "本地数据库完整性检查失败")
            if connection.execute("PRAGMA foreign_key_check").fetchall():
                raise StartupError("startup.database_corrupt", "本地数据库外键检查失败")
