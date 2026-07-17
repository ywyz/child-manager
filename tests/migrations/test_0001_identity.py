from __future__ import annotations

from collections.abc import Iterator

import psycopg
import pytest
from alembic import command
from alembic.config import Config


@pytest.fixture
def migrated_database(
    isolated_database_url: str, monkeypatch: pytest.MonkeyPatch
) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        yield connection


def test_identity_migration_creates_tables_extension_and_role_seeds(
    migrated_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    tables = {
        row[0]
        for row in migrated_database.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = current_schema()"
        ).fetchall()
    }
    assert {
        "kindergartens",
        "users",
        "roles",
        "user_roles",
        "refresh_tokens",
        "audit_events",
    } <= tables
    extensions = {row[0] for row in migrated_database.execute("SELECT extname FROM pg_extension")}
    assert "btree_gist" in extensions
    assert migrated_database.execute("SELECT code FROM roles ORDER BY code").fetchall() == [
        ("admin",),
        ("teacher",),
    ]


def test_identity_migration_is_idempotent(
    isolated_database_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute("SELECT count(*) FROM roles").fetchone() == (2,)
