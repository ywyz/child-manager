# Phase 1 Quickstart：首期实现与验收合同

**Feature**: `001-daily-activity-plan`
**Date**: 2026-07-12
**Current repository state**: `main` 只有文档、模板与 Spec Kit 产物；Codex 分支已完成
T004～T020，可执行锁定安装、本地依赖、迁移及 API、Worker、Web 工程入口。下列命令同时
覆盖 M1～M8 验收合同：超出当前里程碑的业务初始化与用户故事步骤仍不可执行，也不表示
已经通过；Trae 状态只以其分支和 Issue #3 的实时证据为准。

## 1. 前提与反目标

需要 Python 3.14、`uv`、PostgreSQL、Redis 和可用浏览器。测试使用固定 AI、工作日和时间
替身，不访问真实/付费 AI 或在线节假日服务。

本 quickstart 不创建或验收生产 Caddy/Compose 拓扑、DNS、证书、Tailscale、生产密钥
托管、备份或发布流程，也不包含 PDF、照片、OCR、对象存储、审批和后续业务子系统。
`compose.dev.yaml` 若由 M1 创建，只允许启动本地测试 PostgreSQL/Redis，不代表生产拓扑。
Codex 与 Trae 同机并行时必须先按
[`local-development-environments.md`](../../docs/development/local-development-environments.md)
进入各自 worktree 并加载对应档位。下列命令统一引用档位变量，不再假定共享固定端口。

## 2. 锁定安装与本地依赖

```bash
test -n "$COMPOSE_PROJECT_NAME"
test -n "$CHILD_MANAGER_PROFILE"
test -n "$CHILD_MANAGER_WEB_PORT"
test -n "$CHILD_MANAGER_API_PORT"
test -n "$CHILD_MANAGER_POSTGRES_PORT"
test -n "$CHILD_MANAGER_REDIS_PORT"
test -n "$CHILD_MANAGER_DATABASE_NAME"
test -n "$CHILD_MANAGER_TEST_DATABASE_NAME"
test -n "$CHILD_MANAGER_RUNTIME_ROOT"
test -n "$CHILD_MANAGER_POSTGRES_PASSWORD"
umask 077
mkdir -p \
  "$CHILD_MANAGER_RUNTIME_ROOT/exports" \
  "$CHILD_MANAGER_RUNTIME_ROOT/logs" \
  "$CHILD_MANAGER_RUNTIME_ROOT/tmp"
uv sync --locked
docker compose -f compose.dev.yaml up -d --wait postgres redis
docker compose -f compose.dev.yaml ps
docker compose -f compose.dev.yaml port postgres 5432
docker compose -f compose.dev.yaml port redis 6379
if ! docker compose -f compose.dev.yaml exec -T postgres \
  psql -U child_manager -d postgres -tAc \
  "SELECT 1 FROM pg_database WHERE datname = '${CHILD_MANAGER_TEST_DATABASE_NAME}'" \
  | rg -q '^1$'; then
  docker compose -f compose.dev.yaml exec -T postgres \
    createdb -U child_manager "$CHILD_MANAGER_TEST_DATABASE_NAME"
fi
```

预期：锁定安装无变更；PostgreSQL 和 Redis 健康，且只绑定回环地址。若 Docker 不可用，
可以提供等价的现有本地服务，但测试连接必须指向隔离数据库，不能使用生产数据。

仅在当前 shell 创建本地开发密钥，不写 `.env` 或仓库文件：

```bash
export CHILD_MANAGER_ENV=development
export CHILD_MANAGER_BIND_HOST=127.0.0.1
export CHILD_MANAGER_COOKIE_SECURE=false
export CHILD_MANAGER_DATABASE_URL="postgresql+psycopg://child_manager:${CHILD_MANAGER_POSTGRES_PASSWORD}@127.0.0.1:${CHILD_MANAGER_POSTGRES_PORT}/${CHILD_MANAGER_DATABASE_NAME}"
export CHILD_MANAGER_TEST_DATABASE_URL="postgresql+psycopg://child_manager:${CHILD_MANAGER_POSTGRES_PASSWORD}@127.0.0.1:${CHILD_MANAGER_POSTGRES_PORT}/${CHILD_MANAGER_TEST_DATABASE_NAME}"
export CHILD_MANAGER_REDIS_URL="redis://127.0.0.1:${CHILD_MANAGER_REDIS_PORT}/0"
export CHILD_MANAGER_JWT_SIGNING_KEY="$(openssl rand -base64 32)"
export CHILD_MANAGER_CSRF_SIGNING_KEY="$(openssl rand -base64 32)"
```

