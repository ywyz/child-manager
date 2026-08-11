# Word 导出契约

## 1. 共同不变量

- 唯一模板源是 `templates/teacherplan/teacherplan.docx`；构建前后和运行时均校验冻结 SHA-256。
- 每次导出从模板副本开始，禁止原地修改、重建近似表格或把模板保存回源码路径。
- 单日和批量共用同一字段映射和 `render_day(snapshot)` 核心。
- 输出只含虚构/真实业务输入，不从代码硬编码园所、班级或教师名字。
- 首期不提供 PDF；下一期 AI 新增集体活动环节到来前，红字标记能力可保留测试但不显示未实现
  入口。

## 2. 冻结输入

```text
DailyPlanExportSnapshot
  plan_id: int
  content_revision: int
  plan_date: date
  teaching_week_text: str
  activity_date_text: str
  semester_name: str
  semester_start_date: date
  semester_end_date: date
  kindergarten_name: str
  class_name: str
  age_group: str
  author_name: str
  content: PlanContentV1
  content_sha256: str
```

Snapshot 在应用服务事务内创建。后台渲染只读 snapshot；渲染期间正文变化不会改变本次结果。

## 3. 单日导出

```text
prepare_single(plan_id)
  -> snapshot 或 plan.not_found

export_single(snapshot, destination)
  -> ExportResult(destination, exported_dates=(date,), skipped=())
```

- 允许导出归档教案和未完整教案；规格未授权沿用旧 B/S “五栏不完整二次确认”门禁。
- UI 默认文件名清洗后为 `一日活动计划-班级-YYYY-MM-DD.docx`，最终路径由教师确认。
- 目标已存在时，必须在启动后台任务前由教师明确确认覆盖。

## 4. 批量预览

请求：

```text
BatchExportRequest
  semester_id: int
  class_id: int
  start_date: date
  end_date: date
```

拒绝整个请求：

- start > end：`export.invalid_range`
- 起止任一日期不在所选同一学期：`export.cross_semester_range`
- 范围没有任何可导出日期：`export.empty_range`

对范围内每个自然日按以下优先级分类：

1. 人工覆盖为 `non_workday` -> 跳过 `manual_non_workday`。
2. 无人工覆盖且 chinesecalendar 为周末/节假日 -> 跳过 `calendar_non_workday`。
3. 没有当前教案 -> 跳过 `plan_missing`。
4. 工作日且有教案（归档或未归档）-> 纳入。
5. 无可靠日历结论但有教案 -> 纳入，并在 preview 标记 `calendar_unknown` 警告；未知只软提示，
   不得被扩张为规格未授权的导出阻断。

人工覆盖为 `workday` 可覆盖周末/节假日。纳入日期严格升序，不限制天数。

```text
BatchExportPreview
  preview_id: UUID
  semester_id: int
  class_id: int
  range: inclusive date range
  included: tuple[DailyPlanExportSnapshot, ...]
  skipped: tuple[SkippedDate, ...]
  warnings: tuple[ExportWarning, ...]
  created_at_utc: datetime
```

UI 必须展示纳入数量、每个跳过日期和原因。教师确认后传递此冻结 preview；不在后台重新计算
“最新”日期清单。

## 5. 批量 DOCX 结构

- 最终只生成一个 `.docx`。
- 每个 included day 都使用完整模板标题、上下文和完整表格。
- 第一日直接位于文档开头；第二日起在该日完整模板内容前插入显式分页符。
- 采用相同模板生成/复制 body XML，不把独立 `.docx` ZIP 字节拼接。
- 每日字段映射、段落、run、字体、字号、颜色、行距和换行与单日渲染完全相同。
- 文档属性不得包含 API Key、恢复口令、远程 Endpoint userinfo 或完整正文摘要。

## 6. 进度、取消与原子发布

```text
ExportProgress
  phase: preparing | rendering | validating | publishing
  completed_days: int
  total_days: int
```

1. 在最终目标的同一目录创建隐藏/随机临时文件。
2. 每日渲染前后检查 cancellation token；取消后关闭文档并删除临时文件。
3. 保存临时 DOCX，重新打开并运行结构/日期/表格数量校验。
4. flush + fsync 文件；必要时同步目录元数据。
5. 再次检查取消；用 `os.replace()` 发布最终文件。
6. 发布失败或目标被 Word/杀毒软件锁定，保留旧最终文件、删除临时文件并返回可理解错误。

稳定错误码：`export.cancelled`、`export.template_changed`、`export.render_failed`、
`export.validation_failed`、`export.destination_locked`、`export.no_space`、
`export.publish_failed`。

## 7. 验证矩阵

- 模板源码 SHA 在导出前后完全相同。
- 单日和批量中同一天的标题、字段文本、表格/行列数、段落和 run 样式等价。
- 批量日期顺序、跳过原因与 preview 100% 一致，每日从新页开始。
- 中文、空格、长路径；只读目录、磁盘满、已有文件、Word 持锁。
- 在第 1/中间/最后一日取消或抛错，最终文件不存在或旧文件原样保留，无残留成功假象。
- Microsoft Word Windows 实机打开；LibreOffice/Linux 检查不能替代该证据。
