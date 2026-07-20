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


def test_loopback_string_is_trusted(trusted: set[str]) -> None:
    """``127.0.0.1`` 字符串等价于其精确成员匹配。"""
    request = FakeRequest(
        client=FakeClient("127.0.0.1"),
        headers={"x-child-manager-client-ip": "10.0.0.5"},
    )
    assert get_client_ip(request, trusted) == "10.0.0.5"


@pytest.mark.parametrize(
    "peer_host",
    ["127.0.0.2", "127.1.1.1", "127.255.255.254"],
)
def test_other_loopback_addresses_not_trusted_when_only_127_0_0_1_configured(
    trusted: set[str], peer_host: str
) -> None:
    """RED 回归：只配置 127.0.0.1 时，其他回环地址不得被信任。

    Codex 第十九轮审阅 P0-1：旧版只要 trusted_peers 含任一回环地址，就信任
    所有回环地址。socket peer=127.0.0.2/127.1.1.1 伪造内部头会被错误采用，
    可分散来源限流（限流键以客户端 IP 为准）。修复后采用精确成员匹配，
    127.0.0.2/127.1.1.1 不在配置集内，必须忽略伪造内部头并回退到真实 peer。
    """
    request = FakeRequest(
        client=FakeClient(peer_host),
        headers={"x-child-manager-client-ip": "203.0.113.77"},
    )
    assert get_client_ip(request, trusted) == peer_host


def test_source_throttle_key_uses_real_peer_not_spoofed_header(trusted: set[str]) -> None:
    """来源限流键以 get_client_ip 结果为准，伪造头不得分散限流。

    Codex 第十九轮审阅 P0-1：若 127.0.0.2 被错误信任并采用伪造内部头
    203.0.113.77，来源限流键会漂移，攻击者可改头绕过 30 次/15 分钟硬频控。
    精确成员匹配后，127.0.0.2 不被信任，get_client_ip 返回真实 peer，
    限流键固定为 127.0.0.2，伪造头无法分散限流。
    """
    request = FakeRequest(
        client=FakeClient("127.0.0.2"),
        headers={"x-child-manager-client-ip": "203.0.113.77"},
    )
    # get_client_ip 必须返回真实 peer，不是伪造头。
    source_ip = get_client_ip(request, trusted)
    assert source_ip == "127.0.0.2"
    # 限流键由 source_ip 派生，伪造头无法影响。
    assert source_ip != "203.0.113.77"


def test_localhost_not_implicitly_trusted(trusted: set[str]) -> None:
    """``localhost`` 不再隐式等价于 127.0.0.1。

    Codex 第十九轮审阅 P0-1：精确成员匹配要求 trusted_peers 显式包含
    ``localhost`` 才信任。配置集为 {127.0.0.1, ::1} 时，socket peer=localhost
    必须回退到真实 peer，不读伪造内部头。
    """
    request = FakeRequest(
        client=FakeClient("localhost"),
        headers={"x-child-manager-client-ip": "203.0.113.77"},
    )
    assert get_client_ip(request, trusted) == "localhost"


def test_localhost_trusted_when_explicitly_configured() -> None:
    """显式配置 localhost 时仍可信任。"""
    request = FakeRequest(
        client=FakeClient("localhost"),
        headers={"x-child-manager-client-ip": "10.0.0.5"},
    )
    assert get_client_ip(request, {"localhost"}) == "10.0.0.5"


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
