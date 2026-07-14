# Child Manager 双实现本地开发环境

文档版本：v1.0

状态：已确认

日期：2026-07-14

适用对象：Codex、Trae、维护者与审阅者

## 1. 文档目的

本文定义 `codex` 与 `trae` 两套独立实现如何在同一台开发机上并行工作，避免 Git 工作区、宿主机端口、Compose 资源、数据库、缓存和运行时文件互相影响，并说明中国大陆网络环境下 Python 包与容器镜像的可选加速方式。

本文只规定本地开发和自动化测试环境，不是生产部署设计。根据 ADR-0009，生产访问网络、反向代理、端口映射、密钥托管、备份和发布流程仍延后到 M9 复审。

## 2. 事实来源与边界

- [`AGENTS.md`](../../AGENTS.md)：安全、Git、依赖、验证和生产部署延后规则。
- [`dual-agent-development.md`](dual-agent-development.md)：双 Agent 的分支、Issue、同步和只读交叉评审协议。
- [`ROADMAP.md`](../ROADMAP.md)：M1 工程骨架、本地依赖和出口门禁。
- [`quickstart.md`](../../specs/001-daily-activity-plan/quickstart.md)：M1–M8 完成后的启动与验收合同。
- [`ADR-0009`](../ADR/ADR-0009-defer-production-deployment-until-feature-complete.md)：当前只允许本地开发与测试所需的最小依赖。

本文不得用于放宽回环绑定、Cookie、CSRF、园所隔离、密钥和生产部署限制。出现冲突时按 `AGENTS.md` 停止会固化冲突的实现并请求确认。

## 3. 工作树隔离

Codex 与 Trae 不得在同一个工作目录中反复切换分支或同时写入。推荐从当前共享仓库建立两个 Git worktree：

```text
<workspace>/child-manager        main：共享文档、模板和架构约束
<workspace>/child-manager-codex  codex：Codex 独立实现
<workspace>/child-manager-trae   trae：Trae 独立实现
```

在分支和工作树操作已获授权、目标目录不存在且各分支未被其他工作树占用时，可由维护者执行：

```bash
git worktree add ../child-manager-codex codex
git worktree add ../child-manager-trae trae
git worktree list
```

每个实现只在自己的 worktree 中创建 `.venv`、运行应用和执行测试。两者可以共享 Git 对象库与 uv 全局下载缓存，但不得共享虚拟环境、未提交文件、数据库、导出目录、临时目录或开发密钥文件。

## 4. 固定本地档位

两个实现统一使用以下宿主机端口。容器内部仍使用 PostgreSQL `5432` 和 Redis `6379`；表中端口只绑定 `127.0.0.1`，不得绑定 `0.0.0.0`、`::` 或局域网地址。

| 项目 | Codex 档位 | Trae 档位 |
| --- | --- | --- |
| `COMPOSE_PROJECT_NAME` | `child_manager_codex` | `child_manager_trae` |
| NiceGUI Web | `18080` | `28080` |
| FastAPI API | `18000` | `28000` |
| PostgreSQL 宿主机端口 | `15432` | `25432` |
| Redis 宿主机端口 | `16379` | `26379` |
| 开发数据库名 | `child_manager_codex` | `child_manager_trae` |
| 测试数据库名 | `child_manager_codex_test` | `child_manager_trae_test` |

Dramatiq Worker 不监听浏览器或宿主机服务端口。自动化测试临时启动的 HTTP 替身优先请求操作系统分配动态端口 `0`，不得再占用一组共享固定端口。

### 4.1 Codex 档位

```bash
export CHILD_MANAGER_PROFILE=codex
export COMPOSE_PROJECT_NAME=child_manager_codex
export CHILD_MANAGER_WEB_PORT=18080
export CHILD_MANAGER_API_PORT=18000
export CHILD_MANAGER_POSTGRES_PORT=15432
export CHILD_MANAGER_REDIS_PORT=16379
export CHILD_MANAGER_DATABASE_NAME=child_manager_codex
export CHILD_MANAGER_TEST_DATABASE_NAME=child_manager_codex_test
export CHILD_MANAGER_RUNTIME_ROOT="${XDG_RUNTIME_DIR:-/tmp}/child-manager-codex"
```

### 4.2 Trae 档位

```bash
export CHILD_MANAGER_PROFILE=trae
export COMPOSE_PROJECT_NAME=child_manager_trae
export CHILD_MANAGER_WEB_PORT=28080
export CHILD_MANAGER_API_PORT=28000
export CHILD_MANAGER_POSTGRES_PORT=25432
export CHILD_MANAGER_REDIS_PORT=26379
export CHILD_MANAGER_DATABASE_NAME=child_manager_trae
export CHILD_MANAGER_TEST_DATABASE_NAME=child_manager_trae_test
export CHILD_MANAGER_RUNTIME_ROOT="${XDG_RUNTIME_DIR:-/tmp}/child-manager-trae"
```

