# Implementation Plan: 首期一日活动计划完整闭环

**Branch**: `docs`（共享规格）；`dev`（唯一实现） | **Date**: 2026-07-12 | **Updated**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: `specs/001-daily-activity-plan/spec.md`；范围为 Roadmap M1–M8，M9 生产部署复审排除。

## Summary

交付单园云版一日活动计划完整首期：先建立 Python 3.14 monorepo、认证与园所/班级授权，
再完成必要设置、手工教案和历史，随后接入 PostgreSQL 权威状态的异步 AI、教师栏目级采用、
固定 Word 导出、审计、降级与功能验收。NiceGUI Web、FastAPI API 和 Dramatiq Worker 独立
运行；浏览器只访问当前实现档位的 NiceGUI Web，同源 `/api/v1/*` 由 Web 作为服务端 BFF
（Backend for Frontend）转发到本档位回环 API。BFF 必须转发 Cookie、`Origin/Referer`、
`X-CSRF-Token` 与 API 的 `Set-Cookie`，浏览器不得直连本档位 API 端口。所有业务
真相保存在 PostgreSQL，Redis 只负责投递和短期协调；AI 结果先成为结构化预览，只有教师
明确采用时修改正文并创建快照。

BFF 必须丢弃浏览器提交的 `Forwarded`、`X-Forwarded-For` 和内部客户端地址头，再根据其
直接 socket 对端重建内部来源信息；API 仅在直接对端是显式配置的回环 Web BFF 时信任该
内部头，用于公开身份 ceremony 的来源限流。生产代理链与信任列表仍留到 M9 复审。

本计划直接采用本轮已确认的差异：当前学期必需但学期外周次为空；区域按目标栏目校验；
一键只生成四栏，反思在五栏完整后由教师显式触发；集体拆分先采用保存，之后才独立生成、
预览和采用新增环节；
`pending_dispatch` 即表示请求已受理；栏目基线与实际输入决定预览是否过期；解绑教师立即
撤权但保留署名快照；工作日来源新增 `unavailable`；导出缺失确认只检查前五栏，空反思仍
保留模板三行但不触发确认。实现前先同步仍保留旧表述的共享文档。

## Technical Context

**Language/Version**: Python 3.14+
**Primary Dependencies**: NiceGUI 3.x、FastAPI、Pydantic 2、SQLAlchemy 2、Alembic、
Psycopg 3、Dramatiq 2 + Redis、HTTPX、PyJWT、webauthn 3.x、cryptography、python-docx、
chinesecalendar
**Storage**: PostgreSQL（生产业务与任务权威状态）；Redis（消息投递/短期协调）；受保护的
本地开发导出目录与临时目录（生产持久化方案延后）；SQLite 仅限不依赖 PostgreSQL 特性的
单元/开发测试
**Testing**: Pytest（单元、契约、API、Repository、迁移、Worker、AI 替身、Word）；
NiceGUI 核心流程浏览器冒烟；Ruff、Pyright、依赖方向检查、敏感信息扫描
**Target Platform**: Linux 上的独立 Web/API/Worker 进程；WebAuthn ceremony 只在受限公网的
HTTPS 单一来源或自动化/本地开发的 `localhost` 安全上下文执行；生产拓扑仍延后到 M9
**Project Type**: Python monorepo Web application + API + background worker
**Performance Goals**: 普通页面/列表 P95 ≤ 2 秒；保存 P95 ≤ 1 秒；后台任务受理并返回 ID
≤ 2 秒；页面每 1–2 秒短轮询且完成/失败/离页后停止
**Constraints**: 同园同班同日唯一教案；园所隔离和 API 服务端授权；乐观锁；历史不可变；
AI 总模型调用 ≤ 3；常规测试零真实外部调用；固定 Word 模板 SHA-256
`72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043`；核心流程满足
WCAG 2.2 AA 可验证要求
**Scale/Scope**: 首期单实例单园；最多 100 个账号、30 个并发会话、至少 100 个排队任务；
31 张首期表、7 个稳定 AI 任务、6 个教案栏目、1 个固定 Word 模板

## Constitution Check

*GATE: M0、M1 为 `complete`；历史双实现证据保留。自 2026-07-21 起采用 `main/docs/dev` 单实现流程。M2 为 `in_progress`，#4 是 `dev` 的唯一当前验收入口；M3 在 M2 完成前保持 `pending`。*

