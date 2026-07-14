"""结构化日志脱敏与追踪字段。"""

from packages.backend.observability import (
    REQUEST_ID,
    TRACE_ID,
    merge_request_context,
    redact_mapping,
    request_context,
)


def test_redaction_removes_nested_secrets_and_url_passwords() -> None:
    event = redact_mapping(
        {
            "api_key": "sk-full-secret",
            "authorization": "Bearer token-value",
            "database_url": "postgresql://user:database-password@db/app",
            "nested": {"password": "account-password", "safe": "kept"},
        }
    )
    rendered = repr(event)

    for secret in ("sk-full-secret", "token-value", "database-password", "account-password"):
        assert secret not in rendered
    assert event["nested"] == {"password": "[REDACTED]", "safe": "kept"}


def test_request_context_always_contains_request_and_trace_ids() -> None:
    assert request_context(request_id="request-1") == {
        "request_id": "request-1",
        "trace_id": "request-1",
    }
    assert request_context(request_id="request-1", trace_id="trace-2") == {
        "request_id": "request-1",
        "trace_id": "trace-2",
    }


def test_redaction_removes_url_query_secrets_and_handles_invalid_ports() -> None:
    event = redact_mapping(
        {
            "service_url": "https://example.test/path?api_key=top-secret#fragment-secret",
            "broken_url": "https://example.test:invalid/path?token=another-secret",
        }
    )

    rendered = repr(event)
    assert "top-secret" not in rendered
    assert "fragment-secret" not in rendered
    assert "another-secret" not in rendered


def test_redaction_removes_signing_keys_master_keys_and_url_lists() -> None:
    event = redact_mapping(
        {
            "jwt_signing_key": "jwt-secret-value",
            "csrf_signing_key": "csrf-secret-value",
            "master_key": "master-secret-value",
            "service_urls": ["https://example.test/path?token=query-secret"],
        }
    )

    rendered = repr(event)
    for secret in ("jwt-secret-value", "csrf-secret-value", "master-secret-value", "query-secret"):
        assert secret not in rendered


def test_structlog_processor_merges_context_variables() -> None:
    request_token = REQUEST_ID.set("request-1")
    trace_token = TRACE_ID.set("trace-2")
    try:
        event = merge_request_context(None, "info", {"event": "ready"})
    finally:
        TRACE_ID.reset(trace_token)
        REQUEST_ID.reset(request_token)

    assert event == {"event": "ready", "request_id": "request-1", "trace_id": "trace-2"}
