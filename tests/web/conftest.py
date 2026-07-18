"""Web 测试共享 fixture。

不直接使用 nicegui.testing.plugin（它会无条件导入 selenium），而是按需导入
user_simulation 提供 User 对象。
"""

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from nicegui.testing.user import User
from nicegui.testing.user_simulation import user_simulation


@pytest_asyncio.fixture
async def user() -> AsyncGenerator[User]:
    main_file = Path(__file__).with_name("main.py").resolve()
    async with user_simulation(main_file=main_file) as u:
        yield u
