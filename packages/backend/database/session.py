import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def _get_database_url() -> str:
    url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    if not url:
        raise RuntimeError(
            "未配置 CHILD_MANAGER_DATABASE_URL；生产环境必须显式配置 PostgreSQL 连接串"
        )
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
