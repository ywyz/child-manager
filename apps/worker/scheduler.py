"""待投递任务恢复扫描的稳定时间契约。"""

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

PENDING_DISPATCH_SCAN_SECONDS = 15
EXPIRED_LEASE_SCAN_SECONDS = 30
PROMPT_TEST_RECOVERY_LIMIT = 100

logger = logging.getLogger(__name__)


class AiRecoveryStore(Protocol):
    def reserve_recoverable_jobs(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]: ...


class AiResultMaintenanceRepository(Protocol):
    def expire_due_previews(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
    ) -> int: ...

    def clear_retained_content(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
    ) -> int: ...


@dataclass(frozen=True, slots=True)
class AiResultMaintenanceCounts:
    expired: int
    content_cleared: int


def run_ai_recovery_scan(
    *,
    store: AiRecoveryStore,
    dispatch: Callable[[UUID], None],
    kindergarten_ids: Iterable[UUID],
    now: datetime | None = None,
    limit: int = 100,
    include_expired: bool = True,
) -> int:
    """从 PostgreSQL 预留可恢复任务后逐项投递，单项失败不阻断后续任务。"""

    effective_now = now or datetime.now(UTC)
    dispatched = 0
    for kindergarten_id in kindergarten_ids:
        try:
            job_ids = store.reserve_recoverable_jobs(
                kindergarten_id,
                now=effective_now,
                limit=limit,
                include_expired=include_expired,
            )
        except Exception as exc:
            logger.error(
                "AI 任务恢复扫描失败",
                extra={
                    "kindergarten_id": str(kindergarten_id),
                    "exception_type": type(exc).__name__,
                },
            )
            continue
        for job_id in job_ids:
            try:
                dispatch(job_id)
            except Exception as exc:
                logger.error(
                    "AI 任务恢复投递失败",
                    extra={
                        "job_id": str(job_id),
                        "exception_type": type(exc).__name__,
                    },
                )
                continue
            dispatched += 1
    return dispatched


def run_ai_result_maintenance(
    *,
    repository: AiResultMaintenanceRepository,
    kindergarten_ids: Iterable[UUID],
    now: datetime | None = None,
    limit_per_kindergarten: int = 100,
) -> AiResultMaintenanceCounts:
    """逐园执行预览过期和正文清理，并只记录计数。"""

    effective_now = now or datetime.now(UTC)
    expired = 0
    content_cleared = 0
    for kindergarten_id in kindergarten_ids:
        try:
            kindergarten_expired = repository.expire_due_previews(
                kindergarten_id,
                now=effective_now,
                limit=limit_per_kindergarten,
            )
            kindergarten_cleared = repository.clear_retained_content(
                kindergarten_id,
                now=effective_now,
                limit=limit_per_kindergarten,
            )
        except Exception as exc:
            logger.error(
                "AI 园所结果维护失败",
                extra={
                    "kindergarten_id": str(kindergarten_id),
                    "exception_type": type(exc).__name__,
                },
            )
            continue
        expired += kindergarten_expired
        content_cleared += kindergarten_cleared
        logger.info(
            "AI 园所结果维护完成",
            extra={
                "kindergarten_id": str(kindergarten_id),
                "expired_count": kindergarten_expired,
                "content_cleared_count": kindergarten_cleared,
            },
        )
    counts = AiResultMaintenanceCounts(
        expired=expired,
        content_cleared=content_cleared,
    )
    logger.info(
        "AI 结果维护完成",
        extra={
            "expired_count": counts.expired,
            "content_cleared_count": counts.content_cleared,
        },
    )
    return counts
