# Tasks: 幼儿园管理助手桌面首期

**Input**: `specs/003-desktop-local-first/` 下的 `spec.md`、`plan.md`、`research.md`、
`data-model.md`、`quickstart.md` 与 `contracts/`

**Docs Baseline**: `d4ac961a04a273a0384e295190296f69538b313b` |
**Issue**: https://github.com/ywyz/child-manager/issues/19 | **Implementation Branch**: `dev`

**Authorization Record (2026-08-11)**: 维护者已确认 T034 无计时 Windows 二元验收事实。初始
收口 `b53c1c43c69e3ae3058d74b6163ecfc2bd7d4e95` 的双轴 Review 发现产品显示名偏差后，维护者
确认最小修复：`cf106e44cb907a4958879a16ee061dccc8c2b1f9` 保留为原始实现锚点，
`7af4d46f1114616eb798e5991805a164026c63df` 为 Review 修复锚点；其后只含证据、状态与 Graphify
同步的提交作为新固定 Review SHA。双轴 Review 通过后才可合并 `main`；T035–T040 由独立
Slice 2A Issue 驱动，完成 clean RED 后停在 T040，不得进入 T041 GREEN。

**Authorization Record (2026-08-11, Slice 2A GREEN)**: 维护者要求先把 Issue #19 的固定 docs
SHA 更新为上述新 SHA，并同步 T044 新增的迁移保护范围；回读确认后授权恢复 T041–T048
GREEN。本授权不包含 commit、push、Review、`main` 集成或 T049 及以后任务。

**Tests**: 规格与宪章明确要求自动化测试；每个切片先收集测试并得到只来自本切片未实现行为的
RED，再实施并运行该切片自有门禁。导入、fixture、数据库配置或运行环境错误均不是有效 RED。

**Authorization**: 本任务清单不授权实现。只有设计收敛到 `docs`、Issue 固定完整 docs SHA，且
维护者明确授权 `dev` 实现后才能开始 T001；不得在 `design/desktop-local-first` 晋升原型代码。

## Format: `[ID] [P?] [Story] Description`

- **[P]**：与当前未完成任务不存在文件或行为依赖，可并行处理。
- **[US1]**：离线一日教案；**[US2]**：可选 AI 与受控 Agent；**[US3]**：备份恢复；
  **[US4]**：桌面体验。
- 每个任务都给出目标文件与自己的验证责任；后续切片测试不得冒充当前切片完成证据。

## Phase 1: Setup（实现授权与项目骨架）

**Purpose**: 固定实施基线、依赖和正式桌面命名空间；不实现业务行为。

- [x] T001 在 `specs/003-desktop-local-first/tasks.md` 写入已确认 docs 完整 SHA、GitHub Issue URL 与授权记录，并以 `git branch --show-current` 验证只在 `dev` 开始实现
- [x] T002 在 `pyproject.toml` 与 `uv.lock` 锁定计划中的 Python/PySide6/SQLAlchemy/Alembic/python-docx/chinesecalendar/httpx/cryptography/keyring/boto3 版本，并以 `uv sync --locked` 验证 Python 3.14 锁定安装
- [x] T003 [P] 建立 `src/kindergarten_manager/`、`tests/desktop/{unit,application,database,contracts,integration,ui,packaging}/` 与空包边界，不复制 `apps/desktop/prototype_daily_plan.py`
- [x] T004 [P] 在 `tests/desktop/conftest.py` 提供临时数据根、固定时钟、虚构业务资料、Qt offscreen 和禁止真实网络 fixture，并验证 fixture 自测可收集

**Checkpoint**: 依赖可重复安装，正式包和测试目录存在，尚无业务实现。

---

## Phase 2: Foundational（所有纵向切片共享的最小边界）

**Purpose**: 只建立错误/DTO、Qt 后台桥接和架构禁入规则，不提前建设业务模块。

**⚠️ CRITICAL**: 本阶段完成前不得开始任何用户故事；本阶段不得创建本地 HTTP、通用 DI、事件总线或 Repository 接口森林。

- [x] T005 [P] 在 `tests/desktop/contracts/test_architecture_boundaries.py` 写入禁入测试：新命名空间不得导入旧 `apps.web/api/worker`、identity/jobs、PostgreSQL migration，UI/domain 依赖方向符合应用服务契约
- [x] T006 [P] 在 `tests/desktop/unit/test_application_dto.py` 覆盖 `CommandResult`、稳定错误码、冻结 DTO 与正文/凭据不进入 repr/log 的契约
- [x] T007 [P] 在 `tests/desktop/ui/test_runtime_bridge.py` 覆盖 operation ID、进度、取消、迟到结果丢弃、Widget/Session 不跨线程和有界退出
- [x] T008 实现 `src/kindergarten_manager/application/dto.py` 与 `src/kindergarten_manager/observability.py`，使 T006 通过且所有用户可见摘要为简体中文
- [x] T009 实现 `src/kindergarten_manager/ui/runtime.py` 的 Qt 线程池/信号/取消桥接，使 T007 通过且不引入 Redis、Dramatiq 或独立 Worker
- [x] T010 运行 `uv run pytest --collect-only tests/desktop`、T005–T009 相关测试、Ruff 和 Pyright，确认基础门禁通过且架构禁入测试真实扫描 `src/kindergarten_manager`

**Checkpoint**: 共享边界可用；业务数据、页面和外部集成仍未实现。

---

## Phase 3: Slice 1 / User Story 1 - 首次启动到当天 Word（Priority: P1）🎯 MVP

**Goal**: 完成维护者指定的第一个闭环：桌面程序启动 → 首次设置 → SQLite 初始化 → 创建班级/学期 → 编辑并保存一日教案 → 导出当天 Word。

**Independent Test**: 在断网、空数据根环境运行 `python -m kindergarten_manager`，填写虚构教师和园所，创建一个学期与班级，编辑当天结构化教案并保存，重启后内容仍在，随后导出并在 Microsoft Word 打开当天 DOCX；源码模板哈希不变。

### Tests for Slice 1（必须先 RED）

