# GitHub Issue 草案：桌面 Slice 3 本地恢复与远程加密备份（T061–T078）

> 本文件只是本地草案，尚未创建 GitHub Issue，也不授权开始 T061。

## 固定基线

- 完整 docs SHA：`d4ac961a04a273a0384e295190296f69538b313b`
- Slice 2B 固定实现 SHA：`a14a24dc65e3a535125b356b3d740c0062adf545`
- 前置状态：Slice 2B T054–T060 已完成 Linux/静态 GREEN；最终证据提交、远端 Quality CI 与
  Issue #20 回填仍须在创建 Slice 3 Issue 前精确固定
- 实施分支：`dev`

事实来源固定为上述 docs SHA：

- `specs/003-desktop-local-first/spec.md`
- `specs/003-desktop-local-first/plan.md`
- `specs/003-desktop-local-first/tasks.md`（T061–T078）
- `specs/003-desktop-local-first/data-model.md`
- `specs/003-desktop-local-first/contracts/application-services.md`
- `specs/003-desktop-local-first/quickstart.md`
- `docs/ADR/ADR-0012-local-first-desktop-product-reset.md`

## 目标

在桌面本地优先边界内实现一致性本地备份、`KMBACKUP1` 加密信封、显式版本恢复，以及 WebDAV/S3
单向不可变远程备份。远程不可用、凭据缺失或持续失败不得阻断本地编辑、保存、单日 Word、可选 AI
关闭状态或 Agent READ/DRAFT。

## 范围与依赖顺序

1. T061–T066：分别建立 SQLite snapshot、加密信封、archive safety、远程 store、恢复事务和 UI
   的确定性 RED；不访问真实远程服务。
2. T067：收集 clean RED，先证明 Slice 1/2A/2B 回归仍绿，失败仅来自当前缺失行为。
3. T068：备份 Domain 值对象。
4. T069：SQLite `Connection.backup()` 一致快照、完整性、计数、hash、取消与保留策略。
5. T070：`KMBACKUP1`、固定 KDF 上限、scrypt/AES-GCM 与安全解包。
6. T071：Windows Credential Locker 的 WebDAV/S3 secret 与可选恢复口令缓存窄边界。
7. T072/T073：WebDAV 与 S3 不可变加密对象 Adapter；可在共同契约稳定后分别实施。
8. T074：daily/manual/轮换、上传、列举、显式下载与恢复事务 Application 服务。
9. T075：当日本地备份和迁移前备份失败即停止升级。
10. T076：备份/恢复页面；只选择具体版本，不猜测最新对象。
11. T077：唯一 composition root 装配；远程网络只经 Qt runtime 后台运行。
12. T078：全矩阵、100 次本地保存、质量入口、Graphify 与验收证据。

每项继续遵循 collect → 目标 RED → 最小 GREEN → 目标/稳定回归 → Ruff/Pyright/锁检查 →
专项隐私/启动探针 → Graphify → 真实通过后勾选与记录证据。

## 非目标

- 不实现同步、冲突合并、双向复制、自动选择“最新”远程对象或远程 SQLite。
- 不把明文数据库、正文、教师/园所/班级信息、凭据、恢复口令或密钥写入远端 manifest/log/audit。
- 不自行实现 S3 SigV4，不把 multipart ETag 当 SHA-256。
- 不实现 Agent WRITE/Confirmation、长期 Agent 记忆、多 Agent、并行 Tool 或 Level 3 Workflow。
- 不引入本地 HTTP、FastAPI、NiceGUI、PostgreSQL、Redis/Worker 或 Cloud 部署拓扑。
- 不访问真实 WebDAV/S3，不提交真实 endpoint、bucket、access key、secret 或备份样本。
- 不修改或重排 Word 模板，不顺带修复其他 QA Issue。

## 验收标准

- [ ] SQLite backup 是同一时点一致快照；取消/空间不足失败不发布半成品。
- [ ] restore 前后运行 integrity、foreign key 与关键表计数校验。
- [ ] daily 只轮换 30 份；pre-migration/pre-restore 按契约保留且不被 daily 轮换误删。
- [ ] `KMBACKUP1` 黄金向量稳定；错口令、header/AAD/ciphertext/tag 篡改、截断和恶意 KDF 参数
      全部 fail closed。
- [ ] archive 条目白名单拒绝路径穿越、重复条目、符号链接、压缩炸弹、长度/hash 不符与未来格式。
- [ ] WebDAV/S3 替身覆盖上传、列举、显式对象下载、删除、超时、中断和长度不符；远端只收到加密对象。
- [ ] 恢复必须显式选择候选；旧 Schema 只在 staging 升级，未来 Schema 拒绝；原子替换失败或首次
      打开失败自动回滚。
- [ ] 恢复前停止新任务、取消/等待运行 operation，并关闭全部 Session/engine；普通事务不等待远程网络。
- [ ] 当日本地备份和迁移前备份只有成功后更新状态；失败即停止升级，但远程失败不阻断本地保存。
- [ ] 远程持续失败时连续保存 100 次教案均成功，正文/revision/版本规则保持正确。
- [ ] 跨全新安装恢复虚构数据库成功；清单与错误/日志无身份信息、正文、路径、口令或 secret。
- [ ] 默认 `uv run pytest -q` 不出现 Cloud/PostgreSQL/Redis 环境错误。
- [ ] Slice 1/2A/2B、Ruff、Pyright、锁检查、启动/隐私探针与 Graphify 诊断全部真实通过。
- [ ] Windows 检查表和可复现构建物已准备；Windows 结果只由用户手工填写，不以 Linux 代替。

## 验证命令

```bash
uv run pytest --collect-only -q
uv run pytest -q tests/desktop/database/test_backup_snapshot.py
uv run pytest -q tests/desktop/unit/test_backup_envelope.py
uv run pytest -q tests/desktop/contracts/test_backup_archive_safety.py
uv run pytest -q tests/desktop/contracts/test_remote_backup_stores.py
uv run pytest -q tests/desktop/application/test_restore_transaction.py
uv run pytest -q tests/desktop/ui/test_backup_restore_flow.py
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv sync --locked
uv lock --check
graphify update .
graphify extract . --backend openai
graphify diagnose multigraph --graph graphify-out/graph.json --undirected
```

远程 store 测试必须使用内存/本地确定性替身和禁网保护；真实远程或付费服务不属于自动化验收。

## 首次授权建议与停止边界

Issue 创建后首次只授权 T061：先 `pytest --collect-only`，再建立 SQLite snapshot clean RED，并只将
T061 标为完成。T061 完成不自动授权 T062、T067、GREEN、提交、Review、push、Windows 验收或
`main` 集成；每个门禁继续独立授权。
