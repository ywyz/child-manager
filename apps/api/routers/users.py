"""管理员账号、邀请、凭据、恢复和会话管理端点。"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Request

from apps.api.dependencies import AdminSessionDependency, IdentityServiceDependency
from apps.api.routers.auth import _credential, require_csrf
from packages.backend.identity.repository import InvitationRecord
from packages.backend.identity.service import IdentityError, ManagedUser
from packages.contracts.identity import (
    AccountActivationRequest,
    AdminCredentialRevocationResult,
    CreateUserRequest,
    CredentialList,
    InvitationCreateRequest,
    InvitationIssued,
    InvitationList,
    RecoveryApprovalRequest,
    RecoveryEnrollmentIssued,
    RecoveryRequestList,
    RoleUpdate,
    UserPage,
    UserPatch,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


def _user(value: ManagedUser) -> dict[str, object]:
    record = value.user
    return {
        "id": record.id,
        "username": record.username,
        "phone_e164": record.phone_e164,
        "display_name": record.display_name,
        "role_codes": value.role_codes,
        "status": record.status,
        "credential_count": value.credential_count,
        "activated_at": record.activated_at,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


def _invitation(record: InvitationRecord, secret: str | None = None) -> dict[str, object]:
    if record.revoked_at is not None:
        status = "revoked"
    elif record.consumed_at is not None:
        status = "consumed"
    elif record.expires_at <= datetime.now(UTC):
        status = "expired"
    else:
        status = "pending"
    result: dict[str, object] = {
        "id": record.id,
        "user_id": record.user_id,
        "status": status,
        "expires_at": record.expires_at,
        "issued_at": record.issued_at,
        "consumed_at": record.consumed_at,
        "revoked_at": record.revoked_at,
    }
    if secret is not None:
        result["invitation_token"] = secret
    return result


@router.get("", response_model=UserPage)
def list_users(
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    if page < 1 or not 1 <= page_size <= 100:
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
    return _user(
        service.create_user(
            session,
            username=body.username,
            phone_e164=body.phone_e164,
            display_name=body.display_name,
            role_codes=list(body.role_codes),
            request_id=_request_id(request),
        )
    )


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
    return _user(
        service.update_user(
            session,
            user_id,
            username=body.username,
            phone_e164=phone,
            display_name=body.display_name,
            request_id=_request_id(request),
        )
    )


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
    body: AccountActivationRequest,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    del body
    require_csrf(request)
    return _user(
        service.set_status(session, user_id, status="active", request_id=_request_id(request))
    )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate(
    user_id: UUID,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    return _user(
        service.set_status(session, user_id, status="suspended", request_id=_request_id(request))
    )


@router.get("/{user_id}/invitations", response_model=InvitationList)
def invitations(
    user_id: UUID,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    return {"items": [_invitation(item) for item in service.list_invitations(session, user_id)]}


@router.post("/{user_id}/invitations", status_code=201, response_model=InvitationIssued)
def invitation_issue(
    user_id: UUID,
    body: InvitationCreateRequest,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    record, secret = service.issue_invitation(
        session, user_id, expires_in_hours=body.expires_in_hours
    )
    return _invitation(record, secret)


@router.post("/{user_id}/invitations/{invitation_id}/revoke", status_code=204)
def invitation_revoke(
    user_id: UUID,
    invitation_id: UUID,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> None:
    require_csrf(request)
    service.revoke_invitation(session, user_id, invitation_id)


@router.get("/{user_id}/credentials", response_model=CredentialList)
def credentials(
    user_id: UUID,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    return {"items": [_credential(item) for item in service.list_credentials(session, user_id)]}


@router.delete(
    "/{user_id}/credentials/{credential_id}", response_model=AdminCredentialRevocationResult
)
def credential_revoke(
    user_id: UUID,
    credential_id: UUID,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    require_csrf(request)
    sessions_revoked, reinvitation = service.admin_revoke_credential(
        session, user_id, credential_id
    )
    return {
        "credential_id": credential_id,
        "sessions_revoked": sessions_revoked,
        "reinvitation": (_invitation(reinvitation[0], reinvitation[1]) if reinvitation else None),
    }


@router.post("/{user_id}/sessions/revoke", status_code=204)
def sessions_revoke(
    user_id: UUID,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> None:
    require_csrf(request)
    with service._connect() as connection, connection.transaction():
        from packages.backend.identity.repository import IdentityRepository

        IdentityRepository(connection, session.user.kindergarten_id).revoke_user_sessions(
            user_id, reason="admin_revoked"
        )


@router.get("/{user_id}/recovery-requests", response_model=RecoveryRequestList)
def recovery_requests(
    user_id: UUID,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    items = service.list_recovery_requests(session, user_id)
    return {
        "items": [
            {
                "id": item.id,
                "user_id": item.user_id,
                "status": item.status,
                "requested_at": item.requested_at,
                "expires_at": item.expires_at,
                "approved_at": item.approved_at,
            }
            for item in items
        ]
    }


@router.post(
    "/{user_id}/recovery-requests/{recovery_request_id}/approve",
    response_model=RecoveryEnrollmentIssued,
)
def recovery_approve(
    user_id: UUID,
    recovery_request_id: UUID,
    body: RecoveryApprovalRequest,
    request: Request,
    session: AdminSessionDependency,
    service: IdentityServiceDependency,
) -> dict[str, object]:
    del body
    require_csrf(request)
    enrollment_token, expires_at = service.approve_recovery_request(
        session, user_id, recovery_request_id
    )
    return {
        "recovery_request_id": recovery_request_id,
        "enrollment_token": enrollment_token,
        "expires_at": expires_at,
    }
