"""OpenAPI 3.1 文档与基础机器契约。"""

from pathlib import Path
from typing import Any

import yaml
from openapi_spec_validator import validate

OPENAPI_PATH = Path("specs/001-daily-activity-plan/contracts/openapi.yaml")


def load_document() -> dict[str, Any]:
    loaded = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_openapi_document_is_valid_31() -> None:
    document = load_document()

    assert document["openapi"] == "3.1.0"
    validate(document)


def test_openapi_locks_repeated_auth_and_clear_cookies() -> None:
    document = load_document()
    components = document["components"]
    assert isinstance(components, dict)
    headers = components["headers"]
    assert isinstance(headers, dict)

    for name in ("AuthSetCookies", "ClearAuthCookies"):
        header = headers[name]
        assert isinstance(header, dict)
        schema = header["schema"]
        assert schema["type"] == "array"
        assert schema["minItems"] == 2
        assert schema["maxItems"] == 2


def test_openapi_locks_two_unavailable_codes() -> None:
    document = load_document()
    components = document["components"]
    schemas = components["schemas"]
    codes = schemas["UnavailableError"]["properties"]["code"]["enum"]

    assert codes == ["database.unavailable", "configuration.unavailable"]
