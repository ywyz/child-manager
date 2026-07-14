"""API 请求 ID 与追踪 ID 中间件。"""

import re
from uuid import UUID, uuid7

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from packages.backend.observability import REQUEST_ID, TRACE_ID

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def _request_id(value: str) -> str:
    try:
        return str(UUID(value))
    except ValueError:
        return str(uuid7())


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        supplied_request_id = headers.get("x-request-id", "")
        request_id = _request_id(supplied_request_id)
        supplied_trace_id = headers.get("x-trace-id", "")
        trace_id = (
            supplied_trace_id if _REQUEST_ID_PATTERN.fullmatch(supplied_trace_id) else request_id
        )
        state = scope.setdefault("state", {})
        state["request_id"] = request_id
        state["trace_id"] = trace_id
        request_token = REQUEST_ID.set(request_id)
        trace_token = TRACE_ID.set(trace_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["X-Request-ID"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            REQUEST_ID.reset(request_token)
            TRACE_ID.reset(trace_token)
