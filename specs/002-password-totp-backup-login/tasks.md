---

description: "密码与 TOTP 备用登录的依赖有序实施任务"

---

# Tasks: 密码与 TOTP 备用登录

**Input**: Design documents from `/specs/002-password-totp-backup-login/`

**Docs Baseline**: 待此次 docs 提交确认后固定 | **Issue**: 待创建 M3A Issue | **Implementation Branch**: `dev`

**Prerequisites**: plan.md、spec.md、research.md、data-model.md、contracts/openapi.yaml

**Tests**: 本功能是认证边界变更，必须严格执行 RED → GREEN；RED 不得包含 collection、
fixture 或数据库基础设施错误。

**Authorization**: 本清单不授权实现。Issue 固定已确认 docs 提交、用户授权在 `dev` 开始
M3A 前，不得执行 T003 之后的代码任务。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 不同文件且无未完成依赖，可并行执行
- **[US1/US2/US3]**: 对应 `spec.md` 的用户故事

## Phase 1: Baseline & Setup

**Purpose**: 固定可实施基线，不改变现有 M3 范围和迁移编号。

- [ ] T001 创建 M3A 实现 Issue，固定确认后的 docs 提交，链接
  `specs/002-password-totp-backup-login/`、ADR-0010、ADR-0011、威胁模型和总 OpenAPI，并
  写明范围、非目标、验收、风险及验证命令
- [ ] T002 将固定 docs 提交同步到 `dev`，确认 M3 T036–T045 与
  `packages/backend/database/migrations/versions/0004_settings.py` 已完成且 Alembic head
  唯一，再记录 `0005_password_totp_backup_login` 的起点

**Checkpoint**: Issue 和迁移父版本均不可移动；否则停止实施。

---

## Phase 2: Intentional RED Gate

**Purpose**: 在任何业务实现前锁定密码/TOTP、安全状态、契约、迁移、API 和浏览器行为。

- [ ] T003 [P] 为密码策略、Argon2id 参数/渐进重摘要、RFC 6238 时间窗口、原子重放和
  AES-GCM AAD/认证标签失败增加 RED 单元测试到
  `tests/unit/identity/test_passwords.py`、`tests/unit/identity/test_totp.py` 和
  `tests/unit/identity/test_secret_encryption.py`
- [ ] T004 [P] 为本规格 OpenAPI 路径、请求响应、请求秘密 `writeOnly`、一次性响应秘密
  `readOnly` + `x-sensitive`、通用认证失败和
  运行时路由一致性增加 RED 契约测试到 `tests/contract/test_backup_auth_contract.py`
- [ ] T005 [P] 为 `0004_settings -> 0005_password_totp_backup_login` 升降级、约束、
  既有会话回填/撤销以及 Repository 园所隔离增加 RED 测试到
  `tests/migrations/test_0005_password_totp_backup_login.py` 和
  `tests/repository/test_backup_auth_isolation.py`
- [ ] T006 [P] [US1] 为管理员受限门禁、管理员角色新增/移除后的门禁重算、教师每次
  WebAuthn 登录及安全设置页的可跳过提示、一次性 TOTP 展示、绑定过期/并发消费和密码策略
  增加 RED API/Web 测试到 `tests/api/test_backup_enrollment.py` 和
  `tests/web/test_backup_auth_smoke.py`
- [ ] T007 [P] [US2] 为双因素备用登录、账号枚举一致性、三层限流、TOTP 重放、普通业务
  会话和五分钟 `add_passkey` 专用升级增加 RED API 测试到
  `tests/api/test_backup_authentication.py`
- [ ] T008 [P] [US3] 为 WebAuthn 保护的轮换/关闭、管理员强制、会话撤销、紧急恢复清理和
  最后管理员双人核验不降级增加 RED API 测试到 `tests/api/test_backup_maintenance.py`
- [ ] T009 运行 T003–T008 的目标测试并把预期失败清单写入 M3A Issue；确认所有测试成功
  收集、隔离 PostgreSQL 可用、失败仅来自尚未实现的 M3A 行为

**Checkpoint**: 形成可复现 RED 基线后才能进入 GREEN。

---

## Phase 3: Foundational GREEN

**Purpose**: 实现三个用户故事共用的数据、密码学、Repository 和认证保证级别。

- [ ] T010 创建
  `packages/backend/database/migrations/versions/0005_password_totp_backup_login.py`，
  增加 `backup_auth_credentials`、`backup_auth_enrollments`、会话保证字段和
  `backup_auth_version`，通过 T005 的升降级与约束测试
