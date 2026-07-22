# Child Manager 架构决策记录

本目录保存 Child Manager 已接受的架构决策记录（Architecture Decision Record，ADR）。ADR 解释“为什么这样设计”，[`docs/design/system-architecture.md`](../design/system-architecture.md) 说明这些决策组合后的整体架构，PRD 则定义用户行为与验收结果。

## 状态约定

- `提议`：尚未确认，不得作为实现基线。
- `已接受`：当前实现必须遵守。
- `部分被取代`：部分条款由后续 ADR 替代，未明确取代的条款继续有效。
- `已取代`：由后续 ADR 替代，保留历史背景。
- `已废弃`：不再适用，且没有直接替代方案。

任何 ADR 状态变化都应通过新增 ADR 完成，并在新旧记录中建立双向链接。不要直接重写已接受 ADR 的历史取舍；文字勘误除外。

## 决策索引

| ADR | 决策 | 状态 |
| --- | --- | --- |
| [ADR-0001](ADR-0001-cloud-only.md) | 只交付 Cloud 版本，首期单园运行并保留园所隔离边界 | 已接受 |
| [ADR-0002](ADR-0002-separate-web-api-worker-modular-monolith.md) | 采用独立 Web、API、Worker 运行单元的模块化单体 | 已接受 |
| [ADR-0003](ADR-0003-postgresql-authoritative-dramatiq-redis-jobs.md) | PostgreSQL 保存任务权威状态，Dramatiq 与 Redis 负责异步执行 | 已接受 |
| [ADR-0004](ADR-0004-same-origin-cookie-authentication.md) | 采用同源入口、HttpOnly Cookie 与 API 统一授权 | 部分被 ADR-0010 取代（密码部分失效） |
| [ADR-0005](ADR-0005-provider-neutral-ai-and-central-prompts.md) | AI 供应商中立，并建立管理员专用提示词系统 | 已接受 |
| [ADR-0006](ADR-0006-fixed-word-template-export-boundary.md) | 一日活动计划采用固定 Word 模板导出边界 | 已接受 |
| [ADR-0007](ADR-0007-caddy-compose-and-file-secrets.md) | 采用 Caddy、Docker Compose 与文件挂载 Secrets | 已被 ADR-0009 取代（保留历史与安全结果） |
| [ADR-0008](ADR-0008-degradable-calendar-and-external-services.md) | 日期与外部服务采用本地优先和软降级 | 已接受 |
| [ADR-0009](ADR-0009-defer-production-deployment-until-feature-complete.md) | 功能完成前延后生产部署与访问网络决策 | 部分被 ADR-0010 取代（生产部署延后继续有效） |
| [ADR-0010](ADR-0010-restricted-public-entry-passkey-authentication-and-recovery.md) | 采用受限公网 B/S 入口、WebAuthn 通行密钥与双条件恢复 | 已接受 |

## 与旧仓库 ADR 的关系

旧仓库 `ywyz/kindergartenManager` 的 ADR 只作为历史经验，不延续其编号或状态。本目录重新从 `ADR-0001` 编号，因为这是独立项目的决策历史。

旧仓库中仍可吸收的经验包括固定 Word 模板、结构化 AI 输出、UI 不承载业务规则和工作日判断不阻断教案流程。以下旧决策已被本项目明确替代：

- 本地版优先和离线运行。
- NiceGUI 直接调用业务服务与数据库的一体化进程。
- SQLite 作为正式产品存储，未来再迁移 PostgreSQL。
- 本地 keyring、用户数据目录和本机文件管理方案。
- 在线节假日 API 优先或不可用时伪装成普通工作日。

## 新增 ADR 的判断标准

满足以下任一条件时应新增 ADR：

- 方案会影响多个业务模块或部署单元。
- 变更代价高，涉及数据迁移、安全边界或外部兼容。
- 存在两个以上合理方案，且取舍需要长期保留。
- 决策会改变已有 ADR、系统架构或实现分支共同基线。

局部类名、普通依赖升级、可逆的页面布局和单个接口字段通常不需要 ADR。
