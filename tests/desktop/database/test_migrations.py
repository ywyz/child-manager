from __future__ import annotations

import errno
import hashlib
import os
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config

from kindergarten_manager.infrastructure.database.models import metadata
from kindergarten_manager.infrastructure.database.upgrade import (
    DESKTOP_HEAD_REVISION,
    DESKTOP_INITIAL_REVISION,
    MigrationProtectionError,
    upgrade_database,
)
from tests.desktop.helpers import implemented


def _schema_objects(database: Path) -> dict[str, str]:
    with sqlite3.connect(database) as connection:
        return {
            name: sql or ""
            for name, sql in connection.execute(
                "SELECT name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
            )
        }


def _migration_source_sha256(path: Path) -> str:
    source = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(source).hexdigest()


def test_migration_source_hash_is_independent_of_platform_line_endings(
    tmp_path: Path,
) -> None:
    migration = tmp_path / "0001_example.py"
    migration.write_bytes(b"revision = '0001'\r\n")

    assert (
        _migration_source_sha256(migration)
        == "a987ebd17e75e71ab4352733fd47de6e236cff317398918cec570fc7df181207"
    )


def test_empty_database_upgrades_idempotently_with_named_integrity_contracts(
    tmp_path: Path,
) -> None:
    database = tmp_path / "desktop.sqlite3"

    first = implemented(lambda: upgrade_database(database))
    second = implemented(lambda: upgrade_database(database))
    objects = _schema_objects(database)

    assert first == second == DESKTOP_HEAD_REVISION
    assert set(objects) == {
        "alembic_version",
        "app_profile",
        "kindergarten_settings",
        "class_groups",
        "class_areas",
        "semesters",
        "lesson_plans",
        "lesson_plan_versions",
        "calendar_overrides",
        "ai_configuration",
        "prompt_overrides",
        "ai_previews",
        "uq_class_groups_name_nocase",
        "uq_class_areas_class_type_name_nocase",
        "uq_semesters_one_current",
        "uq_lesson_plans_class_date",
        "trg_lesson_plan_versions_immutable_update",
        "trg_lesson_plan_versions_immutable_delete",
        "uq_ai_previews_operation_section",
        "ix_ai_previews_plan_state",
    }
    combined_sql = "\n".join(objects.values()).lower()
    for name in (
        "ck_app_profile_singleton",
        "ck_app_profile_theme",
        "ck_kindergarten_settings_singleton",
        "ck_kindergarten_settings_timezone",
        "ck_class_groups_age_group",
        "fk_class_areas_class_id_class_groups",
        "ck_class_areas_area_type",
        "uq_class_groups_name_nocase",
        "uq_class_areas_class_type_name_nocase",
        "ck_semesters_date_range",
        "uq_semesters_one_current",
        "fk_lesson_plans_class_id_class_groups",
        "fk_lesson_plans_semester_id_semesters",
        "uq_lesson_plans_class_date",
        "fk_lesson_plan_versions_plan_id_lesson_plans",
        "trg_lesson_plan_versions_immutable_update",
        "trg_lesson_plan_versions_immutable_delete",
        "ck_ai_configuration_singleton",
        "ck_ai_configuration_credential_configured",
        "ck_ai_configuration_enabled",
        "ck_prompt_overrides_prompt_code",
        "ck_prompt_overrides_content",
        "fk_ai_previews_lesson_plan_id_lesson_plans",
        "ck_ai_previews_section_code",
        "ck_ai_previews_result_schema_code",
        "ck_ai_previews_state",
        "uq_ai_previews_operation_section",
        "ix_ai_previews_plan_state",
    ):
        assert name in combined_sql
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == (
            DESKTOP_HEAD_REVISION,
        )
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []

    migrations = Path("src/kindergarten_manager/infrastructure/database/migrations")
    assert (migrations / "env.py").is_file()
    assert (migrations / "versions" / "0001_desktop_initial.py").is_file()
    assert (migrations / "versions" / "0002_desktop_ai.py").is_file()
    assert (migrations / "versions" / "0003_desktop_ai_profiles.py").is_file()
    assert (
        _migration_source_sha256(migrations / "versions" / "0001_desktop_initial.py")
        == "a1d55d374ffa6144d2e772f2f2b7cc33a5e76e94c0c5d22b02fc13e41db844e5"
    )
    assert "render_as_batch=True" in (migrations / "env.py").read_text(encoding="utf-8")
    assert all(
        ".create_all(" not in source.read_text(encoding="utf-8")
        for source in Path("src/kindergarten_manager").rglob("*.py")
    )


