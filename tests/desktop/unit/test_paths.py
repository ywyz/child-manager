from __future__ import annotations

from pathlib import Path

from kindergarten_manager.infrastructure.paths import APPLICATION_ID, resolve_desktop_paths
from tests.desktop.helpers import implemented


def test_paths_use_stable_generic_data_location_and_never_install_directory(tmp_path: Path) -> None:
    generic_data = tmp_path / "GenericDataLocation"
    install_directory = tmp_path / "Program Files" / "KindergartenManager"
    install_directory.mkdir(parents=True)

    paths = implemented(
        lambda: resolve_desktop_paths(
            generic_data_location=generic_data,
            install_directory=install_directory,
        )
    )

    assert paths.root == generic_data / APPLICATION_ID
    assert paths.data == paths.root / "data"
    assert paths.database == paths.data / "child-manager.sqlite3"
    assert paths.backups == paths.root / "backups"
    assert paths.daily_backups == paths.backups / "daily"
    assert paths.pre_migration_backups == paths.backups / "pre-migration"
    assert paths.pre_restore_backups == paths.backups / "pre-restore"
    assert paths.recovery == paths.root / "recovery"
    assert paths.staging == paths.root / "staging"
    assert paths.cache == paths.root / "cache"
    assert paths.logs == paths.root / "logs"
    assert all(
        path.is_dir()
        for path in (
            paths.root,
            paths.data,
            paths.backups,
            paths.daily_backups,
            paths.pre_migration_backups,
            paths.pre_restore_backups,
            paths.recovery,
            paths.staging,
            paths.cache,
            paths.logs,
        )
    )
    assert not paths.database.is_relative_to(install_directory)
