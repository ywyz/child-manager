"""SQLite 同步 Session 工厂。"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool


def create_sqlite_engine(database_path: Path) -> Engine:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite+pysqlite:///{path}", poolclass=NullPool)

    @event.listens_for(engine, "connect")
    def apply_sqlite_pragmas(dbapi_connection: object, _record: object) -> None:
        _apply_sqlite_pragmas(dbapi_connection)

    return engine


def create_session_factory(database_path: Path) -> sessionmaker[Session]:
    engine = create_sqlite_engine(database_path)

    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@contextmanager
def connect_sqlite(
    database_path: Path,
    *,
    read_only: bool = False,
) -> Iterator[sqlite3.Connection]:
    path = Path(database_path)
    if read_only:
        connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
    try:
        _apply_sqlite_pragmas(connection)
        yield connection
    finally:
        connection.close()


def _apply_sqlite_pragmas(dbapi_connection: object) -> None:
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    try:
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA busy_timeout = 5000")
        cursor.execute("PRAGMA journal_mode = DELETE")
        cursor.execute("PRAGMA synchronous = FULL")
    finally:
        cursor.close()
