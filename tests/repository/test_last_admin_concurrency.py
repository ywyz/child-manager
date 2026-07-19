"""最后管理员并发保护：双事务 PostgreSQL 回归测试。

模拟两个并发管理员事务同时尝试移除最后一个有效管理员：
使用两个独立数据库连接同时打开事务并 SELECT FOR UPDATE，
验证只有一个事务能成功提交，另一个被 LastAdminError 拒绝，
最终仍保留恰好一名有效管理员。
"""

import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from packages.backend.identity.exceptions import LastAdminError
from packages.backend.identity.repository import IdentityRepository
from packages.backend.identity.service import IdentityService
from tests.conftest import IS_POSTGRESQL


@pytest.fixture
def isolated_engine(isolated_database_url: str) -> Iterator:
    engine = create_engine(isolated_database_url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        engine.dispose()


def _seed_two_admins(database_url: str) -> tuple[str, str, str]:
    """在隔离 schema 中初始化园所并创建两名有效管理员，返回 (kg_id, admin1_id, admin2_id)。"""
    from alembic.command import upgrade
    from alembic.config import Config

    os.environ["CHILD_MANAGER_DATABASE_URL"] = database_url
    config = Config("alembic.ini")
    upgrade(config, "head")

    engine = create_engine(database_url)
    session_local = sessionmaker(bind=engine)
    session = session_local()
    try:
        service = IdentityService(session)
        init_result = service.init_admin(
            kg_name="双事务测试园", admin_username="admin1", password="ValidPassword2024!"
        )
        session.commit()
        kg_id = init_result["kindergarten_id"]
        admin1_id = init_result["user_id"]

        repo = IdentityRepository(session)
        admin_role = repo.get_role_by_code("admin")
        assert admin_role is not None
        admin2 = repo.create_user(
            kindergarten_id=kg_id,
            username="admin2",
            username_normalized="admin2",
            phone_e164=None,
            display_name="管理员二",
            password_hash="$2b$12$placeholderhashfortestonlyvalue",
        )
        repo.assign_role(
            kindergarten_id=kg_id,
            user_id=admin2.id,
            role_id=admin_role.id,
            assigned_by=admin1_id,
        )
        session.commit()
        return kg_id, admin1_id, str(admin2.id)
    finally:
        session.close()
        engine.dispose()


def _build_current_user(service: IdentityService, kg_id: str, user_id: str):
    user = service.get_user_by_id(kg_id, user_id)
    assert user is not None
    return service.build_current_user(user)


@pytest.mark.skipif(not IS_POSTGRESQL, reason="最后管理员双事务并发需要 PostgreSQL 行锁")
def test_concurrent_deactivate_last_admins_keeps_one(
    isolated_database_url: str,
) -> None:
    """并发停用最后两名管理员：一个成功，一个被拒绝，最终保留 1 名。"""
    kg_id, admin1_id, admin2_id = _seed_two_admins(isolated_database_url)

    def deactivate_admin(admin_id: str) -> bool:
        """在独立连接/事务中停用指定管理员，返回是否成功。"""
        engine = create_engine(isolated_database_url)
        session_local = sessionmaker(bind=engine)
        session = session_local()
        try:
            service = IdentityService(session)
            admin_user_response = service.get_user(kg_id, admin_id)
            assert admin_user_response is not None
            # 直接调用 deactivate_user 触发 SELECT FOR UPDATE 保护的最后管理员检查。
            service.deactivate_user(
                kindergarten_id=kg_id,
                admin_user=_build_current_user(service, kg_id, admin_id),
                user_id=admin_id,
            )
            session.commit()
            return True
        except LastAdminError:
            session.rollback()
            return False
        finally:
            session.close()
            engine.dispose()

    with ThreadPoolExecutor(max_workers=2) as pool:
        future_a = pool.submit(deactivate_admin, admin1_id)
        future_b = pool.submit(deactivate_admin, admin2_id)
        success_a = future_a.result()
        success_b = future_b.result()

    # 恰好一个事务成功提交，另一个被 LastAdminError 拒绝。
    assert (success_a, success_b) in {(True, False), (False, True)}, (
        f"期望一成功一失败，实际 success_a={success_a}, success_b={success_b}"
    )

    # 最终仍保留恰好一名有效管理员。
    engine = create_engine(isolated_database_url)
    session_local = sessionmaker(bind=engine)
    session = session_local()
    try:
        repo = IdentityRepository(session)
        active_admins = repo.get_active_admins_for_update(kg_id)
        assert len(active_admins) == 1, f"期望保留 1 名有效管理员，实际 {len(active_admins)}"
    finally:
        session.close()
        engine.dispose()