- [x] T011 [P] [US1] 在 `tests/desktop/unit/test_paths.py` 和 `tests/desktop/application/test_bootstrap.py` 覆盖稳定 `GenericDataLocation/cn.kindergartenmanager.desktop`、空库首启、只读/损坏/未来 Schema 拒绝和安装目录零运行数据
- [x] T012 [P] [US1] 在 `tests/desktop/database/test_migrations.py` 覆盖空库到 `0001_desktop_initial`、重复升级、命名 FK/unique/check/index/immutable trigger、`integrity_check` 与 `foreign_key_check`
- [x] T013 [P] [US1] 在 `tests/desktop/application/test_settings_service.py` 覆盖最少首次设置、教师/园所/学期/班级/区域约束、单一当前学期和事务回滚
- [x] T014 [P] [US1] 在 `tests/desktop/unit/test_content.py` 与 `tests/desktop/unit/test_calendar.py` 覆盖首期结构化字段、教学周、日期/季节文本及非工作日/覆盖外年份只软提示
- [x] T015 [P] [US1] 在 `tests/desktop/application/test_lesson_plan_service.py` 和 `tests/desktop/database/test_lesson_plan_repository.py` 覆盖同班同日唯一、打开/创建、revision 乐观校验、保存正文和重启读取
- [x] T016 [P] [US1] 在 `tests/desktop/contracts/test_word_single_export.py` 覆盖冻结 snapshot、旧 Renderer 字段映射、模板表格/字体/字号/段落/换行、同目录临时文件、原子覆盖与模板哈希不变
- [x] T017 [P] [US1] 在 `tests/desktop/ui/test_first_run_daily_plan_flow.py` 覆盖首次设置、创建班级/学期、结构化编辑、保存状态、重启加载和“导出当天 Word”文件对话框闭环
- [x] T018 [US1] 先运行 `uv run pytest --collect-only` 收集 T011–T017，再运行这些测试并将干净 RED 记录到 `docs/implementation-evidence/desktop-slice-1-red.md`；导入、Qt fixture、模板或 SQLite 环境错误必须先修复

### Implementation for Slice 1

- [x] T019 [P] [US1] 实现 `src/kindergarten_manager/infrastructure/paths.py`，创建 plan.md 冻结的数据/备份/staging/cache/logs 子目录并通过 T011 路径用例
- [x] T020 [P] [US1] 实现 `src/kindergarten_manager/domain/content.py` 与 `src/kindergarten_manager/domain/calendar.py`，仅提取旧纯函数/值对象行为并通过 T014，不运行时导入旧 backend
- [x] T021 [US1] 实现 `src/kindergarten_manager/infrastructure/database/engine.py` 的同步 SQLAlchemy Session 工厂与 SQLite PRAGMA，禁止跨线程共享连接和 `create_all()`
- [x] T022 [US1] 实现 `src/kindergarten_manager/infrastructure/database/models.py` 的首期基础表、命名约束与状态字段，不加入账号、租户、幼儿、Cloud Job、同步、Agent 会话/记忆或尚未解锁的 Agent 写入审计实体
- [x] T023 [US1] 创建独立 Alembic 链 `src/kindergarten_manager/infrastructure/database/migrations/versions/0001_desktop_initial.py` 与 `env.py`，启用 batch mode 并使 T012 全部通过
- [x] T024 [US1] 实现 `src/kindergarten_manager/infrastructure/database/upgrade.py` 和 `src/kindergarten_manager/application/bootstrap.py` 的路径检查、完整性检查、Alembic 升级与首次设置判定；每日备份行为留给 US3 接入
- [x] T025 [US1] 实现 `src/kindergarten_manager/infrastructure/database/repositories.py` 中本切片需要的设置、班级、学期和当前教案具体 SQLite 操作，并通过 T013/T015 的事务与唯一性用例
- [x] T026 [US1] 实现 `src/kindergarten_manager/application/settings.py` 的首次设置、班级、区域和学期用例，使每个聚合保存只占一个事务
- [x] T027 [US1] 实现 `src/kindergarten_manager/application/lesson_plans.py` 的 `open_or_create`、revision 校验、正文保存和日期软提示；本切片不实现 AI、历史、归档或搜索
- [x] T028 [US1] 在 `src/kindergarten_manager/infrastructure/exports/teacherplan_renderer.py` 提取旧模板字段映射并实现只读模板副本的 `render_day(snapshot)`，不得导入旧 Job/Export Store/HTTP 下载层
- [x] T029 [US1] 实现 `src/kindergarten_manager/application/exports.py` 的 `prepare_single` 与单日原子发布，覆盖已有目标确认、锁文件、磁盘满和失败清理
- [x] T030 [P] [US1] 实现 `src/kindergarten_manager/ui/pages/first_run.py` 的教师、园所、学期和班级最少设置向导，失败时不得进入可写主窗口
- [x] T031 [US1] 实现 `src/kindergarten_manager/ui/pages/daily_plan.py` 的班级/日期上下文、01–05 与反思结构化编辑、显式保存和固定状态区
- [x] T032 [US1] 实现 `src/kindergarten_manager/ui/pages/single_export.py` 的“导出当天 Word”、原生目标选择、覆盖确认和完成/失败反馈
- [x] T033 [US1] 实现 `src/kindergarten_manager/__main__.py`、`src/kindergarten_manager/app.py` 与 `src/kindergarten_manager/ui/main_window.py` 的唯一 composition root，把首次设置和主窗口串成可启动闭环
- [x] T034 [US1] 运行 T011–T017、`uv run ruff format --check .`、`uv run ruff check .`、`uv run pyright`，并由一名未参与实现、只依赖界面提示的验收参与者在断网 Windows 上完成首次启动、基础设置并创建第一份教案；在 `docs/implementation-evidence/desktop-slice-1-acceptance.md` 记录上述流程通过，以及重启→当天 Word 打开证据

**Checkpoint**: MVP 可单独使用；AI、远程备份、批量 Word、历史/归档和完整视觉收敛均不得计入本切片。

---

## Phase 4: Slice 2A / User Story 2 - 现有可选 AI Provider、结构化预览与采用（Priority: P2）