实现分支的 `compose.dev.yaml` 必须从这些变量读取宿主机端口，并为缺失的档位变量提供清晰错误，而不是静默回退到可能冲突的固定端口。Compose 服务间仍通过服务名和容器端口通信；只有宿主机启动的应用、诊断工具和测试使用表中的宿主机端口。

两个档位还必须分别从当前 shell 或仓库外、权限受控的档位文件加载 `CHILD_MANAGER_POSTGRES_PASSWORD`。首次创建档位文件时使用 `openssl rand -hex 32` 生成不同值；不得把生成结果写入仓库、`.env`、Compose、日志、测试快照或本文。所有需要连接数据库的终端必须加载同一档位的同一值。

## 5. Compose、数据与文件隔离

`compose.dev.yaml` 只允许包含本地开发和自动化测试所需的 PostgreSQL、Redis 及其健康检查，不得加入 Caddy、生产 Web/API/Worker 编排、DNS、证书、Tailscale、备份或发布任务。

并行运行必须同时满足：

- Compose 项目名不同，使容器、默认网络和命名卷分别归属 `child_manager_codex` 与 `child_manager_trae`。
- PostgreSQL、Redis 的宿主机端口不同，且只绑定回环地址。
- 数据库名、测试数据库名和测试 Worker 标识包含实现档位；并行测试时再增加进程或 worker 后缀。
- 导出、上传解析、Cookie jar、日志和临时文件使用档位专属目录；测试结束清理自己创建的文件，不删除另一档位内容。
- `CHILD_MANAGER_RUNTIME_ROOT` 是本档位运行文件的唯一根目录；Quickstart 在其下创建 `exports/`、`logs/` 与 `tmp/`，Cookie jar 也写入该目录。实现不得静默回退到另一档位或共享固定目录。
- 开发密钥只在当前 shell 或仓库外、权限受控的档位专属文件中生成，不写 `.env`、Compose 文件、日志或 Git。
- 停止一套环境时显式带上其 `COMPOSE_PROJECT_NAME`，不得使用会影响另一项目的全局容器或卷清理命令。

建议在启动后检查实际绑定：

```bash
docker compose -f compose.dev.yaml ps
docker compose -f compose.dev.yaml port postgres 5432
docker compose -f compose.dev.yaml port redis 6379
```

## 6. 技术栈与中国大陆网络边界

M1 及后续功能按现有架构基线使用以下技术栈；本地环境文档不另行引入第二套框架：

| 层级 | 已确认技术 | 主要下载来源与大陆网络处理 |
| --- | --- | --- |
| 语言与依赖 | Python 3.14+、uv、`pyproject.toml`、`uv.lock` | Python 包默认来自 PyPI；访问不稳定时使用第 7 节的 CERNET 用户级镜像 |
| Web | NiceGUI | 随 Python 锁定依赖安装，不需要为当前方案增加 npm 或 Node.js 安装链 |
| API | FastAPI、Uvicorn | 随 Python 锁定依赖安装；浏览器只访问 NiceGUI，同源 BFF 回环访问 API |
| 后台任务 | Dramatiq、Redis | Dramatiq 随 Python 依赖安装；Redis 开发镜像按第 8 节选择官方源或临时加速入口 |
| 数据与迁移 | PostgreSQL、SQLAlchemy 2.x、Alembic | Python 驱动与迁移工具随 uv 安装；PostgreSQL 开发镜像按第 8 节处理 |
| 质量门禁 | Pytest、Ruff、Pyright、OpenAPI 校验 | 全部由实现分支锁定版本；不得因镜像暂时不可用而跳过或替换标准检查 |
| 本地依赖编排 | Docker Compose | 仅编排 PostgreSQL、Redis 最小开发依赖，不代表生产容器拓扑 |

当前没有必须从 npm、GHCR、Quay.io 或 Kubernetes 仓库安装的应用运行依赖。若后续经任务确认新增这些来源，再按实际锁定制品配置镜像覆盖；不得仅因加速站支持某仓库就提前增加技术栈或镜像。

镜像只能解决依赖或容器制品下载，不能替代 GitHub 仓库访问、外部 AI 服务或未来在线日历服务的网络连通性。实现和测试不得假设这些外部网络稳定：常规测试使用确定性替身，真实外部服务只在明确授权的专项验证中访问。

## 7. Python 包下载

项目依赖只由 `pyproject.toml` 与 `uv.lock` 管理。中国大陆网络访问 PyPI 较慢或不稳定时，可以在开发机用户级配置 CERNET 联合镜像，不把地区性镜像写入项目 `pyproject.toml` 或锁文件策略：

Linux/Unix 的 `~/.config/uv/uv.toml`：

