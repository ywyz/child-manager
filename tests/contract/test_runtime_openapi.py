"""M2 运行时 OpenAPI 与冻结契约的一致性门禁。"""

from pathlib import Path
from typing import Any

import yaml

from apps.api.app import create_app

FROZEN = yaml.safe_load(
    Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
)
M2_PREFIXES = ("/health/", "/api/v1/auth", "/api/v1/users")
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def _resolve(document: dict[str, Any], value: dict[str, Any]) -> dict[str, Any]:
    reference = value.get("$ref")
    if reference is None:
        return value
    current: Any = document
    for part in str(reference).removeprefix("#/").split("/"):
        current = current[part]
    assert isinstance(current, dict)
    return current


def _operations(document: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (path, method): operation
        for path, path_item in document["paths"].items()
        if path.startswith(M2_PREFIXES)
        for method, operation in path_item.items()
        if method in HTTP_METHODS
    }


def _effective_security(
    document: dict[str, Any], operation: dict[str, Any]
) -> list[dict[str, list[str]]]:
    return operation.get("security", document.get("security", []))


def _parameter_shape(
    document: dict[str, Any], operation: dict[str, Any]
) -> set[tuple[str, str, bool]]:
    return {
        (
            str(parameter["in"]).lower(),
            str(parameter["name"]).lower(),
            bool(parameter.get("required", False)),
        )
        for raw_parameter in operation.get("parameters", [])
        for parameter in [_resolve(document, raw_parameter)]
    }


def _response_shape(
    document: dict[str, Any], operation: dict[str, Any]
) -> dict[str, tuple[frozenset[str], str | None]]:
    result: dict[str, tuple[frozenset[str], str | None]] = {}
    for status, raw_response in operation["responses"].items():
        response = _resolve(document, raw_response)
        schema = response.get("content", {}).get("application/json", {}).get("schema")
        reference = schema.get("$ref") if isinstance(schema, dict) else None
        result[str(status)] = (frozenset(response.get("headers", {})), reference)
    return result


def _request_schema(operation: dict[str, Any]) -> str | None:
    schema = (
        operation.get("requestBody", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema")
    )
    return schema.get("$ref") if isinstance(schema, dict) else None


def test_runtime_m2_openapi_matches_frozen_operation_contract() -> None:
    runtime = create_app().openapi()
    frozen_operations = _operations(FROZEN)
    runtime_operations = _operations(runtime)

    assert runtime_operations.keys() == frozen_operations.keys()
    for key, frozen_operation in frozen_operations.items():
        runtime_operation = runtime_operations[key]
        assert set(runtime_operation["responses"]) == set(frozen_operation["responses"]), key
        assert _response_shape(runtime, runtime_operation) == _response_shape(
            FROZEN, frozen_operation
        ), key
        assert _request_schema(runtime_operation) == _request_schema(frozen_operation), key
        assert _parameter_shape(runtime, runtime_operation) == _parameter_shape(
            FROZEN, frozen_operation
        ), key
        assert _effective_security(runtime, runtime_operation) == _effective_security(
            FROZEN, frozen_operation
        ), key
