<!--
Sync Impact Report
- Version change: 2.1.0 -> 3.0.0
- Modified principles:
  - 技术、安全与范围约束 -> WebAuthn 首选登录 + 密码与 TOTP 双因素备用登录
- Added sections: none
- Removed sections: none
- Templates reviewed:
  - ✅ .specify/templates/plan-template.md（无需修改）
  - ✅ .specify/templates/spec-template.md（无需修改）
  - ✅ .specify/templates/tasks-template.md（无需修改）
  - ✅ .specify/templates/checklist-template.md（无需修改）
  - ✅ .specify/templates/constitution-template.md（无需修改）
- Runtime guidance reviewed:
  - ✅ AGENTS.md
  - ✅ CONTEXT.md
  - ✅ README.md
  - ✅ CONTRIBUTING.md
  - ✅ docs/ROADMAP.md
  - ✅ docs/development/single-implementation-development.md
- Command templates: .specify/templates/commands/ is not present in this installation
- Migration and compatibility:
  - M3 T036–T045 与 0004_settings.py 保持不变
  - M3A 使用独立 Issue 和 0005_password_totp_backup_login.py
  - 旧 M2 密码列删除历史不回滚；新摘要只存在于独立备用认证表
- Follow-up condition: 本次 docs 提交确认并由 Issue 固定后，才可在 dev 实施 M3A
-->
# Child Manager 项目宪章

## Core Principles

### I. 事实来源与范围忠实

每项规格、计划、任务和实现都必须先依据其领域事实来源：`AGENTS.md` 管理开发过程，
`docs` 分支中的 `docs/`、`specs/`、OpenAPI 契约和 `templates/` 管理产品、架构、稳定契约与
导出版式，`README.md` 管理稳定概览与导航，GitHub Issue 管理执行状态与验收证据。
旧仓库只能提供经验，不能成为本项目需求。若来源冲突，
必须指出位置和影响，并停止会固化冲突的工作，直到获得明确确认。实现必须保持当前任务
的最小范围；不得预建照片、视觉、对象存储、审批、多园运营或生产部署空壳。

### II. 服务边界与单向依赖

NiceGUI Web、FastAPI API 和 Dramatiq Worker 必须保持独立运行边界。Web 只能通过 API
使用业务能力，不得连接数据库或导入 ORM、Repository、`packages/backend`。API 必须拥有
认证、授权、输入校验、事务和业务编排；Worker 只能依据 PostgreSQL 中的权威任务上下文
执行 AI、Word 等长任务。`packages/contracts` 只能承载稳定请求、响应、事件、任务、错误
和枚举契约。新增抽象必须对应第二个实现、外部集成边界或明确测试替身，禁止机械工厂、
通用插件系统和无业务价值的接口层。

### III. 园所隔离与服务端授权（NON-NEGOTIABLE）

所有园所范围业务表、Repository 方法、查询、写入、唯一性校验和组合外键都必须显式包含
`kindergarten_id`。园所身份只能来自 API 的服务端会话上下文，客户端提交值不能作为授权
依据。API 必须在每次请求验证账号状态、角色、园所和教师—班级关系；页面隐藏按钮不构成
权限控制。教师只能访问关联班级；管理员可查看、导出、归档和恢复全园教案，但未同时
具备该班教师身份时不得编辑正文、调用 AI 或维护班级区域。任何跨园或跨班越权均为发布
阻断缺陷。

### IV. 权威状态、事务与可恢复性

PostgreSQL 必须是业务数据和后台任务状态的唯一权威，数据库结构只能通过 Alembic 修改。
教案唯一性、乐观锁、快照时机、归档只读和历史不可变等不变量必须由数据库约束与应用
事务共同保证。Redis 只负责任务投递和运行协调；API 与 Worker 必须使用最小任务契约、
幂等键、租约和恢复扫描收敛数据库/Redis/文件之间的失败窗口。重复消息、重试或进程恢复
不得重复创建版本、覆盖人工内容、突破最多三次模型调用或覆盖既有导出。

### V. 教师控制、AI 与 Word 保真

系统必须在 AI 或在线节假日服务不可用时保持手工创建、编辑、保存、归档和导出主流程。
AI 必须通过供应商中立的 OpenAI 兼容适配器与已发布提示词运行，使用固定结构化 Schema
校验，并先保存预览；只有教师明确采用且版本校验通过后才能写入正文和创建快照。外部
请求必须最小化数据。Word 导出必须复制固定模板、保持表格与样式、校验模板哈希，且只有
带结构化新增标记的集体活动新增环节使用红色字体；不得覆盖原模板或从零重建近似文档。

### VI. 可执行验证与真实证据

每个用户故事必须可独立验收，每项任务必须包含明确路径与验证方式。缺陷修复必须先添加
可复现失败的测试。实现必须按风险覆盖单元、API、Repository 园所隔离、PostgreSQL 迁移、
Worker 幂等与恢复、AI 替身、Word 样式和关键 Web 流程；常规测试不得访问真实 AI、在线
节假日接口或其他外部网络。只有实际执行的命令和观察到的结果才能作为完成证据；不得
通过删除测试、放宽断言、伪造状态或把计划文件当作实现来宣告完成。

## 技术、安全与范围约束