预期：开发配置只允许回环地址使用 `Secure=false` Cookie。把 API 使用的
`CHILD_MANAGER_BIND_HOST` 或 Web 的 `--host` 参数改为 `0.0.0.0` 或 `::` 时，对应进程必须拒绝启动。

## 3. 数据库与首次初始化

```bash
uv run alembic upgrade head
uv run alembic current
# 以下 init-admin 命令仅在 T034 完成后执行：
uv run python -m packages.backend.bootstrap init-admin
uv run python -m packages.backend.bootstrap init-admin
```

第一次 CLI 应交互询问园所名称、管理员用户名、显示名和密码；密码不回显，也不从命令行
参数或环境变量读取。园所、角色种子、管理员及角色分配在一个事务中完成。第二次运行只
显示“系统已初始化”，不得新增账号或修改原数据。任一步注入失败时数据库保持空初始化状态。

## 4. 启动三个独立进程

在三个终端使用同一档位的本地配置。`CHILD_MANAGER_API_PORT` 只供回环地址上的 Web BFF、
Worker 和诊断测试访问；浏览器唯一入口是 `CHILD_MANAGER_WEB_PORT`，不能直连 API 端口：

```bash
uv run python -m apps.api --host "$CHILD_MANAGER_BIND_HOST" --port "$CHILD_MANAGER_API_PORT"
```

```bash
uv run python -m apps.worker
```

```bash
uv run python -m apps.web --host "$CHILD_MANAGER_BIND_HOST" --port "$CHILD_MANAGER_WEB_PORT" \
  --api-base-url "http://127.0.0.1:${CHILD_MANAGER_API_PORT}"
```

Web 必须把浏览器同源 `/api/v1/*` 请求服务器侧转发到 API，并双向转发认证 Cookie、
`Origin/Referer`、`X-CSRF-Token` 和 API 返回的 `Set-Cookie`。浏览器脚本不得读取 access 或
refresh Cookie，也不得把 token 放入 localStorage 或 NiceGUI 持久化存储。BFF 必须丢弃
浏览器伪造的 `Forwarded`、`X-Forwarded-For` 与内部客户端地址头，按直接 socket 对端重建；
API 仅信任显式配置的回环 BFF，伪造地址不得绕过或嫁祸登录来源限流。
登录和刷新响应必须各保留两条独立 access/refresh `Set-Cookie`；退出响应必须保留两条独立
过期 Cookie。浏览器网络面板和 raw headers 中不得出现逗号折叠后的单一字段。

自动化先运行 `uv run pytest tests/web/test_bff_proxy.py`：逐项验证方法、路径、query、body，
Cookie、Origin/Referer、`X-CSRF-Token`，多个 `Set-Cookie`、`Content-Type`、`X-Request-ID`，
hop-by-hop 头剥离和伪造来源头重建；浏览器网络记录不得出现任何直连
`CHILD_MANAGER_API_PORT` 的请求。

检查：

```bash
export CHILD_MANAGER_COOKIE_JAR="$CHILD_MANAGER_RUNTIME_ROOT/cookies.txt"
curl --fail "http://127.0.0.1:${CHILD_MANAGER_API_PORT}/health/live"
curl --fail "http://127.0.0.1:${CHILD_MANAGER_API_PORT}/health/ready"
curl --fail "http://127.0.0.1:${CHILD_MANAGER_WEB_PORT}/"
# 以下 CSRF 业务端点仅在 T035 完成后检查：
curl --fail --cookie-jar "$CHILD_MANAGER_COOKIE_JAR" \
  "http://127.0.0.1:${CHILD_MANAGER_WEB_PORT}/api/v1/auth/csrf"
rm -f "$CHILD_MANAGER_COOKIE_JAR"
```

