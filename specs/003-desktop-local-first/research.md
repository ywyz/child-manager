# 桌面首期技术研究与决策

本文记录 Phase 0 的技术决策。版本事实核对日期为 2026-08-08；正式实现仍须由 `uv.lock`
固定完整依赖图，并在 Windows 构建机验证 wheel、许可证和打包结果。

## 1. Python、PySide6 与界面技术

**Decision**: 使用 CPython 3.14.6 x64 标准 GIL 构建、PySide6 6.11 系列（首次锁定 6.11.1）
和 Qt Widgets。项目约束 `>=3.14,<3.15`，但发布构建固定 3.14.6。首期不使用 QML，也不
引入第三方 Fluent 控件库。

**Rationale**: ADR-0012 与宪章已冻结该方向。PySide6 是 Qt 官方 Python 绑定；6.11.1 的
Windows x64 wheel 使用 `abi3`，元数据声明 Python `>=3.10,<3.15`，包含 Python 3.14。
Widgets 更适合首期高密度表单、长文本、键盘焦点和原生文件对话框，现有原型也只作为布局
验证，不形成运行时依赖。[PySide6 PyPI](https://pypi.org/project/PySide6/)、
[Qt for Python](https://doc.qt.io/qtforpython-6/)

**Alternatives considered**:

- PyQt6：许可取舍不如 PySide6 与当前分发计划匹配，ADR-0012 已否决。
- QML：增加第二套语言/运行时边界，首期没有动画或触控优先需求证明其必要。
- NiceGUI 封装桌面：仍引入本地 HTTP/浏览器渲染，违背重置目标。

发布前必须核对 PySide6/Qt 的 LGPL 动态库分发、版权声明与第三方许可证清单；构建产物不得
静态隐藏或删除用户依法需要的许可材料。

## 2. SQLite、SQLAlchemy 与 Alembic

**Decision**: 使用 CPython 自带 `sqlite3` 作为驱动，SQLAlchemy 2.0 系列（首次锁定
2.0.51）作为同步 ORM/事务层，Alembic 1.19 系列（首次锁定 1.19.0）建立全新 SQLite
迁移链。运行时不安装 `pysqlite3`、SQLCipher 或异步 SQLite 驱动。

**Rationale**: SQLite 无需单独服务，符合单机唯一权威。SQLAlchemy 2.0.51 有 CPython 3.14
Windows wheel；Alembic 1.19.0 声明支持 Python 3.14。SQLite 对多种 `ALTER TABLE` 操作需
“move and copy”，因此 `env.py` 固定 `render_as_batch=True`、显式命名约束并在线迁移。
[SQLAlchemy PyPI](https://pypi.org/project/SQLAlchemy/)、
[Alembic PyPI](https://pypi.org/project/alembic/)、
[Alembic SQLite batch migrations](https://alembic.sqlalchemy.org/en/latest/batch.html)

数据库运行策略冻结为：

- 每个连接 `PRAGMA foreign_keys=ON`、`busy_timeout=5000`、`synchronous=FULL`；首期保持
  SQLite 默认 rollback journal (`journal_mode=DELETE`)。单进程短事务无需 WAL，减少 checkpoint
  和伴随文件的备份/恢复面。
- 应用层串行化写操作；每个线程独立创建/关闭 Session，不关闭 `check_same_thread` 来共享
  同一连接。
- 日期存 `YYYY-MM-DD` 文本，UTC 时间存 Unix epoch milliseconds，结构化教案存带版本号的
  规范 JSON；不依赖 SQLite 隐式时区或 JSON 扩展。
- 首次建库和已有库升级都走 Alembic。旧 PostgreSQL revision 和数据不进入新链。

**Alternatives considered**:

- 直接 `sqlite3` 全手写 SQL：依赖更少，但会重复事务、映射和迁移边界，且降低旧纯领域模型
  的可测试性。
- 复用 PostgreSQL 迁移：包含方言、租户、组合外键和队列状态，不是 SQLite 的合法基线。
- SQLCipher：增加原生打包和密钥恢复复杂度；首期已禁止幼儿个人信息，秘密另存凭据库，
  完整备份另做认证加密。若未来引入敏感个人数据，必须重新 Design。

`chinesecalendar 1.11.0` 当前数据只覆盖 2004–2026，且 PyPI 元数据尚未声明 Python 3.14；
实现前必须在 3.14.6 专项导入/边界测试，2027 及以后在未升级经核验数据前统一返回“待确认”，
人工覆盖仍可用，不调用旧 Timor 在线 API。

## 3. 数据目录与资源定位

**Decision**: 用 Qt `QStandardPaths.GenericDataLocation` 解析系统本地持久数据目录，再固定
附加 `cn.kindergartenmanager.desktop`；数据库、备份、staging、cache 和日志使用其下独立
子目录。用户导出默认打开 `DocumentsLocation`。模板在构建时由仓库唯一源文件按固定哈希
复制进只读发布载荷。

**Rationale**: Qt 在 Windows 将 `GenericDataLocation` 映射到本地应用数据根。显式 ASCII
子目录避免中文显示名或 Qt application name 变化改变权威库位置，并为未来 full-trust MSIX
与 Inno EXE 约定同一路径；仍须单独验收渠道切换，不能假设 package identity 天然共享。
[QStandardPaths](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QStandardPaths.html)

**Alternatives considered**:

- 手拼 `%LOCALAPPDATA%`/`C:\Users`：用户重定向和跨平台开发下不可靠。
- 让用户每次选数据库：会制造副本、网盘直接打开和并发风险。
- 把模板复制成第二个源码文件：产生两个事实来源；构建复制和哈希验证更清楚。

## 4. 线程、任务和取消

**Decision**: Qt 主线程只渲染 UI。AI、远程备份和慢 Word 导出通过 Qt 线程池运行，输入先
冻结为不可变 DTO；任务通过信号返回不可变结果。AI 同时只允许一个进程内任务，关闭应用后
不恢复。数据库连接和 Widget 均不跨线程传递。

**Rationale**: 这满足界面响应和单任务约束，同时避免把旧 Dramatiq/Redis 权威状态搬进
桌面。导出的大部分数据可以在主事务中冻结，后台只处理 CPU/文件工作；备份线程使用独立
SQLite backup 连接。

**Alternatives considered**:

- `asyncio` 驱动全应用：Qt 事件循环集成增加复杂度，首期没有高并发网络需求。
- 独立 Worker/Redis：违背单进程和重启不恢复 AI 的决策。
- 后台线程直接访问 Widget/共享 Session：线程不安全且难以证明取消后不采用过期结果。

## 5. 模块边界

**Decision**: 冻结 `ui -> application -> domain` 单向依赖。基础设施实现应用层所需的窄端口，
由 `app.py` 装配。Repository 使用具体 SQLite 实现；仅 AI、Word、凭据和远程备份定义端口，
因为它们有第二实现或测试替身。

**Rationale**: 该结构把事务、文件和异步有效性规则放进深模块，同时避免为单一 SQLite 实现
机械创建接口/工厂。架构测试将禁止新命名空间导入旧 `apps.*`、identity、jobs 和 PostgreSQL
迁移。

**Alternatives considered**:

- 复刻 Web/API/Worker 三层：部署边界已不存在，只会制造进程内 RPC 形状。
- 每个类一个接口/依赖容器：首期只有一个实现，无法换来实际隔离收益。
- Widget 直接调用 Repository：保存、版本、备份与 AI 采用事务会散落在信号处理器中。

## 6. 受控 Agent Runtime

**Decision**: 采用一个位于 Application Layer 的 `AgentRuntime`。Runtime 通过窄
`AgentProviderPort` 使用现有 OpenAI 兼容配置，通过关闭 Schema 的 Tool registry 访问业务；
Slice 2B 只开放 READ/DRAFT，Slice 3 备份恢复完成后才以字段级 `PlanPatch`、逐次
`Confirmation`、最小不可变审计和短事务开放 WRITE。Context、对话、ToolResult、Patch 和确认
均为当前进程短期值，不形成长期业务记忆。

**Rationale**: Provider 是外部、不确定且可被 Prompt injection 影响的输入，不能成为权限或
事务主体。把上下文裁剪、Tool 调度、确认绑定和 stale 重检集中在一个深 Application module，
可以让 UI 与 Provider 共享同一套可执行不变量；Scripted Provider Adapter 又能在无网络测试中
覆盖完整 Tool loop。单机单教师没有多 Agent 或 Workflow 编排的并发收益。

线程/事务研究结论：

- 整个 Agent loop 在一个 Qt 后台 operation 中串行运行，不并行 Tool call，不创建子 Agent。
- 跨线程只传冻结 DTO；每个 Tool 自建/关闭 Session，Provider 等待与教师确认期间零事务。
- READ 返回带 revision 的裁剪投影；DRAFT 只产生规范 Patch，不写 preview 或业务表。
- WRITE 在确认后新开事务，重读并校验 Patch hash、revision、before hash 和领域不变量，再原子
  创建操作前版本、应用完整 Patch、更新 revision 和写最小 audit；WRITE 永不自动重试。
- Provider Adapter 只解析 Tool call，不执行 Tool；具体 SDK 类型不穿过 Provider seam。

**Alternatives considered**:

- Provider 直接调用应用服务/Repository：扩大不受信输出的权限，绕过字段级确认和事务重检。
- 通用 MCP/插件、shell/Python/SQL Tool：首期无真实扩展需求，无法证明数据、文件和网络范围。
- 持久化 Provider thread、conversation、向量记忆或教师画像：制造含正文的第二事实来源，扩大
  备份、删除、迁移和陈旧上下文风险。
- 多 Agent 或 Level 3 Workflow：引入委派、部分提交、恢复与审计组合，继续延后到新 ADR。

详细 Interface 见 [`contracts/agent-runtime.md`](contracts/agent-runtime.md)。

## 7. Word 单日与批量导出

**Decision**: python-docx 1.2 系列负责同一渲染核心。单日渲染一个完整模板副本；批量先冻结
预览清单，再按日期升序把每日完整模板 body 合并为一个文档，每日从新页开始。所有输出先写
目标同目录临时文件，重新打开验证后原子发布。

**Rationale**: python-docx 1.2.0 是稳定 MIT 依赖，现有 Renderer 已证明模板单元格映射可以
在不重建版式的前提下完成。批量只复制同一模板产生的 XML 节点，避免不同样式集之间的合并
问题；同目录临时文件使最终替换保持同一文件系统。
[python-docx PyPI](https://pypi.org/project/python-docx/)

**Alternatives considered**:

- 为批量导出生成 ZIP/多个 Word：直接违反 FR-031。
- 从零用代码重建表格：无法证明模板保真。
- 引入通用 DOCX 合并依赖：同一固定模板不需要额外依赖，且增加打包/兼容面。
- 在旧 Worker 中生成：引入 Job/PostgreSQL/Redis，违反桌面边界。

## 8. SQLite 备份与恢复

**Decision**: 使用 `sqlite3.Connection.backup()` 创建一致性 SQLite 快照，之后做
`PRAGMA integrity_check`、关键表计数和 SHA-256。升级前、恢复前和每日备份共享同一快照
核心，不直接复制打开中的 `.sqlite3`/WAL 文件。

**Rationale**: Python 3.14 文档说明 Connection backup 可在数据库被其他连接访问时工作，
比文件级复制更适合运行中的 SQLite 数据库。[Python sqlite3 backup](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup)

**Alternatives considered**:

- `shutil.copy2()` 主数据库：在事务或 journal 状态变化时可能得到不一致副本。
- SQL 文本 dump：恢复慢、类型/触发器/索引验证更复杂，不是完整原样快照。

## 9. 备份容器、加密与凭据

**Decision**: 自动本地保护备份是数据目录内的完整 `KMBACKUP1` 包，不包含任何秘密；可携带
和所有远程备份必须加密。恢复口令以 scrypt (`N=2^17,r=8,p=1`, 16-byte salt) 派生 32-byte
key，使用 AES-256-GCM、随机 12-byte nonce 和版本化 AAD 加密整个 ZIP 载荷。参数写入头部，
允许未来提高成本并继续读取旧版本。

**Rationale**: scrypt 是内存硬 KDF，RFC 推荐 `r=8,p=1` 并按设备调整 N；AESGCM 对密文和
AAD 同时认证，错误 key/nonce/AAD 或篡改会触发标签校验失败。首期参数需要在最低 Windows
目标机验证时间和内存，但不在运行时自动降低。
[cryptography Scrypt](https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#scrypt)、
[cryptography AESGCM](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM)

AI Key、WebDAV 密码/令牌、S3 Secret/Session Token 和可自动备份使用的恢复口令通过 keyring
25 系列访问操作系统凭据存储。Windows 只接受 Credential Locker 的 Windows backend，并固定
`local-machine` persistence；Linux 只接受 `keyring.backends.SecretService.Keyring`，使用当前
用户登录 keyring 并记录为 `local-user` persistence。若受支持后端不可用或锁定，则关闭对应
外部能力，绝不回退到明文文件、环境变量或 SQLite。
[keyring documentation](https://keyring.readthedocs.io/en/latest/)

**Alternatives considered**:

- 自创流密码/口令哈希协议：不可接受。
- 只用 ZIP 密码：算法与认证保证不足。
- 把恢复口令加密后存数据库：加密密钥仍需另处保存，且备份会携带密文凭据。
- DPAPI 直接调用：Windows 绑定更强，但无法支持 Ubuntu 的真实 AI 测试；keyring 提供窄
  跨平台边界并保持 Application Layer 与平台 SDK 隔离。

## 10. WebDAV 与 S3

**Decision**: WebDAV 适配器复用 httpx；S3 适配器使用锁定的 boto3。二者只实现上传、列举、
下载和删除不可变加密备份对象，配置/错误语义分别保留，不抽象成同步文件系统。

**Rationale**: WebDAV 是 HTTP 协议，现有 httpx 已有超时、无隐式代理和脱敏经验；S3 SigV4
不应自行实现。共享的 `RemoteBackupStore` 只表达备份对象行为，恰好有两个真实实现和测试
替身。

**Alternatives considered**:

- 自己实现 S3 签名：安全与兼容风险不值得。
- 把远端挂载成本地目录：容易被误当作实时 SQLite 或同步目录。
- 统一成任意云盘插件平台：超出首期范围。

## 11. Windows 构建、安装与后期 MSIX

**Decision**: 使用 PySide6 官方 `pyside6-deploy 6.11.1` 和受控 `pysidedeploy.spec` 生成
Nuitka `4.0` `standalone` x64 载荷，编译器固定 MSVC 2022；首期用 Inno Setup `7.0.2` x64
生成 per-user 安装 EXE。后期以同一 standalone
载荷和 Windows SDK manifest 生成 Store MSIX；两个渠道不共享安装器逻辑，只共享应用二进制、
稳定 ID 与数据目录契约。

**Rationale**: `pyside6-deploy` 是 Nuitka 的官方包装并支持 standalone。standalone 目录便于
验证 Qt 插件、OpenSSL、SQLite 和模板资源，Inno Setup 再负责压缩安装；onefile 每次运行解压
到临时目录，不利于资源/安全软件/启动故障诊断。Inno Setup 提供可自动化的 `ISCC.exe`。
Microsoft 文档说明现有 EXE/桌面载荷可转换/打包为 MSIX，Store 通道再承担签名与更新。
[pyside6-deploy](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html)、
[Inno Setup command-line compiler](https://jrsoftware.org/ishelp/topic_compilercmdline.htm)、
[Microsoft MSIX packaging](https://learn.microsoft.com/en-us/windows/msix/packaging-tool/create-app-package)

**Alternatives considered**:

- PyInstaller：可用但不是本项目已选 Qt 官方部署路径。
- Nuitka onefile：临时解压和首启行为增加桌面数据目录与安全软件验收面。
- 首期直接 Store-only：会把商店账号、签名和审核放到功能验收关键路径。
- 应用静默更新：违反规格；EXE 通道只打开 HTTPS 下载页。

## 12. 旧 B/S 复用原则

**Decision**: “复用”以经过测试的行为为单位，不以目录复制为单位。正式桌面代码不得运行时
依赖 `apps/web`、`apps/api`、`apps/worker` 或旧 PostgreSQL Repository。允许提取的资产只有：

- 固定 DOCX 模板、字段映射和样式断言；
- 首期四栏/反思的结构化教案值对象、完整性规则、教学周/日期/季节纯函数；下一期 DOCX
  source、group split/add-step 模型本期不落盘；
- AI 结构结果模型、规范哈希、输入最小化、过期预览判定和 Provider-neutral HTTP 防护；
- 仅复用 Provider-neutral HTTP/结构校验行为，不复用旧 Job 状态、Provider thread、Cloud
  审计、任意 Tool 或写入编排；
- 对上述行为的虚构 fixture 与单元断言。

**Rationale**: 代码图谱显示旧运行时中心是 API -> backend/repository、Worker -> Job/Export Store，
`WordExportRunner` 直接依赖 claim/load/mark/write 等 PostgreSQL/Worker 协议；这些不是桌面用例。
相反，`teaching_week`、`PlanContentV1`、`section_sha256` 和 Teacherplan 单元格映射具有较小、
明确且可独立测试的行为边界。

**Alternatives considered**:

- 在桌面新包中直接 import 旧 backend：会保留租户、身份、PostgreSQL 和任务依赖的隐性入口。
- 先复制全部再删：难以证明没有遗留安全/事务语义，且会扩大 Review 面。
- 完全不看旧代码：会丢失已验证的 Word 和结构化内容回归证据。