**Goal**: 在不改变手工闭环的前提下加入一个当前模型、单任务后台生成、结构校验、预览/拒绝/采用和采用前快照。

**Independent Test**: 使用本地模型替身覆盖单栏、四栏部分失败、重试、取消、过期、拒绝和采用；未配置 AI 或关闭网络时 Slice 1 全部继续通过，SQLite/日志/备份中找不到 Key。

### Tests for Slice 2A（必须先 RED）

- [x] T035 [P] [US2] 在 `tests/desktop/unit/test_ai_domain.py` 覆盖允许的栏目 Schema、规范 JSON/hash、输入最小化、预览目标栏有效性和结构错误分类
- [x] T036 [P] [US2] 在 `tests/desktop/contracts/test_ai_client.py` 覆盖回环 HTTP、非回环 HTTPS、禁止 userinfo/重定向、超时/响应上限、最多两次 retryable 重试且不访问真实网络
- [x] T037 [P] [US2] 在 `tests/desktop/contracts/test_credentials.py` 覆盖 Windows backend/local-machine persistence、写后读回、删除和 Null/文件/未知 backend fail closed
- [x] T038 [P] [US2] 在 `tests/desktop/application/test_ai_generation.py` 覆盖单一运行任务、四栏部分失败、取消/关闭丢弃、预览拒绝、目标栏过期和采用前不可变快照事务
- [x] T039 [P] [US2] 在 `tests/desktop/ui/test_ai_preview_flow.py` 覆盖可选入口、固定状态、重复发起提示、逐栏预览/重试/采用及页面切换后迟到信号丢弃
- [x] T040 [US2] 收集并运行 T035–T039 得到干净 RED并记录到 `docs/implementation-evidence/desktop-slice-2a-red.md`，同时重跑 Slice 1 门禁证明 AI 未成为手工保存或单日 Word 的前置条件

### Implementation for Slice 2A

- [x] T041 [P] [US2] 实现 `src/kindergarten_manager/domain/ai.py` 的结果模型、Schema registry、规范 hash 和过期预览判定，只提取旧纯行为而不复制 Job/tenant 状态
- [x] T042 [P] [US2] 实现 `src/kindergarten_manager/infrastructure/credentials.py` 的 keyring 窄边界，确保秘密不进入 DTO repr、SQLite、日志或异常
- [x] T043 [US2] 实现 `src/kindergarten_manager/infrastructure/ai/client.py` 与只读默认提示词 `src/kindergarten_manager/infrastructure/ai/prompts/`，满足 T036 URL/重试规则
- [x] T044 [US2] 创建 `src/kindergarten_manager/infrastructure/database/migrations/versions/0002_desktop_ai.py`，扩展同目录 `models.py`、`repositories.py` 和 `upgrade.py`，支持单例 AI 非敏感配置、提示词覆盖、已校验 preview 及升级前最小本地 `pre_migration` 保护副本；在 `tests/desktop/database/test_migrations.py` 覆盖空库到 head、`0001 -> 0002`、命名约束/索引、完整性检查，以及保护副本成功和失败即停止，运行中任务与 Key 不得落库
- [x] T045 [US2] 实现 `src/kindergarten_manager/application/ai_generation.py` 的冻结输入、Qt 后台单任务、逐栏结果、取消、预览采用/拒绝与事务式采用前快照
- [x] T046 [US2] 实现 `src/kindergarten_manager/ui/pages/ai_settings.py` 与 `src/kindergarten_manager/ui/widgets/ai_preview.py`，只暴露一个当前模型和可恢复默认提示词
- [x] T047 [US2] 在 `src/kindergarten_manager/app.py` 装配凭据、AI client、Coordinator 和退出取消顺序，不引入 Redis、Dramatiq、recovery scan 或独立 Worker
- [x] T048 [US2] 运行 T035–T039、迁移专项、Slice 1 回归、Ruff/Pyright，并在 `docs/implementation-evidence/desktop-slice-2a-acceptance.md` 保存完全使用替身的成功/重试/失败/取消/过期矩阵，以及 `0001 -> 0002_desktop_ai` 保护性备份与升级证据

**Checkpoint**: AI 是可拆除的可选增强；原正文只有教师采用有效预览时才改变。

---

## Phase 5: Slice 2B / User Story 2 - Agent Foundation、Context 与 READ/DRAFT Tools（Priority: P2）

**Windows Follow-up Record (2026-08-12)**: 维护者在
`dev@7cf57cce3cda948d790121a169bef666a5f0370d` 上确认无需 `PYTHONPATH` 的源码启动、真实
`0001 -> 0002_desktop_ai` 迁移保护、数据保留与重启复测通过。该记录不替代其余 Agent
READ/DRAFT Windows 检查项，不自动关闭 Issue #20，也不授权 T061、PR 或 `main`。

**Goal**: 在现有 AI Provider 上建立受控单 `AgentRuntime`、最小 `AgentContext`、Provider port
和类型化 Tool registry；本切片只允许 READ/DRAFT，任何路径都不得正式写入。

**Independent Test**: 使用 Scripted Provider 覆盖合法/未知/越权 Tool、单/多次 Tool call、循环
上限、取消、迟到结果、Context 裁剪和会话结束；DRAFT 只返回 `PlanPatch`，SQLite、版本、preview、
audit、备份和日志中没有 Agent 状态或秘密。

### Tests for Slice 2B（必须先 RED）

