from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from kindergarten_manager.application.bootstrap import BootstrapService, StartupError
from kindergarten_manager.infrastructure.database.upgrade import (
    DESKTOP_HEAD_REVISION,
    MigrationProtectionError,
)
from kindergarten_manager.infrastructure.paths import DesktopPaths
from tests.desktop.helpers import implemented


def _paths(root: Path) -> DesktopPaths:
    paths = DesktopPaths(
        root=root,
        data=root / "data",
        database=root / "data" / "child-manager.sqlite3",
        backups=root / "backups",
        daily_backups=root / "backups" / "daily",
        pre_migration_backups=root / "backups" / "pre-migration",
        pre_restore_backups=root / "backups" / "pre-restore",
        recovery=root / "recovery",
        staging=root / "staging",
        cache=root / "cache",
        logs=root / "logs",
    )
    for directory in (
        paths.data,
        paths.daily_backups,
        paths.pre_migration_backups,
        paths.pre_restore_backups,
        paths.recovery,
        paths.staging,
        paths.cache,
        paths.logs,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return paths


def test_empty_data_root_starts_at_desktop_revision_and_requires_first_run(data_root: Path) -> None:
    state = implemented(lambda: BootstrapService(_paths(data_root)).start())

    assert state.data_root == data_root
    assert state.schema_revision == DESKTOP_HEAD_REVISION
    assert state.first_run is True
    assert state.setup_complete is False
    assert state.daily_backup == "not_due"


@pytest.mark.parametrize(
    ("database_state", "expected_code"),
    [
        ("corrupt", "startup.database_corrupt"),
        ("future", "startup.future_schema"),
        ("read_only", "startup.database_read_only"),
    ],
)
def test_invalid_database_states_refuse_writable_main_window(
    data_root: Path,
    database_state: str,
    expected_code: str,
) -> None:
    paths = _paths(data_root)
    if database_state == "corrupt":
        paths.database.write_bytes(b"not-a-sqlite-database")
    else:
        with sqlite3.connect(paths.database) as connection:
            connection.execute("CREATE TABLE alembic_version (version_num TEXT NOT NULL)")
            connection.execute(
                "INSERT INTO alembic_version(version_num) VALUES (?)",
                ("9999_future" if database_state == "future" else "0001_desktop_initial",),
            )
        if database_state == "read_only":
            paths.database.chmod(0o444)

    try:
        with pytest.raises(StartupError) as captured:
            implemented(lambda: BootstrapService(paths).start())
    finally:
        paths.database.chmod(0o600)

    assert captured.value.error_code == expected_code


def test_unwritable_empty_data_root_is_reported_before_migration(data_root: Path) -> None:
    paths = _paths(data_root)
    paths.data.chmod(0o555)
    try:
        with pytest.raises(StartupError) as captured:
            implemented(lambda: BootstrapService(paths).start())
    finally:
        paths.data.chmod(0o700)

    assert captured.value.error_code == "startup.path_unavailable"


def test_existing_database_is_checked_before_and_after_upgrade(
    data_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _paths(data_root)
    implemented(lambda: BootstrapService(paths).start())
    service = BootstrapService(paths)
    events: list[str] = []
    real_verify = service._verify_database

    def verify() -> None:
        events.append("verify")
        real_verify()

    def upgrade(_database: Path, *, pre_migration_directory: Path) -> str:
        events.append("upgrade")
        assert pre_migration_directory == paths.pre_migration_backups
        return DESKTOP_HEAD_REVISION

    monkeypatch.setattr(service, "_verify_database", verify)
    monkeypatch.setattr("kindergarten_manager.application.bootstrap.upgrade_database", upgrade)

    implemented(service.start)

    assert events == ["verify", "upgrade", "verify"]


def test_failed_pre_migration_protection_refuses_writable_startup(
    data_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _paths(data_root)
    implemented(lambda: BootstrapService(paths).start())

    def fail_protection(_database: Path, *, pre_migration_directory: Path) -> str:
        del pre_migration_directory
        raise MigrationProtectionError(
            "migration.protective_backup_failed",
            "迁移前保护副本创建失败",
        )

    monkeypatch.setattr(
        "kindergarten_manager.application.bootstrap.upgrade_database",
        fail_protection,
    )

    with pytest.raises(StartupError) as captured:
        BootstrapService(paths).start()

    assert captured.value.error_code == "startup.backup_failed"
