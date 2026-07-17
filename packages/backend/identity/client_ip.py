"""登录限流使用的可信客户端地址接缝。"""

from collections.abc import Collection
from ipaddress import ip_address


def parse_trusted_bff_peers(configured: str | None) -> set[str]:
    """只接受显式配置的回环 BFF socket peer。"""

    trusted = {peer.strip() for peer in (configured or "").split(",") if peer.strip()}
    for peer in trusted:
        try:
            loopback = ip_address(peer).is_loopback
        except ValueError as exc:
            raise ValueError("可信 BFF peer 必须是回环地址") from exc
        if not loopback:
            raise ValueError("可信 BFF peer 必须是回环地址")
    return trusted


def resolve_client_ip(
    *,
    socket_peer: str,
    internal_client_ip: str | None,
    trusted_bff_peers: Collection[str],
) -> str:
    trusted = set(trusted_bff_peers)
    for peer in trusted:
        try:
            loopback = ip_address(peer).is_loopback
        except ValueError as exc:
            raise ValueError("可信 BFF peer 必须是回环地址") from exc
        if not loopback:
            raise ValueError("可信 BFF peer 必须是回环地址")
    if socket_peer not in trusted or internal_client_ip is None:
        return socket_peer
    try:
        return str(ip_address(internal_client_ip))
    except ValueError:
        return socket_peer
