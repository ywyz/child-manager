"""同源 Cookie、WebAuthn、邀请、恢复与会话端点。"""

import os
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, Request, Response

from apps.api.dependencies import CurrentSessionDependency, IdentityServiceDependency
from packages.backend.identity.auth_throttle import (
    GLOBAL_THROTTLE_SOURCE,
    subject_throttle_source,
)
from packages.backend.identity.client_ip import resolve_client_ip
from packages.backend.identity.csrf import issue_csrf_token, verify_csrf_token
from packages.backend.identity.repository import CredentialRecord
from packages.backend.identity.service import AuthResult, IdentityError, SessionUser
from packages.contracts.identity import (
    AuthenticationResult,
    AuthenticationVerifyRequest,
    BootstrapRegistrationOptionsRequest,
    Credential,
    CredentialList,
    CredentialPatch,
    CsrfResponse,
    CurrentUser,
    InvitationRegistrationOptionsRequest,
    RecoveryCodeIssued,
    RecoveryCompleted,
    RecoveryRegistrationOptionsRequest,
    RecoveryRequestAccepted,
    RecoveryRequestCreate,
    RegistrationPending,
    RegistrationVerifyRequest,
    SessionList,
    StepUpResult,
    WebAuthnAuthenticationOptions,
    WebAuthnRegistrationOptions,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

ACCESS_COOKIE = "child_manager_access"
REFRESH_COOKIE = "child_manager_refresh"
CSRF_COOKIE = "child_manager_csrf"


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


def _cookie_secure() -> bool:
    return os.environ.get("CHILD_MANAGER_COOKIE_SECURE", "true").lower() == "true"


def _loopback_aliases(origin: str) -> set[str]:
    parsed = urlsplit(origin)
    aliases = {origin.rstrip("/")}
    if parsed.hostname in {"127.0.0.1", "localhost"}:
        alternate = "localhost" if parsed.hostname == "127.0.0.1" else "127.0.0.1"
        port = f":{parsed.port}" if parsed.port is not None else ""
        aliases.add(f"{parsed.scheme}://{alternate}{port}")
    return aliases


def _allowed_origins() -> set[str]:
    configured = os.environ.get("CHILD_MANAGER_ALLOWED_ORIGINS")
    if configured:
        result: set[str] = set()
        for value in configured.split(","):
            if value.strip():
                result.update(_loopback_aliases(value.strip()))
        return result
    if os.environ.get("CHILD_MANAGER_ENV", "production") not in {"development", "test"}:
        return set()
    web_port = os.environ.get("CHILD_MANAGER_WEB_PORT", "18080")
    return {
        "http://testserver",
        f"http://127.0.0.1:{web_port}",
        f"http://localhost:{web_port}",
    }


def _origin(request: Request) -> str:
    origin = request.headers.get("origin")
    if origin is None:
        referer = request.headers.get("referer")
        if referer:
            parsed = urlsplit(referer)
            origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin is None or origin.rstrip("/") not in _allowed_origins():
        raise IdentityError(403, "auth.csrf_invalid", "请求来源或 CSRF 校验失败。")
    return origin.rstrip("/")


def require_csrf(request: Request) -> None:
    origin = _origin(request)
    del origin
    token = request.headers.get("x-csrf-token")
    cookie = request.cookies.get(CSRF_COOKIE)
    signing_key = os.environ.get("CHILD_MANAGER_CSRF_SIGNING_KEY", "")
    if not (
        token
        and cookie
        and token == cookie
        and signing_key
        and verify_csrf_token(token, signing_key)
    ):
        raise IdentityError(403, "auth.csrf_invalid", "请求来源或 CSRF 校验失败。")


def _set_auth_cookies(response: Response, result: AuthResult) -> None:
    common = {"secure": _cookie_secure(), "httponly": True, "samesite": "lax", "path": "/"}
    response.set_cookie(ACCESS_COOKIE, result.access_token, max_age=15 * 60, **common)
    response.set_cookie(REFRESH_COOKIE, result.refresh_token, max_age=7 * 24 * 60 * 60, **common)


def _clear_auth_cookies(response: Response) -> None:
    common = {"secure": _cookie_secure(), "httponly": True, "samesite": "lax", "path": "/"}
    response.delete_cookie(ACCESS_COOKIE, **common)
    response.delete_cookie(REFRESH_COOKIE, **common)


def _payload(service: IdentityServiceDependency, session: SessionUser) -> dict[str, object]:
    return {
        "id": session.user.id,
        "username": session.user.username,
        "display_name": session.user.display_name,
        "kindergarten": service.kindergarten_summary(session.user.kindergarten_id),
        "role_codes": session.role_codes,
        "capabilities": session.capabilities,
        "session_id": session.session_id,
        "last_reauthenticated_at": session.last_reauthenticated_at,
    }


def _credential(record: CredentialRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "label": record.label,
        "transports": record.transports,
        "backup_eligible": record.backup_eligible,
        "backup_state": record.backup_state,
        "created_via": record.created_via,
        "created_at": record.created_at,
        "last_used_at": record.last_used_at,
        "revoked_at": record.revoked_at,
    }


def _source(request: Request) -> str:
    socket_peer = request.client.host if request.client else "127.0.0.1"
    return resolve_client_ip(
        socket_peer=socket_peer,
        internal_client_ip=request.headers.get("x-child-manager-client-ip"),
        trusted_bff_peers=request.app.state.trusted_bff_peers,
    )


ThrottleBucket = tuple[str, str, bool]


def _check_public_throttle(
    request: Request,
    purpose: str,
    *,
    material: str | None = None,
    subject: str | None = None,
) -> tuple[str, tuple[ThrottleBucket, ...]]:
    source = _source(request)
    throttle = request.app.state.auth_throttle
    if throttle is None:
        raise IdentityError(503, "configuration.unavailable", "登录服务暂不可用，请稍后重试。")
    now = request.app.state.clock()
    subject_values = tuple(
        dict.fromkeys(value for value in (subject, material) if value is not None)
    )
    buckets: tuple[ThrottleBucket, ...] = (
        (source, purpose, True),
        *(
            (
                subject_throttle_source(purpose=purpose, subject=value),
                purpose,
                True,
            )
            for value in subject_values
        ),
        (GLOBAL_THROTTLE_SOURCE, purpose, False),
    )
    for bucket_source, bucket_purpose, _reset_on_success in buckets:
        decision = throttle.check(
            source=bucket_source,
            purpose=bucket_purpose,
            now=now,
        )
        if not decision.allowed:
            raise IdentityError(429, "auth.rate_limited", "尝试过多，请稍后重试。")
    return source, buckets


def _record_public_failure(request: Request, buckets: tuple[ThrottleBucket, ...]) -> None:
    now = request.app.state.clock()
    for source, purpose, _reset_on_success in buckets:
        request.app.state.auth_throttle.record_failure(
            source=source,
            purpose=purpose,
            now=now,
        )


def _clear_public_throttle(request: Request, buckets: tuple[ThrottleBucket, ...]) -> None:
    now = request.app.state.clock()
    for source, purpose, reset_on_success in buckets:
        if reset_on_success:
            request.app.state.auth_throttle.record_success(
                source=source,
                purpose=purpose,
                now=now,
            )


@router.get("/csrf", response_model=CsrfResponse)
def csrf(response: Response) -> dict[str, str]:
    signing_key = os.environ.get("CHILD_MANAGER_CSRF_SIGNING_KEY")
    if not signing_key:
        raise IdentityError(503, "configuration.unavailable", "服务端安全配置不可用。")
    token = issue_csrf_token(signing_key)
    response.set_cookie(
        CSRF_COOKIE,
        token,
        max_age=7 * 24 * 60 * 60,
        secure=_cookie_secure(),
        httponly=False,
        samesite="lax",
        path="/",
    )
    return {"csrf_token": token}


@router.post(
    "/bootstrap/registration/options",
    response_model=WebAuthnRegistrationOptions,
    response_model_exclude_none=True,
)
def bootstrap_options(
    body: BootstrapRegistrationOptionsRequest,
    request: Request,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request, "bootstrap_options", material=body.bootstrap_token
    )
    try:
        result = service.bootstrap_registration_options(
            body.bootstrap_token, origin=_origin(request)
        )
    except IdentityError as exc:
        if exc.code == "identity.material_unavailable":
            _record_public_failure(request, buckets)
            service.record_public_authorization_failure(
                purpose="bootstrap_options",
                source=source,
                request_id=_request_id(request),
            )
        raise
    _clear_public_throttle(request, buckets)
    return result


@router.post("/bootstrap/registration/verify", response_model=RegistrationPending)
def bootstrap_verify(
    body: RegistrationVerifyRequest,
    request: Request,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request, "bootstrap_verify", material=str(body.ceremony_id)
    )
    try:
        credential, user_id = service.verify_bootstrap_registration(
            ceremony_id=body.ceremony_id,
            credential=body.credential.model_dump(exclude_none=True),
            label=body.label,
            source=source,
            request_id=_request_id(request),
        )
    except IdentityError as exc:
        if exc.code == "identity.material_unavailable":
            _record_public_failure(request, buckets)
        raise
    _clear_public_throttle(request, buckets)
    return {
        "user_id": user_id,
        "status": "pending_verification",
        "credential_id": credential.id,
        "verification_required": True,
    }


@router.post(
    "/invitation/registration/options",
    response_model=WebAuthnRegistrationOptions,
    response_model_exclude_none=True,
)
def invitation_options(
    body: InvitationRegistrationOptionsRequest,
    request: Request,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request, "invitation_options", material=body.invitation_token
    )
    try:
        result = service.invitation_registration_options(
            body.invitation_token, origin=_origin(request)
        )
    except IdentityError as exc:
        if exc.code == "identity.material_unavailable":
            _record_public_failure(request, buckets)
            service.record_public_authorization_failure(
                purpose="invitation_options",
                source=source,
                request_id=_request_id(request),
            )
        raise
    _clear_public_throttle(request, buckets)
    return result


@router.post("/invitation/registration/verify", response_model=RegistrationPending)
def invitation_verify(
    body: RegistrationVerifyRequest,
    request: Request,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request, "invitation_verify", material=str(body.ceremony_id)
    )
    try:
        credential, user_id = service.verify_invitation_registration(
            ceremony_id=body.ceremony_id,
            credential=body.credential.model_dump(exclude_none=True),
            label=body.label,
            source=source,
            request_id=_request_id(request),
        )
    except IdentityError as exc:
        if exc.code == "identity.material_unavailable":
            _record_public_failure(request, buckets)
        raise
    _clear_public_throttle(request, buckets)
    return {
        "user_id": user_id,
        "status": "pending_verification",
        "credential_id": credential.id,
        "verification_required": True,
    }


@router.post("/authentication/options", response_model=WebAuthnAuthenticationOptions)
def authentication_start(request: Request, service: IdentityServiceDependency) -> dict[str, object]:
    require_csrf(request)
    _check_public_throttle(request, "authentication")
    return service.authentication_options(origin=_origin(request))


@router.post("/authentication/verify", response_model=AuthenticationResult)
def authentication_verify(
    body: AuthenticationVerifyRequest,
    request: Request,
    response: Response,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request,
        "authentication",
        subject=body.credential.id,
    )
    try:
        result = service.verify_authentication(
            ceremony_id=body.ceremony_id,
            credential=body.credential.model_dump(exclude_none=False),
            source=source,
            request_id=_request_id(request),
        )
    except IdentityError as exc:
        if exc.code in {"auth.authentication_failed", "auth.ceremony_expired"}:
            _record_public_failure(request, buckets)
        raise
    _clear_public_throttle(request, buckets)
    _set_auth_cookies(response, result)
    return {"user": _payload(service, result.session), "recovery_code": result.recovery_code}


@router.post("/step-up/options", response_model=WebAuthnAuthenticationOptions)
def step_up_options(
    request: Request, session: CurrentSessionDependency, service: IdentityServiceDependency
) -> dict[str, object]:
    require_csrf(request)
    _check_public_throttle(request, "step_up", subject=str(session.user.id))
    return service.step_up_options(session, origin=_origin(request))


@router.post("/step-up/verify", response_model=StepUpResult)
def step_up_verify(
    body: AuthenticationVerifyRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request,
        "step_up",
        subject=str(session.user.id),
    )
    try:
        verified_at, valid_until = service.verify_step_up(
            session,
            ceremony_id=body.ceremony_id,
            credential=body.credential.model_dump(exclude_none=False),
            source=source,
            request_id=_request_id(request),
        )
    except IdentityError as exc:
        if exc.code in {"auth.authentication_failed", "auth.ceremony_expired"}:
            _record_public_failure(request, buckets)
        raise
    _clear_public_throttle(request, buckets)
    return {"verified_at": verified_at, "valid_until": valid_until}


@router.post("/refresh", response_model=CurrentUser)
def refresh(
    request: Request, response: Response, service: IdentityServiceDependency
) -> dict[str, object]:
    require_csrf(request)
    raw = request.cookies.get(REFRESH_COOKIE)
    source, buckets = _check_public_throttle(
        request,
        "refresh",
        material=raw or "<missing>",
    )
    if not raw:
        _record_public_failure(request, buckets)
        service.record_public_authorization_failure(
            purpose="refresh",
            source=source,
            request_id=_request_id(request),
        )
        raise IdentityError(401, "auth.unauthenticated", "刷新会话已失效，请重新登录。")
    try:
        result = service.refresh(raw, request_id=_request_id(request))
    except IdentityError as exc:
        if exc.status_code == 401:
            _record_public_failure(request, buckets)
            service.record_public_authorization_failure(
                purpose="refresh",
                source=source,
                request_id=_request_id(request),
            )
        raise
    _clear_public_throttle(request, buckets)
    _set_auth_cookies(response, result)
    return _payload(service, result.session)


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, service: IdentityServiceDependency) -> None:
    require_csrf(request)
    service.logout(
        request.cookies.get(REFRESH_COOKIE),
        request_id=_request_id(request),
        raw_access_token=request.cookies.get(ACCESS_COOKIE),
    )
    _clear_auth_cookies(response)


