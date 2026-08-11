# 桌面 Slice 1 Windows 手工验收证据

日期：2026-08-10

## 固定基线

- 分支：`dev`
- 实现代码锚点：`cf106e44cb907a4958879a16ee061dccc8c2b1f9`
- docs 基线：`fff6e0908fcb591c927205d53cdbacd35037bce3`
- Issue：https://github.com/ywyz/child-manager/issues/14
- 固定 Review SHA：由包含本证据、docs 同步和 T034 状态更新的后继收口提交确定；实现代码仍固定到上述 `cf106e44...`。

本次是 Python 3.14 + `uv` 的源码运行验收，不是 `.exe`、MSI、MSIX、standalone 或安装器
验收；Windows 打包仍属于 T115–T119 的后续范围。

## 验收口径

一名未参与实现、只依赖界面提示的验收参与者在断网 Windows 环境执行 Slice 1 手工闭环。
维护者确认结果为“通过，未计时”。按照 docs 基线修订后的 SC-001、实施计划和 T034，本轮不记录
开始时间、完成时间或耗时，也不把 5 分钟作为通过条件。

验收只使用虚构园所、教师、班级和教案资料；未配置 AI 或其他外部服务。

## Windows 观察结果

| 二元证据 | 结果 |
|---|---|
| 无既有桌面数据时首次启动，进入最少设置流程 | 通过 |
| 完成基础设置并创建第一份教案 | 通过 |
| 保存后关闭并重启，最后一次成功保存的教案内容仍可读取 | 通过 |
| 从当前教案执行“导出当天 Word” | 通过 |
| 导出的 `.docx` 在 Windows Microsoft Word 中实际打开，未出现修复提示 | 通过 |

上述结果证明 Slice 1 的断网手工闭环通过；没有计时数据，因此本文不推断或补写任何耗时。

## 精确自动化证据

实现代码锚点的 GitHub Actions Quality 证据为
[run 31392074261 attempt 2](https://github.com/ywyz/child-manager/actions/runs/31392074261)：

- `status=completed`
- `conclusion=success`
- `run_attempt=2`
- `headSha=cf106e44cb907a4958879a16ee061dccc8c2b1f9`
- Ruff format：370 files already formatted
- Ruff check：All checks passed
- Pyright：0 errors / 0 warnings / 0 informations
- Pytest：794 passed / 1 warning

Linux CI 证明实现锚点的自动化门禁通过，但不能替代上一节的 Windows 手工观察；同样，本次
Windows 源码运行通过不代表已经生成 Windows 独立程序或安装器。

## T034 结论与停止边界

T034 已具备无计时的 Windows 二元验收事实、精确实现锚点 CI 和本证据文件，可以标记完成。
Slice 1 仍须以收口提交为固定 Review SHA 完成 Standards/Spec 双轴 Review，Review 通过后才允许
合并 `main`。T035–T040 必须由独立 Slice 2A Issue 驱动，先取得 clean RED，并停在 T040；不得
进入 T041 GREEN，也不得跳到 Agent Foundation。
