# Graph Report - .  (2026-08-02)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 774 nodes · 1141 edges · 125 communities (48 shown, 77 thin omitted)
- Extraction: 85% EXTRACTED · 14% INFERRED · 1% AMBIGUOUS · INFERRED: 160 edges (avg confidence: 0.82)
- Token cost: 6,285 input · 14,303 output

## Graph Freshness
- Built from commit: `47eae46c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Architecture Decision Records
- Pre-Coding Review
- Password TOTP Backup Auth
- Core Data Entities
- Spec Kit Skills
- Branch & Issue Workflow
- Security & Auth Architecture
- AI Lesson Plan Generation
- Core Application Components
- Development Workflow Rules
- Milestone Completion Status
- Tech Stack Dependencies
- Spec Kit Shell Utilities
- Completed Milestones
- Identity & Auth Tables
- Repository Workflow Reset
- Application Architecture Principles
- Branch State Snapshot
- System Design Decisions
- Delivery Phases & Gates
- Core Data Models
- Lesson Plan Data Models
- Lesson Planning Features
- AI Prompt Pipeline
- Runtime Architecture
- API Contracts & Auth
- Production Deployment Review
- Implementation Task Plan
- Engineering Roadmap & Rules
- Database Migrations
- Background Job Processing
- AI Prompt Governance
- Architecture Exploration
- Project Context & Handoff
- Milestone Roadmap Status
- M7 M8 Acceptance Gates
- Lesson Plan PRD
- Feature Script Utilities
- Word Export Jobs
- Authentication Flows
- Task List Constraints
- TDD Delivery Strategy
- US4 AI Batch Implementation
- US5 DOCX Import Implementation
- Foundational Setup Tasks
- WebAuthn Identity Implementation
- Settings Implementation
- Manual Lesson Plan Implementation
- AI Model & Prompt Implementation
- ADR Decision Review
- Prerequisites Check Script
- Setup Plan Script
- Setup Tasks Script
- Tenant Isolation & Authorization
- API Application
- FastAPI Routes & Middleware
- Export History Component
- NiceGUI Web BFF
- Audit Web Page
- Plans Web Page
- Worker Actors
- Dramatiq Worker Infrastructure
- Worker Scheduler
- Data Model Documentation
- Database Schema Documentation
- Backend Package
- Contracts Package
- System Architecture Documentation
- Integrations Module
- Local Development Environments
- Workflow Reset Notes
- Lesson Management PRD
- Issue Template Configuration
- Audit Events
- Audit Models
- Audit Repository & Service
- Audit Repository
- Audit Service
- Bootstrap Admin CLI
- Alembic Migrations
- Word Exports Migration
- Export Models
- Export Repository
- Export Business Rules
- Exports Service
- Identity & Session Package
- Vendor-Neutral AI Client
- Calendar Workday Service
- Calendar Service
- AI Key Encryption
- Export Storage
- DOCX Safe Extraction
- AI Results Repository
- AI Execution Runner
- Jobs Dispatcher
- Background Jobs Infrastructure
- Job Retry Policy
- Jobs Service
- AI Adoption Transaction
- AI Generation Batch
- Group Activity AI
- Lesson Plan Archive/Restore
- Lesson Reflection Generation
- Lesson Plans Service
- Prompt Catalog and Rendering
- Whitelist Prompt Renderer
- Prompts Service
- Settings Archives
- Settings Service
- Audit Contracts
- Common Contracts
- Export Contracts
- Identity Contracts
- Jobs Contracts
- Job Contract Definitions
- Lesson Plan Contracts
- Prompt Contracts
- Settings Contracts
- OpenAPI Contract
- Contracts README
- Daily Activity Plan OpenAPI
- Page IA Research
- Specification Quality Checklist
- Password TOTP Backup Login
- Teacher Plan Word Template

## God Nodes (most connected - your core abstractions)
1. `Combined Audit Conclusion (Q1–Q26)` - 43 edges
2. `AGENTS.md 开发规则` - 38 edges
3. `001 研究 research.md` - 37 edges
4. `Security Threat Model` - 29 edges
5. `2026-07-14 编码前审查报告（Codex + Trae 收敛版）` - 28 edges
6. `Spec Kit Constitution` - 27 edges
7. `M3A: Password+TOTP Backup Login` - 24 edges
8. `System Architecture` - 23 edges
9. `20260713 Pre-Coding Review Report (Codex + Trae)` - 21 edges
10. `2026-07-14 编码前审查解决方案` - 21 edges

## Surprising Connections (you probably didn't know these)
- `WebAuthn 通行密钥认证` --semantically_similar_to--> `WebAuthn/备用登录安全约束`  [INFERRED] [semantically similar]
  docs/ADR/ADR-0010-restricted-public-entry-passkey-authentication-and-recovery.md → .specify/memory/constitution.md
- `API v1 Contract Overview` --references--> `Audit Contracts`  [INFERRED]
  specs/001-daily-activity-plan/contracts/README.md → packages/contracts/audit.py
- `API v1 Contract Overview` --references--> `Exports Contracts (exports.py)`  [INFERRED]
  specs/001-daily-activity-plan/contracts/README.md → packages/contracts/exports.py
- `API v1 OpenAPI Specification 2.1.0` --references--> `Audit API Router`  [INFERRED]
  specs/001-daily-activity-plan/contracts/openapi.yaml → apps/api/routers/audit.py
- `API v1 OpenAPI Specification 2.1.0` --references--> `Auth API Router`  [INFERRED]
  specs/001-daily-activity-plan/contracts/openapi.yaml → apps/api/routers/auth.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **首期一日活动计划完整闭环** — specs_001_daily_activity_plan_spec_secure_initialization, specs_001_daily_activity_plan_spec_necessary_settings, specs_001_daily_activity_plan_spec_manual_lesson_plan_loop, specs_001_daily_activity_plan_spec_prompt_lifecycle, specs_001_daily_activity_plan_spec_four_column_ai_batch, specs_001_daily_activity_plan_spec_group_activity_import, specs_001_daily_activity_plan_spec_fixed_word_export, specs_001_daily_activity_plan_spec_audit_events [EXTRACTED 1.00]
- **Web API Worker 三个独立运行单元** — specs_001_daily_activity_plan_plan_nicegui_web, specs_001_daily_activity_plan_plan_fastapi_api, specs_001_daily_activity_plan_plan_dramatiq_worker [EXTRACTED 1.00]
- **事务化冻结受理模式** — specs_001_daily_activity_plan_plan_postgresql_authoritative_state, specs_001_daily_activity_plan_plan_transactional_reflection_intake, specs_001_daily_activity_plan_plan_transactional_export_intake, specs_001_daily_activity_plan_plan_prompt_test_revision_freeze, specs_001_daily_activity_plan_plan_ai_result_placeholder [INFERRED 0.85]
- **已完成交付范围 T001–T141** — specs_001_daily_activity_plan_tasks_phase_setup, specs_001_daily_activity_plan_tasks_phase_foundational, specs_001_daily_activity_plan_tasks_m2, specs_001_daily_activity_plan_tasks_m3, specs_001_daily_activity_plan_tasks_us2, specs_001_daily_activity_plan_tasks_us3, specs_001_daily_activity_plan_tasks_us4, specs_001_daily_activity_plan_tasks_us5, specs_001_daily_activity_plan_tasks_us6, specs_001_daily_activity_plan_tasks_t001_t008, specs_001_daily_activity_plan_tasks_t009_t012, specs_001_daily_activity_plan_tasks_t013_t019, specs_001_daily_activity_plan_tasks_t020, specs_001_daily_activity_plan_tasks_t021_t025, specs_001_daily_activity_plan_tasks_t026_t034, specs_001_daily_activity_plan_tasks_t035, specs_001_daily_activity_plan_tasks_t036_t039, specs_001_daily_activity_plan_tasks_t040_t044, specs_001_daily_activity_plan_tasks_t045, specs_001_daily_activity_plan_tasks_t046_t051, specs_001_daily_activity_plan_tasks_t052_t060, specs_001_daily_activity_plan_tasks_t061, specs_001_daily_activity_plan_tasks_t062_t072, specs_001_daily_activity_plan_tasks_t073_t085, specs_001_daily_activity_plan_tasks_t086, specs_001_daily_activity_plan_tasks_t087_t097, specs_001_daily_activity_plan_tasks_t098_t109, specs_001_daily_activity_plan_tasks_t110, specs_001_daily_activity_plan_tasks_t111, specs_001_daily_activity_plan_tasks_t112_t117, specs_001_daily_activity_plan_tasks_t118_t125, specs_001_daily_activity_plan_tasks_t126, specs_001_daily_activity_plan_tasks_t127_t132, specs_001_daily_activity_plan_tasks_t133_t140, specs_001_daily_activity_plan_tasks_t141 [EXTRACTED 1.00]
- **M8 ready 与未开始任务 T142–T169** — specs_001_daily_activity_plan_tasks_us7, specs_001_daily_activity_plan_tasks_polish, specs_001_daily_activity_plan_tasks_t142_t149, specs_001_daily_activity_plan_tasks_t150_t157, specs_001_daily_activity_plan_tasks_t158, specs_001_daily_activity_plan_tasks_t159_t162, specs_001_daily_activity_plan_tasks_t163_t166, specs_001_daily_activity_plan_tasks_t167_t169 [EXTRACTED 1.00]
- **固定阶段依赖链** — specs_001_daily_activity_plan_tasks_phase_setup, specs_001_daily_activity_plan_tasks_phase_foundational, specs_001_daily_activity_plan_tasks_m2, specs_001_daily_activity_plan_tasks_m3, specs_001_daily_activity_plan_tasks_m3a, specs_001_daily_activity_plan_tasks_us2, specs_001_daily_activity_plan_tasks_us3, specs_001_daily_activity_plan_tasks_us4, specs_001_daily_activity_plan_tasks_us5, specs_001_daily_activity_plan_tasks_us6, specs_001_daily_activity_plan_tasks_us7, specs_001_daily_activity_plan_tasks_polish [EXTRACTED 1.00]
- **M0 到 M9 阶段依赖与状态生命周期** — docs_roadmap_status_vocabulary, docs_roadmap_milestone_dependency_chain, docs_roadmap_m0_complete, docs_roadmap_m1_complete, docs_roadmap_m2_complete, docs_roadmap_m3_complete, docs_roadmap_m3a_complete, docs_roadmap_m5_complete, docs_roadmap_m4_complete, docs_roadmap_m6_complete, docs_roadmap_m7_complete, docs_roadmap_m8_ready, docs_roadmap_m9_pending [EXTRACTED 1.00]
- **M8 端到端功能验收证据集合** — specs_001_daily_activity_plan_quickstart_settings_acceptance, specs_001_daily_activity_plan_quickstart_manual_plan_acceptance, specs_001_daily_activity_plan_quickstart_ai_job_acceptance, specs_001_daily_activity_plan_quickstart_reflection_acceptance, specs_001_daily_activity_plan_quickstart_docx_security, specs_001_daily_activity_plan_quickstart_word_export_acceptance, specs_001_daily_activity_plan_quickstart_workday_degradation, specs_001_daily_activity_plan_quickstart_audit_privacy, specs_001_daily_activity_plan_quickstart_api_contract, specs_001_daily_activity_plan_quickstart_m8_report [EXTRACTED 1.00]
- **M7 complete 到 M8 ready 的跨文档状态收敛** — readme_m7_completion_evidence, readme_m8_ready, context_m7_complete, context_m8_ready, context_next_task_t142, docs_roadmap_m7_evidence, docs_roadmap_m8_ready, docs_roadmap_next_action_t142, specs_001_daily_activity_plan_quickstart_current_state, specs_001_daily_activity_plan_quickstart_m8_report [INFERRED 0.95]
- **Spec Kit Specification→Plan→Tasks→Implement Workflow** — agents_spec_kit_skills, agents_skills_speckit_specify_skill, agents_skills_speckit_clarify_skill, agents_skills_speckit_plan_skill, agents_skills_speckit_tasks_skill, agents_skills_speckit_analyze_skill, agents_skills_speckit_checklist_skill, agents_skills_speckit_implement_skill, agents_skills_speckit_converge_skill, agents_skills_speckit_constitution_skill, agents_skills_speckit_taskstoissues_skill [EXTRACTED 0.90]
- **Spec Kit 全生命周期流程 (specify→plan→tasks→implement)** — specify_workflows_speckit_workflow_specify_step, specify_workflows_speckit_workflow_review_spec_gate, specify_workflows_speckit_workflow_plan_step, specify_workflows_speckit_workflow_review_plan_gate, specify_workflows_speckit_workflow_tasks_step, specify_workflows_speckit_workflow_implement_step [EXTRACTED 1.00]
- **宪章六大核心原则** — specify_memory_constitution_source_of_truth, specify_memory_constitution_service_boundary, specify_memory_constitution_kindergarten_isolation, specify_memory_constitution_authoritative_state, specify_memory_constitution_teacher_control, specify_memory_constitution_executable_verification [EXTRACTED 1.00]
- **Identity, Authentication and Recovery Flow** — docs_design_database_schema_users, docs_design_database_schema_webauthn_credentials, docs_design_database_schema_webauthn_challenges, docs_design_database_schema_backup_auth_credentials, docs_design_database_schema_backup_auth_enrollments, docs_design_database_schema_bootstrap_initializations, docs_design_database_schema_account_invitations, docs_design_database_schema_recovery_codes, docs_design_database_schema_account_recovery_requests, docs_design_database_schema_identity_verification_approvals, docs_design_database_schema_roles, docs_design_database_schema_user_roles, docs_design_database_schema_refresh_tokens [EXTRACTED 0.90]
- **AI-Assisted Daily Activity Plan Generation and Adoption Flow** — docs_design_database_schema_daily_activity_plans, docs_design_database_schema_daily_activity_plan_snapshots, docs_design_database_schema_lesson_plan_sources, docs_design_database_schema_background_jobs, docs_design_database_schema_ai_generation_results, docs_design_database_schema_prompt_definitions, docs_design_database_schema_prompt_versions, docs_design_database_schema_prompt_test_runs, docs_design_database_schema_ai_model_profiles [EXTRACTED 0.85]
- **Child Manager Cloud Runtime Deployment Units** — docs_design_system_architecture_web_bff, docs_design_system_architecture_api, docs_design_system_architecture_worker, docs_design_system_architecture_contracts, docs_design_system_architecture_backend, docs_design_system_architecture_postgresql, docs_design_system_architecture_redis [EXTRACTED 0.90]
- **M1 双 Agent 独立实现与 Issue 层级交付结构** — concept_branch_codex, concept_branch_trae, concept_issue_1, concept_issue_2, concept_issue_3 [EXTRACTED 0.90]
- **M1 已确认技术基线** — concept_tech_python, concept_tech_uv, concept_tech_nicegui, concept_tech_fastapi, concept_tech_dramatiq, concept_tech_postgresql, concept_tech_redis, concept_tech_alembic, concept_tech_docker_compose [EXTRACTED 0.90]
- **M2 认证授权与身份审计交付结构** — concept_issue_4, concept_issue_5, concept_issue_6, concept_tasks_t021_t035, specs_001_daily_activity_plan_contracts_openapi_doc, docs_adr_adr_0004_same_origin_cookie_authentication [EXTRACTED 0.90]
- **M0 Quality Gates G1–G8** — docs_faq_combined_audit_m0_g1_model_contract_alignment, docs_faq_combined_audit_m0_g2_template_instructions, docs_faq_combined_audit_m0_g3_template_hash, docs_faq_combined_audit_m0_g4_scope_status_alignment, docs_faq_combined_audit_m0_g5_static_validation, docs_faq_combined_audit_m0_g6_graph_consistency, docs_faq_combined_audit_m0_g7_history_privacy_cleanup, docs_faq_combined_audit_m0_g8_shared_baseline, docs_faq_combined_audit_m0_milestone [EXTRACTED 1.00]
- **First-Phase Threat Scenarios** — docs_security_threat_model_scenario_public_scanning, docs_security_threat_model_scenario_phishing, docs_security_threat_model_scenario_invite_leak, docs_security_threat_model_scenario_passkey_loss, docs_security_threat_model_scenario_last_admin, docs_security_threat_model_scenario_device_theft, docs_security_threat_model_scenario_export_leak [EXTRACTED 0.95]
- **M0 Remediation Pipeline (A→D2→M1)** — docs_shenchabaogao_20260713_xiufufangan_task_a, docs_shenchabaogao_20260713_xiufufangan_task_b, docs_shenchabaogao_20260713_xiufufangan_task_c, docs_shenchabaogao_20260713_xiufufangan_task_d1, docs_shenchabaogao_20260713_xiufufangan_task_d2, docs_shenchabaogao_20260713_xiufufangan_m1_launch [EXTRACTED 0.95]
- **M0 内容门禁 G1–G8（2026-07-14 全部关闭）** — gate_m0_g1, gate_m0_g2, gate_m0_g3, gate_m0_g4, gate_m0_g5, gate_m0_g6, gate_m0_g7, gate_m0_g8 [EXTRACTED 0.95]
- **M1 Issue 层级：一个共享父 Issue + Codex/Trae 两个实现子 Issue** — issue_m1_parent, issue_m1_codex, issue_m1_trae [EXTRACTED 0.95]
- **M1 启动授权链：Issue 创建 → T003 建分支 → 实现（各自独立授权，互不推导）** — issue_m1_parent, branch_codex, branch_trae [INFERRED 0.85]
- **身份认证与会话族 (WebAuthn + 备用认证 + 邀请恢复 + Refresh 轮换)** — specs_001_daily_activity_plan_data_model_users, specs_001_daily_activity_plan_data_model_webauthn_credentials, specs_001_daily_activity_plan_data_model_webauthn_challenges, specs_001_daily_activity_plan_data_model_backup_auth_credentials, specs_001_daily_activity_plan_data_model_backup_auth_enrollments, specs_001_daily_activity_plan_data_model_bootstrap_initializations, specs_001_daily_activity_plan_data_model_account_invitations, specs_001_daily_activity_plan_data_model_recovery_codes, specs_001_daily_activity_plan_data_model_account_recovery_requests, specs_001_daily_activity_plan_data_model_identity_verification_approvals, specs_001_daily_activity_plan_data_model_user_roles, specs_001_daily_activity_plan_data_model_roles, specs_001_daily_activity_plan_data_model_refresh_tokens [EXTRACTED 0.90]
- **AI 生成与提示词测试管线 (PostgreSQL 权威任务状态驱动)** — specs_001_daily_activity_plan_data_model_ai_model_profiles, specs_001_daily_activity_plan_data_model_ai_model_profile_capabilities, specs_001_daily_activity_plan_data_model_prompt_definitions, specs_001_daily_activity_plan_data_model_prompt_versions, specs_001_daily_activity_plan_data_model_prompt_test_runs, specs_001_daily_activity_plan_data_model_background_jobs, specs_001_daily_activity_plan_data_model_ai_generation_results, specs_001_daily_activity_plan_data_model_daily_activity_plans, specs_001_daily_activity_plan_data_model_daily_activity_plan_snapshots [EXTRACTED 0.90]
- **Password+TOTP Backup Authentication Flow (M3A)** — packages_backend_identity_passwords_passwords_module, packages_backend_identity_totp_totp_module, packages_backend_identity_secret_encryption_secret_encryption_module, packages_backend_identity_repository_repository_module, packages_backend_identity_service_service_module, packages_contracts_identity_identity_module, apps_api_routers_auth_router, apps_web_pages_auth_page [EXTRACTED 0.90]

## Communities (125 total, 77 thin omitted)

### Community 0 - "Architecture Decision Records"
Cohesion: 0.06
Nodes (70): ADR-0001 Cloud Only, ADR-0002 独立 Web/API/Worker 模块化单体, background_job 权威任务状态机, ADR-0003 PostgreSQL 权威任务状态 + Dramatiq/Redis, ADR-0004 同源 Cookie 认证, 提示词草稿/发布/回滚生命周期, ADR-0005 AI 供应商中立与提示词系统, ADR-0006 固定 Word 模板导出边界 (+62 more)

### Community 1 - "Pre-Coding Review"
Cohesion: 0.09
Nodes (45): codex 实现分支（待授权创建）, main 分支（docs-only 基线）, trae 实现分支（待授权创建）, AI 生成与提示词规则, 班级与教师配置, 一日活动计划, 日期选择与校验, 教案结构化 (+37 more)

### Community 2 - "Password TOTP Backup Auth"
Cohesion: 0.11
Nodes (39): ADR-0010 Identity Rewrite, ADR-0011 Password+TOTP Backup, API Dependencies, API OpenAPI Generation, Auth API Router, audit_events Table, authentication_method Enum, backup_auth_credentials Table (+31 more)

### Community 3 - "Core Data Entities"
Cohesion: 0.08
Nodes (39): Account Invitations, Account Recovery Requests, Age Groups, AI Generation Results, AI Model Profile Capabilities, AI Model Profiles, Audit Events, Background Jobs (+31 more)

### Community 4 - "Spec Kit Skills"
Cohesion: 0.12
Nodes (35): speckit-analyze Skill, speckit-checklist Skill, speckit-clarify Skill, speckit-constitution Skill, speckit-converge Skill, speckit-implement Skill, speckit-plan Skill, speckit-specify Skill (+27 more)

### Community 5 - "Branch & Issue Workflow"
Cohesion: 0.11
Nodes (35): codex 分支 (历史双实现线), dev 分支 (唯一实现与集成), docs 分支 (文档与契约), main 分支 (稳定发布基线), trae 分支 (历史双实现线), Codex Agent, Dev 本地档位 (端口/Compose/数据库隔离), graphify 知识图谱工具与 graphify-out 输出 (+27 more)

### Community 6 - "Security & Auth Architecture"
Cohesion: 0.12
Nodes (29): ADR-0010 Restricted Public Entry & Passkey Auth, ADR-0011 Password+TOTP Backup Login, ADR-0009 Defer Production Deployment Until Feature Complete, Technology Stack (Python 3.14, NiceGUI, FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic), Security Threat Model, AES-256-GCM Secret Encryption, Argon2id Password Hashing, External AI Service (+21 more)

### Community 7 - "AI Lesson Plan Generation"
Cohesion: 0.08
Nodes (28): 栏目级 AI 异步生成与人工采用合同, OpenAI 兼容 AI 模型档案, 学期周次与工作日软提示规则, 首期一日活动计划闭环, 游戏观察 一对一倾听 照片视觉与对象存储后续边界, 教案唯一性 归档 快照与乐观锁不变量, M4 docs c9401c5a189fcc10ee2e15903a186c06b94cea30 dev 8695b04161ea96bddc31c3bfeab2e0957ef68562 main b7676c27d07adc5eca1f0c397217780367481e9c, M6 T087-T126 main beb8784cd5dd5cb2f1ddd39a46f7d0bff0ab3098 Quality 30631050997 attempt 2 (+20 more)

### Community 8 - "Core Application Components"
Cohesion: 0.12
Nodes (24): Audit API Router, Exports API Router, Web API Client, Auth Web Page, word.export Actor, chinesecalendar Library, CSRF & Origin Verification, Daily Reflection (+16 more)

### Community 9 - "Development Workflow Rules"
Cohesion: 0.13
Nodes (22): AGENTS.md 开发规则, AES-256-GCM Key Encryption, Autosave / Snapshot Rules, dev Branch, docs Branch, main Branch, codebase-memory MCP, codegraph (+14 more)

### Community 10 - "Milestone Completion Status"
Cohesion: 0.14
Nodes (21): M0 共同基线 c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7, M6 Review main@b7676c27d07adc5eca1f0c397217780367481e9c→dev@d654b704d1bd0653f7d0209ac58665090a934311 PASS；main@beb8784cd5dd5cb2f1ddd39a46f7d0bff0ab3098；run 30631050997 attempt 2, Issue #12 completed；docs@47eae46c6efec2e7596063bea2fc3352c2ece189；dev@ba9251d2ee74c8959ea53e888cd5a030571fdc69 run 30697998054；main@70ba267fab3a3a0e5c43dc25cb510b4acdd6b244 run 30698318868；729 passed, Issue #10 completed；docs@c9401c5a189fcc10ee2e15903a186c06b94cea30；Review dev@8695b04161ea96bddc31c3bfeab2e0957ef68562 PASS；runs 30235090100/30235439229；main@b7676c27d07adc5eca1f0c397217780367481e9c, US5 dev@32d3c102152848f7488da036ddada461b3d8d3ab；run 30602225731；49 passed、56 passed、完整 666 passed；恶意样本残留 0, US1/M2 安全身份：T021–T035，complete, US1/M3 必要设置：T036–T045，complete, US1/M3A 密码与 TOTP 备用登录：独立 specs/002 T001–T034 (+13 more)

### Community 11 - "Tech Stack Dependencies"
Cohesion: 0.18
Nodes (19): Alembic 迁移, Dramatiq 2 + Redis, FastAPI, HTTPX (外部 HTTP 客户端), NiceGUI 3.x, 旧仓库 adapt_client.py (新增环节参考), 旧仓库 generate_client.py (提示词措辞参考), 旧仓库 lesson_plan_client.py (拆分参考) (+11 more)

### Community 12 - "Spec Kit Shell Utilities"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 13 - "Completed Milestones"
Cohesion: 0.13
Nodes (16): M0 共享设计基线 complete, M1 工程骨架与质量基线 complete, M2 认证授权与身份审计 complete, M2 docs bb025b2 dev fb4f076 Quality 30006114394, M3 首期必要设置 complete, M3 docs bd98a1a dev f5f0084, M3A 密码与 TOTP 备用登录 complete, M3A docs 2f7894c dev 6a9e269 Quality 30161645948 (+8 more)

### Community 14 - "Identity & Auth Tables"
Cohesion: 0.15
Nodes (15): PyJWT (HS256 Access Token), account_invitations 账号邀请, account_recovery_requests 恢复请求, backup_auth_credentials 密码+TOTP 备用材料, backup_auth_enrollments 备用绑定流程, bootstrap_initializations 首位管理员初始化, identity_verification_approvals 身份核验批准, recovery_codes 离线恢复码 (+7 more)

### Community 15 - "Repository Workflow Reset"
Cohesion: 0.27
Nodes (13): Repository Workflow Reset 2026-07-21, Codex Agent, dev Branch (Codex implementation branch), Development Flow (需求→docs→Issue→dev→测试→Review→main), docs Branch (single source of truth), M2 Parent Issue #4 (shared parent → dev acceptance entry), M2 Codex Issue #5 (implementation & acceptance evidence), M2 Trae Issue #6 (closed not planned) (+5 more)

### Community 16 - "Application Architecture Principles"
Cohesion: 0.17
Nodes (13): 应用用例拥有授权事务幂等与审计, FastAPI API, 健康就绪与功能降级边界, NiceGUI Web, Python 3.14 Monorepo, Repository 不自行提交事务, NiceGUI 同源 BFF, 共享契约包纯契约边界 (+5 more)

### Community 17 - "Branch State Snapshot"
Cohesion: 0.23
Nodes (12): 2026-08-02 main docs dev 分支状态快照, M4 docs c9401c5a189fcc10ee2e15903a186c06b94cea30 dev 8695b04161ea96bddc31c3bfeab2e0957ef68562 complete, M5 docs 7d9af6c dev ae74c83 Quality 30202886134 complete, M6 T087-T126 main beb8784cd5dd5cb2f1ddd39a46f7d0bff0ab3098 complete, M7 T127-T141 main 70ba267fab3a3a0e5c43dc25cb510b4acdd6b244 complete, M8 ready 且 T142-T169 未开始, M9 生产部署复审 pending, 固定新 docs SHA 后从 T142 开始 (+4 more)

### Community 18 - "System Design Decisions"
Cohesion: 0.18
Nodes (12): Cloud 单园 独立服务与受限公网确认决策, 角色 通行密钥 备用登录及最后管理员恢复边界, Web API Worker contracts Alembic 与园所隔离边界, WebAuthn 优先及密码 TOTP 备用认证模型, Child Manager 幼儿园教育管理系统, PostgreSQL UTC 备份与 API 权限要求, 需求到 main 固定交付流程, 独立 NiceGUI Web FastAPI API Dramatiq Worker 拓扑 (+4 more)

### Community 19 - "Delivery Phases & Gates"
Cohesion: 0.18
Nodes (11): Phase 1 Design and Contracts, Graphify 代码增量更新, Pre-M1 至 M8 里程碑门禁, 固定 SHA 的质量与验收证据, Phase 0 Research, Spec Kit 一致性审查, 按用户故事组织的任务生成策略, 测试优先的用户故事纵向切片 (+3 more)

### Community 20 - "Core Data Models"
Cohesion: 0.20
Nodes (10): chinesecalendar (本地工作日库), cryptography (AES-GCM/Argon2id), age_groups 年龄段, ai_model_profile_capabilities 模型能力, ai_model_profiles AI 模型档案, audit_events 审计事件, kindergartens 园所根表, semesters 学期 (+2 more)

### Community 21 - "Lesson Plan Data Models"
Cohesion: 0.22
Nodes (10): python-docx (Word 导出), class_areas 班级区域(室内/户外), class_teachers 班级教师关联, classes 班级, daily_activity_plan_authors 教案作者, daily_activity_plan_exports Word 导出记录, daily_activity_plan_snapshots 不可变快照, daily_activity_plans 一日活动计划 (+2 more)

### Community 22 - "Lesson Planning Features"
Cohesion: 0.24
Nodes (10): AI Batch 子任务派生状态, 班级室内与户外区域, 一日活动计划, 四栏一键 AI 批次, 集体活动原始教案导入与生成, 首期必要设置, 受限且可清理的 DOCX 导入, 教师与班级多对多关系 (+2 more)

### Community 23 - "AI Prompt Pipeline"
Cohesion: 0.28
Nodes (9): AI 生成与提示词规则 (graphify 源节点), Pydantic 2, Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界, ai_generation_results AI 生成结果预览, background_jobs PostgreSQL 权威异步任务, prompt_test_runs 提示词异步测试, prompt_versions 提示词版本(草稿/不可变发布), 异步 AI 生成管线 (graphify 源节点) (+1 more)

### Community 24 - "Runtime Architecture"
Cohesion: 0.31
Nodes (9): OpenAI-Compatible Model Service, FastAPI API (apps/api), Export Storage Seam, Holiday Adapter, Key Source Seam, PostgreSQL, Redis, NiceGUI Web / BFF (apps/web) (+1 more)

### Community 25 - "API Contracts & Auth"
Cohesion: 0.25
Nodes (9): 分页 错误 幂等 expected_version 权限与降级 API 合同, 审计覆盖与秘密正文绝对路径零暴露, 同源 BFF Cookie CSRF 来源头与 Set-Cookie 合同, Alembic 与 init-admin 首位管理员初始化, 409 identity.last_admin_recovery_requires_cli 双人恢复, 密码 TOTP 备用登录与新设备通行密钥验收, 数据库与全局配置 503 功能依赖 degraded 语义, API Worker Web 三个独立进程 (+1 more)

### Community 26 - "Production Deployment Review"
Cohesion: 0.25
Nodes (8): M9 网络 密钥 备份恢复与生产冒烟出口门禁, M9 生产安全与部署实现复审 pending, ADR-0009 延后生产实现至 M8 complete, Phase 1 Quickstart 首期实现与验收合同, worktree 端口 数据库与运行目录隔离档位, 仓库外 0600 配置与回环 Secure false 限制, 生产拓扑 PDF 照片 OCR 对象存储与审批反目标, Python 3.14 uv PostgreSQL Redis WebAuthn 浏览器前提

### Community 27 - "Implementation Task Plan"
Cohesion: 0.25
Nodes (8): Phase 1 Setup T001–T008 (graphify 源节点), PostgreSQL (业务与任务权威状态), Python 3.14+, Query 2026-07-13: graphify update 与剩余任务, Redis (消息投递/短期协调), 实施顺序 M1–M8 (graphify 源节点), 实现分支授权边界 (graphify 源节点), 首期一日活动计划实现任务清单 (graphify 源节点)

### Community 28 - "Engineering Roadmap & Rules"
Cohesion: 0.29
Nodes (7): 阶段完成证据合同, 固定 docs SHA 纵向 Issue 与三分支规则, 旧仓库 225fe139d5541539f2be4d0d41ef00061989533d 经验边界, Child Manager 产品与工程路线图 v1.4, uv sync Ruff Pyright Pytest 标准质量门禁, pending ready in_progress blocked complete 状态语义, 架构 契约 迁移 Repository API Worker Word Web 与标准五命令

### Community 29 - "Database Migrations"
Cohesion: 0.52
Nodes (7): Migration 0006 lesson_plans, Migration 0007 ai_prompts_jobs, Migration 0008 ai_generation_results, Migration 0009 group_activity_sources, Migration 0010 word_exports, Query 2026-07-26: T046–T061 与 T062–T086 固定实施顺序, 001 数据模型 data-model.md

### Community 30 - "Background Job Processing"
Cohesion: 0.29
Nodes (7): 唯一 Pending AI 结果占位, 反思任务单事务受理, 脱敏审计事件, PostgreSQL 权威后台任务, 显式一日活动反思生成, 资源感知幂等作用域, pending_dispatch 投递恢复机制

### Community 31 - "AI Prompt Governance"
Cohesion: 0.33
Nodes (7): 提示词测试配置修订冻结, AI 模型档案, 外部 AI 数据最小化, 提示词草稿发布历史与回滚, 白名单纯替换提示词语法, 提示词测试冻结上下文与配置修订, 七个稳定 AI 任务

### Community 32 - "Architecture Exploration"
Cohesion: 0.60
Nodes (6): 共同实施路线, 当前仓库与分支状态, Web、API 与 Worker 服务边界, 目标服务架构, 查询记录 2026-07-11 02:19：接下来需要生成什么文件, 查询记录 2026-07-11 02:42：系统架构文档要素

### Community 33 - "Project Context & Handoff"
Cohesion: 0.33
Nodes (6): AGENTS CONTEXT README ROADMAP 固定阅读顺序, 旧 kindergartenManager 仅作经验参考, 项目当前状态与 Agent 交接入口, 园所 学期 用户班级 区域 模型与提示词必要设置, 设置到教案 AI 归档历史 Word 的目标流程, CONTEXT 可复现状态更新规则

### Community 34 - "Milestone Roadmap Status"
Cohesion: 0.33
Nodes (6): M1 工程骨架 complete, M2 docs bb025b2 dev fb4f076 Quality 30006114394 complete, M3 docs bd98a1a dev f5f0084 complete, M3A docs 2f7894c dev 6a9e269 Quality 30161645948 complete, M1 M2 M3 M3A M5 M4 M6 M7 M8 M9 实施路线, 标准五命令及数据库 API Worker Word 专项验证

### Community 35 - "M7 M8 Acceptance Gates"
Cohesion: 0.53
Nodes (6): M7 T127-T141 固定 Word 导出与历史 complete, M7 docs 47eae46c6efec2e7596063bea2fc3352c2ece189 dev ba9251d2ee74c8959ea53e888cd5a030571fdc69 main 70ba267fab3a3a0e5c43dc25cb510b4acdd6b244 Quality 30697998054 30698318868, M8 PRD 自动化 迁移 浏览器 隐私与报告出口门禁, M8 T142-T169 首期功能验收 ready, M7 complete M8 ready T142-T169 未开始, M8 命令 环境 浏览器 结果 证据 风险完整报告

### Community 36 - "Lesson Plan PRD"
Cohesion: 0.33
Nodes (6): 首期一日活动计划实现计划, 首期一日活动计划完整闭环规格, 固定模板 Word 导出, GitHub Issue #12, 一日活动计划 PRD, 固定 Word 教案模板

### Community 38 - "Word Export Jobs"
Cohesion: 0.50
Nodes (5): Dramatiq Worker, PostgreSQL 权威业务状态, Redis 投递与短期协调, Word 导出单事务冻结受理, 不可变导出历史与独立副本

### Community 39 - "Authentication Flows"
Cohesion: 0.40
Nodes (5): 同源 BFF 可信来源边界, 密码与 TOTP 双因素备用登录, 密码与 TOTP 备用登录独立规格, 安全初始化与带外核验, WebAuthn 通行密钥认证

### Community 40 - "Task List Constraints"
Cohesion: 0.50
Nodes (4): 任务清单不授权文档修改、分支切换、提交、cherry-pick、推送或 PR, 首期一日活动计划完整闭环任务清单, 范围：Roadmap M1–M8；M9 生产部署复审排除, 2026-07-21 工作流重置：后续仅在 dev 实现且 Issue 固定引用 docs SHA

### Community 41 - "TDD Delivery Strategy"
Cohesion: 0.50
Nodes (4): 有效 RED→最小实现→快速测试→故事 checkpoint 的增量交付策略, 固定 RED→GREEN 配对范围 T009–T157, RED 仅可在配对实现最终路径创建无业务规则、无副作用的最小 import skeleton, 有效 RED：collect-only 退出 0 且 errors=0，业务断言 failed>0 且 errors=0

### Community 42 - "US4 AI Batch Implementation"
Cohesion: 0.50
Nodes (4): US4 commits：dev@4a9974eaa80ae1e9b0e6a15035512bbb32b6b2d1、dev@a75e05576f8dfae98b199ea3411f29bc7f76466a、dev@9798aa0、dev@386cccb、dev@c83a4f0、dev@9b6809e、dev@d6754cb、dev@9932aa928132152cabedb2e273980f60cdd51f6c, T087–T097：AI batch、预览、Worker、反思、轮询和 Web RED，已完成, T098–T109：AI 结果、生成、执行、采用、反思、路由、Web 和审计实现，已完成, T110：US4 验收，dev@9932aa928132152cabedb2e273980f60cdd51f6c，126 passed，完整 610 passed、1 warning

### Community 43 - "US5 DOCX Import Implementation"
Cohesion: 0.50
Nodes (4): T111：确定性安全/恶意 DOCX/ZIP 测试工厂，已完成, T112–T117：DOCX 安全、来源、拆分、新增环节、采用和 Web RED，已完成, T118–T125：来源、OOXML、两阶段 AI、采用、API 和 Web 实现，已完成, T126：US5 独立验收，已完成

### Community 44 - "Foundational Setup Tasks"
Cohesion: 0.67
Nodes (3): T009–T012：依赖、公共契约、健康与事务/Alembic RED，已完成, T013–T019：公共契约、配置、数据库、替身及三运行入口实现，已完成, T020：Foundational 专项、五条质量命令与 Graphify 门禁，已完成

### Community 45 - "WebAuthn Identity Implementation"
Cohesion: 0.67
Nodes (3): T021–T025：WebAuthn、身份迁移、API 契约和浏览器流程 RED，已完成, T026–T034：身份模型、ceremony、限流、状态机、CLI、API 与 Web 实现，已完成, T035：M2 独立验收，已完成

### Community 46 - "Settings Implementation"
Cohesion: 0.67
Nodes (3): T036–T039：Settings 契约、规则、权限和 Web RED，已完成, T040–T044：园所、学期、班级、教师、年龄段和区域实现，已完成, T045：M3 独立验收，已完成

### Community 47 - "Manual Lesson Plan Implementation"
Cohesion: 0.67
Nodes (3): T046–T051：手工教案 Schema、持久化、API、日历和 Web RED，已完成, T052–T060：手工教案契约、模型、日历、Repository、服务、API 与 Web 实现，已完成, T061：关闭 AI、Worker 和在线工作日后的 US2 独立验收，已完成

### Community 48 - "AI Model & Prompt Implementation"
Cohesion: 0.67
Nodes (3): T062–T072：模型、密钥、SSRF、提示词、任务和 Web RED，已完成, T073–T085：AI 模型、提示词、加密、任务、Worker、API 与 Web 实现，已完成, T086：US3 独立验收，已完成

## Ambiguous Edges - Review These
- `Repository Workflow Reset 2026-07-21` → `Combined Audit Conclusion (Q1–Q26)`  [AMBIGUOUS]
  docs/faq/combined-audit.md · relation: conceptually_related_to
- `M2 Milestone` → `M1 Milestone`  [AMBIGUOUS]
  docs/faq/combined-audit.md · relation: conceptually_related_to
- `Q23 Production Deployment Deferral` → `ADR-0009 Defer Production Deployment Until Feature Complete`  [AMBIGUOUS]
  docs/faq/combined-audit.md · relation: conceptually_related_to
- `codex 实现分支（待授权创建）` → `提交 e9a0e77（HEAD = origin/main 共同基线）`  [AMBIGUOUS]
  docs/审查报告/20260714审查报告.md · relation: references
- `trae 实现分支（待授权创建）` → `提交 e9a0e77（HEAD = origin/main 共同基线）`  [AMBIGUOUS]
  docs/审查报告/20260714审查报告.md · relation: references
- `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` → `ai_generation_results AI 生成结果预览`  [AMBIGUOUS]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md · relation: conceptually_related_to
- `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` → `background_jobs PostgreSQL 权威异步任务`  [AMBIGUOUS]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md · relation: conceptually_related_to

## Knowledge Gaps
- **237 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+232 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **77 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `Web、API 与 Worker 服务边界` (2× useful, score=1.416647594) _(code changed — re-verify)_
- `班级与教师配置` (2× useful, score=1.39887405)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Repository Workflow Reset 2026-07-21` and `Combined Audit Conclusion (Q1–Q26)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `M2 Milestone` and `M1 Milestone`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Q23 Production Deployment Deferral` and `ADR-0009 Defer Production Deployment Until Feature Complete`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `codex 实现分支（待授权创建）` and `提交 e9a0e77（HEAD = origin/main 共同基线）`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `trae 实现分支（待授权创建）` and `提交 e9a0e77（HEAD = origin/main 共同基线）`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` and `ai_generation_results AI 生成结果预览`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` and `background_jobs PostgreSQL 权威异步任务`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._