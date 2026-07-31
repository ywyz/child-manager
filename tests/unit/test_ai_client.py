import socket
from collections.abc import Iterator
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
    assert client.timeout.connect == 10
    assert client.timeout.read == 120


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


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (400, "ai.request_rejected"),
        (402, "ai.balance_unavailable"),
        (404, "ai.model_not_found"),
        (503, "ai.provider_error"),
    ],
)
def test_client_separates_non_retryable_provider_rejections_from_5xx(
    status_code: int,
    expected_code: str,
) -> None:
    client_module, errors = _modules()
    client = client_module.ProviderNeutralAiClient(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(status_code, text="provider detail")
        ),
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )

    with pytest.raises(errors.AiClientError) as captured:
        client.generate_structured(
            base_url="https://ai.example.test/v1",
            api_key="secret",
            model_name="test-model",
            prompt="test",
        )

    assert captured.value.code == expected_code


def test_client_caps_retry_after_at_sixty_seconds() -> None:
    client_module, errors = _modules()
    client = client_module.ProviderNeutralAiClient(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(429, headers={"Retry-After": "120"})
        ),
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )

    with pytest.raises(errors.AiClientError) as captured:
        client.generate_structured(
            base_url="https://ai.example.test/v1",
            api_key="secret",
            model_name="test-model",
            prompt="test",
        )

    assert captured.value.code == "ai.rate_limited"
    assert captured.value.retry_after_seconds == 60


def test_client_stops_streaming_as_soon_as_response_exceeds_limit() -> None:
    client_module, errors = _modules()

    class OversizedStream(httpx.SyncByteStream):
        def __init__(self) -> None:
            self.yielded_chunks = 0
            self.closed = False

        def __iter__(self) -> Iterator[bytes]:
            self.yielded_chunks += 1
            yield b"x" * client_module.MAX_RESPONSE_BYTES
            self.yielded_chunks += 1
            yield b"y"
            self.yielded_chunks += 1
            yield b"must-not-be-read"

        def close(self) -> None:
            self.closed = True

    stream = OversizedStream()
    client = client_module.ProviderNeutralAiClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, stream=stream)),
        resolver=_resolver,
        allowed_hosts={"ai.example.test"},
    )

    with pytest.raises(errors.AiClientError) as captured:
        client.generate_structured(
            base_url="https://ai.example.test/v1",
            api_key="secret",
            model_name="test-model",
            prompt="test",
        )

    assert captured.value.code == "ai.response_too_large"
    assert stream.yielded_chunks == 2
    assert stream.closed is True