- [ ] T011 [P] 在 `packages/contracts/identity.py` 和
  `packages/backend/identity/models.py` 增加备用状态、绑定、登录及认证方法模型，禁止把
  密码/TOTP 字段放回 `users`
- [ ] T012 [P] 在 `packages/backend/identity/passwords.py` 固定 Argon2id 参数并完成
  Unicode、阻断列表和渐进重摘要；在 `packages/backend/identity/totp.py` 实现 RFC 6238
  生成/验证及候选 counter 计算，通过 T003 对应测试
- [ ] T013 [P] 在 `packages/backend/identity/secret_encryption.py` 和
  `packages/backend/ports.py` 实现 TOTP AES-256-GCM 信封及开发文件/测试适配器，AAD 绑定
  园所、用户、enrollment/凭据和版本；启用时以新 nonce 从 enrollment AAD 重绑到凭据
  AAD，通过认证标签失败与敏感信息测试
- [ ] T014 在 `packages/backend/identity/repository.py` 实现同园所凭据/绑定读写、
  单活动 enrollment、原子 `last_accepted_counter` 与备用因素版本撤销，通过 T005 Repository
  测试
- [ ] T015 在 `packages/backend/identity/service.py` 和 `apps/api/dependencies.py`
  实现认证方式、管理员 `restricted_enrollment` 门禁、最近 WebAuthn/备用重新验证判断及
  `add_passkey` 唯一 purpose；角色变更和恢复后重新计算管理员门禁，不增加第二套认证服务

**Checkpoint**: 数据、密码学和授权原语 GREEN；尚未开放公共备用登录。

---

## Phase 4: User Story 1 — 管理员建立备用登录 (P1)

**Goal**: 管理员先完整设置密码与 TOTP，教师可跳过并持续收到提示。

**Independent Test**: 管理员未完成时无法进入业务页；密码合格且首个 TOTP 成功后两项同时
生效，TOTP 种子不再展示；教师未配置仍可使用业务功能。

- [ ] T016 [US1] 在 `packages/backend/identity/service.py` 实现绑定开始、10 分钟过期、
  一次性种子返回、密码与首个 TOTP 原子启用，以及替换旧 enrollment/材料/备用会话
- [ ] T017 [US1] 在 `apps/api/routers/auth.py` 和 `apps/api/openapi.py` 实现
  `GET/DELETE /auth/backup`、`POST /auth/backup/enrollment` 与 verify 端点、CSRF、限流、
  通用错误和最小化审计
- [ ] T018 [US1] 在 `apps/web/api_client.py` 和 `apps/web/pages/auth.py` 实现管理员
  受限绑定页、二维码/人工输入值只展示一次、教师每次 WebAuthn 登录及安全设置页的可跳过
  提示和备用状态页
- [ ] T019 [US1] 运行 `tests/api/test_backup_enrollment.py`、
  `tests/web/test_backup_auth_smoke.py` 及相关契约/敏感信息测试，记录 US1 GREEN 证据

**Checkpoint**: US1 可独立验收，不依赖公共备用登录。

---

## Phase 5: User Story 2 — 新设备备用登录并新增通行密钥 (P2)

**Goal**: 密码与 TOTP 同时正确可建立普通业务会话，专用再验证只允许新增通行密钥。

**Independent Test**: 未知账号或任一因素错误均通用失败；成功会话可使用普通业务；最近五
分钟再验证可新增但不能删除或修改其他身份材料。

- [ ] T020 [US2] 在 `packages/backend/identity/service.py` 实现等价虚拟密码/TOTP 路径、
  两因素单意图验证、TOTP counter 原子消费、备用因素版本检查和 `password_totp` 会话创建
- [ ] T021 [US2] 在 `packages/backend/identity/auth_throttle.py` 与
  `packages/backend/identity/login_throttle.py` 增加可信来源、账号摘要和端点全局三层备用
  限流，确保通行密钥限流不能被清零或无关阻断
- [ ] T022 [US2] 在 `apps/api/routers/auth.py` 实现公共
  `POST /auth/backup/authentication` 与会话内
  `POST /auth/backup/reauthentication`，公开错误不区分账号、密码、TOTP 或未配置状态
- [ ] T023 [US2] 修改 `packages/backend/identity/service.py` 的通行密钥注册授权：
  `password_totp` 会话仅在五分钟专用证明有效时可新增，成功后消费证明；其余凭据、恢复、
  账号和角色操作仍要求 WebAuthn
- [ ] T024 [US2] 在 `apps/web/pages/auth.py` 与 `apps/web/api_client.py` 增加备用登录、
  再验证和新设备通行密钥绑定流程，不在浏览器日志或 URL 暴露秘密
