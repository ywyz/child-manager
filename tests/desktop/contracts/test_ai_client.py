from __future__ import annotations

import json

import httpx
import pytest

from tests.desktop.helpers import pending_module, pending_symbol


def _module():
    return pending_module("kindergarten_manager.infrastructure.ai.client")


def _response(content: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json={"choices": [{"message": {"content": json.dumps(content)}}]},
    )


@pytest.mark.parametrize(
    "base_url",
    [
        "http://127.0.0.1:11434/v1",
        "http://localhost:11434/v1",
        "http://[::1]:11434/v1",
        "https://ai.example.test/v1",
    ],
)
def test_client_accepts_loopback_http_and_non_loopback_https(base_url: str) -> None:
    module = _module()
    client_type = pending_symbol(module, "ProviderNeutralAiClient")
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _response({"topic": "春天", "questions": ["看到了什么？"]})

    client = client_type(transport=httpx.MockTransport(handler), sleeper=lambda _delay: None)
    result = client.generate_structured(
        base_url=base_url,
        api_key="fixture-secret",
        model_name="fixture-model",
        prompt="fixture prompt",
    )

    assert result["topic"] == "春天"
    assert len(requests) == 1
    assert requests[0].url.path.endswith("/chat/completions")


@pytest.mark.parametrize(
    "base_url",
    [
        "http://ai.example.test/v1",
        "https://user:password@ai.example.test/v1",
    ],
)
def test_client_rejects_insecure_or_userinfo_endpoints_without_network(base_url: str) -> None:
    module = _module()
    client_type = pending_symbol(module, "ProviderNeutralAiClient")
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _response({})

    client = client_type(transport=httpx.MockTransport(handler), sleeper=lambda _delay: None)
    with pytest.raises(ValueError):
        client.generate_structured(
            base_url=base_url,
            api_key="fixture-secret",
            model_name="fixture-model",
            prompt="fixture prompt",
        )
    assert calls == 0


def test_client_rejects_redirect_without_following_location() -> None:
    module = _module()
    client_type = pending_symbol(module, "ProviderNeutralAiClient")
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(302, headers={"location": "https://other.example.test/v1"})

    client = client_type(transport=httpx.MockTransport(handler), sleeper=lambda _delay: None)
    with pytest.raises(Exception) as captured:
        client.generate_structured(
            base_url="https://ai.example.test/v1",
            api_key="fixture-secret",
            model_name="fixture-model",
            prompt="fixture prompt",
        )
    assert getattr(captured.value, "code", None) == "ai.redirect_forbidden"
    assert calls == 1


def test_client_enforces_fixed_timeout_and_response_limit() -> None:
    module = _module()
    client_type = pending_symbol(module, "ProviderNeutralAiClient")

    client = client_type(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, content=b"x" * 65)),
        sleeper=lambda _delay: None,
        max_response_bytes=64,
    )
    assert client.timeout.connect == 10
    assert client.timeout.read == 300
    with pytest.raises(Exception) as captured:
        client.generate_structured(
            base_url="https://ai.example.test/v1",
            api_key="fixture-secret",
            model_name="fixture-model",
            prompt="fixture prompt",
        )
    assert getattr(captured.value, "code", None) == "ai.response_too_large"


def test_retryable_failure_is_retried_at_most_twice() -> None:
    module = _module()
    client_type = pending_symbol(module, "ProviderNeutralAiClient")
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503)

    client = client_type(transport=httpx.MockTransport(handler), sleeper=lambda _delay: None)
    with pytest.raises(Exception) as captured:
        client.generate_structured(
            base_url="https://ai.example.test/v1",
            api_key="fixture-secret",
            model_name="fixture-model",
            prompt="fixture prompt",
        )
    assert getattr(captured.value, "retryable", None) is True
    assert calls == 3


def test_transport_and_structure_errors_share_one_three_call_budget() -> None:
    module = _module()
    client_type = pending_symbol(module, "ProviderNeutralAiClient")
    client_error = pending_symbol(module, "AiClientError")
    calls = 0
    validations = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _response({"topic": "春天", "questions": []})

    def validate(payload: dict[str, object]) -> dict[str, object]:
        nonlocal validations
        validations += 1
        if validations < 3:
            raise client_error("ai.invalid_output", "结构错误", retryable=True)
        return payload

    client = client_type(transport=httpx.MockTransport(handler), sleeper=lambda _delay: None)
    result = client.generate_structured(
        base_url="https://ai.example.test/v1",
        api_key="fixture-secret",
        model_name="fixture-model",
        prompt="fixture prompt",
        validator=validate,
    )

    assert result["topic"] == "春天"
    assert calls == validations == 3
