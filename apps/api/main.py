import os
from collections.abc import Awaitable, Callable
from uuid import uuid7

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from packages.backend.observability import configure_logging

configure_logging()

LOGGER = structlog.get_logger(__name__)


def _request_id(request: Request) -> str:
    return str(request.state.request_id)


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    field_errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    request_id = _request_id(request)
    payload: dict[str, object] = {
        "code": code,
        "message": message,
        "request_id": request_id,
        "field_errors": field_errors or [],
    }
    response = JSONResponse(status_code=status_code, content=payload)
    response.headers["X-Request-ID"] = request_id
    return response


async def _safe_check(name: str, check: Callable[[], Awaitable[bool]]) -> bool:
    try:
        return await check()
    except Exception as exc:
        LOGGER.warning("health_check_failed", component=name, error_type=type(exc).__name__)
        return False


class HealthDependencies:
    def __init__(
        self,
        database: Callable[[], Awaitable[bool]],
        redis: Callable[[], Awaitable[bool]],
        ai: Callable[[], Awaitable[bool]],
        calendar: Callable[[], Awaitable[bool]],
        template: Callable[[], Awaitable[bool]],
        export_storage: Callable[[], Awaitable[bool]],
        security_ready: bool,
    ) -> None:
        self.database = database
        self.redis = redis
        self.ai = ai
        self.calendar = calendar
        self.template = template
        self.export_storage = export_storage
        self.security_ready = security_ready


async def _ai_unconfigured() -> bool:
    return False


async def _runtime_storage_unconfigured() -> bool:
    return False


async def _calendar_library_available() -> bool:
    try:
        from importlib import import_module

        calendar_module = import_module("chinese_calendar")
    except ImportError:
        return False
    return callable(getattr(calendar_module, "is_workday", None))


def build_health_dependencies() -> HealthDependencies:
    from pathlib import Path

    import psycopg
    from redis.asyncio import Redis

    repository_root = Path(__file__).resolve().parents[2]
    runtime_root_value = os.environ.get("CHILD_MANAGER_RUNTIME_ROOT")

    async def database_check() -> bool:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            return False
        native_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        connection = await psycopg.AsyncConnection.connect(native_url, connect_timeout=2)
        async with connection:
            await connection.execute("SELECT 1")
        return True

    async def redis_check() -> bool:
        redis_url = os.environ.get("CHILD_MANAGER_REDIS_URL")
        if not redis_url:
            return False
        # pyright: ignore[reportUnknownMemberType]
        client = Redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        try:
            # pyright: ignore[reportUnknownMemberType]
            return bool(await client.ping())
        finally:
            await client.aclose()

    async def path_check(path: Path, *, writable: bool = False) -> bool:
        return path.is_dir() and (not writable or os.access(path, os.W_OK))

    if runtime_root_value:

        async def export_storage_check() -> bool:
            return await path_check(Path(runtime_root_value) / "exports", writable=True)

    else:
        export_storage_check = _runtime_storage_unconfigured

    security_values = (
        os.environ.get("CHILD_MANAGER_JWT_SIGNING_KEY"),
        os.environ.get("CHILD_MANAGER_CSRF_SIGNING_KEY"),
    )

    async def template_check() -> bool:
        return (repository_root / "templates/teacherplan/teacherplan.docx").is_file()

    return HealthDependencies(
        database=database_check,
        redis=redis_check,
        ai=_ai_unconfigured,
        calendar=_calendar_library_available,
        template=template_check,
        export_storage=export_storage_check,
        security_ready=all(value is not None and bool(value.strip()) for value in security_values),
    )


def custom_openapi(application: FastAPI) -> dict[str, object]:
    if application.openapi_schema:
        return application.openapi_schema
    from fastapi.openapi.utils import get_openapi

    from packages.contracts.common import ErrorResponse, HealthResponse

    openapi_schema = get_openapi(
        title=application.title,
        version=application.version,
        routes=application.routes,
    )
    error_schema = ErrorResponse.model_json_schema(
        ref_template="#/components/schemas/$defs/{model}"
    )
    error_defs = error_schema.pop("$defs", {})
    health_schema = HealthResponse.model_json_schema(
        ref_template="#/components/schemas/$defs/{model}"
    )
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
                "items": {"$ref": "#/components/schemas/$defs/FieldError"},
            },
        },
    }
    schemas: dict[str, object] = {
        **error_defs,
        "Error": error_schema,
        "Health": health_schema,
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


async def _request_context_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[JSONResponse]],
) -> JSONResponse:
    from uuid import UUID

    import structlog.contextvars as ctxvars

    headers = request.headers
    supplied_request_id = headers.get("x-request-id", "")
    try:
        UUID(supplied_request_id)
        request_id = supplied_request_id
    except ValueError, AttributeError:
        request_id = str(uuid7())

    supplied_trace_id = headers.get("x-trace-id", "")
    try:
        UUID(supplied_trace_id)
        trace_id = supplied_trace_id
    except ValueError, AttributeError:
        trace_id = request_id

    state = request.state
    state.request_id = request_id
    state.trace_id = trace_id

    ctxvars.clear_contextvars()
    ctxvars.bind_contextvars(request_id=request_id, trace_id=trace_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        ctxvars.clear_contextvars()


async def _live_handler(request: Request) -> dict[str, object]:
    return {
        "status": "ok",
        "checks": {},
    }


async def _ready_handler(request: Request, health: HealthDependencies) -> JSONResponse:
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
    LOGGER.error(
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

    application.middleware("http")(_request_context_middleware)

    from packages.contracts.common import HealthResponse

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


app = create_app()


def _validate_bind_host(host: str) -> None:
    """进程只能绑定回环地址，包括开发环境。"""
    from ipaddress import ip_address

    try:
        if ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    if host == "localhost":
        return
    raise ValueError(f"API 只能绑定回环地址,当前值: {host}")


def main() -> None:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="启动 Child Manager API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=28000, type=int)
    args = parser.parse_args()

    _validate_bind_host(args.host)

    uvicorn.run(
        "apps.api.main:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
