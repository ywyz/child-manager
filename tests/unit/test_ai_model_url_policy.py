import socket
from importlib import import_module
from typing import Any

import pytest


def _module() -> Any:
    try:
        return import_module("packages.backend.integrations.ai.url_policy")
    except ModuleNotFoundError:
        pytest.fail("T077 尚未提供 AI 地址安全策略", pytrace=False)


def _resolver(*addresses: str) -> Any:
    def resolve(_host: str, port: int, **_kwargs: object) -> list[tuple[object, ...]]:
        return [
            (
                socket.AF_INET6 if ":" in address else socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (address, port),
            )
            for address in addresses
        ]

    return resolve


def test_policy_accepts_only_allowlisted_public_https_and_checks_every_address() -> None:
    module = _module()
    validated = module.validate_ai_base_url(
        "https://ai.example.test/v1",
        resolver=_resolver("93.184.216.34", "2606:2800:220:1:248:1893:25c8:1946"),
        allowed_hosts={"ai.example.test"},
    )

    assert validated.scheme == "https"
    assert validated.host == "ai.example.test"
    assert validated.port == 443

    with pytest.raises(module.AiUrlPolicyError):
        module.validate_ai_base_url(
            "https://ai.example.test/v1",
            resolver=_resolver("93.184.216.34", "127.0.0.1"),
            allowed_hosts={"ai.example.test"},
        )


@pytest.mark.parametrize(
    "url,address",
    [
        ("http://ai.example.test/v1", "93.184.216.34"),
        ("https://localhost/v1", "127.0.0.1"),
        ("https://metadata.example.test/v1", "169.254.169.254"),
        ("https://private.example.test/v1", "10.0.0.1"),
        ("https://multicast.example.test/v1", "224.0.0.1"),
        ("https://ipv6-local.example.test/v1", "fe80::1"),
    ],
)
def test_policy_rejects_non_https_and_non_public_networks(url: str, address: str) -> None:
    module = _module()
    host = url.split("://", 1)[1].split("/", 1)[0]
    with pytest.raises(module.AiUrlPolicyError):
        module.validate_ai_base_url(url, resolver=_resolver(address), allowed_hosts={host})


def test_policy_requires_explicit_server_allowlist() -> None:
    module = _module()
    with pytest.raises(module.AiUrlPolicyError):
        module.validate_ai_base_url(
            "https://not-allowed.example.test/v1",
            resolver=_resolver("93.184.216.34"),
            allowed_hosts={"ai.example.test"},
        )


def test_policy_detects_dns_rebinding_before_connect() -> None:
    module = _module()
    first = module.validate_ai_base_url(
        "https://ai.example.test/v1",
        resolver=_resolver("93.184.216.34"),
        allowed_hosts={"ai.example.test"},
    )
    with pytest.raises(module.AiUrlPolicyError):
        module.revalidate_ai_base_url(
            first,
            resolver=_resolver("127.0.0.1"),
            allowed_hosts={"ai.example.test"},
        )
