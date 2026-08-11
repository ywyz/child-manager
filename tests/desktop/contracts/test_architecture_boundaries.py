from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[3] / "src" / "kindergarten_manager"


def _package_for(path: Path) -> str:
    relative = path.relative_to(SOURCE_ROOT.parent).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    else:
        parts.pop()
    return ".".join(parts)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    package = _package_for(path)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                relative = f"{'.' * node.level}{node.module or ''}"
                imports.add(importlib.util.resolve_name(relative, package))
            elif node.module:
                imports.add(node.module)
    return imports


def _matches(name: str, prefix: str) -> bool:
    return name == prefix or name.startswith(f"{prefix}.")


def _violations(paths: list[Path], forbidden: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    for path in paths:
        for name in _imports(path):
            if any(_matches(name, prefix) for prefix in forbidden):
                found.append(f"{path.relative_to(SOURCE_ROOT.parent.parent)} -> {name}")
    return sorted(found)


def test_desktop_namespace_does_not_import_legacy_runtime() -> None:
    paths = sorted(SOURCE_ROOT.rglob("*.py"))
    assert len(paths) >= 8, "架构测试必须扫描真实桌面命名空间"
    assert (
        _violations(
            paths,
            (
                "apps",
                "packages",
                "fastapi",
                "nicegui",
                "dramatiq",
                "redis",
                "psycopg",
            ),
        )
        == []
    )


def test_ui_only_reaches_application_boundary() -> None:
    paths = sorted((SOURCE_ROOT / "ui").rglob("*.py"))
    assert (
        _violations(
            paths,
            (
                "kindergarten_manager.domain",
                "kindergarten_manager.infrastructure",
                "sqlalchemy",
                "alembic",
                "docx",
                "httpx",
                "boto3",
                "keyring",
            ),
        )
        == []
    )


def test_application_and_domain_dependencies_point_inward() -> None:
    application_paths = sorted((SOURCE_ROOT / "application").rglob("*.py"))
    domain_paths = sorted((SOURCE_ROOT / "domain").rglob("*.py"))
    assert _violations(application_paths, ("kindergarten_manager.ui",)) == []
    assert (
        _violations(
            domain_paths,
            (
                "kindergarten_manager.application",
                "kindergarten_manager.infrastructure",
                "kindergarten_manager.ui",
                "PySide6",
                "sqlalchemy",
                "alembic",
                "docx",
                "httpx",
                "boto3",
                "keyring",
            ),
        )
        == []
    )


def test_composition_root_only_wires_adapters_and_application_services() -> None:
    assert _violations([SOURCE_ROOT / "app.py"], ("sqlite3", "docx")) == []

    application_paths = sorted((SOURCE_ROOT / "application").rglob("*.py"))
    assert _violations(application_paths, ("docx", "sqlalchemy")) == []
