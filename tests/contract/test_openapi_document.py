"""OpenAPI 契约锁定测试。

读取静态 openapi.yaml 并锁定关键结构，防止后续实现漂移。
增加运行时 OpenAPI 与静态契约的一致性门禁。
"""

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from apps.api.main import HealthDependencies, create_app

SPEC_PATH = (
    Path(__file__).resolve().parents[2] / "specs/001-daily-activity-plan/contracts/openapi.yaml"
)


def _load_spec() -> dict[str, Any]:
    with SPEC_PATH.open() as f:
        return yaml.safe_load(f)


def test_static_openapi_spec_is_valid() -> None:
    """静态 OpenAPI spec 应该是合法的 3.1。"""
    from openapi_spec_validator import validate_spec

    spec = _load_spec()
    validate_spec(spec)
    assert spec["openapi"].startswith("3.1")


def test_unavailable_error_has_two_503_codes() -> None:
    """UnavailableError 的 code 必须恰好是两个稳定 503 code。"""
    spec = _load_spec()
    schemas = spec["components"]["schemas"]
    unavail = schemas["UnavailableError"]
    code_prop = unavail["properties"]["code"]
    assert code_prop["enum"] == [
        "database.unavailable",
        "configuration.unavailable",
    ]


def test_error_schema_has_required_envelope() -> None:
    """Error schema 必须包含 code/message/request_id/field_errors。"""
    spec = _load_spec()
    error = spec["components"]["schemas"]["Error"]
    assert set(error["required"]) == {
        "code",
        "message",
        "request_id",
        "field_errors",
    }
    assert error["properties"]["request_id"]["format"] == "uuid"
    assert error["properties"]["field_errors"]["type"] == "array"
    assert error["additionalProperties"] is False


def test_error_field_schema_has_code() -> None:
    """ErrorField 必须包含 field/code/message。"""
    spec = _load_spec()
    ef = spec["components"]["schemas"]["ErrorField"]
    assert set(ef["required"]) == {"field", "code", "message"}


def test_health_schema_matches_spec() -> None:
    """Health schema 的 checks 值必须是 ok/degraded/unavailable/not_required。"""
    spec = _load_spec()
    health = spec["components"]["schemas"]["Health"]
    status_enum = health["properties"]["status"]["enum"]
    assert "ok" in status_enum
    assert "degraded" in status_enum
    assert "unavailable" in status_enum

    check_enum = health["properties"]["checks"]["additionalProperties"]["enum"]
    assert set(check_enum) == {
        "ok",
        "degraded",
        "unavailable",
        "not_required",
    }


def test_login_has_repeated_auth_cookies() -> None:
    """登录必须返回两条独立 Set-Cookie（repeated header）。"""
    spec = _load_spec()
    login_resp = spec["paths"]["/api/v1/auth/login"]["post"]["responses"]["200"]
    set_cookie = login_resp["headers"]["Set-Cookie"]
    assert set_cookie["$ref"] == "#/components/headers/AuthSetCookies"

    header = spec["components"]["headers"]["AuthSetCookies"]
    schema = header["schema"]
    assert schema["type"] == "array"
    assert schema["minItems"] == 2
    assert schema["maxItems"] == 2


def test_logout_has_repeated_clear_cookies() -> None:
    """退出必须清除两条独立 Set-Cookie。"""
    spec = _load_spec()
    logout_resp = spec["paths"]["/api/v1/auth/logout"]["post"]["responses"]["204"]
    set_cookie = logout_resp["headers"]["Set-Cookie"]
    assert set_cookie["$ref"] == "#/components/headers/ClearAuthCookies"

    header = spec["components"]["headers"]["ClearAuthCookies"]
    schema = header["schema"]
    assert schema["minItems"] == 2
    assert schema["maxItems"] == 2


def test_pagination_parameters_locked() -> None:
    """page >= 1, page_size 1–100。"""
    spec = _load_spec()
    params = spec["components"]["parameters"]
    page = params["Page"]
    assert page["schema"]["minimum"] == 1
    assert page["schema"]["default"] == 1

    page_size = params["PageSize"]
    assert page_size["schema"]["minimum"] == 1
    assert page_size["schema"]["maximum"] == 100
    assert page_size["schema"]["default"] == 20


def _runtime_schemas() -> dict[str, Any]:
    """获取运行时 OpenAPI 的 components/schemas。"""

    async def _ok() -> bool:
        return True

    deps = HealthDependencies(
        database=_ok,
        redis=_ok,
        ai=_ok,
        calendar=_ok,
        template=_ok,
        export_storage=_ok,
        security_ready=True,
    )
    app = create_app(dependencies=deps)
    client = TestClient(app)
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    return resp.json()["components"]["schemas"]


def test_runtime_error_schema_has_required_envelope() -> None:
    """运行时 Error schema 必须包含 code/message/request_id/field_errors。"""
    schemas = _runtime_schemas()
    error = schemas["Error"]
    assert set(error["required"]) == {
        "code",
        "message",
        "request_id",
        "field_errors",
    }


def test_runtime_error_request_id_is_uuid_format() -> None:
    """运行时 Error 的 request_id 必须是 uuid 格式。"""
    schemas = _runtime_schemas()
    error = schemas["Error"]
    props = error["properties"]
    request_id_schema = props["request_id"]
    assert request_id_schema.get("format") == "uuid"


def test_runtime_error_no_additional_properties() -> None:
    """运行时 Error schema 必须禁止额外字段。"""
    schemas = _runtime_schemas()
    error = schemas["Error"]
    assert error.get("additionalProperties") is False


def test_runtime_health_schema_present() -> None:
    """运行时必须包含 Health schema。"""
    schemas = _runtime_schemas()
    assert "Health" in schemas
    health = schemas["Health"]
    assert health.get("additionalProperties") is False
    props = health["properties"]
    assert "status" in props
    assert "checks" in props


def test_runtime_openapi_is_valid() -> None:
    """运行时 OpenAPI 必须通过规范校验，无悬空引用。"""
    from openapi_spec_validator import validate_spec

    async def _ok() -> bool:
        return True

    deps = HealthDependencies(
        database=_ok,
        redis=_ok,
        ai=_ok,
        calendar=_ok,
        template=_ok,
        export_storage=_ok,
        security_ready=True,
    )
    app = create_app(dependencies=deps)
    client = TestClient(app)
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    validate_spec(resp.json())


def test_runtime_health_schema_status_is_enum() -> None:
    """运行时 Health status 必须是枚举，不是任意字符串。"""
    schemas = _runtime_schemas()
    health = schemas["Health"]
    props = health["properties"]
    status_prop = props["status"]
    assert "enum" in status_prop
    assert set(status_prop["enum"]) == {"ok", "degraded", "unavailable"}


def test_runtime_health_schema_checks_value_is_enum() -> None:
    """运行时 Health checks 值必须是枚举。"""
    schemas = _runtime_schemas()
    health = schemas["Health"]
    checks_prop = health["properties"]["checks"]
    value_schema = checks_prop.get("additionalProperties", {})
    assert "enum" in value_schema
    assert set(value_schema["enum"]) == {
        "ok",
        "degraded",
        "unavailable",
        "not_required",
    }


def test_runtime_unavailable_error_has_two_codes() -> None:
    """运行时 UnavailableError 必须恰好是两个稳定 503 code。"""
    schemas = _runtime_schemas()
    unavail = schemas["UnavailableError"]
    code_prop = unavail["properties"]["code"]
    assert code_prop["enum"] == [
        "database.unavailable",
        "configuration.unavailable",
    ]
