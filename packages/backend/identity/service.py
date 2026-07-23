"""通行密钥身份用例、一次性材料状态机与实时会话授权。"""

import base64
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any, LiteralString
from uuid import UUID, uuid7

import psycopg

from packages.backend.audit.repository import AuditRepository
from packages.backend.identity.challenges import (
    ChallengeBinding,
    ChallengePurpose,
    issue_challenge,
)
from packages.backend.identity.identifiers import normalize_phone, normalize_username
from packages.backend.identity.repository import (
    CredentialRecord,
    IdentityRepository,
    InvitationRecord,
    RecoveryRequestRecord,
    UserRecord,
)
from packages.backend.identity.secret_tokens import SecretPurpose, issue_secret, verify_secret
from packages.backend.identity.tokens import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from packages.backend.identity.webauthn import (
    authentication_options,
    registration_options,
    verify_authentication,
    verify_registration,
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
    token_family_id: UUID
    session_id: UUID
    last_reauthenticated_at: datetime | None

    @property
    def capabilities(self) -> list[str]:
        capabilities = {"plans:view", "credentials:manage"}
        if "admin" in self.role_codes:
            capabilities.add("users:manage")
        return sorted(capabilities)


@dataclass(frozen=True, slots=True)
class ManagedUser:
    user: UserRecord
    role_codes: list[str]
    credential_count: int


@dataclass(frozen=True, slots=True)
class AuthResult:
    session: SessionUser
    access_token: str
    refresh_token: str
    recovery_code: str | None = None


@dataclass(frozen=True, slots=True)
class _RegistrationResult:
    credential: CredentialRecord
    recovery_code: str | None = None
    sessions_revoked: int = 0


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _decode_base64url(value: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except ValueError as exc:
        raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。") from exc


def _client_challenge(credential: dict[str, Any]) -> str:
    try:
        response = credential["response"]
        assert isinstance(response, dict)
        encoded = str(response["clientDataJSON"])
        client_data = json.loads(_decode_base64url(encoded))
        return str(client_data["challenge"])
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。") from exc


def _challenge_digest(challenge: str) -> str:
    return sha256(_decode_base64url(challenge)).hexdigest()


class IdentityService:
    def __init__(
        self,
        *,
        database_url: str,
        jwt_signing_key: str,
        rp_id: str,
        rp_name: str,
    ) -> None:
        self.database_url = database_url
        self.jwt_signing_key = jwt_signing_key
        self.rp_id = rp_id
        self.rp_name = rp_name

    @classmethod
    def from_environment(cls) -> IdentityService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        jwt_key = os.environ.get("CHILD_MANAGER_JWT_SIGNING_KEY")
        rp_id = os.environ.get("CHILD_MANAGER_WEBAUTHN_RP_ID")
        rp_name = os.environ.get("CHILD_MANAGER_WEBAUTHN_RP_NAME", "Child Manager")
        if not database_url or not jwt_key or not rp_id:
            raise IdentityError(503, "configuration.unavailable", "服务端安全配置不可用。")
        return cls(
            database_url=database_url,
            jwt_signing_key=jwt_key,
            rp_id=rp_id,
            rp_name=rp_name,
        )

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
    def _optional_kindergarten_id(
        connection: psycopg.Connection[tuple[object, ...]],
    ) -> UUID | None:
        rows = connection.execute(
            "SELECT id FROM kindergartens WHERE is_active ORDER BY created_at LIMIT 2"
        ).fetchall()
        return rows[0][0] if len(rows) == 1 else None  # type: ignore[return-value]

    @staticmethod
    def normalize_login_key(value: str) -> str:
        compact = value.strip()
        if compact.startswith("+") or compact.replace(" ", "").replace("-", "").isdigit():
            phone = normalize_phone(value)
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
    def require_admin(session: SessionUser) -> None:
        if "admin" not in session.role_codes:
            raise IdentityError(403, "auth.forbidden", "没有执行此操作的权限。")

    @staticmethod
    def require_recent_verification(session: SessionUser) -> None:
        verified = session.last_reauthenticated_at
        if verified is None or verified < datetime.now(UTC) - timedelta(minutes=5):
            raise IdentityError(403, "auth.step_up_required", "请先使用通行密钥重新验证。")

    def kindergarten_summary(self, kindergarten_id: UUID) -> dict[str, object]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, name, timezone FROM kindergartens WHERE id=%s AND is_active",
                (kindergarten_id,),
            ).fetchone()
        if row is None:
            raise IdentityError(401, "auth.unauthenticated", "登录状态已失效，请重新登录。")
        return {"id": row[0], "name": row[1], "timezone": row[2]}

    def _managed(self, repository: IdentityRepository, user: UserRecord) -> ManagedUser:
        return ManagedUser(
            user,
            repository.roles_for_user(user.id),
            repository.credential_count(user.id),
        )

    def _registration_options(
        self,
        repository: IdentityRepository,
        *,
        user: UserRecord,
        purpose: ChallengePurpose,
        authorization_context: str,
        origin: str,
    ) -> dict[str, object]:
        now = datetime.now(UTC)
        binding = ChallengeBinding(
            purpose=purpose,
            kindergarten_id=repository.kindergarten_id,
            user_id=user.id,
            authorization_context=authorization_context,
            rp_id=self.rp_id,
            origin=origin,
            requires_user_verification=True,
        )
        issued = issue_challenge(binding=binding, now=now)
        repository.create_challenge(
            ceremony_id=issued.record.ceremony_id,
            user_id=user.id,
            purpose=purpose.value,
            challenge_hash=issued.record.challenge_digest,
            authorization_context=authorization_context,
            expected_rp_id=self.rp_id,
            expected_origin=origin,
            expires_at=issued.record.expires_at,
        )
        options = registration_options(
            challenge=issued.challenge,
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_handle=user.webauthn_user_handle,
            username=user.username,
            display_name=user.display_name,
            exclude_credential_ids=(
                []
                if purpose is ChallengePurpose.SELF_ADD_REGISTRATION
                else [item.credential_id for item in repository.list_credentials(user.id)]
            ),
        )
        return {
            "ceremony_id": issued.record.ceremony_id,
            "expires_at": issued.record.expires_at,
            **options,
        }

    def _authentication_options(
        self,
        repository: IdentityRepository,
        *,
        purpose: ChallengePurpose,
        origin: str,
        user: UserRecord | None = None,
        authorization_context: str | None = None,
    ) -> dict[str, object]:
        now = datetime.now(UTC)
        issued = issue_challenge(
            binding=ChallengeBinding(
                purpose=purpose,
                kindergarten_id=repository.kindergarten_id,
                user_id=user.id if user else None,
                authorization_context=authorization_context,
                rp_id=self.rp_id,
                origin=origin,
                requires_user_verification=True,
            ),
            now=now,
        )
        repository.create_challenge(
            ceremony_id=issued.record.ceremony_id,
            user_id=user.id if user else None,
            purpose=purpose.value,
            challenge_hash=issued.record.challenge_digest,
            authorization_context=authorization_context,
            expected_rp_id=self.rp_id,
            expected_origin=origin,
            expires_at=issued.record.expires_at,
        )
        allow = (
            [item.credential_id for item in repository.list_credentials(user.id)] if user else []
        )
        options = authentication_options(
            challenge=issued.challenge,
            rp_id=self.rp_id,
            allow_credential_ids=allow,
        )
        return {
            "ceremony_id": issued.record.ceremony_id,
            "expires_at": issued.record.expires_at,
            **options,
        }

    def authentication_options(self, *, origin: str) -> dict[str, object]:
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._optional_kindergarten_id(connection)
            return self._authentication_options(
                IdentityRepository(connection, kindergarten_id),
                purpose=ChallengePurpose.AUTHENTICATION,
                origin=origin,
            )

    def bootstrap_registration_options(self, secret: str, *, origin: str) -> dict[str, object]:
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._optional_kindergarten_id(connection)
            if kindergarten_id is None:
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            repository = IdentityRepository(connection, kindergarten_id)
            row = connection.execute(
                """SELECT id, user_id, token_digest FROM bootstrap_initializations
                WHERE kindergarten_id=%s AND consumed_at IS NULL AND activated_at IS NULL
                AND expires_at>now() FOR UPDATE""",
                (kindergarten_id,),
            ).fetchone()
            if row is None or not verify_secret(
                SecretPurpose.BOOTSTRAP, secret=secret, digest=str(row[2])
            ):
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            user = repository.get_user(row[1])  # type: ignore[arg-type]
            assert user is not None
            return self._registration_options(
                repository,
                user=user,
                purpose=ChallengePurpose.BOOTSTRAP_REGISTRATION,
                authorization_context=str(row[0]),
                origin=origin,
            )

    def invitation_registration_options(self, secret: str, *, origin: str) -> dict[str, object]:
        material = issue_secret(SecretPurpose.INVITATION)
        del material
        digest = sha256(f"child-manager:invitation:{secret}".encode()).hexdigest()
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._optional_kindergarten_id(connection)
            if kindergarten_id is None:
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            repository = IdentityRepository(connection, kindergarten_id)
            invitation = repository.find_invitation(digest, lock=True)
            if invitation is None:
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            invitation_id, user_id = invitation
            user = repository.get_user(user_id)
            assert user is not None
            return self._registration_options(
                repository,
                user=user,
                purpose=ChallengePurpose.INVITATION_REGISTRATION,
                authorization_context=str(invitation_id),
                origin=origin,
            )

    def recovery_registration_options(self, secret: str, *, origin: str) -> dict[str, object]:
        digest = sha256(f"child-manager:recovery_enrollment:{secret}".encode()).hexdigest()
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._optional_kindergarten_id(connection)
            if kindergarten_id is None:
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            repository = IdentityRepository(connection, kindergarten_id)
            enrollment = repository.find_recovery_enrollment(digest, lock=True)
            if enrollment is None:
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            request_id, user_id = enrollment
            user = repository.get_user(user_id)
            assert user is not None
            connection.execute(
                """UPDATE account_recovery_requests SET status='registration_pending',
                updated_at=now() WHERE kindergarten_id=%s AND id=%s""",
                (kindergarten_id, request_id),
            )
            return self._registration_options(
                repository,
                user=user,
                purpose=ChallengePurpose.RECOVERY_REGISTRATION,
                authorization_context=str(request_id),
                origin=origin,
            )

    def self_add_registration_options(
        self, session: SessionUser, *, origin: str
    ) -> dict[str, object]:
        self.require_recent_verification(session)
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            user = repository.get_user(session.user.id)
            if user is None:
                raise IdentityError(401, "auth.unauthenticated", "登录状态已失效，请重新登录。")
            return self._registration_options(
                repository,
                user=user,
                purpose=ChallengePurpose.SELF_ADD_REGISTRATION,
                authorization_context=str(session.token_family_id),
                origin=origin,
            )

    def _verify_registration(
        self,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        label: str | None,
        expected_purpose: ChallengePurpose,
        expected_user_id: UUID | None = None,
        expected_authorization_context: str | None = None,
        source: str,
        request_id: UUID | None,
    ) -> _RegistrationResult:
        try:
            return self._verify_registration_transaction(
                ceremony_id=ceremony_id,
                credential=credential,
                label=label,
                expected_purpose=expected_purpose,
                expected_user_id=expected_user_id,
                expected_authorization_context=expected_authorization_context,
            )
        except IdentityError as exc:
            if exc.code not in {"identity.material_unavailable", "auth.authentication_failed"}:
                raise
            self._persist_registration_failure(
                ceremony_id=ceremony_id,
                expected_purpose=expected_purpose,
                source=source,
                request_id=request_id,
            )
            raise IdentityError(
                410, "identity.material_unavailable", "登记凭据无效或已失效。"
            ) from exc

    def _persist_registration_failure(
        self,
        *,
        ceremony_id: UUID,
        expected_purpose: ChallengePurpose,
        source: str,
        request_id: UUID | None,
    ) -> None:
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._optional_kindergarten_id(connection)
            repository = IdentityRepository(connection, kindergarten_id)
            challenge = repository.get_challenge(ceremony_id, lock=True)
            repository.record_challenge_failure(ceremony_id)
            if kindergarten_id is None:
                return
            actor_user_id = challenge.user_id if challenge is not None else None
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.CREDENTIAL_REGISTERED,
                actor_user_id=actor_user_id,
                actor_role_codes=(
                    repository.roles_for_user(actor_user_id) if actor_user_id is not None else []
                ),
                resource_type="webauthn_challenge",
                resource_id=ceremony_id,
                request_id=request_id,
                outcome="failure",
                metadata={"reason": expected_purpose.value, "source": source},
            )

    @staticmethod
    def _complete_recovery_registration(
        *,
        connection: psycopg.Connection[tuple[object, ...]],
        repository: IdentityRepository,
        kindergarten_id: UUID,
        user_id: UUID,
        recovery_request_id: UUID,
        credential_id: UUID,
        now: datetime,
    ) -> tuple[str, int]:
        material = issue_secret(SecretPurpose.RECOVERY_CODE)
        repository.rotate_recovery_code(user_id, code_hash=material.record.digest)
        revoked_credential_ids = repository.revoke_other_credentials(
            user_id,
            keep_credential_id=credential_id,
            reason="account_recovered",
        )
        revoked_invitation_ids = repository.revoke_active_invitations(user_id)
        sessions_revoked = repository.revoke_user_sessions(user_id, reason="account_recovered")
        repository.set_status(user_id, "active", actor_user_id=user_id)
        connection.execute(
            """UPDATE account_recovery_requests SET status='completed',
            enrollment_consumed_at=%s, completed_at=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (now, now, kindergarten_id, recovery_request_id),
        )
        roles = repository.roles_for_user(user_id)
        audit = AuditRepository(connection, kindergarten_id)
        audit.append(
            event_code=IdentityAuditEventCode.RECOVERY_COMPLETED,
            actor_user_id=user_id,
            actor_role_codes=roles,
            resource_type="account_recovery_request",
            resource_id=recovery_request_id,
            outcome="success",
        )
        audit.append(
            event_code=IdentityAuditEventCode.RECOVERY_CODE_ROTATED,
            actor_user_id=user_id,
            actor_role_codes=roles,
            resource_type="user",
            resource_id=user_id,
            outcome="success",
            metadata={"reason": "account_recovered"},
        )
        for revoked_credential_id in revoked_credential_ids:
            audit.append(
                event_code=IdentityAuditEventCode.CREDENTIAL_REVOKED,
                actor_user_id=user_id,
                actor_role_codes=roles,
                resource_type="webauthn_credential",
                resource_id=revoked_credential_id,
                outcome="success",
                metadata={"reason": "account_recovered"},
            )
        for revoked_invitation_id in revoked_invitation_ids:
            audit.append(
                event_code=IdentityAuditEventCode.INVITATION_REVOKED,
                actor_user_id=user_id,
                actor_role_codes=roles,
                resource_type="account_invitation",
                resource_id=revoked_invitation_id,
                outcome="success",
                metadata={"reason": "account_recovered"},
            )
        if sessions_revoked:
            audit.append(
                event_code=IdentityAuditEventCode.SESSION_REVOKED,
                actor_user_id=user_id,
                actor_role_codes=roles,
                resource_type="user",
                resource_id=user_id,
                outcome="success",
                metadata={"reason": "account_recovered"},
            )
        return material.secret, sessions_revoked

    def _verify_registration_transaction(
        self,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        label: str | None,
        expected_purpose: ChallengePurpose,
        expected_user_id: UUID | None = None,
        expected_authorization_context: str | None = None,
    ) -> _RegistrationResult:
        now = datetime.now(UTC)
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._optional_kindergarten_id(connection)
            if kindergarten_id is None:
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            repository = IdentityRepository(connection, kindergarten_id)
            challenge = repository.get_challenge(ceremony_id, lock=True)
            if (
                challenge is None
                or challenge.purpose != expected_purpose.value
                or challenge.consumed_at is not None
                or challenge.expires_at <= now
                or (expected_user_id is not None and challenge.user_id != expected_user_id)
                or (
                    expected_authorization_context is not None
                    and challenge.authorization_context != expected_authorization_context
                )
            ):
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            if expected_purpose is ChallengePurpose.SELF_ADD_REGISTRATION:
                assert expected_user_id is not None
                assert expected_authorization_context is not None
                if not repository.has_active_refresh_family(
                    expected_user_id, UUID(expected_authorization_context)
                ):
                    raise IdentityError(
                        410, "identity.material_unavailable", "登记凭据无效或已失效。"
                    )
            raw_challenge = _client_challenge(credential)
            if challenge.challenge_hash != _challenge_digest(raw_challenge):
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            context_id = UUID(str(challenge.authorization_context))
            source_queries: dict[ChallengePurpose, LiteralString] = {
                ChallengePurpose.BOOTSTRAP_REGISTRATION: """SELECT 1
                    FROM bootstrap_initializations WHERE kindergarten_id=%s AND id=%s
                    AND consumed_at IS NULL AND activated_at IS NULL AND expires_at>now()
                    FOR UPDATE""",
                ChallengePurpose.INVITATION_REGISTRATION: """SELECT 1
                    FROM account_invitations WHERE kindergarten_id=%s AND id=%s
                    AND consumed_at IS NULL AND revoked_at IS NULL AND expires_at>now()
                    FOR UPDATE""",
                ChallengePurpose.RECOVERY_REGISTRATION: """SELECT 1
                    FROM account_recovery_requests WHERE kindergarten_id=%s AND id=%s
                    AND status IN ('approved','registration_pending')
                    AND enrollment_consumed_at IS NULL AND enrollment_expires_at>now()
                    FOR UPDATE""",
            }
            source_valid = source_queries.get(expected_purpose)
            if (
                source_valid is not None
                and connection.execute(source_valid, (kindergarten_id, context_id)).fetchone()
                is None
            ):
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            if not repository.consume_challenge(ceremony_id, now=now):
                raise IdentityError(410, "identity.material_unavailable", "登记凭据无效或已失效。")
            try:
                verified = verify_registration(
                    credential=credential,
                    expected_challenge=raw_challenge,
                    expected_rp_id=challenge.expected_rp_id,
                    expected_origin=challenge.expected_origin,
                )
            except Exception as exc:
                raise IdentityError(
                    410, "identity.material_unavailable", "登记凭据无效或已失效。"
                ) from exc
            assert challenge.user_id is not None
            transports = credential.get("response", {}).get("transports", [])
            created = repository.create_credential(
                user_id=challenge.user_id,
                credential_id=verified.credential_id,
                public_key_cose=verified.credential_public_key,
                sign_count=verified.sign_count,
                transports=[str(item) for item in transports],
                aaguid=UUID(verified.aaguid) if verified.aaguid else None,
                backup_eligible=str(verified.credential_device_type.value) == "multi_device",
                backup_state=verified.credential_backed_up,
                label=(label or "通行密钥").strip(),
                created_via={
                    ChallengePurpose.BOOTSTRAP_REGISTRATION: "bootstrap",
                    ChallengePurpose.INVITATION_REGISTRATION: "invitation",
                    ChallengePurpose.SELF_ADD_REGISTRATION: "self_add",
                    ChallengePurpose.RECOVERY_REGISTRATION: "recovery",
                }[expected_purpose],
            )
            recovery_code: str | None = None
            sessions_revoked = 0
            if expected_purpose is ChallengePurpose.BOOTSTRAP_REGISTRATION:
                connection.execute(
                    """UPDATE bootstrap_initializations SET consumed_at=%s,
                    registered_credential_id=%s, updated_at=now()
                    WHERE kindergarten_id=%s AND id=%s AND consumed_at IS NULL""",
                    (now, created.id, kindergarten_id, context_id),
                )
                repository.set_status(
                    challenge.user_id, "pending_verification", actor_user_id=challenge.user_id
                )
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.BOOTSTRAP_REGISTERED,
                    actor_user_id=challenge.user_id,
                    actor_role_codes=repository.roles_for_user(challenge.user_id),
                    resource_type="bootstrap_initialization",
                    resource_id=context_id,
                    outcome="success",
                )
            elif expected_purpose is ChallengePurpose.INVITATION_REGISTRATION:
                if not repository.consume_invitation(context_id, credential_id=created.id):
                    raise IdentityError(
                        410, "identity.material_unavailable", "登记凭据无效或已失效。"
                    )
                repository.set_status(
                    challenge.user_id, "pending_verification", actor_user_id=challenge.user_id
                )
            elif expected_purpose is ChallengePurpose.RECOVERY_REGISTRATION:
                recovery_code, sessions_revoked = self._complete_recovery_registration(
                    connection=connection,
                    repository=repository,
                    kindergarten_id=kindergarten_id,
                    user_id=challenge.user_id,
                    recovery_request_id=context_id,
                    credential_id=created.id,
                    now=now,
                )
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.CREDENTIAL_REGISTERED,
                actor_user_id=challenge.user_id,
                actor_role_codes=repository.roles_for_user(challenge.user_id),
                resource_type="webauthn_credential",
                resource_id=created.id,
                outcome="success",
            )
            return _RegistrationResult(created, recovery_code, sessions_revoked)

    def verify_bootstrap_registration(
        self,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        label: str | None,
        source: str,
        request_id: UUID | None,
    ) -> tuple[CredentialRecord, UUID]:
        result = self._verify_registration(
            ceremony_id=ceremony_id,
            credential=credential,
            label=label,
            expected_purpose=ChallengePurpose.BOOTSTRAP_REGISTRATION,
            source=source,
            request_id=request_id,
        )
        return result.credential, result.credential.user_id

    def verify_invitation_registration(
        self,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        label: str | None,
        source: str,
        request_id: UUID | None,
    ) -> tuple[CredentialRecord, UUID]:
        result = self._verify_registration(
            ceremony_id=ceremony_id,
            credential=credential,
            label=label,
            expected_purpose=ChallengePurpose.INVITATION_REGISTRATION,
            source=source,
            request_id=request_id,
        )
        return result.credential, result.credential.user_id

    def verify_self_add_registration(
        self,
        session: SessionUser,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        label: str | None,
        source: str,
        request_id: UUID | None,
    ) -> CredentialRecord:
        self.require_recent_verification(session)
        result = self._verify_registration(
            ceremony_id=ceremony_id,
            credential=credential,
            label=label,
            expected_purpose=ChallengePurpose.SELF_ADD_REGISTRATION,
            expected_user_id=session.user.id,
            expected_authorization_context=str(session.token_family_id),
            source=source,
            request_id=request_id,
        )
        return result.credential

    def verify_recovery_registration(
        self,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        label: str | None,
        source: str,
        request_id: UUID | None,
    ) -> tuple[CredentialRecord, str, int]:
        result = self._verify_registration(
            ceremony_id=ceremony_id,
            credential=credential,
            label=label,
            expected_purpose=ChallengePurpose.RECOVERY_REGISTRATION,
            source=source,
            request_id=request_id,
        )
        assert result.recovery_code is not None
        return result.credential, result.recovery_code, result.sessions_revoked

    def verify_authentication(
        self,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        source: str,
        request_id: UUID | None,
    ) -> AuthResult:
        try:
            return self._verify_authentication_transaction(
                ceremony_id=ceremony_id,
                credential=credential,
                source=source,
                request_id=request_id,
            )
        except IdentityError as exc:
            if exc.code == "auth.authentication_failed":
                self._persist_authentication_failure(
                    ceremony_id=ceremony_id,
                    source=source,
                    request_id=request_id,
                    kindergarten_id=None,
                )
            raise

    def _persist_authentication_failure(
        self,
        *,
        ceremony_id: UUID,
        source: str,
        request_id: UUID | None,
        kindergarten_id: UUID | None,
    ) -> None:
        with self._connect() as connection, connection.transaction():
            resolved_kindergarten_id = kindergarten_id or self._optional_kindergarten_id(connection)
            repository = IdentityRepository(connection, resolved_kindergarten_id)
            challenge = repository.get_challenge(ceremony_id, lock=True)
            repository.record_challenge_failure(ceremony_id)
            if resolved_kindergarten_id is None:
                return
            actor_user_id = challenge.user_id if challenge is not None else None
            AuditRepository(connection, resolved_kindergarten_id).append(
                event_code=IdentityAuditEventCode.AUTHENTICATION_FAILED,
                actor_user_id=actor_user_id,
                actor_role_codes=(
                    repository.roles_for_user(actor_user_id) if actor_user_id is not None else []
                ),
                resource_type="webauthn_challenge",
                resource_id=ceremony_id,
                request_id=request_id,
                outcome="failure",
                metadata={"source": source},
            )

    def _verify_authentication_transaction(
        self,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        source: str,
        request_id: UUID | None,
    ) -> AuthResult:
        now = datetime.now(UTC)
        result: AuthResult | None = None
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._optional_kindergarten_id(connection)
            repository = IdentityRepository(connection, kindergarten_id)
            challenge = repository.get_challenge(ceremony_id, lock=True)
            if (
                challenge is None
                or challenge.purpose != ChallengePurpose.AUTHENTICATION.value
                or challenge.consumed_at is not None
                or challenge.expires_at <= now
            ):
                raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。")
            raw_challenge = _client_challenge(credential)
            if challenge.challenge_hash != _challenge_digest(raw_challenge):
                raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。")
            repository.consume_challenge(ceremony_id, now=now)
            raw_credential_id = _decode_base64url(str(credential.get("rawId", "")))
            stored = repository.get_credential_by_raw_id(raw_credential_id)
            if kindergarten_id is None or stored is None:
                raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。")
            user = repository.get_user(stored.user_id, lock=True)
            if user is None or user.status != "active":
                raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。")
            try:
                verified = verify_authentication(
                    credential=credential,
                    expected_challenge=raw_challenge,
                    expected_rp_id=challenge.expected_rp_id,
                    expected_origin=challenge.expected_origin,
                    credential_public_key=stored.public_key_cose,
                    credential_current_sign_count=stored.sign_count,
                )
            except Exception as exc:
                raise IdentityError(
                    401, "auth.authentication_failed", "通行密钥认证失败。"
                ) from exc
            repository.update_credential_use(stored.id, sign_count=verified.new_sign_count, now=now)
            family_id = uuid7()
            raw_refresh = generate_refresh_token()
            repository.create_refresh(
                user_id=user.id,
                family_id=family_id,
                token_hash=hash_refresh_token(raw_refresh),
                issued_at=now,
                expires_at=now + timedelta(days=7),
                last_reauthenticated_at=now,
            )
            connection.execute(
                """UPDATE users SET last_login_at=%s, updated_at=now()
                WHERE kindergarten_id=%s AND id=%s""",
                (now, kindergarten_id, user.id),
            )
            roles = repository.roles_for_user(user.id)
            recovery_code: str | None = None
            active_recovery = connection.execute(
                """SELECT 1 FROM recovery_codes WHERE kindergarten_id=%s AND user_id=%s
                AND consumed_at IS NULL AND revoked_at IS NULL""",
                (kindergarten_id, user.id),
            ).fetchone()
            if active_recovery is None:
                recovery = issue_secret(SecretPurpose.RECOVERY_CODE)
                repository.rotate_recovery_code(user.id, code_hash=recovery.record.digest)
                recovery_code = recovery.secret
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.RECOVERY_CODE_ROTATED,
                    actor_user_id=user.id,
                    actor_role_codes=roles,
                    resource_type="user",
                    resource_id=user.id,
                    request_id=request_id,
                    outcome="success",
                    metadata={"reason": "initial_issue"},
                )
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.AUTHENTICATION_SUCCEEDED,
                actor_user_id=user.id,
                actor_role_codes=roles,
                resource_type="refresh_family",
                resource_id=family_id,
                request_id=request_id,
                outcome="success",
                metadata={"source": source},
            )
            session = SessionUser(user, roles, family_id, family_id, now)
            result = AuthResult(
                session=session,
                access_token=create_access_token(
                    user_id=str(user.id),
                    kindergarten_id=str(kindergarten_id),
                    token_family_id=str(family_id),
                    signing_key=self.jwt_signing_key,
                    now=now,
                ),
                refresh_token=raw_refresh,
                recovery_code=recovery_code,
            )
        assert result is not None
        return result

    def step_up_options(self, session: SessionUser, *, origin: str) -> dict[str, object]:
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            user = repository.get_user(session.user.id)
            if user is None:
                raise IdentityError(401, "auth.unauthenticated", "登录状态已失效，请重新登录。")
            return self._authentication_options(
                repository,
                purpose=ChallengePurpose.STEP_UP,
                origin=origin,
                user=user,
                authorization_context=str(session.token_family_id),
            )

    def verify_step_up(
        self,
        session: SessionUser,
        *,
        ceremony_id: UUID,
        credential: dict[str, Any],
        source: str,
        request_id: UUID | None,
    ) -> tuple[datetime, datetime]:
        try:
            return self._verify_step_up_transaction(
                session, ceremony_id=ceremony_id, credential=credential
            )
        except IdentityError as exc:
            if exc.code == "auth.authentication_failed":
                self._persist_authentication_failure(
                    ceremony_id=ceremony_id,
                    source=source,
                    request_id=request_id,
                    kindergarten_id=session.user.kindergarten_id,
                )
            raise

    def _verify_step_up_transaction(
        self, session: SessionUser, *, ceremony_id: UUID, credential: dict[str, Any]
    ) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            challenge = repository.get_challenge(ceremony_id, lock=True)
            if (
                challenge is None
                or challenge.purpose != ChallengePurpose.STEP_UP.value
                or challenge.user_id != session.user.id
                or challenge.authorization_context != str(session.token_family_id)
                or challenge.consumed_at is not None
                or challenge.expires_at <= now
            ):
                raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。")
            raw_challenge = _client_challenge(credential)
            if challenge.challenge_hash != _challenge_digest(raw_challenge):
                raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。")
            repository.consume_challenge(ceremony_id, now=now)
            stored = repository.get_credential_by_raw_id(
                _decode_base64url(str(credential.get("rawId", "")))
            )
            if stored is None or stored.user_id != session.user.id:
                raise IdentityError(401, "auth.authentication_failed", "通行密钥认证失败。")
            try:
                verified = verify_authentication(
                    credential=credential,
                    expected_challenge=raw_challenge,
                    expected_rp_id=challenge.expected_rp_id,
                    expected_origin=challenge.expected_origin,
                    credential_public_key=stored.public_key_cose,
                    credential_current_sign_count=stored.sign_count,
                )
            except Exception as exc:
                raise IdentityError(
                    401, "auth.authentication_failed", "通行密钥认证失败。"
                ) from exc
            repository.update_credential_use(stored.id, sign_count=verified.new_sign_count, now=now)
            connection.execute(
                """UPDATE refresh_tokens SET last_reauthenticated_at=%s, updated_at=now()
                WHERE kindergarten_id=%s AND user_id=%s AND token_family_id=%s
                AND revoked_at IS NULL""",
                (
                    now,
                    session.user.kindergarten_id,
                    session.user.id,
                    session.token_family_id,
                ),
            )
        return now, now + timedelta(minutes=5)

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
            current = repository.get_family_session(user_id, family_id)
            if (
                user is None
                or user.status != "active"
                or current is None
                or current.revoked_at is not None
                or current.expires_at <= datetime.now(UTC)
            ):
                raise IdentityError(401, "auth.unauthenticated", "登录状态已失效，请重新登录。")
            return SessionUser(
                user,
                repository.roles_for_user(user.id),
                family_id,
                family_id,
                current.last_reauthenticated_at,
            )

    def refresh(self, raw_token: str, *, request_id: UUID | None) -> AuthResult:
        now = datetime.now(UTC)
        result: AuthResult | None = None
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._kindergarten_id(connection)
            repository = IdentityRepository(connection, kindergarten_id)
            old = repository.get_refresh(hash_refresh_token(raw_token), lock=True)
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
                if user is None or user.status != "active" or old.expires_at <= now:
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
                    result = AuthResult(
                        SessionUser(
                            user,
                            roles,
                            old.token_family_id,
                            old.token_family_id,
                            old.last_reauthenticated_at,
                        ),
                        create_access_token(
                            user_id=str(user.id),
                            kindergarten_id=str(kindergarten_id),
                            token_family_id=str(old.token_family_id),
                            signing_key=self.jwt_signing_key,
                            now=now,
                        ),
                        new_raw,
                    )
        if result is None:
            raise IdentityError(401, "auth.unauthenticated", "刷新会话已失效，请重新登录。")
        return result

    def logout(
        self,
        raw_token: str | None,
        *,
        request_id: UUID | None,
        raw_access_token: str | None = None,
    ) -> None:
        if not raw_token and not raw_access_token:
            return
        identity: tuple[UUID, UUID] | None = None
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._kindergarten_id(connection)
            repository = IdentityRepository(connection, kindergarten_id)
            if raw_token:
                token = repository.get_refresh(hash_refresh_token(raw_token), lock=True)
                if token:
                    identity = token.user_id, token.token_family_id
            elif raw_access_token:
                try:
                    claims = decode_access_token(
                        raw_access_token, signing_key=self.jwt_signing_key, now=datetime.now(UTC)
                    )
                    identity = UUID(str(claims["sub"])), UUID(str(claims["fid"]))
                except KeyError, ValueError:
                    identity = None
            if identity:
                repository.revoke_family(identity[1], reason="logout")
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.LOGGED_OUT,
                    actor_user_id=identity[0],
                    actor_role_codes=repository.roles_for_user(identity[0]),
                    resource_type="refresh_family",
                    resource_id=identity[1],
                    request_id=request_id,
                    outcome="success",
                )

    def create_user(
        self,
        session: SessionUser,
        *,
        username: str,
        phone_e164: str | None,
        display_name: str,
        role_codes: list[str],
        request_id: UUID | None,
    ) -> ManagedUser:
        self.require_admin(session)
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
                return self._managed(repository, user)
        except psycopg.errors.UniqueViolation:
            raise IdentityError(
                409, "identity.identifier_conflict", "用户名或手机号已被使用。"
            ) from None

    def list_users(
        self, session: SessionUser, *, page: int, page_size: int
    ) -> tuple[list[ManagedUser], int]:
        self.require_admin(session)
        with self._connect() as connection:
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            users, total = repository.list_users(page=page, page_size=page_size)
            return [self._managed(repository, user) for user in users], total

    def get_user(self, session: SessionUser, user_id: UUID) -> ManagedUser:
        self.require_admin(session)
        with self._connect() as connection:
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            user = repository.get_user(user_id)
            if user is None:
                raise IdentityError(404, "resource.not_found", "账号不存在。")
            return self._managed(repository, user)

    def update_user(
        self,
        session: SessionUser,
        user_id: UUID,
        *,
        username: str | None,
        phone_e164: str | None,
        display_name: str | None,
        request_id: UUID | None,
    ) -> ManagedUser:
        self.require_admin(session)
        try:
            normalized_username = normalize_username(username) if username is not None else None
            normalized_phone = normalize_phone(phone_e164)
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
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=IdentityAuditEventCode.USER_UPDATED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="user",
                    resource_id=user.id,
                    request_id=request_id,
                    outcome="success",
                )
                return self._managed(repository, user)
        except ValueError as exc:
            raise IdentityError(422, "identity.invalid_identifier", str(exc)) from None
        except LookupError:
            raise IdentityError(404, "resource.not_found", "账号不存在。") from None
        except psycopg.errors.UniqueViolation:
            raise IdentityError(
                409, "identity.identifier_conflict", "用户名或手机号已被使用。"
            ) from None

    def set_roles(
        self, session: SessionUser, user_id: UUID, role_codes: list[str], *, request_id: UUID | None
    ) -> ManagedUser:
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
                return self._managed(repository, user)
        except LookupError:
            raise IdentityError(404, "resource.not_found", "账号不存在。") from None
        except ValueError as exc:
            raise IdentityError(409, "identity.last_admin_required", str(exc)) from None

    def set_status(
        self, session: SessionUser, user_id: UUID, *, status: str, request_id: UUID | None
    ) -> ManagedUser:
        self.require_admin(session)
        try:
            with self._connect() as connection, connection.transaction():
                repository = IdentityRepository(connection, session.user.kindergarten_id)
                user = repository.set_status(user_id, status, actor_user_id=session.user.id)
                sessions_revoked = 0
                if status != "active":
                    sessions_revoked = repository.revoke_user_sessions(
                        user_id, reason="user_suspended"
                    )
                audit = AuditRepository(connection, session.user.kindergarten_id)
                audit.append(
                    event_code=(
                        IdentityAuditEventCode.USER_ACTIVATED
                        if status == "active"
                        else IdentityAuditEventCode.USER_DEACTIVATED
                    ),
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="user",
                    resource_id=user_id,
                    request_id=request_id,
                    outcome="success",
                )
                if sessions_revoked:
                    audit.append(
                        event_code=IdentityAuditEventCode.SESSION_REVOKED,
                        actor_user_id=session.user.id,
                        actor_role_codes=session.role_codes,
                        resource_type="user",
                        resource_id=user_id,
                        request_id=request_id,
                        outcome="success",
                        metadata={"reason": "user_suspended"},
                    )
                return self._managed(repository, user)
        except LookupError:
            raise IdentityError(404, "resource.not_found", "账号不存在。") from None
        except ValueError as exc:
            raise IdentityError(409, "identity.last_admin_required", str(exc)) from None

    def activate_user(
        self,
        session: SessionUser,
        user_id: UUID,
        *,
        verification_note: str | None,
        request_id: UUID | None,
    ) -> ManagedUser:
        self.require_admin(session)
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            user = repository.get_user(user_id, lock=True)
            if user is None:
                raise IdentityError(404, "resource.not_found", "账号不存在。")
            if user.status != "pending_verification":
                raise IdentityError(
                    409,
                    "identity.activation_state_conflict",
                    "账号尚未完成通行密钥登记或状态已变化。",
                )
            invitation = connection.execute(
                """SELECT i.id FROM account_invitations i
                JOIN webauthn_credentials c
                  ON c.kindergarten_id=i.kindergarten_id
                 AND c.id=i.registered_credential_id
                WHERE i.kindergarten_id=%s AND i.user_id=%s
                  AND i.consumed_at IS NOT NULL
                  AND c.user_id=i.user_id AND c.revoked_at IS NULL
                ORDER BY i.consumed_at DESC, i.id DESC
                LIMIT 1 FOR UPDATE OF i, c""",
                (session.user.kindergarten_id, user_id),
            ).fetchone()
            if invitation is None:
                raise IdentityError(
                    409,
                    "identity.activation_state_conflict",
                    "账号尚未完成通行密钥登记或状态已变化。",
                )
            repository.create_verification_approval(
                context_type="invitation",
                context_id=UUID(str(invitation[0])),
                user_id=user_id,
                approver_user_id=session.user.id,
                approver_kind="admin",
                approver_reference=str(session.user.id),
                note=verification_note,
                decided_at=datetime.now(UTC),
            )
            activated = repository.set_status(user_id, "active", actor_user_id=session.user.id)
            AuditRepository(connection, session.user.kindergarten_id).append(
                event_code=IdentityAuditEventCode.USER_ACTIVATED,
                actor_user_id=session.user.id,
                actor_role_codes=session.role_codes,
                resource_type="user",
                resource_id=user_id,
                request_id=request_id,
                outcome="success",
            )
            return self._managed(repository, activated)

    def list_credentials(
        self, session: SessionUser, user_id: UUID | None = None
    ) -> list[CredentialRecord]:
        target = user_id or session.user.id
        if target != session.user.id:
            self.require_admin(session)
        with self._connect() as connection:
            return IdentityRepository(connection, session.user.kindergarten_id).list_credentials(
                target
            )

    def rename_credential(
        self, session: SessionUser, credential_id: UUID, label: str
    ) -> CredentialRecord:
        self.require_recent_verification(session)
        with self._connect() as connection, connection.transaction():
            try:
                repository = IdentityRepository(connection, session.user.kindergarten_id)
                credential = repository.rename_credential(
                    session.user.id, credential_id, label.strip()
                )
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=IdentityAuditEventCode.CREDENTIAL_UPDATED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="webauthn_credential",
                    resource_id=credential_id,
                    outcome="success",
                )
                return credential
            except LookupError:
                raise IdentityError(404, "resource.not_found", "通行密钥不存在。") from None

    def revoke_own_credential(self, session: SessionUser, credential_id: UUID) -> None:
        self.require_recent_verification(session)
        try:
            with self._connect() as connection, connection.transaction():
                repository = IdentityRepository(connection, session.user.kindergarten_id)
                if not repository.revoke_credential(
                    session.user.id, credential_id, reason="user_revoked"
                ):
                    raise LookupError
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=IdentityAuditEventCode.CREDENTIAL_REVOKED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="webauthn_credential",
                    resource_id=credential_id,
                    outcome="success",
                    metadata={"reason": "user_revoked"},
                )
        except LookupError:
            raise IdentityError(404, "resource.not_found", "通行密钥不存在。") from None
        except ValueError as exc:
            raise IdentityError(409, "auth.last_credential", str(exc)) from None

    def issue_invitation(
        self, session: SessionUser, user_id: UUID, *, expires_in_hours: int
    ) -> tuple[InvitationRecord, str]:
        self.require_admin(session)
        material = issue_secret(SecretPurpose.INVITATION)
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            if repository.get_user(user_id) is None:
                raise IdentityError(404, "resource.not_found", "账号不存在。")
            record = repository.create_invitation(
                user_id=user_id,
                issued_by=session.user.id,
                token_hash=material.record.digest,
                expires_at=datetime.now(UTC) + timedelta(hours=expires_in_hours),
            )
            AuditRepository(connection, session.user.kindergarten_id).append(
                event_code=IdentityAuditEventCode.INVITATION_ISSUED,
                actor_user_id=session.user.id,
                actor_role_codes=session.role_codes,
                resource_type="account_invitation",
                resource_id=record.id,
                outcome="success",
            )
            return record, material.secret

    def list_invitations(self, session: SessionUser, user_id: UUID) -> list[InvitationRecord]:
        self.require_admin(session)
        with self._connect() as connection:
            return IdentityRepository(connection, session.user.kindergarten_id).list_invitations(
                user_id
            )

    def revoke_invitation(self, session: SessionUser, user_id: UUID, invitation_id: UUID) -> None:
        self.require_admin(session)
        with self._connect() as connection, connection.transaction():
            IdentityRepository(connection, session.user.kindergarten_id).revoke_invitation(
                user_id, invitation_id
            )
            AuditRepository(connection, session.user.kindergarten_id).append(
                event_code=IdentityAuditEventCode.INVITATION_REVOKED,
                actor_user_id=session.user.id,
                actor_role_codes=session.role_codes,
                resource_type="account_invitation",
                resource_id=invitation_id,
                outcome="success",
            )

    def admin_revoke_credential(
        self, session: SessionUser, user_id: UUID, credential_id: UUID
    ) -> tuple[int, tuple[InvitationRecord, str] | None]:
        self.require_admin(session)
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            user = repository.get_user(user_id)
            if user is None:
                raise IdentityError(404, "resource.not_found", "账号不存在。")
            credentials = repository.list_credentials(user_id, lock=True)
            if not any(item.id == credential_id for item in credentials):
                raise IdentityError(404, "resource.not_found", "通行密钥不存在。")
            if len(credentials) == 1 and not repository.can_deactivate(user_id):
                raise IdentityError(
                    409,
                    "auth.last_credential",
                    "不能撤销最后一名有效管理员的最后一个通行密钥。",
                )
            repository.revoke_credential(
                user_id, credential_id, reason="admin_revoked", allow_last=True
            )
            sessions = repository.revoke_user_sessions(user_id, reason="credential_revoked")
            audit = AuditRepository(connection, session.user.kindergarten_id)
            audit.append(
                event_code=IdentityAuditEventCode.CREDENTIAL_REVOKED,
                actor_user_id=session.user.id,
                actor_role_codes=session.role_codes,
                resource_type="webauthn_credential",
                resource_id=credential_id,
                outcome="success",
                metadata={"reason": "admin_revoked"},
            )
            if sessions:
                audit.append(
                    event_code=IdentityAuditEventCode.SESSION_REVOKED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="user",
                    resource_id=user_id,
                    outcome="success",
                    metadata={"reason": "credential_revoked"},
                )
            reinvitation: tuple[InvitationRecord, str] | None = None
            if repository.credential_count(user_id) == 0:
                repository.set_status(
                    user_id, "pending_registration", actor_user_id=session.user.id
                )
                material = issue_secret(SecretPurpose.INVITATION)
                invitation = repository.create_invitation(
                    user_id=user_id,
                    issued_by=session.user.id,
                    token_hash=material.record.digest,
                    expires_at=datetime.now(UTC) + timedelta(hours=24),
                )
                reinvitation = invitation, material.secret
                audit.append(
                    event_code=IdentityAuditEventCode.INVITATION_ISSUED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="account_invitation",
                    resource_id=invitation.id,
                    outcome="success",
                    metadata={"reason": "last_credential_revoked"},
                )
            return sessions, reinvitation

    def submit_recovery_request(self, *, login: str, recovery_code: str) -> bool:
        normalized = self.safe_login_key(login)
        with self._connect() as connection, connection.transaction():
            kindergarten_id = self._optional_kindergarten_id(connection)
            if kindergarten_id is None:
                return False
            repository = IdentityRepository(connection, kindergarten_id)
            user = repository.find_user_by_login(normalized) if normalized else None
            if user is None:
                return False
            digest = sha256(f"child-manager:recovery_code:{recovery_code}".encode()).hexdigest()
            code_id = repository.find_recovery_code(user.id, digest)
            if code_id is None or not repository.consume_recovery_code(code_id):
                return False
            recovery_request_id = repository.create_recovery_request(
                user_id=user.id,
                recovery_code_id=code_id,
                expires_at=datetime.now(UTC) + timedelta(hours=24),
            )
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.RECOVERY_REQUESTED,
                actor_user_id=user.id,
                actor_role_codes=repository.roles_for_user(user.id),
                resource_type="account_recovery_request",
                resource_id=recovery_request_id,
                outcome="success",
            )
            return True

    def list_recovery_requests(
        self, session: SessionUser, user_id: UUID
    ) -> list[RecoveryRequestRecord]:
        self.require_admin(session)
        with self._connect() as connection:
            return IdentityRepository(
                connection, session.user.kindergarten_id
            ).list_recovery_requests(user_id)

    def approve_recovery_request(
        self,
        session: SessionUser,
        user_id: UUID,
        request_id: UUID,
        *,
        verification_note: str | None,
    ) -> tuple[str, datetime]:
        self.require_admin(session)
        material = issue_secret(SecretPurpose.RECOVERY_ENROLLMENT)
        expires_at = datetime.now(UTC) + timedelta(minutes=15)
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            try:
                if not repository.can_deactivate(user_id):
                    raise IdentityError(
                        409,
                        "identity.last_admin_recovery_requires_cli",
                        "最后管理员恢复必须改由部署控制台完成双人核验。",
                    )
            except LookupError:
                raise IdentityError(
                    409, "identity.recovery_state_conflict", "恢复申请状态已变化。"
                ) from None
            if not repository.approve_recovery_request(
                user_id, request_id, token_hash=material.record.digest, expires_at=expires_at
            ):
                raise IdentityError(409, "identity.recovery_state_conflict", "恢复申请状态已变化。")
            repository.create_verification_approval(
                context_type="recovery",
                context_id=request_id,
                user_id=user_id,
                approver_user_id=session.user.id,
                approver_kind="admin",
                approver_reference=str(session.user.id),
                note=verification_note,
                decided_at=datetime.now(UTC),
            )
            AuditRepository(connection, session.user.kindergarten_id).append(
                event_code=IdentityAuditEventCode.RECOVERY_APPROVED,
                actor_user_id=session.user.id,
                actor_role_codes=session.role_codes,
                resource_type="account_recovery_request",
                resource_id=request_id,
                outcome="success",
            )
        return material.secret, expires_at

    def rotate_recovery_code(self, session: SessionUser) -> tuple[str, datetime]:
        self.require_recent_verification(session)
        material = issue_secret(SecretPurpose.RECOVERY_CODE)
        issued_at = datetime.now(UTC)
        with self._connect() as connection, connection.transaction():
            IdentityRepository(connection, session.user.kindergarten_id).rotate_recovery_code(
                session.user.id, code_hash=material.record.digest
            )
            AuditRepository(connection, session.user.kindergarten_id).append(
                event_code=IdentityAuditEventCode.RECOVERY_CODE_ROTATED,
                actor_user_id=session.user.id,
                actor_role_codes=session.role_codes,
                resource_type="user",
                resource_id=session.user.id,
                outcome="success",
                metadata={"reason": "user_rotated"},
            )
        return material.secret, issued_at

    def list_sessions(self, session: SessionUser):
        with self._connect() as connection:
            return IdentityRepository(connection, session.user.kindergarten_id).list_sessions(
                session.user.id
            )

    def revoke_session(self, session: SessionUser, family_id: UUID) -> bool:
        with self._connect() as connection, connection.transaction():
            repository = IdentityRepository(connection, session.user.kindergarten_id)
            count = repository.revoke_session(session.user.id, family_id, reason="user_revoked")
            if count:
                AuditRepository(connection, session.user.kindergarten_id).append(
                    event_code=IdentityAuditEventCode.SESSION_REVOKED,
                    actor_user_id=session.user.id,
                    actor_role_codes=session.role_codes,
                    resource_type="refresh_family",
                    resource_id=family_id,
                    outcome="success",
                    metadata={"reason": "user_revoked"},
                )
        return count > 0
