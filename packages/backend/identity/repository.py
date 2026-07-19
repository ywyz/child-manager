"""所有查询都显式绑定 kindergarten_id 的身份 Repository。"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

import psycopg


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: UUID
    kindergarten_id: UUID
    username: str
    username_normalized: str
    phone_e164: str | None
    display_name: str
    password_hash: str
    is_active: bool
    password_changed_at: datetime
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class RefreshRecord:
    id: UUID
    kindergarten_id: UUID
    user_id: UUID
    token_family_id: UUID
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    replaced_by_id: UUID | None


_USER_COLUMNS = """id, kindergarten_id, username, username_normalized, phone_e164,
display_name, password_hash, is_active, password_changed_at, created_at, updated_at"""


def _user(row: tuple[object, ...] | None) -> UserRecord | None:
    return UserRecord(*row) if row is not None else None  # type: ignore[arg-type]


class IdentityRepository:
    def __init__(
        self, connection: psycopg.Connection[tuple[object, ...]], kindergarten_id: UUID
    ) -> None:
        self.connection = connection
        self.kindergarten_id = kindergarten_id

    def _lock_admin_membership(self) -> None:
        self.connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (str(self.kindergarten_id),),
        )

    # 所有会话写路径保持 user → family → row 的锁序。这样可避免整用户撤销与轮换互相死锁。
    def _lock_refresh_family(self, family_id: UUID) -> None:
        self.connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (f"refresh-family:{self.kindergarten_id}:{family_id}",),
        )

    def lock_user_sessions(self, user_id: UUID) -> None:
        self.connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (f"user-sessions:{self.kindergarten_id}:{user_id}",),
        )

    def active_admin_count(self) -> int:
        row = self.connection.execute(
            """SELECT count(*) FROM users u
            JOIN user_roles ur ON ur.kindergarten_id=u.kindergarten_id AND ur.user_id=u.id
            JOIN roles r ON r.id=ur.role_id
            WHERE u.kindergarten_id=%s AND u.is_active AND r.code='admin'""",
            (self.kindergarten_id,),
        ).fetchone()
        if row is None or not isinstance(row[0], int):
            return 0
        return row[0]

    def can_deactivate(self, user_id: UUID) -> bool:
        self._lock_admin_membership()
        row = self.connection.execute(
            """SELECT u.is_active, EXISTS(
                SELECT 1 FROM user_roles ur JOIN roles r ON r.id=ur.role_id
                WHERE ur.kindergarten_id=u.kindergarten_id AND ur.user_id=u.id AND r.code='admin')
            FROM users u WHERE u.kindergarten_id=%s AND u.id=%s FOR UPDATE""",
            (self.kindergarten_id, user_id),
        ).fetchone()
        if row is None:
            raise LookupError("账号不存在")
        is_active, is_admin = bool(row[0]), bool(row[1])
        return not (is_active and is_admin and self.active_admin_count() <= 1)

    def get_user(self, user_id: UUID, *, lock: bool = False) -> UserRecord | None:
        suffix = " FOR UPDATE" if lock else ""
        row = self.connection.execute(
            f"SELECT {_USER_COLUMNS} FROM users WHERE kindergarten_id=%s AND id=%s{suffix}",
            (self.kindergarten_id, user_id),
        ).fetchone()
        return _user(row)

    def find_user_by_login(self, login: str) -> UserRecord | None:
        row = self.connection.execute(
            f"""SELECT {_USER_COLUMNS} FROM users
            WHERE kindergarten_id=%s AND (username_normalized=%s OR phone_e164=%s)""",
            (self.kindergarten_id, login, login),
        ).fetchone()
        return _user(row)

    def roles_for_user(self, user_id: UUID) -> list[str]:
        return [
            str(row[0])
            for row in self.connection.execute(
                """SELECT r.code FROM user_roles ur JOIN roles r ON r.id=ur.role_id
                WHERE ur.kindergarten_id=%s AND ur.user_id=%s ORDER BY r.code""",
                (self.kindergarten_id, user_id),
            ).fetchall()
        ]

    def create_user(
        self,
        *,
        username: str,
        username_normalized: str,
        phone_e164: str | None,
        display_name: str,
        password_hash: str,
        role_codes: list[str],
        actor_user_id: UUID,
    ) -> UserRecord:
        now = datetime.now(UTC)
        user_id = uuid7()
        self.connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, phone_e164, display_name,
             password_hash, password_changed_at, created_by, updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                user_id,
                self.kindergarten_id,
                username,
                username_normalized,
                phone_e164,
                display_name,
                password_hash,
                now,
                actor_user_id,
                actor_user_id,
            ),
        )
        self.set_roles(user_id, role_codes, actor_user_id=actor_user_id, protect_last=False)
        record = self.get_user(user_id)
        assert record is not None
        return record

    def list_users(self, *, page: int, page_size: int) -> tuple[list[UserRecord], int]:
        total_row = self.connection.execute(
            "SELECT count(*) FROM users WHERE kindergarten_id=%s", (self.kindergarten_id,)
        ).fetchone()
        rows = self.connection.execute(
            f"""SELECT {_USER_COLUMNS} FROM users WHERE kindergarten_id=%s
            ORDER BY created_at, id LIMIT %s OFFSET %s""",
            (self.kindergarten_id, page_size, (page - 1) * page_size),
        ).fetchall()
        return ([_user(row) for row in rows if row is not None], int(total_row[0]))  # type: ignore[list-item,index]

    def update_user(
        self,
        user_id: UUID,
        *,
        username: str | None,
        username_normalized: str | None,
        phone_e164: str | None,
        display_name: str | None,
        actor_user_id: UUID,
    ) -> UserRecord:
        current = self.get_user(user_id, lock=True)
        if current is None:
            raise LookupError("账号不存在")
        row = self.connection.execute(
            """UPDATE users SET username=%s, username_normalized=%s, phone_e164=%s,
            display_name=%s, updated_by=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s RETURNING """
            + _USER_COLUMNS,
            (
                username if username is not None else current.username,
                username_normalized
                if username_normalized is not None
                else current.username_normalized,
                phone_e164,
                display_name if display_name is not None else current.display_name,
                actor_user_id,
                self.kindergarten_id,
                user_id,
            ),
        ).fetchone()
        record = _user(row)
        assert record is not None
        return record

    def set_roles(
        self,
        user_id: UUID,
        role_codes: list[str],
        *,
        actor_user_id: UUID,
        protect_last: bool = True,
    ) -> None:
        user = self.get_user(user_id, lock=True)
        if user is None:
            raise LookupError("账号不存在")
        current = set(self.roles_for_user(user_id))
        requested = set(role_codes)
        if (
            protect_last
            and "admin" in current
            and "admin" not in requested
            and not self.can_deactivate(user_id)
        ):
            raise ValueError("不能移除最后一个有效管理员")
        role_rows = self.connection.execute(
            "SELECT id, code FROM roles WHERE code = ANY(%s)", (list(requested),)
        ).fetchall()
        if {str(row[1]) for row in role_rows} != requested:
            raise ValueError("角色无效")
        self.connection.execute(
            "DELETE FROM user_roles WHERE kindergarten_id=%s AND user_id=%s",
            (self.kindergarten_id, user_id),
        )
        now = datetime.now(UTC)
        for role_id, _code in role_rows:
            self.connection.execute(
                """INSERT INTO user_roles
                (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
                VALUES (%s,%s,%s,%s,%s)""",
                (self.kindergarten_id, user_id, role_id, actor_user_id, now),
            )

    def set_active(self, user_id: UUID, *, active: bool, actor_user_id: UUID) -> UserRecord:
        self.lock_user_sessions(user_id)
        if not active and not self.can_deactivate(user_id):
            raise ValueError("不能停用最后一个有效管理员")
        row = self.connection.execute(
            """UPDATE users SET is_active=%s, updated_by=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s RETURNING """
            + _USER_COLUMNS,
            (active, actor_user_id, self.kindergarten_id, user_id),
        ).fetchone()
        record = _user(row)
        if record is None:
            raise LookupError("账号不存在")
        return record

    def update_password(self, user_id: UUID, password_hash: str, *, actor_user_id: UUID) -> None:
        self.lock_user_sessions(user_id)
        cursor = self.connection.execute(
            """UPDATE users SET password_hash=%s, password_changed_at=now(), updated_by=%s,
            updated_at=now() WHERE kindergarten_id=%s AND id=%s""",
            (password_hash, actor_user_id, self.kindergarten_id, user_id),
        )
        if cursor.rowcount != 1:
            raise LookupError("账号不存在")

    def create_refresh(
        self,
        *,
        user_id: UUID,
        family_id: UUID,
        token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> UUID:
        self.lock_user_sessions(user_id)
        token_id = uuid7()
        self.connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (token_id, self.kindergarten_id, user_id, family_id, token_hash, issued_at, expires_at),
        )
        return token_id

    def get_refresh(self, token_hash: str, *, lock: bool = False) -> RefreshRecord | None:
        record = self._select_refresh(token_hash, lock=False)
        if record is None or not lock:
            return record
        self.lock_user_sessions(record.user_id)
        self._lock_refresh_family(record.token_family_id)
        return self._select_refresh(token_hash, lock=True)

    def _select_refresh(self, token_hash: str, *, lock: bool) -> RefreshRecord | None:
        suffix = " FOR UPDATE" if lock else ""
        row = self.connection.execute(
            """SELECT id, kindergarten_id, user_id, token_family_id, issued_at, expires_at,
            revoked_at, replaced_by_id FROM refresh_tokens
            WHERE kindergarten_id=%s AND token_hash=%s"""
            + suffix,
            (self.kindergarten_id, token_hash),
        ).fetchone()
        return RefreshRecord(*row) if row is not None else None  # type: ignore[arg-type]

    def has_active_refresh_family(self, user_id: UUID, family_id: UUID) -> bool:
        row = self.connection.execute(
            """SELECT EXISTS(SELECT 1 FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s AND token_family_id=%s
              AND revoked_at IS NULL AND expires_at>now())""",
            (self.kindergarten_id, user_id, family_id),
        ).fetchone()
        return bool(row and row[0])

    def rotate_refresh(self, old: RefreshRecord, *, new_hash: str, now: datetime) -> UUID:
        self.lock_user_sessions(old.user_id)
        self._lock_refresh_family(old.token_family_id)
        if old.revoked_at is not None or old.expires_at <= now:
            raise ValueError("Refresh token 已失效")
        new_id = self.create_refresh(
            user_id=old.user_id,
            family_id=old.token_family_id,
            token_hash=new_hash,
            issued_at=now,
            expires_at=old.expires_at,
        )
        self.connection.execute(
            """UPDATE refresh_tokens SET revoked_at=%s, revoke_reason='rotated',
            replaced_by_id=%s, last_used_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (now, new_id, now, self.kindergarten_id, old.id),
        )
        return new_id

    def revoke_family(self, family_id: UUID, *, reason: str) -> None:
        user_row = self.connection.execute(
            """SELECT user_id FROM refresh_tokens
            WHERE kindergarten_id=%s AND token_family_id=%s ORDER BY id LIMIT 1""",
            (self.kindergarten_id, family_id),
        ).fetchone()
        if user_row is None:
            return
        self.lock_user_sessions(user_row[0])  # type: ignore[arg-type]
        self._lock_refresh_family(family_id)
        self.connection.execute(
            """UPDATE refresh_tokens SET revoked_at=COALESCE(revoked_at, now()),
            revoke_reason=%s, updated_at=now()
            WHERE kindergarten_id=%s AND token_family_id=%s""",
            (reason, self.kindergarten_id, family_id),
        )

    def revoke_user_sessions(self, user_id: UUID, *, reason: str) -> None:
        self.lock_user_sessions(user_id)
        family_ids = self.connection.execute(
            """SELECT DISTINCT token_family_id FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s ORDER BY token_family_id""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        for (family_id,) in family_ids:
            self._lock_refresh_family(family_id)  # type: ignore[arg-type]
        self.connection.execute(
            """UPDATE refresh_tokens SET revoked_at=COALESCE(revoked_at, now()),
            revoke_reason=%s, updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s""",
            (reason, self.kindergarten_id, user_id),
        )
