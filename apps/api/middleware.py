from collections.abc import Awaitable, Callable
from uuid import UUID, uuid7

import structlog.contextvars as ctxvars
from fastapi import Request
from fastapi.responses import JSONResponse


def request_id(request: Request) -> str:
    return str(request.state.request_id)


async def request_context_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[JSONResponse]],
) -> JSONResponse:
    headers = request.headers
    supplied_request_id = headers.get("x-request-id", "")
    try:
        UUID(supplied_request_id)
        parsed_request_id = supplied_request_id
    except ValueError, AttributeError:
        parsed_request_id = str(uuid7())

    supplied_trace_id = headers.get("x-trace-id", "")
    try:
        UUID(supplied_trace_id)
        trace_id = supplied_trace_id
    except ValueError, AttributeError:
        trace_id = parsed_request_id

    state = request.state
    state.request_id = parsed_request_id
    state.trace_id = trace_id

    ctxvars.clear_contextvars()
    ctxvars.bind_contextvars(request_id=parsed_request_id, trace_id=trace_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = parsed_request_id
        return response
    finally:
        ctxvars.clear_contextvars()
