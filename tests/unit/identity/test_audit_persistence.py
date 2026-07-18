"""审计持久化测试：关键身份事件在失败路径下仍写入 audit_events。"""

from collections.abc import Iterator

import pytest
from sqlalchemy import func, select

from packages.backend.audit.models import AuditEvent
from packages.backend.database import session as session_module
from packages.backend.identity.service import IdentityService
from packages.contracts import audit as audit_events


@pytest.fixture(autouse=True)
def _set_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    from packages.backend.config import settings

    monkeypatch.setattr(
        settings,
        "jwt_signing_key",
        "test-jwt-signing-key-32bytes-long-12345",
        raising=False,
    )
    monkeypatch.setattr(
        settings,
        "csrf_signing_key",
        "test-csrf-signing-key-32bytes-long-1234",
        raising=False,
    )


@pytest.fixture
def service(migrated_database_url: str) -> Iterator[IdentityService]:
    """在已迁移的隔离 schema 上构造 IdentityService。"""
    session = session_module.SessionLocal()
    try:
        yield IdentityService(session)
    finally:
        session.close()


@pytest.fixture
def kindergarten(service: IdentityService):
    result = service.init_admin(
        kg_name="审计测试园", admin_username="admin", password="ValidPassword2024!"
    )
    _commit(service)
    return result["kindergarten_id"]


def _audit_count(session, kindergarten_id: str, event_code: str) -> int:
    stmt = select(func.count(AuditEvent.id)).where(
        AuditEvent.kindergarten_id == kindergarten_id,
        AuditEvent.event_code == event_code,
    )
    return int(session.execute(stmt).scalar() or 0)


def _commit(service: IdentityService) -> None:
    service._session.commit()


def test_login_failure_audit_persisted(service: IdentityService, kindergarten: str) -> None:
    result = service.authenticate(username="admin", password="wrong-password")
    assert result is None
    _commit(service)

    count = _audit_count(service._session, kindergarten, audit_events.IDENTITY_LOGIN)
    assert count >= 1


def test_refresh_replay_audit_persisted(service: IdentityService, kindergarten: str) -> None:
    login = service.login(username="admin", password="ValidPassword2024!")
    assert login is not None
    _commit(service)

    old_refresh = login.refresh_value
    first = service.refresh(refresh_cookie=old_refresh)
    assert first is not None
    _commit(service)

    replay = service.refresh(refresh_cookie=old_refresh)
    assert replay is None
    _commit(service)

    count = _audit_count(service._session, kindergarten, audit_events.IDENTITY_TOKEN_REPLAY)
    assert count == 1


def test_init_admin_audit_persisted(service: IdentityService) -> None:
    result = service.init_admin(
        kg_name="初始化审计园", admin_username="admin", password="ValidPassword2024!"
    )
    _commit(service)
    kg_id = result["kindergarten_id"]

    count = _audit_count(service._session, kg_id, audit_events.IDENTITY_INIT_ADMIN)
    assert count == 1
