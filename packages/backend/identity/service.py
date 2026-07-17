"""身份用例：实时授权、会话轮换、撤销与最后管理员保护。"""

import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID, uuid7

import psycopg

from packages.backend.audit.repository import AuditRepository
from packages.backend.identity.identifiers import normalize_phone, normalize_username
from packages.backend.identity.passwords import hash_password, password_violations, verify_password
from packages.backend.identity.repository import IdentityRepository, UserRecord
from packages.backend.identity.tokens import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from packages.contracts.audit import IdentityAuditEventCode


class IdentityError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


@dataclass(frozen=True, slots=True)
class SessionUser:
    user: UserRecord
    role_codes: list[str]

    @property
    def capabilities(self) -> list[str]:
        capabilities = {"plans:view"}
        if "admin" in self.role_codes:
            capabilities.add("users:manage")
        return sorted(capabilities)


@dataclass(frozen=True, slots=True)
class AuthResult:
    session: SessionUser
    access_token: str
    refresh_token: str


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _session_version(password_hash: str) -> str:
    return sha256(password_hash.encode()).hexdigest()[:16]


_DUMMY_PASSWORD_HASH = hash_password("不存在账号使用的固定占位密码 2026")


class IdentityService:
    def __init__(self, *, database_url: str, jwt_signing_key: str) -> None:
        self.database_url = database_url
        self.jwt_signing_key = jwt_signing_key

    @classmethod
    def from_environment(cls) -> IdentityService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        jwt_key = os.environ.get("CHILD_MANAGER_JWT_SIGNING_KEY")
        if not database_url or not jwt_key:
            raise IdentityError(503, "configuration.unavailable", "服务端安全配置不可用。")
        return cls(database_url=database_url, jwt_signing_key=jwt_key)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _kindergarten_id(connection: psycopg.Connection[tuple[object, ...]]) -> UUID:
        rows = connection.execute(
            "SELECT id FROM kindergartens WHERE is_active ORDER BY created_at LIMIT 2"
        ).fetchall()
        if len(rows) != 1:
            raise IdentityError(503, "configuration.unavailable", "园所身份配置不可用。")
        return rows[0][0]  # type: ignore[return-value]

    @staticmethod
    def normalize_login_key(value: str) -> str:
        compact = value.strip()
        if compact.startswith("+") or compact.replace(" ", "").replace("-", "").isdigit():
            try:
                phone = normalize_phone(value)
            except ValueError:
                phone = None
            if phone is not None:
                return phone
        return normalize_username(value)

    @classmethod
    def safe_login_key(cls, value: str) -> str:
        try:
            return cls.normalize_login_key(value)
        except ValueError:
            return ""

    @staticmethod
    def _assert_password(password: str) -> None:
        violations = password_violations(password)
        if violations:
            message = (
                "密码长度必须为 15–128 个字符。"
                if "length" in violations
                else "该密码过于常见，请更换。"
            )
            raise IdentityError(422, "identity.weak_password", message)

    def login(
        self, *, login: str, password: str, request_id: UUID | None, source: str
    ) -> AuthResult:
        normalized = self.safe_login_key(login)
        now = datetime.now(UTC)
        result: AuthResult | None = None
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._kindergarten_id(connection)
            repository = IdentityRepository(connection, kindergarten_id)
            user = repository.find_user_by_login(normalized)
            password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
            valid = verify_password(password, password_hash)
            if user is None or not user.is_active or not valid:
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.LOGIN_FAILED,
                    actor_user_id=user.id if user is not None else None,
                    actor_role_codes=repository.roles_for_user(user.id) if user is not None else [],
                    resource_type="user",
                    resource_id=user.id if user is not None else None,
                    request_id=request_id,
                    outcome="failure",
                    metadata={"source": source},
                )
            else:
                roles = repository.roles_for_user(user.id)
                raw_refresh = generate_refresh_token()
                family_id = uuid7()
                repository.create_refresh(
                    user_id=user.id,
                    family_id=family_id,
                    token_hash=hash_refresh_token(raw_refresh),
                    issued_at=now,
                    expires_at=now + timedelta(days=7),
                )
                connection.execute(
                    """UPDATE users SET last_login_at=%s, updated_at=now()
                    WHERE kindergarten_id=%s AND id=%s""",
                    (now, kindergarten_id, user.id),
                )
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.LOGIN_SUCCEEDED,
                    actor_user_id=user.id,
                    actor_role_codes=roles,
                    resource_type="user",
                    resource_id=user.id,
                    request_id=request_id,
                    outcome="success",
                    metadata={"source": source},
                )
                access = create_access_token(
                    user_id=str(user.id),
                    kindergarten_id=str(kindergarten_id),
                    token_family_id=str(family_id),
                    signing_key=self.jwt_signing_key,
                    now=now,
                    session_version=_session_version(user.password_hash),
                )
                result = AuthResult(SessionUser(user, roles), access, raw_refresh)
        if result is None:
            raise IdentityError(401, "auth.login_failed", "用户名、手机号或密码错误。")
        return result

    def record_login_rate_limited(
        self, *, login: str, source: str, request_id: UUID | None
    ) -> None:
        normalized = self.safe_login_key(login)
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._kindergarten_id(connection)
            repository = IdentityRepository(connection, kindergarten_id)
            user = repository.find_user_by_login(normalized) if normalized else None
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.LOGIN_RATE_LIMITED,
                actor_user_id=user.id if user is not None else None,
                actor_role_codes=repository.roles_for_user(user.id) if user is not None else [],
                resource_type="user",
                resource_id=user.id if user is not None else None,
                request_id=request_id,
                outcome="failure",
                metadata={"source": source},
            )

    def authenticate_access(self, token: str) -> SessionUser:
        try:
            claims = decode_access_token(
                token, signing_key=self.jwt_signing_key, now=datetime.now(UTC)
            )
            user_id = UUID(str(claims["sub"]))
            kindergarten_id = UUID(str(claims["kid"]))
            family_id = UUID(str(claims["fid"]))
        except ValueError, KeyError:
            raise IdentityError(
                401, "auth.unauthenticated", "登录状态已失效，请重新登录。"
            ) from None
        with self._connect() as connection:
            repository = IdentityRepository(connection, kindergarten_id)
            user = repository.get_user(user_id)
            if (
                user is None
                or not user.is_active
                or claims.get("sv") != _session_version(user.password_hash)
                or not repository.has_active_refresh_family(user_id, family_id)
            ):
                raise IdentityError(401, "auth.unauthenticated", "登录状态已失效，请重新登录。")
            return SessionUser(user, repository.roles_for_user(user.id))

    def kindergarten_summary(self, kindergarten_id: UUID) -> dict[str, object]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, name, timezone FROM kindergartens WHERE id=%s AND is_active",
                (kindergarten_id,),
            ).fetchone()
            if row is None:
                raise IdentityError(401, "auth.unauthenticated", "登录状态已失效，请重新登录。")
            return {"id": row[0], "name": row[1], "timezone": row[2]}

    def refresh(self, raw_token: str, *, request_id: UUID | None) -> AuthResult:
        now = datetime.now(UTC)
        token_hash = hash_refresh_token(raw_token)
        result: AuthResult | None = None
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._kindergarten_id(connection)
            repository = IdentityRepository(connection, kindergarten_id)
            old = repository.get_refresh(token_hash, lock=True)
            if old is None:
                raise IdentityError(401, "auth.unauthenticated", "刷新会话已失效，请重新登录。")
            if old.revoked_at is not None:
                repository.revoke_family(old.token_family_id, reason="replay")
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.REFRESH_REPLAYED,
                    actor_user_id=old.user_id,
                    actor_role_codes=repository.roles_for_user(old.user_id),
                    resource_type="refresh_family",
                    resource_id=old.token_family_id,
                    request_id=request_id,
                    outcome="failure",
                )
            else:
                user = repository.get_user(old.user_id, lock=True)
                if user is None or not user.is_active or old.expires_at <= now:
                    repository.revoke_family(old.token_family_id, reason="expired_or_inactive")
                else:
                    new_raw = generate_refresh_token()
                    repository.rotate_refresh(old, new_hash=hash_refresh_token(new_raw), now=now)
                    roles = repository.roles_for_user(user.id)
                    AuditRepository(connection, kindergarten_id).append(
                        event_code=IdentityAuditEventCode.TOKEN_REFRESHED,
                        actor_user_id=user.id,
                        actor_role_codes=roles,
                        resource_type="refresh_family",
                        resource_id=old.token_family_id,
                        request_id=request_id,
                        outcome="success",
                    )
                    access = create_access_token(
                        user_id=str(user.id),
                        kindergarten_id=str(kindergarten_id),
                        token_family_id=str(old.token_family_id),
                        signing_key=self.jwt_signing_key,
                        now=now,
                        session_version=_session_version(user.password_hash),
                    )
                    result = AuthResult(SessionUser(user, roles), access, new_raw)
        if result is None:
            raise IdentityError(401, "auth.unauthenticated", "刷新会话已失效，请重新登录。")
        return result

    def logout(self, raw_token: str | None, *, request_id: UUID | None) -> None:
        if not raw_token:
            return
        token_hash = hash_refresh_token(raw_token)
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._kindergarten_id(connection)
            repository = IdentityRepository(connection, kindergarten_id)
            token = repository.get_refresh(token_hash, lock=True)
            if token is None:
                return
            repository.revoke_family(token.token_family_id, reason="logout")
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.LOGGED_OUT,
                actor_user_id=token.user_id,
                actor_role_codes=repository.roles_for_user(token.user_id),
                resource_type="refresh_family",
                resource_id=token.token_family_id,
                request_id=request_id,
                outcome="success",
            )

    def change_password(
        self,
        session: SessionUser,
        *,
        current_password: str,
        new_password: str,
        request_id: UUID | None,
    ) -> None:
        self._assert_password(new_password)
        if not verify_password(current_password, session.user.password_hash):
            raise IdentityError(401, "auth.login_failed", "当前密码错误。")
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            repository.update_password(
                session.user.id, hash_password(new_password), actor_user_id=session.user.id
            )
            repository.revoke_user_sessions(session.user.id, reason="password_changed")
            AuditRepository(connection, session.user.kindergarten_id).append(
                event_code=IdentityAuditEventCode.PASSWORD_CHANGED,
                actor_user_id=session.user.id,
                actor_role_codes=session.role_codes,
                resource_type="user",
                resource_id=session.user.id,
                request_id=request_id,
                outcome="success",
            )

    @staticmethod
    def require_admin(session: SessionUser) -> None:
        if "admin" not in session.role_codes:
            raise IdentityError(403, "auth.forbidden", "没有执行此操作的权限。")

    def create_user(
        self,
        session: SessionUser,
        *,
        username: str,
        phone_e164: str | None,
        display_name: str,
        password: str,
        role_codes: list[str],
        request_id: UUID | None,
    ) -> SessionUser:
        self.require_admin(session)
        self._assert_password(password)
        try:
            normalized_username = normalize_username(username)
            normalized_phone = normalize_phone(phone_e164)
        except ValueError as exc:
            raise IdentityError(422, "identity.invalid_identifier", str(exc)) from None
        try:
            with self._connect() as connection, connection.transaction():
                repository = IdentityRepository(connection, session.user.kindergarten_id)
                user = repository.create_user(
                    username=normalized_username,
                    username_normalized=normalized_username,
                    phone_e164=normalized_phone,
                    display_name=display_name.strip(),
                    password_hash=hash_password(password),
                    role_codes=role_codes,
                    actor_user_id=session.user.id,
                )
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=IdentityAuditEventCode.USER_CREATED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="user",
                    resource_id=user.id,
                    request_id=request_id,
                    outcome="success",
                    metadata={"target_role_codes": sorted(role_codes)},
                )
                return SessionUser(user, repository.roles_for_user(user.id))
        except psycopg.errors.UniqueViolation:
            raise IdentityError(
                409, "identity.identifier_conflict", "用户名或手机号已被使用。"
            ) from None

    def list_users(
        self, session: SessionUser, *, page: int, page_size: int
    ) -> tuple[list[SessionUser], int]:
        self.require_admin(session)
        with self._connect() as connection:
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            users, total = repository.list_users(page=page, page_size=page_size)
            return (
                [SessionUser(user, repository.roles_for_user(user.id)) for user in users],
                total,
            )

    def get_user(self, session: SessionUser, user_id: UUID) -> SessionUser:
        self.require_admin(session)
        with self._connect() as connection:
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            user = repository.get_user(user_id)
            if user is None:
                raise IdentityError(404, "resource.not_found", "账号不存在。")
            return SessionUser(user, repository.roles_for_user(user.id))

    def update_user(
        self,
        session: SessionUser,
        user_id: UUID,
        *,
        username: str | None,
        phone_e164: str | None,
        display_name: str | None,
        request_id: UUID | None,
    ) -> SessionUser:
        self.require_admin(session)
        try:
            normalized_username = normalize_username(username) if username is not None else None
            normalized_phone = normalize_phone(phone_e164)
        except ValueError as exc:
            raise IdentityError(422, "identity.invalid_identifier", str(exc)) from None
        try:
            with self._connect() as connection, connection.transaction():
                repository = IdentityRepository(connection, session.user.kindergarten_id)
                user = repository.update_user(
                    user_id,
                    username=normalized_username,
                    username_normalized=normalized_username,
                    phone_e164=normalized_phone,
                    display_name=display_name.strip() if display_name is not None else None,
                    actor_user_id=session.user.id,
                )
                roles = repository.roles_for_user(user.id)
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=IdentityAuditEventCode.USER_UPDATED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="user",
                    resource_id=user.id,
                    request_id=request_id,
                    outcome="success",
                )
                return SessionUser(user, roles)
        except LookupError:
            raise IdentityError(404, "resource.not_found", "账号不存在。") from None
        except psycopg.errors.UniqueViolation:
            raise IdentityError(
                409, "identity.identifier_conflict", "用户名或手机号已被使用。"
            ) from None

    def set_roles(
        self, session: SessionUser, user_id: UUID, role_codes: list[str], *, request_id: UUID | None
    ) -> SessionUser:
        self.require_admin(session)
        try:
            with self._connect() as connection, connection.transaction():
                repository = IdentityRepository(connection, session.user.kindergarten_id)
                repository.set_roles(user_id, role_codes, actor_user_id=session.user.id)
                user = repository.get_user(user_id)
                assert user is not None
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=IdentityAuditEventCode.USER_ROLES_CHANGED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="user",
                    resource_id=user_id,
                    request_id=request_id,
                    outcome="success",
                    metadata={"target_role_codes": sorted(role_codes)},
                )
                return SessionUser(user, repository.roles_for_user(user_id))
        except LookupError:
            raise IdentityError(404, "resource.not_found", "账号不存在。") from None
        except ValueError as exc:
            raise IdentityError(409, "identity.last_admin_required", str(exc)) from None

    def set_active(
        self, session: SessionUser, user_id: UUID, *, active: bool, request_id: UUID | None
    ) -> SessionUser:
        self.require_admin(session)
        try:
            with self._connect() as connection, connection.transaction():
                repository = IdentityRepository(connection, session.user.kindergarten_id)
                user = repository.set_active(user_id, active=active, actor_user_id=session.user.id)
                if not active:
                    repository.revoke_user_sessions(user_id, reason="user_deactivated")
                event = (
                    IdentityAuditEventCode.USER_ACTIVATED
                    if active
                    else IdentityAuditEventCode.USER_DEACTIVATED
                )
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=event,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="user",
                    resource_id=user_id,
                    request_id=request_id,
                    outcome="success",
                )
                return SessionUser(user, repository.roles_for_user(user_id))
        except LookupError:
            raise IdentityError(404, "resource.not_found", "账号不存在。") from None
        except ValueError as exc:
            raise IdentityError(409, "identity.last_admin_required", str(exc)) from None

    def reset_password(
        self, session: SessionUser, user_id: UUID, password: str, *, request_id: UUID | None
    ) -> None:
        self.require_admin(session)
        self._assert_password(password)
        try:
            with self._connect() as connection, connection.transaction():
                repository = IdentityRepository(connection, session.user.kindergarten_id)
                repository.update_password(
                    user_id, hash_password(password), actor_user_id=session.user.id
                )
                repository.revoke_user_sessions(user_id, reason="password_reset")
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=IdentityAuditEventCode.PASSWORD_RESET,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="user",
                    resource_id=user_id,
                    request_id=request_id,
                    outcome="success",
                )
        except LookupError:
            raise IdentityError(404, "resource.not_found", "账号不存在。") from None
