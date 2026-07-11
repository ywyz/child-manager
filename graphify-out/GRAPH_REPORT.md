# Graph Report - .  (2026-07-11)

## Corpus Check
- Corpus is ~2,394 words - fits in a single context window. You may not need a graph.

## Summary
- 36 nodes · 29 edges · 12 communities (5 shown, 7 thin omitted)
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.92)
- Token cost: 20,350 input · 6,820 output

## Community Hubs (Navigation)
- [[_COMMUNITY_核心文档与模板|核心文档与模板]]
- [[_COMMUNITY_规则查询与格式|规则查询与格式]]
- [[_COMMUNITY_上下文与 AI 边界|上下文与 AI 边界]]
- [[_COMMUNITY_旧架构排除|旧架构排除]]
- [[_COMMUNITY_AI 提示词管线|AI 提示词管线]]
- [[_COMMUNITY_教案业务规则|教案业务规则]]
- [[_COMMUNITY_服务架构边界|服务架构边界]]
- [[_COMMUNITY_Word 导出保护|Word 导出保护]]
- [[_COMMUNITY_园所数据隔离|园所数据隔离]]
- [[_COMMUNITY_分支当前状态|分支当前状态]]
- [[_COMMUNITY_共同实施路线|共同实施路线]]
- [[_COMMUNITY_旧仓库参考|旧仓库参考]]

## God Nodes (most connected - your core abstractions)
1. `CONTEXT.md 补充建议查询` - 6 edges
2. `AGENTS.md 补充建议查询` - 5 edges
3. `一日活动计划系统说明` - 4 edges
4. `不继承旧仓库架构` - 4 edges
5. `Child Manager 项目上下文` - 3 edges
6. `AI 生成与提示词规则` - 2 edges
7. `Child Manager 幼儿园教育管理系统` - 2 edges
8. `集体活动结构化` - 2 edges
9. `AI 生成边界` - 2 edges
10. `日期选择与校验` - 2 edges

## Surprising Connections (you probably didn't know these)
- `目标服务架构` --semantically_similar_to--> `Web、API 与 Worker 服务边界`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `一日活动计划` --semantically_similar_to--> `一日活动计划业务不变量`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `AI 提示词管理子系统` --semantically_similar_to--> `AI 生成与提示词规则`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `Word 导出` --semantically_similar_to--> `Word 模板保护与导出验证`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `异步 AI 生成管线` --conceptually_related_to--> `AI 生成与提示词规则`  [INFERRED]
  README.md → AGENTS.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **一日活动计划一致性控制** — agents_daily_plan_invariants, readme_daily_activity_plan, templates_teacherplan_date_validation [INFERRED 0.95]
- **AI 内容生成契约** — agents_ai_generation_rules, readme_async_ai_pipeline, readme_prompt_management, templates_teacherplan_collective_activity_structuring [INFERRED 0.95]
- **Word 导出保真约束** — agents_word_template_protection, readme_word_export, templates_teacherplan_red_inserted_segment [INFERRED 0.95]

## Communities (12 total, 7 thin omitted)

### Community 0 - "核心文档与模板"
Cohesion: 0.33
Nodes (7): Child Manager Agent 开发规则, Child Manager 项目上下文, Child Manager 幼儿园教育管理系统, 集体活动结构化, 日期选择与校验, AI 新增环节红色字体, 一日活动计划系统说明

### Community 1 - "规则查询与格式"
Cohesion: 0.29
Nodes (7): 班级与教师配置, 日期选择与校验, 需要直接比较文件, AGENTS.md 补充建议查询, Word 格式边界, 日期选择与校验, Word 导出格式控制

### Community 2 - "上下文与 AI 边界"
Cohesion: 0.40
Nodes (5): AI 生成边界, AI 教案结构化, 配置, 区分已确认设计与已实现状态, CONTEXT.md 补充建议查询

### Community 3 - "旧架构排除"
Cohesion: 0.50
Nodes (4): 集成式 NiceGUI 架构, 不继承旧仓库架构, 本地优先架构, MySQL

### Community 4 - "AI 提示词管线"
Cohesion: 0.67
Nodes (3): AI 生成与提示词规则, 异步 AI 生成管线, AI 提示词管理子系统

## Knowledge Gaps
- **16 isolated node(s):** `Child Manager Agent 开发规则`, `园所数据隔离`, `一日活动计划业务不变量`, `共同实施路线`, `当前仓库与分支状态` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CONTEXT.md 补充建议查询` connect `上下文与 AI 边界` to `规则查询与格式`, `旧架构排除`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `不继承旧仓库架构` connect `旧架构排除` to `上下文与 AI 边界`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `AGENTS.md 补充建议查询` connect `规则查询与格式` to `上下文与 AI 边界`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **What connects `Child Manager Agent 开发规则`, `Web、API 与 Worker 服务边界`, `园所数据隔离` to the rest of the system?**
  _22 weakly-connected nodes found - possible documentation gaps or missing edges._