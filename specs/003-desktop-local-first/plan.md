# Implementation Plan: 幼儿园管理助手桌面首期

**Design Branch**: `design/desktop-local-first`\
**Implementation Branch**: `dev`（仅在发布 docs、创建 Issue 并完成 T001 后开放已授权切片）\
**Date**: 2026-08-08\
**Spec**: [`spec.md`](spec.md)（已确认；实施时必须固定为本轮 `docs` 的完整提交 SHA）\
**Issue**: 由本轮 `docs` 发布后的完整提交 SHA 创建；Issue URL、SHA 与授权记录只在 `dev`
的 T001 回填，避免用移动分支名或制造自引用提交

**Input**: `specs/003-desktop-local-first/spec.md`、ADR-0012、宪章 v4.1.0，以及维护者要求冻结
PySide6、SQLite、Alembic、本地数据目录、模块边界、Word 单日/批量导出、备份和打包策略。

## Summary

首期实现为 Windows 单进程 PySide6/Qt Widgets 桌面应用。SQLite 是唯一业务数据权威，
SQLAlchemy 2.x 管理同步事务，新的独立 Alembic 迁移链负责 Schema 演进。应用不启动 HTTP
服务，不依赖浏览器、FastAPI、PostgreSQL、Redis、Dramatiq 或独立 Worker。

实施采用 `ui -> application -> domain` 单向依赖，基础设施通过窄边界接入 SQLite、操作系统
凭据、OpenAI 兼容 AI、受控单 Agent、固定 Word 模板和 WebDAV/S3。旧 B/S 代码只按行为和纯逻辑逐项提取：
保留结构化教案、日期规则、AI 校验和 Word 模板经验，废弃 Web/API/Worker、认证、多园、
PostgreSQL 与队列装配，避免把旧模块数量当作复用目标。

## Technical Context

**Language/Version**: CPython `3.14.6` x64 标准 GIL 构建；项目约束 `>=3.14,<3.15`，由
`.python-version` 与 `uv.lock` 固定解释器和全部传递依赖\
**Primary Dependencies**: PySide6 `6.11.*`（首锁 `6.11.1`）、Qt Widgets、SQLAlchemy
`2.0.*`（首锁 `2.0.51`）、Alembic `1.19.*`（首锁 `1.19.0`）、Pydantic `2.12.*`、
python-docx `1.2.*`、chinesecalendar `1.11.*`、httpx `0.28.*`、cryptography `49.*`、
keyring `25.*`；S3 适配器使用 boto3 的锁定稳定版本\
**Storage**: CPython 随附 `sqlite3` + 单一 SQLite 文件；`foreign_keys=ON`、rollback journal、
`synchronous=FULL`、`busy_timeout=5000`；秘密只进入 Windows Credential Locker 或 Linux
Secret Service\
**Testing**: Pytest、Pyright、Ruff；临时 SQLite 文件、AI/WebDAV/S3/凭据替身、DOCX 结构与
样式回归；Linux offscreen 桌面烟雾 + Windows 真实安装和高 DPI 验收\
**Target Platform**: Windows 11 x64 首发；Ubuntu GNOME 支持源码运行、Secret Service 与真实
AI/Agent 测试，但不声明 Linux 安装包；不声明 Windows 10 或 macOS 首期发布支持\
**Project Type**: 单进程桌面应用\
**Performance Goals**: 1366x768、125%/150% DPI 下编辑保持响应；停止输入 5 秒内显示保存
结果；普通打开/保存不被远程服务阻塞；批量导出与备份持续报告进度并可取消\
**Constraints**: 核心流程完全离线；单教师多班级；不得保存幼儿个人信息；数据库、备份与
日志不在安装目录；不共享 SQLite 连接跨线程；不自动恢复未完成 AI/Agent 任务；单 Agent、
Tool-only、READ/DRAFT 先行、逐 Patch 确认 WRITE、无长期业务记忆\
**Scale/Scope**: 单机一个数据库、一个当前教师资料、数十班级/学期、数千教案及版本；首期
仅一日活动计划、设置、数据与备份，不预建其他业务模块

