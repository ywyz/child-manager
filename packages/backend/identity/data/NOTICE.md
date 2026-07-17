# SecLists 弱密码资源来源说明

本目录包含从 SecLists 项目冻结复制的弱密码资源，仅用于本地密码强度校验。

- **项目**: SecLists
- **发布版本**: 2026.1
- **Git commit**: `190c6f7bd58c847ceadfe57d9853592737f059e8`
- **原始路径**: `Passwords/Common-Credentials/10k-most-common.txt`
- **原始 URL**: https://github.com/danielmiessler/SecLists/blob/190c6f7bd58c847ceadfe57d9853592737f059e8/Passwords/Common-Credentials/10k-most-common.txt
- **许可证**: MIT License（SecLists 仓库根目录声明）

## 本地文件校验

```text
sha256sum packages/backend/identity/data/10k-most-common.txt
4adb3f0afb4a10cf19ebe48d8c69a46f934bbc8d77c694c210564f9583e7f4ba

wc -l -c packages/backend/identity/data/10k-most-common.txt
10000 73017
```

自动化测试不得访问真实网络；该文件在仓库内静态保存，供测试时直接读取。