- [x] T049 [P] [US2] 在 `tests/desktop/contracts/test_agent_runtime_contract.py` 覆盖 `Permission`、关闭 Tool Schema、`ToolResult`、Provider port、未知/WRITE Tool 和伪造 Permission 拒绝，以及具体 SDK 类型不穿过 Application Interface
- [x] T050 [P] [US2] 在 `tests/desktop/unit/test_agent_context.py` 覆盖最小字段白名单、实体 revision、过期/切换失效、Key/绝对路径/无关班级/完整历史排除和 repr/log 脱敏
- [x] T051 [P] [US2] 在 `tests/desktop/application/test_agent_read_draft.py` 用 Scripted Provider 覆盖单 Agent、READ/DRAFT Tool loop、稳定 `PlanPatch`、调用/响应/时限上限、Provider 拒绝/结构错误和全程零写入
- [x] T052 [P] [US2] 在 `tests/desktop/ui/test_agent_draft_flow.py` 覆盖固定状态区、字段级 draft 展示、重复 turn 拒绝、取消、页面切换/关闭迟到结果丢弃和“直接修改/总是允许”无 WRITE 路径
- [x] T053 [US2] 先收集 T049–T052，再运行得到只来自 Agent Foundation 未实现行为的干净 RED并记录到 `docs/implementation-evidence/desktop-slice-2b-red.md`；同时扫描 SQLite/备份/log 确认没有 conversation/thread/message/vector/Context/Patch 持久化

### Implementation for Slice 2B

- [x] T054 [P] [US2] 实现 `src/kindergarten_manager/application/agent_runtime.py` 中冻结 `AgentContext`、`Permission`、`ToolDescriptor`、`ToolResult`、`PlanPatch` 与最小 Runtime Interface，不包含 WRITE/Confirmation 执行方法
- [x] T055 [P] [US2] 定义窄 `AgentProviderPort` 并在 `src/kindergarten_manager/infrastructure/ai/agent_provider.py` 实现 OpenAI-compatible Adapter，在测试 fixture 实现 Scripted Adapter；Provider 只返回文本/Tool call 而不执行 Tool
- [x] T056 [US2] 实现 `src/kindergarten_manager/application/agent_tools.py` 的关闭 registry，以及 `lesson_plan.read_current/read_context`、`calendar.read_evaluation`、`settings.read_class_areas` 和两个纯 DRAFT Tool；不注册任意 WRITE、文件、URL、SQL 或代码 Tool
- [x] T057 [US2] 实现 `AgentRuntime` 的单 turn 串行 loop、Context 裁剪、Schema/Permission 校验、上限、取消和结果脱敏；Provider 等待期间无数据库事务，每次 READ Tool 自建并关闭 Session
- [x] T058 [US2] 实现 `src/kindergarten_manager/ui/widgets/agent_draft.py` 的意图提交、Context 范围、字段级 PlanPatch 展示、拒绝/丢弃和非阻断状态；不显示确认或写入控件
- [x] T059 [US2] 在 `src/kindergarten_manager/app.py` 装配唯一 Runtime、Provider Adapter 和 READ/DRAFT registry，退出时先失效 Context/Patch 再取消 operation；禁止子 Agent、并行 Tool 和 Provider 托管 thread
- [x] T060 [US2] 运行 T049–T052、Slice 1/2A 回归、Ruff/Pyright，并在 `docs/implementation-evidence/desktop-slice-2b-acceptance.md` 记录 Tool-only 越权矩阵、零写入扫描、单 Agent/取消和重启后无长期业务记忆证据

**Checkpoint**: Agent 只能读取和草拟；没有正式写入、Confirmation、持久化会话、长期业务记忆、
多 Agent 或 Level 3 Workflow。

---

## Phase 6: Slice 3 / User Story 3 - 本地恢复与远程加密备份（Priority: P3）

**Goal**: 建立一致性本地备份、`KMBACKUP1` 加密信封、显式版本恢复以及 WebDAV/S3 单向远程备份；绝不形成同步系统。

**Independent Test**: 对虚构完整数据库执行 daily/manual/pre-migration/pre-restore、错口令与篡改拒绝、WebDAV/S3 替身上传/列举/下载失败、跨新安装恢复，并在远程持续失败时连续保存 100 次教案。

### Tests for Slice 3（必须先 RED）

- [ ] T061 [P] [US3] 在 `tests/desktop/database/test_backup_snapshot.py` 覆盖 `Connection.backup()` 一致快照、取消、空间不足、integrity/FK/计数、30 份 daily 轮换和 pre-migration/pre-restore 保留
- [ ] T062 [P] [US3] 在 `tests/desktop/unit/test_backup_envelope.py` 覆盖 KMBACKUP1 黄金向量、scrypt/AES-GCM、错口令、header/AAD/密文/tag 篡改、截断及恶意 KDF 参数
- [ ] T063 [P] [US3] 在 `tests/desktop/contracts/test_backup_archive_safety.py` 覆盖条目白名单、路径穿越、重复条目、符号链接、压缩炸弹、长度/hash 和未来格式拒绝
- [ ] T064 [P] [US3] 在 `tests/desktop/contracts/test_remote_backup_stores.py` 覆盖 WebDAV/S3 上传、列举、显式对象下载、删除、超时/中断/长度不符和远端只收到加密对象
- [ ] T065 [P] [US3] 在 `tests/desktop/application/test_restore_transaction.py` 覆盖显式候选、旧 Schema staging 升级、未来 Schema 拒绝、pre-restore、原子替换和首次打开失败自动回滚
- [ ] T066 [P] [US3] 在 `tests/desktop/ui/test_backup_restore_flow.py` 覆盖具体版本选择、恢复确认、进度/取消、失败重试、忘记口令说明和不自动猜最新备份
- [ ] T067 [US3] 收集并运行 T061–T066 得到干净 RED并记录到 `docs/implementation-evidence/desktop-slice-3-red.md`，再运行 Slice 1、2A、2B 门禁证明远程失败与凭据丢失不阻断本地编辑、单日 Word、可选 AI 关闭状态或 Agent READ/DRAFT

### Implementation for Slice 3

