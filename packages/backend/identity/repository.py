"""身份 Repository。"""

from datetime import UTC, datetime
from uuid import uuid7

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from packages.backend.identity.models import (
    Kindergarten,
    RefreshToken,
    Role,
    User,
    UserRole,
)


def _uuid() -> str:
    # 冻结 Schema §3.2 要求主键使用 UUIDv7。
    return str(uuid7())


class IdentityRepository:
    """同园身份 Repository；所有操作必须显式传入 kindergarten_id。"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_kindergarten(self, *, name: str, timezone: str = "Asia/Shanghai") -> Kindergarten:
        kg = Kindergarten(id=_uuid(), name=name, timezone=timezone)
        self._session.add(kg)
        self._session.flush()
        return kg

    def get_kindergarten_by_id(self, kindergarten_id: str) -> Kindergarten | None:
        return self._session.get(Kindergarten, kindergarten_id)

    def create_role(self, *, code: str, name: str) -> Role:
        role = Role(id=_uuid(), code=code, name=name)
        self._session.add(role)
        self._session.flush()
        return role

    def get_role_by_code(self, code: str) -> Role | None:
        stmt = select(Role).where(Role.code == code)
        return self._session.execute(stmt).scalar_one_or_none()

    def create_user(
        self,
        *,
        kindergarten_id: str,
        username: str,
        username_normalized: str,
        phone_e164: str | None,
        display_name: str,
        password_hash: str,
        created_by: str | None = None,
    ) -> User:
        now = datetime.now(UTC)
        user = User(
            id=_uuid(),
            kindergarten_id=kindergarten_id,
            username=username,
            username_normalized=username_normalized,
            phone_e164=phone_e164,
            display_name=display_name,
            password_hash=password_hash,
            is_active=True,
            password_changed_at=now,
            created_by=created_by,
            updated_by=created_by,
        )
        self._session.add(user)
        self._session.flush()
        return user

    def get_user_by_username(self, kindergarten_id: str, username: str) -> User | None:
        # 调用方（service 层）已通过 normalize_username 完成 NFKC+trim+lower；
        # 这里直接使用传入值查询，避免在 repository 层重复且不一致地规范化。
        stmt = select(User).where(
            User.kindergarten_id == kindergarten_id,
            User.username_normalized == username,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_user_by_phone(self, kindergarten_id: str, phone: str) -> User | None:
        stmt = select(User).where(
            User.kindergarten_id == kindergarten_id,
            User.phone_e164 == phone,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_user_by_id(self, kindergarten_id: str, user_id: str) -> User | None:
        stmt = select(User).where(User.kindergarten_id == kindergarten_id, User.id == user_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def update_user(
        self,
        *,
        user: User,
        username: str | None = None,
        username_normalized: str | None = None,
        display_name: str | None = None,
        phone_e164: str | None = None,
        phone_e164_set: bool = False,
        password_hash: str | None = None,
        is_active: bool | None = None,
        updated_by: str | None = None,
    ) -> User:
        if username is not None:
            user.username = username
        if username_normalized is not None:
            user.username_normalized = username_normalized
        if display_name is not None:
            user.display_name = display_name
        if phone_e164_set:
            user.phone_e164 = phone_e164
        if password_hash is not None:
            user.password_hash = password_hash
            user.password_changed_at = datetime.now(UTC)
        if is_active is not None:
            user.is_active = is_active
        if updated_by is not None:
            user.updated_by = updated_by
        self._session.flush()
        return user

    def record_login(self, user: User) -> None:
        user.last_login_at = datetime.now(UTC)
        self._session.flush()

    def assign_role(
        self,
        *,
        kindergarten_id: str,
        user_id: str,
        role_id: str,
        assigned_by: str,
    ) -> UserRole:
        user_role = UserRole(
            kindergarten_id=kindergarten_id,
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
        )
        self._session.add(user_role)
        self._session.flush()
        return user_role

    def remove_role(self, *, kindergarten_id: str, user_id: str, role_id: str) -> int:
        stmt = delete(UserRole).where(
            UserRole.kindergarten_id == kindergarten_id,
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        result = self._session.execute(stmt)
        self._session.flush()
        return int(getattr(result, "rowcount", 0) or 0)

    def list_users(self, kindergarten_id: str) -> list[User]:
        stmt = select(User).where(User.kindergarten_id == kindergarten_id)
        return list(self._session.execute(stmt).scalars().all())

    def list_user_roles(self, kindergarten_id: str, user_id: str) -> list[str]:
        stmt = (
            select(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.kindergarten_id == kindergarten_id,
                UserRole.user_id == user_id,
            )
        )
        return list(self._session.execute(stmt).scalars().all())

    def get_active_admin_count(self, kindergarten_id: str) -> int:
        """返回具有 admin 角色的有效用户数量。"""
        stmt = (
            select(func.count(User.id))
            .join(UserRole, User.id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .where(
                User.kindergarten_id == kindergarten_id,
                User.is_active.is_(True),
                Role.code == "admin",
                UserRole.kindergarten_id == kindergarten_id,
            )
        )
        return int(self._session.execute(stmt).scalar() or 0)

    def get_active_admins_for_update(self, kindergarten_id: str) -> list[User]:
        """带行锁的有效管理员列表，用于最后管理员并发保护。"""
        stmt = (
            select(User)
            .join(UserRole, User.id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .where(
                User.kindergarten_id == kindergarten_id,
                User.is_active.is_(True),
                Role.code == "admin",
                UserRole.kindergarten_id == kindergarten_id,
            )
            .with_for_update()
        )
        return list(self._session.execute(stmt).scalars().all())

    def deactivate_user(self, kindergarten_id: str, user_id: str) -> User:
        user = self.get_user_by_id(kindergarten_id, user_id)
        if user is None:
            msg = "用户不存在"
            raise ValueError(msg)
        user.is_active = False
        self._session.flush()
        return user

    def create_refresh_token(
        self,
        *,
        kindergarten_id: str,
        user_id: str,
        token_family_id: str,
        token_hash: str,
        expires_at: datetime,
        client_label: str | None = None,
    ) -> RefreshToken:
        token = RefreshToken(
            id=_uuid(),
            kindergarten_id=kindergarten_id,
            user_id=user_id,
            token_family_id=token_family_id,
            token_hash=token_hash,
            expires_at=expires_at,
            client_label=client_label,
        )
        self._session.add(token)
        self._session.flush()
        return token

    def find_refresh_token_by_hash(
        self, kindergarten_id: str, token_hash: str
    ) -> RefreshToken | None:
        """在指定园所内通过 token_hash 定位 Refresh Token。"""
        stmt = select(RefreshToken).where(
            RefreshToken.kindergarten_id == kindergarten_id,
            RefreshToken.token_hash == token_hash,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def find_refresh_token_by_hash_for_update(
        self, kindergarten_id: str, token_hash: str
    ) -> RefreshToken | None:
        """带行锁的 find_refresh_token_by_hash；隔离语义同上。"""
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.kindergarten_id == kindergarten_id,
                RefreshToken.token_hash == token_hash,
            )
            .with_for_update()
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def is_family_active(self, kindergarten_id: str, token_family_id: str) -> bool:
        """family 内存在未撤销的 token 时视为活跃。"""
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.kindergarten_id == kindergarten_id,
                RefreshToken.token_family_id == token_family_id,
                RefreshToken.revoked_at.is_(None),
            )
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none() is not None

    def revoke_refresh_token(
        self,
        kindergarten_id: str,
        token_hash: str,
        *,
        revoke_reason: str | None = None,
        replaced_by_id: str | None = None,
    ) -> int:
        """撤销单个 Refresh Token（用于正常轮换）。

        Codex 第十九轮 P0-4：轮换时同一 UPDATE 必须同时写 ``revoked_at`` 与
        ``replaced_by_id``，满足 CHECK ``ck_refresh_tokens_replaced_implies_revoked``
        （``replaced_by_id IS NULL OR revoked_at IS NOT NULL``）。分两次 UPDATE 会
        违反该约束，因此 ``replaced_by_id`` 必须随撤销同语句写入。
        """
        extra_values: dict[str, str] = (
            {} if replaced_by_id is None else {"replaced_by_id": replaced_by_id}
        )
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.kindergarten_id == kindergarten_id,
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
            )
            .values(
                revoked_at=datetime.now(UTC),
                revoke_reason=revoke_reason,
                **extra_values,
            )
        )
        result = self._session.execute(stmt)
        self._session.flush()
        return int(getattr(result, "rowcount", 0) or 0)

    def revoke_refresh_family(
        self,
        kindergarten_id: str,
        token_family_id: str,
        *,
        revoke_reason: str | None = None,
    ) -> int:
        """撤销整个 Refresh family（用于退出、改密、重置、停用、重放）。"""
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.kindergarten_id == kindergarten_id,
                RefreshToken.token_family_id == token_family_id,
            )
            .values(
                revoked_at=datetime.now(UTC),
                revoke_reason=revoke_reason,
            )
        )
        result = self._session.execute(stmt)
        self._session.flush()
        return int(getattr(result, "rowcount", 0) or 0)

    def revoke_user_tokens(
        self,
        kindergarten_id: str,
        user_id: str,
        *,
        revoke_reason: str | None = None,
    ) -> int:
        """撤销用户的全部 Refresh Token 及其 family。"""
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.kindergarten_id == kindergarten_id,
                RefreshToken.user_id == user_id,
            )
            .values(
                revoked_at=datetime.now(UTC),
                revoke_reason=revoke_reason,
            )
        )
        result = self._session.execute(stmt)
        self._session.flush()
        return int(getattr(result, "rowcount", 0) or 0)
