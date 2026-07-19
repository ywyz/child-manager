"""带业务数据的旧 0005 库升级到 head 的回归测试。

Codex 第十二轮审阅 P0-1：空 0005 升级通过，但带旧园所/角色/用户/用户角色/
Refresh/审计数据的 0005 升级在 0006 `_migrate_roles_to_global` 处因
`kindergarten_id/created_at/updated_at` NOT NULL 约束失败。
"""

from collections.abc import Iterator

import pytest
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from tests.conftest import IS_POSTGRESQL


def _seed_legacy_0005_data(engine: Engine) -> None:
    """在已升级到 0005 的库中插入完整的旧业务数据。"""
    with engine.begin() as conn:
        # 旧 0001/0002/0003/0004/0005 的表结构：所有 ID 为 varchar(36)，
        # roles 含 kindergarten_id/created_at/updated_at NOT NULL。
        conn.execute(
            text(
                "INSERT INTO kindergartens (id, name, timezone, created_at, updated_at) "
                "VALUES (:id, :name, 'Asia/Shanghai', now(), now())"
            ),
            {"id": "00000000-0000-7000-8000-000000000001", "name": "旧园所"},
        )
        conn.execute(
            text(
                "INSERT INTO roles (id, kindergarten_id, code, name, created_at, updated_at) "
                "VALUES (:id, :kg, :code, :name, now(), now())"
            ),
            {
                "id": "00000000-0000-7000-8000-000000000010",
                "kg": "00000000-0000-7000-8000-000000000001",
                "code": "admin",
                "name": "管理员",
            },
        )
        conn.execute(
            text(
                "INSERT INTO roles (id, kindergarten_id, code, name, created_at, updated_at) "
                "VALUES (:id, :kg, :code, :name, now(), now())"
            ),
            {
                "id": "00000000-0000-7000-8000-000000000011",
                "kg": "00000000-0000-7000-8000-000000000001",
                "code": "teacher",
                "name": "教师",
            },
        )
        conn.execute(
            text(
                "INSERT INTO users (id, kindergarten_id, username, phone, display_name, "
                "password_hash, is_active, created_at, updated_at, created_by, updated_by) "
                "VALUES (:id, :kg, :username, NULL, :display, :pw, true, now(), now(), NULL, NULL)"
            ),
            {
                "id": "00000000-0000-7000-8000-000000000100",
                "kg": "00000000-0000-7000-8000-000000000001",
                "username": "admin",
                "display": "管理员",
                "pw": "argon2id$placeholder",
            },
        )
        conn.execute(
            text(
                "INSERT INTO user_roles (id, kindergarten_id, user_id, role_id, created_at) "
                "VALUES (:id, :kg, :user, :role, now())"
            ),
            {
                "id": "00000000-0000-7000-8000-000000000200",
                "kg": "00000000-0000-7000-8000-000000000001",
                "user": "00000000-0000-7000-8000-000000000100",
                "role": "00000000-0000-7000-8000-000000000010",
            },
        )
        conn.execute(
            text(
                "INSERT INTO refresh_tokens (id, kindergarten_id, user_id, family_id, "
                "token_hash, expires_at, revoked_at, created_at, updated_at, family_expires_at) "
                "VALUES (:id, :kg, :user, :family, :hash, now() + interval '7 days', NULL, "
                "now(), now(), now() + interval '7 days')"
            ),
            {
                "id": "00000000-0000-7000-8000-000000000300",
                "kg": "00000000-0000-7000-8000-000000000001",
                "user": "00000000-0000-7000-8000-000000000100",
                "family": "00000000-0000-7000-8000-000000000400",
                "hash": "legacytokenhash0000000000000000000000000000000000000000000000000000",
            },
        )
        conn.execute(
            text(
                "INSERT INTO audit_events (id, kindergarten_id, event_type, actor_user_id, "
                "resource_type, resource_id, action, result, event_metadata, created_at, updated_at) "
                "VALUES (:id, :kg, 'identity.login', :actor, 'user', :res, 'login', 'success', "
                "'{}'::jsonb, now(), now())"
            ),
            {
                "id": "00000000-0000-7000-8000-000000000500",
                "kg": "00000000-0000-7000-8000-000000000001",
                "actor": "00000000-0000-7000-8000-000000000100",
                "res": "00000000-0000-7000-8000-000000000100",
            },
        )


@pytest.fixture
def engine_with_legacy_0005_data(isolated_database_url: str) -> Iterator[Engine]:
    import os

    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "0005_refresh_family_revoked")

    engine = create_engine(isolated_database_url)
    _seed_legacy_0005_data(engine)

    yield engine
    engine.dispose()


@pytest.mark.skipif(
    not IS_POSTGRESQL,
    reason="带数据迁移需要 PostgreSQL 的 NOT NULL 约束与 UUID 类型语义",
)
def test_upgrade_from_0005_with_legacy_data_preserves_associations(
    engine_with_legacy_0005_data: Engine, isolated_database_url: str
) -> None:
    """带旧角色/用户/关联/令牌/审计数据的 0005 库升级到 head 必须保留 user_roles 关联。"""
    import os

    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    # 关键断言：此前因 roles NOT NULL 约束在此抛出 IntegrityError。
    upgrade(config, "head")

    engine = create_engine(isolated_database_url)
    try:
        inspector = inspect(engine)
        with engine.begin() as conn:
            # 旧 admin 角色已收敛为全局角色，user_roles 关联必须保留。
            role_rows = conn.execute(text("SELECT code FROM roles ORDER BY code")).fetchall()
            codes = {row[0] for row in role_rows}
            assert {"admin", "teacher"} <= codes

            # user_roles 必须仍指向有效角色，且 role_id 已更新为全局角色 ID。
            ur_rows = conn.execute(
                text(
                    "SELECT ur.user_id, r.code FROM user_roles ur JOIN roles r ON ur.role_id = r.id"
                )
            ).fetchall()
            assert any(row[1] == "admin" for row in ur_rows)

            # refresh_tokens 数据保留，且 token_family_id 列存在。
            rt_rows = conn.execute(
                text("SELECT user_id, token_family_id FROM refresh_tokens")
            ).fetchall()
            assert len(rt_rows) == 1

            # audit_events 数据保留，新列 event_code/outcome 已填充。
            ae_rows = conn.execute(text("SELECT event_code, outcome FROM audit_events")).fetchall()
            assert len(ae_rows) == 1
            assert ae_rows[0][0] == "identity.login"
            assert ae_rows[0][1] == "success"

        # 旧 roles 列已被移除。
        role_columns = {c["name"] for c in inspector.get_columns("roles")}
        assert "kindergarten_id" not in role_columns
        assert "created_at" not in role_columns
        assert "updated_at" not in role_columns
    finally:
        engine.dispose()
