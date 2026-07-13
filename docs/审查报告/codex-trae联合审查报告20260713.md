# Child Manager 编码前联合审查报告（Codex + Trae）

> 审查日期：2026-07-13  
> 报告性质：Codex 与 Trae 编码前审查的合并定稿  
> 事实基线：以 `docs/faq/combined-audit.md` 及其引用的 canonical 文档为准  
> 操作边界：本报告不授权编码、创建或切换分支、提交、推送、创建 Issue、Pull Request 或改写 Git 历史。

## 1. 联合结论

**当前不能进入编码，也不应发布 M1 实现 Issue 任务列表。**

两份原审查报告已经在核心决策、主要阻断项、M0 门禁状态和解锁顺序上完成收敛。项目的业务规格、实现计划和任务覆盖已经足够详细；当前阻塞不在任务数量，而在 M0 共享基线尚未形成一致、可信、可重复验证的完成证据。

可以准备 Issue 草稿，但在 M0-G1～M0-G8 全部关闭前，不应创建 M1 实现子 Issue、执行 T003 或开始 T004 之后的代码任务。

## 2. 当前文档与已满足规则

### 2.1 文档状态

| 文档类型 | 文件路径 | 当前判断 |
| --- | --- | --- |
| 规格文档 | `specs/001-daily-activity-plan/spec.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 实现计划 | `specs/001-daily-activity-plan/plan.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 任务清单 | `specs/001-daily-activity-plan/tasks.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 数据模型 | `specs/001-daily-activity-plan/data-model.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| OpenAPI 契约 | `specs/001-daily-activity-plan/contracts/openapi.yaml` | 文件已存在、结构基本完备、待 M0 收敛 |
| 状态机契约 | `specs/001-daily-activity-plan/contracts/job-state-machine.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 系统架构 | `docs/design/system-architecture.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 交叉审计结论 | `docs/faq/combined-audit.md` | 当前唯一有效的审计事实基线 |

### 2.2 已确认满足的规则

- AES-256-GCM、随机 96 位 nonce、AAD 和密钥轮换边界已经进入开发规则和数据模型。
- `expired` 已进入任务状态机。
- `retry_of_job_id` 已定义为独立的同园组合自外键。
- 首期时区固定为只读 `Asia/Shanghai`。
- `before_restore`、`restored` 已在数据模型中定义。
- 当前 Word 模板已经脱敏，SHA-256 为 `72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043`，固定引用一致。
- `ai_generation_results` 已明确完整结果最多保留 30 天；采用后可清理正文，但保留必要任务、模型、提示词、Schema、哈希和审计元数据。该项符合 Q8，不是遗漏。

## 3. M0 阻断项

以下事项均须处理；不使用“低优先级”表达，避免误解为可以跳过。

### 3.1 模型与契约

1. `spec.md` FR-031 只描述“带原因的完整快照”，尚未明确完整原因码：
   - `manual_save`
   - `ai_adopted`
   - `archive`
   - `unarchive`
   - `before_restore`
   - `restored`
2. `docs/design/system-architecture.md` 尚未概括并引用 Q13 的完整客户端幂等定义：园所、操作者、HTTP 方法、规范化路由模板和 key 构成 scope；请求 fingerprint 另含规范化实际 path、业务 query 与 canonical JSON body。

### 3.2 模板说明

`templates/teacherplan/一日活动计划系统说明.md` 尚有以下漂移：

- 节假日服务仍使用旧 HTTP 地址，未同步为 `https://timor.tech/api/holiday/info/{YYYY-MM-DD}`。
- 集体活动仍使用 `[[字段名]]` 文本标记，未明确新增环节由 `is_ai_added=true` 表达，正文不得写入“新增”等标记文字。
- 反思仍使用旧字段和 `[[...]]` 标记，未同步 `highlights`、`issues`、`adjustments` 及中文三行映射。
- 未明确三个反思值分别执行 Unicode NFKC 规范化后拼接，按完整 Unicode 码点计数；空格、标点和 emoji 均计入，合计不得超过 200。
- 仍保留 `U+0000–U+FFFF` 及超出范围可能截断或替换的 BMP 旧规则，与完整 Unicode 和 emoji 支持冲突。

### 3.3 状态、证据与分支流程

