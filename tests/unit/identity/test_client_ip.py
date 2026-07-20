"""可信 BFF 客户端地址解析测试。"""

from dataclasses import dataclass

import pytest
from starlette.requests import Request

from packages.backend.identity.client_ip import get_client_ip


@dataclass(frozen=True)
class FakeClient:
    host: str


@dataclass
class FakeRequest:
    """使用字符串 key 的 headers，与 Starlette ``Headers`` 行为一致。

    Codex 第十八轮审阅发现：旧版用 ``dict[bytes, bytes]`` 假对象掩盖了
    ``client_ip.py`` 对 Starlette ``Headers`` 再以 bytes key 调用 ``get``
    的 ``AttributeError``。真实 ``Headers`` 只接受字符串 key。
    """

    client: FakeClient | None
    headers: dict[str, str]

    def get(self, name: str) -> str | None:
        return self.headers.get(name.lower())


@pytest.fixture
def trusted() -> set[str]:
    return {"127.0.0.1", "::1"}


def test_uses_internal_header_when_bff_peer_is_loopback(trusted: set[str]) -> None:
    request = FakeRequest(
        client=FakeClient("127.0.0.1"),
        headers={"x-child-manager-client-ip": "192.168.1.10"},
    )
    assert get_client_ip(request, trusted) == "192.168.1.10"


def test_ignores_internal_header_when_bff_peer_not_trusted(trusted: set[str]) -> None:
    request = FakeRequest(
        client=FakeClient("203.0.113.1"),
        headers={"x-child-manager-client-ip": "192.168.1.10"},
    )
    assert get_client_ip(request, trusted) == "203.0.113.1"


def test_ignores_forwarded_and_xff(trusted: set[str]) -> None:
    request = FakeRequest(
        client=FakeClient("127.0.0.1"),
        headers={
            "forwarded": "for=203.0.113.10",
            "x-forwarded-for": "203.0.113.11",
            "x-child-manager-client-ip": "10.0.0.5",
        },
    )
    assert get_client_ip(request, trusted) == "10.0.0.5"


def test_falls_back_to_peer_when_no_internal_header(trusted: set[str]) -> None:
    request = FakeRequest(
        client=FakeClient("127.0.0.1"),
        headers={},
    )
    assert get_client_ip(request, trusted) == "127.0.0.1"


def test_localhost_string_is_trusted(trusted: set[str]) -> None:
    request = FakeRequest(
        client=FakeClient("localhost"),
        headers={"x-child-manager-client-ip": "10.0.0.5"},
    )
    assert get_client_ip(request, trusted) == "10.0.0.5"


def test_real_starlette_request_trusted_peer_without_internal_header_falls_back_to_peer(
    trusted: set[str],
) -> None:
    """RED 回归：真实 Starlette ``Request`` 在可信回环 peer 且缺内部头时
    必须回退到 socket peer，不得抛 ``AttributeError``。

    Codex 第十八轮审阅 P0-2：旧版 ``client_ip.py`` 在内部头缺失时对
    Starlette ``Headers`` 再以 bytes key 调用 ``get``，真实 ``Request``
    探针复现 ``AttributeError: 'bytes' object has no attribute 'encode'``。
    """
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],  # 不含 x-child-manager-client-ip
        "client": ("127.0.0.1", 50000),
        "server": ("127.0.0.1", 8000),
        "query_string": b"",
    }
    request = Request(scope)
    assert get_client_ip(request, trusted) == "127.0.0.1"


def test_real_starlette_request_trusted_peer_with_internal_header_uses_header(
    trusted: set[str],
) -> None:
    """真实 Starlette ``Request`` 在可信 peer 且有内部头时使用内部头值。"""
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"x-child-manager-client-ip", b"192.168.1.10")],
        "client": ("127.0.0.1", 50000),
        "server": ("127.0.0.1", 8000),
        "query_string": b"",
    }
    request = Request(scope)
    assert get_client_ip(request, trusted) == "192.168.1.10"
