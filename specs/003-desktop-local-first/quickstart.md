# 桌面首期实施后快速验收指南

> 本文是 Phase 1 设计产物，描述正式实现完成后必须可运行的验收步骤。本文本身不授权实现；
> 只有 `docs` 完整 SHA、引用该 SHA 的 Issue 与 `dev` T001 记录齐全后才能按授权切片执行。
> 当前只开放 Slice 1 RED，任何命令成功都不能证明未实现能力已经存在，也不能提前开始
> Agent Foundation。

## 1. 前置条件

- 已确认的 docs 完整提交 SHA 和引用该 SHA 的实现 Issue。
- `dev` 实现分支；不得从 Design 原型直接晋升。
- CPython 3.14.6、`uv`，Linux 开发机或 Windows x64 验收机。
- Windows 打包机另需 Visual Studio 2022 C++ Build Tools、`pyside6-deploy 6.11.1`、
  Nuitka 4.0 和 Inno Setup 7.0.2 x64。
- 所有示例只用虚构园所、教师、班级和教案，不配置真实付费 AI/WebDAV/S3。

## 2. 锁定安装与静态检查

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

预期：锁文件无改动；新 `kindergarten_manager` 命名空间不导入旧 Web/API/Worker、身份、Jobs
或 PostgreSQL 迁移模块。

## 3. 自动化测试分层

```bash
uv run pytest tests/desktop/unit
uv run pytest tests/desktop/application
uv run pytest tests/desktop/database
uv run pytest tests/desktop/contracts
uv run pytest tests/desktop/integration
QT_QPA_PLATFORM=offscreen uv run pytest tests/desktop/ui
uv run pytest
```

预期：

- 日历、教学周、结构化教案、AI hash/Schema 和 Word 字段映射纯规则通过。
- SQLite 使用临时文件，覆盖全新建库、迁移、FK/unique/check/immutable trigger 和损坏场景。
- AI、凭据、WebDAV、S3 全部使用替身，无外部网络。
- 完整测试不得把旧 Cloud 测试通过解释为桌面故事通过。

## 4. 首次启动与本地目录

开发启动：

```bash
uv run python -m kindergarten_manager
```

首次启动验收：

1. 断开网络，在没有现有数据目录的测试用户下启动。
2. 确认应用使用 `QStandardPaths.GenericDataLocation/cn.kindergartenmanager.desktop` 规则，
   安装/源码目录没有生成数据库、备份、日志或导出。
3. 输入虚构教师“测试教师”、园所“示例幼儿园”，创建秋季学期与“大一班”“中二班”。
4. 关闭再启动，确认设置、浅色/深色/跟随系统主题和当前班级保持。
5. 修改中文显示名的测试构建，确认仍解析到同一 ASCII 数据根。

失败矩阵：数据根只读、空间不足、零字节数据库、损坏数据库、未来 Alembic revision。预期均
停止写入并显示中文错误，不创建“已保存”假象。

## 5. P1 手工教案闭环

1. 在大一班选择学期内工作日，创建教案并逐字段编辑 01–05 栏及反思。
2. 停止输入约 3 秒；5 秒内固定状态区显示成功，版本列表没有新增。
3. 选择“保存版本”并填写说明；版本列表新增一个不可变快照。
4. 修改内容后恢复该版本；确认先创建恢复前快照，再恢复内容。
5. 归档后确认只读；恢复归档后继续编辑。
6. 切换班级、日期、上一周/下一周/本周，确认未保存内容不会静默丢失。
7. 在学期外、非工作日和 2027 年日期创建教案，确认只软提示；2027 日历来源为“待确认”。
8. 设置人工上课/不上课覆盖，确认其优先并可删除回到内置/未知判断。
9. 重启应用，确认最后一次成功保存内容完整。

## 6. Word 单日导出

1. 记录 `templates/teacherplan/teacherplan.docx` SHA-256。
2. 在当前日期选择“导出当天 Word”，目标路径包含中文和空格。
3. 检查输出标题、学期月份、班级、教师、周次、日期和所有结构化字段。
4. 用自动化检查表格数、行列、段落、run 字体/字号/颜色/换行。
5. 在 Windows Microsoft Word 中实际打开，确认版式无修复提示。
6. 再次核对源码模板 SHA 完全不变。

还要验证目标已存在、只读目录、磁盘满和 Word 持锁；旧目标必须保留，无残留临时成品。

