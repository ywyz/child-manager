"""公开身份 ceremony 的来源限流公共 seam。"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
from math import ceil
from threading import Lock

from redis import Redis

GLOBAL_THROTTLE_SOURCE = "__global__"
SUBJECT_THROTTLE_SOURCE_PREFIX = "__subject__:"


def subject_throttle_source(*, purpose: str, subject: str) -> str:
    digest = sha256(f"child-manager:{purpose}:{subject}".encode()).hexdigest()
    return f"{SUBJECT_THROTTLE_SOURCE_PREFIX}{digest}"


@dataclass(frozen=True)
class ThrottleDecision:
    allowed: bool
    retry_after_seconds: int = 0


class MemoryAuthThrottle:
    """按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。"""

    def __init__(
        self,
        *,
        failure_limit: int,
        window: timedelta,
        subject_failure_limit: int | None = None,
        global_failure_limit: int | None = None,
    ) -> None:
        if (
            min(
                failure_limit,
                subject_failure_limit if subject_failure_limit is not None else failure_limit,
                global_failure_limit if global_failure_limit is not None else failure_limit,
            )
            < 1
        ):
            raise ValueError("身份限流阈值必须为正整数")
        self._failure_limit = failure_limit
        self._subject_failure_limit = (
            subject_failure_limit if subject_failure_limit is not None else failure_limit
        )
        self._global_failure_limit = (
            global_failure_limit if global_failure_limit is not None else failure_limit
        )
        self._window = window
        self._failures: dict[tuple[str, str], list[datetime]] = {}
        self._lock = Lock()

    def check(self, *, source: str, purpose: str, now: datetime) -> ThrottleDecision:
        with self._lock:
            failures = self._active_failures(source, purpose, now)
            if len(failures) < self._limit_for(source):
                return ThrottleDecision(allowed=True)
            retry_after = max(1, ceil((failures[0] + self._window - now).total_seconds()))
            return ThrottleDecision(allowed=False, retry_after_seconds=retry_after)

    def _limit_for(self, source: str) -> int:
        if source == GLOBAL_THROTTLE_SOURCE:
            return self._global_failure_limit
        if source.startswith(SUBJECT_THROTTLE_SOURCE_PREFIX):
            return self._subject_failure_limit
        return self._failure_limit

    def record_failure(self, *, source: str, purpose: str, now: datetime) -> None:
        with self._lock:
            failures = self._active_failures(source, purpose, now)
            failures.append(now)
            self._failures[(source, purpose)] = failures

    def record_success(self, *, source: str, purpose: str, now: datetime) -> None:
        del now
        with self._lock:
            self._failures.pop((source, purpose), None)

    def _active_failures(self, source: str, purpose: str, now: datetime) -> list[datetime]:
        cutoff = now - self._window
        failures = [value for value in self._failures.get((source, purpose), []) if value > cutoff]
        if failures:
            self._failures[(source, purpose)] = failures
        else:
            self._failures.pop((source, purpose), None)
        return failures


class RedisAuthThrottle:
    """多进程 API 使用的 Redis 固定窗口实现。"""

    def __init__(
        self,
        redis: Redis,
        *,
        failure_limit: int,
        window: timedelta,
        subject_failure_limit: int | None = None,
        global_failure_limit: int | None = None,
    ) -> None:
        if (
            min(
                failure_limit,
                subject_failure_limit if subject_failure_limit is not None else failure_limit,
                global_failure_limit if global_failure_limit is not None else failure_limit,
            )
            < 1
        ):
            raise ValueError("身份限流阈值必须为正整数")
        self._redis = redis
        self._failure_limit = failure_limit
        self._subject_failure_limit = (
            subject_failure_limit if subject_failure_limit is not None else failure_limit
        )
        self._global_failure_limit = (
            global_failure_limit if global_failure_limit is not None else failure_limit
        )
        self._window_seconds = max(1, ceil(window.total_seconds()))

    def _key(self, source: str, purpose: str) -> str:
        source_digest = sha256(source.encode()).hexdigest()
        return f"child-manager:auth-throttle:{purpose}:{source_digest}"

    def check(self, *, source: str, purpose: str, now: datetime) -> ThrottleDecision:
        del now
        key = self._key(source, purpose)
        count = int(self._redis.get(key) or 0)
        if count < self._limit_for(source):
            return ThrottleDecision(allowed=True)
        ttl = self._redis.ttl(key)
        return ThrottleDecision(allowed=False, retry_after_seconds=max(1, ttl))

    def _limit_for(self, source: str) -> int:
        if source == GLOBAL_THROTTLE_SOURCE:
            return self._global_failure_limit
        if source.startswith(SUBJECT_THROTTLE_SOURCE_PREFIX):
            return self._subject_failure_limit
        return self._failure_limit

    def record_failure(self, *, source: str, purpose: str, now: datetime) -> None:
        del now
        key = self._key(source, purpose)
        with self._redis.pipeline() as pipeline:
            pipeline.incr(key)
            pipeline.expire(key, self._window_seconds, nx=True)
            pipeline.execute()

    def record_success(self, *, source: str, purpose: str, now: datetime) -> None:
        del now
        self._redis.delete(self._key(source, purpose))