- [ ] T068 [P] [US3] 实现 `src/kindergarten_manager/domain/backups.py` 的 manifest、状态转换、对象键和 RestoreCandidate 值对象，禁止教师/园所/班级/正文进入清单
- [ ] T069 [US3] 实现 `src/kindergarten_manager/infrastructure/backups/snapshot.py` 的 SQLite backup、完整性/计数/hash 和同目录临时包原子发布
- [ ] T070 [US3] 实现 `src/kindergarten_manager/infrastructure/backups/envelope.py` 的规范 header、固定 KDF 上限、AES-GCM 和安全解包，使 T062/T063 通过
- [ ] T071 [US3] 扩展 `src/kindergarten_manager/infrastructure/credentials.py` 保存 WebDAV/S3 secret 与可选缓存恢复口令，缺失时只关闭对应外部能力
- [ ] T072 [P] [US3] 实现 `src/kindergarten_manager/infrastructure/backups/webdav.py` 的不可变加密对象操作与脱敏错误
- [ ] T073 [P] [US3] 实现 `src/kindergarten_manager/infrastructure/backups/s3.py` 的 boto3 SigV4 对象操作，不自行实现签名且不把 multipart ETag 当 SHA-256
- [ ] T074 [US3] 实现 `src/kindergarten_manager/application/backups.py` 的 daily/manual/轮换、上传、列举、下载和恢复事务，恢复前停止新任务并关闭全部 Session/engine
- [ ] T075 [US3] 在 `src/kindergarten_manager/application/bootstrap.py` 接入“当日本地备份”和“迁移前备份失败即停止升级”，只有成功后更新 last backup date
- [ ] T076 [US3] 实现 `src/kindergarten_manager/ui/pages/backups.py` 的本地/远程清单、具体版本选择、进度/取消、口令输入、恢复确认和失败重试
- [ ] T077 [US3] 在 `src/kindergarten_manager/app.py` 装配备份适配器并保证远程操作只经 Qt runtime 后台运行，普通数据库事务不等待远程网络
- [ ] T078 [US3] 运行 T061–T066、Slice 1/2A/2B 回归、Ruff/Pyright，并在 `docs/implementation-evidence/desktop-slice-3-acceptance.md` 记录篡改/错口令/远端中断/跨新安装恢复及远程失败下 100 次本地保存证据

**Checkpoint**: 数据可恢复且远端只是一组加密不可变备份；没有同步、冲突合并或远端 SQLite。

---

## Phase 7: User Story 2 - Agent 确认写入（Priority: P2 write stage）

**Goal**: 只在 Slice 3 备份恢复通过后，为已注册教案字段增加 `PlanPatch`、逐次确认、最小不可变
审计和单事务 WRITE；不得扩大为设置、归档、删除、文件、备份或远程写入。

**Independent Test**: 使用 Scripted Provider 和临时 SQLite，验证精确 Patch 展示、Confirmation
绑定、stale/重放/过期拒绝、有效确认精确提交，以及 snapshot/正文/revision/audit 任一步失败全
回滚；Provider 断网不影响确认后的本地事务。

### Tests for Agent WRITE（必须先 RED）

- [ ] T079 [P] [US2] 在 `tests/desktop/contracts/test_agent_patch_confirmation.py` 覆盖规范 `PlanPatch`、关闭字段路径、稳定 hash、字段级 before/after，以及 Confirmation 绑定 patch/target/revision/session/turn/expiry/nonce
- [ ] T080 [P] [US2] 在 `tests/desktop/database/test_agent_action_audit_migration.py` 覆盖 `0001` -> `0002_agent_action_audit`、命名 FK/unique/check、UPDATE/DELETE 拒绝、无正文列和迁移前备份失败即停止
- [ ] T081 [P] [US2] 在 `tests/desktop/application/test_agent_confirmed_write.py` 覆盖未确认/伪造/错 hash/错目标/错 turn/过期/复用/stale 零写入、有效确认精确字段提交和未知 commit action ID 对账不重放
- [ ] T082 [P] [US2] 在 `tests/desktop/contracts/test_agent_write_privacy.py` 覆盖 audit/SQLite/备份/log/repr 不含 Prompt、Provider 原文、Context、Tool 输入输出、before/after 正文、Key、口令或绝对路径
- [ ] T083 [P] [US2] 在 `tests/desktop/ui/test_agent_confirmation_flow.py` 覆盖完整差异/警告/快照影响展示、明确确认、拒绝、修改后重新生成、stale 后重新确认和无“总是允许”
- [ ] T084 [US2] 收集并运行 T079–T083 得到干净 RED并记录到 `docs/implementation-evidence/desktop-agent-write-red.md`；先证明 Slice 3 pre-migration/restore 可用，失败不得来自 Provider 网络或环境错误

### Implementation for Agent WRITE

- [ ] T085 [P] [US2] 扩展 `src/kindergarten_manager/application/agent_runtime.py` 实现规范 Patch builder、一次性内存 Confirmation、过期/Context 失效和双重验证，不把确认授权给 Provider
- [ ] T086 [US2] 创建 `0002_agent_action_audit` migration 与不可变模型，只保存 action/tool/target/patch/confirmation/revision/outcome/time；先调用已验收 pre-migration 备份
- [ ] T087 [US2] 在 `src/kindergarten_manager/application/agent_tools.py` 注册仅限教案白名单字段的 WRITE Tool，在一个短事务中重读、校验、保存操作前版本、应用完整 Patch、递增 revision 和写 audit，任一步失败全部回滚
- [ ] T088 [US2] 扩展 `AgentRuntime.confirm/reject`，使 confirm 创建新的本地 WRITE operation，WRITE 永不自动重试；取消、迟到、未知 commit 只对账不重放
- [ ] T089 [US2] 扩展 `src/kindergarten_manager/ui/widgets/agent_draft.py` 显示逐字段差异和一次性确认/拒绝，不提供批量长期授权；确认后 Context/Patch 立即失效
- [ ] T090 [US2] 运行 T079–T083、Slice 1/2A/2B/3 回归、迁移/备份专项、Ruff/Pyright，并在 `docs/implementation-evidence/desktop-agent-write-acceptance.md` 记录零写入负向矩阵、精确提交、全回滚、审计最小化和重启无记忆证据

**Checkpoint**: Agent 只能把教师已看到并逐次确认的单一 Patch 原子写入；Level 3 Workflow、
多 Agent、后台自主执行和长期业务记忆仍不存在。

---

## Phase 8: Slice 4 / User Story 1 - 批量 Word 预览与合并（Priority: P1 extension）

**Goal**: 在已稳定的单日渲染核心上增加同学期日期预览、一个 DOCX 合并、逐日进度、取消和原子发布。