## 7. Slice 2A：P2 可选 AI Provider 与结构化预览

未配置 AI：完整重复第 5–7 节，均须成功。

使用本地替身：

1. 从包含虚构教案的 `0001_desktop_initial` 数据库启动升级，确认先生成并验证本地
   `pre_migration` 保护副本，再到达 `0002_desktop_ai`；模拟备份失败时 Schema 和原数据不变。
2. 配置一个当前模型和虚构 Key；确认 SQLite/备份/日志中找不到 Key。
3. 单栏生成成功 -> 预览 -> 拒绝，正文与版本不变。
4. 单栏生成成功 -> 修改无关栏 -> 仍可采用；修改目标栏 -> preview stale，拒绝覆盖。
5. 采用有效预览，确认先创建采用前快照再更新正文。
6. 一键四栏使两个成功、一个结构错误重试后成功、一个最终失败；成功预览保留，失败栏可单独
   重试，原正文不变。
7. 发起任务后重复发起，返回单任务提示；取消或关闭应用，迟到结果不写数据库。
8. 重启应用，不恢复未完成任务。

Endpoint 验收：回环 HTTP 替身允许；非回环 HTTP、URL userinfo 和重定向拒绝；非回环 HTTPS
正常验证证书。

## 8. Slice 2B：Agent Foundation（READ/DRAFT only）

使用 Scripted Provider，不访问真实网络：

1. 请求读取当前教案、日历与班级区域；核对 Provider 只收到白名单字段、实体 revision 和当前
   意图所需正文，不收到 Key、绝对路径、无关班级或完整历史。
2. 请求生成栏目/反思修改建议；确认 Runtime 返回规范 `PlanPatch` 和字段级 before/after，
   SQLite 正文、版本数、AI preview 和审计行数全部不变。
3. 让 Provider 请求未知 Tool、伪造 Permission、WRITE Tool、额外参数、越界 ID 和任意文件/
   URL/代码能力；全部返回稳定拒绝且不做近似匹配。
4. 让 Provider 执行一次与多次合法 READ/DRAFT Tool call，再覆盖循环上限、超长响应、结构错误、
   Provider 拒绝、取消和页面切换后的迟到结果丢弃。
5. 在第一个 turn 运行时发起第二个 turn，确认被拒绝；核对没有子 Agent 或并行 Tool call。
6. 结束会话并重启应用；确认 conversation、Context、ToolResult、Patch、Confirmation、embedding
   和 Provider thread 均未恢复或写入 SQLite/备份/日志。
7. 尝试以自然语言要求“直接修改”或“以后都允许”，确认 Slice 2B 没有 WRITE Tool，零写入。

## 9. Slice 3：P3 备份与恢复

### 9.1 本地

1. 当日首次成功打开创建 daily，第二次不重复；制造 31 日样本后只保留最近 30 份 daily。
2. 检查包中只有 manifest 和一致性 SQLite，不含任何凭据。
3. 模拟 WAL/事务写入（即使首期使用 rollback journal，此测试保护未来变化），确认 backup API
   快照能通过 integrity/FK 和业务计数。
4. 执行迁移前/恢复前备份，确认不被 daily 轮换立即删除。

### 9.2 加密与远程替身

1. 用固定测试口令生成可携带包，使用黄金向量验证 header、scrypt 参数和 AES-GCM。
2. 篡改 header/AAD/密文/tag、截断、错口令、恶意 KDF 参数、ZIP 路径穿越/压缩炸弹，全部拒绝。
3. WebDAV/S3 替身分别覆盖成功、超时、长度不符和中断；远程对象只能收到加密包。
4. 在持续远程失败时执行 100 次本地编辑保存，全部成功。

### 9.3 恢复

1. 在新测试用户中显式选择具体备份，不让应用猜“最新”。
2. 验证当前库先产生 pre_restore，候选库在 staging 校验/迁移后才替换。
3. 验证旧 Schema 能迁移恢复，未来 Schema 明确拒绝。
4. 在下载、解密、迁移、替换和替换后首次打开各阶段强制退出，当前数据或保护性备份始终可
   恢复。

## 10. Agent 写入阶段

仅在 Slice 3 完整通过后启用测试用 WRITE Tool：

1. 生成只修改一个已注册教案字段的 Patch；检查 UI 展示 Tool、目标、逐字段 before/after、
   warning、base revision 以及将创建快照和最小审计的影响。
