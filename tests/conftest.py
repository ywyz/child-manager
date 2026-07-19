import ipaddress
import os
import socket
from collections.abc import Iterator
from typing import Any
from urllib.parse import quote
from uuid import uuid4

# P1-2：在任何应用模块（apps.api.routers.auth 等）被子目录 conftest 导入前，
# 必须先固定测试环境变量，否则 settings 会按 production 构造，导致 _throttle 等
# 模块级初始化读取到错误环境。pytest_configure hook 在所有 conftest 加载后才执行，
# 无法覆盖子目录 conftest 导入应用模块的时序，因此在模块顶部设置。
_TEST_DATABASE_URL = os.environ.get("CHILD_MANAGER_TEST_DATABASE_URL", "")
os.environ.setdefault("CHILD_MANAGER_ENVIRONMENT", "test")
if _TEST_DATABASE_URL:
    os.environ.setdefault("CHILD_MANAGER_DATABASE_URL", _TEST_DATABASE_URL)
os.environ.setdefault("CHILD_MANAGER_JWT_SIGNING_KEY", "test-jwt-signing-key-32bytes-long-0000")
os.environ.setdefault("CHILD_MANAGER_CSRF_SIGNING_KEY", "test-csrf-signing-key-32bytes-long-000")

import pytest  # noqa: E402

from tests.database_config import require_test_database_url  # noqa: E402

pytest_plugins = ["nicegui.testing.user_plugin"]

BASE_DATABASE_URL = require_test_database_url()
IS_POSTGRESQL = BASE_DATABASE_URL.startswith("postgresql")


def pytest_configure(config: pytest.Config) -> None:
    """在测试模块导入前固定环境变量，确保 Settings 读取到测试值。"""
    # 模块级已设置主要环境变量；此处保留 setdefault 以兼容显式覆盖。
    os.environ.setdefault("CHILD_MANAGER_ENVIRONMENT", "test")
    os.environ.setdefault("CHILD_MANAGER_DATABASE_URL", BASE_DATABASE_URL)
    os.environ.setdefault("CHILD_MANAGER_JWT_SIGNING_KEY", "test-jwt-signing-key-32bytes-long-0000")
    os.environ.setdefault(
        "CHILD_MANAGER_CSRF_SIGNING_KEY", "test-csrf-signing-key-32bytes-long-000"
    )


def _native_psycopg_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


@pytest.fixture(autouse=True)
def block_external_network(monkeypatch: pytest.MonkeyPatch) -> None:
    original_connect = socket.socket.connect

    def guarded_connect(sock: socket.socket, address: Any) -> None:
        if isinstance(address, tuple) and address:
            host = str(address[0])
            try:
                allowed = ipaddress.ip_address(host).is_loopback
            except ValueError:
                allowed = host == "localhost"
            if not allowed:
                raise RuntimeError(f"测试禁止外部网络连接: {host}")
        original_connect(sock, address)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)


@pytest.fixture
def isolated_database_url() -> Iterator[str]:
    if IS_POSTGRESQL:
        import psycopg
        from psycopg import sql

        schema = f"test_{uuid4().hex}"
        with psycopg.connect(_native_psycopg_url(BASE_DATABASE_URL), autocommit=True) as connection:
            connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        options = quote(f"-csearch_path={schema}")
        try:
            yield f"{BASE_DATABASE_URL}?options={options}"
        finally:
            with psycopg.connect(
                _native_psycopg_url(BASE_DATABASE_URL), autocommit=True
            ) as connection:
                connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
    else:
        yield BASE_DATABASE_URL


@pytest.fixture
def migrated_database_url(isolated_database_url: str) -> Iterator[str]:
    """在隔离 schema 上运行 Alembic 升级，并临时替换 SQLAlchemy 引擎。"""
    from alembic.command import upgrade
    from alembic.config import Config
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from packages.backend.database import session as session_module

    original_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    original_engine = session_module.engine
    original_session_local = session_module.SessionLocal

    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    session_module.engine = create_engine(isolated_database_url, pool_pre_ping=True, echo=False)
    session_module.SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=session_module.engine
    )

    config = Config("alembic.ini")
    upgrade(config, "head")

    try:
        yield isolated_database_url
    finally:
        session_module.engine.dispose()
        if original_url is not None:
            os.environ["CHILD_MANAGER_DATABASE_URL"] = original_url
        else:
            os.environ.pop("CHILD_MANAGER_DATABASE_URL", None)
        session_module.engine = original_engine
        session_module.SessionLocal = original_session_local


@pytest.fixture(autouse=True)
def _reset_login_throttle_storage() -> Iterator[None]:
    """每个测试前清空内存限流状态，避免跨测试误拦截。"""
    from apps.api.routers import auth as auth_router

    backend = getattr(auth_router._throttle, "_backend", None)
    if backend is not None and hasattr(backend, "storage"):
        backend.storage.clear()
    yield
