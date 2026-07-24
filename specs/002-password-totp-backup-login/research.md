# Phase 0 Research: 密码与 TOTP 备用登录

## R-001 密码策略

**Decision**: 密码长度为 8–128 个 Unicode 字符；允许空格、粘贴和密码管理器；不设置字符
组合规则、不周期轮换。建立和修改时对规范化后的密码执行本地弱密码、泄露密码以及账号/
产品相关词阻断，并对失败验证限流。

**Rationale**: NIST SP 800-63B 对作为多因素组成部分的密码允许最低 8 字符，要求至少支持
64 字符、Unicode、粘贴，并反对组合规则与无泄露证据的周期轮换。备用登录始终还要求
TOTP，因此采用 8 字符最低值；128 字符上限降低拒绝服务风险且超过最低互操作要求。

**Alternatives rejected**:

- 密码单独登录：不满足用户确认的双因素边界。
- 强制大小写、数字和符号：可用性差，且不如长度与阻断列表有效。
- 在线泄露密码查询：认证设置不应依赖外部网络，也不得向第三方泄露密码衍生信息。

**Sources**:

- [NIST SP 800-63B — Passwords](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#password)

## R-002 密码摘要

**Decision**: 复用已锁定的 `argon2-cffi`，使用 Argon2id；实现时固定可审计参数，至少达到
RFC 9106 的第二推荐档（64 MiB、3 次迭代），每个密码使用独立 16 字节随机盐，并在成功
验证后按 `check_needs_rehash` 渐进升级参数。

**Rationale**: Argon2id 同时缓解侧信道与 GPU 离线破解风险。项目已依赖
`argon2-cffi>=25.1,<26` 并锁定 Python 3.14 wheel，无需增加密码摘要依赖。

**Alternatives rejected**:

- PBKDF2/bcrypt：项目已有更合适的 Argon2id 实现，没有并存两套摘要格式的价值。
- 自行实现 KDF：增加密码学实现风险。

**Sources**:

- [RFC 9106 — Argon2 Memory-Hard Function](https://www.rfc-editor.org/rfc/rfc9106.html)
- [`argon2-cffi` API](https://argon2-cffi.readthedocs.io/en/stable/api.html)
- [`argon2-cffi` parameters](https://argon2-cffi.readthedocs.io/en/stable/parameters.html)

## R-003 TOTP 参数与重放

**Decision**: 每账号生成唯一随机 160 位种子，采用 HMAC-SHA-1、6 位数字、30 秒周期；验证
当前时间步及前后各一个时间步，但以数据库中的 `last_accepted_counter` 原子拒绝已经成功
使用的相同或更早计数器。

**Rationale**: 30 秒是 RFC 6238 默认值，6 位与 SHA-1 具有最广泛认证器兼容性；HMAC
使用方式不依赖 SHA-1 的碰撞抗性。允许相邻时间步解决合理时钟偏差，持久化最后成功计数器
满足同一 OTP 不得重复接受的要求。

**Alternatives rejected**:

- 更宽的时间窗口：增加在线猜测和重放机会。
- 只在进程内记录重放：多进程和重启后不能保证一次性。
- 引入 TOTP 第三方库：标准库足以实现小而可测试的 RFC 6238 核心。

**Sources**:

- [RFC 6238 — TOTP](https://www.rfc-editor.org/rfc/rfc6238.html)
- [NIST SP 800-63B — Single-factor OTP](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#sfotp)

## R-004 TOTP 种子保护

**Decision**: TOTP 种子使用 AES-256-GCM 加密；每次写入生成随机 96 位 nonce。待确认
enrollment 的 AAD 绑定 `kindergarten_id`、`user_id`、`enrollment_id` 和 envelope version；
成功启用时以新 nonce 重新加密，并把 AAD 改绑 `credential_id`。密文记录 `key_id`，主密钥
位于数据库和代码库之外；开发环境读取权限受限的仓库外文件，测试注入固定适配器，生产
托管方案按 ADR-0009 延后。

**Rationale**: TOTP 验证端必须恢复共享种子，单向摘要不可用；AEAD 同时提供保密性和
完整性，账号上下文 AAD 防止密文跨账号替换。

**Alternatives rejected**:

- 明文或仅数据库透明加密：数据库泄露时保护不足，且不能绑定账号上下文。
- 普通环境变量保存主密钥：违反项目密钥硬性规则。
- 复用用户密码加密 TOTP：会造成循环依赖，也无法支持 WebAuthn 重设。

## R-005 认证保证级别

**Decision**: 会话持久化 `authentication_method`（`webauthn` 或
`password_totp`）以及最近 WebAuthn/备用重新验证时间。密码与 TOTP 建立的会话可访问普通
业务，但备用重新验证证明的固定 purpose 为 `add_passkey`，五分钟有效，不能授权其他身份
操作；新增通行密钥不会自动提升原会话。

**Rationale**: 密码与 OTP 都不具备钓鱼抗性。把来源和最近验证时间显式建模，API 才能
避免把普通业务授权误当作高风险身份授权。

**Alternatives rejected**:

- 所有已登录会话等价：会让备用路径绕过 WebAuthn 保护的凭据与恢复管理。
- 新增通行密钥后原地升级：注册成功不证明当前会话随后使用过该通行密钥。

**Sources**:

- [NIST SP 800-63B — Phishing resistance](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#verifimp)

## R-006 设置、恢复与设备切换

**Decision**: 管理员强制配置，教师可选。仍有通行密钥时，备用因素建立、重设和关闭均要求
最近 WebAuthn 验证；所有通行密钥不可用时不开放密码/TOTP 重置捷径，继续使用离线恢复码
加人工核验。TOTP 迁移通过重新绑定新种子完成，并使旧种子、旧备用会话和未消费证明失效。

**Rationale**: 软件 OTP 更换设备本质是新认证器绑定；新设备确认后必须使旧认证器失效。
恢复路径若只验证其中一个备用因素，会比登录路径更弱并成为账号接管入口。

**Alternatives rejected**:

- 管理员代用户重置：破坏带外核验和最后管理员双人核验边界。
- 保留新旧 TOTP 并行宽限期：设备丢失场景会延长攻击窗口。

## R-007 账号枚举、限流与审计

**Decision**: 密码与 TOTP 在同一次登录意图中验证，对未知账号执行等价的密码成本与虚拟
TOTP 路径；公开响应和审计字段使用同一失败类别。按可信来源、账号标识摘要和端点全局三层
限流，TOTP 成功不能单独清零密码或全局失败状态。审计只记录主体、方法、结果、请求 ID 和
必要时间，不记录任何认证秘密。

**Rationale**: 新公开端点不能恢复当前 WebAuthn 设计已经消除的账号枚举、伪造来源分区或
单因子探测通道。

## R-008 里程碑与迁移顺序

**Decision**: 新增里程碑命名为 M3A，排在 M3 后、M4 前。M3 仍拥有 T036–T045 和
`0004_settings.py`；M3A 迁移使用 `0005_password_totp_backup_login.py`，
`down_revision = "0004_settings"`。

**Rationale**: 当前 M3 已固定 Issue、任务范围和迁移编号。更改 M3 会破坏已确认基线，
而把本功能延后到 M4 之后会让后续身份依赖继续建立在已被产品决定替换的“仅通行密钥”
假设上。

**Alternatives rejected**:

- 插入或重编号 `0004`：重现已经解决的迁移命名冲突。
- 扩大现有 M3 Issue：违反固定 T036–T045 范围与文档基线。
