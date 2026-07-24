"""所有查询和写入都显式绑定 ``kindergarten_id`` 的身份 Repository。"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

import psycopg
from psycopg.types.json import Jsonb


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: UUID
    kindergarten_id: UUID
    username: str
    username_normalized: str
    phone_e164: str | None
    display_name: str
    webauthn_user_handle: bytes
    status: str
    activated_at: datetime | None
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    backup_auth_version: int

    @property
    def is_active(self) -> bool:
        return self.status == "active"


@dataclass(frozen=True, slots=True)
class RefreshRecord:
    id: UUID
    kindergarten_id: UUID
    user_id: UUID
    token_family_id: UUID
    issued_at: datetime
    expires_at: datetime
    last_used_at: datetime | None
    last_reauthenticated_at: datetime | None
    authentication_method: str
    webauthn_verified_at: datetime | None
    backup_verified_at: datetime | None
    backup_reauthenticated_at: datetime | None
    backup_auth_version: int | None
    revoked_at: datetime | None
    replaced_by_id: UUID | None


@dataclass(frozen=True, slots=True)
class CredentialRecord:
    id: UUID
    kindergarten_id: UUID
    user_id: UUID
    credential_id: bytes
    public_key_cose: bytes
    sign_count: int
    transports: list[str]
    aaguid: UUID | None
    backup_eligible: bool
    backup_state: bool
    label: str
    created_via: str
    created_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None


@dataclass(frozen=True, slots=True)
class ChallengeRecord:
    id: UUID
    kindergarten_id: UUID | None
    user_id: UUID | None
    purpose: str
    challenge_hash: str
    authorization_context: str | None
    expected_rp_id: str
    expected_origin: str
    requires_user_verification: bool
    expires_at: datetime
    consumed_at: datetime | None


@dataclass(frozen=True, slots=True)
class InvitationRecord:
    id: UUID
    kindergarten_id: UUID
    user_id: UUID
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None
    revoked_at: datetime | None


@dataclass(frozen=True, slots=True)
class RecoveryRequestRecord:
    id: UUID
    kindergarten_id: UUID
    user_id: UUID
    status: str
    requested_at: datetime
    expires_at: datetime
    approved_at: datetime | None


@dataclass(frozen=True, slots=True)
class BackupCredentialRecord:
    id: UUID
    kindergarten_id: UUID
    user_id: UUID
    status: str
    password_hash: str | None
    password_changed_at: datetime | None
    totp_ciphertext: bytes | None
    totp_nonce: bytes | None
    totp_key_id: str | None
    totp_envelope_version: int | None
    totp_algorithm: str
    totp_digits: int
    totp_period_seconds: int
    last_accepted_counter: int | None
    enabled_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class BackupEnrollmentRecord:
    id: UUID
    kindergarten_id: UUID
    user_id: UUID
    session_token_id: UUID
    totp_ciphertext: bytes
    totp_nonce: bytes
    totp_key_id: str
    totp_envelope_version: int
    expires_at: datetime
    consumed_at: datetime | None
    invalidated_at: datetime | None
    invalidation_reason: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class BackupRevocationResult:
    backup_auth_version: int
    sessions_revoked: int


@dataclass(frozen=True, slots=True)
class BackupSecurityEventRecord:
    event_code: str
    occurred_at: datetime
    authentication_method: str | None
    client_hint: str | None


_USER_COLUMNS = """id, kindergarten_id, username, username_normalized, phone_e164,
display_name, webauthn_user_handle, status, activated_at, last_login_at, created_at, updated_at,
backup_auth_version"""
_REFRESH_COLUMNS = """id, kindergarten_id, user_id, token_family_id, issued_at, expires_at,
last_used_at, last_reauthenticated_at, authentication_method, webauthn_verified_at,
backup_verified_at, backup_reauthenticated_at, backup_auth_version, revoked_at, replaced_by_id"""
_CREDENTIAL_COLUMNS = """id, kindergarten_id, user_id, credential_id, public_key_cose,
sign_count, transports, aaguid, backup_eligible, backup_state, label, created_via,
created_at, last_used_at, revoked_at"""
_CHALLENGE_COLUMNS = """id, kindergarten_id, user_id, purpose, challenge_hash,
authorization_context, expected_rp_id, expected_origin, requires_user_verification,
expires_at, consumed_at"""
_BACKUP_CREDENTIAL_COLUMNS = """id, kindergarten_id, user_id, status, password_hash,
password_changed_at, totp_ciphertext, totp_nonce, totp_key_id, totp_envelope_version,
totp_algorithm, totp_digits, totp_period_seconds, last_accepted_counter, enabled_at,
revoked_at, created_at, updated_at"""
_BACKUP_ENROLLMENT_COLUMNS = """id, kindergarten_id, user_id, session_token_id,
totp_ciphertext, totp_nonce, totp_key_id, totp_envelope_version, expires_at, consumed_at,
invalidated_at, invalidation_reason, created_at, updated_at"""


def _user(row: tuple[object, ...] | None) -> UserRecord | None:
    return UserRecord(*row) if row is not None else None  # type: ignore[arg-type]


def _credential(row: tuple[object, ...] | None) -> CredentialRecord | None:
    return CredentialRecord(*row) if row is not None else None  # type: ignore[arg-type]


def _backup_credential(row: tuple[object, ...] | None) -> BackupCredentialRecord | None:
    return BackupCredentialRecord(*row) if row is not None else None  # type: ignore[arg-type]


def _backup_enrollment(row: tuple[object, ...] | None) -> BackupEnrollmentRecord | None:
    return BackupEnrollmentRecord(*row) if row is not None else None  # type: ignore[arg-type]


class IdentityRepository:
    def __init__(
        self,
        connection: psycopg.Connection[tuple[object, ...]],
        kindergarten_id: UUID | None,
    ) -> None:
        self.connection = connection
        self.kindergarten_id = kindergarten_id

    def _lock_admin_membership(self) -> None:
        self.connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (str(self.kindergarten_id),),
        )

    # 所有会话写路径保持 user -> family -> row 的锁序。
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
            WHERE u.kindergarten_id=%s AND u.status='active' AND r.code='admin'""",
            (self.kindergarten_id,),
        ).fetchone()
        return row[0] if row and isinstance(row[0], int) else 0

    def can_deactivate(self, user_id: UUID) -> bool:
        self._lock_admin_membership()
        row = self.connection.execute(
            """SELECT u.status='active', EXISTS(
                SELECT 1 FROM user_roles ur JOIN roles r ON r.id=ur.role_id
                WHERE ur.kindergarten_id=u.kindergarten_id AND ur.user_id=u.id
                AND r.code='admin')
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
        rows = self.connection.execute(
            """SELECT r.code FROM user_roles ur JOIN roles r ON r.id=ur.role_id
            WHERE ur.kindergarten_id=%s AND ur.user_id=%s ORDER BY r.code""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        return [str(row[0]) for row in rows]

    def credential_count(self, user_id: UUID) -> int:
        row = self.connection.execute(
            """SELECT count(*) FROM webauthn_credentials
            WHERE kindergarten_id=%s AND user_id=%s AND revoked_at IS NULL""",
            (self.kindergarten_id, user_id),
        ).fetchone()
        return row[0] if row and isinstance(row[0], int) else 0

    def create_user(
        self,
        *,
        username: str,
        username_normalized: str,
        phone_e164: str | None,
        display_name: str,
        role_codes: list[str],
        actor_user_id: UUID,
    ) -> UserRecord:
        user_id = uuid7()
        self.connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, phone_e164, display_name,
             webauthn_user_handle, status, created_by, updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'pending_registration',%s,%s)""",
            (
                user_id,
                self.kindergarten_id,
                username,
                username_normalized,
                phone_e164,
                display_name,
                uuid7().bytes + uuid7().bytes,
                actor_user_id,
                actor_user_id,
            ),
        )
        self.set_roles(user_id, role_codes, actor_user_id=actor_user_id, protect_last=False)
        record = self.get_user(user_id)
        assert record is not None
        return record

    def list_users(self, *, page: int, page_size: int) -> tuple[list[UserRecord], int]:
        total = self.connection.execute(
            "SELECT count(*) FROM users WHERE kindergarten_id=%s", (self.kindergarten_id,)
        ).fetchone()
        rows = self.connection.execute(
            f"""SELECT {_USER_COLUMNS} FROM users WHERE kindergarten_id=%s
            ORDER BY created_at, id LIMIT %s OFFSET %s""",
            (self.kindergarten_id, page_size, (page - 1) * page_size),
        ).fetchall()
        return ([UserRecord(*row) for row in rows], int(total[0]) if total else 0)  # type: ignore[arg-type]

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
                username_normalized or current.username_normalized,
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
        if "teacher" in current and "teacher" not in requested:
            self.connection.execute(
                """DELETE FROM class_teachers
                WHERE kindergarten_id=%s AND user_id=%s""",
                (self.kindergarten_id, user_id),
            )
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

    def set_status(self, user_id: UUID, status: str, *, actor_user_id: UUID) -> UserRecord:
        self.lock_user_sessions(user_id)
        if status != "active" and not self.can_deactivate(user_id):
            raise ValueError("不能停用最后一个有效管理员")
        row = self.connection.execute(
            """UPDATE users SET status=%s, activated_at=CASE WHEN %s='active'
            THEN COALESCE(activated_at, now()) ELSE activated_at END,
            updated_by=%s, updated_at=now() WHERE kindergarten_id=%s AND id=%s
            RETURNING """
            + _USER_COLUMNS,
            (status, status, actor_user_id, self.kindergarten_id, user_id),
        ).fetchone()
        record = _user(row)
        if record is None:
            raise LookupError("账号不存在")
        return record

    def create_refresh(
        self,
        *,
        user_id: UUID,
        family_id: UUID,
        token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
        last_reauthenticated_at: datetime | None = None,
        client_label: str | None = None,
        authentication_method: str = "webauthn",
        webauthn_verified_at: datetime | None = None,
        backup_verified_at: datetime | None = None,
        backup_reauthenticated_at: datetime | None = None,
        backup_auth_version: int | None = None,
    ) -> UUID:
        self.lock_user_sessions(user_id)
        if (
            authentication_method in {"webauthn", "restricted_enrollment"}
            and webauthn_verified_at is None
        ):
            webauthn_verified_at = last_reauthenticated_at or issued_at
        token_id = uuid7()
        self.connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at,
             last_reauthenticated_at, client_label, authentication_method,
             webauthn_verified_at, backup_verified_at, backup_reauthenticated_at,
             backup_auth_version)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                token_id,
                self.kindergarten_id,
                user_id,
                family_id,
                token_hash,
                issued_at,
                expires_at,
                last_reauthenticated_at,
                client_label,
                authentication_method,
                webauthn_verified_at,
                backup_verified_at,
                backup_reauthenticated_at,
                backup_auth_version,
            ),
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
            f"""SELECT {_REFRESH_COLUMNS} FROM refresh_tokens
            WHERE kindergarten_id=%s AND token_hash=%s{suffix}""",
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

    def get_family_session(self, user_id: UUID, family_id: UUID) -> RefreshRecord | None:
        row = self.connection.execute(
            f"""SELECT {_REFRESH_COLUMNS} FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s AND token_family_id=%s
            ORDER BY issued_at DESC LIMIT 1""",
            (self.kindergarten_id, user_id, family_id),
        ).fetchone()
        return RefreshRecord(*row) if row else None  # type: ignore[arg-type]

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
            last_reauthenticated_at=old.last_reauthenticated_at,
            authentication_method=old.authentication_method,
            webauthn_verified_at=old.webauthn_verified_at,
            backup_verified_at=old.backup_verified_at,
            backup_reauthenticated_at=old.backup_reauthenticated_at,
            backup_auth_version=old.backup_auth_version,
        )
        self.connection.execute(
            """UPDATE refresh_tokens SET revoked_at=%s, revoke_reason='rotated',
            replaced_by_id=%s, last_used_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (now, new_id, now, self.kindergarten_id, old.id),
        )
        return new_id

    def revoke_family(self, family_id: UUID, *, reason: str) -> int:
        row = self.connection.execute(
            """SELECT user_id FROM refresh_tokens WHERE kindergarten_id=%s
            AND token_family_id=%s ORDER BY id LIMIT 1""",
            (self.kindergarten_id, family_id),
        ).fetchone()
        if row is None:
            return 0
        self.lock_user_sessions(row[0])  # type: ignore[arg-type]
        self._lock_refresh_family(family_id)
        active = self.connection.execute(
            """SELECT count(*) FROM refresh_tokens WHERE kindergarten_id=%s
            AND token_family_id=%s AND revoked_at IS NULL""",
            (self.kindergarten_id, family_id),
        ).fetchone()
        self.connection.execute(
            """UPDATE refresh_tokens SET revoked_at=COALESCE(revoked_at, now()),
            revoke_reason=%s, updated_at=now() WHERE kindergarten_id=%s
            AND token_family_id=%s""",
            (reason, self.kindergarten_id, family_id),
        )
        return active[0] if active and isinstance(active[0], int) else 0

    def revoke_user_sessions(self, user_id: UUID, *, reason: str) -> int:
        self.lock_user_sessions(user_id)
        families = self.connection.execute(
            """SELECT DISTINCT token_family_id FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s ORDER BY token_family_id""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        for (family_id,) in families:
            self._lock_refresh_family(family_id)  # type: ignore[arg-type]
        active = self.connection.execute(
            """SELECT count(*) FROM refresh_tokens WHERE kindergarten_id=%s
            AND user_id=%s AND revoked_at IS NULL""",
            (self.kindergarten_id, user_id),
        ).fetchone()
        self.connection.execute(
            """UPDATE refresh_tokens SET revoked_at=COALESCE(revoked_at, now()),
            revoke_reason=%s, updated_at=now() WHERE kindergarten_id=%s AND user_id=%s""",
            (reason, self.kindergarten_id, user_id),
        )
        return active[0] if active and isinstance(active[0], int) else 0

    def list_sessions(self, user_id: UUID) -> list[RefreshRecord]:
        rows = self.connection.execute(
            f"""SELECT DISTINCT ON (token_family_id) {_REFRESH_COLUMNS}
            FROM refresh_tokens WHERE kindergarten_id=%s AND user_id=%s
            ORDER BY token_family_id, issued_at DESC""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        return [RefreshRecord(*row) for row in rows]  # type: ignore[arg-type]

    def revoke_session(self, user_id: UUID, family_id: UUID, *, reason: str) -> int:
        row = self.connection.execute(
            """SELECT EXISTS(SELECT 1 FROM refresh_tokens WHERE kindergarten_id=%s
            AND user_id=%s AND token_family_id=%s)""",
            (self.kindergarten_id, user_id, family_id),
        ).fetchone()
        return self.revoke_family(family_id, reason=reason) if row and row[0] else 0

    def get_backup_credential(
        self, user_id: UUID, *, lock: bool = False
    ) -> BackupCredentialRecord | None:
        suffix = " FOR UPDATE" if lock else ""
        row = self.connection.execute(
            f"""SELECT {_BACKUP_CREDENTIAL_COLUMNS} FROM backup_auth_credentials
            WHERE kindergarten_id=%s AND user_id=%s{suffix}""",
            (self.kindergarten_id, user_id),
        ).fetchone()
        return _backup_credential(row)

    def has_enabled_backup_auth(self, user_id: UUID) -> bool:
        row = self.connection.execute(
            """SELECT EXISTS(SELECT 1 FROM backup_auth_credentials
            WHERE kindergarten_id=%s AND user_id=%s AND status='enabled')""",
            (self.kindergarten_id, user_id),
        ).fetchone()
        return bool(row and row[0])

    def start_backup_enrollment(
        self,
        *,
        user_id: UUID,
        session_token_id: UUID,
        totp_ciphertext: bytes,
        totp_nonce: bytes,
        totp_key_id: str,
        totp_envelope_version: int,
        expires_at: datetime,
    ) -> BackupEnrollmentRecord:
        self.lock_user_sessions(user_id)
        self.connection.execute(
            """UPDATE backup_auth_enrollments
            SET invalidated_at=now(), invalidation_reason='superseded', updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s
              AND consumed_at IS NULL AND invalidated_at IS NULL""",
            (self.kindergarten_id, user_id),
        )
        enrollment_id = uuid7()
        row = self.connection.execute(
            f"""INSERT INTO backup_auth_enrollments
            (id, kindergarten_id, user_id, session_token_id, totp_ciphertext, totp_nonce,
             totp_key_id, totp_envelope_version, expires_at)
            SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s
            WHERE EXISTS(
                SELECT 1 FROM refresh_tokens
                WHERE kindergarten_id=%s AND user_id=%s AND id=%s
                  AND revoked_at IS NULL AND expires_at>now()
            )
            RETURNING {_BACKUP_ENROLLMENT_COLUMNS}""",
            (
                enrollment_id,
                self.kindergarten_id,
                user_id,
                session_token_id,
                totp_ciphertext,
                totp_nonce,
                totp_key_id,
                totp_envelope_version,
                expires_at,
                self.kindergarten_id,
                user_id,
                session_token_id,
            ),
        ).fetchone()
        record = _backup_enrollment(row)
        if record is None:
            raise ValueError("当前会话不能建立备用登录绑定")
        return record

    def consume_backup_enrollment(
        self,
        enrollment_id: UUID,
        *,
        user_id: UUID,
        session_token_id: UUID,
        now: datetime,
    ) -> BackupEnrollmentRecord | None:
        row = self.connection.execute(
            f"""UPDATE backup_auth_enrollments AS enrollment
            SET consumed_at=%s, updated_at=now()
            WHERE enrollment.kindergarten_id=%s
              AND enrollment.user_id=%s
              AND enrollment.id=%s
              AND enrollment.session_token_id=%s
              AND enrollment.consumed_at IS NULL
              AND enrollment.invalidated_at IS NULL
              AND enrollment.expires_at>%s
              AND EXISTS(
                  SELECT 1 FROM refresh_tokens AS session
                  WHERE session.kindergarten_id=enrollment.kindergarten_id
                    AND session.user_id=enrollment.user_id
                    AND session.id=enrollment.session_token_id
                    AND session.revoked_at IS NULL
                    AND session.expires_at>%s
              )
            RETURNING {_BACKUP_ENROLLMENT_COLUMNS}""",
            (
                now,
                self.kindergarten_id,
                user_id,
                enrollment_id,
                session_token_id,
                now,
                now,
            ),
        ).fetchone()
        return _backup_enrollment(row)

    def save_backup_credential(
        self,
        *,
        credential_id: UUID,
        user_id: UUID,
        password_hash: str,
        password_changed_at: datetime,
        totp_ciphertext: bytes,
        totp_nonce: bytes,
        totp_key_id: str,
        totp_envelope_version: int,
        enabled_at: datetime,
        last_accepted_counter: int,
    ) -> BackupCredentialRecord:
        row = self.connection.execute(
            f"""INSERT INTO backup_auth_credentials
            (id, kindergarten_id, user_id, status, password_hash, password_changed_at,
             totp_ciphertext, totp_nonce, totp_key_id, totp_envelope_version,
             last_accepted_counter, enabled_at)
            VALUES (%s,%s,%s,'enabled',%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (kindergarten_id, user_id) DO UPDATE SET
              id=EXCLUDED.id,
              status='enabled',
              password_hash=EXCLUDED.password_hash,
              password_changed_at=EXCLUDED.password_changed_at,
              totp_ciphertext=EXCLUDED.totp_ciphertext,
              totp_nonce=EXCLUDED.totp_nonce,
              totp_key_id=EXCLUDED.totp_key_id,
              totp_envelope_version=EXCLUDED.totp_envelope_version,
              last_accepted_counter=EXCLUDED.last_accepted_counter,
              enabled_at=EXCLUDED.enabled_at,
              revoked_at=NULL,
              updated_at=now()
            RETURNING {_BACKUP_CREDENTIAL_COLUMNS}""",
            (
                credential_id,
                self.kindergarten_id,
                user_id,
                password_hash,
                password_changed_at,
                totp_ciphertext,
                totp_nonce,
                totp_key_id,
                totp_envelope_version,
                last_accepted_counter,
                enabled_at,
            ),
        ).fetchone()
        record = _backup_credential(row)
        if record is None:
            raise LookupError("备用登录凭据写入失败")
        return record

    def accept_totp_counter(self, credential_id: UUID, counter: int) -> bool:
        row = self.connection.execute(
            """UPDATE backup_auth_credentials
            SET last_accepted_counter=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND status='enabled'
              AND (last_accepted_counter IS NULL OR last_accepted_counter < %s)
            RETURNING id""",
            (counter, self.kindergarten_id, credential_id, counter),
        ).fetchone()
        return row is not None

    def revoke_backup_auth(self, user_id: UUID, *, reason: str) -> BackupRevocationResult:
        self.lock_user_sessions(user_id)
        self.connection.execute(
            """UPDATE backup_auth_credentials
            SET status='revoked',
                password_hash=NULL,
                totp_ciphertext=NULL,
                totp_nonce=NULL,
                totp_key_id=NULL,
                totp_envelope_version=NULL,
                last_accepted_counter=NULL,
                revoked_at=COALESCE(revoked_at, now()),
                updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s""",
            (self.kindergarten_id, user_id),
        )
        self.connection.execute(
            """UPDATE backup_auth_enrollments
            SET invalidated_at=now(), invalidation_reason='factor_changed', updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s
              AND consumed_at IS NULL AND invalidated_at IS NULL""",
            (self.kindergarten_id, user_id),
        )
        version_row = self.connection.execute(
            """UPDATE users SET backup_auth_version=backup_auth_version+1, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s
            RETURNING backup_auth_version""",
            (self.kindergarten_id, user_id),
        ).fetchone()
        if version_row is None or not isinstance(version_row[0], int):
            raise LookupError("账号不存在")
        active = self.connection.execute(
            """SELECT count(*) FROM refresh_tokens
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method IN ('password_totp','restricted_enrollment')
              AND revoked_at IS NULL""",
            (self.kindergarten_id, user_id),
        ).fetchone()
        self.connection.execute(
            """UPDATE refresh_tokens
            SET revoked_at=COALESCE(revoked_at, now()), revoke_reason=%s, updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s
              AND authentication_method IN ('password_totp','restricted_enrollment')""",
            (reason, self.kindergarten_id, user_id),
        )
        sessions_revoked = active[0] if active and isinstance(active[0], int) else 0
        return BackupRevocationResult(version_row[0], sessions_revoked)

    def recalculate_backup_enrollment_gate(self, user_id: UUID) -> bool:
        row = self.connection.execute(
            """SELECT EXISTS(
                SELECT 1 FROM user_roles ur JOIN roles r ON r.id=ur.role_id
                WHERE ur.kindergarten_id=u.kindergarten_id
                  AND ur.user_id=u.id AND r.code='admin'
            ), EXISTS(
                SELECT 1 FROM backup_auth_credentials bac
                WHERE bac.kindergarten_id=u.kindergarten_id
                  AND bac.user_id=u.id AND bac.status='enabled'
            ), u.backup_auth_version
            FROM users u WHERE u.kindergarten_id=%s AND u.id=%s FOR UPDATE""",
            (self.kindergarten_id, user_id),
        ).fetchone()
        if row is None:
            raise LookupError("账号不存在")
        restricted = bool(row[0]) and not bool(row[1])
        if restricted:
            self.connection.execute(
                """UPDATE refresh_tokens
                SET authentication_method='restricted_enrollment',
                    backup_auth_version=%s,
                    backup_verified_at=NULL,
                    backup_reauthenticated_at=NULL,
                    updated_at=now()
                WHERE kindergarten_id=%s AND user_id=%s
                  AND authentication_method='webauthn'
                  AND revoked_at IS NULL""",
                (row[2], self.kindergarten_id, user_id),
            )
        else:
            self.connection.execute(
                """UPDATE refresh_tokens
                SET authentication_method='webauthn',
                    backup_auth_version=NULL,
                    backup_verified_at=NULL,
                    backup_reauthenticated_at=NULL,
                    updated_at=now()
                WHERE kindergarten_id=%s AND user_id=%s
                  AND authentication_method='restricted_enrollment'
                  AND revoked_at IS NULL""",
                (self.kindergarten_id, user_id),
            )
        return restricted

    def update_backup_reauthentication(
        self,
        user_id: UUID,
        family_id: UUID,
        *,
        verified_at: datetime,
    ) -> bool:
        row = self.connection.execute(
            """UPDATE refresh_tokens
            SET backup_reauthenticated_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s AND token_family_id=%s
              AND authentication_method='password_totp'
              AND revoked_at IS NULL AND expires_at>%s
            RETURNING id""",
            (
                verified_at,
                self.kindergarten_id,
                user_id,
                family_id,
                verified_at,
            ),
        ).fetchone()
        return row is not None

    def list_backup_security_events(
        self, user_id: UUID, *, limit: int = 20
    ) -> list[BackupSecurityEventRecord]:
        safe_limit = max(1, min(limit, 20))
        rows = self.connection.execute(
            """SELECT event_code, occurred_at,
                   metadata->>'authentication_method',
                   metadata->>'client_hint'
            FROM audit_events
            WHERE kindergarten_id=%s AND actor_user_id=%s
              AND event_code = ANY(%s)
            ORDER BY occurred_at DESC, id DESC
            LIMIT %s""",
            (
                self.kindergarten_id,
                user_id,
                [
                    "auth.backup_enabled",
                    "auth.backup_changed",
                    "auth.backup_disabled",
                    "auth.backup_login_succeeded",
                    "auth.passkey_added_from_backup",
                    "auth.backup_revoked_by_recovery",
                ],
                safe_limit,
            ),
        ).fetchall()
        return [BackupSecurityEventRecord(*row) for row in rows]  # type: ignore[arg-type]

    def create_challenge(
        self,
        *,
        ceremony_id: UUID,
        user_id: UUID | None,
        purpose: str,
        challenge_hash: str,
        authorization_context: str | None,
        expected_rp_id: str,
        expected_origin: str,
        expires_at: datetime,
    ) -> None:
        self.connection.execute(
            """INSERT INTO webauthn_challenges
            (id, kindergarten_id, user_id, purpose, challenge_hash, authorization_context,
             expected_rp_id, expected_origin, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                ceremony_id,
                self.kindergarten_id,
                user_id,
                purpose,
                challenge_hash,
                authorization_context,
                expected_rp_id,
                expected_origin,
                expires_at,
            ),
        )

    def get_challenge(self, ceremony_id: UUID, *, lock: bool = False) -> ChallengeRecord | None:
        suffix = " FOR UPDATE" if lock else ""
        row = self.connection.execute(
            f"""SELECT {_CHALLENGE_COLUMNS} FROM webauthn_challenges
            WHERE kindergarten_id IS NOT DISTINCT FROM %s AND id=%s{suffix}""",
            (self.kindergarten_id, ceremony_id),
        ).fetchone()
        return ChallengeRecord(*row) if row else None  # type: ignore[arg-type]

    def consume_challenge(self, ceremony_id: UUID, *, now: datetime) -> bool:
        cursor = self.connection.execute(
            """UPDATE webauthn_challenges SET consumed_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND consumed_at IS NULL AND expires_at>%s""",
            (now, self.kindergarten_id, ceremony_id, now),
        )
        return cursor.rowcount == 1

    def record_challenge_failure(self, ceremony_id: UUID) -> None:
        self.connection.execute(
            """UPDATE webauthn_challenges SET failure_count=failure_count+1, updated_at=now()
            WHERE kindergarten_id IS NOT DISTINCT FROM %s AND id=%s""",
            (self.kindergarten_id, ceremony_id),
        )

    def list_credentials(
        self, user_id: UUID, *, include_revoked: bool = False, lock: bool = False
    ) -> list[CredentialRecord]:
        suffix = "" if include_revoked else " AND revoked_at IS NULL"
        lock_clause = " FOR UPDATE" if lock else ""
        rows = self.connection.execute(
            f"""SELECT {_CREDENTIAL_COLUMNS} FROM webauthn_credentials
            WHERE kindergarten_id=%s AND user_id=%s{suffix}
            ORDER BY created_at, id{lock_clause}""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        return [CredentialRecord(*row) for row in rows]  # type: ignore[arg-type]

    def get_credential_by_raw_id(self, credential_id: bytes) -> CredentialRecord | None:
        row = self.connection.execute(
            f"""SELECT {_CREDENTIAL_COLUMNS} FROM webauthn_credentials
            WHERE kindergarten_id=%s AND credential_id=%s AND revoked_at IS NULL""",
            (self.kindergarten_id, credential_id),
        ).fetchone()
        return _credential(row)

    def create_credential(
        self,
        *,
        user_id: UUID,
        credential_id: bytes,
        public_key_cose: bytes,
        sign_count: int,
        transports: list[str],
        aaguid: UUID | None,
        backup_eligible: bool,
        backup_state: bool,
        label: str,
        created_via: str,
    ) -> CredentialRecord:
        record_id = uuid7()
        self.connection.execute(
            """INSERT INTO webauthn_credentials
            (id, kindergarten_id, user_id, credential_id, public_key_cose, sign_count,
             transports, aaguid, backup_eligible, backup_state, label, created_via)
            VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s)""",
            (
                record_id,
                self.kindergarten_id,
                user_id,
                credential_id,
                public_key_cose,
                sign_count,
                Jsonb(transports),
                aaguid,
                backup_eligible,
                backup_state,
                label,
                created_via,
            ),
        )
        row = self.connection.execute(
            f"SELECT {_CREDENTIAL_COLUMNS} FROM webauthn_credentials WHERE id=%s",
            (record_id,),
        ).fetchone()
        record = _credential(row)
        assert record is not None
        return record

    def update_credential_use(self, credential_id: UUID, *, sign_count: int, now: datetime) -> None:
        self.connection.execute(
            """UPDATE webauthn_credentials SET sign_count=%s, last_used_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (sign_count, now, self.kindergarten_id, credential_id),
        )

    def rename_credential(self, user_id: UUID, credential_id: UUID, label: str) -> CredentialRecord:
        row = self.connection.execute(
            f"""UPDATE webauthn_credentials SET label=%s, updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s AND id=%s AND revoked_at IS NULL
            RETURNING {_CREDENTIAL_COLUMNS}""",
            (label, self.kindergarten_id, user_id, credential_id),
        ).fetchone()
        record = _credential(row)
        if record is None:
            raise LookupError("通行密钥不存在")
        return record

    def revoke_credential(
        self, user_id: UUID, credential_id: UUID, *, reason: str, allow_last: bool = False
    ) -> bool:
        credentials = self.list_credentials(user_id, lock=True)
        if not allow_last and len(credentials) <= 1:
            raise ValueError("至少保留一个有效通行密钥")
        cursor = self.connection.execute(
            """UPDATE webauthn_credentials SET revoked_at=COALESCE(revoked_at, now()),
            revoke_reason=COALESCE(revoke_reason,%s), updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s AND id=%s""",
            (reason, self.kindergarten_id, user_id, credential_id),
        )
        return cursor.rowcount == 1

    def revoke_other_credentials(
        self, user_id: UUID, *, keep_credential_id: UUID, reason: str
    ) -> list[UUID]:
        rows = self.connection.execute(
            """UPDATE webauthn_credentials SET revoked_at=COALESCE(revoked_at, now()),
            revoke_reason=COALESCE(revoke_reason,%s), updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s AND id<>%s AND revoked_at IS NULL
            RETURNING id""",
            (reason, self.kindergarten_id, user_id, keep_credential_id),
        ).fetchall()
        return [row[0] for row in rows]  # type: ignore[misc]

    def revoke_active_invitations(self, user_id: UUID) -> list[UUID]:
        rows = self.connection.execute(
            """UPDATE account_invitations SET revoked_at=COALESCE(revoked_at, now()),
            updated_at=now() WHERE kindergarten_id=%s AND user_id=%s
            AND consumed_at IS NULL AND revoked_at IS NULL RETURNING id""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        return [row[0] for row in rows]  # type: ignore[misc]

    def create_invitation(
        self, *, user_id: UUID, issued_by: UUID, token_hash: str, expires_at: datetime
    ) -> InvitationRecord:
        assert self.kindergarten_id is not None
        self.revoke_active_invitations(user_id)
        invitation_id = uuid7()
        self.connection.execute(
            """INSERT INTO account_invitations
            (id, kindergarten_id, user_id, issued_by, token_hash, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (invitation_id, self.kindergarten_id, user_id, issued_by, token_hash, expires_at),
        )
        return InvitationRecord(
            invitation_id,
            self.kindergarten_id,
            user_id,
            datetime.now(UTC),
            expires_at,
            None,
            None,
        )

    def list_invitations(self, user_id: UUID) -> list[InvitationRecord]:
        rows = self.connection.execute(
            """SELECT id, kindergarten_id, user_id, created_at, expires_at,
            consumed_at, revoked_at FROM account_invitations
            WHERE kindergarten_id=%s AND user_id=%s ORDER BY created_at, id""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        return [InvitationRecord(*row) for row in rows]  # type: ignore[arg-type]

    def find_invitation(self, token_hash: str, *, lock: bool = False) -> tuple[UUID, UUID] | None:
        suffix = " FOR UPDATE" if lock else ""
        row = self.connection.execute(
            f"""SELECT id, user_id FROM account_invitations WHERE kindergarten_id=%s
            AND token_hash=%s AND consumed_at IS NULL AND revoked_at IS NULL
            AND expires_at>now(){suffix}""",
            (self.kindergarten_id, token_hash),
        ).fetchone()
        return (row[0], row[1]) if row else None  # type: ignore[return-value]

    def consume_invitation(self, invitation_id: UUID, *, credential_id: UUID | None = None) -> bool:
        cursor = self.connection.execute(
            """UPDATE account_invitations SET consumed_at=now(), registered_credential_id=%s,
            updated_at=now() WHERE kindergarten_id=%s AND id=%s AND consumed_at IS NULL
            AND revoked_at IS NULL AND expires_at>now()""",
            (credential_id, self.kindergarten_id, invitation_id),
        )
        return cursor.rowcount == 1

    def revoke_invitation(self, user_id: UUID, invitation_id: UUID) -> None:
        self.connection.execute(
            """UPDATE account_invitations SET revoked_at=COALESCE(revoked_at, now()),
            updated_at=now() WHERE kindergarten_id=%s AND user_id=%s AND id=%s""",
            (self.kindergarten_id, user_id, invitation_id),
        )

    def find_recovery_code(self, user_id: UUID, code_hash: str) -> UUID | None:
        row = self.connection.execute(
            """SELECT id FROM recovery_codes WHERE kindergarten_id=%s AND user_id=%s
            AND code_hash=%s AND consumed_at IS NULL AND revoked_at IS NULL FOR UPDATE""",
            (self.kindergarten_id, user_id, code_hash),
        ).fetchone()
        return row[0] if row else None  # type: ignore[return-value]

    def consume_recovery_code(self, recovery_code_id: UUID) -> bool:
        cursor = self.connection.execute(
            """UPDATE recovery_codes SET consumed_at=now(), updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND consumed_at IS NULL AND revoked_at IS NULL""",
            (self.kindergarten_id, recovery_code_id),
        )
        return cursor.rowcount == 1

    def rotate_recovery_code(self, user_id: UUID, *, code_hash: str) -> UUID:
        new_id = uuid7()
        old_rows = self.connection.execute(
            """SELECT id FROM recovery_codes WHERE kindergarten_id=%s AND user_id=%s
            AND revoked_at IS NULL FOR UPDATE""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        if old_rows:
            self.connection.execute(
                """UPDATE recovery_codes SET revoked_at=COALESCE(revoked_at, now()),
                updated_at=now()
                WHERE kindergarten_id=%s AND user_id=%s AND revoked_at IS NULL""",
                (self.kindergarten_id, user_id),
            )
        self.connection.execute(
            """INSERT INTO recovery_codes
            (id, kindergarten_id, user_id, code_hash, issued_at)
            VALUES (%s,%s,%s,%s,now())""",
            (new_id, self.kindergarten_id, user_id, code_hash),
        )
        if old_rows:
            self.connection.execute(
                """UPDATE recovery_codes SET replaced_by_id=%s, updated_at=now()
                WHERE kindergarten_id=%s AND id=ANY(%s)""",
                (new_id, self.kindergarten_id, [row[0] for row in old_rows]),
            )
        return new_id

    def create_recovery_request(
        self, *, user_id: UUID, recovery_code_id: UUID, expires_at: datetime
    ) -> UUID:
        request_id = uuid7()
        self.connection.execute(
            """INSERT INTO account_recovery_requests
            (id, kindergarten_id, user_id, recovery_code_id, status, requested_at, expires_at)
            VALUES (%s,%s,%s,%s,'pending_verification',now(),%s)""",
            (request_id, self.kindergarten_id, user_id, recovery_code_id, expires_at),
        )
        return request_id

    def list_recovery_requests(self, user_id: UUID) -> list[RecoveryRequestRecord]:
        rows = self.connection.execute(
            """SELECT id, kindergarten_id, user_id, status, requested_at, expires_at,
            approved_at FROM account_recovery_requests WHERE kindergarten_id=%s
            AND user_id=%s ORDER BY requested_at, id""",
            (self.kindergarten_id, user_id),
        ).fetchall()
        return [RecoveryRequestRecord(*row) for row in rows]  # type: ignore[arg-type]

    def approve_recovery_request(
        self, user_id: UUID, request_id: UUID, *, token_hash: str, expires_at: datetime
    ) -> bool:
        cursor = self.connection.execute(
            """UPDATE account_recovery_requests SET status='approved', approved_at=now(),
            enrollment_token_hash=%s, enrollment_expires_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND user_id=%s AND id=%s
            AND status='pending_verification' AND expires_at>now()""",
            (token_hash, expires_at, self.kindergarten_id, user_id, request_id),
        )
        return cursor.rowcount == 1

    def create_verification_approval(
        self,
        *,
        context_type: str,
        context_id: UUID,
        user_id: UUID,
        approver_user_id: UUID | None,
        approver_kind: str,
        approver_reference: str,
        note: str | None,
        decided_at: datetime,
    ) -> UUID:
        approval_id = uuid7()
        self.connection.execute(
            """INSERT INTO identity_verification_approvals
            (id, kindergarten_id, context_type, context_id, user_id, approver_user_id,
             approver_kind, approver_reference, decision, note, decided_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'approved',%s,%s)""",
            (
                approval_id,
                self.kindergarten_id,
                context_type,
                context_id,
                user_id,
                approver_user_id,
                approver_kind,
                approver_reference,
                note,
                decided_at,
            ),
        )
        return approval_id

    def find_recovery_enrollment(
        self, token_hash: str, *, lock: bool = False
    ) -> tuple[UUID, UUID] | None:
        suffix = " FOR UPDATE" if lock else ""
        row = self.connection.execute(
            f"""SELECT id, user_id FROM account_recovery_requests
            WHERE kindergarten_id=%s AND enrollment_token_hash=%s
            AND status IN ('approved','registration_pending')
            AND enrollment_consumed_at IS NULL AND enrollment_expires_at>now(){suffix}""",
            (self.kindergarten_id, token_hash),
        ).fetchone()
        return (row[0], row[1]) if row else None  # type: ignore[return-value]