- `spec.md` 标记为 `Ready for Implementation`，`plan.md` 声称只剩分支授权；Roadmap 和 `combined-audit.md` 明确 M0 仍为 `in_progress`，CONTEXT 与 Tasks 也保留尚未完成的同步步骤和过时流程。各文件的状态语义与证据必须统一。
- T002 仍使用提交 `56cc5e2` 的旧审查证据，不能证明当前文档基线通过最终门禁。
- T003 仍要求选择单一实现分支并 cherry-pick 旧基线，与当前双 Agent 协议冲突。
- 正确流程是：M0 完成并形成最终 docs-only `main` 基线后，经明确授权从同一提交创建 `codex` 和 `trae`，记录相同基线提交 ID；后续新的共享文档提交才分别在授权后 cherry-pick。

### 3.4 静态验证、图谱、历史与最终基线

- README 的 OpenAPI 与契约说明链接错误指向根目录 `contracts/`，当前本地链接门禁失败。
- 文档修订后必须重新验证本地链接、模板结构/样式/哈希和 Spec Kit 一致性。
- graphify 必须在最终文档修订后再次更新和诊断；仅刷新本报告不能提前关闭 M0-G6。
- 当前模板文件已脱敏，但早期模板仍可从 Git 历史访问。历史隐私清理属于独立高风险操作，必须另行授权并验证本地、远程、分支和标签状态。
- 前述门禁未关闭，最终单一目的 docs-only `main` 共享基线尚未形成。

## 4. M0 门禁最终判断

| 门禁 | 当前判断 | 主要原因 |
| --- | --- | --- |
| M0-G1 模型与契约一致 | 未关闭 | FR-031 原因码缺失；系统架构未概括并引用 Q13 客户端幂等定义 |
| M0-G2 模板说明一致 | 未关闭 | 反思字段、结构化标记、NFKC、码点、200 限制、HTTPS 和 BMP 规则存在漂移 |
| M0-G3 模板脱敏与哈希一致 | 当前满足，待复核 | 当前模板已脱敏且固定哈希一致；结构/样式随 G5 复核，历史问题归入 G7 |
| M0-G4 范围与状态一致 | 未关闭 | Roadmap、CONTEXT、Spec、Plan、Tasks 的状态语义、证据和分支流程不一致 |
| M0-G5 静态一致性验证 | 未关闭 | 已发现两个 README 失效链接；修复后还需复核模板结构、样式和哈希 |
| M0-G6 知识图谱一致 | 未关闭 | 最终文档修订后必须重新更新、查询和诊断 |
| M0-G7 历史隐私清理 | 未关闭 | 旧模板历史仍可访问，需独立授权清理并复核全部历史引用 |
| M0-G8 共享基线形成 | 未关闭 | 前置门禁未完成，当前 HEAD 不能作为最终冻结基线 |

## 5. Spec Kit 与 Issue 组织判断

机械覆盖结论沿用双方已核验结果：

- 功能需求 72 项，编号连续，均有任务映射。
- 成功标准 17 项，编号连续，均有任务映射。
- 任务 T001～T165 编号连续、无重复。
- T002 虽已勾选，但其审查证据已经过期，必须在最终基线上重新复核。
- 任务覆盖率只表示计划已经映射需求，不表示功能已实现或 M0 已通过。

M1 进入 `ready` 后，Issue 应按里程碑和可验证纵向切片组织，不机械创建 165 个 Issue：

```text
M<n> 共享父 Issue
├── M<n> Codex 实现子 Issue
└── M<n> Trae 实现子 Issue
```

## 6. 建议解锁顺序

1. 修订模板说明：同步三字段反思、结构化新增标志、NFKC、完整 Unicode 码点、合计 200、HTTPS 地址，并删除 `[[...]]` 和 BMP 旧规则。
2. 在 FR-031 明确完整快照原因码及 `before_restore`、`restored` 恢复顺序。
3. 在系统架构概括并引用 Q13 客户端幂等 scope 与 fingerprint 定义。
4. 修复 README 的两个契约链接。
5. 统一 `combined-audit.md`、Roadmap、CONTEXT、Spec、Plan 和 Tasks 的状态语义、日期、门禁证据与下一步。
6. 重写 T002/T003，删除旧证据和初始 cherry-pick 流程。
7. 重新执行文档链接、模板结构/字体/字号/段落/换行/哈希和 Spec Kit 一致性检查。
8. 更新、查询并诊断 graphify；清理临时产物。
9. 经单独明确授权执行 Git 历史隐私清理，并验证本地、远程、分支和标签状态。
10. 经授权形成最终单一目的 docs-only `main` 基线提交，将 M0 标记为 `complete`、M1 标记为 `ready`。
11. 经再次授权从同一最终提交创建 `codex`、`trae`，记录相同基线提交 ID。
12. 建立 M1 共享父 Issue、Codex 实现子 Issue和 Trae 实现子 Issue，再分别进入独立实现。

