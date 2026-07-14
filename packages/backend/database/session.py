"""应用事务边界骨架。"""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

SessionFactory = Callable[[], AsyncSession]


@asynccontextmanager
async def transactional_session(
    session_factory: async_sessionmaker[AsyncSession] | SessionFactory,
) -> AsyncIterator[AsyncSession]:
    """由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。"""

    session = session_factory()
    try:
        async with session.begin():
            yield session
    finally:
        await session.close()