## Constitution Check

### Phase 0 前门禁

- [ ] **实施入口**：本文件本身不授权实现；必须先完成 `docs` 提交/推送和引用完整 SHA 的
  Issue，再由 `dev` 的 T001 核对授权范围。当前授权只开放 Slice 1 RED，不开放 GREEN 或
  Agent Foundation。
- [x] 范围、非目标、验收、风险和验证责任已由 003 规格、ADR-0012 与本计划明确。
- [x] 正式实现只以 `dev` 为目标；当前 Design 分支只包含文档和可丢弃原型。
- [x] 单进程 PySide6、SQLite 唯一权威、单教师、无认证/多园/Cloud 符合宪章 II–IV。
- [x] AI 可选且先预览后采用；Word 基于只读模板副本，符合宪章 V。
- [x] 受控 Agent 仍由教师逐次确认、只经 Application Tool 访问业务且不持久化长期业务记忆，
  没有降低宪章 II、IV、V 的本地权威与教师控制要求。
- [x] Linux 自动化与 Windows 人工/安装证据分离，符合宪章 VI。

结论：**Design 门禁通过；实施入口只可按 docs -> Issue -> dev/T001 顺序打开。** 未发现需要
以复杂度例外解释的宪章违反。

### Phase 1 后复核

- [x] `research.md` 已消除技术选型中的 `NEEDS CLARIFICATION`。
- [x] `data-model.md` 不含账号、角色、租户、幼儿、照片、任务队列或同步实体。
- [x] `contracts/` 明确 UI 只能调用应用服务，后台任务不直接操作 Widget 或共享数据库连接。
- [x] 单日/批量 Word、备份包、恢复和原子发布失败语义均有可执行契约。
- [x] 旧 B/S 复用矩阵按行为分类，未把 Web/API/Worker 基础设施搬入桌面。
- [ ] docs 完整 SHA 与 Issue URL 仍须在发布后由 T001 固定到 `dev`；在此之前不得写正式代码，
  完成后也只按维护者本次授权进入 Slice 1 RED。

结论：**Phase 1 设计通过；下一治理动作是发布 `docs`、创建 Issue、完成 T001，再开始 Slice 1
RED。Agent Foundation 仍保持关闭。**

## Project Structure

### Documentation (this feature)

```text
specs/003-desktop-local-first/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── application-services.md
│   ├── agent-runtime.md
│   ├── backup-package-v1.md
│   └── word-export.md
└── tasks.md                 # 已生成的完整首期任务清单
```

### Source Code (formal implementation target)

```text
src/kindergarten_manager/
├── __main__.py
├── app.py                   # 唯一 composition root
├── ui/
│   ├── main_window.py
│   ├── runtime.py           # Qt 线程、信号、取消桥接
│   ├── theme.py
│   ├── icons/
│   ├── widgets/
│   └── pages/
├── application/
│   ├── dto.py
│   ├── bootstrap.py
│   ├── settings.py
│   ├── lesson_plans.py
│   ├── ai_generation.py
│   ├── agent_runtime.py
│   ├── agent_tools.py
│   ├── exports.py
│   └── backups.py
├── domain/
│   ├── lesson_plans.py
│   ├── content.py
│   ├── calendar.py
│   ├── ai.py
│   ├── exports.py
│   └── backups.py
└── infrastructure/
    ├── database/
    │   ├── engine.py
    │   ├── models.py
    │   ├── repositories.py
    │   ├── migrations/
    │   └── upgrade.py
    ├── paths.py
    ├── credentials.py
    ├── ai/
    │   └── agent_provider.py
    ├── exports/
    └── backups/

templates/teacherplan/
└── teacherplan.docx         # 唯一源模板；构建时按哈希复制到发布载荷

packaging/windows/
├── pysidedeploy.spec
├── installer.iss
└── msix/                    # 后期 Store 通道，不属于首期完成门禁

tests/desktop/
├── unit/
├── application/
├── database/
├── contracts/
├── integration/
├── ui/
└── packaging/
```