预期：API 存活；就绪响应分别报告 PostgreSQL、Redis 与必要配置。PostgreSQL 不可用返回
503 `database.unavailable`；所有核心请求共同依赖的 JWT/CSRF 等全局安全配置缺失/无效返回
503 `configuration.unavailable`。Redis、AI、日历、Word 模板或导出存储不可用时整体仍返回
200，但相应 check 为 degraded；实际依赖端点可在受理前返回 `configuration.unavailable`。
Redis 不可用时 API 保持可提供同步手工能力并以 degraded 状态报告，
不能把已保存到 PostgreSQL 的任务改报未受理。固定 AI/在线日历不可用不得令 API 整体
不就绪。浏览器访问本档位 `CHILD_MANAGER_WEB_PORT` 进入中文登录页，CSRF 响应及 Cookie
也来自同一 Web 端口；档位专属 cookie jar 仅用于本次本地检查，命令结束时必须删除。

## 5. 自动化质量门禁

先运行相关快速测试，再运行完整门禁：

```bash
uv run pytest tests/architecture tests/contract
uv run pytest tests/migrations tests/repository
uv run pytest tests/api tests/worker tests/word tests/web
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

预期全部为 0 exit code，且测试输出没有外部网络调用。任何命令未配置或未执行都必须明确
报告，不能替换成更宽松命令后声称通过。

模板原件检查：

```bash
sha256sum templates/teacherplan/teacherplan.docx
git status --short -- templates/teacherplan/teacherplan.docx
```

预期哈希：

```text
72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043
```

预期 `git status` 对模板无输出。

## 6. 浏览器验收路径

### 6.1 初始化、登录与会话

1. 打开 `http://127.0.0.1:${CHILD_MANAGER_WEB_PORT}/`，由同源 BFF 的
   `/api/v1/auth/csrf` 取得签名 CSRF Cookie；浏览器不得请求
   `http://127.0.0.1:${CHILD_MANAGER_API_PORT}/api/v1/*`。
2. 使用初始化管理员登录；确认 Cookie 为 HttpOnly/SameSite=Lax，开发环境仅 Secure=false。
3. 缺失/伪造 `X-CSRF-Token` 或错误 Origin 的状态变更必须得到
   `403 auth.csrf_invalid`。
4. 连续错误登录验证账号维度指数延迟与来源维度 429；不存在、错误密码、停用账号显示
   同一类中文提示。
5. 刷新后旧 Refresh Token 不再可用；重放旧 token 后该 token family 全部撤销。
6. 修改密码、管理员重置和停用账号后既有会话不能完成下一请求。

预期：所有成功、失败、限流、刷新重放和账号变更均有脱敏审计，不泄露账号是否存在。

### 6.2 必要设置与权限

1. 在“系统设置”创建当前学期、教师、班级、年龄段关系和教师关联。
2. 保存一个室内/户外区域都为空的班级；系统允许保存并提示配置未完成。
3. 只配置户外区域；教师仍可完整使用手工教案和户外 AI，室内 AI 显示缺少室内区域。
4. 教师登录后只看到关联班级；管理员可查看、导出、归档/恢复全园教案，但未关联该班时
   不能编辑、调用 AI 或维护区域。
5. 解除教师关联；旧教案仍显示署名，但该教师刷新或下一请求立即失去访问，且不能再次被
   选为新作者。

### 6.3 纯手工教案

1. 在“教案”日历选择关联班级和学期内工作日；创建后再次选择同日，应打开同一 ID。
2. 选择当前学期外日期；教案仍绑定当前学期快照，周次显示为空，只出现软提示。
3. 填写六栏，停止输入约 3 秒；显示“保存中 → 已保存”，版本加一但快照数不变。
4. 显式保存；恰好新增一条 `manual_save` 快照。
5. 两个标签页基于同版本修改；后提交者收到 `409 lesson_plan.version_conflict`，正文不覆盖。
6. 归档后页面只读；恢复归档后可编辑。恢复历史先保留恢复前内容，旧历史不变。

预期：关闭 AI、Redis Worker 和在线工作日来源时，手工创建、保存、归档、恢复和已有导出
下载仍可用；依赖故障的功能给出中文提示。

### 6.4 可靠 AI 任务与栏目级采用

1. 先制造未保存修改再点击一键生成；Web 必须先完成无快照自动保存（autosave），保存失败或 409 时
   不提交生成。保存成功后使用固定 AI 替身继续；恰好出现晨间、晨谈、室内、户外四个
   子任务，集体和反思任务数为 0。
   父任务数据库 execution/attempt/租约字段必须为 NULL，API 显示 attempt 为 0/0 且 status
   只由四个子任务派生。
