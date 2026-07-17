"""可信 BFF 客户端地址解析测试。"""

from dataclasses import dataclass

import pytest

from packages.backend.identity.client_ip import get_client_ip


@dataclass(frozen=True)
class FakeClient:
    host: str


@dataclass
class FakeRequest:
    client: FakeClient | None
    headers: dict[bytes, bytes]

    def get(self, name: bytes) -> bytes | None:
        return self.headers.get(name.lower())


@pytest.fixture
def trusted() -> set[str]:
    return {"127.0.0.1", "::1"}


def test_uses_internal_header_when_bff_peer_is_loopback(trusted: set[str]) -> None:
    request = FakeRequest(
        client=FakeClient("127.0.0.1"),
        headers={b"x-child-manager-client-ip": b"192.168.1.10"},
    )
    assert get_client_ip(request, trusted) == "192.168.1.10"


def test_ignores_internal_header_when_bff_peer_not_trusted(trusted: set[str]) -> None:
    request = FakeRequest(
        client=FakeClient("203.0.113.1"),
        headers={b"x-child-manager-client-ip": b"192.168.1.10"},
    )
    assert get_client_ip(request, trusted) == "203.0.113.1"


def test_ignores_forwarded_and_xff(trusted: set[str]) -> None:
    request = FakeRequest(
        client=FakeClient("127.0.0.1"),
        headers={
            b"forwarded": b"for=203.0.113.10",
            b"x-forwarded-for": b"203.0.113.11",
            b"x-child-manager-client-ip": b"10.0.0.5",
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
        headers={b"x-child-manager-client-ip": b"10.0.0.5"},
    )
    assert get_client_ip(request, trusted) == "10.0.0.5"