@router.get("/me", response_model=CurrentUser)
def me(session: CurrentSessionDependency, service: IdentityServiceDependency) -> dict[str, object]:
    return _payload(service, session)


@router.get("/credentials", response_model=CredentialList)
def credentials(
    session: CurrentSessionDependency, service: IdentityServiceDependency
) -> dict[str, object]:
    return {"items": [_credential(item) for item in service.list_credentials(session)]}


@router.post(
    "/credentials/registration/options",
    response_model=WebAuthnRegistrationOptions,
    response_model_exclude_none=True,
)
def credential_options(
    request: Request, session: CurrentSessionDependency, service: IdentityServiceDependency
) -> dict[str, object]:
    require_csrf(request)
    _check_public_throttle(
        request,
        "credential_registration",
        material=str(session.token_family_id),
    )
    return service.self_add_registration_options(session, origin=_origin(request))


@router.post("/credentials/registration/verify", response_model=Credential, status_code=201)
def credential_verify(
    body: RegistrationVerifyRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request,
        "credential_registration",
        material=str(session.token_family_id),
    )
    try:
        credential = service.verify_self_add_registration(
            session,
            ceremony_id=body.ceremony_id,
            credential=body.credential.model_dump(exclude_none=True),
            label=body.label,
            source=source,
            request_id=_request_id(request),
        )
    except IdentityError as exc:
        if exc.code == "identity.material_unavailable":
            _record_public_failure(request, buckets)
        raise
    _clear_public_throttle(request, buckets)
    return _credential(credential)


