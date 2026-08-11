from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from types import ModuleType
from typing import Any

import pytest


def implemented[T](call: Callable[[], T]) -> T:
    """把明确的未实现接口记为业务 RED；其他异常仍按环境/代码错误暴露。"""

    try:
        return call()
    except NotImplementedError as error:
        pytest.fail(f"SLICE1_RED: {error}", pytrace=False)


def pending_module(module_name: str) -> ModuleType:
    """把计划中的 Slice 2A 模块缺失转换为可诊断 RED，而非 collection error。"""

    try:
        return import_module(module_name)
    except ModuleNotFoundError as error:
        missing = error.name or ""
        if missing == module_name or module_name.startswith(f"{missing}."):
            pytest.fail(f"SLICE2A_RED: 尚未实现公开模块 {module_name}", pytrace=False)
        raise


def pending_symbol(module: ModuleType, symbol_name: str) -> Any:
    """允许后续 GREEN 逐步增加公开 seam，同时保持缺失符号为 clean RED。"""

    try:
        return getattr(module, symbol_name)
    except AttributeError:
        pytest.fail(
            f"SLICE2A_RED: {module.__name__} 尚未实现公开符号 {symbol_name}",
            pytrace=False,
        )
