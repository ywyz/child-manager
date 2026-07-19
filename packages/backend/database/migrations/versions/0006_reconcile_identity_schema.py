"""reconcile identity schema

Revision ID: 0006_reconcile_identity_schema
Revises: 0005_refresh_family_revoked
Create Date: 2026-07-19 00:00:00.000000

"""

import unicodedata
from collections.abc import Sequence
from uuid import uuid7

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

_UUID = sa.Uuid(as_uuid=False)

revision: str = "0006_reconcile_identity_schema"
down_revision: str | None = "0005_refresh_family_revoked"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _normalize_username_nfkc(value: str) -> str:
    """与应用层 identifiers.normalize_username 一致：NFKC + trim + lower。

    迁移回填必须使用与应用相同的规范化规则，否则旧账号升级后无法按新规范
    登录（T021/T029 冻结规则）。
    """
    return unicodedata.normalize("NFKC", value).strip().lower()


def _abort_if_oversized(table: str, column: str, max_length: int) -> None:
    """检测旧库中存在超长值时以清晰错误阻止升级。

    AGENTS.md 要求数据迁移不得静默截断合法旧数据。这里在收窄字段前先扫描，
    若存在超出新长度的值，给出可操作错误（包含表、列、最大长度与超长行数），
    让运维先完成可审计的数据修复再升级。
    """
    bind = op.get_bind()
    oversized = bind.execute(
        sa.text(f"SELECT COUNT(*) FROM {table} WHERE char_length({column}) > :max_len"),
        {"max_len": max_length},
    ).scalar_one()
    if oversized > 0:
        msg = (
            f"无法收窄 {table}.{column} 至 {max_length} 字符：检测到 {oversized} 行"
            f"超长旧值。请先审计并修复这些行（例如更新为符合新长度的值），"
            f"再重新执行升级。"
        )
        raise RuntimeError(msg)


def _backfill_username_normalized() -> None:
    """按 NFKC+trim+lower 回填 username_normalized 并检测碰撞。

    回填必须使用与应用层 identifiers.normalize_username 相同的规则，否则
    旧账号升级后无法按新规范登录（例如旧用户名 " Ｔｅａｃｈｅｒ " 经 NFKC
    应规范化为 "teacher"，而仅 lower() 会得到 " ｔｅａｃｈｅｒ "）。

    若同一园所内多个旧用户名经规范化后碰撞，以清晰错误阻止升级，要求先
    完成可审计的数据修复（重命名其中一方），不得静默选择保留方。
    """
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, kindergarten_id, username FROM users")).fetchall()
    # 先在 Python 侧计算规范化值并检测碰撞。
    seen: dict[tuple[str, str], str] = {}
    collisions: list[str] = []
    updates: list[tuple[str, str, str]] = []
    for row in rows:
        user_id, kg_id, username = row
        normalized = _normalize_username_nfkc(username if username is not None else "")
        key = (str(kg_id), normalized)
        if key in seen:
            collisions.append(
                f"kindergarten_id={kg_id} normalized='{normalized}'"
                f" (user_id={seen[key]} 与 user_id={user_id})"
            )
            continue
        seen[key] = str(user_id)
        updates.append((str(user_id), str(kg_id), normalized))
    if collisions:
        msg = (
            "检测到用户名 NFKC 规范化碰撞，无法安全回填 username_normalized：\n"
            + "\n".join(collisions)
            + "\n请先审计并重命名其中一方，再重新执行升级。"
        )
        raise RuntimeError(msg)
    # 逐行回填，避免一次性 UPDATE 使用非确定性 SQL 函数。
    for user_id, _kg_id, normalized in updates:
        bind.execute(
            sa.text("UPDATE users SET username_normalized = :norm WHERE id = :uid"),
            {"norm": normalized, "uid": user_id},
        )