def test_existing_ai_database_adds_an_isolated_vision_profile(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    migrations = Path("src/kindergarten_manager/infrastructure/database/migrations")
    config = Config()
    config.set_main_option("script_location", str(migrations))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database}")
    command.upgrade(config, "0002_desktop_ai")
    with sqlite3.connect(database) as connection:
        connection.execute(
            "INSERT INTO ai_configuration VALUES (1, ?, ?, 1, 1, 1, 1)",
            ("https://text.example.test/v1", "text-model"),
        )

    assert upgrade_database(database, pre_migration_directory=tmp_path / "backups") == (
        DESKTOP_HEAD_REVISION
    )

    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT base_url, model_name, vision_base_url, vision_model_name, "
            "vision_credential_configured, vision_enabled FROM ai_configuration WHERE id = 1"
        ).fetchone()
    assert row == ("https://text.example.test/v1", "text-model", None, None, 0, 0)


def test_version_rows_are_immutable_at_database_boundary(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    implemented(lambda: upgrade_database(database))

    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            "INSERT INTO app_profile VALUES (1, ?, ?, ?, NULL, 1, 1)",
            ("cn.kindergartenmanager.desktop", "测试教师", "system"),
        )
        connection.execute(
            "INSERT INTO kindergarten_settings VALUES (1, ?, ?, 1, 1)",
            ("星河幼儿园", "Asia/Shanghai"),
        )
        class_id = connection.execute(
            "INSERT INTO class_groups("
            "name, age_group, sort_order, is_active, created_at_utc_ms, updated_at_utc_ms"
            ") "
            "VALUES (?, ?, 0, 1, 1, 1) RETURNING id",
            ("向日葵班", "middle"),
        ).fetchone()[0]
        semester_id = connection.execute(
            "INSERT INTO semesters("
            "name, start_date, end_date, is_current, created_at_utc_ms, updated_at_utc_ms"
            ") "
            "VALUES (?, ?, ?, 1, 1, 1) RETURNING id",
            ("2026 秋季", "2026-09-01", "2027-01-31"),
        ).fetchone()[0]
        plan_id = connection.execute(
            "INSERT INTO lesson_plans(class_id, semester_id, plan_date, author_name, "
            "content_schema_version, content_json, content_revision, "
            "created_at_utc_ms, updated_at_utc_ms) "
            "VALUES (?, ?, ?, ?, 1, ?, 1, 1, 1) RETURNING id",
            (class_id, semester_id, "2026-09-07", "测试教师", '{"schema_version":1}'),
        ).fetchone()[0]
        version_id = connection.execute(
            "INSERT INTO lesson_plan_versions(lesson_plan_id, reason, description, author_name, "
            "content_schema_version, content_json, source_revision, created_at_utc_ms) "
            "VALUES (?, ?, NULL, ?, 1, ?, 1, 1) RETURNING id",
            (plan_id, "explicit_save", "测试教师", '{"schema_version":1}'),
        ).fetchone()[0]

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE lesson_plan_versions SET description = 'changed' WHERE id = ?",
                (version_id,),
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("DELETE FROM lesson_plan_versions WHERE id = ?", (version_id,))


