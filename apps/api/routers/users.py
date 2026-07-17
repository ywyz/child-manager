"""管理员账号管理端点。"""

from uuid import UUID

from fastapi import APIRouter, Request

from apps.api.dependencies import AdminSessionDependency, IdentityServiceDependency
from apps.api.routers.auth import require_csrf
from packages.backend.identity.service import SessionUser
from packages.contracts.identity import (
    CreateUserRequest,
    PasswordResetRequest,
    RoleUpdate,
    UserPage,
    UserPatch,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


def _user(session: SessionUser) -> dict[str, object]:
    record = session.user
    return {
        "id": record.id,
        "username": record.username,
        "phone_e164": record.phone_e164,
        "display_name": record.display_name,
        "role_codes": session.role_codes,
        "is_active": record.is_active,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@router.get("", response_model=UserPage)
def list_users(
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    if page < 1 or not 1 <= page_size <= 100:
        from packages.backend.identity.service import IdentityError

        raise IdentityError(422, "request.invalid_pagination", "分页参数无效。")
    users, total = service.list_users(session, page=page, page_size=page_size)
    return {
        "items": [_user(user) for user in users],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.post("", status_code=201, response_model=UserResponse)
def create_user(
    body: CreateUserRequest,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    created = service.create_user(
        session,
        username=body.username,
        phone_e164=body.phone_e164,
        display_name=body.display_name,
        password=body.password,
        role_codes=list(body.role_codes),
        request_id=_request_id(request),
    )
    return _user(created)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    return _user(service.get_user(session, user_id))


@router.patch("/{user_id}", response_model=UserResponse)
def patch_user(
    user_id: UUID,
    body: UserPatch,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    current = service.get_user(session, user_id)
    phone = body.phone_e164 if "phone_e164" in body.model_fields_set else current.user.phone_e164
    updated = service.update_user(
        session,
        user_id,
        username=body.username,
        phone_e164=phone,
        display_name=body.display_name,
        request_id=_request_id(request),
    )
    return _user(updated)


@router.put("/{user_id}/roles", response_model=UserResponse)
def set_roles(
    user_id: UUID,
    body: RoleUpdate,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    return _user(
        service.set_roles(session, user_id, list(body.role_codes), request_id=_request_id(request))
    )


@router.post("/{user_id}/activate", response_model=UserResponse)
def activate(
    user_id: UUID,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    return _user(service.set_active(session, user_id, active=True, request_id=_request_id(request)))


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate(
    user_id: UUID,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    return _user(
        service.set_active(session, user_id, active=False, request_id=_request_id(request))
    )


@router.post("/{user_id}/reset-password", status_code=204)
def reset_password(
    user_id: UUID,
    body: PasswordResetRequest,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> None:
    require_csrf(request)
    service.reset_password(session, user_id, body.new_password, request_id=_request_id(request))
