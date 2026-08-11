# 桌面 Slice 2A 本地验收证据

## 1. 范围与固定基线

- 日期：2026-08-11
- 实现分支：`dev`
- 开始实现时基线：`e2ee14a9c30370efb9bdd587f3885bf87f91ba7f`
- 固定 docs SHA：`d4ac961a04a273a0384e295190296f69538b313b`
- 执行 Issue：https://github.com/ywyz/child-manager/issues/19
- Issue 回读结果：旧 SHA 出现 0 次，新 SHA 出现 7 次；T044 已包含空库到 head、
  `0001 -> 0002_desktop_ai`、命名约束/索引、完整性检查、迁移前保护副本成功及失败即停止。
- 证据边界：本文件记录 GREEN 提交前的本地候选树；后续提交、Review、push、远端 CI 与
  Issue 状态以各自固定 SHA/运行记录为准，`main` 集成仍需单独授权。

全部 AI 验收使用 `httpx.MockTransport`、内存凭据后端、脚本化 Runtime 或其他本地替身；没有
调用真实或付费 AI，也没有访问外部网络。

## 2. 行为矩阵

| 场景 | 自动化证据 | 结果 |
|---|---|---|
| 单栏成功 | `test_ai_domain.py`、`test_ai_generation.py` | 冻结最小输入，生成结果只进入 ready preview，不自动覆盖正文 |
| 四栏部分失败 | `test_batch_keeps_successful_previews_when_one_section_fails` | 成功栏目保留，失败栏目独立记录稳定错误码 |
| retryable 重试 | `test_retryable_failure_is_retried_at_most_twice` | 首次调用加最多两次重试，共 3 次；无真实网络 |
| 结构失败 | `test_ai_domain.py` 的 missing/wrong-type/unknown-field 分类 | 无效结构被稳定分类，不写正文 |
| 取消与退出 | `test_cancel_and_close_discard_late_results` | 请求取消后释放单任务槽位，取消/退出后的迟到结果丢弃 |
| 页面切换迟到 | `test_page_change_invalidates_epoch_and_discards_late_signal` | page epoch 变化后不显示迟到 preview |
| 明确拒绝 | `test_reject_changes_only_preview_and_stale_target_cannot_be_adopted` | 只改变 preview 状态，正文与版本不变 |
| preview 过期 | 上述协调器测试与 `test_stale_preview_is_invalidated_without_snapshot_or_content_write` | 目标栏目 hash 变化后标记 invalidated，零正文写入、零快照 |
| 明确采用 | `test_adoption_snapshots_before_mutating_current_content` 与 Repository 事务测试 | 同事务先写 `pre_ai_adopt` 快照，再更新正文/revision，最后标记 adopted |
| 凭据隔离 | `test_credentials.py`、`test_ai_settings.py` | 仅 Windows 本机持久化后端可用；Key 不进入 DTO repr、SQLite 或错误文本 |
| 可选增强 | `tests/desktop` 全回归 | 未配置 AI 时手工设置、保存、重启读取和单日 Word 均不受阻塞 |

## 3. `0001 -> 0002_desktop_ai` 迁移保护

- `0001_desktop_initial.py` SHA-256 保持
  `a1d55d374ffa6144d2e772f2f2b7cc33a5e76e94c0c5d22b02fc13e41db844e5`，没有修改历史迁移。
- 空数据库直接升级到 `0002_desktop_ai`，重复升级幂等；新增 `ai_configuration`、
  `prompt_overrides` 和 `ai_previews`，约束、外键与索引均具名。
- 真实 `0001` 数据库升级前使用 SQLite backup API 生成随机命名的独立保护副本，校验
  `integrity_check`、`foreign_key_check` 和副本仍为 `0001_desktop_initial` 后，才开始 Alembic
  升级；活动库升级后既有虚构教师数据保持不变。
- 保护副本目录不可创建时抛出 `migration.protective_backup_failed`，活动库版本仍为 `0001`、
  既有数据保持不变、AI 表不存在；Bootstrap 对外稳定映射为 `startup.backup_failed`，不进入
  可写主窗口。
- 运行中 operation 只存在进程内；SQLite 只保存非敏感配置、提示词 override 与通过结构校验的
  preview。API Key 的端到端替身测试确认只进入凭据存储。

## 4. 已执行验证

| 命令 | 结果 |
|---|---|
| `uv run pytest --collect-only` | 836 项收集成功，无导入、fixture 或环境错误 |
| T035–T039 | 34 passed |
| AI 设置 + 迁移/Repository/Bootstrap 专项 | 17 passed；与上项合计 51 passed |
| `uv run pytest tests/desktop -q` | 107 passed；覆盖 Slice 1 与 Slice 2A |
| `uv run ruff format --check .` | 通过，388 files already formatted |
| `uv run ruff check .` | 通过 |
| `uv run pyright` | 通过，0 errors / 0 warnings |
| `graphify update .` | 代码增量抽取成功；新增/修改实现与测试均进入图谱 |
| `graphify extract . --backend openai` | OpenAI 兼容后端语义抽取成功；无需对抽取降级 |
| Graphify 社区命名 | OpenAI 返回 5 个空的不可解析结果并在 300 秒总时限结束；随后 DeepSeek 成功完成社区命名，未调用 `luna_worker` |
| `graph.html` | 图谱超过 5000 节点，Graphify 按可视化上限明确跳过 HTML；未绕过限制 |
| T044 Graphify 定向查询 | 命中 `0002_desktop_ai.py`、升级保护成功/失败测试、`BootstrapService`、`upgrade_database()` 与 data-model 4.10 |
| `graphify diagnose multigraph --graph graphify-out/graph.json --undirected` | 缺失端点、悬空边、自环、精确重复边和折叠边均为 0 |

仓库级 `uv run pytest -q` 也已实际执行：550 passed、1 failed、282 errors。失败与错误均来自历史
Cloud 测试在 fixture/健康检查阶段无法连接本机 PostgreSQL/Redis（PostgreSQL 目标为回环地址
`127.0.0.1:15432`）；Docker API 在当前环境同样无访问权限，不能启动该历史依赖。这是环境
门禁，不是本次桌面 RED 或桌面回归失败；桌面范围 107 项独立通过。

## 5. 本地结论与停止边界

T041–T048 行为、迁移保护、替身矩阵、桌面回归、静态门禁与 Graphify 检查均已在本地完成。
本文件不代替固定提交 Review、远端 CI、Windows 实机或 `main` 集成证据。
