# Ubuntu Secret Service 真实 AI 测试能力实施证据

- 日期：2026-08-14
- Issue：[#26](https://github.com/ywyz/child-manager/issues/26)
- 固定文档基线：`docs@2b2e311833541d31909b38588b9814f4c743e9f9`
- 平台：Ubuntu 24.04 GNOME、已登录图形用户会话、Secret Service + 用户 D-Bus

## RED

确认的公共测试缝为 `create_credential_store()` 与 `create_desktop_window()`。新增 Linux Secret
Service 接受、`local-user`、稳定服务/账号键、访问错误脱敏和桌面 AI 设置保存用例后：

```text
5 failed, 9 passed
```

五个失败分别来自 Linux backend 尚未受支持、三种访问错误尚未脱敏转换，以及 Linux 组合根
尚未创建凭据存储；没有导入、Qt、SQLite 或环境错误。

首次固定 SHA 双轴审查后又补充了后端身份、发现异常、写后读回和完整组合根链路用例。修复前
三个定向用例稳定失败：Windows 显示名伪造未拒绝、backend 发现异常未转换、写入异常值未被
读回校验发现。

## GREEN

- `tests/desktop/contracts/test_credentials.py`：`16 passed`
- 凭据与桌面组合根纵向用例：`18 passed`
- 凭据、AI、Agent、UI 与组合根专项：`61 passed`
- `create_desktop_window()` 纵向用例已从设置保存继续覆盖栏目生成与 Agent，并验证两条路径均
  从同一凭据存储读取稳定账号键。
- 完整测试：`209 passed`
- Ruff format/check：通过
- Pyright：`0 errors, 0 warnings, 0 informations`
- `uv sync --locked`、`uv lock --check`：通过
- wheel 与 sdist：构建成功

## 真实 Secret Service 烟雾

使用稳定应用服务名和专用虚构账号 `smoke.t060d.review.20260814`，未读取或覆盖真实 AI Key：

1. 当前真实 backend 为 `SecretService Keyring`，persistence 为 `local-user`。
2. 第一进程写入虚构值并读回成功。
3. 独立第二进程读回成功。
4. 第三进程删除，随后读取为 `None`，专用凭据残留为 0。

烟雾不打印秘密值，不访问真实 AI 网络，也不把值写入 SQLite、备份、日志或测试快照。

## 边界与待手工验收

- Ubuntu 源码桌面现在可以在 AI 设置页把维护者自己的 API Key 保存到 Secret Service，并复用
  现有文本生成、集体活动拆分与 Agent READ/DRAFT 链路。
- 常规自动化不调用真实或付费 AI；维护者仍须在固定实现 SHA 的 UI 中输入自己的 Endpoint、
  模型名和 Key，完成真实模型请求后回填 Issue #26。
- 本证据不替代 Windows Credential Locker、DPI、文件锁、原生对话框、安装器或 Microsoft
  Word 验收，也不声明 Linux 安装包。
