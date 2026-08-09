# 桌面应用服务契约

## 1. 目的

本契约冻结 Qt UI 与桌面应用核心之间的边界。方法名是计划级接口，不是要求预建全部类；正式
实现按用户故事建立最小垂直切片。

## 2. 依赖规则

- UI 可以导入 `application.dto` 和应用服务，不得导入 ORM model、Repository、Alembic、
  httpx、boto3、keyring 或 python-docx。
- 应用服务可以导入 domain 和基础设施端口；事务与快照由应用服务控制。
- domain 不导入 PySide6 或任何基础设施依赖。
- 后台函数接收冻结 dataclass/Pydantic DTO，不接收 Widget、Session 或可变 ViewModel。
- 所有失败返回稳定 `error_code` + 简体中文摘要；异常和日志不得含正文、Key、口令或 token。

## 3. 共享结果类型

```text
CommandResult[T]
  ok: bool
  value: T | null
  error_code: str | null
  message: str
  retryable: bool

TaskProgress
  operation_id: UUID
  phase: str
  completed: int
  total: int | null
  message: str

CancellationToken
  cancel_requested: bool
```

成功状态通常通过固定状态区显示，不弹阻断对话框；数据损坏、覆盖确认和恢复确认可以使用模态
对话框。

## 4. `BootstrapService`

### `start() -> StartupState`

顺序执行路径检查、数据库检查、每日备份判定、必要的升级前备份、Alembic 升级、完整性复核
和最小设置检查。

```text
StartupState
  data_root: Path
  schema_revision: str
  first_run: bool
  setup_complete: bool
  daily_backup: not_due | succeeded | failed
  warnings: tuple[UserWarning, ...]
```

错误：`startup.path_unavailable`、`startup.database_read_only`、`startup.database_corrupt`、
`startup.backup_failed`、`startup.migration_failed`、`startup.future_schema`。上述错误均不得进入
可写主窗口。

## 5. `SettingsService`

```text
get_settings() -> SettingsView
save_profile(teacher_display_name, theme) -> SettingsView
save_kindergarten(name) -> KindergartenView
create_or_update_semester(...) -> SemesterView
set_current_semester(semester_id) -> SemesterView
create_or_update_class(...) -> ClassView
set_class_areas(class_id, indoor, outdoor) -> ClassView
```

保存每个聚合使用一个事务。设置服务不管理账号、角色、邀请、多园或 Cloud 配置。

## 6. `CalendarService`

```text
evaluate(date, semester_id) -> CalendarEvaluation
set_override(date, workday | non_workday, note?) -> CalendarEvaluation
clear_override(date) -> CalendarEvaluation
teaching_week(date, semester_id) -> TeachingWeek
```

```text
CalendarEvaluation
  date: date
  semester_status: inside | outside
  workday_status: workday | non_workday | unknown
  source: manual | chinesecalendar | unavailable
  warnings: tuple[str, ...]
```

人工覆盖优先。chinesecalendar 数据覆盖外返回 unknown，不联网猜测。所有异常只软提示，不阻止
单日保存；批量导出按 Word 契约跳过已确认的 non_workday，unknown 随已有教案纳入并警告。

## 7. `LessonPlanService`

```text
open_or_create(class_id, plan_date, semester_id) -> LessonPlanEditorState
autosave(plan_id, base_revision, content) -> SaveResult
save_version(plan_id, base_revision, content, description?) -> SaveResult
archive(plan_id) -> LessonPlanEditorState
unarchive(plan_id) -> LessonPlanEditorState
list_versions(plan_id) -> tuple[LessonPlanVersionView, ...]
restore_version(plan_id, version_id) -> LessonPlanEditorState
find(filter) -> tuple[LessonPlanSummary, ...]
```

- `autosave` 在停止输入约 3 秒后触发，只更新当前正文并递增 revision，不创建版本。
- 同一窗口若 `base_revision` 已过期，返回 `plan.stale_editor_state`，UI 必须重新协调未保存内容；
  这不是多人并发协议。
- `save_version` 在一个事务中保存传入正文并创建 `explicit_save` 快照。
- 归档、恢复归档和历史恢复先保存操作前快照，再改变当前状态。
- 归档状态拒绝正文保存和 AI 采用，错误码 `plan.archived_read_only`。
- 日期软提示随 EditorState 返回，不把校验散落在 Widget。

## 8. `AiGenerationCoordinator`

```text
start_single(plan_id, section_code, teacher_context) -> OperationAccepted
start_batch(plan_id, teacher_context) -> OperationAccepted
start_reflection(plan_id, teacher_context) -> OperationAccepted
cancel(operation_id) -> CommandResult[None]
adopt(preview_id) -> LessonPlanEditorState
reject(preview_id) -> PreviewView
```

