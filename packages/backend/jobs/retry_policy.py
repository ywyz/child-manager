"""M4 执行型 AI 任务共享重试上限。"""

from hashlib import sha256
from uuid import UUID

MAX_AI_ATTEMPTS = 3
RETRY_DELAYS_SECONDS = (5, 30)
MAX_RETRY_AFTER_SECONDS = 60
JITTER_RATIO = 0.2
RETRYABLE_AI_ERROR_CODES = frozenset(
    {
        "ai.timeout",
        "ai.unavailable",
        "ai.rate_limited",
        "ai.provider_error",
        "ai.invalid_response",
        "ai.response_too_large",
    }
)


def cap_retry_after_seconds(value: int | None) -> int | None:
    if value is None:
        return None
    return min(value, MAX_RETRY_AFTER_SECONDS)


def is_retryable_ai_error(code: str) -> bool:
    return code in RETRYABLE_AI_ERROR_CODES


def retry_delay_seconds(job_id: UUID, *, attempt_count: int) -> int:
    """按任务与尝试次数生成可复现的有界抖动，便于恢复与确定性测试。"""

    base = RETRY_DELAYS_SECONDS[min(max(attempt_count - 1, 0), len(RETRY_DELAYS_SECONDS) - 1)]
    digest = sha256(f"{job_id}:{attempt_count}".encode()).digest()
    unit = digest[0] / 255
    multiplier = (1 - JITTER_RATIO) + (2 * JITTER_RATIO * unit)
    return max(1, round(base * multiplier))
