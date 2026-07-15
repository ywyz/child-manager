from packages.security.redaction import redact_dict


def test_redact_sensitive_keys():
    data = {
        "password": "secret123",
        "api_key": "sk-abc123",
        "token": "jwt-token-value",
        "username": "testuser",
        "email": "test@example.com",
    }
    result = redact_dict(data)
    assert result["password"] == "******"
    assert result["api_key"] == "******"
    assert result["token"] == "******"
    assert result["username"] == "testuser"
    assert result["email"] == "test@example.com"


def test_redact_nested_dict():
    data = {
        "user": {
            "name": "Alice",
            "credentials": {
                "password": "secret",
                "api_key": "key-123",
            },
        },
        "config": {
            "enabled": True,
            "secret_value": "hidden",
        },
    }
    result = redact_dict(data)
    assert result["user"]["name"] == "Alice"
    assert result["user"]["credentials"]["password"] == "******"
    assert result["user"]["credentials"]["api_key"] == "******"
    assert result["config"]["enabled"] is True
    assert result["config"]["secret_value"] == "******"


def test_redact_list():
    data = {
        "items": [
            {"id": 1, "password": "pass1"},
            {"id": 2, "password": "pass2"},
        ],
        "tokens": ["token1", "token2"],
    }
    result = redact_dict(data)
    assert result["items"][0]["id"] == 1
    assert result["items"][0]["password"] == "******"
    assert result["items"][1]["id"] == 2
    assert result["items"][1]["password"] == "******"
    assert result["tokens"][0] == "******"
    assert result["tokens"][1] == "******"


def test_redact_preserves_non_sensitive():
    data = {
        "name": "Test",
        "value": 123,
        "active": True,
        "metadata": {"tags": ["a", "b"]},
    }
    result = redact_dict(data)
    assert result == data
