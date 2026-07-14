"""Repository 禁止提交与应用事务边界。"""

import ast
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from packages.backend.database.session import transactional_session


def test_backend_repository_modules_do_not_call_commit() -> None:
    violations: list[str] = []
    for path in Path("packages/backend").rglob("*repository.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "commit"
            ):
                violations.append(f"{path}:{node.lineno}")

    assert violations == []


@pytest.mark.asyncio
async def test_application_transaction_rolls_back_writes_on_error(
    isolated_database_url: str,
) -> None:
    engine = create_async_engine(isolated_database_url)

    try:
        with pytest.raises(RuntimeError, match="rollback"):
            async with transactional_session(lambda: AsyncSession(engine)) as session:
                await session.execute(text("CREATE TABLE rollback_probe (id integer NOT NULL)"))
                await session.execute(text("INSERT INTO rollback_probe (id) VALUES (1)"))
                raise RuntimeError("rollback")
        async with engine.connect() as connection:
            table_name = await connection.scalar(text("SELECT to_regclass('rollback_probe')"))
    finally:
        await engine.dispose()

    assert table_name is None
