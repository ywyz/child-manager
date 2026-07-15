import os


def require_test_database_url() -> str:
    """返回显式配置的测试数据库 URL。

    测试数据库必须在运行前通过环境变量显式指定，缺失时清晰失败，
    禁止静默回退到共享或内存数据库，以保证测试隔离可验证。
    """
    value = os.environ.get("CHILD_MANAGER_TEST_DATABASE_URL")
    if value:
        return value
    raise RuntimeError(
        "未配置 CHILD_MANAGER_TEST_DATABASE_URL；必须显式指定测试数据库连接串以使用隔离 schema"
    )