| 宪章门禁 | 内部设计检查 | 当前 Pre-M1 实现门禁 | 计划证据 |
| --- | --- | --- | --- |
| I. 事实来源与范围忠实 | PASS | **PASS（M0）** | canonical 文档、历史清理与最终共享基线均已验证 |
| II. 服务边界与单向依赖 | PASS | **PASS（M1）** | 历史 Codex、Trae 实现均通过 BFF/API/Worker 边界与依赖方向验证；当前 `dev` 仍须维持该门禁 |
| III. 园所隔离与服务端授权 | PASS | **PENDING（M2+）** | 31 实体、组合外键、Repository 参数和 API 权限矩阵已设计；M1 不实现业务数据与授权 |
| IV. 权威状态、事务与可恢复性 | PASS | **PASS（M1 基础）** | 历史实现已建立 PostgreSQL 事务与迁移基础；业务幂等、租约、恢复扫描和文件补偿由后续里程碑实现 |
| V. 教师控制、AI 与 Word 保真 | PASS | **PENDING（M4+）** | 固定 Schema、栏目级预览、采用事务、模板副本/哈希和红字边界已设计，尚未进入对应里程碑 |
| VI. 可执行验证与真实证据 | PASS | **PASS（M1）** | M1 工程入口与质量门禁已有历史证据；当前和后续用户故事仍须在 `dev` 按对应里程碑重新验收 |

**前置同步与授权处理**: T001～T003 以及 Codex/Trae 的 M1 T004～T020 保留为历史记录。自 2026-07-21 起，新的实现必须由 Issue 固定引用已确认的 `docs` 提交，并只在 `dev` 执行；历史验收不自动替代当前文档基线的验证。

**Complexity result**: 无需宪章例外；Web/API/Worker 是已接受的三个运行单元，不属于新增
复杂度。31 张表包含通行密钥、challenge、邀请、恢复与身份核验所需的 12 张身份表；不增加
密码兼容表、反思表、环节表或事务消息系统。

## Project Structure

### Documentation (this feature)

```text
specs/001-daily-activity-plan/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── README.md
│   ├── openapi.yaml
│   └── job-state-machine.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root, implementation target)

```text
apps/
├── web/
│   ├── __main__.py
│   ├── app.py
│   ├── api_client.py
│   ├── pages/
│   │   ├── auth.py
│   │   ├── plans.py
│   │   ├── class_areas.py
│   │   ├── settings.py
│   │   └── audit.py
│   └── components/
├── api/
│   ├── __main__.py
│   ├── app.py
│   ├── dependencies.py
│   └── routers/
│       ├── auth.py
│       ├── users.py
│       ├── settings.py
│       ├── prompts.py
│       ├── plans.py
│       ├── jobs.py
│       ├── exports.py
│       └── audit.py
└── worker/
    ├── __main__.py
    ├── broker.py
    ├── actors.py
    └── scheduler.py

packages/
├── contracts/
│   ├── common.py
│   ├── identity.py
│   ├── settings.py
│   ├── prompts.py
│   ├── lesson_plans.py
│   ├── jobs.py
│   ├── exports.py
│   └── audit.py
└── backend/
    ├── bootstrap/
    ├── database/
    │   ├── base.py
    │   ├── session.py
    │   └── migrations/
    ├── identity/
    ├── settings/
    ├── prompts/
    ├── lesson_plans/
    ├── jobs/
    ├── exports/
    ├── audit/
    └── integrations/
        ├── ai/
        ├── calendar/
        ├── crypto/
        └── files/

templates/
└── teacherplan/