def _ensure_system_roles() -> None:
    """确保全局 admin/teacher 系统角色存在。"""
    bind = op.get_bind()
    for code, name in (("admin", "管理员"), ("teacher", "教师")):
        exists = bind.execute(
            sa.text("SELECT 1 FROM roles WHERE code = :code LIMIT 1"),
            {"code": code},
        ).fetchone()
        if exists is None:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO roles (id, code, name, is_system)
                    VALUES (:id, :code, :name, true)
                    """
                ),
                {"id": str(uuid7()), "code": code, "name": name},
            )


def _migrate_roles_to_global() -> None:
    """将旧园所范围的 roles 表收敛为全局只读字典，并更新 user_roles.role_id。

    旧 0001 的 roles 表要求 kindergarten_id/created_at/updated_at 非空，
    且存在 `uq_roles_kindergarten_code (kindergarten_id, code)` 唯一约束。
    因此收敛顺序为：先建立 old_id -> new_id 映射并更新 user_roles
    （FK 已在阶段 0 删除），再删除全部旧角色，最后插入满足旧 NOT NULL
    约束的全局新角色，避免唯一约束冲突。
    """
    bind = op.get_bind()
    old_roles = bind.execute(
        sa.text("SELECT id, kindergarten_id, code, name FROM roles")
    ).fetchall()
    if not old_roles:
        return

    # 取一个已存在的 kindergarten_id 作为新行的临时值；园所表为空时使用占位 UUID。
    kg_row = bind.execute(sa.text("SELECT id FROM kindergartens LIMIT 1")).fetchone()
    placeholder_kg_id = kg_row[0] if kg_row else "00000000-0000-7000-8000-000000000000"

    # 为每个 code 分配一个新 UUIDv7，同时保留 old_id -> new_id 与 code -> name 映射。
    code_to_new_id: dict[str, str] = {}
    code_to_name: dict[str, str] = {}
    old_to_new: dict[str, str] = {}
    for old_id, _kg_id, code, name in old_roles:
        if code not in code_to_new_id:
            code_to_new_id[code] = str(uuid7())
            code_to_name[code] = name if name else code
        old_to_new[old_id] = code_to_new_id[code]

    # FK 已在阶段 0 删除，可直接更新 user_roles.role_id 指向新全局角色 ID。
    for old_id, new_id in old_to_new.items():
        bind.execute(
            sa.text("UPDATE user_roles SET role_id = :new_id WHERE role_id = :old_id"),
            {"new_id": new_id, "old_id": old_id},
        )

    # 先删除全部旧角色，避免唯一约束 (kindergarten_id, code) 与新行冲突。
    bind.execute(sa.text("DELETE FROM roles"))

    # 插入全局新角色；旧表仍要求 kindergarten_id/created_at/updated_at 非空，
    # 这些列在后续 op.drop_column 中移除。
    for code, new_id in code_to_new_id.items():
        bind.execute(
            sa.text(
                """
                INSERT INTO roles (id, kindergarten_id, code, name, is_system,
                                   created_at, updated_at)
                VALUES (:id, :kg_id, :code, :name, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            ),
            {
                "id": new_id,
                "kg_id": placeholder_kg_id,
                "code": code,
                "name": code_to_name[code],
            },
        )


def _convert_varchar36_to_uuid(table: str, columns: list[str]) -> None:
    """将指定表的 varchar(36) 列批量转换为 uuid 类型。"""
    for column in columns:
        op.execute(
            sa.text(
                f"""
                ALTER TABLE {table}
                ALTER COLUMN {column} TYPE uuid
                USING {column}::uuid
                """
            )
        )


