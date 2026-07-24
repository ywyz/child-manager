# Implementation Plan: 密码与 TOTP 备用登录

**Specification Branch**: `docs` | **Implementation Branch**: `dev` | **Date**: 2026-07-23 | **Spec**: 待本次 docs 提交后固定

**Issue**: 待规格确认后创建；必须固定本次 docs 提交并限定 M3A 范围

**Input**: Feature specification from `/specs/002-password-totp-backup-login/spec.md`

## Summary

在保留 WebAuthn 通行密钥为首选登录方式的前提下，增加必须同时验证密码与 TOTP 的独立
备用登录。备用会话可使用角色允许的普通业务功能；最近五分钟再次完成密码与 TOTP 验证后
只可新增通行密钥。备用因素的建立、轮换与关闭仍要求 WebAuthn 重新验证；所有通行密钥均
不可用时继续走离线恢复码加人工核验。

实现沿用现有身份服务、会话、限流、审计和 WebAuthn 边界：密码使用既有 Argon2id 工具；
TOTP 使用标准库 HMAC 验证并保存最后成功时间步；TOTP 种子通过身份秘密加密端口以
AES-256-GCM 保存。新增独立认证表，不把密码或 TOTP 字段放回 `users`。

## Technical Context

**Language/Version**: Python 3.14+

**Primary Dependencies**: FastAPI、NiceGUI、SQLAlchemy 2.x、Alembic、
`argon2-cffi` 25.x、`cryptography` 49.x；TOTP 计算使用 Python 标准库

**Storage**: PostgreSQL；自动化测试使用隔离 PostgreSQL schema

**Testing**: Pytest、Ruff、Pyright；契约测试、API 测试、Repository 园所隔离测试、
Alembic 升降级测试与 NiceGUI 冒烟测试

**Target Platform**: NiceGUI Web/BFF 作为唯一公网入口，FastAPI API 仅供内部调用；
生产拓扑仍按 ADR-0009 延后

**Project Type**: monorepo Web 应用，独立 Web、API 与 Worker 运行单元

**Performance Goals**: 不以削弱 Argon2id 成本换取吞吐；普通园所规模下认证请求在限流和
密码验证预算内稳定完成，TOTP 验证不访问外部网络

**Constraints**: 备用失败不可枚举账号；TOTP 不可重放；原始密码、摘要、TOTP 种子和验证码
不得进入日志、审计或响应；备用升级证明只授权新增通行密钥

**Scale/Scope**: 单园部署、管理员与教师账号；一个账号最多一套当前有效密码与 TOTP，
可有多个通行密钥

## Constitution Check

*GATE: Issue 创建后及实施前必须全部通过；Phase 1 设计复核结果相同。*

- [ ] Issue 固定已确认的 `docs` 提交并链接 PRD、ADR-0010、ADR-0011、威胁模型与契约。
- [x] 规格明确范围、非目标、验收标准、风险和验证命令。
- [x] 实现仅以 `dev` 为目标；本次 `docs` 不包含业务代码、迁移或实现测试。
- [x] NiceGUI 只经 API 使用身份能力，API 保持认证、授权与事务边界。
- [x] 新表带 `kindergarten_id`，Repository 读写与唯一性校验显式园所隔离。
- [x] 密码与 TOTP 均不可单独登录；管理员不得关闭备用登录。
- [x] WebAuthn 重新验证仍保护因素管理；紧急恢复规则不降级。
- [x] TOTP 种子使用数据库外主密钥加密，秘密不得进入日志、审计和测试快照。
- [x] 当前 M3 的 `0004_settings.py` 保持不变；本功能迁移固定为其后继。
- [ ] Issue 创建后补齐固定提交链接，再解除实现 Gate。

## Project Structure

### Documentation (this feature)

```text
specs/002-password-totp-backup-login/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (implementation target on `dev`)

```text
apps/
├── api/
│   ├── dependencies.py
│   └── routers/auth.py
└── web/
    ├── api_client.py
    └── pages/auth.py

packages/
├── backend/
│   ├── database/migrations/versions/
│   │   └── 0005_password_totp_backup_login.py
│   ├── identity/
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   ├── passwords.py
│   │   ├── totp.py
│   │   └── secret_encryption.py
│   └── ports.py
└── contracts/identity.py

tests/
├── api/
├── contract/
├── migrations/
├── repository/
├── unit/identity/
└── web/
```

**Structure Decision**: 复用现有身份深模块，不创建第二套认证服务。公开 API 只增加到
`apps/api/routers/auth.py`，Web 仍通过 BFF 客户端调用；密码校验、TOTP、加密和状态转换留在
`packages/backend/identity`，契约模型留在 `packages/contracts/identity.py`。

## Phase 0: Research

研究结论记录于 [research.md](research.md)，覆盖密码策略、Argon2id、TOTP 参数与重放、
TOTP 种子加密、认证保证级别、限流和依赖选择。不存在待澄清技术项。

## Phase 1: Design & Contracts

- 数据模型与状态转换：[data-model.md](data-model.md)
- OpenAPI 契约：[contracts/openapi.yaml](contracts/openapi.yaml)
- 实施与验收入口：[quickstart.md](quickstart.md)
- 总体文档同步：宪法、ADR-0011、ADR-0010 关系、威胁模型、PRD、系统架构、总数据模型、
  总数据库结构、ROADMAP 与 001 总规格

## Phase 2: Implementation Strategy

1. 先增加密码、TOTP、认证保证级别、数据库约束、契约、API 和 Web 流程的 RED 测试。
2. 增加 `0005_password_totp_backup_login.py` 与 Repository 隔离实现。
3. 实现密码与 TOTP 原语、种子加密、绑定状态机和公共备用登录。
4. 实现备用会话、五分钟专用升级证明及“只能新增通行密钥”的授权边界。
5. 实现 WebAuthn 保护的轮换/关闭、管理员门禁、恢复清理、审计、通知和限流。
6. 完成 NiceGUI 流程，再执行目标测试、完整验证、敏感信息扫描和 Graphify 更新。

## Complexity Tracking

无宪法例外。密码、TOTP 和短时升级证明仍属于同一个身份深模块；独立表是为了避免把可选
备用认证状态重新耦合到 `users`，不是新增服务或抽象层。
