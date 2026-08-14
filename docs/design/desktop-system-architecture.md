# 幼儿园管理助手桌面系统架构

## 1. 目标与边界

本设计实现 ADR-0012 和 `specs/003-desktop-local-first/spec.md`。首期是 Windows 桌面应用，
面向单教师，可管理多个班级；不启动本地 Web 服务，不包含账号、权限、多人并发、Cloud 或
多设备同步。

技术基线：

- Python 3.14+
- PySide6 6.11 系列与 Qt Widgets
- SQLite 与 SQLAlchemy 2.x
- Alembic 版本迁移
- `chinesecalendar` 1.11 系列
- `python-docx` 固定模板导出
- OpenAI 兼容 AI 客户端（可选）
- 受控单 Agent Runtime（可选、Application Layer、Tool-only）

## 2. 运行结构

```text
Qt Widgets
    │ commands / view models
    ▼
Desktop Application Services
    ├── Lesson Plan Service
    ├── History Service
    ├── Calendar Service
    ├── AI Generation Coordinator (Slice 2A)
    ├── Agent Runtime (Slice 2B+)
    │     ├── Agent Context Builder
    │     ├── READ / DRAFT / confirmed WRITE Tools
    │     └── Agent Provider Port
    ├── Export Service
    └── Backup Service
          │
          ├── SQLite repositories
          ├── OS credential store
          ├── local filesystem
          ├── WebDAV adapter (optional)
          └── S3 adapter (optional)
```

Qt 页面负责呈现、输入和状态反馈。应用服务拥有用例与事务边界。Repository 只处理本地持久
化。外部 AI、凭据、Word 和远程备份都是端口边界，不得在 Widget 信号处理器中直接调用。

受控 Agent 遵循 ADR-0013 和
[`agent-runtime.md`](../../specs/003-desktop-local-first/contracts/agent-runtime.md)。全应用只装配
一个位于 Application Layer 的 `AgentRuntime`；Provider 只能请求已注册 Tool，不能直接访问
Repository、Session、SQLite、文件、Widget、凭据或任意代码/网络能力。Slice 2B 只开放
`READ`/`DRAFT`，写入阶段才开放绑定精确 `PlanPatch` 和一次性 `Confirmation` 的 `WRITE`。
Level 3 Workflow、多 Agent 和长期业务记忆继续延后。

首期不建立通用插件系统。WebDAV 和 S3 共享最小的“上传、列举、下载、删除备份对象”能力，
但各自保持配置与错误语义。

## 3. 线程与任务

SQLite 写入和短读取在应用服务控制的事务中完成。AI、远程备份和较慢的 Word 导出使用 Qt
线程池执行，并通过信号把不可变结果返回主线程。后台任务不得直接操作 Widget。

AI 协调器同时只允许一个任务。任务状态只存在于当前进程：

```text
idle -> running -> succeeded | failed | cancelled
```

关闭应用时请求取消；无法立即取消的网络调用可以结束线程，但不得在关闭后采用结果。应用
重启后回到 `idle`，不会恢复上次任务。

Agent Provider 调用与 Tool loop 同样在一个受控后台 operation 内串行运行。跨线程只传冻结
`AgentContext`、Tool call、`ToolResult`、`PlanPatch` 和 operation ID；每个需要数据库的 Tool
在执行线程内建立并关闭自己的 Session。Provider 等待和教师确认期间不得保持数据库事务。

READ 使用短只读事务；DRAFT 不写持久状态。Agent WRITE 必须在确认后新开一个短事务，在事务
内重新校验目标 revision、字段摘要与业务不变量，并原子完成操作前快照、完整 Patch、revision
更新和最小审计。失败全部回滚；取消或迟到结果不得自动重放 WRITE。

## 4. 模块结构目标

```text
src/kindergarten_manager/
├── app.py
├── ui/
│   ├── main_window.py
│   ├── theme.py
│   ├── icons/
│   ├── widgets/
│   └── pages/
├── application/
│   ├── lesson_plans.py
│   ├── ai_generation.py
│   ├── agent_runtime.py
│   ├── agent_tools.py
│   ├── exports.py
│   └── backups.py
├── domain/
│   ├── lesson_plans.py
│   ├── calendar.py
│   └── backups.py
├── infrastructure/
│   ├── database/
│   ├── credentials/
│   ├── ai/
│   │   └── agent_provider.py
│   ├── exports/
│   └── backups/
└── resources/
```

这是目标结构而非立即创建全部目录的授权。实现按用户故事建立最小垂直切片，只有真实使用到
的模块才落盘。

## 5. 可复用与不可直接迁移

可优先评估复用：

- 教案结构化内容模型与日期/教学周纯规则
- AI 结构化结果模型、输入最小化和预览采用规则
- Provider-neutral 请求/响应防护；不得复用旧 Job、租户、Agent thread 或直接写入协议
- 固定 Word 模板、字段映射与样式回归测试
- `chinesecalendar` 工作日判断与本地人工覆盖语义

不得直接迁移为桌面基础设施：

- `apps/web`、`apps/api`、`apps/worker`
- WebAuthn、TOTP、邀请、令牌、角色和园所隔离装配
- Redis/Dramatiq 任务、租约和恢复扫描
- PostgreSQL 专属迁移、GiST、组合外键和公网部署配置

复用必须通过行为测试证明，不以复制旧模块数量衡量进度。

## 6. 平台与数据目录

应用使用 Qt 的标准路径 API 解析当前用户应用数据、缓存、日志和文档位置。禁止手工拼接
`C:\Users`、`~` 或当前工作目录。稳定应用标识 `cn.kindergartenmanager.desktop` 决定数据
目录；中文显示名变化不得改变目录。

数据目录至少区分：

- 主 SQLite 数据库
- 自动与恢复前备份
- 运行日志（脱敏）
- 临时导出和下载文件

安装目录只包含程序资源。卸载和升级默认不删除用户数据。

## 7. 验证责任

- Linux：领域、SQLite、备份、AI 替身、Word 与无界面测试；GNOME/Secret Service 会话还须
  覆盖真实凭据和 OpenAI-compatible AI/Agent 源码运行验收。
- Linux offscreen：Widget 构造、布局最小尺寸和截图烟雾验证。
- Windows：125%/150% DPI、1366x768、文件对话框、Credential Locker、安装/升级、Word 打开和
  SmartScreen/Store 分发人工验收。
- macOS：首期只保持可移植代码，不声明发布支持。
- Agent：Scripted Provider 覆盖 Tool-only、Context 裁剪、READ/DRAFT 零写入、单 Agent/取消、
  Patch 确认绑定、stale 拒绝、事务回滚和重启后无长期业务记忆。