2. 停止 Redis 后发起新请求；在 2 秒内得到任务 ID 与“等待投递”。恢复 Redis 后，任务
   应在一个 15 秒扫描周期外加调度容差内自动进入队列。
3. 让一个栏目最终失败；其他成功栏目仍可独立预览和采用，只重试该 failed AI 栏目。重试
   必须创建新任务/结果并复制原冻结输入；batch 父任务、提示词测试、Word 导出和其他状态
   返回 `409 job.retry_not_allowed`，需要新输入时走普通新生成。
4. 生成后修改无关栏目并保存，刷新取得最新版本；预览仍可采用。
5. 修改目标栏目或本次实际输入；采用返回 `409 ai.preview_stale`，当前内容不变。
6. 拒绝/关闭预览；正文和快照数不变。每次成功采用只增加一条快照。
7. 用固定时钟验证约 5 秒/30 秒退避、429 `Retry-After` 上限 60 秒和总模型调用不超过 3。
8. 在提示词草稿中验证 `{{class_name}}`、`{{ class_name }}`、水平 Tab 合法；换行/Unicode
   空白、大小写、前导下划线、点号、下标、未知变量、表达式、过滤器、循环和未闭合占位符
   均被拒绝。只有固定白名单纯替换可保存，复杂值的稳定 JSON 与输入哈希可重复，
   `teacher_context` 中的 `{{...}}` 不得被二次解释。
9. 创建提示词测试后改变页面变量对象或草稿；Worker 仍只使用 run 中冻结的实际 input、
   提示词正文/哈希、结果 Schema 和模型非密钥调用快照。再修改模型地址、名称、能力或密钥；
   `call_config_revision` 必须递增，旧任务以 `prompt.configuration_changed` 零外部调用失败，
   不得混用新密钥与旧地址。revision 一致时才读取当前密钥并实时复核账号、模型启用和当前
   地址安全。历史响应的 `input_summary` 只显示排序变量名和 `all_values_redacted=true`，不得
   出现值、正文或模型地址。让原 run 被最近 20 条策略清理后
   重放原 key，应返回同一 job 且关联 run 为空，零删除、零新增、零模型调用。

### 6.5 反思

1. 任一上游栏目的固定 Schema 不完整时，反思按钮不可用且 API 拒绝建任务。
2. 用纯手工内容完成五栏且不添加 AI 新环节；按钮仍可用，但页面可提示尚无新增环节。
3. 五栏有未保存修改时点击；API 必须在同一数据库事务内按 `expected_version` 预保存当前
   页面正文、校验五栏并创建幂等记录、任务与唯一 pending AI 结果占位；占位冻结五栏输入、
   目标基线、模型、提示词和 Schema，预保存不创建教案快照。
4. 用并发修改制造保存冲突；整个事务回滚并返回 409，正文、快照、任务、结果占位和幂等
   记录数不变。
5. 五栏全部完整并成功保存后，未点击时数据库中反思任务仍为 0。
6. 点击后任务 `current_plan` 只使用该事务保存的五个上游栏目及必要展示上下文，不把旧反思
   作为输入。
7. 采用结果后反思包含 `highlights/issues/adjustments`；三个值分别做 NFKC 规范化后拼接，
   按 Unicode code point 计数（内容中的空白、标点和 emoji 都计入）合计不超过 200。

### 6.6 集体活动与安全 `.docx`

1. 分别粘贴文本和上传合法 `.docx`；先显示提取文本供确认，长期无原附件。
2. 验证超过 10 MiB、解压超过 50 MiB、ZIP 条目超过 1000、提取超过 200,000 字符，以及
   宏、外部关系、路径穿越、嵌套压缩和伪装 OOXML 全部被拒绝，临时目录无残留。
3. 让拆分成功；显示“尚未新增适龄环节”，拆分结果可先采用，采用前创建新增任务必须被拒绝。
4. 拆分采用并保存后再创建新增环节任务；让其先失败、稍后重新生成，已采用拆分保持不变；
   采用新增结果后只插入一个结构化 step 且 `is_ai_added=true`。
5. 编辑该 step 不自动取消标记；显式取消后 Word 不再把它标红。

### 6.7 Word 导出与历史

