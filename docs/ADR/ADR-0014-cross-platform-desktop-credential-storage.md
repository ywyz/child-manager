# ADR-0014：桌面凭据使用 Windows Credential Locker 与 Linux Secret Service

- 状态：已接受
- 日期：2026-08-14
- 决策者：项目维护者
- 依赖：[ADR-0012](ADR-0012-local-first-desktop-product-reset.md)

## 背景

桌面应用已通过 `keyring` 窄边界把 AI API Key 排除在 SQLite、备份、日志和异常之外，但当前
组合根只在 Windows 装配凭据存储，并只接受 Windows Credential Locker。这使 Ubuntu 虽可运行
完整桌面源码和自动化测试，却不能在同一界面安全配置真实模型，维护者必须频繁切换到 Windows
才能测试 AI 与 Agent。

Ubuntu 24.04 GNOME 桌面已提供 Secret Service、登录 keyring 和 D-Bus 会话。继续把 Key 写入
环境变量、明文文件或 SQLite 作为测试捷径会破坏既有秘密边界；仅使用进程内替身又不能覆盖
真实桌面配置和重启读回。

## 决策

1. 保留稳定服务名 `cn.kindergartenmanager.desktop` 和固定账号键，通过 `keyring 25.*` 支持：
   - Windows：`Windows WinVaultKeyring`，固定 `local-machine` persistence。
   - Linux：`keyring.backends.SecretService.Keyring`，使用当前操作系统用户的 Secret Service
     登录 keyring，记录为 `local-user` persistence。
2. 桌面组合根在 Windows 与 Linux 都尝试创建平台凭据存储。受支持后端不可用、被锁定或访问
   失败时，外部 AI/Agent fail closed，手工教案、保存和 Word 导出继续可用。
3. Null、明文文件、未知或仅伪造显示名的 backend 一律拒绝；不得回退到环境变量、仓库文件、
   普通配置文件、SQLite、日志、异常或测试快照。
4. `CredentialStore` 只暴露写入、读取、必需读取和删除；后端异常转换为稳定、脱敏的凭据错误，
   不携带 Key、D-Bus 地址、collection 名或后端异常正文。
5. Ubuntu 验收覆盖真实 Secret Service 写入、读回、删除、重启后 AI 设置可用，以及真实
   OpenAI-compatible AI/Agent 链路。验收只使用虚构教案；专用烟雾凭据必须在测试结束时删除。
6. 本决策让 Ubuntu 成为受支持的源码运行与真实 AI 测试平台，不改变 Windows 11 x64 首发、
   安装器、DPI、原生文件对话框和 Microsoft Word 的发布验收边界，也不声明 Linux 安装包。

## 取舍

### 收益

- 维护者可在 Ubuntu 日常开发环境直接测试真实 AI 与 Agent，不再为每次模型测试切换 Windows。
- 两个平台继续使用操作系统秘密存储，SQLite 与备份格式无需迁移。
- 同一窄端口服务 AI，未来备份凭据仍可复用而不把平台 SDK 带入 Application Layer。

### 代价

- Linux 依赖可用且已解锁的 Secret Service/D-Bus 用户会话；纯 SSH、容器或无桌面会话可能只
  能运行替身测试。
- Windows 的 `local-machine` 与 Linux 的 `local-user` 生命周期不同，验收与支持文档必须明确。
- Ubuntu 源码运行成功不能替代 Windows 安装、DPI、文件锁和 Word 验收。

## 被否决方案

### 环境变量或 `.env`

容易进入进程检查、shell 历史、日志和诊断输出，也与既有“秘密不进普通环境变量”边界冲突。

### SQLite 或普通配置文件加密保存

仍需另一个安全主密钥，且备份会携带密文凭据；为本地测试引入自举密钥问题没有收益。

### 仅提供内存测试模式

适合自动化但不能覆盖真实 UI 配置、进程重启与操作系统凭据读回，不满足维护者的日常真实 AI
测试目标。

### 支持任意 keyring backend

会静默接受 Null、明文文件或未知第三方实现，无法证明秘密没有落入普通文件。

## 后续复审条件

若未来发布 Linux 安装包、支持非 GNOME 桌面、无图形会话或系统级多用户部署，必须重新确认
Secret Service 可用性、安装依赖、解锁流程、应用沙箱和凭据迁移；不得从本 ADR 自动推导支持。