tests/
├── architecture/
├── contract/
├── unit/
├── api/
├── repository/
├── migrations/
├── worker/
├── word/
├── web/
└── fixtures/
```

**Structure Decision**: 采用现有架构文档的 monorepo。`apps/*` 只含传输和装配；
`packages/backend/*` 的应用用例拥有授权、事务、幂等与审计；Repository 不自行提交事务；
`packages/contracts` 不含 ORM、Repository、业务逻辑或供应商客户端。M1 创建 API、Worker、
Web 三个可执行入口，并冻结后续初始化 CLI 的命令名称，供 quickstart 和自动化引用；
`init-admin start/activate/recover-last-admin` 的真实业务行为仍由 T032 实现，不在 M1 提供
误导性的空操作。Web 的
`--api-base-url` 仅供 BFF 在服务器侧访问
内部 API；浏览器唯一入口是当前实现档位的 `CHILD_MANAGER_WEB_PORT`，其 `/api/v1/*` 请求由
BFF 转发。Dev 固定档位见
[`local-development-environments.md`](../../docs/development/local-development-environments.md)：

```bash
# T032 完成后可执行：
uv run python -m packages.backend.bootstrap init-admin start
# 浏览器完成首个通行密钥登记和双人带外核验后：
uv run python -m packages.backend.bootstrap init-admin activate --bootstrap-id <uuid>
# 已形成有效待核验恢复请求且目标确为最后管理员时：
uv run python -m packages.backend.bootstrap init-admin recover-last-admin \
  --recovery-request-id <uuid>
# Dev 分支相应实现完成后可执行：
uv run python -m apps.api --host 127.0.0.1 --port "$CHILD_MANAGER_API_PORT"
uv run python -m apps.worker
uv run python -m apps.web --host 127.0.0.1 --port "$CHILD_MANAGER_WEB_PORT" \
  --api-base-url "http://127.0.0.1:${CHILD_MANAGER_API_PORT}"
```

入口名称属于本 feature 的实现契约；当前 `main` 尚无代码。Codex 分支在 T004～T020 后可
执行 API、Worker、Web 命令；初始化子命令仅冻结名称，其真实行为在 T032 完成前不可执行。

## Phase 0: Research

**Output**: [research.md](./research.md)

- 冻结首期边界、技术依赖和外部集成策略。
- 将所有逐项确认转化为 Decision / Rationale / Alternatives。
- 核对依赖的 Python 3.14 可用性和许可；对声明不完整的 Word/日历库执行隔离冒烟。
- 固定旧提示词参考提交，禁止继承旧协议。
- 记录共享文档同步事实和实现前复核门禁。

**Exit verification**:

```bash
rg -n "NEEDS CLARIFICATION|\[FEATURE\]|\[DATE\]|\[###" specs/001-daily-activity-plan \
  --glob '!plan.md' --glob '!checklists/requirements.md'
```

预期无匹配；所有高影响边界已由文档或用户答案解决。

## Phase 1: Design & Contracts

**Outputs**: [data-model.md](./data-model.md)、[contracts/](./contracts/)、
[quickstart.md](./quickstart.md)

### 数据与事务设计

- 沿用 19 个业务实体并新增 7 个 WebAuthn/邀请/恢复实体，连同 5 个既有身份实体共 31 个实体；
  以 `kindergarten_id`、同园组合外键和 Repository 必填参数保证隔离。
- 身份迁移使用 expand → enroll → contract：先建新表并停用密码端点、撤销旧会话，再由
  `migration_admin` 发放单次登记邀请，确认账号完成通行密钥登记后物理删除旧密码列；降级
  只能重建空列，不恢复旧认证能力。
- 初始迁移直接采用学期外周次双空、`source_code=unavailable`、模型默认并发 2，以及 AI
  预览目标栏目基线哈希，不为尚不存在的数据制造兼容迁移。
- 手动保存/归档/恢复/历史恢复/AI 采用在事务内同时处理版本、快照、正文、作者与审计。
- 教师点击反思时，API 在一个数据库事务内校验 `expected_version`、保存页面提交的当前正文
  （该预保存不创建教案快照）、验证五个上游栏目，并写入幂等记录、`pending_dispatch` 任务
  与唯一 pending AI 结果占位；结果占位冻结五栏输入/哈希、目标基线、模型、提示词和 Schema。
  任一步失败全部回滚且不消耗 Idempotency-Key。任务 `current_plan` 只含五个已保存上游栏目
  与必要展示上下文，不含当前旧反思。
- 任务保存后先返回 `pending_dispatch`；扫描、租约、心跳和幂等写入收敛 Redis/Worker
  故障窗口。导出在 CAS 无快照预保存的同一事务复制不可变上下文/正文输入并创建记录和
  任务；Worker 不重读可变当前教案，再以临时文件、校验、原子改名和孤儿清理收敛文件窗口。
- AI 受理事务同样创建唯一结果占位，冻结栏目基线、实际输入、模型、提示词和结果 Schema；
  Worker 只按任务 ID 填充输出，并在外部调用前重验请求人权限、归档和模型启用状态；采用时
  再重读当前可变输入并判断预览是否失效。
- 提示词测试的同一受理事务把经固定 Schema 校验的实际 variables、提示词正文/哈希、结果
  Schema 和模型的 `profile_id/base_url/model_name/capabilities/call_config_revision` 非密钥调用
  配置冻结在 `prompt_test_runs`；公开 `input_summary` 只列变量名和值已脱敏标志。地址、模型名、
  能力或密钥变化原子递增 revision；Worker 外呼前若当前值与冻结值不同，则以
  `prompt.configuration_changed` 零调用失败。revision 一致时才读取当前密钥并实时复核权限、
  模型启用和当前地址安全；完整上下文不进入 Redis、响应、日志或审计。
- `ai.batch` 父记录不投递且不保存第二套执行状态，响应状态实时由恰好四个子任务派生；显式
  重试只克隆最终失败 AI 栏目任务的冻结结果输入，提示词测试和 Word 导出通过各自创建端点
  表达新意图。batch 的数据库执行状态、attempt 和租约字段为 NULL，API 将两个 attempt 字段
  投影为 `0/0`。

### API 与任务契约

- `/api/v1` 统一 Cookie/CSRF、分页、错误、请求 ID、版本冲突和 Idempotency-Key。
- 权限矩阵同时约束 Web 可见能力与 API 实际授权；请求不得提交园所或角色扩大权限。
- NiceGUI Web 是浏览器唯一同源 BFF：浏览器只访问本档位 Web 端口，BFF 把 `/api/v1/*`
  转发到本档位回环 API 端口，并双向转发 Cookie/Origin/Referer/CSRF 与 `Set-Cookie`；浏览器伪造的代理地址
  头必须被剥离，API 只信任显式回环 BFF 重建的内部来源信息。Foundational 集成测试逐项
  验证方法、路径、query、body、认证/来源头、多个 `Set-Cookie`、请求 ID 与 hop-by-hop 头，
  浏览器冒烟的网络记录不得出现直连本档位 `CHILD_MANAGER_API_PORT`。认证完成/刷新各保留
  两条 access/refresh `Set-Cookie`，退出保留两条过期 Cookie，禁止逗号折叠。
- OpenAPI 明确拆分注册与认证的 options/verify ceremony，并覆盖首位管理员初始化、单次邀请、
  本人凭据、管理员撤销与重新邀请、恢复申请/核验/恢复码轮换，以及会话列表/撤销。Challenge
  为 32 字节随机值、5 分钟单次有效，绑定 purpose、RP ID、精确 Origin、账号和上下文；常规
  ceremony 强制用户验证，注册要求 discoverable credential。
- AI 预览采用复核目标栏目基线和实际输入哈希；全局版本仍用于写入 CAS，相关冲突不覆盖。
- 提示词只使用 `\{\{[ \t]*([a-z][a-z0-9_]*)[ \t]*\}\}` 白名单纯替换，复杂值采用稳定
  JSON；解析器不执行表达式、过滤器、循环、嵌套访问或变量值递归渲染。
- 幂等 scope 使用方法和规范化路由模板；请求 fingerprint 还必须纳入已规范化的实际路径
  参数、有语义查询参数及 canonical JSON body，跨 `plan_id`、提示词 code 或 `job_id` 复用同
  key 必须冲突而不能错误重放。
- 除反思采用单事务预保存外，Web 在提交一键或其他单栏 AI 请求前先完成无快照自动保存；
  保存失败或版本冲突不提交生成，API 仍以保存后的 `expected_version` 校验任务基线。
- Word 导出、AI 生成/重试及其他长任务采用 202 + 权威任务状态；页面可在重载后恢复。
- `/health/ready` 仅在 PostgreSQL 或所有核心请求共同依赖的全局 JWT/CSRF 安全配置不可用时
  返回 503；AI、Redis、日历、模板和导出存储等功能专属检查只令整体 200 响应中的分项为
  degraded，实际依赖端点可在受理前返回 `configuration.unavailable`。

### Quickstart 验收合同

- 当前 `main` 无 `pyproject.toml`、代码、迁移或测试，quickstart 只能描述实现后的可执行
  验收，不得声称命令已通过。
- M1 后使用 API、Worker、Web 三个可执行入口；T032 完成后再使用已冻结的初始化与最后管理员
  恢复子命令；后者只接受恢复请求 ID，交互匹配初始化时保存的两项预登记引用，Web/API 对
  最后管理员审批只返回 `identity.last_admin_recovery_requires_cli`；
  WebAuthn 使用浏览器虚拟认证器或 `localhost` 安全上下文，AI/节假日使用固定替身。
- 覆盖初始化凭据、注册/认证 ceremony、邀请、凭据撤销/重新邀请、恢复码与会话、园所隔离、
  手工教案、并发、任务恢复、AI 采用、集体部分成功、
  Word 样式与审计，并明确生产部署和未来子系统反目标。

**Post-design Constitution Check**: 内部设计、T002 最终 Pre-M1 审查、M0-G1～M0-G8、T003 与 M1 T004～T020 均已完成，M0、M1 为 `complete`。M2 已进入 `in_progress`，后续由 #4 与 `dev` 单实现门禁验收。

## Phase 2: Task Generation Strategy

`tasks.md` 按依赖和用户故事组织，不按技术层横切交付。先执行共享文档同步和 M1 基础，再按
US1–US7 建立可独立验收的纵向切片：

1. **Setup / Foundational**: 文档同步、工程骨架、契约、数据库、隔离、日志、测试替身。
2. **US1 / M2**: T021–T035 完成初始化、认证授权、园所隔离和身份审计独立门禁。
3. **US1 / M3**: T036–T045 在 M2 可信身份上下文上完成必要设置独立门禁。
4. **US2**: 纯手工教案、日期、历史、归档和恢复。
5. **US3**: 模型档案、密钥封装和提示词生命周期/测试。
6. **US4**: 可靠异步任务、一键四栏、独立预览/采用和显式反思。
7. **US5**: 安全导入、集体拆分和新增环节部分成功。
8. **US6**: 固定 Word、独立导出历史和授权下载。
9. **US7**: 审计查询与故障边界降级；性能、安全汇总、可访问性和完整验收由最终 Polish
   跨故事阶段完成，不在 US7 checkpoint 提前标记通过。

每个故事先写失败的单元/API/Repository/专项测试，再实现最小通过行为；常规测试不访问
真实外部服务。实现代码变化后按 `AGENTS.md` 运行 `graphify update .`。

## Milestone Gates

| Gate | 完成条件 | 验证证据 |
| --- | --- | --- |
| Pre-M1 | 已确认差异同步至 canonical 文档，且无未解释冲突 | 文档 diff + Spec Kit analyze |
| M1 | 三入口、锁文件、质量工具、数据库/Redis 本地测试依赖可用 | `uv sync --locked` + 五条标准命令 + health checks |
| M2 | 初始化、通行密钥、邀请、恢复、会话、角色和园所隔离可独立验收 | WebAuthn 浏览器/API/Repository/迁移负向矩阵 |
| M3 | 所有直接依赖设置可用，区域允许部分配置 | 设置 API/Web 与隔离测试 |
| M4 | 模型 Key、SSRF、七个提示词生命周期可审计 | crypto/prompt/API/替身测试 |
| M5 | 无 AI 时完整手工教案闭环可用 | 浏览器冒烟 + 并发/快照/迁移测试 |
| M6 | 可靠任务、四栏一键、显式反思、集体部分成功可用 | Worker 恢复/幂等/AI Schema 测试 |
| M7 | 固定模板导出及历史下载保真 | Word 结构/样式/哈希/权限测试 |
| M8 | 所有未延后验收有可复现证据 | 全量质量命令、性能、安全、浏览器报告 |

## Risk Controls

| 风险 | 控制 |
| --- | --- |
| canonical 文档与新答案再次漂移 | 更新 PRD/设计后同步入口文档，并在实现前复跑 Spec Kit 一致性审查 |
| 初始化、邀请或恢复秘密泄露/重放 | 只显示一次、仅存摘要、短时单次消费、状态机与并发消费约束；日志和审计只留脱敏元数据 |
| WebAuthn ceremony 被跨用途或跨来源重放 | challenge 绑定 purpose、账号、上下文、RP ID 与精确 Origin，5 分钟单次消费并强制 UV |
| 管理员误撤最后凭据导致失联 | 本人不得撤销最后有效凭据；管理员撤销教师最后凭据后原子撤销会话并重新邀请；最后管理员恢复采用双人带外核验 |
| 园所/班级越权 | 组合外键、Repository 必填园所、API 每请求实时授权、负向测试 |
| DB/Redis 双写窗口 | `pending_dispatch`、幂等 key、DB 锁扫描、租约与重复消息测试 |
| AI 覆盖教师内容 | 结构化预览、栏目/输入哈希、采用事务和乐观锁 |
| 密钥或敏感正文泄露 | AEAD、最小消息/审计、脱敏错误、代码与日志扫描 |
| `.docx` 资源消耗/主动内容 | 四级大小限制、OOXML 校验、拒绝宏/外链/穿越、临时清理 |
| Word 版式漂移 | 模板哈希、固定单元格/样式断言、原件状态检查 |
| 延后项混入实现 | 任务 anti-goals；M8 验收不包含生产部署或未来子系统 |

## Complexity Tracking

无内部设计复杂度例外；M0、M1 已完成。当前只有 `dev` 承载实现，任何历史分支结果都不能替代 #4 与后续 Issue 的当前验收门禁。
