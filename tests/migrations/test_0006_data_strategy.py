"""0006 迁移数据策略回归测试。

覆盖 Codex Issue #6 指出的三类硬问题：
1. 旧用户名经 NFKC+trim+lower 回填 username_normalized，确保升级后能按新规范登录。
2. 收窄字段前检测超长旧值，以清晰错误阻止升级，不静默截断。
3. 含 NULL resource_id 的 downgrade 必须先填充占位值再恢复 NOT NULL。
"""

from collections.abc import Iterator

import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from tests.conftest import IS_POSTGRESQL


def _seed_legacy_0005_user_with_nfkc_username(engine: Engine) -> None:
    """在已升级到 0005 的库中插入一个带 NFKC 规范化需求的旧用户。

    旧用户名 " Ｔｅａｃｈｅｒ "（全角字符 + 前后空格）经应用层
    normalize_username 应规范化为 "teacher"；仅 lower() 会得到 " ｔｅａｃｈｅｒ "。
    """
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO kindergartens (id, name, timezone, created_at, updated_at) "
                "VALUES (:id, :name, 'Asia/Shanghai', now(), now())"
            ),
            {"id": "00000000-0000-7000-8000-000000000001", "name": "测试园所"},
        )
        conn.execute(
            text(
                "INSERT INTO roles (id, kindergarten_id, code, name, created_at, updated_at) "
                "VALUES (:id, :kg, 'teacher', '教师', now(), now())"
            ),
            {
                "id": "00000000-0000-7000-8000-000000000010",
                "kg": "00000000-0000-7000-8000-000000000001",
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
                # 全角 + 前后空格：NFKC + trim + lower 后应为 "teacher"
                "username": " Ｔｅａｃｈｅｒ ",
                "display": "教师",
                "pw": "argon2id$placeholder",
            },
        )


@pytest.fixture
def engine_with_legacy_0005_nfkc_user(isolated_database_url: str) -> Iterator[Engine]:
    import os

    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "0005_refresh_family_revoked")

    engine = create_engine(isolated_database_url)
    _seed_legacy_0005_user_with_nfkc_username(engine)

    yield engine
    engine.dispose()


@pytest.mark.skipif(
    not IS_POSTGRESQL,
    reason="带数据迁移需要 PostgreSQL 的 NFKC 与 UUID 类型语义",
)
def test_upgrade_nfkc_username_normalized_matches_application_rule(
    engine_with_legacy_0005_nfkc_user: Engine, isolated_database_url: str
) -> None:
    """旧用户名 " Ｔｅａｃｈｅｒ " 升级后 username_normalized 必须为 "teacher"。

    Codex 探针发现 0006 仅用 lower(username) 回填，得到 " ｔｅａｃｈｅｒ "，
    导致旧账号升级后无法按新规范登录。修复后必须使用 NFKC+trim+lower。
    """
    import os

    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "head")

    engine = create_engine(isolated_database_url)
    try:
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT username_normalized FROM users WHERE id = :uid"),
                {"uid": "00000000-0000-7000-8000-000000000100"},
            ).fetchone()
            assert row is not None
            # 关键断言：NFKC+trim+lower，而非仅 lower()
            assert row[0] == "teacher"
    finally:
        engine.dispose()


@pytest.mark.skipif(
    not IS_POSTGRESQL,
    reason="带数据迁移需要 PostgreSQL 的 NOT NULL 约束语义",
)
def test_upgrade_aborts_on_oversized_kindergarten_name(
    isolated_database_url: str,
) -> None:
    """0005 允许 201 字符园所名；0006 收窄到 200 时必须阻止升级并给出清晰错误。

    AGENTS.md 要求数据迁移不得静默截断合法旧数据。修复后应先检测超长值，
    以 RuntimeError 形式阻止升级，让运维先完成可审计的数据修复。
    """
    import os

    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "0005_refresh_family_revoked")

    engine = create_engine(isolated_database_url)
    try:
        with engine.begin() as conn:
            # 插入 201 字符的园所名（0005 允许 255）
            conn.execute(
                text(
                    "INSERT INTO kindergartens (id, name, timezone, created_at, updated_at) "
                    "VALUES (:id, :name, 'Asia/Shanghai', now(), now())"
                ),
                {
                    "id": "00000000-0000-7000-8000-000000000001",
                    "name": "x" * 201,
                },
            )
    finally:
        engine.dispose()

    # 升级必须以 RuntimeError 阻止，不得静默截断
    with pytest.raises(RuntimeError, match=r"无法收窄 kindergartens.name"):
        upgrade(config, "head")