```toml
[[index]]
url = "https://mirrors.cernet.edu.cn/pypi/web/simple"
default = true
```

注意：

- 上述 `[[index]]` 语法用于独立的 `uv.toml`；若未来确需写入 `pyproject.toml`，语法是 `[[tool.uv.index]]`，但当前不这样做。
- `default = true` 会用该镜像替代 uv 默认 PyPI，不构成自动故障转移。镜像不可用或同步滞后时，应临时切回 `https://pypi.org/simple` 后重新执行同一条锁定安装验证。
- 不使用 `--index-strategy unsafe-best-match` 混合挑选多个公共源，避免同名包来源和依赖混淆风险。
- pip 镜像只供 uv 之外确有需要的工具使用；项目不得新增或手工维护 `requirements.txt`。
- 两个实现各自维护、提交和验证自己的 `uv.lock`，不得复制另一实现的锁文件作为验证替代。

临时切回官方 PyPI 时不修改仓库文件：

```bash
UV_DEFAULT_INDEX=https://pypi.org/simple uv sync --locked
```

uv 之外的工具确需使用 pip 时只做显式临时覆盖，不把它变成项目依赖安装入口：

```bash
python -m pip install -i https://mirrors.cernet.edu.cn/pypi/web/simple <tool-name>
```

## 8. Docker 镜像下载

`github.ywyz.tech` 可作为不稳定网络下的可选加速入口，但不得成为仓库内唯一镜像来源。当前 `compose.dev.yaml` 允许通过 shell 变量覆盖镜像，并以以下带 SHA-256 digest 的官方镜像作为不可变默认值：

```yaml
services:
  postgres:
    image: ${CHILD_MANAGER_POSTGRES_IMAGE:-postgres:18-alpine@sha256:9a8afca54e7861fd90fab5fdf4c42477a6b1cb7d293595148e674e0a3181de15}
  redis:
    image: ${CHILD_MANAGER_REDIS_IMAGE:-redis:8-alpine@sha256:9d317178eceac8454a2284a9e6df2466b93c745529947f0cd42a0fa9609d7005}
```

使用加速入口时只在当前 shell 覆盖：

```bash
export CHILD_MANAGER_POSTGRES_IMAGE=github.ywyz.tech/postgres:18-alpine@sha256:9a8afca54e7861fd90fab5fdf4c42477a6b1cb7d293595148e674e0a3181de15
export CHILD_MANAGER_REDIS_IMAGE=github.ywyz.tech/redis:8-alpine@sha256:9d317178eceac8454a2284a9e6df2466b93c745529947f0cd42a0fa9609d7005
```

其他仓库按相同前缀规则使用：

```text
Docker Hub：github.ywyz.tech/<namespace>/<image>:<tag>
GHCR：      github.ywyz.tech/ghcr.io/<namespace>/<image>:<tag>
Quay.io：   github.ywyz.tech/quay.io/<namespace>/<image>:<tag>
Kubernetes：github.ywyz.tech/registry.k8s.io/<image>:<tag>
```

镜像加速的约束：

- 加速入口失败时，取消镜像覆盖变量并重试官方镜像；不得为“修好下载”提交永久代理地址。
- 代理镜像必须使用与官方源相同的锁定 tag；风险较高的基础镜像进一步记录并核对 digest。
- 不执行来源不明的远程安装脚本，不在构建参数、镜像名称或日志中放入凭据。
- M1 只拉取 PostgreSQL、Redis 及实现验证确实需要的最小镜像，不提前拉取生产入口、对象存储或未来子系统镜像。

## 9. 并行启动与验收

每个终端先加载自己的档位变量，再按 [`quickstart.md`](../../specs/001-daily-activity-plan/quickstart.md) 启动依赖、API、Worker 和 Web。浏览器只访问该档位的 NiceGUI Web；不得直连 API。

每个实现先在自己的子 Issue 中完成本档位验证；不得因为另一分支尚未完成而阻塞自身 T008。两个实现都完成分支内 M1 验证后，再由共享 M1 父里程碑执行以下同机并行验收：

1. 两个 worktree 的当前分支分别为 `codex`、`trae`，且工作区互不覆盖。
2. 两个 Compose 项目可同时启动，四个依赖宿主机端口均只绑定 `127.0.0.1`。
3. Codex Web/API 与 Trae Web/API 可同时存活，浏览器和 BFF 只访问本档位地址。
4. 两个 PostgreSQL 数据库、Redis 与 `CHILD_MANAGER_RUNTIME_ROOT` 互不读写；导出、日志、Cookie jar 和临时文件都只出现在本档位根目录。
5. 停止或破坏任一档位的 PostgreSQL/Redis，不会停止或误报另一档位服务。
6. 镜像加速入口关闭后，取消覆盖即可回到官方镜像，不需要修改受版本控制文件。

未实际同时运行两套环境时，不得声称并行端口隔离已通过。