def test_sqlalchemy_metadata_exposes_named_constraints_and_indexes() -> None:
    constraint_names = {
        constraint.name
        for table in metadata.tables.values()
        for constraint in table.constraints
        if constraint.name is not None
    }
    index_names = {
        index.name
        for table in metadata.tables.values()
        for index in table.indexes
        if index.name is not None
    }

    assert "fk_lesson_plans_class_id_class_groups" in constraint_names
    assert "ck_lesson_plans_revision" in constraint_names
    assert "uq_lesson_plans_class_date" in index_names
    assert "uq_semesters_one_current" in index_names
    assert "fk_ai_previews_lesson_plan_id_lesson_plans" in constraint_names
    assert "ck_ai_previews_state" in constraint_names
    assert "uq_ai_previews_operation_section" in index_names
    assert "ix_ai_previews_plan_state" in index_names
    assert isinstance(metadata.naming_convention, dict)
    assert sa.ForeignKeyConstraint in {
        type(item) for table in metadata.tables.values() for item in table.constraints
    }


def test_0001_to_0002_creates_verified_pre_migration_copy_before_upgrade(
    tmp_path: Path,
) -> None:
    database = tmp_path / "desktop.sqlite3"
    backups = tmp_path / "pre-migration"
    _upgrade_to_0001(database)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "INSERT INTO app_profile VALUES (1, ?, ?, ?, NULL, 1, 1)",
            ("cn.kindergartenmanager.desktop", "迁移测试教师", "system"),
        )

    revision = implemented(lambda: upgrade_database(database, pre_migration_directory=backups))

    assert revision == DESKTOP_HEAD_REVISION
    backup_files = list(backups.glob("*.sqlite3"))
    assert len(backup_files) == 1
    with sqlite3.connect(backup_files[0]) as backup:
        assert backup.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert backup.execute("PRAGMA foreign_key_check").fetchall() == []
        assert backup.execute("SELECT version_num FROM alembic_version").fetchone() == (
            DESKTOP_INITIAL_REVISION,
        )
        assert backup.execute("SELECT teacher_display_name FROM app_profile").fetchone() == (
            "迁移测试教师",
        )
        assert (
            backup.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'ai_previews'"
            ).fetchone()
            is None
        )
    with sqlite3.connect(database) as active:
        assert active.execute("SELECT version_num FROM alembic_version").fetchone() == (
            DESKTOP_HEAD_REVISION,
        )
        assert active.execute("SELECT teacher_display_name FROM app_profile").fetchone() == (
            "迁移测试教师",
        )


