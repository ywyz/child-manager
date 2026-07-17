"""首位管理员初始化必须在单一数据库事务内完成。"""

from datetime import UTC, datetime
from uuid import uuid7

import psycopg

from packages.backend.audit.repository import AuditRepository
from packages.backend.identity.identifiers import normalize_username
from packages.backend.identity.passwords import hash_password, password_violations
from packages.contracts.audit import IdentityAuditEventCode


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def initialize_admin(
    *,
    database_url: str,
    kindergarten_name: str,
    username: str,
    display_name: str,
    password: str,
) -> bool:
    """返回 True 表示创建成功，False 表示系统已经初始化。"""

    violations = password_violations(password)
    if violations:
        raise ValueError("密码必须为 15–128 个字符且不能是常见弱密码")
    normalized_username = normalize_username(username)
    with psycopg.connect(_native_url(database_url)) as connection, connection.transaction():
        connection.execute("SELECT pg_advisory_xact_lock(1128812109)")
        existing = connection.execute("SELECT 1 FROM kindergartens LIMIT 1 FOR UPDATE").fetchone()
        if existing is not None:
            return False
        now = datetime.now(UTC)
        kindergarten_id = uuid7()
        user_id = uuid7()
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, %s)",
            (kindergarten_id, kindergarten_name.strip()),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             password_hash, password_changed_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                user_id,
                kindergarten_id,
                normalized_username,
                normalized_username,
                display_name.strip(),
                hash_password(password),
                now,
            ),
        )
        admin_role = connection.execute("SELECT id FROM roles WHERE code='admin'").fetchone()
        if admin_role is None:
            raise RuntimeError("管理员角色种子缺失")
        connection.execute(
            """INSERT INTO user_roles
            (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (kindergarten_id, user_id, admin_role[0], user_id, now),
        )
        connection.execute(
            """UPDATE users SET created_by=%s, updated_by=%s
            WHERE kindergarten_id=%s AND id=%s""",
            (user_id, user_id, kindergarten_id, user_id),
        )
        AuditRepository(connection, kindergarten_id).append(
            event_code=IdentityAuditEventCode.INITIALIZED,
            actor_user_id=user_id,
            actor_role_codes=["admin"],
            resource_type="kindergarten",
            resource_id=kindergarten_id,
            outcome="success",
        )
        return True
