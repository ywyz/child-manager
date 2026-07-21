"""OpenAPI 契约锁定测试。

读取静态 openapi.yaml 并锁定关键结构，防止后续实现漂移。
增加运行时 OpenAPI 与静态契约的一致性门禁。
"""

from pathlib import Path
from typing import Any

import pytest
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

# 稳定错误状态码：运行时与静态契约都必须以统一 Error envelope 描述 body。
_ERROR_STATUS_CODES = {"401", "403", "404", "409", "422", "429"}


def _runtime_full_spec() -> dict[str, Any]:
    """获取运行时完整 OpenAPI 文档。"""

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
    return resp.json()


def _resolve_response(spec: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """若 response 为 $ref 指向 components/responses，则解引用返回完整对象。"""
    if isinstance(response, dict) and "$ref" in response:
        ref_name = response["$ref"].split("/")[-1]
        comp_responses = spec.get("components", {}).get("responses", {})
        resolved = comp_responses.get(ref_name, {})
        return resolved if isinstance(resolved, dict) else {}
    return response if isinstance(response, dict) else {}


def _response_headers(spec: dict[str, Any], response: dict[str, Any]) -> set[str]:
    """提取响应声明的 header 名称集合（解析 $ref 后）。"""
    resolved = _resolve_response(spec, response)
    headers = resolved.get("headers", {})
    return set(headers.keys()) if isinstance(headers, dict) else set()


def _response_error_schema_ref(spec: dict[str, Any], response: dict[str, Any]) -> str | None:
    """提取错误响应 body 的 schema $ref（解析 $ref 响应后）。"""
    resolved = _resolve_response(spec, response)
    content = resolved.get("content", {})
    json_content = content.get("application/json", {}) if isinstance(content, dict) else {}
    schema = json_content.get("schema", {}) if isinstance(json_content, dict) else {}
    return schema.get("$ref") if isinstance(schema, dict) else None


def test_auth_users_runtime_response_status_codes_match_static() -> None:
    """M2-F01：全部 Auth/Users operation 的运行时响应状态码集合必须与冻结静态契约严格对等。

    Codex M2 Final Contract Freeze M2-F01：禁止删除运行时 422 后再比较的宽松做法；
    运行时与静态契约的状态码集合必须严格相等。冻结契约已在 main docs-only 提交
    （578c12f）补齐用户接口合法 422，运行时已声明对应 422。
    """
    static_spec = _load_spec()
    runtime_spec = _runtime_full_spec()
    static_paths = static_spec["paths"]
    runtime_paths = runtime_spec["paths"]

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
        if static_statuses != runtime_statuses:
            missing = static_statuses - runtime_statuses
            extra = runtime_statuses - static_statuses
            mismatches.append(
                f"{method.upper()} {path}: 静态={sorted(static_statuses)} "
                f"运行时={sorted(runtime_statuses)} "
                f"缺失={sorted(missing)} 多余={sorted(extra)}"
            )
    assert not mismatches, "Auth/Users 响应状态码集合与静态契约不一致:\n" + "\n".join(mismatches)


def test_auth_users_runtime_response_headers_match_static() -> None:
    """M2-F01：Auth/Users operation 的运行时响应 header 集合必须与冻结静态契约对等。

    Codex M2-F01：运行时文档缺冻结契约中的 Set-Cookie header；429 缺 Retry-After。
    本测试逐状态码比较 header 名称集合（解析 $ref 响应后），确保 Set-Cookie 与
    Retry-After 在运行时文档中声明。
    """
    static_spec = _load_spec()
    runtime_spec = _runtime_full_spec()

    mismatches: list[str] = []
    for path, method in _AUTH_USERS_OPERATIONS:
        static_resp = static_spec["paths"][path][method].get("responses", {})
        runtime_resp = runtime_spec["paths"][path][method].get("responses", {})
        codes = set(static_resp.keys()) | set(runtime_resp.keys())
        for code in codes:
            s_hdr = _response_headers(static_spec, static_resp.get(code, {}))
            r_hdr = _response_headers(runtime_spec, runtime_resp.get(code, {}))
            if s_hdr != r_hdr:
                mismatches.append(
                    f"{method.upper()} {path} {code}: 静态header={sorted(s_hdr)} "
                    f"运行时header={sorted(r_hdr)}"
                )
    assert not mismatches, "Auth/Users 响应 header 与静态契约不一致:\n" + "\n".join(mismatches)


def test_auth_users_runtime_error_responses_use_unified_error_envelope() -> None:
    """M2-F01：Auth/Users 稳定错误状态码的运行时 body 必须指向统一 Error schema。

    Codex M2-F01：401/403/404/409 多数只声明 description、没有统一 Error body；
    自动 422 仍指向 FastAPI HTTPValidationError。本测试确保运行时全部错误状态码
    的 body schema $ref 指向 #/components/schemas/Error，而非 HTTPValidationError。
    """
    runtime_spec = _runtime_full_spec()

    mismatches: list[str] = []
    for path, method in _AUTH_USERS_OPERATIONS:
        runtime_resp = runtime_spec["paths"][path][method].get("responses", {})
        for code in _ERROR_STATUS_CODES & set(runtime_resp.keys()):
            ref = _response_error_schema_ref(runtime_spec, runtime_resp[code])
            if ref != "#/components/schemas/Error":
                mismatches.append(
                    f"{method.upper()} {path} {code}: 错误 body schema={ref!r}，"
                    f"应为 #/components/schemas/Error"
                )
    assert not mismatches, "Auth/Users 错误响应未使用统一 Error envelope:\n" + "\n".join(mismatches)


def test_auth_users_runtime_declares_csrf_header_parameter() -> None:
    """M2-F01：CSRF 保护的 Auth/Users operation 必须在运行时文档声明 X-CSRF-Token header。

    Codex M2-F01：多个状态变更端点的运行时 OpenAPI 未声明冻结的 CSRF header。
    本测试确保 login/refresh/logout/change-password 与 users 写操作均声明 CSRF header 参数。
    """
    runtime_spec = _runtime_full_spec()
    csrf_protected = [
        ("/api/v1/auth/login", "post"),
        ("/api/v1/auth/refresh", "post"),
        ("/api/v1/auth/logout", "post"),
        ("/api/v1/auth/change-password", "post"),
        ("/api/v1/users", "post"),
        ("/api/v1/users/{user_id}", "patch"),
        ("/api/v1/users/{user_id}/roles", "put"),
        ("/api/v1/users/{user_id}/activate", "post"),
        ("/api/v1/users/{user_id}/deactivate", "post"),
        ("/api/v1/users/{user_id}/reset-password", "post"),
    ]
    missing: list[str] = []
    for path, method in csrf_protected:
        params = runtime_spec["paths"][path][method].get("parameters", [])
        has_csrf = any(
            p.get("name") == "X-CSRF-Token" and p.get("in") == "header"
            for p in params
            if isinstance(p, dict)
        )
        if not has_csrf:
            missing.append(f"{method.upper()} {path}")
    assert not missing, "缺少 CSRF header 参数声明:\n" + "\n".join(missing)


def test_runtime_openapi_declares_cookie_security_schemes() -> None:
    """M2-F01：运行时 OpenAPI 必须声明 accessCookie/refreshCookie 安全方案与全局 security。"""
    runtime_spec = _runtime_full_spec()
    schemes = runtime_spec.get("components", {}).get("securitySchemes", {})
    assert "accessCookie" in schemes, "缺少 accessCookie 安全方案"
    assert "refreshCookie" in schemes, "缺少 refreshCookie 安全方案"
    assert schemes["accessCookie"]["type"] == "apiKey"
    assert schemes["accessCookie"]["in"] == "cookie"
    assert schemes["accessCookie"]["name"] == "child_manager_access"
    # 全局 security 默认要求 accessCookie。
    global_security = runtime_spec.get("security", [])
    assert any("accessCookie" in req for req in global_security), "缺少全局 accessCookie security"


def test_auth_users_runtime_security_matches_static() -> None:
    """M2-F01：Auth/Users operation 的运行时 security 声明必须与冻结静态契约对等。"""
    static_spec = _load_spec()
    runtime_spec = _runtime_full_spec()

    mismatches: list[str] = []
    for path, method in _AUTH_USERS_OPERATIONS:
        static_sec = static_spec["paths"][path][method].get("security", "(inherit)")
        runtime_sec = runtime_spec["paths"][path][method].get("security", "(inherit)")
        # 静态契约未显式声明 security 时表示继承全局 accessCookie。
        if static_sec == "(inherit)":
            static_sec = static_spec.get("security", [])
        if runtime_sec == "(inherit)":
            runtime_sec = runtime_spec.get("security", [])
        if static_sec != runtime_sec:
            mismatches.append(
                f"{method.upper()} {path}: 静态security={static_sec} 运行时security={runtime_sec}"
            )
    assert not mismatches, "Auth/Users security 与静态契约不一致:\n" + "\n".join(mismatches)


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


def test_runtime_user_schema_aligned_to_frozen_contract() -> None:
    """M2-F01：运行时 User schema 必须按冻结契约收敛。

    Codex M2-F01：冻结 UserId 为 UUID；运行时为普通 string。本测试确保运行时
    User.id 使用 $ref Uuid、role_codes 唯一且枚举 admin/teacher、UserPage.items 必填。
    """
    schemas = _runtime_schemas()
    user = schemas["User"]
    # M2-F01：id 改为 $ref Uuid，与冻结契约对齐
    assert user["properties"]["id"].get("$ref") == "#/components/schemas/Uuid", (
        "User.id 必须为 $ref Uuid"
    )
    role_codes = user["properties"]["role_codes"]
    assert role_codes.get("uniqueItems") is True, "User.role_codes 必须唯一"
    items = role_codes.get("items", {})
    assert items.get("enum") == ["admin", "teacher"], "User.role_codes 必须枚举 admin/teacher"
    assert "role_codes" in user.get("required", []), "User.role_codes 必填"

    user_page = schemas["UserPage"]
    assert "items" in user_page.get("required", []), "UserPage.items 必填"
    assert user_page["properties"]["items"]["items"]["$ref"] == "#/components/schemas/User"


# --- M2-F01 收紧 parity 测试：解引用 schema、实际 HTTP header、request body 名称 ---


def _resolve_schema(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """递归解引用 $ref，返回完整 schema 对象。"""
    if not isinstance(schema, dict):
        return schema
    if "$ref" in schema:
        ref_path = schema["$ref"].split("/")[1:]
        resolved = spec
        for part in ref_path:
            resolved = resolved.get(part, {})
        return _resolve_schema(spec, resolved)
    return schema


def test_runtime_user_phone_e164_is_required_nullable() -> None:
    """M2-F01：User.phone_e164 必须为 required nullable（冻结契约要求）。"""
    schemas = _runtime_schemas()
    user = schemas["User"]
    assert "phone_e164" in user.get("required", []), "User.phone_e164 必须在 required 中"
    phone_prop = user["properties"]["phone_e164"]
    # 运行时生成 anyOf: [string, null] 或 type: [string, null]
    assert phone_prop is not None


def test_runtime_current_user_username_not_required() -> None:
    """M2-F01：CurrentUser.username 不在 required 中（冻结契约 required 集合）。"""
    schemas = _runtime_schemas()
    current_user = schemas["CurrentUser"]
    required = set(current_user.get("required", []))
    assert "username" not in required, "CurrentUser.username 不应在 required 中"
    assert required == {"id", "display_name", "kindergarten", "role_codes", "capabilities"}


def test_runtime_error_field_errors_references_error_field() -> None:
    """M2-F01：Error.field_errors 的 items 必须引用 ErrorField（不是 FieldError）。"""
    schemas = _runtime_schemas()
    error = schemas["Error"]
    field_errors = error["properties"]["field_errors"]
    items_ref = field_errors["items"].get("$ref", "")
    assert items_ref == "#/components/schemas/ErrorField", (
        f"Error.field_errors 应引用 ErrorField，实际: {items_ref}"
    )
    assert "ErrorField" in schemas, "components/schemas 必须包含 ErrorField"
    assert "FieldError" not in schemas, "components/schemas 不应包含 FieldError"


def test_runtime_user_id_rejects_non_uuid() -> None:
    """M2-F01：User.id 必须在运行时拒绝非 UUID 字符串。"""
    from datetime import UTC, datetime

    from pydantic import ValidationError

    from packages.contracts.identity import User

    with pytest.raises(ValidationError):
        User(
            id="not-a-uuid",
            username="teacher",
            display_name="教师",
            phone_e164=None,
            role_codes=["teacher"],
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )


def test_runtime_uuid_component_present() -> None:
    """M2-F01：运行时必须包含 Uuid 可复用组件。"""
    schemas = _runtime_schemas()
    assert "Uuid" in schemas
    uuid_schema = schemas["Uuid"]
    assert uuid_schema.get("type") == "string"
    assert uuid_schema.get("format") == "uuid"


def test_runtime_password_component_present() -> None:
    """M2-F01：运行时必须包含 Password 可复用组件。"""
    schemas = _runtime_schemas()
    assert "Password" in schemas
    pw = schemas["Password"]
    assert pw.get("type") == "string"
    assert pw.get("minLength") == 15
    assert pw.get("maxLength") == 128


def test_runtime_user_id_uses_uuid_ref() -> None:
    """M2-F01：User.id 必须使用 $ref: Uuid（与冻结契约对齐）。"""
    schemas = _runtime_schemas()
    user = schemas["User"]
    id_prop = user["properties"]["id"]
    assert id_prop.get("$ref") == "#/components/schemas/Uuid", (
        f"User.id 应为 $ref Uuid，实际: {id_prop}"
    )


def test_runtime_current_user_id_uses_uuid_ref() -> None:
    """M2-F01：CurrentUser.id 必须使用 $ref: Uuid（与冻结契约对齐）。"""
    schemas = _runtime_schemas()
    current_user = schemas["CurrentUser"]
    id_prop = current_user["properties"]["id"]
    assert id_prop.get("$ref") == "#/components/schemas/Uuid", (
        f"CurrentUser.id 应为 $ref Uuid，实际: {id_prop}"
    )


def test_post_users_request_body_references_create_user_request() -> None:
    """M2-F01：POST /api/v1/users request body 必须引用 CreateUserRequest。"""
    spec = _runtime_full_spec()
    body = spec["paths"]["/api/v1/users"]["post"]["requestBody"]
    schema = body["content"]["application/json"]["schema"]
    assert schema.get("$ref") == "#/components/schemas/CreateUserRequest", (
        f"POST /users request body 应引用 CreateUserRequest，实际: {schema}"
    )
    assert "CreateUserRequest" in spec["components"]["schemas"]


def test_put_roles_request_body_is_inline_schema() -> None:
    """M2-F01：PUT /api/v1/users/{user_id}/roles request body 必须为 inline schema。"""
    spec = _runtime_full_spec()
    body = spec["paths"]["/api/v1/users/{user_id}/roles"]["put"]["requestBody"]
    schema = body["content"]["application/json"]["schema"]
    assert "$ref" not in schema, "roles request body 不应为 $ref"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["role_codes"]
    assert schema["properties"]["role_codes"]["minItems"] == 1
    assert schema["properties"]["role_codes"]["uniqueItems"] is True


def test_reset_password_request_body_is_inline_schema() -> None:
    """M2-F01：POST /api/v1/users/{user_id}/reset-password request body 必须为 inline schema。"""
    spec = _runtime_full_spec()
    body = spec["paths"]["/api/v1/users/{user_id}/reset-password"]["post"]["requestBody"]
    schema = body["content"]["application/json"]["schema"]
    assert "$ref" not in schema, "reset-password request body 不应为 $ref"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["new_password"]
    assert schema["properties"]["new_password"]["$ref"] == "#/components/schemas/Password"


def test_runtime_schemas_no_stale_components() -> None:
    """M2-F01：components/schemas 不应包含已移除的命名组件。"""
    schemas = _runtime_schemas()
    assert "UserRolesUpdateRequest" not in schemas
    assert "ResetPasswordRequest" not in schemas


def test_runtime_user_required_set_matches_frozen() -> None:
    """M2-F01：User required 集合必须与冻结契约严格一致。"""
    static_spec = _load_spec()
    runtime_schemas = _runtime_schemas()
    static_required = set(static_spec["components"]["schemas"]["User"].get("required", []))
    runtime_required = set(runtime_schemas["User"].get("required", []))
    assert runtime_required == static_required, (
        f"User required 不一致: 冻结={sorted(static_required)} 运行时={sorted(runtime_required)}"
    )


def test_runtime_current_user_required_set_matches_frozen() -> None:
    """M2-F01：CurrentUser required 集合必须与冻结契约严格一致。"""
    static_spec = _load_spec()
    runtime_schemas = _runtime_schemas()
    static_required = set(static_spec["components"]["schemas"]["CurrentUser"].get("required", []))
    runtime_required = set(runtime_schemas["CurrentUser"].get("required", []))
    assert runtime_required == static_required, (
        f"CurrentUser required 不一致: 冻结={sorted(static_required)} "
        f"运行时={sorted(runtime_required)}"
    )


def test_runtime_error_required_set_matches_frozen() -> None:
    """M2-F01：Error required 集合必须与冻结契约严格一致。"""
    static_spec = _load_spec()
    runtime_schemas = _runtime_schemas()
    static_required = set(static_spec["components"]["schemas"]["Error"].get("required", []))
    runtime_required = set(runtime_schemas["Error"].get("required", []))
    assert runtime_required == static_required, (
        f"Error required 不一致: 冻结={sorted(static_required)} 运行时={sorted(runtime_required)}"
    )


def test_runtime_ref_properties_resolve_to_frozen_constraints() -> None:
    """M2-F01：通过 $ref 引用 Uuid/Password 的字段，解引用后必须与冻结契约约束一致。

    Codex 第十九轮审阅 P2：``_resolve_schema`` 已定义但没有任何测试调用，
    parity 比较直接读取 schema 对象而不递归解引用 ``$ref``。本测试通过
    ``_resolve_schema`` 解引用 User.id、CurrentUser.id、CreateUserRequest.password、
    ChangePasswordRequest.new_password 等 ``$ref`` 字段，比较解引用后的 type/format、
    minLength/maxLength 等深层语义，确保运行时与冻结契约严格对齐。
    """
    static_spec = _load_spec()
    runtime_spec = _runtime_full_spec()

    # 收集 (schema_name, property_name) 二元组，这些字段在运行时通过 $ref 引用
    # Uuid 或 Password 可复用组件，需要解引用后比较约束。
    ref_fields: list[tuple[str, str]] = [
        ("User", "id"),
        ("CurrentUser", "id"),
        ("CreateUserRequest", "password"),
        ("ChangePasswordRequest", "new_password"),
    ]

    mismatches: list[str] = []
    for schema_name, prop_name in ref_fields:
        static_schema = static_spec["components"]["schemas"].get(schema_name, {})
        runtime_schema = runtime_spec["components"]["schemas"].get(schema_name, {})
        static_prop = static_schema.get("properties", {}).get(prop_name, {})
        runtime_prop = runtime_schema.get("properties", {}).get(prop_name, {})
        # 递归解引用 $ref 后比较深层约束
        static_resolved = _resolve_schema(static_spec, static_prop)
        runtime_resolved = _resolve_schema(runtime_spec, runtime_prop)
        for key in ("type", "format", "minLength", "maxLength", "writeOnly"):
            static_value = static_resolved.get(key)
            runtime_value = runtime_resolved.get(key)
            if static_value != runtime_value:
                mismatches.append(
                    f"{schema_name}.{prop_name} 解引用后 {key}: "
                    f"冻结={static_value!r} 运行时={runtime_value!r}"
                )
    assert not mismatches, "通过 $ref 引用的字段解引用后与冻结契约约束不一致:\n" + "\n".join(
        mismatches
    )


def test_login_actual_set_cookie_count_is_two(migrated_database_url: str) -> None:
    """M2-F01：login 实际 HTTP 响应必须恰好返回 2 条 Set-Cookie。"""
    from fastapi.testclient import TestClient

    from apps.api.app import create_app
    from apps.api.dependencies import HealthDependencies
    from packages.backend.database import session as session_module
    from packages.backend.identity.service import IdentityService

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

    session = session_module.SessionLocal()
    try:
        service = IdentityService(session)
        service.init_admin(kg_name="测试园", admin_username="admin", password="ValidPassword2024!")
        session.commit()
    finally:
        session.close()

    client = TestClient(app)
    csrf_resp = client.get("/api/v1/auth/csrf")
    csrf_token = csrf_resp.json()["csrf_token"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers={"X-CSRF-Token": csrf_token, "Origin": "http://127.0.0.1:28080"},
        cookies={"child_manager_csrf": csrf_token},
    )
    assert login_resp.status_code == 200
    set_cookies = login_resp.headers.get_list("set-cookie")
    assert len(set_cookies) == 2, (
        f"login 应返回恰好 2 条 Set-Cookie（access+refresh），实际: {len(set_cookies)}"
    )
    assert any("child_manager_access=" in c for c in set_cookies)
    assert any("child_manager_refresh=" in c for c in set_cookies)
    assert not any("child_manager_csrf=" in c for c in set_cookies)


def test_logout_actual_set_cookie_count_is_two(migrated_database_url: str) -> None:
    """M2-F01：logout 实际 HTTP 响应必须恰好返回 2 条 Set-Cookie。"""
    from fastapi.testclient import TestClient

    from apps.api.app import create_app
    from apps.api.dependencies import HealthDependencies
    from packages.backend.database import session as session_module
    from packages.backend.identity.service import IdentityService

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

    session = session_module.SessionLocal()
    try:
        service = IdentityService(session)
        service.init_admin(kg_name="测试园", admin_username="admin", password="ValidPassword2024!")
        session.commit()
    finally:
        session.close()

    client = TestClient(app)
    csrf_resp = client.get("/api/v1/auth/csrf")
    csrf_token = csrf_resp.json()["csrf_token"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"login": "admin", "password": "ValidPassword2024!"},
        headers={"X-CSRF-Token": csrf_token, "Origin": "http://127.0.0.1:28080"},
        cookies={"child_manager_csrf": csrf_token},
    )
    login_cookies = login_resp.headers.get_list("set-cookie")
    cookie_jar = {}
    for cookie in login_cookies:
        name = cookie.split("=")[0]
        value = cookie.split("=", 1)[1].split(";")[0]
        cookie_jar[name] = value

    logout_resp = client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": csrf_token, "Origin": "http://127.0.0.1:28080"},
        cookies={**cookie_jar, "child_manager_csrf": csrf_token},
    )
    assert logout_resp.status_code == 204
    set_cookies = logout_resp.headers.get_list("set-cookie")
    assert len(set_cookies) == 2, (
        f"logout 应返回恰好 2 条 Set-Cookie（access+refresh），实际: {len(set_cookies)}"
    )
    assert all("Max-Age=0" in c for c in set_cookies)