**Structure Decision**: 正式桌面代码只进入新的 `kindergarten_manager` 根命名空间。它不得从
`apps/web`、`apps/api`、`apps/worker` 或旧 PostgreSQL Repository 运行时导入。现有
`apps/desktop/prototype_daily_plan.py` 继续是可丢弃原型，不能移动或改名后冒充正式 UI。

## Frozen Architecture Decisions

### 1. 模块与依赖方向

```text
Qt Widgets -> application services -> domain
                     |
                     +-> concrete infrastructure adapters
```

- Widget 只持有 ViewModel/DTO 和命令回调，不持有 SQLAlchemy Session、HTTP 客户端、DOCX
  对象或凭据。
- 应用服务拥有用例、事务与快照边界；领域模块不导入 PySide6、SQLAlchemy、httpx、boto3、
  keyring 或 python-docx。
- SQLite Repository 是具体的本地深模块。首期不为每个 Repository 建接口；只有 AI 客户端、
  凭据存储、Word 渲染和远程备份因存在外部实现或测试替身而定义窄 Protocol。
- `app.py` 是唯一装配点。禁止通用插件平台、依赖注入容器、事件总线和本地 HTTP 层。

### 2. 受控 Agent Runtime

- 全应用只装配一个 `AgentRuntime`，位于 Application Layer；同一时刻最多一个 Agent turn，
  不创建子 Agent、并行 Agent、委派或 Level 3 Workflow。
- Provider 是不受信外部 Adapter，只能返回文本或请求 registry 中的类型化 Tool。Runtime 不向
  Provider 暴露 Repository、Session、SQLite、文件、Widget、凭据、任意 URL 或代码执行能力。
- `AgentContext` 按 turn 从 READ Tool 构建，只含最小冻结投影和相关 revision；会话结束、切换
  Context、取消或退出即丢弃，不建立 conversation/message/vector/summary/profile 表。
- Slice 2B 只注册 READ/DRAFT Tool。DRAFT 生成规范 `PlanPatch` 但零持久化；正式 WRITE 只能在
  Slice 3 备份恢复之后，通过绑定 Patch hash、目标、revision、会话/turn、有效期和 nonce 的
  一次性 `Confirmation` 解锁。
- WRITE 在确认后新开短事务，事务内重读、校验 revision/字段摘要/业务不变量，并原子创建操作前
  快照、应用完整 Patch、更新 revision 与追加最小审计。失败全部回滚，WRITE 不自动重试。
- Application Layer 依赖窄 `AgentProviderPort`；OpenAI-compatible 与 Scripted Adapter 是两个
  Adapter。具体 SDK 类型不得穿过 seam。
- 完整 Interface、错误语义、线程/事务契约见 [`contracts/agent-runtime.md`](contracts/agent-runtime.md)。

### 3. SQLite、事务与 Alembic

- 新数据库使用独立迁移链，不继承旧 `0001`–`0010` PostgreSQL revision，也不迁移旧数据：
  Slice 1 固定为 `0001_desktop_initial`；Slice 2A 用 `0002_desktop_ai` 从已存在的 `0001`
  数据库增加非敏感 AI 配置、提示词覆盖和已校验预览；Slice 3 通过后，Agent WRITE 再用
  `0003_agent_action_audit` 增加最小不可变审计。不得改写已发布 revision 来追加后续表。
- 应用首次启动和每次升级只调用 Alembic `upgrade head`；禁止 `create_all()` 修改正式库。
- `env.py` 启用命名约定和 `render_as_batch=True`。迁移必须显式检查 SQLite 上的外键、唯一
  约束、CHECK 和索引，不信任未经审阅的 autogenerate 输出。
- 每个工作线程建立并关闭自己的 Session/连接；连接不跨线程传递。应用层串行化写事务，
  后台线程只接收冻结 DTO，或使用独立只读/备份连接。Provider 等待和教师确认期间不得保持
  数据库事务；每个 Agent Tool 调用独立取得并关闭 Session。
- 启动顺序固定为：路径/空间检查 -> 打开并完整性检查 -> 必要时升级前备份 -> Alembic ->
  `foreign_key_check`/关键计数 -> 启动 UI。失败时停止写入并保留原库及备份。

