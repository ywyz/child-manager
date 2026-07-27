"""OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。"""

from __future__ import annotations

import json
import socket
from ipaddress import ip_address
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx

from packages.backend.integrations.ai.errors import AiClientError
from packages.backend.integrations.ai.limits import AI_TIMEOUT, MAX_RESPONSE_BYTES
from packages.backend.integrations.ai.url_policy import (
    AiUrlPolicyError,
    Resolver,
    revalidate_ai_base_url,
    validate_ai_base_url,
)


def _pinned_url(base_url: str, address: str) -> str:
    parsed = urlsplit(base_url)
    normalized = ip_address(address).compressed
    host = f"[{normalized}]" if ":" in normalized else normalized
    netloc = f"{host}:{parsed.port}" if parsed.port is not None else host
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, ""))


class ProviderNeutralAiClient:
    def __init__(
        self,
        *,
        transport: httpx.BaseTransport | None = None,
        resolver: Resolver | None = None,
        allowed_hosts: set[str] | frozenset[str],
    ) -> None:
        self._transport = transport
        self._resolver: Resolver = resolver or socket.getaddrinfo
        self._allowed_hosts = frozenset(allowed_hosts)
        self.timeout = AI_TIMEOUT

    def generate_structured(
        self,
        *,
        base_url: str,
        api_key: str,
        model_name: str,
        prompt: str,
    ) -> dict[str, Any]:
        try:
            validated = validate_ai_base_url(
                base_url,
                resolver=self._resolver,
                allowed_hosts=self._allowed_hosts,
            )
        except AiUrlPolicyError as exc:
            raise AiClientError("ai.address_rejected", "模型地址安全校验失败。") from exc
        pinned_base_url = _pinned_url(base_url, sorted(validated.addresses)[0])
        url = f"{pinned_base_url.rstrip('/')}/chat/completions"
        host_header = (
            validated.host if validated.port == 443 else f"{validated.host}:{validated.port}"
        )
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        try:
            with (
                httpx.Client(
                    transport=self._transport,
                    timeout=self.timeout,
                    follow_redirects=False,
                    trust_env=False,
                ) as client,
                client.stream(
                    "POST",
                    url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Host": host_header,
                    },
                    json=payload,
                    extensions={"sni_hostname": validated.host},
                ) as response,
            ):
                try:
                    revalidate_ai_base_url(
                        validated,
                        resolver=self._resolver,
                        allowed_hosts=self._allowed_hosts,
                    )
                except AiUrlPolicyError as exc:
                    raise AiClientError(
                        "ai.address_rejected",
                        "模型地址安全校验失败。",
                    ) from exc
                if response.is_redirect:
                    raise AiClientError("ai.redirect_rejected", "模型服务重定向已拒绝。")
                if response.status_code in {401, 403}:
                    raise AiClientError(
                        "ai.authentication_failed",
                        "模型服务认证失败。",
                    )
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "")
                    retry_after_seconds = (
                        min(60, int(retry_after)) if retry_after.isdigit() else None
                    )
                    raise AiClientError(
                        "ai.rate_limited",
                        "模型服务请求过于频繁。",
                        retry_after_seconds=retry_after_seconds,
                    )
                if response.status_code >= 500:
                    raise AiClientError("ai.provider_error", "模型服务返回错误。")
                if response.status_code == 402:
                    raise AiClientError(
                        "ai.balance_unavailable",
                        "模型服务余额不可用。",
                    )
                if response.status_code == 404:
                    raise AiClientError("ai.model_not_found", "模型不存在。")
                if response.status_code >= 400:
                    raise AiClientError(
                        "ai.request_rejected",
                        "模型请求配置无效。",
                    )
                body = bytearray()
                for chunk in response.iter_bytes():
                    if len(body) + len(chunk) > MAX_RESPONSE_BYTES:
                        raise AiClientError(
                            "ai.response_too_large",
                            "模型响应超过安全限制。",
                        )
                    body.extend(chunk)
        except AiClientError:
            raise
        except httpx.TimeoutException as exc:
            raise AiClientError("ai.timeout", "模型服务响应超时。") from exc
        except httpx.HTTPError as exc:
            raise AiClientError("ai.unavailable", "模型服务暂不可用。") from exc
        try:
            content = json.loads(body)["choices"][0]["message"]["content"]
            result = json.loads(content)
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AiClientError("ai.invalid_response", "模型响应结构无效。") from exc
        if not isinstance(result, dict):
            raise AiClientError("ai.invalid_response", "模型响应结构无效。")
        return result
