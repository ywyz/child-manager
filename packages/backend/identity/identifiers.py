"""用户名、手机号等身份标识规范化。"""

import re
import unicodedata

_USERNAME_PATTERN = re.compile(r"^[a-z0-9._@\-]+$")


def normalize_username(value: str) -> str:
    """返回规范化用户名：NFKC、去首尾空白、小写。"""
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    if not normalized:
        msg = "用户名不能为空"
        raise ValueError(msg)
    return normalized


def normalize_phone(value: str | None) -> str | None:
    """返回 E.164 手机号或空值；当前只接受中国大陆手机号。"""
    if value is None:
        return None
    cleaned = value.strip().replace(" ", "").replace("-", "")
    if cleaned == "":
        return None

    if cleaned.startswith("+"):
        digits = cleaned
    else:
        digits = "+86" + cleaned

    if not re.fullmatch(r"\+86[1-9]\d{10}", digits):
        msg = "手机号格式无效"
        raise ValueError(msg)
    return digits
