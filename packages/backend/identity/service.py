"""身份与认证业务 Service。"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.backend.audit.service import AuditService
from packages.backend.config import settings
from packages.backend.identity.csrf import generate_csrf_token
from packages.backend.identity.exceptions import LastAdminError, UserNotFoundError
from packages.backend.identity.identifiers import normalize_phone, normalize_username
from packages.backend.identity.models import Kindergarten, User
from packages.backend.identity.passwords import (
    hash_password,
    validate_password,
    verify_password,
)
from packages.backend.identity.repository import IdentityRepository
from packages.backend.identity.tokens import (
    create_access_token,
    generate_refresh_value,
    hash_refresh_value,
    parse_refresh_kindergarten_id,
)
from packages.contracts import audit as audit_events
from packages.contracts.identity import (
    CurrentUser,
    KindergartenSnapshot,
    UserCreateRequest,
    UserPatch,
    UserResponse,
)


@dataclass(frozen=True)
class LoginResult:
    """登录成功后的完整结果，避免使用无类型字典。

    当前用户对象在事务提交前构造完成，Router 层不再额外查询数据库。
    """

    user: User
    roles: list[str]
    kindergarten_id: str
    family_id: str
    access_token: str
    refresh_value: str
    csrf_token: str
    current_user: CurrentUser


@dataclass(frozen=True)
class RefreshResult:
    """刷新成功后的完整结果。"""

    user_id: str
    kindergarten_id: str
    family_id: str
    roles: list[str]
    access_token: str
    refresh_value: str
    csrf_token: str
    current_user: CurrentUser


class IdentityService:
    """身份业务编排：协调 Repository、Token、CSRF 与审计。"""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = IdentityRepository(session)
        self._audit = AuditService(session)

    def _record_identity(
        self,
        *,
        kindergarten_id: str,
        event_type: str,
        actor_user_id: str | None,
        resource_id: str,
        action: str,
        result: str,
        source_ip: str | None = None,
    ) -> None:
        self._audit.record_identity(
            kindergarten_id=kindergarten_id,
            event_type=event_type,
            actor_user_id=actor_user_id,
            resource_id=resource_id,
            action=action,
            result=result,
            source_ip=source_ip,
        )
        # 应用用例方法内部统一控制事务边界；Router/CLI 只负责传输与装配。

    def _get_kindergarten(self) -> Kindergarten | None:
        """M2 单园部署：返回唯一园所。

        当前仅支持单园，所有已认证请求通过 token/session 携带明确的
        kindergarten_id；本方法仅用于登录前定位唯一园所。
        """
        stmt = select(Kindergarten)
        return self._session.execute(stmt).scalar_one_or_none()

    def ensure_roles(self, kindergarten_id: str) -> None:
        """幂等确保园所具备 admin/teacher 角色。"""
        for code, name in (("admin", "管理员"), ("teacher", "教师")):
            if self._repo.get_role_by_code(kindergarten_id, code) is None:
                self._repo.create_role(kindergarten_id=kindergarten_id, code=code, name=name)

    def build_current_user(self, user: User) -> CurrentUser:
        roles = self._repo.list_user_roles(user.kindergarten_id, user.id)
        kindergarten = self._repo.get_kindergarten_by_id(user.kindergarten_id)
        if kindergarten is None:
            msg = "用户所属园所不存在"
            raise RuntimeError(msg)
        return CurrentUser(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            kindergarten=KindergartenSnapshot(
                id=kindergarten.id,
                name=kindergarten.name,
                timezone=kindergarten.timezone,
            ),
            role_codes=roles,
            capabilities=[],
        )

    def record_login_rate_limited(self, *, username: str, source_ip: str | None = None) -> None:
        """记录因登录限流被拒绝的登录失败审计。"""
        kg = self._get_kindergarten()
        if kg is None:
            return
        self._record_identity(
            kindergarten_id=kg.id,
            event_type=audit_events.IDENTITY_LOGIN,
            actor_user_id=None,
            resource_id="unknown",
            action="login",
            result=audit_events.RESULT_FAILURE,
            source_ip=source_ip,
        )
        self._session.commit()

    def authenticate(
        self, *, username: str, password: str, source_ip: str | None = None
    ) -> tuple[User, list[str]] | None:
        kg = self._get_kindergarten()
        if kg is None:
            return None

        account_key = normalize_username(username)
        user = self._repo.get_user_by_username(kg.id, account_key)
        if user is None:
            # 对非用户名形态的输入尝试按手机号查找；任何异常统一视为登录失败，
            # 避免泄露账号是否存在。
            try:
                phone = normalize_phone(username)
            except ValueError:
                phone = None
            if phone is not None:
                user = self._repo.get_user_by_phone(kg.id, phone)

        if user is None or not verify_password(password, user.password_hash):
            self._record_identity(
                kindergarten_id=kg.id,
                event_type=audit_events.IDENTITY_LOGIN,
                actor_user_id=None,
                resource_id="unknown",
                action="login",
                result=audit_events.RESULT_FAILURE,
                source_ip=source_ip,
            )
            self._session.commit()
            return None

        if not user.is_active:
            self._record_identity(
                kindergarten_id=kg.id,
                event_type=audit_events.IDENTITY_LOGIN,
                actor_user_id=None,
                resource_id=user.id,
                action="login",
                result=audit_events.RESULT_FAILURE,
                source_ip=source_ip,
            )
            self._session.commit()
            return None

        roles = self._repo.list_user_roles(kg.id, user.id)
        self._record_identity(
            kindergarten_id=kg.id,
            event_type=audit_events.IDENTITY_LOGIN,
            actor_user_id=user.id,
            resource_id=user.id,
            action="login",
            result=audit_events.RESULT_SUCCESS,
            source_ip=source_ip,
        )
        return user, roles

    def login(
        self, *, username: str, password: str, source_ip: str | None = None
    ) -> LoginResult | None:
        result = self.authenticate(username=username, password=password, source_ip=source_ip)
        if result is None:
            return None
        user, roles = result

        family_id = str(uuid4())
        access_token = create_access_token(
            user_id=user.id,
            kindergarten_id=user.kindergarten_id,
            roles=roles,
            family_id=family_id,
            signing_key=settings.jwt_signing_key,
            expire_minutes=settings.jwt_expire_minutes,
        )
        refresh_value = generate_refresh_value(kindergarten_id=user.kindergarten_id)
        refresh_hash = hash_refresh_value(refresh_value)
        family_expires_at = datetime.now(UTC) + timedelta(days=7)
        self._repo.create_refresh_token(
            kindergarten_id=user.kindergarten_id,
            user_id=user.id,
            family_id=family_id,
            token_hash=refresh_hash,
            expires_at=family_expires_at,
            family_expires_at=family_expires_at,
        )
        csrf_token = generate_csrf_token(settings.csrf_signing_key)
        current_user = self.build_current_user(user)
        self._session.commit()
        return LoginResult(
            user=user,
            roles=roles,
            kindergarten_id=user.kindergarten_id,
            family_id=family_id,
            access_token=access_token,
            refresh_value=refresh_value,
            csrf_token=csrf_token,
            current_user=current_user,
        )

    def refresh(self, *, refresh_cookie: str) -> RefreshResult | None:
        kindergarten_id = parse_refresh_kindergarten_id(refresh_cookie)
        if kindergarten_id is None:
            return None
        token_hash = hash_refresh_value(refresh_cookie)
        token_row = self._repo.find_refresh_token_by_hash_for_update(kindergarten_id, token_hash)
        if token_row is None:
            return None

        now = datetime.now(UTC)
        if (
            token_row.revoked_at is not None
            or token_row.family_revoked_at is not None
            or token_row.expires_at < now
            or token_row.family_expires_at < now
        ):
            self._record_identity(
                kindergarten_id=token_row.kindergarten_id,
                event_type=audit_events.IDENTITY_TOKEN_REPLAY,
                actor_user_id=None,
                resource_id=token_row.user_id,
                action="refresh",
                result=audit_events.RESULT_FAILURE,
            )
            self._repo.revoke_refresh_family(token_row.kindergarten_id, token_row.family_id)
            self._session.commit()
            return None

        user = self._repo.get_user_by_id(token_row.kindergarten_id, token_row.user_id)
        if user is None or not user.is_active:
            self._session.commit()
            return None

        # 正常轮换：只撤销当前 token，保留 family；Access Token 携带同一 family_id。
        self._repo.revoke_refresh_token(token_row.kindergarten_id, token_hash)
        roles = self._repo.list_user_roles(token_row.kindergarten_id, token_row.user_id)
        access_token = create_access_token(
            user_id=token_row.user_id,
            kindergarten_id=token_row.kindergarten_id,
            roles=roles,
            family_id=token_row.family_id,
            signing_key=settings.jwt_signing_key,
            expire_minutes=settings.jwt_expire_minutes,
        )
        refresh_value = generate_refresh_value(kindergarten_id=token_row.kindergarten_id)
        new_hash = hash_refresh_value(refresh_value)
        expires_at = min(token_row.family_expires_at, now + timedelta(days=7))
        self._repo.create_refresh_token(
            kindergarten_id=token_row.kindergarten_id,
            user_id=token_row.user_id,
            family_id=token_row.family_id,
            token_hash=new_hash,
            expires_at=expires_at,
            family_expires_at=token_row.family_expires_at,
        )
        csrf_token = generate_csrf_token(settings.csrf_signing_key)
        self._record_identity(
            kindergarten_id=token_row.kindergarten_id,
            event_type=audit_events.IDENTITY_REFRESH,
            actor_user_id=token_row.user_id,
            resource_id=token_row.user_id,
            action="refresh",
            result=audit_events.RESULT_SUCCESS,
        )
        current_user = self.build_current_user(user)
        self._session.commit()
        return RefreshResult(
            user_id=token_row.user_id,
            kindergarten_id=token_row.kindergarten_id,
            family_id=token_row.family_id,
            roles=roles,
            access_token=access_token,
            refresh_value=refresh_value,
            csrf_token=csrf_token,
            current_user=current_user,
        )

    def is_token_family_active(self, kindergarten_id: str, family_id: str) -> bool:
        """Access Token 携带的 family 是否仍活跃。"""
        return self._repo.is_family_active(kindergarten_id, family_id)

    def logout(self, *, refresh_cookie: str | None, source_ip: str | None = None) -> None:
        if not refresh_cookie:
            return
        kindergarten_id = parse_refresh_kindergarten_id(refresh_cookie)
        if kindergarten_id is None:
            return
        token_row = self._repo.find_refresh_token_by_hash(
            kindergarten_id, hash_refresh_value(refresh_cookie)
        )
        if token_row is not None:
            self._repo.revoke_refresh_family(token_row.kindergarten_id, token_row.family_id)
            self._record_identity(
                kindergarten_id=token_row.kindergarten_id,
                event_type=audit_events.IDENTITY_LOGOUT,
                actor_user_id=token_row.user_id,
                resource_id=token_row.user_id,
                action="logout",
                result=audit_events.RESULT_SUCCESS,
                source_ip=source_ip,
            )
            self._session.commit()

    def change_password(
        self, *, kindergarten_id: str, user_id: str, old_password: str, new_password: str
    ) -> bool:
        user = self._repo.get_user_by_id(kindergarten_id, user_id)
        if user is None or not verify_password(old_password, user.password_hash):
            return False
        validate_password(new_password)
        user.password_hash = hash_password(new_password)
        self._repo.revoke_user_tokens(kindergarten_id, user.id)
        self._record_identity(
            kindergarten_id=kindergarten_id,
            event_type=audit_events.IDENTITY_CHANGE_PASSWORD,
            actor_user_id=user.id,
            resource_id=user.id,
            action="change_password",
            result=audit_events.RESULT_SUCCESS,
        )
        self._session.commit()
        return True

    def _build_user_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            phone_e164=user.phone,
            role_codes=self._repo.list_user_roles(user.kindergarten_id, user.id),
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def create_user(
        self, *, kindergarten_id: str, creator: CurrentUser, request: UserCreateRequest
    ) -> UserResponse:
        self.ensure_roles(kindergarten_id)

        username = normalize_username(request.username)
        phone = normalize_phone(request.phone_e164) if request.phone_e164 else None
        validate_password(request.password)

        user = self._repo.create_user(
            kindergarten_id=kindergarten_id,
            username=username,
            phone=phone,
            display_name=request.display_name,
            password_hash=hash_password(request.password),
            created_by=creator.id,
        )
        for role_code in request.role_codes:
            role = self._repo.get_role_by_code(kindergarten_id, role_code)
            if role is not None:
                self._repo.assign_role(
                    kindergarten_id=kindergarten_id, user_id=user.id, role_id=role.id
                )
        response = self._build_user_response(user)
        self._record_identity(
            kindergarten_id=kindergarten_id,
            event_type=audit_events.IDENTITY_CREATE_USER,
            actor_user_id=creator.id,
            resource_id=user.id,
            action="create_user",
            result=audit_events.RESULT_SUCCESS,
        )
        self._session.commit()
        return response

    def list_users(
        self, kindergarten_id: str, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[UserResponse], int]:
        users = self._repo.list_users(kindergarten_id)
        total = len(users)
        start = (page - 1) * page_size
        end = start + page_size
        page_users = sorted(users, key=lambda u: u.username)[start:end]
        return [self._build_user_response(user) for user in page_users], total

    def get_user(self, kindergarten_id: str, user_id: str) -> UserResponse | None:
        user = self._repo.get_user_by_id(kindergarten_id, user_id)
        if user is None:
            return None
        return self._build_user_response(user)

    def update_user(
        self, *, kindergarten_id: str, admin_user_id: str, user_id: str, patch: UserPatch
    ) -> UserResponse | None:
        user = self._repo.get_user_by_id(kindergarten_id, user_id)
        if user is None:
            return None
        if patch.username is not None:
            user.username = normalize_username(patch.username)
        if patch.display_name is not None:
            user.display_name = patch.display_name
        if patch.phone_e164 is not None:
            user.phone = normalize_phone(patch.phone_e164)
        elif patch.phone_e164_is_set:
            user.phone = None
        user.updated_by = admin_user_id
        self._record_identity(
            kindergarten_id=kindergarten_id,
            event_type=audit_events.IDENTITY_UPDATE_USER,
            actor_user_id=admin_user_id,
            resource_id=user.id,
            action="update_user",
            result=audit_events.RESULT_SUCCESS,
        )
        self._session.commit()
        return self._build_user_response(user)

    def set_user_roles(
        self, *, kindergarten_id: str, admin_user_id: str, user_id: str, role_codes: Sequence[str]
    ) -> UserResponse | None:
        user = self._repo.get_user_by_id(kindergarten_id, user_id)
        if user is None:
            return None
        self.ensure_roles(kindergarten_id)
        current_roles = set(self._repo.list_user_roles(kindergarten_id, user_id))
        new_roles = set(role_codes)
        if "admin" in current_roles and "admin" not in new_roles:
            if self._repo.get_active_admin_count(kindergarten_id) <= 1 and user.is_active:
                raise LastAdminError()
        for role_code in new_roles - current_roles:
            role = self._repo.get_role_by_code(kindergarten_id, role_code)
            if role is not None:
                self._repo.assign_role(
                    kindergarten_id=kindergarten_id, user_id=user.id, role_id=role.id
                )
        for role_code in current_roles - new_roles:
            role = self._repo.get_role_by_code(kindergarten_id, role_code)
            if role is not None:
                self._repo.remove_role(
                    kindergarten_id=kindergarten_id, user_id=user.id, role_id=role.id
                )
        self._record_identity(
            kindergarten_id=kindergarten_id,
            event_type=audit_events.IDENTITY_SET_ROLES,
            actor_user_id=admin_user_id,
            resource_id=user.id,
            action="set_user_roles",
            result=audit_events.RESULT_SUCCESS,
        )
        self._session.commit()
        return self._build_user_response(user)

    def activate_user(
        self, *, kindergarten_id: str, admin_user_id: str, user_id: str
    ) -> UserResponse | None:
        user = self._repo.get_user_by_id(kindergarten_id, user_id)
        if user is None:
            return None
        user.is_active = True
        self._record_identity(
            kindergarten_id=kindergarten_id,
            event_type=audit_events.IDENTITY_ACTIVATE_USER,
            actor_user_id=admin_user_id,
            resource_id=user.id,
            action="activate_user",
            result=audit_events.RESULT_SUCCESS,
        )
        self._session.commit()
        return self._build_user_response(user)

    def reset_password(
        self, *, kindergarten_id: str, admin_user_id: str, target_user_id: str, new_password: str
    ) -> bool:
        user = self._repo.get_user_by_id(kindergarten_id, target_user_id)
        if user is None:
            return False
        validate_password(new_password)
        user.password_hash = hash_password(new_password)
        self._repo.revoke_user_tokens(kindergarten_id, user.id)
        self._record_identity(
            kindergarten_id=kindergarten_id,
            event_type=audit_events.IDENTITY_RESET_PASSWORD,
            actor_user_id=admin_user_id,
            resource_id=user.id,
            action="reset_password",
            result=audit_events.RESULT_SUCCESS,
        )
        self._session.commit()
        return True

    def deactivate_user(
        self, *, kindergarten_id: str, admin_user_id: str, user_id: str
    ) -> UserResponse:
        target = self._repo.get_user_by_id(kindergarten_id, user_id)
        if target is None:
            raise UserNotFoundError()
        target_roles = self._repo.list_user_roles(kindergarten_id, user_id)
        if (
            target.is_active
            and "admin" in target_roles
            and self._repo.get_active_admin_count(kindergarten_id) <= 1
        ):
            raise LastAdminError()
        self._repo.deactivate_user(kindergarten_id, user_id)
        self._repo.revoke_user_tokens(kindergarten_id, user_id)
        response = self._build_user_response(target)
        self._record_identity(
            kindergarten_id=kindergarten_id,
            event_type=audit_events.IDENTITY_DEACTIVATE_USER,
            actor_user_id=admin_user_id,
            resource_id=user_id,
            action="deactivate_user",
            result=audit_events.RESULT_SUCCESS,
        )
        self._session.commit()
        return response

    def init_admin(self, *, kg_name: str, admin_username: str, password: str) -> dict[str, Any]:
        kg = self._repo.create_kindergarten(name=kg_name or "默认幼儿园")
        self.ensure_roles(kg.id)
        admin_role = self._repo.get_role_by_code(kg.id, "admin")
        if admin_role is None:
            raise RuntimeError("管理员角色初始化失败")
        user = self._repo.create_user(
            kindergarten_id=kg.id,
            username=normalize_username(admin_username),
            phone=None,
            display_name="系统管理员",
            password_hash=hash_password(password),
        )
        self._repo.assign_role(kindergarten_id=kg.id, user_id=user.id, role_id=admin_role.id)
        self._record_identity(
            kindergarten_id=kg.id,
            event_type=audit_events.IDENTITY_INIT_ADMIN,
            actor_user_id=user.id,
            resource_id=user.id,
            action="init_admin",
            result=audit_events.RESULT_SUCCESS,
        )
        self._session.commit()
        return {"user_id": user.id, "kindergarten_id": kg.id}

    def get_user_by_id(self, kindergarten_id: str, user_id: str) -> User | None:
        return self._repo.get_user_by_id(kindergarten_id, user_id)