- 同时只有一个 `running` operation；重复发起返回 `ai.operation_in_progress`。
- batch 是一个前台 operation、四个独立栏目结果；实现可以顺序请求，失败栏目不撤销成功预览。
- 每个子请求最多自动重试两次，只针对稳定 retryable 错误。
- worker 接收冻结输入、目标栏目 hash、Schema code 和凭据值；凭据只驻留调用内存。
- 完成后先结构校验，再写 `ready` preview；不会自动更新正文。
- adopt 在数据库事务中重检目标栏目 hash，过期返回 `ai.preview_stale` 并标记 invalidated。
- 关闭应用请求取消并丢弃迟到结果；启动时不扫描/恢复未完成任务。

Endpoint 策略冻结为：禁止 URL userinfo 和重定向；非回环地址必须 HTTPS 并正常验证证书；
`localhost/127.0.0.1/::1` 可显式使用 HTTP 以支持本机模型。不得直接复用 Cloud 公网 allowlist、
租户 allowlist 或 Worker DNS pinning 配置。

## 9. `AgentRuntime`

`AgentRuntime` 是 Application Layer 的单 Agent 深模块，不替代 `AiGenerationCoordinator`：
Slice 2A 继续提供现有结构化预览；Slice 2B 才增加 Context 与 READ/DRAFT Tool，Slice 3 之后
才增加确认 WRITE。

```text
start_turn(intent, context_request) -> OperationAccepted
cancel(operation_id) -> ToolResult[None]
confirm(confirmation) -> OperationAccepted       # 仅 Agent 写入阶段
reject(patch_id) -> ToolResult[None]
```

- Provider 只经 `AgentProviderPort` 返回文本/Tool call，不能直接访问业务或执行 Tool。
- 所有业务访问经过注册 Application Tool；Slice 2B 不存在 WRITE Tool。
- Context、ToolResult、Patch、Confirmation 和会话只在内存短期存在，不是第二业务权威。
- WRITE 必须绑定教师看到的精确 Patch，并在一个新短事务内完成重检、快照、正文、revision 与
  最小审计；失败全回滚且不自动重试。

完整值对象、Permission、Provider、确认、线程/事务和非目标见
[`agent-runtime.md`](agent-runtime.md)。

## 10. `ExportService`

```text
prepare_single(plan_id) -> DailyPlanExportSnapshot
preview_batch(semester_id, class_id, start_date, end_date) -> BatchExportPreview
export_single(snapshot, destination, cancellation) -> ExportResult
export_batch(preview, destination, cancellation, progress) -> ExportResult
```

详细日期选择、字段、原子发布和失败语义见 [`word-export.md`](word-export.md)。准备阶段读取并
冻结业务数据；后台渲染不重新查询变化中的教案。

## 11. `BackupService`

```text
create_daily_if_due() -> BackupResult
create_manual(destination, passphrase?) -> BackupResult
upload(backup_id, target, cancellation, progress) -> BackupResult
list_local() -> tuple[BackupSummary, ...]
list_remote(target, cancellation) -> tuple[BackupSummary, ...]
inspect(source, passphrase?) -> RestoreCandidate
restore(candidate, confirmation, cancellation, progress) -> RestoreResult
```

详细格式与恢复事务见 [`backup-package-v1.md`](backup-package-v1.md)。

## 12. Qt 运行时桥接

`ui.runtime` 是 Qt 专用适配层：

```text
submit(callable, frozen_input, cancellation_token)
  -> emits progress(TaskProgress)
  -> emits succeeded(CommandResult)
  -> emits failed(CommandResult)
  -> emits finished(operation_id)
```

- 信号接收者必须比较当前 `operation_id` 和页面上下文；页面已切换/关闭时丢弃 UI 更新。
- `cancel()` 只设置 token；网络/文件库无法立刻中断时，迟到结果仍不得被采用或发布。
- Word/备份在发布最终文件之前必须再次检查取消。
- 应用退出按“停止接受新任务 -> 请求取消 -> 等待有界时间 -> 关闭数据库”顺序执行。
- Agent 退出在请求取消前先使会话、Context、Patch 与 Confirmation 失效；Provider/Tool 迟到
  结果不能恢复确认或触发 WRITE。

## 13. 架构契约测试

- 扫描 `src/kindergarten_manager/ui`，禁止导入 `sqlalchemy`、`alembic`、`docx`、`httpx`、
  `boto3`、`keyring` 和 infrastructure database model。
- 扫描整个新命名空间，禁止导入 `apps.web`、`apps.api`、`apps.worker`、旧 identity/jobs 或
  PostgreSQL migration package。
- domain 包只能依赖标准库和明确的数据验证依赖，不得依赖 PySide6/SQLAlchemy。
- 任务替身证明：后台线程从不接收 Widget/Session；页面离开和取消后不采用结果。
- Agent 替身证明：Provider 不能绕过 Tool registry，READ/DRAFT 零写入，确认绑定精确 Patch，
  WRITE 全事务且会话结束/重启后没有长期业务记忆。
