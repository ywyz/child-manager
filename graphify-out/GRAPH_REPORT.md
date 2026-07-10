# Graph Report - .  (2026-07-10)

## Corpus Check
- Corpus is ~236 words - fits in a single context window. You may not need a graph.

## Summary
- 20 nodes · 23 edges · 5 communities (4 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.9)
- Token cost: 2,486 input · 3,854 output

## Community Hubs (Navigation)
- [[_COMMUNITY_计划配置与校验|计划配置与校验]]
- [[_COMMUNITY_AI 内容生成|AI 内容生成]]
- [[_COMMUNITY_教案结构与导出|教案结构与导出]]
- [[_COMMUNITY_游戏区域设置|游戏区域设置]]
- [[_COMMUNITY_项目入口|项目入口]]

## God Nodes (most connected - your core abstractions)
1. `AI内容生成` - 7 edges
2. `一日活动计划系统说明` - 4 edges
3. `日期选择与校验` - 4 edges
4. `本地版与Cloud版设置` - 4 edges
5. `学期配置` - 3 edges
6. `教案结构化` - 3 edges
7. `室内区域游戏` - 3 edges
8. `下午户外游戏` - 3 edges
9. `班级与教师配置` - 2 edges
10. `既有计划调取` - 2 edges

## Surprising Connections (you probably didn't know these)
- `学期配置` --shares_data_with--> `本地版与Cloud版设置`  [EXTRACTED]
  templates/teacherplan/一日活动计划系统说明.md → templates/teacherplan/一日活动计划系统说明.md  _Bridges community 0 → community 3_
- `下午户外游戏` --references--> `AI内容生成`  [EXTRACTED]
  templates/teacherplan/一日活动计划系统说明.md → templates/teacherplan/一日活动计划系统说明.md  _Bridges community 1 → community 3_
- `一日活动反思` --references--> `AI内容生成`  [EXTRACTED]
  templates/teacherplan/一日活动计划系统说明.md → templates/teacherplan/一日活动计划系统说明.md  _Bridges community 1 → community 0_
- `教案结构化` --references--> `AI内容生成`  [EXTRACTED]
  templates/teacherplan/一日活动计划系统说明.md → templates/teacherplan/一日活动计划系统说明.md  _Bridges community 1 → community 2_

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **AI生成的一日活动计划内容** — templates_teacherplan__morning_activity, templates_teacherplan__morning_conversation, templates_teacherplan__group_activity, templates_teacherplan__indoor_area_game, templates_teacherplan__afternoon_outdoor_game, templates_teacherplan__daily_activity_reflection, templates_teacherplan__ai_content_generation [EXTRACTED 1.00]
- **配置驱动的计划上下文** — templates_teacherplan__semester_configuration, templates_teacherplan__class_and_teacher_configuration, templates_teacherplan__local_and_cloud_settings, templates_teacherplan__date_selection_and_validation [EXTRACTED 1.00]

## Communities (5 total, 1 thin omitted)

### Community 0 - "计划配置与校验"
Cohesion: 0.29
Nodes (8): chinesecalendar库, 班级与教师配置, 一日活动计划系统说明, 一日活动反思, 日期选择与校验, 既有计划调取, 学期配置, Timor节假日API

### Community 1 - "AI 内容生成"
Cohesion: 0.50
Nodes (4): 幼儿年龄适配内容, AI内容生成, 晨间活动, 晨间谈话

### Community 2 - "教案结构与导出"
Cohesion: 0.50
Nodes (4): AI新增活动环节, 集体活动, 教案结构化, Word导出格式控制

### Community 3 - "游戏区域设置"
Cohesion: 1.00
Nodes (3): 下午户外游戏, 室内区域游戏, 本地版与Cloud版设置

## Knowledge Gaps
- **7 isolated node(s):** `child-manager`, `chinesecalendar库`, `Timor节假日API`, `晨间活动`, `晨间谈话` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AI内容生成` connect `AI 内容生成` to `计划配置与校验`, `教案结构与导出`, `游戏区域设置`?**
  _High betweenness centrality (0.559) - this node is a cross-community bridge._
- **Why does `教案结构化` connect `教案结构与导出` to `AI 内容生成`?**
  _High betweenness centrality (0.275) - this node is a cross-community bridge._
- **What connects `child-manager`, `chinesecalendar库`, `Timor节假日API` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._