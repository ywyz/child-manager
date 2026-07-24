# Phase 0 研究：首期一日活动计划完整闭环

**Feature**: `001-daily-activity-plan`
**Date**: 2026-07-12
**Updated**: 2026-07-22
**Status**: 研究决策已收敛；M1 `complete`；M2 `in_progress`，由 `dev` 按 #4 单实现验收

## 1. 研究方法与决策优先级

本研究同时核对 `AGENTS.md`、`README.md`、经确认的 `docs/`、Word 模板及说明、
`graphify-out/graph.json`、旧仓库固定提交中的提示词，以及本轮逐项确认的答案。旧仓库只
提供教学措辞参考，不提供本项目需求或架构事实。

当共享文档仍保留旧表述，而本轮已经针对同一问题给出明确答案时，本 feature 采用本轮
答案，并把共享文档同步列为实现前门禁；这不等同于本轮擅自修改共享文档。生产部署、
访问网络、生产密钥托管和恢复拓扑继续由 ADR-0009 延后。

## 2. Feature 与架构

### 2.1 首期使用一套 Spec Kit 文档

- **Decision**: M1–M8 作为一个 feature，共用一套 `spec.md`、`plan.md` 和 `tasks.md`；
  M9 生产部署复审不在本 feature 内。
- **Rationale**: 首期价值是“设置 → 手工教案 → AI 辅助 → 教师采用 → Word 导出 →
  审计与验收”的完整闭环，各里程碑共享认证、园所隔离、任务与数据不变量。
- **Alternatives considered**: 只规划 M1 无法交付业务价值；每个里程碑各建一套规格会
  重复跨阶段约束并放大漂移。

### 2.2 独立运行单元与模块化单体

- **Decision**: 保持 NiceGUI Web、FastAPI API、Dramatiq Worker 三个独立进程；稳定
  请求、响应、事件和枚举放入 `packages/contracts`，领域、应用、Repository 与集成代码
  放入 `packages/backend`。Web 只调用 `/api/v1`，不得导入 ORM 或连接数据库。
- **Rationale**: 这与 ADR-0002、现有架构和 `AGENTS.md` 一致，既保持进程故障隔离，也
  避免首期拆成多个业务微服务。
- **Alternatives considered**: 单进程会模糊权限与长任务边界；业务微服务会引入首期不
  需要的分布式事务和部署复杂度。

### 2.3 技术基线与依赖

- **Decision**: Python 3.14+、NiceGUI 3.x、FastAPI、Pydantic 2、SQLAlchemy 2、
  Alembic、Psycopg 3、Dramatiq 2 + Redis、HTTPX、PyJWT、webauthn 3.x、cryptography、
  python-docx 和 chinesecalendar；`uv` 管理 `pyproject.toml` 与 `uv.lock`。生产数据使用
  PostgreSQL，SQLite 仅限确定性的单元/开发测试且业务代码不得依赖其特性。
- **Rationale**: 这些依赖直接对应已确认的 UI、API、数据、任务、认证、加密、Word 和
  本地工作日边界。2026-07-12 查询 PyPI 时，核心框架均有可用的 Python 3.14 发行信息；
  python-docx 1.2.0 与 chinesecalendar 1.11.0 虽未声明 3.14 classifier，但已在隔离的
  Python 3.14 环境完成导入和最小功能冒烟。
- **Alternatives considered**: 不增加第二套依赖清单；不采用 Celery、同步长请求、
  `create_all()` 或生产 SQLite。依赖的准确版本由 M1 写入 `uv.lock`，锁定前再次检查许可
  与 Python 3.14 兼容性。
