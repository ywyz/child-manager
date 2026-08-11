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
| 四栏部分失败 | `test_batch_keeps_successful_previews_when_one_section_fails`、`test_retry_failed_section_preserves_other_successful_previews` | 成功栏目保留且失败栏单独重试时仍可采用，失败栏目独立记录稳定错误码 |
| retryable 重试 | `test_retryable_failure_is_retried_at_most_twice` | 首次调用加最多两次重试，共 3 次；无真实网络 |
| 混合失败预算 | `test_transport_and_structure_errors_share_one_three_call_budget` | 传输、供应商响应与结构校验共用同一 3 次调用预算，不发生嵌套重试放大 |
| 结构失败 | `test_ai_domain.py` 的 missing/wrong-type/unknown-field 分类 | 无效结构被稳定分类，不写正文 |
| 取消与退出 | `test_cancel_and_close_discard_late_results` | 请求取消后释放单任务槽位，取消/退出后的迟到结果丢弃 |
| 页面切换迟到 | `test_page_change_invalidates_epoch_and_discards_late_signal` | page epoch 变化后不显示迟到 preview |
| 明确拒绝 | `test_reject_changes_only_preview_and_stale_target_cannot_be_adopted` | 只改变 preview 状态，正文与版本不变 |
| preview 过期 | 上述协调器测试与 `test_stale_preview_is_invalidated_without_snapshot_or_content_write` | 目标栏目 hash 变化后标记 invalidated，零正文写入、零快照 |
| 明确采用 | `test_adoption_snapshots_before_mutating_current_content`、`test_ai_result_merge_preserves_teacher_owned_section_fields` 与 Repository 事务测试 | 同事务先写 `pre_ai_adopt` 快照，再合并结果并保留教师维护的区域字段、更新正文/revision，最后标记 adopted |
| Provider 冻结 | `test_submit_freezes_configuration_credential_and_prompt_before_background_work` | 配置、Key 与提示词在提交后台任务前一次性读取；后台线程只使用不可变且 secret 不进入 repr 的冻结 DTO |
| 真实 UI 接线 | `test_actual_panel_wires_per_section_preview_adopt_and_retry` 与教案页回归 | 教案页实际渲染逐栏/四栏入口、预览、采用、拒绝、重试和取消控件；生成前先保存当前可见编辑，离页停止轮询并取消运行任务 |
| 凭据隔离 | `test_credentials.py`、`test_ai_settings.py` | 只接受 keyring 25.7.0 的真实 `Windows WinVaultKeyring`，并固定 `persist = "local machine"`；Key 不进入 DTO repr、SQLite 或错误文本 |
| 设置原子性 | `test_application_service_owns_ai_settings_transaction_scope`、`test_ai_settings_aggregate_rolls_back_configuration_and_prompts_together` | Application service 显式开启同一 SQLite 事务保存配置与五项提示词覆盖；失败整体回滚 |
| 可选增强 | `tests/desktop` 全回归 | 未配置 AI 时手工设置、保存、重启读取和单日 Word 均不受阻塞 |

## 3. `0001 -> 0002_desktop_ai` 迁移保护

- `0001_desktop_initial.py` SHA-256 保持
  `a1d55d374ffa6144d2e772f2f2b7cc33a5e76e94c0c5d22b02fc13e41db844e5`，没有修改历史迁移。
- 空数据库直接升级到 `0002_desktop_ai`，重复升级幂等；新增 `ai_configuration`、
  `prompt_overrides` 和 `ai_previews`，约束、外键与索引均具名。
- 真实 `0001` 数据库升级前使用 SQLite backup API 生成随机命名的独立保护副本，校验
  `integrity_check`、`foreign_key_check` 和副本仍为 `0001_desktop_initial` 后，才开始 Alembic
  升级；保护副本重命名前后还必须通过 SHA-256 一致性校验，活动库升级后既有虚构教师数据
  保持不变。
- 保护副本目录不可创建时抛出 `migration.protective_backup_failed`，活动库版本仍为 `0001`、
  既有数据保持不变、AI 表不存在；Bootstrap 对外稳定映射为 `startup.backup_failed`，不进入
  可写主窗口。
- 保护副本 SHA-256 校验不一致时删除 partial 与最终副本并抛出同一稳定错误，活动库仍停在
  `0001`，不会开始 Alembic 升级。
- 运行中 operation 只存在进程内；SQLite 只保存非敏感配置、提示词 override 与通过结构校验的
  preview。API Key 的端到端替身测试确认只进入凭据存储。

## 4. 已执行验证

