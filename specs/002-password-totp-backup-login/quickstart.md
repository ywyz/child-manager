# Quickstart: 密码与 TOTP 备用登录

本文件是 M3A 实施与验收入口。文档确认前不得在 `dev` 开始实现。

## 1. 实施前 Gate

1. 创建独立 M3A GitHub Issue，固定包含本规格的 `docs` 提交。
2. Issue 明确范围、非目标、验收标准、验证命令以及 `0005` 对 `0004_settings` 的依赖。
3. 将确认后的 docs 提交同步到 `dev`，确认没有未解决冲突。
4. 设置隔离 PostgreSQL schema：

   ```bash
   export CHILD_MANAGER_TEST_DATABASE_URL='postgresql+psycopg://.../child_manager_test?...'
   ```

5. 先运行契约、迁移、密码/TOTP、API 与 Web 的 RED 测试；collection、fixture 和数据库错误
   不算 RED。

## 2. 关键验收旅程

### 管理员强制绑定

1. 已激活管理员以通行密钥登录。
2. 未配置备用因素时只能看到绑定流程，不能访问业务页面。
3. 设置合格密码，扫描/复制只展示一次的 TOTP 种子，并输入首个验证码。
4. 完成后进入业务页面；状态只显示已启用和更新时间，不显示秘密。

### 新设备备用登录

1. 在没有可用通行密钥的新浏览器输入账号、密码和 TOTP。
2. 任一错误、未知账号、未配置或重放均得到同一通用失败。
3. 两项正确时进入普通业务页面，会话标记为 `password_totp`。
4. 再次验证密码与 TOTP，在五分钟内为新设备新增通行密钥。
5. 验证同一会话不能删除旧通行密钥、重设因素、轮换恢复码或管理账号。
6. 下次认证后查看本人最近安全事件，确认备用登录和新增通行密钥均有不含秘密的警报。

### 因素维护与恢复

1. 使用通行密钥重新验证后重设密码或 TOTP，确认旧备用会话立即失效。
2. 教师可关闭备用登录；管理员关闭请求必须被拒绝。
3. 丢失全部通行密钥时，不出现密码/TOTP 快捷重置；仍要求离线恢复码加人工核验。
4. 恢复完成后确认旧密码、TOTP、通行密钥、会话、邀请与旧恢复码均失效。

## 3. 专项验证

```bash
uv run pytest tests/unit/identity -q
uv run pytest tests/contract/test_auth_contract.py -q
uv run pytest tests/migrations/test_0005_password_totp_backup_login.py -q
uv run pytest tests/repository/test_identity_isolation.py -q
uv run pytest tests/api/test_backup_auth.py tests/api/test_credentials.py tests/api/test_recovery.py -q
uv run pytest tests/web/test_auth_smoke.py -q
```

必须另外验证：

- TOTP 当前、前一和后一时间步；相同/更早计数器重放；并发双重消费。
- 未知账号、密码错误、TOTP 错误、未配置因素的公开响应一致。
- `totp_secret`、`otpauth://`、密码、摘要和验证码不进入日志、异常、审计或快照。
- 备用重新验证只能到达“新增通行密钥”授权分支。
- 本人安全事件只返回当前园所、当前用户最近 20 条白名单投影，不产生已读写入。
- 所有 Repository 查询均带 `kindergarten_id`。

## 4. 完整验证

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
graphify update .
git diff --check
```

`graphify update .` 后检查 manifest、JSON 可解析性、核心节点、敏感值扫描和无向多重图诊断；
图谱缩小必须调查覆盖率，不能直接强制覆盖。