2. 不确认、拒绝、修改 Patch、确认超时、错 patch hash/target/turn、复用 nonce，逐项确认正文、
   revision、版本和 audit 均无变化。
3. 确认后先用手工保存改变 revision，再提交旧确认；必须返回 stale 并要求重新生成/再次确认。
4. 对有效确认，核对只修改展示字段，并在同一事务中创建操作前版本、递增 revision、追加一条
   不含正文/Prompt/Provider 原文的不可变 audit。
5. 注入领域校验、版本插入、正文更新、audit 插入和 commit 异常，确认全部回滚；未知 commit
   通过 action ID/revision 对账，不自动重放 WRITE。
6. 在教师确认后断开 Provider 网络，确认本地 WRITE 仍可只消费规范 Patch 完成；事务内没有
   Provider、Word、备份或 UI 调用。
7. 重启应用后确认 Patch/Confirmation 不恢复，audit 不能被用作对话或偏好记忆。

Level 3 Workflow、多 Agent、定时/后台自主运行和无人值守 WRITE 不属于本指南；出现相关入口
即验收失败。

## 11. Word 批量导出

### 11.1 实施前 spike 门禁

用相同模板构造 3 天文档，专门验证 body、section、header/footer、关系 ID、分页和 Word 实机
打开。Spike 失败时不得进入完整实现，须回到固定批量模板或经依赖审查的专用合并库。

### 11.2 业务验收

1. 准备一个包含已有教案、周末、法定节假日、人工工作日、人工非工作日、未知年份和空缺日
   的同一学期日期范围。
2. 打开批量预览，核对纳入数量和每个跳过日期/原因；未知日历但已有教案应纳入并警告，不得
   当作非工作日跳过。
3. 确认导出，观察逐日进度；输出必须只有一个 DOCX、日期升序、每天完整模板并从新页开始。
4. 将预览与实际日期逐项比较，必须 100% 一致。
5. 分别在第一天、中间和发布前取消；最终文件不得出现，已有同名文件不得改变。
6. 尝试跨学期和全空范围，确认导出不能开始。

## 12. Windows UI 与 DPI

在干净 Windows x64 VM 或真机：

- 1366x768，125%/150% 缩放；浅色、深色、跟随系统分别执行 P1 核心流程。
- 检查主要操作无水平滚动、焦点轮廓可见、状态不只靠颜色、主题切换不丢未保存内容。
- 检查原生文件对话框、中文/空格/长路径、操作系统凭据写入/读回/删除。
- 检查 Windows backend 不可用时 fail closed；不得出现文件或 SQLite 明文回退。

Linux offscreen 截图或 Widget 构造通过不能替代本节。

## 13. Windows standalone 与安装器

计划中的确定性构建入口应等价于：

```powershell
uv sync --locked
pyside6-deploy src/kindergarten_manager/__main__.py --config-file packaging/windows/pysidedeploy.spec
ISCC.exe packaging/windows/installer.iss
```

验收：

1. 构建使用 CPython 3.14.6 x64、MSVC 2022、Nuitka 4.0，模式为 standalone，不是 onefile。
2. 在没有 Python/Qt 的干净 Windows 用户上 per-user 安装并启动。
3. 检查 Qt platform/image/SVG/TLS 插件、SQLite、模板、chinesecalendar 和 keyring backend 均
   被收集；生成单日 Word 和本地备份。
4. 从旧版本安装器升级，应用先完成 pre_migration 再升级 Schema；安装器本身不碰数据库。
5. 卸载后数据根仍存在；重装可重新打开数据。
6. 产出安装 EXE、大小、SHA-256、完整 Git SHA、SBOM 和第三方许可证清单。
7. 未签名包接受 SmartScreen 现实，不显示任何关闭安全软件/绕过提示。

## 14. 后期 MSIX 兼容性（非首期完成门禁）

以同一 standalone payload 构造 full-trust x64 MSIX，验证：Store identity 与应用稳定 ID 分离；
EXE/MSIX 读取同一显式数据根；渠道切换、并存单实例、升级、卸载任一渠道均不丢数据。首次可用
MSIX Packaging Tool 做兼容验证，稳定流水线应从 payload + manifest 确定性构建。

## 15. 完整质量门禁

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

另附 Windows 人工证据：操作系统/缩放、安装包 SHA、构建 Git SHA、首次启动、升级/卸载保留、
Word 实机打开、凭据、备份恢复和无幼儿个人信息检查。只有实际观察到的结果才能标记通过。