| 命令 | 结果 |
|---|---|
| `uv run pytest --collect-only -q` | 845 项收集成功，无导入、fixture 或环境错误 |
| T035–T039 | 38 passed |
| AI Runtime/设置 + 迁移/Repository/Bootstrap 专项 | 21 passed；与上项合计 59 passed |
| `uv run pytest -q tests/desktop` | 116 passed；覆盖 Slice 1 与 Slice 2A |
| `uv run ruff format --check .` | 通过，389 files already formatted |
| `uv run ruff check .` | 通过 |
| `uv run pyright` | 通过，0 errors / 0 warnings |
| `graphify update .` | 代码增量抽取成功，更新阶段得到 5351 nodes / 15421 edges |
| `graphify extract` 降级链 | 最终验收文档语义抽取中，OpenAI 兼容后端 300 秒无输出后超时；DeepSeek 成功重抽取 15 个代码文件与 1 个验收文档，未调用 `luna_worker` |
| Graphify 社区命名 | OpenAI 对最后一批 36 个社区返回空的不可解析结果；虽进程退出码为 0，仍按语义失败处理。随后 DeepSeek 成功完成最终 336 个社区命名，未调用 `luna_worker` |
| `graph.html` | 图谱超过 5000 节点，Graphify 按可视化上限明确跳过 HTML；未绕过限制 |
| T048 Graphify 定向查询 | 命中真实 `AiPreviewPanel`、AI 结果字段合并、Provider 冻结、设置事务边界及 T035–T048 验收节点；未用退出码替代语义覆盖检查 |
| `graphify diagnose multigraph --graph graphify-out/graph.json --undirected` | 最终 5391 nodes / 15093 edges；缺失端点、悬空边、自环、精确重复边和折叠边均为 0；另有 1 个既存历史审查文档推断节点 `FR-031` 被标记 unverified，与本次桌面实现节点无关 |

仓库级 `uv run pytest -q` 也已实际执行：550 passed、1 failed、282 errors。失败与错误均来自历史
Cloud 测试在 fixture/健康检查阶段无法连接本机 PostgreSQL/Redis（PostgreSQL 目标为回环地址
`127.0.0.1:15432`）；Docker API 在当前环境同样无访问权限，不能启动该历史依赖。这是环境
门禁，不是本次桌面 RED 或桌面回归失败；桌面范围 116 项独立通过。

## 5. 首次固定 GREEN Review 收口

首次固定候选 `d81791fd7651c0a8fa1692d647f1709759f7e9f1` 未推送。Standards/Spec
双轴 Review 发现的有效问题已在后续候选中逐项收口：

- 已校验 AI 结果现在显式保存顶层 `schema_version = 1`，采用正文时只移除该信封字段；
- 采用顺序、过期判定与失效落库由 Application service 在单一 Repository transaction 中控制；
- 取消结果复用共享 `CommandResult` / `OperationAccepted`，不再定义弱化重复 DTO；
- 设置配置与提示词覆盖原子保存，迁移保护副本增加 SHA-256 重命名前后校验；
- Qt 页面通过显式 `DesktopServices` 接口接入真实逐栏预览面板，不再用 `getattr`/`Any` 探测；
- Windows backend 名称与 keyring 25.7.0 实际值一致，过期 preview 在持久化事务内标记
  `invalidated`，结构错误与传输错误共用最多 3 次真实调用预算。

修复后固定 GREEN SHA、第二次双轴 Review、push、远端 CI 精确 `headSha` 与 Issue 验收状态仍按
后续独立门禁记录；首次候选不作为可推送结论。

第二个固定候选 `c5d40a4a3d5e93fcfb4fc5e2137f4465e302923d` 同样未推送。它已收口首次
Review 的九项问题，但第二次 Review 又发现真实 UI/事务边界的剩余偏差；后续候选继续修正：

- 失败栏单独重试不再清空其他成功预览；
- 生成前先保存当前可见编辑，避免采用后重载 SQLite 时丢失教师未保存内容；
- 离开教案页会停止轮询并取消运行任务，迟到结果由 operation discard 边界拒绝；
- AI 栏目结果改为字段合并，区域游戏保留教师维护的 `areas`；
- Provider 配置、Key 和提示词在提交后台线程前冻结；
- AI 设置事务改由 Application service 明确开启，Repository transaction 只提供持久化机制；
- 删除未接入真实 UI 的重复 `AiPreviewFlow` 状态机。

第二个候选也不作为可推送结论；只有上述修复后的新固定 SHA 再次通过双轴 Review 才能进入
push 门禁。

## 6. 本地结论与停止边界

T041–T048 行为、迁移保护、替身矩阵、桌面回归、静态门禁与 Graphify 检查均已在本地完成。
本文件不代替固定提交 Review、远端 CI、Windows 实机或 `main` 集成证据。