### 4. 本地目录

使用 `QStandardPaths.GenericDataLocation` 取得系统本地持久数据目录，再附加稳定 ASCII 应用
标识 `cn.kindergartenmanager.desktop`；不得拼接用户主目录或依赖中文显示名：

```text
GenericDataLocation/cn.kindergartenmanager.desktop/
├── data/child-manager.sqlite3
├── backups/
│   ├── daily/
│   ├── pre-migration/
│   └── pre-restore/
├── recovery/                # 仅恢复事务的短期回滚副本
├── staging/                 # 与数据库同卷，便于恢复/导出原子替换
├── cache/
└── logs/
```

用户 Word 和可携带备份始终通过原生文件对话框选择目标；默认从 `DocumentsLocation` 开始。
安装、升级和卸载不得默认删除上述数据根目录。

### 5. Word 单日与批量导出

- 单日和批量共用一个纯渲染核心和同一模板哈希；不维护两套字段映射。
- 单日输入为一个冻结 `DailyPlanExportSnapshot`。批量先生成可审阅 `BatchExportPreview`；
  同一学期内已确认非工作日和无教案日期跳过，日历未知但已有教案则纳入并警告，所有纳入
  快照按日期升序冻结。
- 批量生成一个 DOCX；每一天复制完整模板内容，第二天起在完整模板前插入分页符。禁止把多日
  内容压缩到同一张表或生成多个最终文件。
- 生成写入目标目录内的随机临时文件，全部渲染、重新打开和结构校验成功后 `os.replace()`
  发布。取消、异常或文件锁定只删除临时文件，不覆盖旧目标。
- 旧 `TeacherplanRenderer` 的单元格映射与样式测试可提取；旧 Job、PostgreSQL Export Store、
  Worker 重试、导出历史和 HTTP 下载不得复用。

### 6. 备份与恢复

- SQLite 一致性副本必须通过 `sqlite3.Connection.backup()` 生成，随后执行完整性检查和
  SHA-256；不得在数据库打开时直接复制主文件/WAL。
- 每日、迁移前和恢复前本机备份存放数据目录。每日备份最多保留最近 30 份；迁移前/恢复前
  备份不被每日轮换立即删除。
- 可携带/远程备份采用 `KMBACKUP1` 容器：规范化清单 + SQLite 快照组成 ZIP 载荷，使用
  scrypt（`N=2^17,r=8,p=1`、16 字节随机盐）派生 256 位密钥，再以 AES-256-GCM 和 96 位
  随机 nonce 整体认证加密。版本、应用标识、备份 ID 与 Schema 版本绑定为 AAD。
- AI Key、WebDAV/S3 凭据和可自动运行的恢复口令通过 keyring 进入 Windows Credential
  Locker（`local-machine`）或 Linux Secret Service（`local-user`）；Null、文件、未知或仅
  伪造显示名的 backend fail closed。SQLite 和备份只保存“已配置”状态与非敏感 Endpoint/对象键。
- WebDAV/S3 只上传加密完成的不可变对象。失败只更新备份结果；不加入同步、增量上传、最新
  版本自动选择、冲突合并或远端直接打开 SQLite。
- 恢复先下载/解密到 staging，验证格式、AAD、哈希、SQLite 完整性和可迁移性，再创建当前库
  保护性备份并原子替换。任何失败都恢复原状态。

### 7. Windows 打包与更新

- 只在 Windows x64 构建发布物。`pyside6-deploy` 以受版本控制的 `pysidedeploy.spec` 调用
  Nuitka `standalone` 模式；不采用 onefile，避免每次启动解压和资源路径漂移。
- 首期锁定 `pyside6-deploy 6.11.1` + Nuitka `4.0`，使用 MSVC 2022（Python 3.14 不走
  MinGW）；锁定 Inno Setup `7.0.2` x64 生成中文、per-user、无需管理员权限的标准安装器。
  安装器只部署程序和
  只读资源到 `%LOCALAPPDATA%\Programs`，卸载默认保留应用数据。