**Independent Test**: 用同一学期包含工作日、周末、节假日、人工覆盖、未知日历和缺失教案的范围，预览与最终日期 100% 一致，输出只有一个 Word 且每日从新页开始；任意阶段取消不留下不完整成品。

### Spike and Tests for Slice 4（必须先过 spike，再得到业务 RED）

- [ ] T091 [US1] 在 `tests/desktop/contracts/test_word_batch_spike.py` 完成同模板 3 日 body/section/header/footer/relationship/分页 spike，并在 `docs/implementation-evidence/desktop-word-batch-spike.md` 记录 Microsoft Word 实机结果；失败即停止本切片并回到设计
- [ ] T092 [P] [US1] 在 `tests/desktop/application/test_batch_export_preview.py` 覆盖同学期范围、升序冻结、跳过原因、人工覆盖、未知日历有教案则纳入以及空范围拒绝
- [ ] T093 [P] [US1] 在 `tests/desktop/contracts/test_word_batch_export.py` 覆盖单日/批量同日样式等价、每天完整模板/新页、重新打开校验、第一/中间/发布前取消和旧目标保留
- [ ] T094 [P] [US1] 在 `tests/desktop/ui/test_batch_export_flow.py` 覆盖预览数量/明细、原生目标选择、覆盖确认、进度、取消与错误反馈
- [ ] T095 [US1] 收集并运行 T092–T094 得到干净 RED并记录到 `docs/implementation-evidence/desktop-slice-4-red.md`，同时保持 T016 单日 Word 契约通过；不得用 spike 文档代替业务测试

### Implementation for Slice 4

- [ ] T096 [US1] 扩展 `src/kindergarten_manager/application/exports.py` 实现 `preview_batch`，在事务内冻结 included/skipped/warnings 且后台不重新查询“最新”清单
- [ ] T097 [US1] 实现 `src/kindergarten_manager/infrastructure/exports/batch_renderer.py`，只复用同一 `render_day` 生成的模板节点，禁止 ZIP 字节拼接和多个最终文件
- [ ] T098 [US1] 实现 `src/kindergarten_manager/ui/pages/batch_export.py` 的日期范围、预览确认、进度/取消和最终单文件反馈
- [ ] T099 [US1] 在 `src/kindergarten_manager/app.py` 装配批量导出后台任务，发布前再次检查取消并丢弃页面切换后的迟到信号
- [ ] T100 [US1] 运行 T091–T094、全部 Word 回归、Ruff/Pyright，并在 `docs/implementation-evidence/desktop-slice-4-acceptance.md` 记录 Windows Word 中文/空格/长路径、文件锁与分页实机证据

**Checkpoint**: 固定主序列和批量 Word 扩展均完成：MVP → AI 2A → Agent 2B READ/DRAFT →
备份恢复 → Agent 确认 WRITE → 批量 Word。

---

## Phase 9: User Story 1 Completion - 历史、归档、查找与周导航（Priority: P1 remainder）

**Goal**: 补齐规格中不属于首个最小闭环的手工教案能力，但不得改变此前切片的行为。

**Independent Test**: 自动保存不创建版本；显式版本、历史恢复、归档/恢复归档按语义创建不可变快照；归档只读；搜索和周导航保护未保存内容。

- [ ] T101 [P] [US1] 在 `tests/desktop/application/test_lesson_plan_history.py` 覆盖 3 秒自动保存、显式版本、历史恢复、归档/恢复归档快照语义和归档只读
- [ ] T102 [P] [US1] 在 `tests/desktop/application/test_calendar_navigation.py` 覆盖人工工作日覆盖/撤销、查找过滤、上一周/下一周/本周和重叠学期不静默猜测
- [ ] T103 [P] [US1] 在 `tests/desktop/ui/test_history_archive_navigation.py` 覆盖固定保存状态、历史列表、归档只读、日期主题轨道和切换上下文的未保存保护
- [ ] T104 [US1] 收集并运行 T101–T103 得到干净 RED并记录到 `docs/implementation-evidence/desktop-us1-completion-red.md`，失败不得来自此前切片回归或计时不稳定 fixture
- [ ] T105 [US1] 扩展 `src/kindergarten_manager/infrastructure/database/repositories.py` 实现不可变版本、归档状态、日历覆盖和查找查询，使数据库触发器拒绝历史 UPDATE/DELETE
- [ ] T106 [US1] 扩展 `src/kindergarten_manager/application/lesson_plans.py` 并实现 `src/kindergarten_manager/application/calendar.py` 的 autosave/version/archive/restore/find/override/week 用例
- [ ] T107 [US1] 扩展 `src/kindergarten_manager/ui/pages/daily_plan.py` 并新增 `src/kindergarten_manager/ui/widgets/week_strip.py`、`history_panel.py`，实现自动保存、周导航、主题轨道和历史/归档交互
- [ ] T108 [US1] 运行 T101–T103、US1 全部回归和重启恢复验收，并在 `docs/implementation-evidence/desktop-us1-completion-acceptance.md` 记录自动保存 5 秒内反馈且不制造历史快照

**Checkpoint**: User Story 1 的全部规格行为完成且仍可完全离线使用。

---

## Phase 10: User Story 4 - 桌面体验与 Windows 分发收敛（Priority: P4）

**Goal**: 完成主题、最低窗口、高 DPI、焦点/键盘、安装/升级/卸载保留和可审计发布物。

**Independent Test**: 在干净 Windows 11 x64、1366x768、125%/150% 下用浅色/深色/跟随系统执行核心流程；standalone per-user 安装、升级、卸载、重装均不删除数据，发布元数据完整。

