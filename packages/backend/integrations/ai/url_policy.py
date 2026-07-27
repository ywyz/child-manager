"""AI 模型地址的保存时与连接前 SSRF 防护。"""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

Resolver = Callable[..., Sequence[tuple[Any, ...]]]


class AiUrlPolicyError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ValidatedAiBaseUrl:
    value: str
    scheme: str
    host: str
    port: int
    addresses: frozenset[str]


def _addresses(host: str, port: int, resolver: Resolver) -> frozenset[str]:
    try:
        records = resolver(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise AiUrlPolicyError("模型地址无法解析。") from exc
    values = frozenset(str(record[4][0]) for record in records)
    if not values:
        raise AiUrlPolicyError("模型地址没有可用的网络地址。")
    return values


def _require_public(addresses: Iterable[str]) -> None:
    for value in addresses:
        address = ipaddress.ip_address(value)
        if (
            not address.is_global
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
        ):
            raise AiUrlPolicyError("模型地址必须解析到公网地址。")


def validate_ai_base_url(
    value: str,
    *,
    resolver: Resolver = socket.getaddrinfo,
    allowed_hosts: set[str] | frozenset[str],
) -> ValidatedAiBaseUrl:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname:
        raise AiUrlPolicyError("模型地址必须使用公网 HTTPS。")
    if parsed.username or parsed.password or parsed.fragment:
        raise AiUrlPolicyError("模型地址不能包含用户信息或片段。")
    host = parsed.hostname.rstrip(".").lower()
    normalized_allowlist = {item.rstrip(".").lower() for item in allowed_hosts}
    if host not in normalized_allowlist:
        raise AiUrlPolicyError("模型地址不在服务端允许列表中。")
    port = parsed.port or 443
    addresses = _addresses(host, port, resolver)
    _require_public(addresses)
    return ValidatedAiBaseUrl(value, parsed.scheme, host, port, addresses)


def revalidate_ai_base_url(
    previous: ValidatedAiBaseUrl,
    *,
    resolver: Resolver = socket.getaddrinfo,
    allowed_hosts: set[str] | frozenset[str],
) -> ValidatedAiBaseUrl:
    current = validate_ai_base_url(
        previous.value,
        resolver=resolver,
        allowed_hosts=allowed_hosts,
    )
    if current.addresses != previous.addresses:
        raise AiUrlPolicyError("模型地址解析结果发生变化，已拒绝连接。")
    return current