## 7. 最终决策与授权边界

当前决策为：**不允许进入编码，不发布 M1 实现 Issue，不执行 T003。**

M0 内容门禁与后续操作授权必须分开：完成 M0 不自动授权提交、历史改写、分支或 Issue 操作。历史清理、最终基线提交和实现分支操作仍须分别获得用户明确授权。

本报告合并后，原 Codex、Trae 阶段性报告不再作为独立当前依据；后续审查统一引用本文和 `docs/faq/combined-audit.md`。

## 8. 修复验证记录

### 8.1 执行范围与基线

- 验证日期：2026-07-13。
- 修复前分支为 `main`，HEAD 为 `f20df3fa30e58d580fbe430e0e94c42d6a2ea4b9`，工作区无已有未提交修改。
- 本轮只修改 Markdown 和 graphify 生成物；未修改 `.docx`，未提交、推送、创建/切换分支、操作 Issue 或改写 Git 历史。
- 修复前与修复后模板 SHA-256 均为 `72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043`。
- 修复前 graphify 为 1610 节点/1256 边；对 `HEAD:graphify-out/graph.json` 执行完整性诊断，缺失端点、悬空边、自环、精确重复边和同端点折叠边均为 0。

### 8.2 实际检查与结果

| 检查 | 实际结果 |
| --- | --- |
| `git diff --check` | 通过，无空白错误 |
| 模板哈希与工作区 | SHA-256 不变；`git diff -- templates/teacherplan/teacherplan.docx` 无输出 |
| Word XML 结构/样式 | 1 张表、19 行、36 个单元格、145 个段落；字体与半磅字号集合可解析且文件字节未变 |
| 模板说明旧规则检索 | 旧 HTTP、文本结构标记、BMP 范围及截断/替换规则无命中 |
| 模板说明新规则检索 | HTTPS、`is_ai_added`、`highlights`、`issues`、`adjustments`、NFKC、200 和 emoji 均命中 |
| Markdown 本地链接 | 缺失数 0 |
| OpenAPI 解析 | OpenAPI 3.1.0，61 个 path、99 个 Schema |
| Spec Kit 前置检查 | `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` 通过 |
| Spec Kit 一致性审查 | 72 个 FR、17 个 SC、T001～T165 均连续且无重复；FR/SC 均有任务映射；无未解释 CRITICAL/HIGH 问题或宪章冲突 |
| graphify 更新 | 阶段 1～3 完整文档语义增量为 1575 节点/1332 边/403 社区；G7/G8 最终状态替换式增量后为 1392 节点/1122 边/391 社区 |
| graphify 收缩调查 | 最终增量按来源移除 6 份长文档的旧候选状态节点，再写入 42 个聚焦当前状态的节点、46 条边和 3 个超边；净收缩来自替换旧的细粒度重复抽取结果，M0 complete、M1 ready、G7/G8 已关闭及 T003 仍待授权等当前概念均可定位 |
| graphify 完整性诊断 | 缺失端点 0、悬空边 0、自环 0、精确重复边 0、同端点折叠边 0 |
| graphify 定向查询 | 已查询 M0-G1～G8、FR-031 快照原因与恢复、Q13 幂等、模板反思/Unicode/`is_ai_added`、T002/T003 双 Agent 流程；相关节点均可定位且无旧单分支结论被当作当前事实 |

上表证据对应的实际命令与脚本入口为：

