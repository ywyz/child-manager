"""API 测试共享 fixture。"""

from collections.abc import Iterator

import pytest

from packages.backend.database import session as session_module
from packages.backend.identity.passwords import hash_password
from packages.backend.identity.repository import IdentityRepository
from packages.backend.identity.service import IdentityService


@pytest.fixture(autouse=True)
def _seed_test_identity(migrated_database_url: str) -> Iterator[None]:
    """在已迁移的隔离 schema 中写入最小身份数据供 API 测试使用。"""
    session = session_module.SessionLocal()
    try:
        service = IdentityService(session)
        service.init_admin(
            kg_name="阳光幼儿园",
            admin_username="admin",
            password="ValidPassword2024!",
        )

        repo = IdentityRepository(session)
        kg = service._get_kindergarten()
        assert kg is not None
        admin_role = repo.get_role_by_code(kg.id, "admin")
        assert admin_role is not None

        disabled_user = repo.create_user(
            kindergarten_id=kg.id,
            username="disabled",
            phone=None,
            display_name="已停用账号",
            password_hash=hash_password("ValidPassword2024!"),
        )
        disabled_user.is_active = False
        repo.assign_role(
            kindergarten_id=kg.id,
            user_id=disabled_user.id,
            role_id=admin_role.id,
        )

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    yield
