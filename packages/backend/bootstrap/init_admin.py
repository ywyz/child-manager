"""首位管理员的部署控制台初始化与双人核验激活。"""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import psycopg

from packages.backend.audit.repository import AuditRepository
from packages.backend.identity.identifiers import normalize_username
from packages.backend.identity.repository import IdentityRepository
from packages.backend.identity.secret_tokens import SecretPurpose, issue_secret
from packages.contracts.audit import IdentityAuditEventCode


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def start_initialization(
    *,
    database_url: str,
    kindergarten_name: str,
    username: str,
    display_name: str,
    owner_reference: str,
    operator_reference: str,
) -> tuple[UUID, str] | None:
    """创建待登记管理员，并只返回一次初始化秘密。"""

    normalized = normalize_username(username)
    if not owner_reference.strip() or not operator_reference.strip():
        raise ValueError("必须预登记园所负责人和独立运维/安全责任人。")
    if owner_reference.strip() == operator_reference.strip():
        raise ValueError("园所负责人和独立运维/安全责任人必须是不同人员。")
    material = issue_secret(SecretPurpose.BOOTSTRAP)
    with psycopg.connect(_native_url(database_url)) as connection, connection.transaction():
        connection.execute("SELECT pg_advisory_xact_lock(1128812109)")
        if connection.execute("SELECT 1 FROM kindergartens LIMIT 1 FOR UPDATE").fetchone():
            return None
        now = datetime.now(UTC)
        kindergarten_id = uuid7()
        user_id = uuid7()
        bootstrap_id = uuid7()
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s,%s)",
            (kindergarten_id, kindergarten_name.strip()),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             webauthn_user_handle, status, created_by, updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,'pending_registration',%s,%s)""",
            (
                user_id,
                kindergarten_id,
                normalized,
                normalized,
                display_name.strip(),
                uuid7().bytes + uuid7().bytes,
                user_id,
                user_id,
            ),
        )
        role = connection.execute("SELECT id FROM roles WHERE code='admin'").fetchone()
        if role is None:
            raise RuntimeError("管理员角色种子缺失")
        connection.execute(
            """INSERT INTO user_roles
            (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (kindergarten_id, user_id, role[0], user_id, now),
        )
        connection.execute(
            """INSERT INTO bootstrap_initializations
            (id, kindergarten_id, user_id, token_digest, owner_reference,
             operator_reference, expires_at, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                bootstrap_id,
                kindergarten_id,
                user_id,
                material.record.digest,
                owner_reference.strip(),
                operator_reference.strip(),
                now + timedelta(minutes=15),
                now,
                now,
            ),
        )
        AuditRepository(connection, kindergarten_id).append(
            event_code=IdentityAuditEventCode.BOOTSTRAP_STARTED,
            actor_user_id=user_id,
            actor_role_codes=["admin"],
            resource_type="bootstrap_initialization",
            resource_id=bootstrap_id,
            outcome="success",
        )
        return bootstrap_id, material.secret


def activate_initialization(
    *, database_url: str, bootstrap_id: UUID, owner_reference: str, operator_reference: str
) -> bool:
    """仅在通行密钥已登记并完成两位预登记人员核验后激活。"""

    with psycopg.connect(_native_url(database_url)) as connection, connection.transaction():
        row = connection.execute(
            """SELECT kindergarten_id, user_id, owner_reference, operator_reference,
            registered_credential_id, activated_at FROM bootstrap_initializations
            WHERE id=%s FOR UPDATE""",
            (bootstrap_id,),
        ).fetchone()
        if (
            row is None
            or owner_reference.strip() != row[2]
            or operator_reference.strip() != row[3]
            or row[2] == row[3]
        ):
            raise ValueError("必须由预登记园所负责人和独立运维/安全责任人双人核验。")
        if row[5] is not None:
            return True
        if row[4] is None:
            raise ValueError("请先登记通行密钥，再由园所负责人和独立运维完成核验。")
        kindergarten_id, user_id = row[0], row[1]
        now = datetime.now(UTC)
        connection.execute(
            """UPDATE users SET status='active', activated_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (now, kindergarten_id, user_id),
        )
        connection.execute(
            "UPDATE bootstrap_initializations SET activated_at=%s, updated_at=now() WHERE id=%s",
            (now, bootstrap_id),
        )
        for approver_kind, reference in (
            ("owner", owner_reference.strip()),
            ("operator", operator_reference.strip()),
        ):
            connection.execute(
                """INSERT INTO identity_verification_approvals
                (id, kindergarten_id, context_type, context_id, user_id, approver_kind,
                 approver_reference, decision, decided_at)
                VALUES (%s,%s,'bootstrap',%s,%s,%s,%s,'approved',%s)""",
                (
                    uuid7(),
                    kindergarten_id,
                    bootstrap_id,
                    user_id,
                    approver_kind,
                    reference,
                    now,
                ),
            )
        AuditRepository(connection, kindergarten_id).append(
            event_code=IdentityAuditEventCode.BOOTSTRAP_ACTIVATED,
            actor_user_id=user_id,
            actor_role_codes=["admin"],
            resource_type="bootstrap_initialization",
            resource_id=bootstrap_id,
            outcome="success",
        )
        return True