- **Primary references**: [NiceGUI](https://pypi.org/project/nicegui/)、
  [FastAPI](https://pypi.org/project/fastapi/)、
  [SQLAlchemy](https://pypi.org/project/SQLAlchemy/)、
  [Psycopg](https://pypi.org/project/psycopg/)、
  [Pydantic](https://pypi.org/project/pydantic/)、
  [Alembic](https://pypi.org/project/alembic/)、
  [Dramatiq](https://pypi.org/project/dramatiq/)、
  [python-docx](https://pypi.org/project/python-docx/)、
  [chinesecalendar](https://pypi.org/project/chinesecalendar/)。

## 3. 教案、日期与权限

### 3.1 当前学期和学期外日期

- **Decision**: 创建教案前必须存在当前学期；教案保存该学期引用和展示快照。活动日期
  在学期外时，`teaching_week_number` 与 `teaching_week_text` 同时为空，页面软提示，
  保存、AI 与经用户确认的导出继续；Word 周次单元格留空。
- **Rationale**: 保留稳定的学期展示上下文，同时不伪造学期外周次。
- **Alternatives considered**: 无当前学期也创建会失去 Word 上下文；继续外推周次会产生
  不真实数据；硬阻止学期外日期违背软降级规则。

### 3.2 区域按目标栏目校验

- **Decision**: 班级允许室内或户外区域不完整。室内、户外 AI 请求只校验各自类别至少
  一个启用区域；缺少哪类只阻止对应栏目，手工编辑和其他 AI 栏目继续。
- **Rationale**: 区域是特定 AI 栏目的输入，不是班级或手工教案的全局门禁。
- **Alternatives considered**: 保存班级时强制两类齐全；任一类别缺失时禁用全部 AI。

### 3.3 作者署名与当前授权分离

- **Decision**: `class_teachers` 是教师班级访问的当前事实来源。解除关联立即撤权；既有
  当前教案和历史保留作者姓名快照。署名不授予权限，解绑后不能新选该教师为作者，但可
  保留或显式移除已有署名。
- **Rationale**: 当前授权必须可立即收回，历史展示又不能因人员变动丢失。
- **Alternatives considered**: 因署名阻止解绑会妨碍账号治理；自动删除署名会破坏追溯；
  以署名反推权限会形成越权。

### 3.4 快照只表达可恢复内容变化

- **Decision**: 手动保存、归档、恢复归档、历史恢复，以及教师明确采用 AI 结果时创建
  教案快照；自动保存、AI 生成、重新生成、自动或显式重试、失败、拒绝均不创建快照。
  后者由任务、AI 结果和审计事件追踪。
- **Rationale**: 未采用预览时正文没有变化，创建相同内容快照会混淆恢复历史和操作日志。
- **Alternatives considered**: 生成时和采用时都创建会产生重复快照；只在生成时创建无法
  表达真正写入正文的时点。

## 4. AI 提示词、结果与教师控制

### 4.1 七个稳定提示词及来源

- **Decision**: 稳定标识为：
  `daily_activity_plan.morning_activity`、
  `daily_activity_plan.morning_talk`、
  `daily_activity_plan.group_activity_split`、
  `daily_activity_plan.group_activity_add_step`、
  `daily_activity_plan.indoor_area_game`、
  `daily_activity_plan.afternoon_outdoor_game`、
  `daily_activity_plan.daily_reflection`。旧仓库仅作措辞参考，正文必须按当前变量白名单、
  固定 Schema、隐私规则和 Word 格式重写。七份 v1 默认提示词必须先冻结为可导入、可哈希
  的只读资源，再编写 `0004` 种子迁移；迁移复制该冻结版本，不得在以后升级时动态读取可变
  的运行时草稿或最新 catalog。
- **Rationale**: 稳定命名空间支持版本、任务、审计与回滚；重写可保留教学经验而不继承
  旧架构、旧变量或自由文本解析。
- **Alternatives considered**: 直接复制旧提示词会引入旧字段与隐式规则；完全延后正文会
  让首次安装没有七个默认提示词。
- **Reference snapshot**: 旧仓库固定提交
  [`225fe139`](https://github.com/ywyz/kindergartenManager/commit/225fe139d5541539f2be4d0d41ef00061989533d)：
  晨间、晨谈、室内、户外、反思参考
  [`generate_client.py`](https://github.com/ywyz/kindergartenManager/blob/225fe139d5541539f2be4d0d41ef00061989533d/app/integration/ai_client/generate_client.py)，
  拆分参考
  [`lesson_plan_client.py`](https://github.com/ywyz/kindergartenManager/blob/225fe139d5541539f2be4d0d41ef00061989533d/app/integration/ai_client/lesson_plan_client.py)，
  新增环节参考
  [`adapt_client.py`](https://github.com/ywyz/kindergartenManager/blob/225fe139d5541539f2be4d0d41ef00061989533d/app/integration/ai_client/adapt_client.py)。

### 4.2 逐任务最小变量白名单

- **Decision**:
  - 晨间活动、晨间谈话：`plan_date`、`weekday_text`、`teaching_week_text`、`season`、
    `class_name`、`age_group_name`、`teacher_context`。
  - 集体活动拆分：`source_text`、`age_group_name`、`teacher_context`。
  - 集体活动新增环节：`group_activity`、`age_group_name`、`teacher_context`。
  - 室内区域：晨间公共变量加 `indoor_areas`。
  - 下午户外：晨间公共变量加 `outdoor_areas`。
  - 反思：`plan_date`、`class_name`、`age_group_name`、`current_plan`。
  `teacher_context` 只含教师主动填写的教学上下文，不含账号或身份；学期外
  `teaching_week_text` 可空。
- **Rationale**: 每项任务只向外部 AI 发送完成当前任务所需数据。
- **Alternatives considered**: 共享全量上下文扩大隐私和耦合面；管理员自由增加变量会
  绕过契约审查。

### 4.2.1 占位符与确定性渲染

- **Decision**: 提示词模板只识别词法 `\{\{[ \t]*([a-z][a-z0-9_]*)[ \t]*\}\}`：花括号内
  只允许零个或多个 U+0020 空格/U+0009 水平 Tab，不接受换行或其他 Unicode 空白；标识符
  必须匹配 `[a-z][a-z0-9_]*`。解析器只做一次白名单纯替换，不支持表达式、
  过滤器、循环、函数、条件、包含文件或 `a.b`/`a[0]` 等嵌套访问；变量值中即使出现
  `{{...}}` 也保持原文，不递归渲染。字符串按原文插入，空值渲染为空字符串，数字和布尔值
  使用 JSON 标量表示；数组保持顺序，对象按 key 排序，均使用 UTF-8、`ensure_ascii=false`、
  无无意义空白的稳定 JSON。保存/发布时拒绝未知、非法或未闭合占位符；执行时缺少已引用
  变量则任务在外呼前失败。
- **Rationale**: 这套语法足以承载七个固定任务，同时避免引入可执行模板语言、服务端对象
  遍历和因序列化漂移造成的输入哈希不稳定。
- **Alternatives considered**: Jinja2 表达式/过滤器；Mustache 区块与循环；允许嵌套访问；
  对变量值二次渲染；数组和对象使用不稳定的 Python `repr`。

### 4.3 固定结构化结果

- **Decision**: 代码和版本化契约拥有结果 Schema，管理员只能编辑提示词正文。晨间、
  室内和户外的 AI 结果必须各恰好包含 3 个非空且以中文 `。` 结束的陈述，晨谈必须恰好
  包含 3 个非空且以中文 `？` 结束的问题。区域游戏 AI 结果不得回传 `areas`；
  `focus_guidance` 必须等于生成输入中一个已启用区域名称，采用时 API 从已经通过输入哈希
  校验的区域快照写入 `areas`，不得允许 AI 伪造或改写区域。集体拆分的主题、目标、准备、
  重点、难点及每个活动过程字段必须非空，拆分结果不得提交 `is_ai_added`，API 采用时统一
  将拆分步骤置为 `false`。集体新增任务只返回一个非空 `step` 与
  `suggested_insert_index`，且 `0 <= index <= len(生成输入中的 group_activity.process)`；
  越界是结果结构错误并进入统一的最多两次自动重试，不得静默 clamp。API 合并后设置
  `is_ai_added=true`。反思固定为三个均非空的
  `highlights`、`issues`、`adjustments`；校验时三个值分别 Unicode NFKC 规范化后直接拼接，
  按 Unicode 码点计数，字段名和导出换行不计、值内空格及标点计入，总数不超过 200，Word
  按三行输出。该规则同时用于 AI 结构校验、采用与手工保存，避免入口间计数不一致。
- **Rationale**: 固定 Schema 才能稳定校验、保存、恢复和映射 Word；增量返回可避免 AI
  重写教师已经确认的完整集体活动。
- **Alternatives considered**: 让 AI 复用容许手工渐进编辑的宽松 Schema；提示词自定义
  Schema；新增任务返回整个集体活动；允许 AI 自行提交新增标记；反思用单段自由文本。

### 4.4 一键生成、反思与集体活动部分成功

- **Decision**: 一键生成恰好创建晨间活动、晨间谈话、室内区域游戏、下午户外游戏四个
  独立子任务，不含集体活动或反思。晨间、晨谈、集体、室内、户外五栏按固定 Schema
  完整并保存后，教师才可显式点击生成反思；未点击不建任务。集体拆分成功后先提示教师
  采用拆分；拆分采用并保存后才可创建新增环节任务。新增失败不改变已采用拆分，之后只需
  重新生成、预览和采用新增环节。五栏完整只依据当前正文
  满足固定 Schema，不要求内容来自 AI，也不要求集体活动已含 `is_ai_added` 环节；缺少该
  环节只显示提示。点击生成反思时，API 先按客户端当前 `expected_version` 保存页面修改；
  保存、完整性校验和任务插入在同一数据库事务中，保存采用无快照的当前内容更新语义；
  只有事务成功才返回任务，保存失败/冲突或任务插入失败都不得留下半完成状态。反思任务的
  `current_plan` 只包含五个上游栏目及必要展示上下文，不包含当前旧反思。
  除反思这一单事务预保存例外外，一键和其他单栏 AI 点击时 Web 必须先用当前
  `expected_version` 完成一次无快照 autosave；保存失败或 409 时不得发送生成请求。生成
  API 不接收整份未保存正文，只校验 autosave 返回的最新 `expected_version` 后创建任务。
- **Rationale**: 反思依赖完整且已保存的事实；栏目和集体两步分别保留成功结果与教师
  决定权。
- **Alternatives considered**: 一键提前生成反思；非反思生成直接携带页面未保存全文；存在
  未保存修改时禁用按钮并要求教师另行
  手动保存；把 AI 新增环节作为反思硬门禁；集体两步必须原子成功；失败时丢弃可用拆分
  结果；把旧反思一并发给模型让其基于旧答案改写。

### 4.5 栏目级预览有效性与采用并发

- **Decision**: 每个预览记录目标栏目的基线哈希与本次实际输入哈希。只有目标栏目或
  实际输入变化才使其失效；无关栏目编辑或采用不影响。采用请求仍携带客户端当前
  `expected_version`，API 在一个事务中重新鉴权、执行乐观锁并复核两个哈希；若仅全局
  版本冲突，刷新最新版本后仍可采用尚有效的预览。
  `teacher_context` 是创建该任务时保存的瞬时不可变输入快照，不是教案当前字段；采用重算
  输入哈希时复用任务内该快照，只重读日期/周次/班级/年龄段/区域/相关正文等可变服务端
  输入。页面随后为“新生成”修改 teacher context 不追溯使旧预览失效；要让新 context 生效
  必须重新生成。采用请求体因此只需最新 `expected_version`，不接收 teacher context。
  创建 AI 任务的受理事务必须同时插入唯一的 pending `ai_generation_results` placeholder，
  保存目标栏目基线、不可变 `input_context/input_sha256`、模型、提示词版本和结果 Schema，
  output 暂为空。Worker 只读取该冻结输入并幂等填入 output，不得因 Redis 延迟而重读后来
  变化的 plan/settings；采用时仍按前述规则重读当前可变服务端输入判断 stale。
- **Rationale**: 一键生成的四个结果独立；只比较生成时全局版本会让采用第一个结果后
  其余结果全部误失效。
- **Alternatives considered**: 整批采用；任一版本变化全部失效；采用一个后主动废弃其他
  结果。

## 5. 异步任务与外部 AI

### 5.1 PostgreSQL 权威任务和可靠投递

- **Decision**: API 在数据库事务中保存 `pending_dispatch` 后即视为请求已受理，目标在
  2 秒内返回任务 ID 与“等待投递”；Redis 暂不可用不回滚任务，也不得在数据库提交后改回
  503。提交前 PostgreSQL 不可用使用 `database.unavailable`，创建任务所必需的服务端本地
  配置缺失或无效使用 `configuration.unavailable`。整体 ready 只把 PostgreSQL 和所有核心请求
  共同依赖的 JWT/CSRF 等全局安全配置视为 503 条件；模型、模板、导出存储、日历和 Redis 等
  功能专属边界只报告 degraded，实际依赖端点可在受理前返回
  `configuration.unavailable`。15 秒扫描待投递任务，恢复后自动投递；Redis 只携带 `job_id`。
- **Rationale**: 数据库是业务意图和任务状态唯一权威，避免故障时返回失败诱发重复点击。
- **Alternatives considered**: Redis 失败时不存任务会丢失意图；已存任务却返回失败会造成
  重复任务。

### 5.2 租约、并发与重试

- **Decision**: DB 租约 120 秒，业务心跳 30 秒，过期租约扫描 30 秒；首期 Worker 4
  线程；每模型档案默认并发 2 且可配置。AI HTTP 连接超时 10 秒、读取超时 120 秒；可重试
  错误最多再试两次，约 5 秒和 30 秒抖动退避；429 优先遵循 `Retry-After`，单次最多等待
  60 秒；业务模型调用总数最多 3。
  Worker 每次真正发出 AI 或提示词测试外部请求前，必须按 `requested_by` 重验账号启用、
  当前角色/班级关系、教案未归档，以及模型档案仍启用、密钥完整且能力可用。任一权限或
  配置已撤销时以不可重试失败结束，外部调用数为 0；预览采用事务仍再次实时鉴权。
- **Rationale**: 心跳可在租约内多次续约，恢复时间和首期 100 个排队任务规模相称；抖动
  避免集中重试，调用计数由 PostgreSQL 保证不因消息重投突破上限。
- **Alternatives considered**: 更短租约容易误抢长响应；更高默认并发会无控制压迫供应商；
  更长超时会延迟确定故障反馈。
- **Primary reference**: [Dramatiq Guide](https://dramatiq.io/guide.html) 与
  [Dramatiq Reference](https://dramatiq.io/reference.html)。

### 5.3 提示词测试同样异步执行

- **Decision**: 管理员测试提示词也创建 PostgreSQL 权威后台任务；API 返回 `202`、任务 ID
  与 `pending_dispatch`，页面使用与正式生成相同的轮询/恢复机制。受理事务先按路径提示词代码
  对固定输入 Schema 校验 variables，再把规范化后的不可变 `input_context`/SHA-256、提示词
  正文/哈希、结果 Schema，以及模型档案 ID、冻结 API 地址、模型名、能力和单调
  `call_config_revision` 等非密钥调用配置与 run/job 一起保存；不复制 API Key 或密文。
  地址、模型名、能力或密钥变化必须在同一事务递增档案 revision。Worker 只按 `job_id` 读取该权威上下文，Redis、
  日志和审计均不携带完整变量/提示词/模型地址；公开 `input_summary` 只列已提供变量名和
  `all_values_redacted=true`。外呼前 Worker 先比较当前与冻结 revision；不一致时以
  `prompt.configuration_changed` 零调用失败，管理员须重新发起测试。只有 revision 一致时才
  读取当前档案密钥，并实时重验请求人权限、模型启用和当前地址是否符合 URL 安全策略，
  从而禁止新密钥与旧冻结地址混用。结果写入 `prompt_test_runs`，不进入教案；每个
  提示词只保留最近 20 条。创建顺序
  固定为先检查幂等命中；只有新 key 才锁定 prompt definition、按时间删除最旧已完成记录并
  插入 run/job，pending/running 记录不得被清理。若 20 条均未完成，返回 409
  `prompt.too_many_active_tests`，且不得创建 job 或 run。完成 run 被清理后保留原 job 作为幂等
  锚点；同 key/摘要重放返回原 job 且关联运行可为空，不得重新创建或再次调用模型。
- **Rationale**: 单次模型读取可能达到 120 秒且可能重试；同步占用 API 请求会违反“AI 等
  长任务由 Worker 执行”的服务边界，也难以在页面刷新、Redis 故障和重复点击时可靠恢复。
- **Alternatives considered**: 管理端同步等待最多 120 秒；为提示词测试另建一套短任务机制。
  前者阻塞 API，后者重复现有幂等、租约和审计能力。

### 5.4 任务身份、父任务聚合与显式重试

- **Decision**: 一键生成在单一事务创建 `job_type=ai.batch` 的非执行父任务及晨间、晨谈、
  室内、户外四个子任务；只有子任务投递和调用模型。父任务数据库中的
  `execution_status/attempt_count/max_attempts`、租约和执行时间均为 NULL，API 投影时将两个
  attempt 字段固定显示为 0，并从子任务派生 status。只有执行型 AI 的 `max_attempts=3`。API 每次
  从恰好四个子任务派生展示状态：任一子任务仍运行时按
  `running > retrying > queued > pending_dispatch` 展示；全部进入模型执行完成集合且至少一项
  产生非失败结果时为 `succeeded`，混有失败则 `has_partial_failure=true`；全部失败才为
  `failed`。用户显式重试只接受存在 AI 结果且最终失败的执行型 AI 栏目任务；`ai.batch`、
  `prompt.test`、`word.export` 及非 failed 任务均拒绝。重试使用新 `Idempotency-Key` 创建新的
  根任务和 pending 结果，以 `retry_of_job_id` 关联原失败任务，并从原结果精确复制栏目基线、
  实际输入、模型、提示词与结果 Schema；不得按重试时 current plan/settings 重建。若要使用
  新输入，必须走普通新生成。`parent_job_id`、`retry_of_job_id`、任务结果、提示词
  测试和导出记录到任务的关系都必须使用 `(kindergarten_id, id)` 组合外键，禁止跨园谱系。
  由客户端直接受理的根任务（含 `ai.batch` 父任务）的 `idempotency_scope`、
  `idempotency_key`、`request_fingerprint_sha256` 三项必须全非空；`ai.batch` 的四个内部子任务
  没有独立客户端 key，三项必须全空，并用
  `(kindergarten_id, parent_job_id, target_section)` 部分唯一约束防止重复栏目子任务。数据库
  CHECK 禁止三项只填一部分。
- **Rationale**: 父任务只负责可恢复聚合，子任务保持独立成功；新任务表达用户的新意图，
  谱系和组合外键同时提供追踪与园所隔离。
- **Alternatives considered**: 把 `ai.batch` 当作第五个模型任务；父任务复制四份正文；失败
  任务原地回退到 queued；只用 UUID 外键后在业务层检查园所。

## 6. 认证、会话与密钥安全

### 6.1 WebAuthn 依赖、Ceremony 与兼容边界

- **Decision**: 服务端采用 `webauthn` 3.x（Duo Labs `py_webauthn`，BSD-3-Clause）完成选项
  生成和响应验证；实现 Issue 必须在 `uv.lock` 锁定具体版本并执行 Python 3.14 冒烟。注册
  使用可发现凭据、`residentKey=required`、`userVerification=required`、attestation `none`；
  认证不先提交用户名，`allowCredentials` 为空或省略，由 Credential ID/user handle 识别账号，
  同样要求 UV。浏览器与 API 之间所有 ArrayBuffer 使用无填充 Base64URL JSON。
  challenge 由服务端随机生成 32 字节，最长 5 分钟、单次使用，保存摘要并绑定 purpose、
  RP ID、精确 Origin、园所、账号或授权上下文。完成时验证 type、challenge、Origin、
  RP ID hash、UP/UV、签名、Credential ID、user handle 和账号状态；不同 purpose 不可互换。
- **Rationale**: W3C WebAuthn 要求可信 RP 生成不可预测 challenge 并匹配返回值；可发现凭据
  避免登录前账号枚举。成熟服务端库减少自写 CBOR/COSE/签名验证的安全风险，其 3.0.0 wheel
  由 CPython 3.14 构建且声明 Python >=3.10，但项目仍需按自身 3.14 锁定环境验证。
- **Alternatives considered**: 自行解析 CBOR/COSE；要求用户名后返回 `allowCredentials`；
  `userVerification=preferred`；以密码单因素兼容不支持 WebAuthn 的浏览器。前两项增加实现/
  枚举风险；后两项违反 ADR-0010/0011。M3A 的密码+TOTP 是已激活用户设备切换路径，不降低
  WebAuthn ceremony 要求。
- **Primary references**: [W3C Web Authentication Level 3](https://www.w3.org/TR/webauthn-3/)、
  [PyPI webauthn](https://pypi.org/project/webauthn/)。

### 6.2 初始化、邀请、凭据与恢复

- **Decision**: 空系统 CLI 只在事务中创建园所、角色和 `pending_registration` 首位管理员，
  再生成至少 128 位随机熵、15 分钟过期的单次初始化凭据；CLI 分开显示 HTTPS 入口和原始
  凭据，不生成通行密钥、不把秘密放入 URL。浏览器完成注册后账号仍是
  `pending_verification`，园所负责人和部署责任人两项带外核验后才激活。
  后续账号邀请最长 24 小时、可撤销、重签即撤销旧邀请，注册凭据与消费邀请同事务但不创建
  会话。本人增加/命名/撤销凭据、主动轮换恢复码和高风险管理操作要求 5 分钟内 WebAuthn
  step-up；本人不能撤销最后凭据。管理员可撤销教师最后凭据、全部会话并重新邀请。
  激活后的首次成功通行密钥认证向用户签发首个离线恢复码；此后每个 active 账号只有一个
  有效恢复码，管理员和 CLI 不接触原始码。紧急恢复请求同时要求恢复码和人工核验；普通账号
  由有效管理员通过 Web/API 审批。最后管理员 Web/API 审批返回
  `409 identity.last_admin_recovery_requires_cli`，部署控制台只能用
  `init-admin recover-last-admin --recovery-request-id <uuid>` 交互匹配初始化时预登记的园所
  负责人和独立运维/安全责任人，在单一事务中写入两项不可变批准并签发 15 分钟单次浏览器
  登记凭据；CLI 不接收恢复码、credential JSON 或预登记引用参数。恢复登记成功后原子撤销
  旧密码/TOTP、通行密钥、会话、邀请和恢复码，签发新码但不创建登录会话。
- **Rationale**: 初始化、邀请或恢复的单一秘密泄露都不能直接产生业务会话；CLI 只建立
  短时授权而不越过浏览器/认证器的 WebAuthn 安全边界。恢复后强制重新登录避免恢复登记
  能力升级为长期会话。
- **Alternatives considered**: CLI 直接写入凭据；公开 Web 初始化；邀请注册即激活；恢复码
  单独登录；管理员设置临时密码；万能恢复码或数据库改值。全部违反 ADR-0010 的双条件和
  无后门边界。
- **Primary references**: [ADR-0010](../../docs/ADR/ADR-0010-restricted-public-entry-passkey-authentication-and-recovery.md)、
  [首期安全威胁模型](../../docs/security/threat-model.md)。

### 6.3 Access/Refresh Token 与 CSRF

- **Decision**: Access Token 是 15 分钟 HS256 JWT，签名密钥为数据库外随机 256 位值，
  claims 仅 `iss/aud/sub/jti/sid/iat/nbf/exp/kindergarten_id`；`sid` 绑定 Refresh Token family，
  角色、班级、账号和 family 撤销状态每次由服务端查询。Refresh Token 为随机 256 位不透明值，
  只保存强哈希，绝对有效期 7 天，每次刷新轮换；退出、本人/管理员会话撤销、停用、最后凭据
  撤销、恢复或重放撤销相应 family，重放撤销整个 family。认证 Cookie 使用 Secure、HttpOnly、
  SameSite=Lax；状态变更同时校验 Origin/Referer，并使用签名双提交 CSRF Cookie 与
  `X-CSRF-Token`。只有显式开发配置且绑定回环地址时可将 Secure 设为 false。认证完成和刷新
  family 持久化认证方法、备用因素版本及最近 WebAuthn/备用验证时间，API 以此区分普通业务和
  高风险身份授权。认证完成和刷新必须各发送两条独立 `Set-Cookie` 字段，退出/当前会话撤销必须发送两条独立过期字段；BFF
  与 raw-header 契约测试不得用逗号折叠它们。
- **Rationale**: WebAuthn 证明用户控制凭据，但不替代服务端可撤销会话。`sid` 实时检查让
  管理员撤销或恢复后的旧 Access Token 在下一请求失效；Refresh 轮换可检测重放。
- **Alternatives considered**: 把角色写入长寿命 JWT；只等待 15 分钟 Access 过期；保存明文
  Refresh Token；只依赖 SameSite；在非回环开发地址关闭 Secure。
- **Primary references**: [RFC 9700 OAuth 2.0 Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html)、
  [OWASP REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)、
  [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)。

### 6.4 旧密码数据迁移与不可逆回滚边界

- **Decision**: 身份迁移分 expand/enroll/contract。Expand 新增账号状态和 WebAuthn/邀请/
  恢复表，应用同时删除密码登录、改密和重置路由，停止读写旧密码列并撤销全部旧 Refresh
  family；原 active 账号转 `pending_registration`。Enroll 只在没有 WebAuthn active 管理员的
  迁移窗口允许本机 CLI 为一个既有管理员签发 `migration_admin` 短时登记凭据。Contract 在
  密码路由不存在、所需账号完成登记和旧字段零读写门禁后删除 `password_hash`、
  `password_changed_at`、`is_active`。Contract downgrade 只重建空列，不能恢复秘密或密码
  登录；历史数据回退使用迁移前停机备份，恢复后仍重新执行 WebAuthn 迁移。
- **Rationale**: 直接先删密码列会让现有管理员无法完成通行密钥登记；把旧密码登录保留到
  全员迁移又会违反 ADR 并留下隐藏兼容路径。分阶段迁移允许恢复结构问题，但明确密码秘密
  删除后不可逆。
- **Alternatives considered**: 一次性 drop 并手工改库；无限期保留只读哈希；contract downgrade
  重新启用旧应用。前两项形成锁死或残留风险，后一项重新引入已废止认证路径。

### 6.5 密码与 TOTP 双因素备用登录

- **Decision**: M3A 在 M3 后、M4 前增加必须同时验证密码与 TOTP 的独立备用登录。管理员
  强制配置，教师可选；成功建立普通业务会话。密码使用 8–128 Unicode 字符、Argon2id、
  本地阻断列表且不设组合/周期轮换规则。TOTP 使用每账号唯一 160 位种子、HMAC-SHA-1、
  6 位/30 秒和相邻一个时间步容差，以 PostgreSQL 原子 `last_accepted_counter` 拒绝重放。
  种子以 AES-256-GCM 加密、随机 96 位 nonce，AAD 绑定园所/用户/凭据/版本。备用会话最近
  五分钟再次验证两项因素后只可新增通行密钥；因素维护要求 WebAuthn。所有通行密钥不可用
  时继续离线恢复码加人工核验。
- **Rationale**: 用户设备切换不应每次启动人工紧急恢复；两项共同验证比任一单因素更强。
  但密码和 TOTP 均不具备钓鱼抗性，因此只能以认证保证级别限制身份操作，WebAuthn 仍为首选。
- **Migration**: M2 contract 删除旧 `users` 密码列的历史不回滚；M3A 在独立表引入新摘要。
  `0005_password_totp_backup_login` 继承 `0004_settings`，尚未实施的下游迁移顺延一位。
- **Alternatives considered**: 密码单独、TOTP 单独、短信/邮件、备用会话只补建通行密钥、
  备用会话管理全部身份材料、管理员代重置。均与已确认的可用性或恢复安全边界冲突。
- **Primary references**:
  [`specs/002-password-totp-backup-login/research.md`](../002-password-totp-backup-login/research.md)、
  [ADR-0011](../../docs/ADR/ADR-0011-password-totp-backup-login.md)、[RFC 6238](https://www.rfc-editor.org/rfc/rfc6238.html)、
  [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html)。

### 6.6 AI Key envelope 与模型地址 SSRF

- **Decision**: API Key 使用 AES-256-GCM，每次随机 96 位 nonce，AAD 绑定
  `kindergarten_id/profile_id/envelope_version`；封装保存 version、key_id、nonce、
  ciphertext。轮换时新写入使用当前 Key，旧 Key 暂时只读，后台分批重加密并逐条验证后才
  可移除。轮换批次按稳定游标和幂等记录恢复；单条失败保留旧密文和旧 key 可读状态，整个
  批次未完成或验证数量不一致时禁止停用旧 key。维护 CLI 只接收目标 key id、批量大小、
  dry-run 和断点游标，不接收主密钥；只有完成报告的扫描数、重加密数、验证数和失败数满足
  预期后，维护者才可从数据库外 keyring 移除旧 key。模型 Base URL 默认只允许公网 HTTPS，
  不跟随重定向；阻止 loopback、link-local、
  multicast、云元数据和未授权私网，连接前后验证全部 DNS A/AAAA。私网/本地地址只能由
  服务端 allowlist 显式开启，开发 loopback 同样显式配置。
- **Rationale**: AEAD 同时保护机密性和完整性，AAD 防跨园/跨档案替换；完整地址与 DNS
  校验限制管理员可配置 URL 形成 SSRF。
- **Alternatives considered**: 无 AAD 的通用加密串、Fernet 黑盒封装、允许重定向、只在
  保存时解析一次 DNS。
- **Primary references**: [cryptography AESGCM](https://cryptography.io/en/stable/hazmat/primitives/aead/)、
  [OWASP Cryptographic Storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)、
  [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)。

## 7. API 与 Web 交互契约

### 7.1 版本、分页、错误与幂等

- **Decision**: API 根路径 `/api/v1`。可增长列表使用 `page/page_size`，默认 20、最大 100，
  响应为 `items/page/page_size/total`。`GET /settings/age-groups` 是固定四项枚举，返回完整有序
  非分页集合；`GET /settings/classes/{class_id}/areas/{area_type}` 使用标准分页，`PUT` 对单班
  单类别整体保存成功只返回 204，不返回可能无界的区域集合。错误统一为
  `code/message/request_id/field_errors`；
  `code` 是稳定英文机器码，`message` 是中文，`field_errors` 仅验证错误出现。保存、归档、
  恢复归档、历史恢复、AI 采用携带 `expected_version`；冲突返回 409
  `lesson_plan.version_conflict`。AI 生成、提示词测试、显式重试和 Word 导出必须携带
  `Idempotency-Key`。幂等作用域固定为
  `kindergarten_id + requested_by + HTTP method + normalized route template + key`，不使用易随
  实现改名的 `job_type` 代替方法/路径。请求摘要的 canonical payload 必须包含解析并规范化的
  实际路径参数、有业务语义的查询参数和 canonical JSON 请求体；UUID 使用标准小写文本，
  query 按名称和值稳定排序，JSON 对象按 key 排序且去除无意义空白。相同摘要返回原任务及原
  202 受理语义，不同摘要返回 `409 request.idempotency_conflict`。新的显式重试使用新 key 并
  写同园 `retry_of_job_id`。
- **Rationale**: 资源版本解决并发覆盖，幂等键解决网络重发和重复点击，统一 envelope
  支持 Web 稳定处理及跨服务诊断。
- **Alternatives considered**: 无界列表、端点自定义错误、只靠数据库唯一约束、用同一个
  key 表示用户明确的新重试。

### 7.2 页面信息架构与无障碍

- **Decision**: 角色化侧边栏包含“教案、班级区域、系统设置、审计记录”；系统设置分
  园所、学期、用户与班级、AI 模型、提示词。教案首页提供日历/列表；六栏目在一个纵向
  编辑页，顶部固定班级、日期、提示和保存操作，AI 预览内联在目标栏目，导出历史在教案
  内。核心流程按 WCAG 2.2 AA 可验证设计，覆盖键盘、焦点、标签/错误关联、对比度、非纯
  颜色状态及触控尺寸，但不宣称第三方组件获得整体认证。
- **Rationale**: 单页保留整份教案上下文，适配桌面和平板；可访问性要求转化为可测试的
  交互而不是抽象口号。
- **Alternatives considered**: 多步骤向导割裂上下文；仿 Word 表格直接编辑对响应式和
  无障碍更脆弱；对第三方组件作无法证明的认证承诺。

## 8. 文件、Word 与工作日服务

### 8.1 `.docx` 上传边界

- **Decision**: 压缩文件最大 10 MiB，解压总量最大 50 MiB，ZIP 条目最多 1000，提取文本
  最多 200,000 字符；扩展名、MIME、ZIP 签名和 OOXML 结构必须一致；拒绝宏、外部关系、
  路径穿越和嵌套压缩。流程结束清理临时文件，只长期保存提取文本、清理后原文件名、哈希
  与时间。
- **Rationale**: `.docx` 是 ZIP 容器，必须同时控制压缩前后资源并拒绝主动/外部内容；
  业务只需要教师确认后的文本。
- **Alternatives considered**: 只校验扩展名；保存原附件；无解压上限；接受宏或外部关系。
- **Primary reference**: [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)。

### 8.2 固定 Word 模板

- **Decision**: 基于模板副本生成；实现前后核对原模板 SHA-256
  `72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043`。学期外周次留空，
  反思按三行输出；只有 `is_ai_added=true` 的集体活动环节正文标红。每次导出创建独立记录
  和服务器副本，历史文件缺失不静默重建。教师可见文件名固定为
  `一日活动计划_{清理后班级名}_{YYYY-MM-DD}.docx`：班级名先做 NFKC，将控制字符和
  `/\:*?"<>|` 替换为 `_`、折叠连续 `_`、去掉首尾空格/点/下划线，空结果回退为 `班级`；
  内部存储 key 必须独立且不可由显示名推导路径。
  导出缺失确认集合固定为晨间、晨谈、集体、室内和户外五栏；`daily_reflection` 为空不属于
  缺失且不触发确认，导出仍保留反思三行固定位置并输出空内容。请求在
  `confirm_incomplete=false` 且五栏存在缺失时，必须先无副作用返回
  `409 export.confirmation_required`，不保存正文、不消耗幂等 key、不创建导出或任务。五栏
  完整或用户确认后，在一个事务内以 `expected_version` 做无教案快照的 CAS 保存，并把保存后
  的不可变 `context_snapshot/content_snapshot/content_schema_version/content_sha256` 复制到
  export row，再创建 export job；任一步失败全部回滚。Worker 只读取 export row 的快照，
  不得稍后重读可能已经变化的 current plan。
- **Rationale**: 模板是实际版式事实来源，独立副本和哈希可证明没有覆盖原件或同名历史。
- **Alternatives considered**: 重建模板、直接修改模板原件、把全部 AI 内容标红、丢失历史
  时重新生成并冒充原文件。

### 8.3 工作日超时、缓存与来源

- **Decision**: 本地库仍为第一来源；在线补充固定使用不跟随重定向的 HTTPS
  `https://timor.tech/api/holiday/info/{YYYY-MM-DD}`。响应 `code=0` 且 `type.type` 为 0/3
  映射 `workday`，1/2 映射 `non_workday`；非 0、缺字段、未知枚举、重定向、网络错误或超时
  均作为 online unavailable，不猜测结论。在线连接超时 2 秒、总超时 5 秒；已确认工作/
  非工作日缓存 24 小时；
  `unknown/unavailable` 缓存 5 分钟；本地与在线冲突时本地优先，保存
  `source=combined` 和最小冲突摘要，缓存 1 小时并软提示。两来源均不可用时固定
  `result=unknown/source=unavailable`。
- **Rationale**: 本地优先和短超时保护主流程；不同 TTL 避免放大故障或长期固化不确定
  结果；`unavailable` 不与真正组合结果混淆。
- **Alternatives considered**: 未知来源留空、复用 `combined`、在线失败阻止保存、所有结果
  使用同一长缓存。
- **Primary reference**: [Timor 节假日 API 官方文档](https://timor.tech/api/holiday/)。

### 8.4 故障隔离矩阵

- **Decision**: PostgreSQL 业务读写失败时使用 503 `database.unavailable`；所有核心请求共同
  依赖的全局安全配置缺失时，整体 ready 返回 503 `configuration.unavailable`。模板、导出
  存储、AI、日历或 Redis 等功能专属配置/固定资源失败只使 ready 分项 degraded、整体仍 200，
  但实际依赖端点可在受理前返回 `configuration.unavailable`，且不得声称任务已受理；
  PostgreSQL 已提交后 Redis 失败保持 `202 pending_dispatch`。AI 或 Worker 故障只影响相关
  后台处理，数据库手工创建/保存/归档/恢复和现有可读导出继续；工作日来源故障降级为
  `unknown/unavailable`；模板或渲染失败只影响新导出；导出存储不可用可以影响新导出和实际
  依赖该存储的下载，但不能使教案 API 或其他本地能力整体 unready。每个失败都保留已保存
  正文并返回稳定中文问题类型。
- **Rationale**: “降级可用”必须以真实依赖边界判断，不能承诺在存储本身不可用时仍下载，
  也不能让 Redis 或 AI 故障扩大为整个应用故障。
- **Alternatives considered**: 任一集成失败都返回全局 503；Redis 投递失败把已提交任务改报
  未受理；导出存储失败仍伪称历史下载可用。

## 9. 已完成的共享文档同步

2026-07-13 已获用户授权并完成 docs-only 同步：`AGENTS.md`、`README.md`、`CONTEXT.md`、PRD、系统架构、领域数据模型、PostgreSQL Schema 与 Roadmap 已统一采用本 feature 的已确认规则。同步范围包括 AI 采用时建快照、一键四栏与显式反思、按目标栏目校验区域、`pending_dispatch`、学期外空周次、`unknown/unavailable`、栏目基线和实际输入判定预览、解绑保留署名、模型默认并发 2、前五栏导出缺失确认与白名单纯替换。

这是一次只包含文档的共享基线变更：未增加生产部署、照片/对象存储或后续子系统。具体长期规则以 canonical 文档为准；本节仅保留同步事实，不再复制全部规则。

## 10. 已排除范围

- 不设计生产反向代理、Compose 拓扑、DNS、证书、Tailscale、生产备份或主密钥托管。
- 不实现照片、视觉识别、对象存储、游戏观察、一对一倾听、审批/审核状态或天气标签。
- 不迁移旧仓库代码、数据库或提示词运行协议。
- 不在常规测试中调用真实 AI、在线节假日或其他付费/不稳定网络。
