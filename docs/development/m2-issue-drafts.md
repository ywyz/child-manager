# M2 认证、授权与身份审计 Issue 草稿与执行记录

> 草稿日期：2026-07-16
> 当前状态：Issue #4～#6 已创建并建立父子关系，尚未授权共享基线同步或业务实现
> 草稿核对时 `main` HEAD：`96920309c92f1ffa95903cd6bf90919ab5fee140`，与远端 `main` 一致
> 共享文档状态：M1→M2 docs-only 内容已发布到 `main`；实现共同基线待获得分支同步授权后按届时 `main` HEAD 回填

## 0. 草稿事实与授权边界

- M1 共享父 Issue [#1](https://github.com/ywyz/child-manager/issues/1)、Codex 子 Issue
  [#2](https://github.com/ywyz/child-manager/issues/2) 和 Trae 子 Issue
  [#3](https://github.com/ywyz/child-manager/issues/3) 均已关闭，M1 为 `complete`。
- M2 为 `ready`，权威任务范围是 T021～T035；M3 必要设置 T036～T045 不属于本里程碑。
- 创建前核对时 GitHub 只有已关闭的 M1 Issue #1～#3，没有重复 M2 Issue；现已创建
  [M2 父 Issue #4](https://github.com/ywyz/child-manager/issues/4)、
  [Codex 子 Issue #5](https://github.com/ywyz/child-manager/issues/5) 和
  [Trae 子 Issue #6](https://github.com/ywyz/child-manager/issues/6)，并将 #5、#6 注册为 #4 的
  原生 Sub-issues。
- M1→M2 docs-only 内容已发布到 `main`；`codex`、`trae` 仍停留在各自 M1 最终 HEAD，不得把
  旧实现分支 HEAD 写成 M2 共同基线。获得分支同步授权后，以包含本文的届时 `main` HEAD
  作为两方完全相同的共同基线并回填 Issues。
- 本文件记录已获授权并完成的 Issue 创建，但不授权同步或切换分支、提交、推送、创建
  Pull Request 或开始 T021。共享基线同步和 M2 实现仍分别等待明确授权。
- M2 仍采用一个共享父 Issue 和两个完整、独立的实现子 Issue；不把 T021～T035 机械拆成
  15 个 GitHub Issue，也不让两个实现互相依赖。

## 1. 共享父 Issue 草稿

### 标题

`M2：认证、授权与身份审计（共享父 Issue）`

### 正文

#### 当前状态与入口

- M1：`complete`；M2：`ready`。
- M1 Issues：#1～#3 均已关闭。
- M2 共同基线：docs-only 内容已发布到 `main`；分别同步到 `codex`、`trae` 后回填精确提交。
- 本 Issue 已创建为 #4；这只表示共享范围已登记，不自动授权分支同步或实现。
- T021～T035 已发布到远端 `main`，但尚未同步两个实现分支；同步和实现分别获得授权前不得
  开始 T021。

#### 共同目标

- 从空 PostgreSQL 安全初始化首位管理员，且重复初始化不产生第二套园所或角色。
- 建立园所、用户、角色、用户角色、刷新令牌和身份审计数据边界及 Alembic 迁移。
- 建立 Argon2id 密码、短期 Access JWT、可轮换/撤销的 opaque Refresh token、重放检测和
  登录限流。
- 建立同源 HttpOnly Cookie、签名双提交 CSRF、来源校验及 API 服务端实时授权。
- 管理员可创建、查看、启停、重置账号和调整角色，并保护最后一个有效管理员。
- NiceGUI Web 提供中文登录、改密和账号管理流程，但仍只通过 API 使用业务能力。
- 从初始化、登录、改密、重置、停用和角色变更开始写入最小化身份审计事件。

#### 任务映射与执行顺序

- T021～T025：先建立身份规则、迁移/隔离、契约、API/CLI 和浏览器流程的有效 RED 测试。
- T026～T034：按依赖实现弱密码资源、身份契约、迁移与模型、密码/令牌/CSRF、可信客户端
  地址与限流、Repository/Service/审计、初始化 CLI、Auth/Users API 和 Web 页面。
- T035：完成 M2 独立验收、标准质量门禁和 graphify 更新。
- Codex、Trae 各自在自己的实现子 Issue 中完整执行 T021～T035；父 Issue 不承载实现专属
  类名、提交列表或临时调试记录。

#### 入口门禁

- [x] M1 已完成，共享父 Issue 和两个实现子 Issue 均已关闭。
- [x] M2/M3 任务边界已在共享规格中明确：M2 为 T021～T035，M3 为 T036～T045。
- [x] 当前 docs-only 修改已形成单一目的共享提交并发布到 `origin/main`。
- [ ] `codex` 与 `trae` 已经授权同步并指向同一版 M2 共享文档基线。
- [x] M2 父 Issue #4 和实现子 Issue #5、#6 的创建已获得明确授权并完成父子关系登记。
- [ ] T021～T035 的业务实现已获得明确授权。

#### 共同出口门禁

- [ ] 空库 `alembic upgrade head` 创建身份与审计 Schema，再次运行保持幂等。
- [ ] 不开放公众注册，不允许停用或移除最后一个有效管理员。
- [ ] 未登录、停用账号、过期/撤销/重放 Refresh token、弱密码、登录限流和缺少 CSRF 的
  请求均由 API 拒绝，且不泄露账号是否存在。
- [ ] PostgreSQL 证明园所组合外键、同园用户名/手机号唯一、角色边界和 Refresh family
  轮换/撤销事务；跨园读写均被 Repository 或数据库边界拒绝。
- [ ] 登录/刷新分别返回两条独立认证 Cookie，退出返回两条独立过期 Cookie；BFF 不逗号
  折叠，Cookie 不进入 JavaScript、NiceGUI 持久化存储或日志。
- [ ] 只有显式开发配置且 Web/API 均绑定回环地址时允许 `Secure=false`；非回环组合拒绝启动。
- [ ] 浏览器冒烟覆盖登录、刷新、退出、改密、账号创建/重置/停用、停用后下一请求失权和
  伪造来源头无效。
- [ ] 身份关键操作产生白名单审计事件，审计不含密码、令牌、Cookie 或完整敏感正文。
- [ ] 两个实现分别通过 T035 专项测试、五条标准质量命令和 graphify 更新；一方通过不代表
  另一方或共享父 Issue完成。

#### 共享事实来源

- [开发规则](../../AGENTS.md)
- [项目上下文](../../CONTEXT.md)
- [Roadmap M2](../ROADMAP.md#8-m2认证授权与身份审计)
- [双 Agent 独立开发协议](dual-agent-development.md)
- [功能规格](../../specs/001-daily-activity-plan/spec.md)
- [实施计划](../../specs/001-daily-activity-plan/plan.md)
- [T021～T035 权威任务](../../specs/001-daily-activity-plan/tasks.md#m2认证授权与身份审计)
- [API v1 契约总则](../../specs/001-daily-activity-plan/contracts/README.md)
- [OpenAPI 3.1 契约](../../specs/001-daily-activity-plan/contracts/openapi.yaml)
- [ADR-0004：同源 Cookie 认证](../ADR/ADR-0004-same-origin-cookie-authentication.md)

#### 实现子 Issue

| 实现 | Issue | 状态 | 目标分支 | 共同基线 |
| --- | --- | --- | --- | --- |
| Codex | [#5](https://github.com/ywyz/child-manager/issues/5) | `pending` | `codex` | 获得分支同步授权后按届时 `main` HEAD 回填 |
| Trae | [#6](https://github.com/ywyz/child-manager/issues/6) | `pending` | `trae` | 与 Codex 完全相同，获得分支同步授权后回填 |

#### 非目标

- 不实现 M3 的学期、班级、年龄段、教师关联、主班教师、区域或工作日设置。
- 不创建教案、AI、提示词、Word 导出、照片、OCR、对象存储、审批或未来业务空壳。
- 不设计生产 Caddyfile、生产 Compose、DNS、证书、Tailscale、备份、密钥托管或发布流程。
- 不在 `main` 添加业务实现，也不统一 Codex、Trae 的内部类名和代码结构。

## 2. Codex 实现子 Issue 草稿

### 标题

`M2：Codex 认证、授权与身份审计实现`

### 正文

#### 关联与边界

- 父 Issue：[#4](https://github.com/ywyz/child-manager/issues/4)。
- 目标分支：`codex`。
- 共同基线：docs-only 内容已发布到 `main`；获得分支同步授权后按届时 `main` HEAD 回填，且
  必须与 Trae 子 Issue 完全相同。
- 当前状态：`pending`；Issue 创建不等于实现授权。
- 远端 `main` 已发布新的 T021～T035 章节；共享基线同步和实现分别获得授权前不得开始 T021。
- 只记录 Codex 自己的方案、提交、迁移、验证、风险和阻塞，不复制或引用 Trae 实现证据。

#### T021～T035 有序执行清单

- [ ] T021：先写标识规范化、可信客户端地址、密码、令牌和登录限流 RED 单元测试。
- [ ] T022：先写身份/审计迁移、同园唯一、组合外键、最后管理员、Refresh family 事务和跨园
  隔离 RED 测试。
- [ ] T023：先写 Auth/Users、Cookie/CSRF、错误和分页 RED 契约测试。
- [ ] T024：先写初始化 CLI、登录/刷新/退出/改密、账号管理、会话撤销和 CSRF RED API 测试。
- [ ] T025：先写登录、账号管理、按角色导航、停用后失权和伪造来源头无效的 RED Web 冒烟。
- [ ] T026：引入冻结版本和哈希的 SecLists 弱密码资源及 MIT 来源说明，不运行真实网络测试。
- [ ] T027：实现 Auth/Users 身份契约及身份操作所需的早期审计事件代码。
- [ ] T028：实现身份/审计模型、迁移和幂等 `admin/teacher` 角色种子。
- [ ] T029：实现标识、密码、Access/Refresh token 和签名双提交 CSRF。
- [ ] T030：实现只信任显式回环 BFF peer 的客户端地址解析、Redis 登录限流和确定性替身。
- [ ] T031：实现同园 Repository、实时授权、最后管理员、会话撤销和身份白名单审计。
- [ ] T032：实现密码不回显、单事务且重复运行安全的 `init-admin` 交互 CLI。
- [ ] T033：接入可信会话、CSRF、登录限流和 Auth/Users API，正确追加独立 Cookie headers。
- [ ] T034：实现中文登录/改密/账号管理 Web 流程、按角色导航和可信 BFF 转发。
- [ ] T035：完成 M2 独立验收、五条标准质量命令和 graphify 更新。

逐项文件、断言和命令以
[T021～T035 权威清单](../../specs/001-daily-activity-plan/tasks.md#m2认证授权与身份审计)
为准；本摘要不得覆盖或弱化 Tasks。

#### 实施与验证原则

1. T021～T025 必须先达到 `collect-only` 成功且 `failed>0, errors=0` 的有效 RED，再开始配对实现。
2. 只实现使当前任务转绿的最小行为；M2 不创建 M3 设置模型、迁移、端点或页面。
3. 每次先运行任务相关快速测试；T035 再运行完整专项矩阵与五条标准质量命令。
4. PostgreSQL、Alembic、Cookie raw headers、CSRF、跨园、撤权、重放和浏览器流程必须有实际
   证据，不能用 SQLite、页面隐藏或另一分支结果替代。
5. 常规测试禁用真实网络；弱密码资源仅按 T026 的冻结版本、来源、哈希和尺寸验收。

#### 验收证据

- 分支 HEAD、共同基线和实际提交：完成后逐项回填。
- RED 证据：逐项回填收集命令、失败断言和 `errors=0`。
- GREEN 与专项测试：逐项回填实际命令和结果。
- 标准五条命令：逐条回填，不写模糊的“全部通过”。
- 浏览器冒烟、PostgreSQL/Alembic、graphify、已知风险和阻塞：如实回填。

#### 非目标

- 不开始 T036 及以后任务，不修改 Trae 分支，不复制或 cherry-pick Trae 实现。
- 不修改共享规格来固化 Codex 专属实现选择；发现共同歧义时按双 Agent 协议暂停并上报。
- 不创建生产部署、照片、对象存储或未来业务模块。

## 3. Trae 实现子 Issue 草稿

### 标题

`M2：Trae 认证、授权与身份审计实现`

### 正文

#### 关联与边界

- 父 Issue：[#4](https://github.com/ywyz/child-manager/issues/4)。
- 目标分支：`trae`。
- 共同基线：docs-only 内容已发布到 `main`；获得分支同步授权后按届时 `main` HEAD 回填，且
  必须与 Codex 子 Issue 完全相同。
- 当前状态：`pending`；Issue 创建不等于实现授权。
- 远端 `main` 已发布新的 T021～T035 章节；共享基线同步和实现分别获得授权前不得开始 T021。
- 只记录 Trae 自己的方案、提交、迁移、验证、风险和阻塞，不复制或引用 Codex 实现证据。

#### T021～T035 有序执行清单

- [ ] T021：先写标识规范化、可信客户端地址、密码、令牌和登录限流 RED 单元测试。
- [ ] T022：先写身份/审计迁移、同园唯一、组合外键、最后管理员、Refresh family 事务和跨园
  隔离 RED 测试。
- [ ] T023：先写 Auth/Users、Cookie/CSRF、错误和分页 RED 契约测试。
- [ ] T024：先写初始化 CLI、登录/刷新/退出/改密、账号管理、会话撤销和 CSRF RED API 测试。
- [ ] T025：先写登录、账号管理、按角色导航、停用后失权和伪造来源头无效的 RED Web 冒烟。
- [ ] T026：引入冻结版本和哈希的 SecLists 弱密码资源及 MIT 来源说明，不运行真实网络测试。
- [ ] T027：实现 Auth/Users 身份契约及身份操作所需的早期审计事件代码。
- [ ] T028：实现身份/审计模型、迁移和幂等 `admin/teacher` 角色种子。
- [ ] T029：实现标识、密码、Access/Refresh token 和签名双提交 CSRF。
- [ ] T030：实现只信任显式回环 BFF peer 的客户端地址解析、Redis 登录限流和确定性替身。
- [ ] T031：实现同园 Repository、实时授权、最后管理员、会话撤销和身份白名单审计。
- [ ] T032：实现密码不回显、单事务且重复运行安全的 `init-admin` 交互 CLI。
- [ ] T033：接入可信会话、CSRF、登录限流和 Auth/Users API，正确追加独立 Cookie headers。
- [ ] T034：实现中文登录/改密/账号管理 Web 流程、按角色导航和可信 BFF 转发。
- [ ] T035：完成 M2 独立验收、五条标准质量命令和 graphify 更新。

逐项文件、断言和命令以
[T021～T035 权威清单](../../specs/001-daily-activity-plan/tasks.md#m2认证授权与身份审计)
为准；本摘要不得覆盖或弱化 Tasks。

#### 实施与验证原则

1. T021～T025 必须先达到 `collect-only` 成功且 `failed>0, errors=0` 的有效 RED，再开始配对实现。
2. 只实现使当前任务转绿的最小行为；M2 不创建 M3 设置模型、迁移、端点或页面。
3. 每次先运行任务相关快速测试；T035 再运行完整专项矩阵与五条标准质量命令。
4. PostgreSQL、Alembic、Cookie raw headers、CSRF、跨园、撤权、重放和浏览器流程必须有实际
   证据，不能用 SQLite、页面隐藏或另一分支结果替代。
5. 常规测试禁用真实网络；弱密码资源仅按 T026 的冻结版本、来源、哈希和尺寸验收。

#### 验收证据

- 分支 HEAD、共同基线和实际提交：完成后逐项回填。
- RED 证据：逐项回填收集命令、失败断言和 `errors=0`。
- GREEN 与专项测试：逐项回填实际命令和结果。
- 标准五条命令：逐条回填，不写模糊的“全部通过”。
- 浏览器冒烟、PostgreSQL/Alembic、graphify、已知风险和阻塞：如实回填。

#### 非目标

- 不开始 T036 及以后任务，不修改 Codex 分支，不复制或 cherry-pick Codex 实现。
- 不修改共享规格来固化 Trae 专属实现选择；发现共同歧义时按双 Agent 协议暂停并上报。
- 不创建生产部署、照片、对象存储或未来业务模块。

## 4. 草稿只读复核清单

- [x] 父 Issue 与两个实现子 Issue 均只覆盖 M2 T021～T035，没有混入 M3 设置任务。
- [x] 父 Issue 只描述共同目标、入口、出口、事实来源和非目标，不包含实现专属方案。
- [x] Codex、Trae 子 Issue 的任务、TDD、验证和非目标对称，且各自独立记录证据。
- [x] 账号管理 Web 流程属于 M2；学期、班级、区域与工作日设置明确留在 M3。
- [x] Cookie、CSRF、来源、限流、Refresh 重放、最后管理员、园所隔离和身份审计均有门禁。
- [x] 共同基线没有提前写成旧 HEAD；Issue 创建、分支同步和实现授权保持分离。
- [x] 文档链接、任务编号、Markdown 格式和 docs-only 文件范围验证通过。