def recover_last_admin(
    *,
    database_url: str,
    recovery_request_id: UUID,
    owner_reference: str,
    operator_reference: str,
) -> tuple[str, datetime]:
    """由两位预登记责任人批准最后管理员恢复，并只返回一次登记秘密。"""

    owner = owner_reference.strip()
    operator = operator_reference.strip()
    if not owner or not operator or owner == operator:
        raise ValueError("必须由不同的园所负责人和独立运维/安全责任人双人核验。")
    material = issue_secret(SecretPurpose.RECOVERY_ENROLLMENT)
    with psycopg.connect(_native_url(database_url)) as connection, connection.transaction():
        target = connection.execute(
            """SELECT kindergarten_id, user_id FROM account_recovery_requests
            WHERE id=%s""",
            (recovery_request_id,),
        ).fetchone()
        if target is None:
            raise ValueError("恢复申请无效或状态已变化。")
        kindergarten_id, user_id = target
        repository = IdentityRepository(connection, kindergarten_id)
        try:
            is_last_active_admin = not repository.can_deactivate(user_id)
        except LookupError:
            is_last_active_admin = False
        if not is_last_active_admin:
            raise ValueError("目标不是当前唯一有效管理员，不能使用最后管理员恢复。")

        now = datetime.now(UTC)
        request = connection.execute(
            """SELECT rr.status, rr.expires_at, rr.enrollment_token_hash,
                      rc.consumed_at, rc.revoked_at
            FROM account_recovery_requests rr
            JOIN recovery_codes rc
              ON rc.kindergarten_id=rr.kindergarten_id AND rc.id=rr.recovery_code_id
            WHERE rr.kindergarten_id=%s AND rr.user_id=%s AND rr.id=%s
            FOR UPDATE OF rr, rc""",
            (kindergarten_id, user_id, recovery_request_id),
        ).fetchone()
        if (
            request is None
            or request[0] != "pending_verification"
            or request[1] <= now
            or request[2] is not None
            or request[3] is None
            or request[4] is not None
        ):
            raise ValueError("恢复申请无效或状态已变化。")

        references = connection.execute(
            """SELECT owner_reference, operator_reference
            FROM bootstrap_initializations WHERE kindergarten_id=%s
            ORDER BY created_at, id LIMIT 1 FOR SHARE""",
            (kindergarten_id,),
        ).fetchone()
        if (
            references is None
            or references[0] == references[1]
            or owner != references[0]
            or operator != references[1]
        ):
            raise ValueError("必须由预登记园所负责人和独立运维/安全责任人双人核验。")
        if connection.execute(
            """SELECT 1 FROM identity_verification_approvals
            WHERE kindergarten_id=%s AND context_type='recovery' AND context_id=%s
            LIMIT 1""",
            (kindergarten_id, recovery_request_id),
        ).fetchone():
            raise ValueError("恢复申请无效或状态已变化。")

        expires_at = now + timedelta(minutes=15)
        for approver_kind, reference in (("owner", owner), ("operator", operator)):
            connection.execute(
                """INSERT INTO identity_verification_approvals
                (id, kindergarten_id, context_type, context_id, user_id, approver_kind,
                 approver_reference, decision, decided_at)
                VALUES (%s,%s,'recovery',%s,%s,%s,%s,'approved',%s)""",
                (
                    uuid7(),
                    kindergarten_id,
                    recovery_request_id,
                    user_id,
                    approver_kind,
                    reference,
                    now,
                ),
            )
        updated = connection.execute(
            """UPDATE account_recovery_requests
            SET status='approved', approved_at=%s, enrollment_token_hash=%s,
                enrollment_expires_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s AND id=%s
              AND status='pending_verification' AND expires_at>%s
              AND enrollment_token_hash IS NULL""",
            (
                now,
                material.record.digest,
                expires_at,
                kindergarten_id,
                user_id,
                recovery_request_id,
                now,
            ),
        )
        if updated.rowcount != 1:
            raise ValueError("恢复申请无效或状态已变化。")
        AuditRepository(connection, kindergarten_id).append(
            event_code=IdentityAuditEventCode.RECOVERY_APPROVED,
            actor_user_id=user_id,
            actor_role_codes=["admin"],
            resource_type="account_recovery_request",
            resource_id=recovery_request_id,
            outcome="success",
        )
    return material.secret, expires_at


def migrate_passkeys(*, database_url: str) -> list[tuple[str, str]]:
    """为尚无通行密钥的迁移账号轮换并签发一次性登记凭据。"""

    issued: list[tuple[str, str]] = []
    with psycopg.connect(_native_url(database_url)) as connection, connection.transaction():
        connection.execute("SELECT pg_advisory_xact_lock(1128812110)")
        users = connection.execute(
            """SELECT u.id, u.kindergarten_id, u.username
            FROM users u WHERE u.status='pending_registration' AND NOT EXISTS (
                SELECT 1 FROM webauthn_credentials c
                WHERE c.kindergarten_id=u.kindergarten_id AND c.user_id=u.id
                AND c.revoked_at IS NULL)
            ORDER BY u.kindergarten_id, u.created_at, u.id FOR UPDATE"""
        ).fetchall()
        for user_id, kindergarten_id, username in users:
            material = issue_secret(SecretPurpose.INVITATION)
            connection.execute(
                """UPDATE account_invitations SET revoked_at=COALESCE(revoked_at, now()),
                updated_at=now() WHERE kindergarten_id=%s AND user_id=%s
                AND consumed_at IS NULL AND revoked_at IS NULL""",
                (kindergarten_id, user_id),
            )
            invitation_id = uuid7()
            connection.execute(
                """INSERT INTO account_invitations
                (id, kindergarten_id, user_id, issued_by, token_hash, expires_at)
                VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    invitation_id,
                    kindergarten_id,
                    user_id,
                    user_id,
                    material.record.digest,
                    datetime.now(UTC) + timedelta(hours=24),
                ),
            )
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.INVITATION_ISSUED,
                actor_user_id=user_id,
                actor_role_codes=[],
                resource_type="account_invitation",
                resource_id=invitation_id,
                outcome="success",
                metadata={"reason": "password_migration"},
            )
            issued.append((str(username), material.secret))
    return issued
