"""Alembic 迁移环境。

模块级代码需兼容两种导入方式：
1. alembic.command.upgrade/downgrade 调用时，context.config 已设置
2. 测试通过 patch 直接导入本模块时，context.config 为 None
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from packages.backend.database.session import Base

config = getattr(context, "config", None)

if config is not None and config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str | None:
    return os.environ.get("CHILD_MANAGER_DATABASE_URL")


def run_migrations_offline() -> None:
    url = get_database_url()
    if url is None and config is not None:
        url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise RuntimeError("未配置数据库 URL，无法运行迁移")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    database_url = get_database_url()
    if database_url:
        from sqlalchemy import create_engine

        connectable = create_engine(database_url, poolclass=pool.NullPool)
    elif config is not None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    else:
        raise RuntimeError("未配置数据库 URL，无法运行迁移")

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if config is not None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
