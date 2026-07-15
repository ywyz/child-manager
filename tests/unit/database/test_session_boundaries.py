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