- 目标基线必须是 Python 3.14+、NiceGUI、FastAPI、PostgreSQL、SQLAlchemy 2.x、
  Alembic、Redis、Dramatiq 2.x、`uv`、Ruff、Pyright 和 Pytest。
- 产品只交付 Cloud 版本；首期一个运行实例服务一所幼儿园，同时保留未来多园隔离边界。
  PostgreSQL 是生产数据库；SQLite 只可用于快速开发和确定性测试，不得替代 PostgreSQL
  的迁移、组合外键、部分索引、GiST、并发和事务验证。
- 首期仅有管理员和教师，界面使用简体中文；业务日期按 `Asia/Shanghai` 计算，时间点以
  UTC 存储。
- WebAuthn 通行密钥必须是首选且具备钓鱼抗性的登录方式；系统可以提供密码与 TOTP
  两项共同成立的独立备用登录，但不得提供密码单独、TOTP 单独、短信/邮件验证码、默认
  管理员或万能恢复码弱兜底。管理员必须配置完整备用登录，教师可以选择启用。备用会话
  可以使用角色允许的普通业务；最近五分钟再次完成密码与 TOTP 验证只可新增通行密钥，
  不能删除旧凭据或修改其他高风险身份材料。备用因素的建立、重设和关闭必须由 WebAuthn
  重新验证保护；所有通行密钥均不可用时仍必须同时满足离线恢复码与人工核验，最后管理员
  继续要求双人核验。首位管理员和后续账号仍分别使用本机短时初始化凭据或管理员单次邀请
  绑定首个通行密钥。访问与刷新令牌只能通过安全的 HttpOnly Cookie 传递；状态变更必须
  具备 SameSite、来源校验和 CSRF 防护。开发关闭 Cookie `Secure` 仅允许显式配置与回环
  地址绑定。
- AI Key 必须由服务端认证加密保存；初始化/邀请/恢复秘密、令牌、API Key、主密钥、完整
  敏感教案和未来照片不得进入 Git、Redis 消息、日志、异常、审计或测试快照。
- 首期功能验收完成前，不得设计、创建或验收生产 Caddyfile、生产 Compose、公网 DNS、
  证书、端口映射、Tailscale、生产密钥托管、生产备份任务或发布流程。ADR-0007 中相关
  旧结论已由 ADR-0009 取代。
- 原始 Word 模板 `templates/teacherplan/teacherplan.docx` 必须保持只读；运行时输出只能
  写入专用临时或导出目录，测试数据不得包含真实教师或幼儿身份。

## 开发工作流与质量门禁

1. 工作开始前必须按 `AGENTS.md`、`README.md`、`CONTEXT.md`、`CONTRIBUTING.md`、`docs`
   分支中任务对应的 Roadmap/PRD/设计/ADR/规格/契约/模板、GitHub Issue、迁移和测试的顺序
   建立事实底稿；仓库可查信息不得转问用户。
2. 多步骤任务必须先列出最短计划，并为每步给出可执行验证。正式实现 Issue 必须固定引用
   已确认的 `docs` 提交，并包含范围、非目标、验收标准和验证方式；缺少任一项不得开始实现。
3. 长期分支固定为：`main` 保存稳定版本与发布基线，禁止临时开发；`docs` 保存 PRD、架构、
   ADR、Context、Development Guide、共享规格、OpenAPI 和模板，禁止修改业务代码、迁移、
   实现测试或依赖锁；`dev` 是 Codex 唯一实现与集成分支。流程必须是
   `Design -> docs -> Issue -> dev -> 测试 -> Review -> main`。未经明确授权不得切换/创建
   分支、提交、推送、创建 PR、合并或改写历史。
4. 从工程骨架建立后，每个相关实现阶段至少执行：

   ```bash
   uv sync --locked
   uv run ruff format --check .
   uv run ruff check .
   uv run pyright
   uv run pytest
   ```

   尚未配置的命令必须如实报告；数据库、Worker、Word 和真实 UI 流程还必须执行对应专项
   检查。业务代码或活跃治理/架构文档变化后应运行 `graphify update .`，失败时记录原因。
5. 评审必须逐项检查本宪章、PRD 验收、服务依赖、园所隔离、权限、迁移、事务、任务幂等、
   数据最小化、模板哈希和非目标。任何未解释的宪章违反都必须在进入实现前消除。

## Governance

本宪章是 Spec Kit 规格、计划和任务的强制治理门禁，但不替代 `AGENTS.md` 的开发规则，
也不改写 PRD、ADR、数据模型或 Word 模板的领域事实。发现冲突时必须按“事实来源与范围
忠实”原则暂停，而不是降低本宪章或其他已确认约束。

宪章修订必须：说明动机和影响；同步受影响的 Spec Kit 模板、运行指导和活动规格；记录
迁移或兼容措施；经项目维护者明确批准。版本遵循语义化版本：移除或重新定义不可协商原则
为 MAJOR，新增原则或实质扩展治理为 MINOR，澄清且不改变语义为 PATCH。所有规格评审、
计划评审、任务生成和实现交付都必须再次执行宪章检查；复杂度例外必须在计划中列出更简单
方案及其被拒理由。

**Version**: 3.0.0 | **Ratified**: 2026-07-12 | **Last Amended**: 2026-07-23