- 发布同时产出安装 EXE、版本、大小、SHA-256、构建 Git SHA、SBOM/许可证清单和构建日志。
  未签名 EXE 不规避 SmartScreen；应用只检查版本并打开 HTTPS 下载页。
- 后期 Store 通道复用同一 standalone payload，通过 Windows SDK/MSIX manifest 生成 x64
  MSIX，由 Store 签名和更新。MSIX 与 EXE 共用稳定应用 ID 和数据目录契约，但分别执行升级、
  卸载保留和凭据访问验收。

## Old B/S Reuse and Retirement Matrix

| 分类 | 旧资产 | 桌面处理 |
|---|---|---|
| 原样保留 | `templates/teacherplan/teacherplan.docx` | 继续作为唯一模板；构建与测试核对 SHA-256 |
| 提取后复用 | `packages/contracts/lesson_plans.py` 的首期四栏、反思和当前教案内容模型 | 提取值对象到 `domain/content.py`；移除 API ContractModel 与 Cloud 字段；下一期 group split/add-step/source 模型不落盘 |
| 提取后复用 | `packages/backend/lesson_plans/calendar.py` | 保留教学周、日期文本、季节纯函数；工作日来源改为本地库 + 人工覆盖 |
| 提取后复用 | `lesson_plans/schemas.py`、`ai_schemas.py`、`ai_fingerprints.py` | 保留完整性、结构校验和目标栏目哈希；去除 Job/园所/权限上下文；不得把旧生成流程解释为 Agent Tool 或确认协议 |
| 适配复用 | `integrations/ai/client.py` 与 URL policy | 保留 OpenAI 兼容、超时、响应上限、禁止 userinfo/重定向；重写 Cloud allowlist：回环可 HTTP，非回环必须 HTTPS |
| 适配复用 | `integrations/files/teacherplan_renderer.py` | 保留已验证字段映射与样式写入，新增冻结快照和同模板批量合并 |
| 只复用行为证据 | 相关 calendar/content/AI/Word 单元测试与 DOCX fixture | 迁移断言和虚构 fixture；不把旧 Web/API/Worker 测试计为桌面验收 |
| 明确废弃 | `apps/web`、`apps/api`、`apps/worker` | 不进入运行时或打包产物 |
| 明确废弃 | identity/auth、WebAuthn/TOTP/invite/token/role/tenant | 首期无账号、认证、角色或多园隔离 |
| 明确废弃 | PostgreSQL Repository、旧 Alembic 迁移、GiST/组合园所外键 | 建立 SQLite 专用模型和新迁移链；旧数据不迁移 |
| 明确废弃 | Redis/Dramatiq Job、lease、recovery scan、scheduler | Qt 线程池 + 进程内任务状态；重启不恢复 AI 任务 |
| 明确废弃 | ExportService/WordExportRunner 的 Job/Store/HTTP 下载层 | 只提取渲染规则，重写桌面导出编排和原子文件发布 |
| 明确废弃 | 多模型档案、提示词发布/回滚子系统、Cloud 审计 | 首期一个当前模型 + 内置可恢复提示词；只保留必要本地诊断 |
| 明确废弃 | Provider 托管 thread、长任务记忆、任意 Tool/插件、Agent 直接 Repository/SQL | 新 Runtime 只用最小 Context、注册 Tool 和本地确认；不迁移任何旧运行状态 |
| 设计证据，不复用代码 | `apps/desktop/prototype_daily_plan.py` 与截图 | 保留布局结论；正式 UI 从任务和契约重新实现 |

## Implementation Sequence

1. **Setup 与 Foundation**：固定授权基线、锁定依赖、建立新命名空间、Qt 后台桥接和架构
   禁入测试。验证：锁定安装、测试收集、Ruff/Pyright 和新命名空间不导入旧 apps。
2. **Slice 1 / MVP：首次启动到当天 Word**：路径、SQLite/Alembic、首次设置、当前教案编辑、
   日期软提示和单日原子导出。验证：断网 Windows 完成首次设置和第一份教案，
   重启后内容仍在且当天 Word 保持模板哈希与样式；历史、归档、批量 Word 暂不计入。
