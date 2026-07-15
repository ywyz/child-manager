import ipaddress
import socket
from collections.abc import Iterator
from typing import Any
from urllib.parse import quote
from uuid import uuid4

import pytest

from tests.database_config import require_test_database_url

BASE_DATABASE_URL = require_test_database_url()
IS_POSTGRESQL = BASE_DATABASE_URL.startswith("postgresql")


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
            with psycopg.connect(_native_psycopg_url(BASE_DATABASE_URL), autocommit=True) as connection:
                connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
    else:
        yield BASE_DATABASE_URL