def test_0001_to_0002_fsyncs_protective_copy_with_windows_writable_descriptor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "desktop.sqlite3"
    backups = tmp_path / "pre-migration"
    _upgrade_to_0001(database)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "INSERT INTO app_profile VALUES (1, ?, ?, ?, NULL, 1, 1)",
            ("cn.kindergartenmanager.desktop", "Windows 迁移教师", "system"),
        )

    real_open: Any = Path.open
    real_fsync = os.fsync
    real_connect: Any = sqlite3.connect
    real_replace = Path.replace
    open_modes: dict[int, str] = {}
    locked_paths: Counter[Path] = Counter()

    class WindowsLockingConnection(sqlite3.Connection):
        locked_path: Path | None = None

        def close(self) -> None:
            if self.locked_path is not None:
                locked_paths[self.locked_path] -= 1
                if locked_paths[self.locked_path] == 0:
                    del locked_paths[self.locked_path]
                self.locked_path = None
            super().close()

    def windows_connect(database_path: str | bytes | Path, *args: Any, **kwargs: Any):
        kwargs["factory"] = WindowsLockingConnection
        connection = real_connect(database_path, *args, **kwargs)
        raw_path = os.fsdecode(database_path)
        if raw_path.startswith("file:"):
            raw_path = raw_path.removeprefix("file:").split("?", maxsplit=1)[0]
        resolved_path = Path(raw_path).resolve()
        if resolved_path.suffix == ".partial":
            connection.locked_path = resolved_path
            locked_paths[resolved_path] += 1
        return connection

    def recording_open(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> Any:
        handle = real_open(path, mode, buffering, encoding, errors, newline)
        open_modes[handle.fileno()] = mode
        return handle

    def windows_fsync(file_descriptor: int) -> None:
        mode = open_modes[file_descriptor]
        if not any(marker in mode for marker in ("+", "w", "a")):
            raise OSError(errno.EBADF, "Bad file descriptor")
        real_fsync(file_descriptor)

    def windows_replace(path: Path, target: Path) -> Path:
        if path.resolve() in locked_paths:
            raise PermissionError(32, "另一个程序正在使用此文件", path, target)
        return real_replace(path, target)

    monkeypatch.setattr(Path, "open", recording_open)
    monkeypatch.setattr(Path, "replace", windows_replace)
    monkeypatch.setattr(os, "fsync", windows_fsync)
    monkeypatch.setattr(sqlite3, "connect", windows_connect)

    first_revision = upgrade_database(database, pre_migration_directory=backups)
    restarted_revision = upgrade_database(database, pre_migration_directory=backups)

    assert first_revision == restarted_revision == DESKTOP_HEAD_REVISION
    backup_files = list(backups.glob("*.sqlite3"))
    assert len(backup_files) == 1
    with sqlite3.connect(backup_files[0]) as backup:
        assert backup.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert backup.execute("SELECT version_num FROM alembic_version").fetchone() == (
            DESKTOP_INITIAL_REVISION,
        )
        assert backup.execute("SELECT teacher_display_name FROM app_profile").fetchone() == (
            "Windows 迁移教师",
        )
    with sqlite3.connect(database) as active:
        assert active.execute("SELECT version_num FROM alembic_version").fetchone() == (
            DESKTOP_HEAD_REVISION,
        )
        assert active.execute("SELECT teacher_display_name FROM app_profile").fetchone() == (
            "Windows 迁移教师",
        )


def test_failed_pre_migration_copy_stops_before_schema_or_data_changes(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    invalid_backup_directory = tmp_path / "not-a-directory"
    invalid_backup_directory.write_text("占位文件", encoding="utf-8")
    _upgrade_to_0001(database)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "INSERT INTO app_profile VALUES (1, ?, ?, ?, NULL, 1, 1)",
            ("cn.kindergartenmanager.desktop", "保留数据教师", "system"),
        )

    with pytest.raises(MigrationProtectionError) as captured:
        implemented(
            lambda: upgrade_database(
                database,
                pre_migration_directory=invalid_backup_directory,
            )
        )

    assert captured.value.code == "migration.protective_backup_failed"
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == (
            DESKTOP_INITIAL_REVISION,
        )
        assert connection.execute("SELECT teacher_display_name FROM app_profile").fetchone() == (
            "保留数据教师",
        )
        assert (
            connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'ai_previews'"
            ).fetchone()
            is None
        )


def test_checksum_mismatch_removes_protective_copy_and_stops_migration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "desktop.sqlite3"
    backups = tmp_path / "pre-migration"
    _upgrade_to_0001(database)
    checksums = iter(("before-replace", "after-replace"))
    monkeypatch.setattr(
        "kindergarten_manager.infrastructure.database.upgrade._sha256_file",
        lambda _path: next(checksums),
    )

    with pytest.raises(MigrationProtectionError) as captured:
        upgrade_database(database, pre_migration_directory=backups)

    assert captured.value.code == "migration.protective_backup_failed"
    assert list(backups.iterdir()) == []
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == (
            DESKTOP_INITIAL_REVISION,
        )


def _upgrade_to_0001(database: Path) -> None:
    migrations = Path("src/kindergarten_manager/infrastructure/database/migrations")
    config = Config()
    config.set_main_option("script_location", str(migrations))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database}")
    command.upgrade(config, DESKTOP_INITIAL_REVISION)