- [ ] T109 [P] [US4] 在 `tests/desktop/ui/test_theme_accessibility.py` 覆盖三种主题即时切换/持久化、焦点轮廓、状态不只靠颜色和切换不丢编辑内容
- [ ] T110 [P] [US4] 在 `tests/desktop/ui/test_responsive_workspace.py` 覆盖 1366x768 布局、辅助区折叠、主要操作无水平滚动和 125%/150% 几何约束
- [ ] T111 [P] [US4] 在 `tests/desktop/packaging/test_payload_manifest.py` 覆盖 standalone 载荷只含新桌面入口、Qt/SSL/SQLite/模板/日历/keyring 资源且不含旧 Web/API/Worker
- [ ] T112 [US4] 收集并运行 T109–T111 得到干净 RED并记录到 `docs/implementation-evidence/desktop-us4-red.md`；Linux offscreen 结果只算自动化证据，不标记 Windows 验收完成
- [ ] T113 [US4] 实现 `src/kindergarten_manager/ui/theme.py`、`src/kindergarten_manager/ui/icons/` 与统一状态令牌，使 T109 通过且不引入第三方 Fluent 控件库
- [ ] T114 [US4] 收敛 `src/kindergarten_manager/ui/main_window.py` 和各页面响应式布局、键盘顺序、可访问名称与固定状态区，使 T110 通过
- [ ] T115 [US4] 创建 `packaging/windows/pysidedeploy.spec`，锁定 pyside6-deploy/Nuitka standalone、MSVC 2022、只读模板及 Qt 插件收集，并使 T111 通过
- [ ] T116 [US4] 创建 `packaging/windows/installer.iss` 的中文 per-user 安装/升级/卸载规则，程序进入 `%LOCALAPPDATA%\Programs` 且卸载默认保留稳定数据根
- [ ] T117 [US4] 实现 `src/kindergarten_manager/infrastructure/update_check.py` 与 `src/kindergarten_manager/ui/pages/about.py`，只检查版本并打开 HTTPS 下载页，不静默下载执行或规避 SmartScreen
- [ ] T118 [US4] 在 `docs/implementation-evidence/desktop-windows-acceptance.md` 记录真实 Windows DPI、主题、文件对话框、凭据、Word 打开、冷机安装、升级/卸载保留和无 Python/Qt 启动证据
- [ ] T119 [US4] 运行全部 UI/packaging 测试与 Windows 构建，在 `docs/implementation-evidence/desktop-release-manifest.md` 核对 EXE 大小/SHA-256/完整 Git SHA/SBOM/许可证清单；FC-001 的 MSIX 仅保留后续兼容验证，不作为首期门禁

**Checkpoint**: 四个用户故事和 Windows 首发证据齐全；Linux 结果未被冒充为 Windows 证据。

---

## Phase 11: Polish & Cross-Cutting Quality Gates

**Purpose**: 只处理跨切片验证、文档和 Review，不加入新业务能力。

- [ ] T120 [P] 在 `README.md`、`CONTEXT.md`、`docs/ROADMAP.md` 与 `specs/003-desktop-local-first/quickstart.md` 同步实际完成范围、启动/测试命令、数据目录、Agent 权限/无长期记忆、备份恢复和平台限制，不宣称未观察到的验收
- [ ] T121 [P] 在 `tests/desktop/contracts/test_privacy_and_secrets.py` 扫描 SQLite、备份、日志、异常、示例与发布载荷，拒绝幼儿个人信息、Key、口令、token、真实身份 fixture 和 Agent conversation/Context/Patch/Provider 原文残留
- [ ] T122 运行 `uv sync --locked`、Ruff format/check、Pyright、`uv run pytest` 及 quickstart 全矩阵，分别记录 Linux 自动化与 Windows 人工/安装结果
- [ ] T123 运行 `graphify update .` 和 `graphify diagnose multigraph --graph graphify-out/graph.json --undirected`，确认新代码图没有旧 Web/API/Worker/PostgreSQL 运行时依赖且生成物未手工编辑
- [ ] T124 在固定实现提交上分别执行 Standards 与 Spec Review，将结论写入 `docs/implementation-evidence/desktop-final-review.md`，核对 Issue docs SHA、任务证据、Agent Tool/确认/事务/无记忆、模板哈希、凭据/备份安全、Windows 证据与非目标后再申请进入 `main`

### Agent Requirement Coverage

| Requirement | 覆盖任务 | 完成证据 |
|---|---|---|
| FR-033 单 Agent/Application Layer | T049、T051、T052、T054、T057、T059、T060 | 单 turn、重复拒绝、无子 Agent/并行 Tool |
| FR-034 Tool-only | T049、T051、T056、T057、T060 | 未知/越权/任意能力拒绝与 registry 扫描 |
| FR-035 最小 Context | T050、T053、T054、T056、T057、T060 | 白名单、revision、秘密/无关数据排除 |
| FR-036 READ/DRAFT 零写入 | T049、T051–T060 | SQLite/版本/preview/audit/备份/log 零变化 |
| FR-037 Patch + Confirmation | T079、T081、T083–T085、T088–T090 | 完整差异、精确绑定、过期/复用/stale 拒绝 |
| FR-038 审计与事务 WRITE | T080–T082、T084、T086–T090 | migration、全有或全无、未知 commit 不重放 |
| FR-039 Provider port | T049、T051、T055、T057、T060 | OpenAI-compatible/Scripted Adapter 与 SDK 隔离 |
| FR-040 线程/事务 | T052、T057、T059、T081、T087、T088、T090 | 冻结 DTO、每 Tool Session、确认期间零事务 |
| FR-041 无长期业务记忆 | T050、T051、T053、T059、T060、T082、T090、T121 | DB/备份/log/重启扫描零残留 |
| SC-011 Agent 权限与确认矩阵 | T060、T090 | 所有负向用例零写入，有效 Patch 精确提交 |
| SC-012 Agent 状态零持久化 | T053、T060、T082、T090、T121 | 仅业务结果和最小不可变审计留存 |

FC-003 的 Level 3 Workflow 是明确非目标，不计入首期任务覆盖率；T005、T049、T056、T059、
T111、T121 和 T124 共同阻止其入口、调度器、动态 Tool 或发布载荷空壳。

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Design confirmed + Issue + dev authorization
  -> Phase 1 Setup
  -> Phase 2 Foundation
  -> Slice 1 MVP (US1: startup to single-day Word)
  -> Slice 2A optional AI Provider + structured preview (US2)
  -> Slice 2B Agent Foundation + READ/DRAFT only (US2)
  -> Slice 3 remote backup and restore (US3)
  -> Agent confirmed WRITE (US2)
  -> Slice 4 batch Word (US1 extension)
  -> US1 remainder
  -> US4 UI/package convergence
  -> Cross-cutting gates and Review