```bash
git status --short --branch
git rev-parse HEAD
git diff --check
sha256sum templates/teacherplan/teacherplan.docx
git diff --quiet -- templates/teacherplan/teacherplan.docx
rg -n "http://timor.tech|\\[\\[|U\\+0000|U\\+FFFF|截断|替换" templates/teacherplan/一日活动计划系统说明.md
rg -n "https://timor.tech/api/holiday/info|is_ai_added|highlights|issues|adjustments|NFKC|200|emoji" templates/teacherplan/一日活动计划系统说明.md
.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
graphify update .
graphify cluster-only .
graphify query "M0-G1 到 M0-G8 当前状态和关闭条件" --budget 1200
graphify query "FR-031 快照原因码 manual_save ai_adopted archive unarchive before_restore restored 以及恢复顺序" --budget 1200
graphify query "Q13 客户端幂等 scope fingerprint 重放 冲突 内部批量子任务" --budget 1200
graphify query "模板反思 highlights issues adjustments NFKC Unicode 码点 200 emoji is_ai_added" --budget 1200
graphify query "T002 T003 Pre-M1 双 Agent codex trae 同一 main 提交 初始创建分支" --budget 1200
```

内联检查的完整可执行命令如下：

```bash
python3 - <<'PY'
import re
from pathlib import Path

missing = []
for path in Path('.').rglob('*.md'):
    if any(part in {'.git', 'graphify-out'} for part in path.parts):
        continue
    in_fence = False
    for line_number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in re.finditer(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', line):
            raw = match.group(1).strip()
            if not raw or raw.startswith(('#', 'http://', 'https://', 'mailto:')):
                continue
            target = raw.split('#', 1)[0].strip('<>')
            if target and not (path.parent / target).resolve().exists():
                missing.append((str(path), line_number, raw))
print(f'missing_links={len(missing)}')
for item in missing:
    print(item)
PY

python3 - <<'PY'
import re
from pathlib import Path

spec = Path('specs/001-daily-activity-plan/spec.md').read_text(encoding='utf-8')
tasks = Path('specs/001-daily-activity-plan/tasks.md').read_text(encoding='utf-8')
series = {
    'FR': ([int(v) for v in re.findall(r'^- \*\*FR-(\d{3})\*\*:', spec, re.M)], 72),
    'SC': ([int(v) for v in re.findall(r'^- \*\*SC-(\d{3})\*\*:', spec, re.M)], 17),
    'T': ([int(v) for v in re.findall(r'^- \[[ xX]\] T(\d{3})\b', tasks, re.M)], 165),
}
for name, (values, end) in series.items():
    print(name, len(values), values == list(range(1, end + 1)), len(values) == len(set(values)))

covered_fr = set()
covered_sc = set()
for line in tasks.splitlines():
    if '**Requirements covered**:' not in line:
        continue
    for prefix, covered in [('FR', covered_fr), ('SC', covered_sc)]:
        pattern = prefix + r'-(\d{3})(?:–' + prefix + r'-(\d{3}))?'
        for start, end in re.findall(pattern, line):
            covered.update(range(int(start), int(end or start) + 1))
covered_sc.update(int(v) for v in re.findall(r'\bSC-(010|017)\b', tasks))
print('FR_coverage', len(covered_fr), sorted(set(range(1, 73)) - covered_fr))
print('SC_coverage', len(covered_sc), sorted(set(range(1, 18)) - covered_sc))
PY

python3 - <<'PY'
from collections import Counter
from zipfile import ZipFile
from xml.etree import ElementTree as ET

namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile('templates/teacherplan/teacherplan.docx') as archive:
    document = ET.fromstring(archive.read('word/document.xml'))
    styles = ET.fromstring(archive.read('word/styles.xml'))
print('tables', len(document.findall('.//w:tbl', namespace)))
print('rows', len(document.findall('.//w:tr', namespace)))
print('cells', len(document.findall('.//w:tc', namespace)))
print('paragraphs', len(document.findall('.//w:p', namespace)))
fonts = Counter()
for node in document.findall('.//w:rFonts', namespace) + styles.findall('.//w:rFonts', namespace):
    for key, value in node.attrib.items():
        if key.rsplit('}', 1)[-1] in {'ascii', 'hAnsi', 'eastAsia', 'cs'}:
            fonts[value] += 1
sizes = Counter(
    node.attrib.get(f'{{{namespace["w"]}}}val')
    for node in document.findall('.//w:sz', namespace) + styles.findall('.//w:sz', namespace)
)
print('fonts', dict(fonts))
print('half_point_sizes', dict(sizes))
PY

python3 - <<'PY'
from pathlib import Path
import yaml

document = yaml.safe_load(
    Path('specs/001-daily-activity-plan/contracts/openapi.yaml').read_text(encoding='utf-8')
)
print('openapi', document['openapi'])
print('paths', len(document.get('paths', {})))
print('schemas', len(document.get('components', {}).get('schemas', {})))
PY

$(cat graphify-out/.graphify_python) - <<'PY'
import json
import subprocess
from pathlib import Path
from graphify.diagnostics import diagnose_extraction

def diagnose(data):
    return diagnose_extraction(
        {'nodes': data['nodes'], 'edges': data.get('links', []), 'hyperedges': data.get('hyperedges', [])},
        directed=bool(data.get('directed')),
        root='.',
    )

baseline = json.loads(subprocess.check_output(['git', 'show', 'HEAD:graphify-out/graph.json']))
current = json.loads(Path('graphify-out/graph.json').read_text(encoding='utf-8'))
for name, data in [('baseline', baseline), ('current', current)]:
    result = diagnose(data)
    print(name, len(data['nodes']), len(data.get('links', [])))
    for key in (
        'missing_endpoint_edges',
        'dangling_endpoint_edges',
        'self_loop_edges',
        'exact_duplicate_edges',
        'directed_same_endpoint_collapsed_edges',
        'undirected_same_endpoint_collapsed_edges',
    ):
        print(key, result.get(key))
PY
```

