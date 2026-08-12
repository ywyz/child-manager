"""可复现的 Slice 2B Agent 零持久化只读探针。"""

from __future__ import annotations

import ast
import sqlite3
import tempfile
from pathlib import Path

from kindergarten_manager.application.bootstrap import BootstrapService
from kindergarten_manager.infrastructure.paths import DesktopPaths

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SOURCE_PATHS = (
    REPOSITORY_ROOT / "src/kindergarten_manager/infrastructure/database",
    REPOSITORY_ROOT / "src/kindergarten_manager/application/bootstrap.py",
)
RUNTIME_SOURCE_PATHS = (REPOSITORY_ROOT / "src/kindergarten_manager/app.py",)
TOOL_SQL_SOURCE_PATHS = (
    REPOSITORY_ROOT / "src/kindergarten_manager/app.py",
    REPOSITORY_ROOT / "src/kindergarten_manager/infrastructure/database/repositories.py",
)
FORBIDDEN_PERSISTENCE_TOKENS = (
    "agent_context",
    "agent_session",
    "conversation",
    "agent_message",
    "tool_result",
    "plan_patch",
    "agent_patch",
    "context_fact",
    "entity_revision",
    "provider_transcript",
)
BROAD_SCHEMA_TOKENS = (
    "conversation",
    "thread",
    "message",
    "vector",
    "agent_context",
    "agent_patch",
    "plan_patch",
)
PERSISTENCE_SINK_TOKENS = (
    "create table",
    "insert into",
    "update ",
    "delete from",
    "write_bytes",
    "write_text",
    "logging.",
    "logger.",
)
AGENT_TOOL_FUNCTIONS = {
    "read_current",
    "read_context",
    "read_calendar",
    "read_class_areas",
    "draft_patch",
    "load_tool_plan",
    "load_tool_context",
    "load_tool_semester",
    "load_tool_class_areas",
}
WRITE_SQL_TOKENS = ("insert into", "update ", "delete from", "create table", "drop table")


def _paths(root: Path) -> DesktopPaths:
    backups = root / "backups"
    return DesktopPaths(
        root=root,
        data=root / "data",
        database=root / "data/child-manager.sqlite3",
        backups=backups,
        daily_backups=backups / "daily",
        pre_migration_backups=backups / "pre-migration",
        pre_restore_backups=backups / "pre-restore",
        recovery=root / "recovery",
        staging=root / "staging",
        cache=root / "cache",
        logs=root / "logs",
    )


def _source_hits() -> tuple[str, ...]:
    hits: list[str] = []
    for source_path in SOURCE_PATHS:
        files = (source_path,) if source_path.is_file() else source_path.rglob("*.py")
        for file_path in sorted(files):
            content = file_path.read_text(encoding="utf-8").casefold()
            for token in FORBIDDEN_PERSISTENCE_TOKENS:
                if token in content:
                    relative = file_path.relative_to(REPOSITORY_ROOT)
                    hits.append(f"{relative}:{token}")
    for file_path in RUNTIME_SOURCE_PATHS:
        for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), 1):
            folded = line.casefold()
            if any(token in folded for token in FORBIDDEN_PERSISTENCE_TOKENS) and any(
                sink in folded for sink in PERSISTENCE_SINK_TOKENS
            ):
                relative = file_path.relative_to(REPOSITORY_ROOT)
                hits.append(f"{relative}:{line_number}:persistence_sink")
    return tuple(hits)


def _agent_tool_write_sql_hits() -> tuple[str, ...]:
    hits: list[str] = []
    for source_path in TOOL_SQL_SOURCE_PATHS:
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or node.name not in AGENT_TOOL_FUNCTIONS:
                continue
            for child in ast.walk(node):
                if not isinstance(child, ast.Constant) or not isinstance(child.value, str):
                    continue
                folded = child.value.casefold()
                for token in WRITE_SQL_TOKENS:
                    if token in folded:
                        relative = source_path.relative_to(REPOSITORY_ROOT)
                        hits.append(f"{relative}:{node.name}:{child.lineno}:{token.strip()}")
    return tuple(hits)


def _schema_inventory(database: Path) -> tuple[tuple[str, str, str], ...]:
    with sqlite3.connect(database) as connection:
        rows = connection.execute(
            "SELECT type, name, COALESCE(sql, '') FROM sqlite_master ORDER BY type, name"
        ).fetchall()
        inventory = [(str(row[0]), str(row[1]), str(row[2])) for row in rows]
        for object_type, name, _definition in rows:
            if object_type != "table" or str(name).startswith("sqlite_"):
                continue
            columns = connection.execute(f'PRAGMA table_info("{name}")').fetchall()
            inventory.extend(
                ("column", f"{name}.{column[1]}", str(column[2])) for column in columns
            )
    return tuple(inventory)


def _matching_inventory(
    inventory: tuple[tuple[str, str, str], ...],
    tokens: tuple[str, ...],
) -> tuple[str, ...]:
    hits: list[str] = []
    for object_type, name, definition in inventory:
        candidate = f"{name} {definition}".casefold()
        for token in tokens:
            if token in candidate:
                hits.append(f"{object_type}:{name}:{token}")
    return tuple(hits)


def main() -> None:
    source_hits = _source_hits()
    tool_write_sql_hits = _agent_tool_write_sql_hits()
    with tempfile.TemporaryDirectory(prefix="child-manager-agent-probe-") as temporary:
        paths = _paths(Path(temporary))
        state = BootstrapService(paths).start()
        inventory = _schema_inventory(paths.database)
        forbidden_schema_hits = _matching_inventory(
            inventory,
            FORBIDDEN_PERSISTENCE_TOKENS,
        )
        broad_schema_hits = _matching_inventory(inventory, BROAD_SCHEMA_TOKENS)
        backup_files = tuple(path for path in paths.backups.rglob("*") if path.is_file())
        log_files = tuple(path for path in paths.logs.rglob("*") if path.is_file())

        print("import_mode=explicit-src-test-harness")
        print("temporary_root=stdlib.TemporaryDirectory")
        print(
            "source_paths="
            + ",".join(str(path.relative_to(REPOSITORY_ROOT)) for path in SOURCE_PATHS)
        )
        print(
            "runtime_source_paths="
            + ",".join(str(path.relative_to(REPOSITORY_ROOT)) for path in RUNTIME_SOURCE_PATHS)
        )
        print(f"agent_persistence_source_hits={len(source_hits)}")
        print(f"source_hit_details={list(source_hits)}")
        print(f"agent_tool_write_sql_hits={list(tool_write_sql_hits)}")
        print(f"schema_revision={state.schema_revision}")
        print(f"sqlite_schema_objects={sum(item[0] != 'column' for item in inventory)}")
        print(f"forbidden_persistence_hits={list(forbidden_schema_hits)}")
        print(f"broad_forbidden_schema_hits={list(broad_schema_hits)}")
        print(f"backup_files={len(backup_files)}")
        print(f"log_files={len(log_files)}")


if __name__ == "__main__":
    main()
