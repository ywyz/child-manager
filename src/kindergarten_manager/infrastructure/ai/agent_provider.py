"""OpenAI-compatible Agent Provider Adapter；只解析响应，不执行 Tool。"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from uuid import UUID, uuid4

import httpx

from kindergarten_manager.application.agent_runtime import (
    Permission,
    ProviderToolCall,
    ProviderTurnRequest,
    ProviderTurnResult,
    ToolDescriptor,
)
from kindergarten_manager.infrastructure.ai.client import _chat_completions_endpoint


class AgentProviderError(RuntimeError):
    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class OpenAICompatibleAgentProvider:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model_name: str,
        transport: httpx.BaseTransport | None = None,
        max_response_bytes: int = 1_048_576,
    ) -> None:
        if max_response_bytes <= 0:
            raise ValueError("Agent 响应上限必须大于零")
        self._endpoint = _chat_completions_endpoint(base_url)
        self._api_key = api_key
        self._model_name = model_name
        self._transport = transport
        self._max_response_bytes = max_response_bytes
        self.timeout = httpx.Timeout(connect=10, read=180, write=180, pool=10)

    def complete(self, request: ProviderTurnRequest) -> ProviderTurnResult:
        payload = {
            "model": self._model_name,
            "messages": [
                {"role": "system", "content": request.system_policy},
                *_provider_messages(request.messages),
            ],
            "tools": [_tool_schema(descriptor) for descriptor in request.tools],
            "tool_choice": "auto",
            "max_tokens": request.response_limit,
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
                    self._endpoint,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=payload,
                ) as response,
            ):
                if response.is_redirect:
                    raise AgentProviderError(
                        "agent.provider_redirect_forbidden",
                        "Agent Provider 不允许重定向",
                    )
                if response.status_code in {408, 429} or response.status_code >= 500:
                    raise AgentProviderError(
                        "agent.provider_unavailable",
                        "Agent Provider 暂时不可用",
                        retryable=True,
                    )
                if response.is_error:
                    raise AgentProviderError(
                        "agent.provider_refused",
                        "Agent Provider 拒绝了本次请求",
                    )
                body = _read_bounded(response, self._max_response_bytes)
        except AgentProviderError:
            raise
        except httpx.TransportError as error:
            raise AgentProviderError(
                "agent.provider_unavailable",
                "Agent Provider 暂时不可用",
                retryable=True,
            ) from error

        try:
            envelope = json.loads(body)
            choice = envelope["choices"][0]
            message = choice["message"]
            finish_reason = _finish_reason(choice.get("finish_reason"))
            content = message.get("content")
            if content is not None and not isinstance(content, str):
                raise TypeError
            tool_calls = tuple(
                _parse_tool_call(raw_call, request.tools)
                for raw_call in message.get("tool_calls", ())
            )
        except KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError:
            raise AgentProviderError(
                "agent.provider_invalid_response",
                "Agent Provider 响应格式无效",
            ) from None

        if len(content or "") > request.response_limit:
            raise AgentProviderError(
                "agent.response_too_large",
                "Agent Provider 响应超过允许上限",
            )
        request_id = envelope.get("id")
        return ProviderTurnResult(
            assistant_content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            provider_request_id=(str(request_id)[:128] if isinstance(request_id, str) else None),
        )


def _read_bounded(response: httpx.Response, limit: int) -> bytes:
    chunks: list[bytes] = []
    size = 0
    for chunk in response.iter_bytes():
        size += len(chunk)
        if size > limit:
            raise AgentProviderError(
                "agent.response_too_large",
                "Agent Provider 响应超过允许上限",
            )
        chunks.append(chunk)
    return b"".join(chunks)


def _parse_tool_call(
    raw_call: object,
    descriptors: tuple[ToolDescriptor, ...],
) -> ProviderToolCall:
    if not isinstance(raw_call, Mapping):
        raise TypeError
    function = raw_call.get("function")
    if not isinstance(function, Mapping):
        raise TypeError
    tool_name = function.get("name")
    raw_arguments = function.get("arguments")
    if not isinstance(tool_name, str) or not isinstance(raw_arguments, str):
        raise TypeError
    arguments = json.loads(raw_arguments)
    if not isinstance(arguments, dict):
        raise TypeError
    permission = next(
        (descriptor.permission for descriptor in descriptors if descriptor.name == tool_name),
        Permission.READ,
    )
    raw_id = raw_call.get("id")
    call_id = _uuid_or_random(raw_id)
    return ProviderToolCall(
        call_id=call_id,
        tool_name=tool_name,
        permission=permission,
        arguments=arguments,
    )


def _uuid_or_random(value: object) -> UUID:
    if isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            pass
    return uuid4()


def _finish_reason(value: object) -> str:
    reasons = {
        "stop": "completed",
        "tool_calls": "tool_calls",
        "length": "length",
        "content_filter": "refused",
    }
    return reasons.get(value, "completed") if isinstance(value, str) else "completed"


def _tool_schema(descriptor: ToolDescriptor) -> dict[str, object]:
    return {
        "type": "function",
        "function": {
            "name": descriptor.name,
            "parameters": _plain_json(descriptor.input_schema),
        },
    }


def _plain_json(value: object) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain_json(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_plain_json(item) for item in value]
    if isinstance(value, Permission):
        return value.value
    return value


def _provider_messages(
    messages: tuple[Mapping[str, object], ...],
) -> list[dict[str, object]]:
    serialized: list[dict[str, object]] = []
    for message in messages:
        role = message.get("role")
        raw_tool_calls = message.get("tool_calls")
        if role == "assistant" and isinstance(raw_tool_calls, tuple):
            tool_calls = []
            for call in raw_tool_calls:
                if not isinstance(call, Mapping):
                    raise AgentProviderError("agent.provider_invalid_request", "Agent 消息格式无效")
                tool_calls.append(
                    {
                        "id": str(call.get("call_id", "")),
                        "type": "function",
                        "function": {
                            "name": str(call.get("tool_name", "")),
                            "arguments": json.dumps(
                                _plain_json(call.get("arguments", {})),
                                ensure_ascii=False,
                                separators=(",", ":"),
                            ),
                        },
                    }
                )
            serialized.append(
                {
                    "role": "assistant",
                    "content": message.get("content"),
                    "tool_calls": tool_calls,
                }
            )
            continue
        raw_results = message.get("results")
        if role == "tool" and isinstance(raw_results, tuple):
            for result in raw_results:
                if not isinstance(result, Mapping):
                    raise AgentProviderError("agent.provider_invalid_request", "Agent 消息格式无效")
                serialized.append(
                    {
                        "role": "tool",
                        "tool_call_id": str(result.get("call_id", "")),
                        "name": str(result.get("tool_name", "")),
                        "content": json.dumps(
                            {
                                "status": result.get("status"),
                                "value": _plain_json(result.get("value")),
                            },
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                    }
                )
            continue
        serialized.append({str(key): _plain_json(value) for key, value in message.items()})
    return serialized
