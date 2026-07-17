"""可信 BFF 客户端地址解析。"""

from ipaddress import ip_address
from typing import Any

_INTERNAL_IP_HEADER = b"x-child-manager-client-ip"


def _is_trusted_peer(host: str | None, trusted_peers: set[str]) -> bool:
    if host is None:
        return False
    if host in trusted_peers:
        return True
    if host == "localhost":
        return "127.0.0.1" in trusted_peers or "::1" in trusted_peers
    try:
        return ip_address(host).is_loopback and any(
            ip_address(peer).is_loopback for peer in trusted_peers
        )
    except ValueError:
        return False


def get_client_ip(request: Any, trusted_peers: set[str]) -> str:
    """解析请求的真实客户端地址。

    仅当直接 socket peer 来自受信任回环地址时，才接受内部转发头；
    否则忽略 Forwarded、X-Forwarded-For 等伪造头，返回 peer 地址。
    """
    peer_host = request.client.host if request.client is not None else None

    if _is_trusted_peer(peer_host, trusted_peers):
        internal = request.headers.get(_INTERNAL_IP_HEADER)
        if internal:
            return internal.decode("ascii") if isinstance(internal, bytes) else str(internal)

    return peer_host if peer_host is not None else "127.0.0.1"
