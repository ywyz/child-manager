"""M2 运行时 OpenAPI 与冻结契约的一致性门禁。"""

import json
from pathlib import Path
from typing import Any

import yaml
from openapi_spec_validator import validate

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


def _canonical_schema(
    document: dict[str, Any],
    value: dict[str, Any],
    *,
    resolving: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    reference = value.get("$ref")
    if reference is not None:
        if reference in resolving:
            return {"$ref": reference}
        return _canonical_schema(
            document,
            _resolve(document, value),
            resolving=resolving | {str(reference)},
        )
    normalized: dict[str, Any] = {}
    for key, item in value.items():
        if key in {"default", "description", "title"}:
            continue
        if isinstance(item, dict):
            normalized[key] = _canonical_schema(document, item, resolving=resolving)
        elif isinstance(item, list):
            normalized[key] = [
                (
                    _canonical_schema(document, child, resolving=resolving)
                    if isinstance(child, dict)
                    else child
                )
                for child in item
            ]
        elif isinstance(item, float) and item.is_integer():
            normalized[key] = int(item)
        else:
            normalized[key] = item
    all_of = normalized.get("allOf")
    if isinstance(all_of, list) and len(all_of) == 1 and isinstance(all_of[0], dict):
        normalized = {
            **all_of[0],
            **{key: value for key, value in normalized.items() if key != "allOf"},
        }
    elif isinstance(all_of, list) and all(isinstance(item, dict) for item in all_of):
        flattened = {key: value for key, value in normalized.items() if key != "allOf"}
        properties: dict[str, Any] = {}
        required: list[str] = []
        for item in all_of:
            properties.update(item.get("properties", {}))
            required.extend(item.get("required", []))
            for key, value in item.items():
                if key not in {"properties", "required"}:
                    flattened[key] = value
        if properties:
            flattened["properties"] = properties
        if required:
            flattened["required"] = sorted(set(required))
        normalized = flattened
    nullable_union = normalized.get("anyOf", normalized.get("oneOf"))
    if (
        isinstance(nullable_union, list)
        and len(nullable_union) == 2
        and {"type": "null"} in nullable_union
    ):
        non_null = next(item for item in nullable_union if item != {"type": "null"})
        if isinstance(non_null, dict) and isinstance(non_null.get("type"), str):
            normalized = {**non_null, "type": [non_null["type"], "null"]}
            if isinstance(normalized.get("enum"), list):
                normalized["enum"] = [*normalized["enum"], None]
    for sortable in ("required", "enum"):
        items = normalized.get(sortable)
        if isinstance(items, list):
            normalized[sortable] = sorted(items, key=str)
    return normalized


def _schema_json(document: dict[str, Any], value: dict[str, Any] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(
        _canonical_schema(document, value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _parameter_shape(
    document: dict[str, Any],
    key: tuple[str, str],
    operation: dict[str, Any],
) -> set[tuple[str, str, bool, str | None]]:
    path_parameters = document["paths"][key[0]].get("parameters", [])
    return {
        (
            str(parameter["in"]).lower(),
            str(parameter["name"]).lower(),
            bool(parameter.get("required", False)),
            _schema_json(document, parameter.get("schema")),
        )
        for raw_parameter in [*path_parameters, *operation.get("parameters", [])]
        for parameter in [_resolve(document, raw_parameter)]
    }


def _response_shape(
    document: dict[str, Any], operation: dict[str, Any]
) -> dict[str, tuple[tuple[tuple[str, str | None], ...], str | None]]:
    result: dict[str, tuple[tuple[tuple[str, str | None], ...], str | None]] = {}
    for status, raw_response in operation["responses"].items():
        response = _resolve(document, raw_response)
        schema = response.get("content", {}).get("application/json", {}).get("schema")
        headers = tuple(
            sorted(
                (
                    name.lower(),
                    _schema_json(document, _resolve(document, raw_header).get("schema")),
                )
                for name, raw_header in response.get("headers", {}).items()
            )
        )
        result[str(status)] = (
            headers,
            _schema_json(document, schema if isinstance(schema, dict) else None),
        )
    return result


def _request_schema(document: dict[str, Any], operation: dict[str, Any]) -> str | None:
    schema = (
        operation.get("requestBody", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema")
    )
    return _schema_json(document, schema if isinstance(schema, dict) else None)


def test_runtime_m2_openapi_matches_frozen_operation_contract() -> None:
    runtime = create_app().openapi()
    validate(runtime)
    frozen_operations = _operations(FROZEN)
    runtime_operations = _operations(runtime)

    assert runtime_operations.keys() == frozen_operations.keys()
    for key, frozen_operation in frozen_operations.items():
        runtime_operation = runtime_operations[key]
        assert set(runtime_operation["responses"]) == set(frozen_operation["responses"]), key
        assert _response_shape(runtime, runtime_operation) == _response_shape(
            FROZEN, frozen_operation
        ), key
        assert _request_schema(runtime, runtime_operation) == _request_schema(
            FROZEN, frozen_operation
        ), key
        assert _parameter_shape(runtime, key, runtime_operation) == _parameter_shape(
            FROZEN, key, frozen_operation
        ), key
        assert _effective_security(runtime, runtime_operation) == _effective_security(
            FROZEN, frozen_operation
        ), key
