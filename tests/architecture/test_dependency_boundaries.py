"""三个运行单元的单向依赖约束。"""

import ast
from pathlib import Path


def test_web_does_not_import_backend_or_database_layers() -> None:
    forbidden_roots = {"sqlalchemy", "packages.backend"}
    violations: list[str] = []

    for source_path in Path("apps/web").rglob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imported = [node.module or ""]
            else:
                continue
            for module_name in imported:
                if any(
                    module_name == root or module_name.startswith(f"{root}.")
                    for root in forbidden_roots
                ):
                    violations.append(f"{source_path}:{node.lineno}:{module_name}")

    assert violations == []


def test_contracts_do_not_import_backend_or_orm() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in Path("packages/contracts").glob("*.py")
    )

    assert "packages.backend" not in source
    assert "sqlalchemy" not in source.lower()
    assert "repository" not in source.lower()
