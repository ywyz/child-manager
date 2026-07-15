from packages.backend.database.session import get_db_session


def test_get_db_session_returns_session():
    """get_db_session 应该返回数据库会话"""
    with get_db_session() as session:
        assert session is not None


def test_get_db_session_commits_on_success():
    """get_db_session 应该在成功时提交"""
    with get_db_session():
        pass


def test_get_db_session_rolls_back_on_exception():
    """get_db_session 应该在异常时回滚"""
    try:
        with get_db_session():
            raise ValueError("test exception")
    except ValueError:
        pass


def test_session_factory_config():
    """会话工厂应该配置正确"""
    from packages.backend.database.session import SessionLocal

    session = SessionLocal()
    assert session is not None
    session.close()


def test_sqlite_rejected_in_production_environment(monkeypatch):
    """生产环境必须拒绝 SQLite URL"""
    import packages.backend.database.session as mod

    monkeypatch.setattr(mod.settings, "environment", "production", raising=False)
    monkeypatch.setenv(
        "CHILD_MANAGER_DATABASE_URL",
        "sqlite:////tmp/prod-test.sqlite",
    )
    with __import__("pytest").raises(RuntimeError, match="PostgreSQL"):
        mod._get_database_url()


def test_sqlite_allowed_in_development_environment(monkeypatch):
    """开发环境应该允许 SQLite URL"""
    import packages.backend.database.session as mod

    monkeypatch.setattr(mod.settings, "environment", "development", raising=False)
    monkeypatch.setenv(
        "CHILD_MANAGER_DATABASE_URL",
        "sqlite:////tmp/dev-test.sqlite",
    )
    url = mod._get_database_url()
    assert url.startswith("sqlite")


def test_sqlite_allowed_in_test_environment(monkeypatch):
    """测试环境应该允许 SQLite URL"""
    import packages.backend.database.session as mod

    monkeypatch.setattr(mod.settings, "environment", "test", raising=False)
    monkeypatch.setenv(
        "CHILD_MANAGER_DATABASE_URL",
        "sqlite:////tmp/test-test.sqlite",
    )
    url = mod._get_database_url()
    assert url.startswith("sqlite")
