import os
import sys
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def _is_testing() -> bool:
    return os.environ.get("CHILD_MANAGER_TESTING") == "1" or "pytest" in sys.modules


def _get_database_url() -> str:
    url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    if not url:
        raise RuntimeError("未配置 CHILD_MANAGER_DATABASE_URL；必须显式配置 PostgreSQL 连接串")
    if not _is_testing() and not url.startswith("postgresql"):
        raise RuntimeError("生产/开发环境必须使用 PostgreSQL；SQLite 仅限自动化测试")
    return url


engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
