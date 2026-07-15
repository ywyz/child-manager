import os


def require_test_database_url() -> str:
    value = os.environ.get("CHILD_MANAGER_TEST_DATABASE_URL")
    if not value:
        raise RuntimeError("必须设置 CHILD_MANAGER_TEST_DATABASE_URL 并指向隔离测试数据库")
    return value