当前仓库尚无 `pyproject.toml`、`uv.lock`、业务代码、迁移或自动化测试，因此本轮纯文档修复未伪运行 Ruff、Pyright 或 Pytest。

### 8.3 M0 门禁验证状态

| 门禁 | 候选基线状态 | 证据 |
| --- | --- | --- |
| M0-G1 | 已关闭 | FR-031 原因码/恢复顺序与数据模型、Schema 一致；系统架构已导航 Q13 契约 |
| M0-G2 | 已关闭 | 模板 Markdown 的 HTTPS、结构化新增标记、反思三字段与 Unicode 规则已同步 |
| M0-G3 | 已关闭 | 当前 `.docx` 脱敏、哈希不变，结构/样式由字节不变与 XML 复核证明 |
| M0-G4 | 已关闭 | CONTEXT、Roadmap、Spec、Plan、Tasks 的最终状态一致，T003 为同一 `main` 提交的双分支流程且仍待授权 |
| M0-G5 | 已关闭 | 链接、格式、模板与 Spec Kit 专项验证通过 |
| M0-G6 | 已关闭 | graphify 文档语义已刷新，收缩可解释且完整性诊断全部为 0 |
| M0-G7 | 已关闭 | 已在隔离镜像中删除旧模板路径、回收旧对象并强制更新远端 `main`；含旧个人信息的模板版本在最终可达历史中不存在 |
| M0-G8 | 已关闭 | 清理后恢复脱敏模板与候选文档，重新执行全部专项验证，并形成单一目的最终 docs-only `main` 基线；提交 ID 由 Git 引用和交付记录保存 |

M0-G1～M0-G8 均已关闭，M0 为 `complete`、M1 为 `ready`。该状态不授权进入编码、发布 M1 实现 Issue 或执行 T003；这些操作仍须用户另行明确授权。

### 8.4 G7 历史清理与 G8 基线证据

- 清理前本地与远端只有 `main`，无标签；远端旧基线为 `f20df3f`。
- 在隔离镜像中从全部引用删除旧模板路径，清理备份引用、reflog 和不可达对象后，清理基线为 `d22b600`。
- 清理镜像中旧模板路径历史命中为 0，两个旧路径 blob 在清理阶段均已回收，且 `git fsck --full --no-reflogs --unreachable` 无输出；形成最终基线时只重新加入当前脱敏模板，含旧个人信息的版本保持不可达。
- 对可达 blob 的脱敏特征扫描未发现旧个人信息；未在日志、报告或提交消息中复述个人信息。
- 已将远端 `main` 强制更新为清理基线，随后在清理后的候选克隆恢复当前脱敏模板和经验证的文档修复。
- 已从 GitHub 全新克隆再次核验引用、模板路径历史、敏感旧版本不可达、脱敏扫描、模板哈希和全部专项检查；最终提交 ID 以 `origin/main` 和交付记录为准。
- 历史改写不会自动删除第三方既有克隆、fork 或平台缓存；协作者必须停止使用旧克隆并从最终 `main` 重新克隆。
