# Graph Report - .  (2026-07-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 281 nodes · 291 edges · 35 communities (18 shown, 17 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 28 edges (avg confidence: 0.85)
- Token cost: 1,390 input · 1,447 output

## Graph Freshness
- Built from commit: `50ad0e60`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Architecture & API Design
- Speckit Specification Workflow
- Development Protocols & Gates
- Child Manager Roadmap
- Data & AI Contracts
- Document Baseline & Quality
- Backup Login Implementation
- Shell Script Utilities
- Security & Data Model Review
- Core Technologies & Specs
- Security Model & Defense
- Project Constitution & Boundaries
- GitHub Issue Workflow
- Documentation & Design Workflow
- Feature Creation Script
- Development Tools & AI
- Data Model & Database Schema
- Backup Login Specification
- Migration Order Dependencies
- Alembic Migration Chain
- Prerequisites Check Script
- Plan Setup Script
- Tasks Setup Script
- AI & Prompt Rules
- Git Branch Rules
- Data Model & Isolation
- Fact Sources & Conflict
- Security & Privacy Rules
- Service Boundaries & Dependencies
- Testing Requirements
- External Key Source
- Dev Workflow & Gates
- Governance
- Tech & Security Constraints
- Spec Quality Checklist

## God Nodes (most connected - your core abstractions)
1. `Child Manager Roadmap` - 14 edges
2. `Architecture Decision Index` - 11 edges
3. `Feature Specification: 首期一日活动计划完整闭环` - 9 edges
4. `单一实现开发协议` - 7 edges
5. `Speckit Tasks` - 6 edges
6. `历史合并审查` - 6 edges
7. `安全威胁模型` - 6 edges
8. `Backup Login Implementation Plan` - 6 edges
9. `Child Manager Project Constitution` - 6 edges
10. `Speckit Specify` - 5 edges

## Surprising Connections (you probably didn't know these)
- `一日活动计划需求面` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_020708_请根据现有文档_和旧仓库的文件思考如何撰写_docs_prd_lesson_management_m.md → docs/faq/combined-audit.md
- `ADR 直接文件核对` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_025449_哪些关键架构决策需要独立_adr_哪些已经确认_决策之间有什么依赖.md → docs/faq/combined-audit.md
- `校正后的数据模型边界` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md → docs/faq/combined-audit.md
- `Speckit Tasks to Issues` --semantically_similar_to--> `Implementation Issue Template`  [INFERRED] [semantically similar]
  .agents/skills/speckit-taskstoissues/SKILL.md → .github/ISSUE_TEMPLATE/implementation.yml
- `Retired Dual Agent Protocol` --semantically_similar_to--> `Design to Implement Workflow`  [INFERRED] [semantically similar]
  docs/development/dual-agent-development.md → CONTRIBUTING.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core Principles of Constitution** — specify_memory_constitution_principle_1, specify_memory_constitution_principle_2, specify_memory_constitution_principle_3, specify_memory_constitution_principle_4, specify_memory_constitution_principle_5, specify_memory_constitution_principle_6 [EXTRACTED 1.00]
- **Governance Framework** — specify_memory_constitution_constitution, specify_memory_constitution_technical_constraints, specify_memory_constitution_development_workflow, specify_memory_constitution_governance [EXTRACTED 1.00]
- **项目治理与规则文档** — agents_agents, specify_memory_constitution_constitution [INFERRED 0.90]
- **认证与安全机制** — agents_security [EXTRACTED 1.00]
- **知识与代码分析工具** — agents_graphify, agents_codebase_mcp, agents_tools [INFERRED 0.85]
- **Feature 001: Daily Activity Plan** — specs_001_daily_activity_plan_plan, specs_001_daily_activity_plan_spec, docs_roadmap, milestone_m6, user_story_us4, user_story_us5, user_story_us6, user_story_us7 [INFERRED 0.90]
- **Core Project Components** — context_ai, context_word, context_postgresql, context_redis, context_webauthn [INFERRED 0.80]
- **Speckit Full SDD Lifecycle** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **Web API Worker Boundary Alignment** — docs_adr_adr_0002_separate_web_api_worker_modular_monolith_modular_monolith, docs_adr_adr_0002_separate_web_api_worker_modular_monolith_service_boundaries, docs_design_system_architecture_modular_runtime_architecture, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **Kindergarten Isolation Stack** — docs_adr_adr_0001_cloud_only_kindergarten_isolation, docs_prd_lesson_management_lesson_plan_invariants, docs_design_data_model_tenant_scoped_data_model, docs_design_database_schema_composite_tenant_foreign_keys, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **本地开发隔离模式** — docs_development_local_development_environments_worktree_resource_isolation, docs_development_local_development_environments_loopback_only_dependencies, docs_development_local_development_environments_production_topology_deferral [EXTRACTED 1.00]
- **M0 收敛证据链** — docs_faq_combined_audit_m0_gate_framework, docs______20260713________m0_gate_closure_evidence, docs______20260713____________final_docs_baseline [INFERRED 0.85]
- **身份纵深防御** — docs_security_threat_model_restricted_public_entry, docs_security_threat_model_phishing_resistant_authentication, docs_security_threat_model_password_totp_backup, docs_security_threat_model_emergency_recovery_dual_control [EXTRACTED 1.00]
- **M6 Reliable AI and Group Activity** — specs_001_daily_activity_plan_tasks_m6_ai_and_group_activity, specs_001_daily_activity_plan_contracts_job_state_machine_background_job_state_machine, specs_001_daily_activity_plan_contracts_job_state_machine_ai_preview_adoption, templates_teacherplan_ai_added_step_red_text [EXTRACTED 1.00]
- **Password and TOTP Backup Login Baseline** — specs_002_password_totp_backup_login_spec_backup_login_feature, specs_002_password_totp_backup_login_plan_backup_login_implementation_plan, specs_002_password_totp_backup_login_data_model_backup_auth_data_model, specs_002_password_totp_backup_login_contracts_openapi_backup_login_api_fragment, specs_002_password_totp_backup_login_tasks_backup_login_task_plan [EXTRACTED 1.00]

