# 桌面 Slice 2A clean RED 证据

## 1. 固定范围

- 执行 Issue：[Issue #19](https://github.com/ywyz/child-manager/issues/19)
- 完整 docs SHA：`fff6e0908fcb591c927205d53cdbacd35037bce3`
- Slice 1 固定 Review SHA：`11527404d4bd13551fe23d793b5e81d8e0e22b74`
- `main` 集成基线：`52432295377c7b88f490822664cfaed0412d3836`
- 本证据只覆盖 T035–T040；T041 GREEN、Agent Foundation 与任何实现模块均未获授权。

## 2. 先收集

第一条测试命令：

```bash
uv run pytest --collect-only
```

结果：`827 tests collected in 4.66s`。相对 Slice 1 的 794 项基线新增 33 项；collection 无
import、fixture、数据库、网络或环境错误。

新增测试分布：

- T035 `test_ai_domain.py`：7 项；
- T036 `test_ai_client.py`：9 项；
- T037 `test_credentials.py`：7 项；
- T038 `test_ai_generation.py`：5 项；
- T039 `test_ai_preview_flow.py`：5 项。

## 3. clean RED

```bash
uv run pytest \
  tests/desktop/unit/test_ai_domain.py \
  tests/desktop/contracts/test_ai_client.py \
  tests/desktop/contracts/test_credentials.py \
  tests/desktop/application/test_ai_generation.py \
  tests/desktop/ui/test_ai_preview_flow.py \
  --quiet
```

结果：`33 failed in 0.14s`。全部失败均由 `tests/desktop/helpers.py` 转换为稳定
`SLICE2A_RED` 断言，原因只包括以下计划中的公开模块尚未实现：

- `kindergarten_manager.domain.ai`；
- `kindergarten_manager.infrastructure.ai.client`；
- `kindergarten_manager.infrastructure.credentials`；
- `kindergarten_manager.application.ai_generation`；
- `kindergarten_manager.ui.widgets.ai_preview`。

测试使用 `httpx.MockTransport`、内存凭据 backend 和脚本化 runtime/store；未访问真实网络、真实
AI、操作系统凭据或付费服务。没有用 import error、skip、fixture 失败、数据库失败、环境失败或
放宽断言制造 RED。

## 4. Slice 1 与质量门禁

排除五个预期 RED 文件后重跑既有桌面 Slice 1：

```bash
uv run pytest tests/desktop \
  --ignore=tests/desktop/unit/test_ai_domain.py \
  --ignore=tests/desktop/contracts/test_ai_client.py \
  --ignore=tests/desktop/contracts/test_credentials.py \
  --ignore=tests/desktop/application/test_ai_generation.py \
  --ignore=tests/desktop/ui/test_ai_preview_flow.py \
  --quiet
```

结果：`65 passed in 3.35s`。AI RED 没有成为手工保存、重启读取或单日 Word 的前置条件。

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

结果：375 files already formatted；Ruff All checks passed；Pyright 0 errors / 0 warnings /
0 informations。

## 5. 停止边界

- T035–T040 已完成并标记；T041 与后续任务保持未勾选。
- 当前只有测试、证据和任务状态变更；没有新增 GREEN 业务实现。
- 本地 RED 变更未提交、未推送；提交/推送、RED Review 与进入 T041–T048 需要后续独立授权。
- 不得跳到 T049 Agent Foundation 或任何 WRITE Tool。