1. 有未保存修改时发起导出；必须先按版本无快照保存，保存失败不建导出任务。
2. 晨间、晨谈、集体、室内、户外五栏有缺失且尚未确认时先得到缺失项，正文/版本/任务/key
   均无变化；确认后把保存、不可变导出输入和任务创建原子提交，不自动调用 AI。反思为空
   不触发确认，直接受理导出。
3. 同一教案导出两次；得到不同记录、内部 storage key 和服务器副本。第一条任务排队后再
   修改当前教案，第一份文件仍必须使用其创建事务冻结的旧输入。
4. 打开结果，验证表格数量/结构、固定文本、字段位置、中文字体、字号、段落和换行。
5. 学期外周次单元格为空；反思为空时仍输出三行空内容；只有仍标记的集体新增 step 正文为红色。
6. 以无权限用户下载得到拒绝且无服务器路径。删除测试导出副本后重下得到
   `410 export.file_missing`，不得重新生成冒充旧文件。

### 6.8 工作日与软降级

固定时钟/替身验证：

- 已确认本地或在线结论缓存 24 小时。
- 两来源不可用保存 `unknown/unavailable`，缓存 5 分钟并软提示。
- 来源冲突时本地优先、保存 `combined` 和最小摘要，缓存 1 小时并软提示。
- 在线连接超过 2 秒或总耗时超过 5 秒即降级，不阻止教案主流程。

### 6.9 审计与敏感信息

管理员在“审计记录”按事件、操作者、资源、结果和日期筛选。至少验证登录、账号/角色、
设置、模型、提示词、AI、手动保存、归档/恢复、历史恢复、导出和下载事件。

扫描代码、日志、错误、Redis 消息、审计与测试快照，预期密码、Cookie、token、完整 API
Key、主密钥、完整教案/AI 正文和绝对服务器路径暴露数为 0。

故障验收必须按依赖边界区分：AI、Redis 投递、Worker 或在线日历故障时，同步手工流程和
底层存储仍可读的既有导出下载继续；新 Word 生成或存储写入失败时，已保存教案和既有成功
副本不受影响，失败记录不得指向半成品；若导出存储的读取能力本身不可用，历史下载应返回
明确脱敏错误，不能宣称仍可下载，也不能重新生成文件冒充旧副本。

## 7. API 契约快速检查

```bash
uv run pytest tests/contract/test_openapi_document.py
uv run pytest tests/contract/test_pagination.py tests/contract/test_errors.py tests/contract/test_idempotency.py
```

预期：

- 所有声明 `page/page_size` 的可增长集合默认 `page_size=20`、最大 100，响应字段固定为
  `items/page/page_size/total`。
- `/settings/age-groups` 固定返回四个系统年龄段且不分页；班级区域 GET 使用标准分页，
  整体 PUT 成功返回 `204` 后由客户端重新分页读取最新顺序。
- FastAPI/Pydantic 和业务错误均为 `code/message/request_id/field_errors`。
- 同请求同 `Idempotency-Key` 返回原任务；同 key 不同摘要返回
  `409 request.idempotency_conflict`。
- 同 key/body 用于不同实际 `plan_id`、提示词 code 或 `job_id` 时必须因 path 参数进入摘要而
  返回冲突，不能错误重放另一资源的任务。
- 保存、归档、恢复、历史恢复、AI 采用和导出校验 `expected_version`。
- 未登录返回 401；已认证但缺少管理员或班级能力返回 403；跨园或不应暴露的资源返回 404。
- PostgreSQL 无法读写权威事实使用 503 `database.unavailable`；所有核心请求依赖的全局安全
  配置使 ready 返回 503 `configuration.unavailable`。功能专属配置/资源只令 ready degraded，
  实际依赖端点可返回 `configuration.unavailable`。Redis 投递失败但 DB 已受理
  时返回 202 `pending_dispatch`，外部 AI/日历/Word 失败通过任务或资源状态表达。

## 8. 完整验收记录

M8 报告必须逐条记录：命令、执行日期、环境、退出码、浏览器 URL、预期与实际结果、截图或
测试报告位置、未执行原因和已知风险。只有全部未延后 PRD 验收项有自动化或可重复人工证据，
且没有未解释跳过，才可进入 M9 的独立生产部署与访问网络复审。