```

- **Slice 1** 不依赖 AI、远程网络或批量 DOCX，是唯一建议的 MVP。
- **Slice 2A** 只依赖 Slice 1 的教案、版本表和 Qt runtime；AI 关闭时不得改变 Slice 1。
- **Slice 2B** 依赖 Slice 2A Provider 防护和 Slice 1 Application Layer；只注册 READ/DRAFT，
  不依赖备份，也不得提前实现任何 WRITE/Confirmation 数据路径。
- **Slice 3** 依赖 SQLite/Bootstrap/runtime，但远程失败不得成为 US1/US2 数据事务依赖；它是
  Agent 写入 migration 和正式 WRITE 的前置门禁。
- **Agent WRITE** 依赖 Slice 2B 与 Slice 3；`0002_agent_action_audit` 必须先生成 pre-migration
  备份，WRITE 只消费已确认 Patch，不依赖 Provider 网络。
- **Slice 4** 必须先通过 T091 spike，并复用 Slice 1 的单日 snapshot/render core。
- **US1 remainder** 排在固定 Agent 主序列和批量 Word 之后，只补历史、归档、查找和周导航。
- **US4** 在业务切片稳定后收敛视觉和分发；真实 Windows 证据不能被 Linux 替代。

### Task-Level Gates

- 每个切片先写该切片 tests，再执行 `pytest --collect-only`，确认环境干净后取得业务 RED。
- 数据模型在 T022/T023 建立 `0001_desktop_initial`；唯一计划中的后续首期 revision 是 T086 的
  `0002_agent_action_audit`，且必须在 Slice 3 后执行。其他切片不得另起冲突基线。
- 同一文件上的任务按 ID 串行；只有标记 `[P]` 且文件/行为均独立的任务可以并行。
- 每个 Checkpoint 都要重跑此前切片回归；后续测试失败不得计入当前切片未完成。
- T124 之前仍须逐门授权 commit、push、Review 和 `main` 集成；任务勾选本身不授权 Git 操作。

## Parallel Opportunities

### Slice 1

- T011–T017 可分别编写路径/启动、迁移、设置、领域、Repository、Word 和 UI 测试。
- T019 路径服务与 T020 纯领域提取可并行；数据库 T021–T025 必须按依赖串行。
- T030 首次设置页可在 T026 应用服务契约稳定后与 T028 Renderer 并行。

### Slice 2A

- T035–T039 测试文件独立；T041 领域规则与 T042 凭据边界可并行。
- AI client、Coordinator 和 UI 必须依次接合，避免让 Widget 或运行中任务成为权威状态。

### Slice 2B

- T049–T052 测试文件独立；T054 值对象与 T055 Provider Adapter 可并行。
- T056 registry 完成后才能接 T057 Runtime loop；T058/T059 只能在 Runtime Interface 稳定后接入。
- 本阶段禁止以并行机会为由创建子 Agent、并行 Tool call 或 WRITE Tool。

### Slice 3

- T061–T066 可并行编写；T072 WebDAV 与 T073 S3 适配器共享契约但实现文件独立。
- Snapshot → Envelope → BackupService/Restore 是安全依赖链，不得为并行而绕过验证。

### Agent WRITE

- T079–T083 测试文件独立；T086 migration 必须在 Slice 3 验收后串行执行。
- T085 Patch/Confirmation -> T087 transactional Tool -> T088 Runtime -> T089 UI 是固定依赖链。
- Provider Adapter 不参与本地 WRITE 事务，不能与 T087 并行发起网络调用。

### Slice 4 and Later

- T092–T094 可在 T091 spike 通过后并行；T096/T097 完成后再接 T098/T099。
- US4 的主题测试、响应式测试和载荷测试文件独立；真实 Windows T118 只能在构建产物存在后执行。

## Implementation Strategy

### MVP First

1. 完成 T001–T010，验证正式包边界和测试环境。
2. 完成 T011–T018，取得 Slice 1 的干净 RED。
3. 完成 T019–T034，独立验收首个桌面闭环。
4. **STOP**：在新授权前不进入 AI；MVP 不以未来功能的测试或占位页面冒充完成。

### Incremental Delivery

1. Slice 1：离线启动、设置、SQLite、班级/学期、保存、当天 Word。
2. Slice 2A：AI Provider 可选生成、结构化预览和人工采用；回归 Slice 1。
3. Slice 2B：单 Agent、Context、READ/DRAFT Tool；以零正式写入为门禁。
4. Slice 3：本地恢复与 WebDAV/S3 加密备份；验证远程故障隔离。
5. Agent 写入：精确 Patch、逐次确认、最小审计和单事务 WRITE。
6. Slice 4：批量预览与单文件 Word 合并；复用单日 Renderer。
7. 补齐 US1 历史/归档/导航，再完成 US4 与正式 Windows 分发证据。
8. 每个切片独立 Review、独立测试、独立授权，不机械复制旧 B/S 模块边界。

## Notes

- `[P]` 仅表示依赖安全，不表示允许创建额外实现分支或绕过单一 `dev` 集成线。
- 测试和示例全部使用虚构教师、园所、班级和教案；常规测试禁止真实 AI/WebDAV/S3 网络。
- 旧代码只按 plan.md 的复用矩阵提取可证明行为；禁止复制旧 apps、认证、多园、PostgreSQL、Redis/Worker 和 HTTP 下载编排。
- FC-002 的 `.docx` 原始教案导入、拆分/补全与新增适龄环节属于下一期，不得在 T001–T124 创建表、入口或空实现。
- FC-003 的 Level 3 Workflow、多 Agent、跨步骤自治、无人值守 WRITE 和长期业务记忆继续延后，
  不得在 T001–T124 创建调度器、Provider thread、动态 Tool 或兼容空壳。
