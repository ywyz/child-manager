# M1 工程骨架与质量基线 Issue 草稿与执行记录

> 草稿日期：2026-07-14
> 草稿复核基线：`ba81925a8b0a9f1a74951358bdf37cd45f8c529b`
> 草稿复核状态：`main...origin/main = 0/0`，M0 `complete`，M1 `ready`
> 执行结果：Issue #1～#3 与 `codex`、`trae` 已创建；共同基线为 `c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7`；M1 实现尚未授权
> 使用方式：以下三段保留创建时的草稿结构；实时状态、父子链接和共同基线以本执行记录及 GitHub Issues 为准。

## 0. 草稿基线与 graphify 处置记录

- 用户已在上一轮明确要求更新 graphify 并同步到 GitHub；既有图谱修改经完整性检查后以 `ba81925` 提交并推送，当前任务开始时工作区干净且 `main...origin/main = 0/0`。
- 本草稿与启动清单修改产生的新文档和 graphify 差异属于当前任务，不冒充既有用户修改；提交、推送、创建 Issue 和分支操作仍按独立授权边界处理。
- 草稿复核时 GitHub Issue 全部状态查询结果为 0 个，不存在重复 M1 Issue。
- 草稿复核验证：本地 Markdown 链接缺失 0，`git diff --check` 通过，graphify 为 1671 节点/1327 边，缺失端点、悬空边、自环、重复或折叠边均为 0。
- 当前 `main` 尚无业务实现，本次不运行或声称 Ruff、Pyright、Pytest、Docker及三个运行入口检查通过。
- 2026-07-14 执行时再次确认 `main...origin/main = 0/0`，并从 `c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7` 创建、推送 `codex` 与 `trae`。
- 已创建 [M1 共享父 Issue #1](https://github.com/ywyz/child-manager/issues/1)、[Codex 子 Issue #2](https://github.com/ywyz/child-manager/issues/2) 和 [Trae 子 Issue #3](https://github.com/ywyz/child-manager/issues/3)，#2、#3 已注册为 #1 的原生 Sub-issues。

## 1. 共享父 Issue 草稿

### 标题

`M1：工程骨架与质量基线（共享父 Issue）`

### 正文

#### 当前状态与基线

- 复核日期：2026-07-14。
- 草稿复核时 `main` HEAD：`ba81925a8b0a9f1a74951358bdf37cd45f8c529b`。
- 草稿复核时 `main...origin/main = 0/0`。
- M0 状态：`complete`；M1 状态：`ready`。
- 验证摘要：GitHub Issue 0 个；文档链接与格式检查通过；graphify 为 1671 节点/1327 边且完整性异常为 0；当前无业务代码，不适用实现分支质量命令。
- T003 已执行；两个实现子 Issue 均已记录共同基线 `c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7`。

#### 共同目标

- 建立 Python 3.14+ 项目、`pyproject.toml` 和 `uv.lock`。
- 建立独立的 NiceGUI Web、FastAPI API 和后台 Worker 运行入口。
- 建立 `packages/contracts`、`packages/backend` 工程骨架（skeleton）及明确的依赖方向。
- 配置 Ruff、Pyright、Pytest、OpenAPI 校验和 GitHub Actions 质量门禁。
- 为本地开发和自动化测试建立仅绑定回环地址的 PostgreSQL、Redis 最小依赖及健康检查。
- 建立结构化日志、请求 ID、追踪 ID、确定性测试替身和 Alembic/事务基础。

#### 任务映射

- T003：已从同一确认的 `main` 提交创建、推送 `codex` 与 `trae`，并记录共同基线。
- T004～T020：由 Codex、Trae 在各自实现子 Issue 中分别、完整、依赖有序地执行；不拆成 17 个独立 GitHub Issue。

#### 入口条件

- [x] M0 `complete`，M0-G1～M0-G8 已关闭。
- [x] M1 `ready`。
- [x] Spec、Plan、Tasks、ADR、模板说明和双 Agent 协议已形成共享文档基线。
- [x] GitHub Issue 操作已获得明确授权并完成。
- [x] T003 分支操作已获得明确授权并完成。
- [ ] M1 实现已获得明确授权。

#### 共同出口门禁

- [ ] `uv sync --locked` 可在干净环境完成。
- [ ] Web、API、Worker 三个运行入口可独立启动并返回存活状态。
- [ ] API 就绪检查可区分 PostgreSQL、Redis 和外部 AI 故障；AI 不可用不令 API 整体不就绪。
- [ ] 静态架构检查能够阻止 Web 导入 ORM、Repository 或 `packages/backend`。
- [ ] 两个实现分别通过 `uv sync --locked`、Ruff format check、Ruff check、Pyright 和 Pytest。
- [ ] 两个实现分别提供自己的专项检查、风险、阻塞和 graphify 更新证据。

#### 共享事实来源

- [AGENTS.md](../../AGENTS.md)
- [CONTEXT.md](../../CONTEXT.md)
- [README.md](../../README.md)
- [Roadmap M1](../ROADMAP.md#7-m1工程骨架与质量基线)
- [双 Agent 独立开发协议](dual-agent-development.md)
- [功能规格](../../specs/001-daily-activity-plan/spec.md)
- [实施计划](../../specs/001-daily-activity-plan/plan.md)
- [任务清单](../../specs/001-daily-activity-plan/tasks.md)
- [ADR 索引](../ADR/README.md)
- [Word 模板说明](../../templates/teacherplan/一日活动计划系统说明.md)
- [Word 模板](../../templates/teacherplan/teacherplan.docx)

#### 协作边界

- 只读交叉评审遵循双 Agent 协议第 5.4 节。
- 共享文档同步遵循第 6 节，只在 `main` 确认后按授权分别同步。
- 规格冲突或高影响歧义遵循第 7 节，冻结受影响工作并由用户确认。
- 两个实现不得互相合并、cherry-pick 或复制实现，也不得把对方验证当作自己的证据。

#### 实现子 Issue

| 实现 | Issue | 状态 | 共同基线 |
| --- | --- | --- | --- |
| Codex | [#2](https://github.com/ywyz/child-manager/issues/2) | `ready` / 待实现授权 | `c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7` |
| Trae | [#3](https://github.com/ywyz/child-manager/issues/3) | `ready` / 待实现授权 | `c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7` |

#### 非目标

- 不实现 M2～M8 业务功能，不预建对应实现 Issue。
- 不创建生产 Caddyfile、生产 Compose、DNS、证书、Tailscale、备份或发布流程。
- 不创建照片、OCR、对象存储、PDF、审批或未来业务子系统空壳。
- 不在 `main` 添加业务实现。

## 2. Codex 实现子 Issue 草稿

### 标题

`M1：Codex 工程骨架与质量基线实现`

### 正文

#### 关联与边界

- 父 Issue：[#1](https://github.com/ywyz/child-manager/issues/1)。
- 目标分支：`codex`。
- 共同基线：`c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7`，与 Trae 子 Issue 完全相同。
- 复核日期：2026-07-14。
- 草稿复核时 `main` HEAD：`ba81925a8b0a9f1a74951358bdf37cd45f8c529b`；`main...origin/main = 0/0`。
- 验证摘要：GitHub Issue 0 个；文档链接与格式检查通过；graphify 为 1671 节点/1327 边且完整性异常为 0；当前无业务代码，不适用实现分支质量命令。
- 当前状态：`ready` / 分支已创建，待实现授权。
- 只记录 Codex 自己的方案、提交、迁移、验证、风险和阻塞。

#### T004～T020 有序执行清单

- [ ] T004：建立 Python 3.14+ 项目、冻结运行入口、依赖与锁文件；验证锁定安装、解释器版本和依赖树。
- [ ] T005：建立三个运行单元、两个共享包、测试目录及稳定可导入的契约/端口骨架；不实现业务规则或未来空壳。
- [ ] T006：配置 Ruff、Pyright、Pytest、OpenAPI 校验和 Python 3.14 GitHub Actions 门禁。
- [ ] T007：增加仅供本地开发/测试的 PostgreSQL、Redis 与忽略规则；只绑定回环地址且不含生产拓扑或秘密。
- [ ] T008：完成初始化（Setup）检查点，实际运行依赖健康检查和五条标准质量命令。
- [ ] T009：先写 Web/API 依赖方向和 BFF 转发红灯（RED）测试。
- [ ] T010：先写统一错误、分页、Request ID、幂等规范化指纹（fingerprint）与 OpenAPI 3.1 红灯测试。
- [ ] T011：先写敏感配置、日志脱敏、回环保护和存活/就绪（live/ready）红灯测试。
- [ ] T012：先写事务边界与 Alembic 空库升级红灯测试，只建立测试收集所需的最小引导骨架（bootstrap）。
- [ ] T013：实现公共错误、分页、Request ID、幂等和 OpenAPI 校验契约，使 T010 转为绿灯（GREEN）。
- [ ] T014：实现分级配置、回环保护、结构化日志、追踪传播和脱敏，使相关测试转为绿灯。
- [ ] T015：建立 SQLAlchemy 2.x、PostgreSQL 事务和 Alembic 基础，使事务与迁移测试转为绿灯。
- [ ] T016：建立隔离数据库、固定时钟、日历/AI/Redis 替身和禁网保护。
- [ ] T017：实现 API 装配、统一异常转换及 `/health/live`、`/health/ready`。
- [ ] T018：建立只传 `job_id` 的消息契约、Dramatiq/Redis Worker 入口和测试消息代理（broker）。
- [ ] T019：建立 NiceGUI Web 入口与 BFF 客户端，使依赖方向和转发测试转为绿灯。
- [ ] T020：完成基础能力（Foundational）检查点，运行专项测试、五条标准命令并更新 graphify。

任务描述和逐项命令以 [T004～T020 权威清单](../../specs/001-daily-activity-plan/tasks.md#phase-1-setuppre-m1-文档门禁与工程初始化) 为准；Issue 摘要不得覆盖权威 Tasks。

#### 实施原则

1. 每项先建立由缺失行为导致的可观察红测接缝（RED seam）。
2. 只实现使当前任务转为绿灯的最小行为。
3. 先运行相关快速测试，再在初始化和基础能力检查点运行完整门禁。
4. 不读取 Trae 结果后省略自身测试，不复制或 cherry-pick Trae 实现。

#### 验收证据

- 分支 HEAD：完成后回填。
- 共同基线：`c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7`。
- 实际提交：逐项回填。
- 快速测试：逐项回填实际命令和结果。
- 标准五条命令：逐条回填，不得合并成模糊的“全部通过”。
- 专项检查与 graphify：回填实际结果或失败原因。
- 已知风险/阻塞：如实回填。

#### 非目标

- 不开始 T021 及以后用户故事任务。
- 不实现生产部署、照片/OCR、对象存储、PDF 或未来业务模块。
- 不修改 Trae 分支，不把 Codex 内部实现选择写回共享规格。

## 3. Trae 实现子 Issue 草稿

### 标题

`M1：Trae 工程骨架与质量基线实现`

### 正文

#### 关联与边界

- 父 Issue：[#1](https://github.com/ywyz/child-manager/issues/1)。
- 目标分支：`trae`。
- 共同基线：`c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7`，与 Codex 子 Issue 完全相同。
- 复核日期：2026-07-14。
- 草稿复核时 `main` HEAD：`ba81925a8b0a9f1a74951358bdf37cd45f8c529b`；`main...origin/main = 0/0`。
- 验证摘要：GitHub Issue 0 个；文档链接与格式检查通过；graphify 为 1671 节点/1327 边且完整性异常为 0；当前无业务代码，不适用实现分支质量命令。
- 当前状态：`ready` / 分支已创建，待实现授权。
- 只记录 Trae 自己的方案、提交、迁移、验证、风险和阻塞。

#### T004～T020 有序执行清单

- [ ] T004：建立 Python 3.14+ 项目、冻结运行入口、依赖与锁文件；验证锁定安装、解释器版本和依赖树。
- [ ] T005：建立三个运行单元、两个共享包、测试目录及稳定可导入的契约/端口骨架；不实现业务规则或未来空壳。
- [ ] T006：配置 Ruff、Pyright、Pytest、OpenAPI 校验和 Python 3.14 GitHub Actions 门禁。
- [ ] T007：增加仅供本地开发/测试的 PostgreSQL、Redis 与忽略规则；只绑定回环地址且不含生产拓扑或秘密。
- [ ] T008：完成初始化（Setup）检查点，实际运行依赖健康检查和五条标准质量命令。
- [ ] T009：先写 Web/API 依赖方向和 BFF 转发红灯（RED）测试。
- [ ] T010：先写统一错误、分页、Request ID、幂等规范化指纹（fingerprint）与 OpenAPI 3.1 红灯测试。
- [ ] T011：先写敏感配置、日志脱敏、回环保护和存活/就绪（live/ready）红灯测试。
- [ ] T012：先写事务边界与 Alembic 空库升级红灯测试，只建立测试收集所需的最小引导骨架（bootstrap）。
- [ ] T013：实现公共错误、分页、Request ID、幂等和 OpenAPI 校验契约，使 T010 转为绿灯（GREEN）。
- [ ] T014：实现分级配置、回环保护、结构化日志、追踪传播和脱敏，使相关测试转为绿灯。
- [ ] T015：建立 SQLAlchemy 2.x、PostgreSQL 事务和 Alembic 基础，使事务与迁移测试转为绿灯。
- [ ] T016：建立隔离数据库、固定时钟、日历/AI/Redis 替身和禁网保护。
- [ ] T017：实现 API 装配、统一异常转换及 `/health/live`、`/health/ready`。
- [ ] T018：建立只传 `job_id` 的消息契约、Dramatiq/Redis Worker 入口和测试消息代理（broker）。
- [ ] T019：建立 NiceGUI Web 入口与 BFF 客户端，使依赖方向和转发测试转为绿灯。
- [ ] T020：完成基础能力（Foundational）检查点，运行专项测试、五条标准命令并更新 graphify。

任务描述和逐项命令以 [T004～T020 权威清单](../../specs/001-daily-activity-plan/tasks.md#phase-1-setuppre-m1-文档门禁与工程初始化) 为准；Issue 摘要不得覆盖权威 Tasks。

#### 实施原则

1. 每项先建立由缺失行为导致的可观察红测接缝（RED seam）。
2. 只实现使当前任务转为绿灯的最小行为。
3. 先运行相关快速测试，再在初始化和基础能力检查点运行完整门禁。
4. 不读取 Codex 结果后省略自身测试，不复制或 cherry-pick Codex 实现。

#### 验收证据

- 分支 HEAD：完成后回填。
- 共同基线：`c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7`。
- 实际提交：逐项回填。
- 快速测试：逐项回填实际命令和结果。
- 标准五条命令：逐条回填，不得合并成模糊的“全部通过”。
- 专项检查与 graphify：回填实际结果或失败原因。
- 已知风险/阻塞：如实回填。

#### 非目标

- 不开始 T021 及以后用户故事任务。
- 不实现生产部署、照片/OCR、对象存储、PDF 或未来业务模块。
- 不修改 Codex 分支，不把 Trae 内部实现选择写回共享规格。

## 4. 草稿只读复核清单

- [x] 三份草稿引用同一 Roadmap、Spec、Plan、Tasks、ADR、模板和双 Agent 协议。
- [x] 父 Issue 只包含共同目标、门禁、任务范围、非目标与子 Issue 状态，没有实现专属类名或提交列表。
- [x] Codex、Trae 子 Issue 的 T004～T020、共同门禁、TDD 和最小实现要求对称。
- [x] 两个子 Issue 只分别记录自己的提交、验证、风险和阻塞。
- [x] T004～T020 未拆成 17 个独立 Issue。
- [x] M2～M8 保持 `pending`，未预建实现 Issue。
- [x] Issue、分支和实现授权彼此独立，草稿完成不声称后续操作已经获批。