## Communities (35 total, 17 thin omitted)

### Community 0 - "Architecture & API Design"
Cohesion: 0.07
Nodes (40): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+32 more)

### Community 1 - "Speckit Specification Workflow"
Cohesion: 0.09
Nodes (28): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+20 more)

### Community 2 - "Development Protocols & Gates"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 3 - "Child Manager Roadmap"
Cohesion: 0.12
Nodes (22): Child Manager Roadmap, M0 Shared Baseline, M1 Engineering Skeleton, M2 Authentication Authorization, M3 Initial Settings, M3A Password TOTP Backup Login, M4 AI Model and Prompt Basics, M5 Manual Lesson Plan Loop (+14 more)

### Community 4 - "Data & AI Contracts"
Cohesion: 0.11
Nodes (20): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, API v1 Contract, Optimistic Lock and Idempotency Contract, Trusted NiceGUI BFF Boundary, Daily Activity Plan Data Model (+12 more)

### Community 5 - "Document Baseline & Quality"
Cohesion: 0.11
Nodes (19): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+11 more)

### Community 6 - "Backup Login Implementation"
Cohesion: 0.12
Nodes (19): Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, Password and TOTP Backup Login API Fragment, Backup Enrollment and Authentication Endpoints, Backup Authentication Security Event Endpoint, Backup Authentication Data Model, Encrypted Credentials and Enrollments (+11 more)

### Community 7 - "Shell Script Utilities"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 8 - "Security & Data Model Review"
Cohesion: 0.17
Nodes (13): AI 密钥安全边界, 权威模型与契约收敛, 客户端幂等作用域, 历史合并审查, M0 收敛门禁框架, Word 模板隐私与历史清理, 旧设计不具权威性, 一日活动计划 PRD 查询 (+5 more)

### Community 9 - "Core Technologies & Specs"
Cohesion: 0.24
Nodes (10): AI, Authentication, Authorization, Branch: dev, Branch: docs, Branch: main, PostgreSQL, Redis (+2 more)

### Community 10 - "Security Model & Defense"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 11 - "Project Constitution & Boundaries"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 12 - "GitHub Issue Workflow"
Cohesion: 0.40
Nodes (5): GitHub Issue Deduplication, Speckit Tasks to Issues, Blank Issue Policy, Immutable Docs Baseline, Implementation Issue Template

### Community 13 - "Documentation & Design Workflow"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 15 - "Development Tools & AI"
Cohesion: 0.67
Nodes (4): AGENTS.md 开发规则文件, codebase-memory MCP, Graphify 知识图谱工具, 搜索工具优先级

### Community 16 - "Data Model & Database Schema"
Cohesion: 0.50
Nodes (4): Tenant Scoped Data Model, Composite Kindergarten Foreign Keys, PostgreSQL and SQLite Validation Matrix, PostgreSQL Physical Schema Contract

### Community 17 - "Backup Login Specification"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 18 - "Migration Order Dependencies"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

## Knowledge Gaps
- **89 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `Web、API 与 Worker 服务边界` (2× useful, score=1.416647594) _(code changed — re-verify)_
- `班级与教师配置` (2× useful, score=1.39887405)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `API v1 Contract` connect `Data & AI Contracts` to `Backup Login Implementation`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **What connects `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Architecture & API Design` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._
- **Should `Speckit Specification Workflow` be split into smaller, more focused modules?**
  _Cohesion score 0.08994708994708994 - nodes in this community are weakly interconnected._
- **Should `Development Protocols & Gates` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._
- **Should `Child Manager Roadmap` be split into smaller, more focused modules?**
  _Cohesion score 0.11688311688311688 - nodes in this community are weakly interconnected._
- **Should `Data & AI Contracts` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._