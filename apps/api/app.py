from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.api.dependencies import HealthDependencies, build_health_dependencies
from apps.api.middleware import request_context_middleware
from packages.backend.observability import configure_logging
from packages.contracts.common import ErrorResponse, HealthResponse

configure_logging()


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    field_errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    from apps.api.middleware import request_id

    request_id_value = request_id(request)
    payload: dict[str, object] = {
        "code": code,
        "message": message,
        "request_id": request_id_value,
        "field_errors": field_errors or [],
    }
    response = JSONResponse(status_code=status_code, content=payload)
    response.headers["X-Request-ID"] = request_id_value
    return response


def custom_openapi(application: FastAPI) -> dict[str, object]:
    if application.openapi_schema:
        return application.openapi_schema

    openapi_schema = get_openapi(
        title=application.title,
        version=application.version,
        routes=application.routes,
    )

    # 从公共模型生成 schema，提取 $defs 合并到顶层
    all_defs: dict[str, object] = {}

    error_schema = ErrorResponse.model_json_schema(ref_template="#/components/schemas/{model}")
    all_defs.update(error_schema.pop("$defs", {}))

    health_schema = HealthResponse.model_json_schema(ref_template="#/components/schemas/{model}")
    all_defs.update(health_schema.pop("$defs", {}))

    unavailable_schema: dict[str, object] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["code", "message", "request_id", "field_errors"],
        "properties": {
            "code": {
                "type": "string",
                "enum": [
                    "database.unavailable",
                    "configuration.unavailable",
                ],
            },
            "message": {"type": "string"},
            "request_id": {"type": "string", "format": "uuid"},
            "field_errors": {
                "type": "array",
                "maxItems": 0,
                "items": {"$ref": "#/components/schemas/FieldError"},
            },
        },
    }

    schemas: dict[str, object] = {
        **all_defs,
        "Error": error_schema,
        "Health": health_schema,
        "HealthResponse": health_schema,
        "UnavailableError": unavailable_schema,
    }
    openapi_schema["components"] = {
        "schemas": schemas,
        "responses": {
            "ErrorResponse": {
                "description": "错误响应",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/Error"}},
                },
            },
            "HealthOk": {
                "description": "健康状态",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/Health"}},
                },
            },
            "Unavailable": {
                "description": "服务不可用",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/UnavailableError"}
                    },
                },
            },
        },
    }
    application.openapi_schema = openapi_schema
    return openapi_schema


async def _live_handler() -> dict[str, object]:
    return {
        "status": "ok",
        "checks": {},
    }


async def _ready_handler(request: Request, health: HealthDependencies) -> JSONResponse:
    from apps.api.dependencies import _safe_check

    database_ready = await _safe_check("database", health.database)
    if not database_ready:
        return _error_response(
            request,
            status_code=503,
            code="database.unavailable",
            message="数据库暂不可用,请稍后重试。",
        )
    if not health.security_ready:
        return _error_response(
            request,
            status_code=503,
            code="configuration.unavailable",
            message="服务端安全配置不可用。",
        )

    checks: dict[str, str] = {
        "database": "ok",
        "security": "ok",
    }
    for name, check in [
        ("redis", health.redis),
        ("ai", health.ai),
        ("calendar", health.calendar),
        ("template", health.template),
        ("export_storage", health.export_storage),
    ]:
        checks[name] = "ok" if await _safe_check(name, check) else "degraded"

    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return JSONResponse(content={"status": status, "checks": checks})


async def _validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    field_errors: list[dict[str, str]] = []
    for error in exc.errors():
        field = ".".join(str(part) for part in error["loc"] if part != "body")
        field_errors.append(
            {
                "field": field,
                "code": str(error["type"]),
                "message": "请求字段无效。",
            }
        )
    return _error_response(
        request,
        status_code=422,
        code="request.validation_error",
        message="请求参数无效,请检查后重试。",
        field_errors=field_errors,
    )


async def _http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if exc.status_code == 404:
        code = "resource.not_found"
        message = "请求的资源不存在。"
    elif exc.status_code == 405:
        code = "request.method_not_allowed"
        message = "请求方法不被允许。"
    else:
        code = "request.http_error"
        message = "请求处理失败。"
    return _error_response(
        request,
        status_code=exc.status_code,
        code=code,
        message=message,
    )


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    import structlog

    logger = structlog.get_logger(__name__)
    logger.error(
        "unhandled_exception",
        path=str(request.url.path),
        error_type=type(exc).__name__,
    )
    return _error_response(
        request,
        status_code=500,
        code="server.internal_error",
        message="服务器内部错误,请稍后重试。",
    )


def create_app(dependencies: HealthDependencies | None = None) -> FastAPI:
    health = dependencies or build_health_dependencies()
    application = FastAPI(title="Child Manager API")
    application.openapi = lambda: custom_openapi(application)

    application.middleware("http")(request_context_middleware)

    application.get(
        "/health/live",
        response_model=HealthResponse,
        responses={},
    )(_live_handler)

    async def ready_endpoint(request: Request) -> JSONResponse:
        return await _ready_handler(request, health)

    application.get(
        "/health/ready",
        response_model=HealthResponse,
        responses={
            503: {"model": None, "description": "服务不可用"},
        },
    )(ready_endpoint)

    application.exception_handler(RequestValidationError)(_validation_error_handler)
    application.exception_handler(StarletteHTTPException)(_http_exception_handler)
    application.exception_handler(Exception)(_unhandled_error_handler)

    return application
