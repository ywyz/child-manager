"""可信 BFF 客户端地址解析。"""

from typing import Any

_INTERNAL_IP_HEADER = "x-child-manager-client-ip"


def _is_trusted_peer(host: str | None, trusted_peers: set[str]) -> bool:
    """判断 socket peer 是否为显式配置的可信 BFF peer。

    采用规范化后的**精确成员匹配**：不因“同为 loopback”就互相信任。
    Codex 第十九轮审阅 P0：旧版只要 trusted_peers 含任一回环地址，就信任
    所有回环地址（含 127.0.0.2/127.1.1.1），导致配置 127.0.0.1 时
    socket peer=127.0.0.2 伪造内部头会被错误采用，可分散来源限流。

    规范化规则与配置一致：NFKC+trim+lower。``localhost`` 不再隐式等价于
    ``127.0.0.1``；若需信任 ``localhost``，必须在 trusted_peers 中显式配置。
    """
    if host is None:
        return False
    normalized = host.strip().lower()
    if not normalized:
        return False
    return normalized in {peer.strip().lower() for peer in trusted_peers}


def get_client_ip(request: Any, trusted_peers: set[str]) -> str:
    """解析请求的真实客户端地址。

    仅当直接 socket peer 来自受信任回环地址时，才接受内部转发头；
    否则忽略 Forwarded、X-Forwarded-For 等伪造头，返回 peer 地址。
    """
    peer_host = request.client.host if request.client is not None else None

    if _is_trusted_peer(peer_host, trusted_peers):
        # Starlette ``Headers`` 以字符串 key 读取；bytes key 会触发
        # ``AttributeError: 'bytes' object has no attribute 'encode'``。
        internal = request.headers.get(_INTERNAL_IP_HEADER)
        if internal:
            return str(internal)

    return peer_host if peer_host is not None else "127.0.0.1"