@router.patch("/credentials/{credential_id}", response_model=Credential)
def credential_patch(
    credential_id: UUID,
    body: CredentialPatch,
    request: Request,
    session: CurrentSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    return _credential(service.rename_credential(session, credential_id, body.label))


@router.delete("/credentials/{credential_id}", status_code=204)
def credential_revoke(
    credential_id: UUID,
    request: Request,
    session: CurrentSessionDependency,
    service: IdentityServiceDependency,
) -> None:
    require_csrf(request)
    service.revoke_own_credential(session, credential_id)


@router.post("/recovery/requests", status_code=202, response_model=RecoveryRequestAccepted)
def recovery_request(
    body: RecoveryRequestCreate,
    request: Request,
    response: Response,
    service: IdentityServiceDependency,
) -> dict[str, str]:
    require_csrf(request)
    login_key = service.safe_login_key(body.login)
    source, buckets = _check_public_throttle(
        request,
        "recovery_request",
        material=f"{login_key}\0{body.recovery_code}",
        subject=login_key or "<invalid-login>",
    )
    accepted = service.submit_recovery_request(login=body.login, recovery_code=body.recovery_code)
    if accepted:
        _clear_public_throttle(request, buckets)
    else:
        _record_public_failure(request, buckets)
        service.record_public_authorization_failure(
            purpose="recovery_request",
            source=source,
            request_id=_request_id(request),
        )
    if request.cookies.get(ACCESS_COOKIE) or request.cookies.get(REFRESH_COOKIE):
        _clear_auth_cookies(response)
    return {"message": "如果账号和恢复材料有效，我们会按既定带外方式继续核验。"}


@router.post(
    "/recovery/registration/options",
    response_model=WebAuthnRegistrationOptions,
    response_model_exclude_none=True,
)
def recovery_options(
    body: RecoveryRegistrationOptionsRequest,
    request: Request,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request, "recovery_options", material=body.enrollment_token
    )
    try:
        result = service.recovery_registration_options(
            body.enrollment_token, origin=_origin(request)
        )
    except IdentityError as exc:
        if exc.code == "identity.material_unavailable":
            _record_public_failure(request, buckets)
            service.record_public_authorization_failure(
                purpose="recovery_options",
                source=source,
                request_id=_request_id(request),
            )
        raise
    _clear_public_throttle(request, buckets)
    return result


@router.post("/recovery/registration/verify", response_model=RecoveryCompleted)
def recovery_verify(
    body: RegistrationVerifyRequest,
    request: Request,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    source, buckets = _check_public_throttle(
        request, "recovery_verify", material=str(body.ceremony_id)
    )
    try:
        credential, recovery_code, sessions_revoked = service.verify_recovery_registration(
            ceremony_id=body.ceremony_id,
            credential=body.credential.model_dump(exclude_none=True),
            label=body.label,
            source=source,
            request_id=_request_id(request),
        )
    except IdentityError as exc:
        if exc.code == "identity.material_unavailable":
            _record_public_failure(request, buckets)
        raise
    _clear_public_throttle(request, buckets)
    return {
        "credential": _credential(credential),
        "recovery_code": recovery_code,
        "sessions_revoked": sessions_revoked,
    }


@router.post("/recovery-code/rotate", response_model=RecoveryCodeIssued)
def recovery_code_rotate(
    request: Request, session: CurrentSessionDependency, service: IdentityServiceDependency
) -> dict[str, object]:
    require_csrf(request)
    recovery_code, issued_at = service.rotate_recovery_code(session)
    return {"recovery_code": recovery_code, "issued_at": issued_at}


@router.get("/sessions", response_model=SessionList)
def sessions(
    session: CurrentSessionDependency, service: IdentityServiceDependency
) -> dict[str, object]:
    items = []
    for item in service.list_sessions(session):
        items.append(
            {
                "id": item.token_family_id,
                "is_current": item.token_family_id == session.token_family_id,
                "created_at": item.issued_at,
                "last_seen_at": item.last_used_at or item.issued_at,
                "expires_at": item.expires_at,
                "revoked_at": item.revoked_at,
                "client_ip_hint": None,
                "user_agent_summary": None,
            }
        )
    return {"items": items}


@router.delete("/sessions/{session_id}", status_code=204)
def session_revoke(
    session_id: UUID,
    request: Request,
    response: Response,
    session: CurrentSessionDependency,
    service: IdentityServiceDependency,
) -> None:
    require_csrf(request)
    service.revoke_session(session, session_id)
    if session_id == session.token_family_id:
        _clear_auth_cookies(response)
