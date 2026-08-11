from __future__ import annotations

from collections.abc import Callable

import pytest


def implemented[T](call: Callable[[], T]) -> T:
    """把明确的未实现接口记为业务 RED；其他异常仍按环境/代码错误暴露。"""

    try:
        return call()
    except NotImplementedError as error:
        pytest.fail(f"SLICE1_RED: {error}", pytrace=False)
