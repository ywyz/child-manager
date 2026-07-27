import socket
from importlib import import_module
from typing import Any

import httpx
import pytest


def _modules() -> tuple[Any, Any]:
    try:
        client = import_module("packages.backend.integrations.ai.client")
        errors = import_module("packages.backend.integrations.ai.errors")
    except ModuleNotFoundError:
        pytest.fail("T078 尚未提供供应商中立 AI 客户端", pytrace=False)
    return client, errors


def _resolver(_host: str, port: int, **_kwargs: object) -> list[tuple[object, ...]]:
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]


def test_client_posts_openai_compatible_request_with_fixed_limits() -> None:
    client_module, _errors = _modules()
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": '{"topic":"春天","questions":["看到了什么？"]}'}}
                ]
            },
        )

    client = client_module.ProviderNeutralAiClient(
        transport=httpx.MockTransport(handler),
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )
    result = client.generate_structured(
        base_url="https://ai.example.test/v1",
        api_key="super-secret-api-key",
        model_name="test-model",
        prompt="请生成晨间谈话",
    )

    assert result == {"topic": "春天", "questions": ["看到了什么？"]}
    assert len(captured) == 1
    assert captured[0].url.path == "/v1/chat/completions"
    assert captured[0].headers["authorization"] == "Bearer super-secret-api-key"
    assert client.timeout.connect <= 5
    assert client.timeout.read <= 60


def test_client_rejects_redirects_without_following_them() -> None:
    client_module, errors = _modules()
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(302, headers={"Location": "https://127.0.0.1/private"})

    client = client_module.ProviderNeutralAiClient(
        transport=httpx.MockTransport(handler),
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )

    with pytest.raises(errors.AiClientError) as captured:
        client.generate_structured(
            base_url="https://ai.example.test/v1",
            api_key="never-log-me",
            model_name="test-model",
            prompt="test",
        )
    assert calls == 1
    assert captured.value.code == "ai.redirect_rejected"


def test_client_errors_are_stable_and_never_include_key_or_prompt() -> None:
    client_module, errors = _modules()

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="provider echoed never-log-me and private prompt")

    client = client_module.ProviderNeutralAiClient(
        transport=httpx.MockTransport(handler),
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )
    with pytest.raises(errors.AiClientError) as captured:
        client.generate_structured(
            base_url="https://ai.example.test/v1",
            api_key="never-log-me",
            model_name="test-model",
            prompt="private prompt",
        )

    assert captured.value.code == "ai.authentication_failed"
    assert "never-log-me" not in str(captured.value)
    assert "private prompt" not in str(captured.value)


def test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin() -> None:
    client_module, _errors = _modules()
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"topic":"春天","questions":[]}'}}]},
        )

    client = client_module.ProviderNeutralAiClient(
        transport=httpx.MockTransport(handler),
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )
    client.generate_structured(
        base_url="https://ai.example.test/v1",
        api_key="secret",
        model_name="test-model",
        prompt="test",
    )

    assert captured[0].url.host == "93.184.216.34"
    assert captured[0].headers["host"] == "ai.example.test"
    assert captured[0].extensions["sni_hostname"] == "ai.example.test"