- [ ] T025 [US2] 运行 `tests/api/test_backup_authentication.py`、
  `tests/api/test_credentials.py`、`tests/api/test_sessions.py` 和 Web 冒烟测试，记录 US2
  GREEN 与负向授权矩阵

**Checkpoint**: US2 可独立从无通行密钥的新设备完成登录和新增通行密钥。

---

## Phase 6: User Story 3 — 安全维护与恢复 (P3)

**Goal**: WebAuthn 保护备用因素生命周期；失去全部通行密钥时不降低紧急恢复。

**Independent Test**: WebAuthn 可重设/关闭，管理员不能关闭；紧急恢复撤销全部旧材料，
并要求管理员重新绑定。

- [ ] T026 [US3] 在 `packages/backend/identity/service.py` 实现 WebAuthn 保护的密码/TOTP
  替换、教师关闭、管理员拒绝关闭，以及备用因素版本增加和旧备用会话/证明即时撤销
- [ ] T027 [US3] 扩展 `packages/backend/identity/service.py` 的恢复完成事务，清除旧密码、
  TOTP、通行密钥、会话、邀请和恢复码；管理员进入 `restricted_enrollment`，教师保持可选
- [ ] T028 [US3] 在 `apps/api/routers/auth.py`、`apps/web/pages/auth.py` 和
  `apps/web/api_client.py` 实现 `GET /auth/security-events`：从现有审计事件投影本人最近
  20 条内建安全事件并在登录后展示警报/列表，覆盖备用登录启用、密码/TOTP 变化、备用登录
  成功、备用会话新增通行密钥、关闭和恢复撤销；不新增通知表、已读状态、管理员代重置或
  短信/邮件路径
- [ ] T029 [US3] 运行 `tests/api/test_backup_maintenance.py`、
  `tests/api/test_recovery.py`、`tests/api/test_invitations.py` 和 Web 冒烟测试，记录 US3
  GREEN 及最后管理员双人核验未降级证据

**Checkpoint**: 三个用户故事均可独立验收。

---

## Phase 7: Cross-cutting Verification

**Purpose**: 证明契约、隔离、敏感信息和完整回归一致。

- [ ] T030 [P] 扩展 `packages/backend/observability.py` 与审计事件契约，确保密码、摘要、
  TOTP、种子、二维码和完整认证请求始终脱敏，并增加 `tests/unit/test_observability.py`
  回归
- [ ] T031 [P] 更新 `tests/contract/test_runtime_openapi.py` 和
  `tests/contract/test_openapi_document.py`，证明运行时 OpenAPI 与固定文档契约一致且 NiceGUI
  仍是唯一浏览器入口
- [ ] T032 执行 `specs/002-password-totp-backup-login/quickstart.md` 的全部旅程和专项测试，
  再运行 `uv sync --locked`、Ruff format/check、Pyright 与完整 Pytest
- [ ] T033 运行敏感信息扫描、`git diff --check` 与 `graphify update .`，验证图谱 manifest、
  JSON 可解析性、核心认证节点和无向多重图诊断，把真实结果写入 M3A Issue
- [ ] T034 对固定 docs 基线和 M3A Issue 执行 Standards + Spec 双轴 Review；解决阻塞发现后
  才可宣称 M3A 完成，且不得自动合并到 `main`

---

## Dependencies & Execution Order

- T001 → T002；两者完成前不授权代码任务。
- T003–T008 可按文件并行；T009 依赖全部 RED 测试。
- T010–T015 依赖 T009；T014 依赖 T010–T013，T015 依赖 T011–T014。
- US1：T016 → T017 → T018 → T019。
- US2 依赖 US1 已提供有效材料：T020 → T021/T022 → T023 → T024 → T025。
- US3 依赖 US1/US2 的材料和会话：T026 → T027 → T028 → T029。
- T030/T031 可在 US3 后并行；T032 → T033 → T034。

## Traceability

| Requirement | Tasks |
|---|---|
| FR-001–FR-006 | T003–T018、T020–T022 |
| FR-007–FR-008 | T007、T015、T020、T022–T025 |
| FR-009–FR-011 | T008、T026–T029 |
| FR-012–FR-015 | T006–T008、T017、T021–T022、T028、T030–T033 |
| SC-001–SC-008 | T009、T019、T025、T029、T032–T034 |

## Notes

- Conventional Commits，中文主题优先；每个提交保持单一目的。
- 任何实现中发现的需求缺口先回 `docs` 修订并更新 Issue 固定基线。
- 不新增短信、邮件、密码单独登录、TOTP 单独登录、管理员代重置或生产密钥托管。
- 不修改 M3 T036–T045，不重编号 `0004_settings.py`。
