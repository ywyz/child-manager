from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Thread

import pytest
from sqlalchemy import text

from kindergarten_manager.infrastructure.database.engine import (
    connect_sqlite,
    create_session_factory,
)
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


def test_sessions_never_reuse_dbapi_connections_across_threads(tmp_path: Path) -> None:
    factory = implemented(lambda: create_session_factory(tmp_path / "desktop.sqlite3"))
    connections: list[sqlite3.Connection] = []

    def acquire_connection() -> None:
        with factory() as session:
            raw = session.connection().connection.driver_connection
            assert isinstance(raw, sqlite3.Connection)
            connections.append(raw)

    first = Thread(target=acquire_connection)
    second = Thread(target=acquire_connection)
    first.start()
    first.join()
    second.start()
    second.join()

    assert len(connections) == 2
    assert connections[0] is not connections[1]


def test_raw_sqlite_connection_applies_same_frozen_pragmas(tmp_path: Path) -> None:
    with connect_sqlite(tmp_path / "desktop.sqlite3") as connection:
        values = {
            name: connection.execute(f"PRAGMA {name}").fetchone()[0]
            for name in ("foreign_keys", "busy_timeout", "journal_mode", "synchronous")
        }

    assert values == {
        "foreign_keys": 1,
        "busy_timeout": 5_000,
        "journal_mode": "delete",
        "synchronous": 2,
    }
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")
