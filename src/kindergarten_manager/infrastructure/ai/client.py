from __future__ import annotations

import ipaddress
import json
import time
from collections.abc import Callable
from typing import Any, TypeVar
from urllib.parse import urlsplit

import httpx

_Validated = TypeVar("_Validated")


class AiClientError(RuntimeError):
    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class ProviderNeutralAiClient:
    def __init__(
        self,
        *,
        transport: httpx.BaseTransport | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        max_response_bytes: int = 1_048_576,
    ) -> None:
        if max_response_bytes <= 0:
            raise ValueError("AI 响应上限必须大于零")
        self.timeout = httpx.Timeout(connect=10, read=300, write=300, pool=10)
        self._transport = transport
        self._sleeper = sleeper
        self._max_response_bytes = max_response_bytes

    def generate_structured(
        self,
        *,
        base_url: str,
        api_key: str,
        model_name: str,
        prompt: str,
        validator: Callable[[dict[str, Any]], _Validated] | None = None,
    ) -> dict[str, Any] | _Validated:
        endpoint = _chat_completions_endpoint(base_url)
        last_error: AiClientError | None = None
        with httpx.Client(
            transport=self._transport,
            timeout=self.timeout,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            for attempt in range(3):
                try:
                    result = self._request(
                        client,
                        endpoint=endpoint,
                        api_key=api_key,
                        model_name=model_name,
                        prompt=prompt,
                    )
                    return validator(result) if validator is not None else result
                except AiClientError as error:
                    if not error.retryable or attempt == 2:
                        raise
                    last_error = error
                    self._sleeper(float(2**attempt))
                except httpx.TransportError as error:
                    last_error = AiClientError(
                        "ai.transport_failed",
                        "AI 服务暂时不可用",
                        retryable=True,
                    )
                    if attempt == 2:
                        raise last_error from error
                    self._sleeper(float(2**attempt))
        assert last_error is not None
        raise last_error

    def _request(
        self,
        client: httpx.Client,
        *,
        endpoint: str,
        api_key: str,
        model_name: str,
        prompt: str,
    ) -> dict[str, Any]:
        with client.stream(
            "POST",
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            },
        ) as response:
            if response.is_redirect:
                raise AiClientError("ai.redirect_forbidden", "AI 服务不允许重定向")
            if response.status_code in {408, 429} or response.status_code >= 500:
                raise AiClientError(
                    "ai.provider_unavailable",
                    "AI 服务暂时不可用",
                    retryable=True,
                )
            if response.is_error:
                raise AiClientError("ai.provider_rejected", "AI 服务拒绝了本次请求")

            chunks: list[bytes] = []
            size = 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > self._max_response_bytes:
                    raise AiClientError("ai.response_too_large", "AI 响应超过允许上限")
                chunks.append(chunk)

        try:
            envelope = json.loads(b"".join(chunks))
            content = envelope["choices"][0]["message"]["content"]
            parsed = json.loads(content) if isinstance(content, str) else content
        except KeyError, IndexError, TypeError, json.JSONDecodeError:
            raise AiClientError(
                "ai.response_invalid",
                "AI 响应格式无效",
                retryable=True,
            ) from None
        if not isinstance(parsed, dict):
            raise AiClientError(
                "ai.response_invalid",
                "AI 响应格式无效",
                retryable=True,
            )
        return parsed


def _chat_completions_endpoint(base_url: str) -> str:
    parsed = urlsplit(base_url)
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("AI 服务地址不得包含用户信息")
    if not parsed.hostname or parsed.query or parsed.fragment:
        raise ValueError("AI 服务地址无效")

    loopback = parsed.hostname.casefold() == "localhost"
    if not loopback:
        try:
            loopback = ipaddress.ip_address(parsed.hostname).is_loopback
        except ValueError:
            loopback = False

    if parsed.scheme == "http" and not loopback:
        raise ValueError("非回环 AI 服务必须使用 HTTPS")
    if parsed.scheme not in ({"http", "https"} if loopback else {"https"}):
        raise ValueError("AI 服务地址协议无效")

    return f"{base_url.rstrip('/')}/chat/completions"


def validate_base_url(base_url: str) -> str:
    _chat_completions_endpoint(base_url)
    return base_url.rstrip("/")
