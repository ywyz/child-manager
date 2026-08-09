from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from kindergarten_manager.infrastructure.database.engine import create_session_factory
from tests.desktop.helpers import implemented


def test_session_factory_applies_frozen_sqlite_pragmas(tmp_path: Path) -> None:
    factory = implemented(lambda: create_session_factory(tmp_path / "desktop.sqlite3"))

    with factory() as first, factory() as second:
        values = {
            name: first.execute(text(f"PRAGMA {name}")).scalar_one()
            for name in ("foreign_keys", "busy_timeout", "journal_mode", "synchronous")
        }

        assert first is not second
        assert values == {
            "foreign_keys": 1,
            "busy_timeout": 5_000,
            "journal_mode": "delete",
            "synchronous": 2,
        }