@pytest.mark.skipif(
    not IS_POSTGRESQL,
    reason="带数据迁移需要 PostgreSQL 的 NOT NULL 约束语义",
)
def test_upgrade_aborts_on_oversized_username(
    isolated_database_url: str,
) -> None:
    """0005 允许 128 字符 username；0006 收窄到 120 时必须阻止升级。"""
    import os

    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "0005_refresh_family_revoked")

    engine = create_engine(isolated_database_url)
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO kindergartens (id, name, timezone, created_at, updated_at) "
                    "VALUES (:id, :name, 'Asia/Shanghai', now(), now())"
                ),
                {
                    "id": "00000000-0000-7000-8000-000000000001",
                    "name": "测试园所",
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
                    # 121 字符（0005 允许 128，0006 收窄到 120）
                    "username": "a" * 121,
                    "display": "教师",
                    "pw": "argon2id$placeholder",
                },
            )
    finally:
        engine.dispose()

    with pytest.raises(RuntimeError, match=r"无法收窄 users.username"):
        upgrade(config, "head")


@pytest.mark.skipif(
    not IS_POSTGRESQL,
    reason="含数据 downgrade 需要 PostgreSQL 的 NOT NULL 约束语义",
)
def test_downgrade_handles_null_resource_id(
    isolated_database_url: str,
) -> None:
    """head -> 0005 降级时，NULL resource_id 必须先填充占位值再恢复 NOT NULL。

    Codex 探针发现 downgrade 强制 resource_id NOT NULL 却未迁移 NULL，
    插入一条 NULL resource_id 审计事件后降级稳定报 NotNullViolation。
    修复后 downgrade 应先填充占位 UUID 再恢复 NOT NULL。
    """
    import os

    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "head")

    engine = create_engine(isolated_database_url)
    try:
        with engine.begin() as conn:
            # 先插入园所以满足 audit_events.fk_audit_events_kindergarten 外键
            conn.execute(
                text(
                    "INSERT INTO kindergartens (id, name, timezone, is_active, created_at, updated_at) "
                    "VALUES (:id, :name, 'Asia/Shanghai', true, now(), now())"
                ),
                {
                    "id": "00000000-0000-7000-8000-000000000001",
                    "name": "测试园所",
                },
            )
            # 插入一条真实登录失败形态的审计事件：resource_id 为 NULL
            conn.execute(
                text(
                    "INSERT INTO audit_events (id, kindergarten_id, event_code, actor_user_id, "
                    "resource_type, resource_id, outcome, metadata, actor_role_codes, occurred_at, "
                    "created_at, updated_at) "
                    "VALUES (:id, :kg, 'identity.login_failed', NULL, 'user', NULL, 'failure', "
                    "'{}'::jsonb, '[]'::jsonb, now(), now(), now())"
                ),
                {
                    "id": "00000000-0000-7000-8000-000000000500",
                    "kg": "00000000-0000-7000-8000-000000000001",
                },
            )
    finally:
        engine.dispose()

    # 降级到 0005 必须成功，不得因 NotNullViolation 失败
    downgrade(config, "0005_refresh_family_revoked")

    engine = create_engine(isolated_database_url)
    try:
        inspector = inspect(engine)
        columns = {c["name"]: c for c in inspector.get_columns("audit_events")}
        # 降级后 resource_id 恢复为 varchar(36) NOT NULL
        assert not columns["resource_id"]["nullable"]
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT resource_id FROM audit_events WHERE id = :id"),
                {"id": "00000000-0000-7000-8000-000000000500"},
            ).fetchone()
            assert row is not None
            # NULL 已被占位 UUID 替换
            assert row[0] == "00000000-0000-0000-0000-000000000000"
    finally:
        engine.dispose()
