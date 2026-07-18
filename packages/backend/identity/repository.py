"""身份 Repository。"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from packages.backend.identity.models import Kindergarten, RefreshToken, Role, User, UserRole


class IdentityRepository:
    """同园身份 Repository；所有操作必须显式传入 kindergarten_id。"""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def _db(self) -> Session:
        return self._session

    def create_kindergarten(self, *, name: str, timezone: str = "Asia/Shanghai") -> Kindergarten:
        kg = Kindergarten(id=str(uuid4()), name=name, timezone=timezone)
        self._db.add(kg)
        self._db.flush()
        return kg

    def get_kindergarten_by_id(self, kindergarten_id: str) -> Kindergarten | None:
        return self._db.get(Kindergarten, kindergarten_id)

    def create_role(self, *, kindergarten_id: str, code: str, name: str) -> Role:
        role = Role(id=str(uuid4()), kindergarten_id=kindergarten_id, code=code, name=name)
        self._db.add(role)
        self._db.flush()
        return role

    def get_role_by_code(self, kindergarten_id: str, code: str) -> Role | None:
        stmt = select(Role).where(Role.kindergarten_id == kindergarten_id, Role.code == code)
        return self._db.execute(stmt).scalar_one_or_none()

    def create_user(
        self,
        *,
        kindergarten_id: str,
        username: str,
        phone: str | None,
        display_name: str,
        password_hash: str,
        created_by: str | None = None,
    ) -> User:
        user = User(
            id=str(uuid4()),
            kindergarten_id=kindergarten_id,
            username=username,
            phone=phone,
            display_name=display_name,
            password_hash=password_hash,
            is_active=True,
            created_by=created_by,
        )
        self._db.add(user)
        self._db.flush()
        return user

    def get_user_by_username(self, kindergarten_id: str, username: str) -> User | None:
        stmt = select(User).where(
            User.kindergarten_id == kindergarten_id, User.username == username
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def get_user_by_phone(self, kindergarten_id: str, phone: str) -> User | None:
        stmt = select(User).where(User.kindergarten_id == kindergarten_id, User.phone == phone)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_user_by_id(self, kindergarten_id: str, user_id: str) -> User | None:
        stmt = select(User).where(User.kindergarten_id == kindergarten_id, User.id == user_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def assign_role(self, *, kindergarten_id: str, user_id: str, role_id: str) -> UserRole:
        user_role = UserRole(
            id=str(uuid4()), kindergarten_id=kindergarten_id, user_id=user_id, role_id=role_id
        )
        self._db.add(user_role)
        self._db.flush()
        return user_role

    def remove_role(self, *, kindergarten_id: str, user_id: str, role_id: str) -> int:
        stmt = delete(UserRole).where(
            UserRole.kindergarten_id == kindergarten_id,
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        result = self._db.execute(stmt)
        self._db.flush()
        return int(getattr(result, "rowcount", 0) or 0)

    def list_users(self, kindergarten_id: str) -> list[User]:
        stmt = select(User).where(User.kindergarten_id == kindergarten_id)
        return list(self._db.execute(stmt).scalars().all())

    def list_user_roles(self, kindergarten_id: str, user_id: str) -> list[str]:
        stmt = (
            select(Role.code)
            .join(UserRole)
            .where(
                UserRole.kindergarten_id == kindergarten_id,
                UserRole.user_id == user_id,
            )
        )
        return list(self._db.execute(stmt).scalars().all())

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
                Role.kindergarten_id == kindergarten_id,
                UserRole.kindergarten_id == kindergarten_id,
            )
        )
        return int(self._db.execute(stmt).scalar() or 0)

    def deactivate_user(self, kindergarten_id: str, user_id: str) -> bool:
        user = self.get_user_by_id(kindergarten_id, user_id)
        if user is None:
            msg = "用户不存在"
            raise ValueError(msg)
        user.is_active = False
        self._db.flush()
        return True

    def create_refresh_token(
        self,
        *,
        kindergarten_id: str,
        user_id: str,
        family_id: str,
        token_hash: str,
        expires_at: datetime,
        family_expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            id=str(uuid4()),
            kindergarten_id=kindergarten_id,
            user_id=user_id,
            family_id=family_id,
            token_hash=token_hash,
            expires_at=expires_at,
            family_expires_at=family_expires_at,
        )
        self._db.add(token)
        self._db.flush()
        return token

    def find_refresh_token_by_hash(
        self, kindergarten_id: str, token_hash: str
    ) -> RefreshToken | None:
        """在指定园所内通过 token_hash 定位 Refresh Token。

        Refresh 明文已编码园所 ID，调用方解析后必须显式传入 kindergarten_id，
        使 Repository 查询符合园所隔离要求。所有下游撤销、创建和用户信息读取
        继续使用 token.kindergarten_id 隔离。
        """
        stmt = select(RefreshToken).where(
            RefreshToken.kindergarten_id == kindergarten_id,
            RefreshToken.token_hash == token_hash,
        )
        return self._db.execute(stmt).scalar_one_or_none()

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
        return self._db.execute(stmt).scalar_one_or_none()

    def revoke_refresh_family(self, kindergarten_id: str, family_id: str) -> int:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.kindergarten_id == kindergarten_id,
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        result = self._db.execute(stmt)
        self._db.flush()
        return int(getattr(result, "rowcount", 0) or 0)

    def revoke_user_tokens(self, kindergarten_id: str, user_id: str) -> int:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.kindergarten_id == kindergarten_id,
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        result = self._db.execute(stmt)
        self._db.flush()
        return int(getattr(result, "rowcount", 0) or 0)