3. **Slice 2A / P2 现有可选 AI**：`0002_desktop_ai` 与升级前最小保护副本、凭据、一个模型、
   提示词覆盖、Qt 后台单任务、结构校验、预览有效性和采用前快照。验证：`0001 -> 0002`
   保护性升级，以及全替身的成功/重试/失败/取消/过期矩阵。
4. **Slice 2B / Agent Foundation**：单 `AgentRuntime`、最小 `AgentContext`、Provider port、Tool
   registry 与 READ/DRAFT Tools。验证：Scripted Provider 的 Tool-only、越权拒绝、零写入、
   无长期业务记忆、单 turn 和取消矩阵；本切片不存在 WRITE Tool。
5. **Slice 3 / P3 备份恢复**：一致性快照、轮换、迁移前备份、加密容器、WebDAV/S3、恢复事务。
   验证：篡改/截断/错口令/远程失败/跨新安装恢复及 100 次本地保存隔离。
6. **Agent 写入阶段**：字段级 `PlanPatch`、完整差异展示、一次性 Confirmation、最小不可变审计
   和单事务 WRITE。验证：未确认/过期/复用/stale 零写入、有效确认精确写入及任意失败全回滚。
7. **Slice 4 / P1 批量 Word**：在单日渲染核心通过 spike 后增加预览、单文件合并、分页、进度、
   取消和原子发布。验证：日期与跳过原因 100% 对齐、模板样式等价及 Windows Word 实机打开。
8. **US1 remainder**：补齐 3 秒自动保存、显式版本、历史恢复、归档/恢复、查找和周导航。
   验证：快照语义、归档只读、日期覆盖和未保存内容保护。
9. **P4 UI 与分发收敛**：主题、高 DPI、键盘/焦点、安装/升级/卸载、发布元数据。验证：真实
   Windows 1366x768、125%/150%、文件对话框、凭据和 Word 打开人工验收。

Level 3 Workflow 不在此序列中；它继续延后，新的 Design/ADR/Issue 之前不得创建调度器、定时
自主运行、跨步骤自动提交或多 Agent 兼容空壳。

## Risks and Controls

- **PySide6/Nuitka/Python 3.14 组合漂移**：只从 `uv.lock` 构建，在 Windows CI 做冷机启动和
  Qt 插件/字体/SSL/SQLite/模板资源烟雾。
- **SQLite 迁移复制表丢约束**：命名全部约束，审阅 batch migration SQL，并在每次 revision
  上做从旧 head 升级、外键/索引/触发器清单比较。
- **批量 DOCX 合并破坏样式**：实施前先做可丢弃 spike，验证 body/section/header/footer/
  relationship；通过后才复制同一模板节点。失败时回到固定批量模板或经审查的专用合并库，
  不得用粗暴 ZIP/XML 拼接或近似重排。
- **备份加密参数未来调整**：KDF/AEAD 参数写入版本化头；旧版本只读兼容，参数升级不重写
  既有备份。
- **旧 B/S 依赖渗透**：添加架构测试禁止 `kindergarten_manager` 导入 `apps.*`、Cloud
  repository/identity/jobs，并检查发布载荷不含 Web/API/Worker 入口。
- **Prompt injection/Provider 越权 Tool**：Tool registry 使用关闭 Schema 与本地 Permission；
  Runtime 拒绝未知/阶段禁用 Tool，Provider 文本不能产生确认或扩大 Context。
- **确认后业务状态变化**：Confirmation 绑定 Patch hash/base revision，WRITE 事务内重读并校验
  字段 before hash；stale 时零写入并要求重新确认。
- **Agent 副本成为第二权威**：Context、对话、Patch 和 ToolResult 只在内存短期存在；只保存
  教师确认后的业务结果与不含正文的最小写入审计。

## Complexity Tracking

无宪章违反需要例外。Repository、外部适配器和 Qt 线程桥接分别对应持久化、第二实现/测试
替身和 UI 线程安全的真实边界；未引入通用插件、事件总线或本地服务。
