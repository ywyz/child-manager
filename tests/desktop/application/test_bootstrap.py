from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from kindergarten_manager.application.bootstrap import BootstrapService, StartupError
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

    assert state.data_root == str(data_root)
    assert state.schema_revision == "0001_desktop_initial"
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
