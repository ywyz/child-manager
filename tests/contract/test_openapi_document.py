"""OpenAPI 契约锁定测试。

读取静态 openapi.yaml 并锁定关键结构，防止后续实现漂移。
增加运行时 OpenAPI 与静态契约的一致性门禁。
"""

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from apps.api.app import create_app
from apps.api.dependencies import HealthDependencies

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


def _runtime_paths() -> dict[str, Any]:
    """获取运行时 OpenAPI 的 paths。"""

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
    return resp.json()["paths"]


def test_runtime_health_live_path_responses_match_static() -> None:
    """运行时 /health/live 的 path responses 必须与静态契约等价。"""
    static_paths = _load_spec()["paths"]
    runtime_paths = _runtime_paths()

    static_live = static_paths["/health/live"]["get"]["responses"]
    runtime_live = runtime_paths["/health/live"]["get"]["responses"]

    assert "200" in runtime_live
    live_200 = runtime_live["200"]
    rt_ref = live_200["content"]["application/json"]["schema"]["$ref"]
    # 静态契约通过 HealthOk 引用 Health；运行时 FastAPI 使用 Pydantic 模型名
    assert static_live["200"]["$ref"] == "#/components/responses/HealthOk"
    assert rt_ref in {
        "#/components/schemas/Health",
        "#/components/schemas/HealthResponse",
    }


def test_runtime_health_ready_path_responses_match_static() -> None:
    """运行时 /health/ready 的 path responses 必须与静态契约等价。"""
    static_paths = _load_spec()["paths"]
    runtime_paths = _runtime_paths()

    static_ready = static_paths["/health/ready"]["get"]["responses"]
    runtime_ready = runtime_paths["/health/ready"]["get"]["responses"]

    # 200 响应必须存在且 schema 指向 Health（或 Pydantic 模型名）
    assert "200" in runtime_ready
    ready_200 = runtime_ready["200"]
    rt_ref = ready_200["content"]["application/json"]["schema"]["$ref"]
    assert rt_ref in {
        "#/components/schemas/Health",
        "#/components/schemas/HealthResponse",
    }

    # 503 响应必须存在且描述与静态契约一致
    assert "503" in runtime_ready
    assert runtime_ready["503"]["description"] == "服务不可用"

    # 静态契约确认 503 引用 Unavailable 响应（含 UnavailableError schema）
    assert static_ready["503"]["$ref"] == "#/components/responses/Unavailable"


def test_runtime_health_schema_equivalent_to_static() -> None:
    """运行时 Health schema 必须与静态契约结构等价。"""
    static_spec = _load_spec()
    static_health = static_spec["components"]["schemas"]["Health"]
    runtime_health = _runtime_schemas()["Health"]

    # status 枚举必须一致
    assert set(runtime_health["properties"]["status"]["enum"]) == set(
        static_health["properties"]["status"]["enum"]
    )

    # checks additionalProperties 枚举必须一致
    runtime_checks_enum = set(
        runtime_health["properties"]["checks"]["additionalProperties"]["enum"]
    )
    static_checks_enum = set(static_health["properties"]["checks"]["additionalProperties"]["enum"])
    assert runtime_checks_enum == static_checks_enum

    # 两者都不允许额外字段
    assert runtime_health.get("additionalProperties") is False
    assert static_health.get("additionalProperties") is False


# Codex 第十九轮审阅 P1：Auth/Users operation 的运行时响应状态集合必须与
# 冻结静态 OpenAPI 契约对等，不得只验证静态 YAML。
_AUTH_USERS_OPERATIONS = [
    ("/api/v1/auth/csrf", "get"),
    ("/api/v1/auth/login", "post"),
    ("/api/v1/auth/refresh", "post"),
    ("/api/v1/auth/logout", "post"),
    ("/api/v1/auth/me", "get"),
    ("/api/v1/auth/change-password", "post"),
    ("/api/v1/users", "get"),
    ("/api/v1/users", "post"),
    ("/api/v1/users/{user_id}", "get"),
    ("/api/v1/users/{user_id}", "patch"),
    ("/api/v1/users/{user_id}/roles", "put"),
    ("/api/v1/users/{user_id}/activate", "post"),
    ("/api/v1/users/{user_id}/deactivate", "post"),
    ("/api/v1/users/{user_id}/reset-password", "post"),
]

# FastAPI 会为带 Path/Query 参数校验的路由自动添加 422 响应，即使静态契约未声明。
# 这些 operation 允许运行时多出 422，只校验运行时包含静态契约的全部状态码。


def _fastapi_auto_adds_422(op: dict[str, Any]) -> bool:
    """判断 FastAPI 是否会为该 operation 自动添加 422 验证响应。"""
    return any(param.get("in") in ("path", "query") for param in op.get("parameters", []))


def test_auth_users_runtime_response_status_codes_match_static() -> None:
    """RED 回归：全部 Auth/Users operation 的运行时响应状态码集合必须与冻结静态契约对等。

    Codex 第十九轮审阅 P1：独立比较显示 13/13 个 Auth/Users operation 的响应状态
    集合不同；例如静态 reset-password 为 204/403/404/409/422，运行时为 200/422。
    """
    static_paths = _load_spec()["paths"]
    runtime_paths = _runtime_paths()

    mismatches: list[str] = []
    for path, method in _AUTH_USERS_OPERATIONS:
        static_op = static_paths.get(path, {}).get(method)
        runtime_op = runtime_paths.get(path, {}).get(method)
        if static_op is None:
            mismatches.append(f"{method.upper()} {path}: 静态契约缺失")
            continue
        if runtime_op is None:
            mismatches.append(f"{method.upper()} {path}: 运行时缺失")
            continue
        static_statuses = set(static_op.get("responses", {}).keys())
        runtime_statuses = set(runtime_op.get("responses", {}).keys())
        # FastAPI 会为带 Path/Query 参数的路由自动添加 422；静态契约未声明时
        # 允许运行时多出 422（且仅允许 422 这一项差异），其余状态码必须严格对等。
        if (
            "422" not in static_statuses
            and "422" in runtime_statuses
            and _fastapi_auto_adds_422(runtime_op)
        ):
            runtime_statuses = runtime_statuses - {"422"}
        if static_statuses != runtime_statuses:
            missing = static_statuses - runtime_statuses
            extra = runtime_statuses - static_statuses
            mismatches.append(
                f"{method.upper()} {path}: 静态={sorted(static_statuses)} "
                f"运行时={sorted(runtime_statuses)} "
                f"缺失={sorted(missing)} 多余={sorted(extra)}"
            )
    assert not mismatches, "Auth/Users 响应状态码集合与静态契约不一致:\n" + "\n".join(mismatches)


def test_reset_password_runtime_declares_204() -> None:
    """RED 回归：reset-password 运行时必须声明 204 状态码。

    Codex 第十九轮审阅 P1：旧版 reset-password 装饰器未声明 status_code=204，
    导致运行时默认 200，与冻结契约 204 不符。
    """
    runtime_paths = _runtime_paths()
    reset_op = runtime_paths["/api/v1/users/{user_id}/reset-password"]["post"]
    assert "204" in reset_op["responses"], (
        f"reset-password 运行时必须声明 204，实际: {sorted(reset_op['responses'].keys())}"
    )
    # 成功状态码必须是 204，不是 200。
    assert "200" not in reset_op["responses"], (
        "reset-password 运行时不应该有 200 状态码（应为 204）"
    )