def upgrade() -> None:
    # --- 启用首个迁移要求的扩展（冻结 Schema 约定）----------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    # --- 阶段 0：将所有 varchar(36) 的 ID/外键列统一转换为 uuid ------------
    # 先删除会影响列类型的外键约束
    op.drop_constraint("fk_user_roles_role", "user_roles", type_="foreignkey")
    op.drop_constraint("fk_user_roles_user", "user_roles", type_="foreignkey")
    op.drop_constraint("fk_refresh_tokens_user", "refresh_tokens", type_="foreignkey")

    _convert_varchar36_to_uuid(
        "kindergartens",
        ["id"],
    )
    _convert_varchar36_to_uuid(
        "roles",
        ["id", "kindergarten_id"],
    )
    _convert_varchar36_to_uuid(
        "users",
        ["id", "kindergarten_id", "created_by", "updated_by"],
    )
    _convert_varchar36_to_uuid(
        "user_roles",
        ["id", "kindergarten_id", "user_id", "role_id"],
    )
    _convert_varchar36_to_uuid(
        "refresh_tokens",
        ["id", "kindergarten_id", "user_id", "family_id"],
    )
    _convert_varchar36_to_uuid(
        "audit_events",
        ["id", "kindergarten_id", "actor_user_id"],
    )

    # resource_id 对齐冻结 Schema §6.2：UUID NULL。
    # 先放宽 NOT NULL 约束，再清理不可转换的旧值，最后转换为 UUID 类型。
    op.alter_column(
        "audit_events",
        "resource_id",
        existing_type=sa.String(36),
        existing_nullable=False,
        nullable=True,
    )
    # 旧值可能是 UUID 字符串（含 UUIDv7）或 username 字符串；不可转换为 UUID 的旧值置 NULL，
    # 身份事件 resource_id 语义统一为 user_id（UUID）或 NULL。
    op.execute(
        sa.text(
            """
            UPDATE audit_events
            SET resource_id = NULL
            WHERE resource_id IS NOT NULL
              AND resource_id !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            """
        )
    )
    op.alter_column(
        "audit_events",
        "resource_id",
        existing_type=sa.String(36),
        type_=_UUID,
        existing_nullable=True,
        postgresql_using="resource_id::uuid",
    )

    # --- kindergartens ---------------------------------------------------------
    # 冻结 Schema §5.1：name VARCHAR(200)。
    # 0005 允许 255 字符，收窄前必须检测超长旧值，不得静默截断。
    _abort_if_oversized("kindergartens", "name", 200)
    op.alter_column(
        "kindergartens",
        "name",
        existing_type=sa.String(255),
        type_=sa.String(200),
        existing_nullable=False,
    )
    op.add_column(
        "kindergartens",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_check_constraint(
        "ck_kindergartens_timezone",
        "kindergartens",
        "timezone = 'Asia/Shanghai'",
    )

    # --- roles: 从园所范围表收敛为全局只读字典 --------------------------------
    op.add_column(
        "roles",
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    _migrate_roles_to_global()
    op.drop_constraint("uq_roles_kindergarten_id", "roles", type_="unique")
    op.drop_constraint("uq_roles_kindergarten_code", "roles", type_="unique")
    # 冻结 Schema §5.3：name VARCHAR(120)。
    _abort_if_oversized("roles", "name", 120)
    op.alter_column(
        "roles",
        "name",
        existing_type=sa.String(128),
        type_=sa.String(120),
        existing_nullable=False,
    )
    op.drop_column("roles", "kindergarten_id")
    op.drop_column("roles", "created_at")
    op.drop_column("roles", "updated_at")
    op.create_unique_constraint("uq_roles_code", "roles", ["code"])

    # 确保系统角色存在（空库升级时 roles 可能为空）
    _ensure_system_roles()

    # --- user_roles: 删除代理 id，改为复合主键，增加分配信息 -----------------
    op.add_column(
        "user_roles",
        sa.Column("assigned_by", _UUID, nullable=True),
    )
    op.add_column(
        "user_roles",
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(sa.text("UPDATE user_roles SET assigned_by = user_id, assigned_at = created_at"))
    op.alter_column("user_roles", "assigned_by", nullable=False)
    op.alter_column("user_roles", "assigned_at", nullable=False)
    op.drop_constraint("user_roles_pkey", "user_roles", type_="primary")
    op.drop_column("user_roles", "id")
    op.drop_constraint("uq_user_roles_kindergarten", "user_roles", type_="unique")
    op.create_primary_key("pk_user_roles", "user_roles", ["kindergarten_id", "user_id", "role_id"])
    op.create_foreign_key("fk_user_roles_role", "user_roles", "roles", ["role_id"], ["id"])
    op.create_foreign_key(
        "fk_user_roles_user",
        "user_roles",
        "users",
        ["kindergarten_id", "user_id"],
        ["kindergarten_id", "id"],
    )
    op.create_foreign_key(
        "fk_user_roles_assigned_by",
        "user_roles",
        "users",
        ["kindergarten_id", "assigned_by"],
        ["kindergarten_id", "id"],
    )

    # --- users: 增加规范化/登录/审计字段，调整唯一约束 -------------------------
    # 冻结 Schema §5.2：username/display_name VARCHAR(120)。
    # 0001 允许 128 字符，收窄前必须检测超长旧值，不得静默截断。
    _abort_if_oversized("users", "username", 120)
    _abort_if_oversized("users", "display_name", 120)
    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(128),
        type_=sa.String(120),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "display_name",
        existing_type=sa.String(128),
        type_=sa.String(120),
        existing_nullable=False,
    )
    op.add_column(
        "users",
        sa.Column("username_normalized", sa.String(120), nullable=True),
    )
    # 回填 username_normalized 必须使用与应用层 identifiers.normalize_username
    # 相同的 NFKC + trim + lower 规则（T021/T029 冻结），否则旧账号升级后无法
    # 按新规范登录。PostgreSQL 无内置 NFKC，通过 Python 在迁移进程内计算后
    # 逐行回填。同时检测 NFKC 规范化后的碰撞，碰撞时阻止升级并要求先修复。
    _backfill_username_normalized()
    op.alter_column("users", "username_normalized", nullable=False)

    op.add_column(
        "users",
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(sa.text("UPDATE users SET password_changed_at = created_at"))
    op.alter_column("users", "password_changed_at", nullable=False)

    op.add_column(
        "users",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.execute(sa.text("UPDATE users SET phone = NULL WHERE phone = ''"))
    op.drop_constraint("uq_users_kindergarten_phone", "users", type_="unique")
    op.alter_column(
        "users",
        "phone",
        new_column_name="phone_e164",
        existing_type=sa.String(32),
        existing_nullable=True,
    )
    op.create_index(
        "ix_users_kindergarten_phone",
        "users",
        ["kindergarten_id", "phone_e164"],
        unique=True,
        postgresql_where=sa.text("phone_e164 IS NOT NULL"),
    )

    op.drop_constraint("uq_users_kindergarten_username", "users", type_="unique")
    op.create_unique_constraint(
        "uq_users_kindergarten_username",
        "users",
        ["kindergarten_id", "username_normalized"],
    )
    op.create_index("ix_users_kindergarten_active", "users", ["kindergarten_id", "is_active"])
    op.create_foreign_key(
        "fk_users_kindergarten", "users", "kindergartens", ["kindergarten_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_users_created_by",
        "users",
        "users",
        ["kindergarten_id", "created_by"],
        ["kindergarten_id", "id"],
    )
    op.create_foreign_key(
        "fk_users_updated_by",
        "users",
        "users",
        ["kindergarten_id", "updated_by"],
        ["kindergarten_id", "id"],
    )
    op.create_check_constraint(
        "ck_users_phone_e164",
        "users",
        "phone_e164 IS NULL OR phone_e164 <> ''",
    )

    # --- refresh_tokens: 重命名 family_id，增加 issued_at 等字段 -------------
    op.add_column(
        "refresh_tokens",
        sa.Column("token_family_id", _UUID, nullable=True),
    )
    op.execute(sa.text("UPDATE refresh_tokens SET token_family_id = family_id"))
    op.alter_column("refresh_tokens", "token_family_id", nullable=False)
    op.drop_column("refresh_tokens", "family_id")

    op.add_column(
        "refresh_tokens",
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(sa.text("UPDATE refresh_tokens SET issued_at = created_at"))
    op.alter_column("refresh_tokens", "issued_at", nullable=False)

    op.add_column(
        "refresh_tokens",
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("revoke_reason", sa.String(64), nullable=True),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("replaced_by_id", _UUID, nullable=True),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("client_label", sa.String(160), nullable=True),
    )
    op.create_unique_constraint(
        "uq_refresh_tokens_kindergarten_id",
        "refresh_tokens",
        ["kindergarten_id", "id"],
    )
    op.create_foreign_key(
        "fk_refresh_tokens_user",
        "refresh_tokens",
        "users",
        ["kindergarten_id", "user_id"],
        ["kindergarten_id", "id"],
    )
    op.create_foreign_key(
        "fk_refresh_tokens_replaced_by",
        "refresh_tokens",
        "refresh_tokens",
        ["kindergarten_id", "replaced_by_id"],
        ["kindergarten_id", "id"],
    )
    op.create_check_constraint(
        "ck_refresh_tokens_expires_after_issued",
        "refresh_tokens",
        "expires_at > issued_at",
    )
    op.create_check_constraint(
        "ck_refresh_tokens_replaced_implies_revoked",
        "refresh_tokens",
        "replaced_by_id IS NULL OR revoked_at IS NOT NULL",
    )
    op.create_index(
        "ix_refresh_tokens_user_revoked_expires",
        "refresh_tokens",
        ["kindergarten_id", "user_id", "revoked_at", "expires_at"],
    )
    op.create_index(
        "ix_refresh_tokens_family_revoked",
        "refresh_tokens",
        ["token_family_id", "revoked_at"],
    )

    # 冻结 Schema §5.5 未定义 family 级过期/撤销列：0003/0005 引入的这两列在此收敛移除，
    # family 撤销语义改由批量设置 family 内所有 token 的 revoked_at 表达。
    op.drop_column("refresh_tokens", "family_expires_at")
    op.drop_column("refresh_tokens", "family_revoked_at")

    # --- audit_events: 调整字段、增加 FK 与索引 --------------------------------
    op.add_column(
        "audit_events",
        sa.Column("event_code", sa.String(120), nullable=True),
    )
    op.execute(sa.text("UPDATE audit_events SET event_code = event_type"))
    op.alter_column("audit_events", "event_code", nullable=False)

    op.add_column(
        "audit_events",
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE audit_events
            SET metadata = COALESCE(
                CASE WHEN jsonb_typeof(event_metadata) = 'object'
                     THEN event_metadata
                     ELSE '{}'::jsonb
                END,
                '{}'::jsonb
            )
            """
        )
    )
    op.alter_column("audit_events", "metadata", nullable=False)

    op.add_column(
        "audit_events",
        sa.Column(
            "actor_role_codes",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "audit_events",
        sa.Column("request_id", _UUID, nullable=True),
    )
    op.add_column(
        "audit_events",
        sa.Column("trace_id", _UUID, nullable=True),
    )
    op.add_column(
        "audit_events",
        sa.Column("job_id", _UUID, nullable=True),
    )
    op.add_column(
        "audit_events",
        sa.Column("outcome", sa.String(16), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE audit_events
            SET outcome = CASE WHEN lower(result) = 'success'
                               THEN 'success'
                               ELSE 'failure'
                          END
            """
        )
    )
    op.alter_column("audit_events", "outcome", nullable=False)

    op.add_column(
        "audit_events",
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(sa.text("UPDATE audit_events SET occurred_at = created_at"))
    op.alter_column("audit_events", "occurred_at", nullable=False)
    op.execute(sa.text("UPDATE audit_events SET updated_at = created_at"))

    op.drop_column("audit_events", "event_type")
    op.drop_column("audit_events", "action")
    op.drop_column("audit_events", "result")
    op.drop_column("audit_events", "event_metadata")

    op.create_unique_constraint(
        "uq_audit_events_kindergarten_id",
        "audit_events",
        ["kindergarten_id", "id"],
    )
    op.create_foreign_key(
        "fk_audit_events_actor_user",
        "audit_events",
        "users",
        ["kindergarten_id", "actor_user_id"],
        ["kindergarten_id", "id"],
    )
    op.create_foreign_key(
        "fk_audit_events_kindergarten",
        "audit_events",
        "kindergartens",
        ["kindergarten_id"],
        ["id"],
    )
    op.create_check_constraint(
        "ck_audit_events_actor_role_codes_array",
        "audit_events",
        "jsonb_typeof(actor_role_codes) = 'array'",
    )
    op.create_check_constraint(
        "ck_audit_events_metadata_object",
        "audit_events",
        "jsonb_typeof(metadata) = 'object'",
    )
    op.create_check_constraint(
        "ck_audit_events_outcome",
        "audit_events",
        "outcome IN ('success', 'failure')",
    )
    op.create_check_constraint(
        "ck_audit_events_immutable",
        "audit_events",
        "updated_at = created_at",
    )
    op.create_index(
        "ix_audit_events_kindergarten_occurred",
        "audit_events",
        ["kindergarten_id", "occurred_at"],
        postgresql_ops={"occurred_at": "DESC"},
    )
    op.create_index(
        "ix_audit_events_kindergarten_event_code_occurred",
        "audit_events",
        ["kindergarten_id", "event_code", "occurred_at"],
        postgresql_ops={"occurred_at": "DESC"},
    )
    op.create_index(
        "ix_audit_events_kindergarten_resource_occurred",
        "audit_events",
        ["kindergarten_id", "resource_type", "resource_id", "occurred_at"],
        postgresql_ops={"occurred_at": "DESC"},
    )
    op.create_index(
        "ix_audit_events_kindergarten_actor_occurred",
        "audit_events",
        ["kindergarten_id", "actor_user_id", "occurred_at"],
        postgresql_ops={"occurred_at": "DESC"},
    )


def downgrade() -> None:
    # --- audit_events: 恢复旧列（数据简化）------------------------------------
    op.drop_index("ix_audit_events_kindergarten_occurred", table_name="audit_events")
    op.drop_index(
        "ix_audit_events_kindergarten_event_code_occurred",
        table_name="audit_events",
    )
    op.drop_index(
        "ix_audit_events_kindergarten_resource_occurred",
        table_name="audit_events",
    )
    op.drop_index(
        "ix_audit_events_kindergarten_actor_occurred",
        table_name="audit_events",
    )
    op.drop_constraint("fk_audit_events_actor_user", "audit_events", type_="foreignkey")
    op.drop_constraint("fk_audit_events_kindergarten", "audit_events", type_="foreignkey")
    op.drop_constraint("uq_audit_events_kindergarten_id", "audit_events", type_="unique")
    op.drop_constraint("ck_audit_events_actor_role_codes_array", "audit_events", type_="check")
    op.drop_constraint("ck_audit_events_metadata_object", "audit_events", type_="check")
    op.drop_constraint("ck_audit_events_outcome", "audit_events", type_="check")
    op.drop_constraint("ck_audit_events_immutable", "audit_events", type_="check")

    op.drop_column("audit_events", "event_code")
    op.drop_column("audit_events", "actor_role_codes")
    op.drop_column("audit_events", "request_id")
    op.drop_column("audit_events", "trace_id")
    op.drop_column("audit_events", "job_id")
    op.drop_column("audit_events", "outcome")
    op.drop_column("audit_events", "occurred_at")
    op.drop_column("audit_events", "metadata")

    op.add_column(
        "audit_events",
        sa.Column("event_type", sa.String(64), nullable=False, server_default=""),
    )
    op.add_column(
        "audit_events",
        sa.Column("action", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "audit_events",
        sa.Column("result", sa.String(32), nullable=False, server_default="failure"),
    )
    op.add_column(
        "audit_events",
        sa.Column("event_metadata", postgresql.JSONB(), nullable=True),
    )
    op.alter_column("audit_events", "event_type", server_default=None)
    op.alter_column("audit_events", "action", server_default=None)
    op.alter_column("audit_events", "result", server_default=None)

    # --- refresh_tokens: 撤销新增字段与约束 ------------------------------------
    op.drop_index("ix_refresh_tokens_user_revoked_expires", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_family_revoked", table_name="refresh_tokens")
    op.drop_constraint(
        "ck_refresh_tokens_expires_after_issued",
        "refresh_tokens",
        type_="check",
    )
    op.drop_constraint(
        "ck_refresh_tokens_replaced_implies_revoked",
        "refresh_tokens",
        type_="check",
    )
    op.drop_constraint("fk_refresh_tokens_replaced_by", "refresh_tokens", type_="foreignkey")
    op.drop_constraint("fk_refresh_tokens_user", "refresh_tokens", type_="foreignkey")
    op.drop_constraint(
        "uq_refresh_tokens_kindergarten_id",
        "refresh_tokens",
        type_="unique",
    )
    op.drop_column("refresh_tokens", "issued_at")
    op.drop_column("refresh_tokens", "last_used_at")
    op.drop_column("refresh_tokens", "revoke_reason")
    op.drop_column("refresh_tokens", "replaced_by_id")
    op.drop_column("refresh_tokens", "client_label")
    op.alter_column(
        "refresh_tokens",
        "token_family_id",
        new_column_name="family_id",
        existing_type=_UUID,
        existing_nullable=False,
    )
    # 恢复 0003/0005 引入的 family 级列，使降级后库结构与 0005 一致。
    op.add_column(
        "refresh_tokens",
        sa.Column("family_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("family_revoked_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- users: 撤销新增列、FK 与唯一约束 --------------------------------------
    op.drop_constraint("ck_users_phone_e164", "users", type_="check")
    op.drop_constraint("fk_users_updated_by", "users", type_="foreignkey")
    op.drop_constraint("fk_users_created_by", "users", type_="foreignkey")
    op.drop_constraint("fk_users_kindergarten", "users", type_="foreignkey")
    op.drop_index("ix_users_kindergarten_active", table_name="users")
    op.drop_index("ix_users_kindergarten_phone", table_name="users")
    op.drop_constraint("uq_users_kindergarten_username", "users", type_="unique")
    op.create_unique_constraint(
        "uq_users_kindergarten_username",
        "users",
        ["kindergarten_id", "username"],
    )
    op.alter_column(
        "users",
        "phone_e164",
        new_column_name="phone",
        existing_type=sa.String(32),
        existing_nullable=True,
    )
    op.create_unique_constraint(
        "uq_users_kindergarten_phone", "users", ["kindergarten_id", "phone"]
    )
    op.drop_column("users", "username_normalized")
    op.drop_column("users", "password_changed_at")
    op.drop_column("users", "last_login_at")
    # 恢复 0001 的长度：username/display_name VARCHAR(128)。
    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(120),
        type_=sa.String(128),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "display_name",
        existing_type=sa.String(120),
        type_=sa.String(128),
        existing_nullable=False,
    )

    # --- user_roles / roles: 简化降级，清空后恢复旧结构 -------------------------
    op.drop_table("user_roles")
    op.drop_table("roles")

    # 在重建旧 roles/user_roles 前，先把仍存在的 uuid 列恢复为 varchar(36)，
    # 使旧外键约束可正常创建。
    op.execute(
        sa.text("ALTER TABLE kindergartens ALTER COLUMN id TYPE varchar(36) USING id::varchar(36)")
    )
    op.execute(sa.text("ALTER TABLE users ALTER COLUMN id TYPE varchar(36) USING id::varchar(36)"))
    op.execute(
        sa.text(
            "ALTER TABLE users ALTER COLUMN kindergarten_id TYPE varchar(36) USING kindergarten_id::varchar(36)"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE users ALTER COLUMN created_by TYPE varchar(36) USING created_by::varchar(36)"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE users ALTER COLUMN updated_by TYPE varchar(36) USING updated_by::varchar(36)"
        )
    )
    op.execute(
        sa.text("ALTER TABLE refresh_tokens ALTER COLUMN id TYPE varchar(36) USING id::varchar(36)")
    )
    op.execute(
        sa.text(
            "ALTER TABLE refresh_tokens ALTER COLUMN kindergarten_id TYPE varchar(36) USING kindergarten_id::varchar(36)"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE refresh_tokens ALTER COLUMN user_id TYPE varchar(36) USING user_id::varchar(36)"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE refresh_tokens ALTER COLUMN family_id TYPE varchar(36) USING family_id::varchar(36)"
        )
    )
    op.execute(
        sa.text("ALTER TABLE audit_events ALTER COLUMN id TYPE varchar(36) USING id::varchar(36)")
    )
    op.execute(
        sa.text(
            "ALTER TABLE audit_events ALTER COLUMN kindergarten_id TYPE varchar(36) USING kindergarten_id::varchar(36)"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE audit_events ALTER COLUMN actor_user_id TYPE varchar(36) USING actor_user_id::varchar(36)"
        )
    )
    # audit_events.resource_id：0001 要求 NOT NULL，但 upgrade 阶段已把
    # 不可转换为 UUID 的旧值（例如 username 字符串）置为 NULL。downgrade
    # 必须先为这些 NULL 行填充可逆占位值，再恢复 NOT NULL，否则会因
    # NotNullViolation 失败。占位使用 '00000000-0000-0000-0000-000000000000'
    # 零值 UUID，并在 resource_type 标注 'legacy_null' 以便后续审计追溯。
    op.execute(
        sa.text(
            """
            UPDATE audit_events
            SET resource_id = '00000000-0000-0000-0000-000000000000'::uuid,
                resource_type = COALESCE(resource_type, 'legacy_null')
            WHERE resource_id IS NULL
            """
        )
    )
    op.alter_column(
        "audit_events",
        "resource_id",
        existing_type=_UUID,
        type_=sa.String(36),
        existing_nullable=True,
        nullable=False,
        postgresql_using="resource_id::varchar(36)",
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("kindergarten_id", sa.String(36), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_roles_kindergarten_id"),
        sa.UniqueConstraint("kindergarten_id", "code", name="uq_roles_kindergarten_code"),
    )
    op.create_table(
        "user_roles",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("kindergarten_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("role_id", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "kindergarten_id",
            "user_id",
            "role_id",
            name="uq_user_roles_kindergarten",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
            name="fk_user_roles_user",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "role_id"],
            ["roles.kindergarten_id", "roles.id"],
            name="fk_user_roles_role",
        ),
    )

    # 重建 0004 创建的 FK，使 0004 的 downgrade 能正常删除它。
    op.create_foreign_key(
        "fk_refresh_tokens_user",
        "refresh_tokens",
        "users",
        ["kindergarten_id", "user_id"],
        ["kindergarten_id", "id"],
    )

    # --- kindergartens: 撤销新增字段与约束 -------------------------------------
    op.drop_constraint("ck_kindergartens_timezone", "kindergartens", type_="check")
    op.drop_column("kindergartens", "is_active")
    # 恢复 0001 的长度：name VARCHAR(255)。
    op.alter_column(
        "kindergartens",
        "name",
        existing_type=sa.String(200),
        type_=sa.String(255),
        existing_nullable=False,
    )
