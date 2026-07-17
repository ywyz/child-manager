import pytest

from packages.backend.identity.client_ip import parse_trusted_bff_peers, resolve_client_ip


def test_configured_loopback_bff_peer_can_supply_internal_client_ip() -> None:
    assert (
        resolve_client_ip(
            socket_peer="127.0.0.1",
            internal_client_ip="203.0.113.9",
            trusted_bff_peers={"127.0.0.1"},
        )
        == "203.0.113.9"
    )


def test_untrusted_peer_cannot_supply_internal_client_ip() -> None:
    assert (
        resolve_client_ip(
            socket_peer="198.51.100.4",
            internal_client_ip="203.0.113.9",
            trusted_bff_peers={"127.0.0.1"},
        )
        == "198.51.100.4"
    )


def test_non_loopback_peer_cannot_be_configured_as_trusted_bff() -> None:
    try:
        resolve_client_ip(
            socket_peer="198.51.100.4",
            internal_client_ip="203.0.113.9",
            trusted_bff_peers={"198.51.100.4"},
        )
    except ValueError as exc:
        assert "回环" in str(exc)
    else:
        raise AssertionError("非回环 peer 不得成为可信 BFF")


def test_trusted_bff_peers_are_empty_until_explicitly_configured() -> None:
    assert parse_trusted_bff_peers(None) == set()
    assert parse_trusted_bff_peers("") == set()
    assert parse_trusted_bff_peers("127.0.0.1,::1") == {"127.0.0.1", "::1"}
    with pytest.raises(ValueError, match="回环"):
        parse_trusted_bff_peers("198.51.100.7")
