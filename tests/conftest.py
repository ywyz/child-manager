"""M1 全局确定性与禁外网测试夹具。"""

import ipaddress
import socket
from collections.abc import Iterator
from urllib.parse import quote
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

from tests.database_config import require_test_database_url

BASE_DATABASE_URL = require_test_database_url()


def _native_psycopg_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


@pytest.fixture(autouse=True)
def block_external_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """只允许回环 TCP 和本机 Unix socket。"""

    original_connect = socket.socket.connect

    def guarded_connect(sock: socket.socket, address: object) -> None:
        if isinstance(address, tuple) and address:
            host = str(address[0])
            try:
                allowed = ipaddress.ip_address(host).is_loopback
            except ValueError:
                allowed = host == "localhost"
            if not allowed:
                raise RuntimeError(f"测试禁止外部网络连接: {host}")
        original_connect(sock, address)  # type: ignore[arg-type]

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)


@pytest.fixture
def isolated_database_url() -> Iterator[str]:
    """为请求该夹具的测试创建并清理独立 PostgreSQL schema。"""

    schema = f"test_{uuid4().hex}"
    with psycopg.connect(_native_psycopg_url(BASE_DATABASE_URL), autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    options = quote(f"-csearch_path={schema}")
    try:
        yield f"{BASE_DATABASE_URL}?options={options}"
    finally:
        with psycopg.connect(_native_psycopg_url(BASE_DATABASE_URL), autocommit=True) as connection:
            connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
