"""登录标识规范化。"""

import re
import unicodedata

_MAINLAND_PHONE = re.compile(r"^1[3-9]\d{9}$")


def normalize_username(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    if not normalized:
        raise ValueError("用户名不能为空")
    if len(normalized) > 120:
        raise ValueError("用户名不能超过 120 个字符")
    return normalized


def normalize_phone(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    compact = re.sub(r"[\s-]", "", unicodedata.normalize("NFKC", value))
    national = compact[3:] if compact.startswith("+86") else compact
    if not _MAINLAND_PHONE.fullmatch(national):
        raise ValueError("手机号必须是有效的中国大陆手机号")
    return f"+86{national}"
