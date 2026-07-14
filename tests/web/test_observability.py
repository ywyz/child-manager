"""Web 结构化日志脱敏。"""

from apps.web.observability import redact_mapping


def test_web_log_redaction_removes_secrets_and_urls() -> None:
    event = redact_mapping(
        {
            "csrf_signing_key": "csrf-secret-value",
            "api_url": "https://example.test/path?token=query-secret",
            "nested": {"cookie": "session-secret"},
        }
    )

    rendered = repr(event)
    for secret in ("csrf-secret-value", "query-secret", "session-secret"):
        assert secret not in rendered
