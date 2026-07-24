# Dev 跨机器开发交接（2026-07-24）

状态：当前实现快照与 Ubuntu 迁移说明

适用分支：`dev`

本文只记录当前实现进度、开发机依赖和恢复步骤，不修改产品、架构或安全契约。长期规则仍以
[`AGENTS.md`](../../AGENTS.md)、固定 `docs` 基线和
[`local-development-environments.md`](local-development-environments.md) 为准。

## 1. 恢复时先确认的基线

| 项目 | 当前事实 |
| --- | --- |
| GitHub 仓库 | `git@github.com:ywyz/child-manager.git` |
| 实现分支 | `dev` |
| M3A Issue | [#8：密码 + TOTP 双因素备用登录](https://github.com/ywyz/child-manager/issues/8) |
| 固定文档基线 | `docs@7fdb8aff46ee1206029a10ba4ed46cb9bdbee54d` |
| Foundational GREEN 实现 | `dev@646f828ffe091c412ae785376757113538ccf4f4` |
| 当前迁移 head | `0005_password_totp_backup_login` |
| 当前任务边界 | T001–T015 已完成；从 T016 开始，不进入 M4 |

交接文档本身位于上述实现提交之后。新机器应以最新 `origin/dev` 为入口，并确认
`646f828ffe091c412ae785376757113538ccf4f4` 是其祖先：

```bash
git clone git@github.com:ywyz/child-manager.git
cd child-manager
git switch dev
git pull --ff-only origin dev
git status --short --branch
git merge-base --is-ancestor \
  646f828ffe091c412ae785376757113538ccf4f4 HEAD
```

不要从 `main` 开始实现。`main` 仍不是当前开发入口；`docs` 只负责已确认设计和契约，
业务实现继续在 `dev` 完成。

## 2. 当前实现进度

### 2.1 已完成

- T001–T002：Issue #8、固定 docs 基线和 `0004_settings` 迁移起点已确认。
- T003–T009：M3A RED 门禁已建立，38 项测试成功收集；当时为
  `34 failed, 4 passed, 0 errors`，失败只来自尚未实现的 M3A 行为。
- T010：`0005_password_totp_backup_login.py` 已完成升级、降级、约束和唯一 Alembic head。
- T011–T013：独立备用认证模型、Argon2id、Unicode 密码策略、RFC 6238 TOTP、
  AES-256-GCM 信封、开发文件密钥和固定测试密钥适配器已完成。
- T014：Repository 已实现园所隔离、单活动 enrollment、TOTP counter 原子消费、
  凭据版本更新和相关会话撤销。
- T015：现有 `IdentityService` 已承载认证保证边界；管理员
  `restricted_enrollment`、五分钟 WebAuthn/备用重新验证和仅 `add_passkey` 的备用证明已完成。
- T010–T015 的本地提交为
  `646f828ffe091c412ae785376757113538ccf4f4`
  （`feat(auth): 完成 M3A 备用登录基础能力`）。

### 2.2 已验证门禁

- 迁移专项：`4 passed`，`uv run alembic heads` 只有
  `0005_password_totp_backup_login (head)`。
- Foundational GREEN 分区：`272 passed, 1 deselected, 1 warning`。
- 原有 246 项测试全部保持通过。
- T016 以后目标集：`17 failed, 1 passed, 0 errors`；失败只来自尚不存在的备用路由和
  Web 行为，没有 collection、fixture、数据库或 T010–T015 基础能力错误。
- `uv sync --locked`、Ruff format/check、Pyright 和 `git diff --check` 均通过。
- Foundational 提交的 Graphify 证据为 2571 个节点、4908 条边、327 个社区，结构和敏感
  信息检查通过；加入本交接记录后的增量图谱证据为 2590 个节点、4926 条边、319 个社区。

完整证据保存在 Issue #8。推送当前交接后，GitHub Actions 的完整 `pytest` 仍可能因
T016 以后故意保留的测试而显示 RED；在完成 T016–T019 前，这不是既有 246 项测试回归。

### 2.3 尚未实现

- 没有开放公共备用登录。
- 没有实现 T016–T019 的绑定 Service、API 和 Web 用户故事。
- 没有实现 T020–T029 的备用登录、重新验证、维护和恢复用户故事。
- 没有执行 T030–T034 的最终脱敏、契约漂移、完整验收和双轴 Review。
- 不得勾选 T016，不得宣称 M3A 完成，也不得进入 M4。

## 3. 下一步：只从 T016 开始

顺序固定为 `T016 → T017 → T018 → T019`：

1. T016：实现绑定开始、10 分钟过期、一次性种子、密码和首个 TOTP 原子启用，以及旧
   enrollment、旧材料和相关备用会话替换。
2. T017：实现绑定状态和验证 API、CSRF、限流、通用错误与最小审计。
3. T018：实现管理员受限绑定页、二维码/人工输入值单次展示、教师可跳过提示与状态页。
4. T019：运行绑定 API、Web、契约和敏感信息测试，更新 Issue #8 的 US1 GREEN 证据。

开始 T016 时先处理一个已定位的实现接缝：

- TOTP enrollment 信封的 AAD 必须绑定最终 `enrollment_id`。
- 当前 `IdentityRepository.start_backup_enrollment()` 在 Repository 内部生成该 ID，
  Service 无法在持久化前用同一个 ID 完成加密。
- 先让 Repository 接收由 Service 生成的 `enrollment_id`，增加“AAD subject ID 等于
  持久化 enrollment ID”的测试，再实现 T016 事务。该调整属于 T016，不是第二套认证服务。

进入后续任务前还要保留以下边界：

- T017 的 `DELETE /auth/backup` 与 T026 的教师关闭/管理员拒绝关闭语义有重叠；T017 只实现
  US1 所需边界，不得静默提前完成 T026。
- T018 冒烟测试出现“本人安全事件”，完整事件投影属于 T028；T018 不得创建空壳第二套事件
  页面或提前实现 T028。
- `specs/002-password-totp-backup-login/quickstart.md` 当前引用不存在的
  `tests/api/test_backup_auth.py`；实际测试已经拆为 `test_backup_enrollment.py`、
  `test_backup_authentication.py` 和 `test_backup_maintenance.py`。最迟在 T019/T032 验收前，
  应先按 `docs -> Issue -> dev` 流程修正固定事实来源。
- 根目录 `CONTEXT.md` 和 `specs/001-daily-activity-plan/quickstart.md` 的阶段摘要早于当前
  T010–T015 提交。判断即时进度时以本文、Issue #8、M3A `tasks.md` 和实时 Git 状态为准，
  不要直接改写 `dev` 中的固定产品契约来消除历史摘要。

## 4. Ubuntu 所需软件

### 4.1 项目必须项

| 软件 | 要求或用途 |
| --- | --- |
| Ubuntu | 当前验证主机为 Ubuntu 24.04.4 LTS x86_64；其他受支持 Ubuntu 版本需重新验证 |
| Git + OpenSSH | 克隆和推送 GitHub；新机器重新配置 SSH key |
| Python | 项目要求 3.14+；使用 uv 管理，不使用系统 Python 3.12 运行项目 |
| uv | 按 `uv.lock` 创建 `.venv`、安装依赖并运行全部 Python 命令 |
| Docker Engine | 只启动本地 PostgreSQL 18 和 Redis 8 |
| Docker Compose plugin | 读取 `compose.dev.yaml`；不是生产部署拓扑 |
| OpenSSL | 生成本地 PostgreSQL、JWT、CSRF 和身份主密钥材料 |
| Chromium | 由 `uv run playwright install --with-deps chromium` 安装，用于 Web 冒烟 |
| `rg` / `fdfind` | 项目规定的文本和文件搜索工具 |
| ast-grep | 项目规定的 AST 搜索工具；优先使用显式命令 `ast-grep` |
| graphify 0.9.23 | 文档/架构知识图谱查询与 `graphify update .` |
| GitHub CLI 或 GitHub Codex 插件 | 查看和更新 Issue #8；至少一种方式完成认证 |

当前主机实测版本，仅作为可复现参考，不替代仓库锁：

```text
Ubuntu 24.04.4 LTS x86_64
uv 0.11.30
uv 管理的 CPython 3.14.6
Git 2.43.0
Docker 29.6.2
Docker Compose v5.3.1
OpenSSL 3.0.13
GitHub CLI 2.96.0
graphify 0.9.23
ripgrep 14.1.0
fdfind 9.0.0
```

Python 应用和开发依赖的唯一版本事实来源是 `pyproject.toml` 与 `uv.lock`。主要运行栈包括
FastAPI、NiceGUI、SQLAlchemy 2、Alembic、Psycopg 3、Dramatiq 2、Redis、
`webauthn` 3、Argon2、cryptography 和 python-docx；不要创建 `requirements.txt`。
Node.js、系统级 `psql` 和系统级 `redis-server` 不是项目运行必需项。

### 4.2 当前主机已发现的工具缺口

当前主机虽然有 `/usr/bin/sg`，但它是 Ubuntu 的系统组切换命令，不是 ast-grep；
`ast-grep` 本身未安装。这与 `AGENTS.md` 中的工具清单不一致。新机器必须安装 ast-grep，
并用下面的命令验证，不能把 `/usr/bin/sg` 的成功退出当成 AST 工具可用：

```bash
command -v ast-grep
ast-grep --version
```

如果要兼容仓库中写作 `sg` 的说明，可以在确认用户级 `PATH` 优先于 `/usr/bin` 后，为
ast-grep 建立用户级 `sg` 入口；不要覆盖 `/usr/bin/sg`。

Docker CLI 已安装，但本次交接时当前账号无权读取 `/var/run/docker.sock`。新机器如果采用
Docker 非 root 模式，应按 Docker 官方说明配置；若加入 `docker` 组，需要理解该组具有近似
root 的权限，并在重新登录后确认：

```bash
docker version
docker compose version
docker ps
```

### 4.3 新机器安装入口

Ubuntu 基础工具可以先安装：

```bash
sudo apt update
sudo apt install -y ca-certificates curl git openssh-client openssl ripgrep fd-find
```

其余工具按各自官方说明安装，避免复制旧机器的二进制或用户配置：

- [uv 安装说明](https://docs.astral.sh/uv/getting-started/installation/)；安装后执行
  `uv python install 3.14`。
- [Docker Engine for Ubuntu](https://docs.docker.com/engine/install/ubuntu/)；同时安装
  Docker Compose plugin。
- [ast-grep Quick Start](https://ast-grep.github.io/guide/quick-start.html)；Ubuntu 上验证
  `ast-grep`，不要误用系统 `/usr/bin/sg`。
- [GitHub CLI Linux 安装说明](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)；
  或在 Codex 中重新连接 GitHub 插件。
- [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) 或
  [Codex IDE 扩展](https://learn.chatgpt.com/docs/codex/ide)；安装后重新配置个人 Skill、
  插件和 MCP。

## 5. Codex、Skill 与 MCP

仓库克隆后会自动得到：

- 根目录 `AGENTS.md`：项目持久开发规则。
- `.agents/skills/speckit-*`：Spec Kit 的 analyze、clarify、plan、tasks、implement 等技能。
- 固定规格、任务、Quickstart 和 OpenAPI 契约。

另一台机器还需要在 Codex 用户环境中确认下列能力；它们不应连同凭据直接提交到仓库：

| 能力 | 当前用途 | 当前机器位置或形态 |
| --- | --- | --- |
| `graphify` Skill | 跨文档/架构查询，业务或重大文档变更后的图谱更新 | `~/.codex/skills/graphify/SKILL.md` |
| codebase-memory MCP | 代码符号、调用链和影响分析的第一搜索入口 | Codex MCP 配置 |
| `tdd` Skill | T016–T019 的 RED → GREEN 实施 | `~/.agents/skills/tdd/SKILL.md` |
| `code-review` Skill | T034 Standards + Spec 双轴 Review | `~/.agents/skills/code-review/SKILL.md` |
| `diagnosing-bugs` Skill | 处理难以定位的失败或性能问题 | `~/.agents/skills/diagnosing-bugs/SKILL.md` |
| `resolving-merge-conflicts` Skill | 仅在真实 merge/rebase 冲突时使用 | `~/.agents/skills/resolving-merge-conflicts/SKILL.md` |
| `codebase-design` Skill | 调整 Repository/Service 接缝时保持深模块边界 | `~/.agents/skills/codebase-design/SKILL.md` |
| GitHub 插件或 `gh` | Issue #8、CI 和仓库状态 | Codex 插件或主机 CLI |

Codex 的个人 `~/.codex/config.toml`、MCP OAuth、GitHub 登录、插件授权和 API 凭据不得提交。
在新机器安装当前 Codex 后，通过 Skills/Plugins 页面重新安装或连接这些能力，并重新配置
codebase-memory MCP。仓库级规则由 `AGENTS.md` 自动提供，不要用个人配置复制一份并造成漂移。

Graphify CLI 可使用 uv tool 独立安装并固定为当前图谱版本：

```bash
uv tool install 'graphifyy==0.9.23'
graphify --version
test -f graphify-out/graph.json
```

若 Codex 用户级 Graphify Skill 尚未安装，仅安装 CLI 不等于 Skill 已存在；还要在 Codex
Skills 中确认 `graphify` 可见。GitHub、codebase-memory 和其他 MCP/插件需要在新机器重新授权，
不要复制旧机器的 OAuth token 或认证数据库。

## 6. 本地环境与秘密

### 6.1 不要迁移的内容

不要从旧机器复制或提交以下内容：

- `.venv/`、`.env*`、`.secrets/`、Cookie jar、日志、导出和临时目录。
- PostgreSQL/Redis Docker volume；当前阶段应从迁移和测试在新机器创建干净本地数据库。
- PostgreSQL 口令、JWT/CSRF 签名密钥、身份主密钥、GitHub/Codex OAuth 或 SSH 私钥。
- 旧机器的绝对路径、Docker socket 权限或运行中的容器状态。

### 6.2 仓库外创建本地秘密

下面只展示生成方式，不把值写入仓库：

```bash
child_manager_secret_dir="${XDG_CONFIG_HOME:-$HOME/.config}/child-manager"
install -d -m 700 "$child_manager_secret_dir"
umask 077
openssl rand -hex 32 > "$child_manager_secret_dir/postgres-password"
openssl rand 32 > "$child_manager_secret_dir/totp-master-v1.key"
chmod 600 \
  "$child_manager_secret_dir/postgres-password" \
  "$child_manager_secret_dir/totp-master-v1.key"
```

`totp-master-v1.key` 必须是恰好 32 字节的二进制文件、属于当前用户、权限不超过 `0600`，
并位于仓库之外。T013 已实现 `FileIdentitySecretKeyProvider`，但 T016 尚未冻结把该文件接入
Service 的环境变量名称；不要自行发明并提交第二套配置契约。

### 6.3 Dev 档位

建议把下列 export 写入仓库外、权限为 `0600` 的个人 shell 文件，然后在每个新终端显式
`source`。其中不应出现提交到 Git 的真实值：

```bash
export CHILD_MANAGER_PROFILE=dev
export COMPOSE_PROJECT_NAME=child_manager_dev
export CHILD_MANAGER_WEB_PORT=18080
export CHILD_MANAGER_API_PORT=18000
export CHILD_MANAGER_POSTGRES_PORT=15432
export CHILD_MANAGER_REDIS_PORT=16379
export CHILD_MANAGER_DATABASE_NAME=child_manager_dev
export CHILD_MANAGER_TEST_DATABASE_NAME=child_manager_dev_test
export CHILD_MANAGER_RUNTIME_ROOT="${XDG_RUNTIME_DIR:-/tmp}/child-manager-dev"

child_manager_secret_dir="${XDG_CONFIG_HOME:-$HOME/.config}/child-manager"
export CHILD_MANAGER_POSTGRES_PASSWORD="$(
  tr -d '\n' < "$child_manager_secret_dir/postgres-password"
)"
export CHILD_MANAGER_DATABASE_URL="postgresql+psycopg://child_manager:${CHILD_MANAGER_POSTGRES_PASSWORD}@127.0.0.1:${CHILD_MANAGER_POSTGRES_PORT}/${CHILD_MANAGER_DATABASE_NAME}"
export CHILD_MANAGER_TEST_DATABASE_URL="postgresql+psycopg://child_manager:${CHILD_MANAGER_POSTGRES_PASSWORD}@127.0.0.1:${CHILD_MANAGER_POSTGRES_PORT}/${CHILD_MANAGER_TEST_DATABASE_NAME}"
export CHILD_MANAGER_REDIS_URL="redis://127.0.0.1:${CHILD_MANAGER_REDIS_PORT}/0"
export CHILD_MANAGER_TEST_REDIS_URL="redis://127.0.0.1:${CHILD_MANAGER_REDIS_PORT}/15"

export CHILD_MANAGER_ENV=development
export CHILD_MANAGER_BIND_HOST=127.0.0.1
export CHILD_MANAGER_COOKIE_SECURE=false
export CHILD_MANAGER_JWT_SIGNING_KEY="$(openssl rand -base64 32)"
export CHILD_MANAGER_CSRF_SIGNING_KEY="$(openssl rand -base64 32)"
export CHILD_MANAGER_ALLOWED_ORIGINS="http://localhost:${CHILD_MANAGER_WEB_PORT}"
export CHILD_MANAGER_TRUSTED_BFF_PEERS=127.0.0.1
export CHILD_MANAGER_WEBAUTHN_RP_ID=localhost
export CHILD_MANAGER_WEBAUTHN_RP_NAME="Child Manager Dev"
```

开发环境关闭 Cookie `Secure` 时，API 和 Web 只能绑定回环地址。不要把 host 改成
`0.0.0.0`、`::` 或局域网地址。

## 7. 新机器恢复与验证

加载 Dev 档位后执行：

```bash
uv python install 3.14
uv sync --locked
uv run python -VV
uv run playwright install --with-deps chromium

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

uv run alembic upgrade head
uv run alembic heads
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

需要启动应用时，在三个加载同一 Dev 档位的终端分别运行：

```bash
uv run python -m apps.api \
  --host "$CHILD_MANAGER_BIND_HOST" \
  --port "$CHILD_MANAGER_API_PORT"
```

```bash
uv run python -m apps.worker
```

```bash
uv run python -m apps.web \
  --host "$CHILD_MANAGER_BIND_HOST" \
  --port "$CHILD_MANAGER_WEB_PORT" \
  --api-base-url "http://127.0.0.1:${CHILD_MANAGER_API_PORT}"
```

浏览器只访问 `http://localhost:18080`，不得直接访问 API 端口。

复现 T010–T015 GREEN 分区：

```bash
uv run pytest \
  --ignore=tests/api/test_backup_enrollment.py \
  --ignore=tests/api/test_backup_authentication.py \
  --ignore=tests/api/test_backup_maintenance.py \
  --ignore=tests/web/test_backup_auth_smoke.py \
  --deselect=tests/contract/test_backup_auth_contract.py::test_runtime_router_matches_the_frozen_backup_contract
```

复现 T016 以后预期 RED：

```bash
uv run pytest \
  tests/api/test_backup_enrollment.py \
  tests/api/test_backup_authentication.py \
  tests/api/test_backup_maintenance.py \
  tests/web/test_backup_auth_smoke.py \
  tests/contract/test_backup_auth_contract.py::test_runtime_router_matches_the_frozen_backup_contract
```

预期分别是 `272 passed, 1 deselected, 1 warning` 和
`17 failed, 1 passed, 0 errors`。如果出现 collection、fixture、数据库连接错误，或者既有
246 项测试失败，不属于预期 RED，必须先修复环境或回归再进入 T016。

业务代码或重大文档变化后继续执行：

```bash
graphify update .
graphify diagnose multigraph --graph graphify-out/graph.json --undirected
git diff --check
```

## 8. 恢复完成判定

只有同时满足以下条件，才开始 T016：

- `dev` 已快进到最新 `origin/dev`，工作树干净。
- `646f828` 是当前 HEAD 的祖先，Alembic 只有 `0005_password_totp_backup_login` 一个 head。
- Dev 档位变量已加载，PostgreSQL/Redis 只绑定 `127.0.0.1`。
- `.venv` 由 `uv sync --locked` 在新机器重建，Chromium 已安装。
- Foundational GREEN 分区通过，T016 以后失败仍只属于预期 RED。
- Graphify Skill、codebase-memory MCP 和 TDD 工作流可用；GitHub Issue #8 可读取。
- 没有把密码、TOTP 种子、密钥、OAuth、`.env`、数据库卷或运行时文件带入 Git。
