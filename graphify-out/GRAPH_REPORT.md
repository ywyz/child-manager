# Graph Report - .  (2026-08-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 757 nodes · 1063 edges · 102 communities (55 shown, 47 thin omitted)
- Extraction: 86% EXTRACTED · 13% INFERRED · 1% AMBIGUOUS · INFERRED: 139 edges (avg confidence: 0.81)
- Token cost: 5,851 input · 5,121 output

## Graph Freshness
- Built from commit: `fff6e090`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- System Architecture & Design
- Pre-Coding Review Planning
- Core Database Entities
- Repository Branches & Issues
- Project Charter & Scope
- Acceptance Contracts & Security
- Security & Tech Stack
- Identity & Backup Auth
- Lesson Plan ADRs
- Spec Kit Skills
- Milestone Status Tracking
- Tech Stack Research
- Shell Utility Functions
- Data Model Tables
- Desktop Reset Governance
- Authentication Tables
- Repository Workflow Reset
- Legacy Migration CDRs
- Phases & Quality Gates
- Project Phases
- Dependencies & Core Tables
- Word Export & Lesson Tables
- Lesson Planning Features
- AI Generation Pipeline
- AI Workbench UI
- Group Activity Editor
- Morning Activity Editor
- Platform Services Integration
- Schema Migrations & Specs
- Implementation Roadmap
- AI Task Processing
- Application Architecture
- Prompt Management
- Word Export Service
- Daily Activity Plan PRD
- Desktop Activity Editor
- Feature Creation Script
- Background Job Worker
- Authentication & BFF
- Access Control & Transactions
- Batch Word Export
- Offline Verification Criteria
- Task List Scope
- Test-Driven Delivery
- US4 AI Batch Delivery
- US5 DOCX Import
- Backup & Restore
- Contribution Guidelines
- AI & Encrypted Backup
- Milestone Reports
- Foundational Implementation
- Identity Implementation
- Settings Implementation
- Manual Lesson Plan
- AI Feature Implementation
- AI Capability Sequencing
- ADR Decisions Query
- Desktop Local Stack
- Weekly Plan Workbench
- Prerequisites Check Script
- Plan Setup Script
- Tasks Setup Script
- Data Isolation & Auth
- Graphify Fallback
- Branch State Boundaries
- Deploy Deferral ADR
- ADR Conventions
- Data Model Doc
- Database Schema Doc
- Credential Storage
- Desktop SQLite Authority
- Dependency Direction
- Navigation Rules
- Desktop Accessibility
- Backend Package
- Contracts Package
- System Architecture Doc
- Integrations Module
- Local Dev Environments
- Workflow Reset Notes
- Lesson Management PRD
- Milestone Evidence
- Issue Templates
- Constitution Template
- OpenAPI Contract
- Contracts README
- Spec OpenAPI
- Page IA Research
- Spec Quality Checklist
- Modeling Principles
- Status Transitions
- Storage Conventions
- Spec Task Baseline
- Single Agent Runtime
- Slice 2B Permissions
- Post-Slice-3 Write Contract
- Bootstrap Startup Order
- Desktop Service Boundary
- CDR Non-blocking Status
- Desktop Stack Research
- Daily Activity Plan Guide
- Teacher Plan Word Template

## God Nodes (most connected - your core abstractions)
1. `Combined Audit Conclusion (Q1–Q26)` - 41 edges
2. `001 研究 research.md` - 35 edges
3. `Security Threat Model` - 29 edges
4. `2026-07-14 编码前审查报告（Codex + Trae 收敛版）` - 25 edges
5. `20260713 Pre-Coding Review Report (Codex + Trae)` - 21 edges
6. `System Architecture` - 20 edges
7. `教案管理 PRD v1.3` - 19 edges
8. `2026-07-14 编码前审查解决方案` - 17 edges
9. `Users` - 16 edges
10. `Data Model Specification` - 16 edges

## Surprising Connections (you probably didn't know these)
- `教案管理 PRD v1.3` --conceptually_related_to--> `一日活动计划`  [INFERRED]
  docs/PRD/lesson-management.md → graphify-out/memory/query_20260711_020708_请根据现有文档_和旧仓库的文件思考如何撰写_docs_prd_lesson_management_m.md
- `System Architecture` --conceptually_related_to--> `目标服务架构`  [INFERRED]
  docs/design/system-architecture.md → graphify-out/memory/query_20260711_021923_接下来需要生成什么文件呢.md
- `单实现开发协议 (当前)` --references--> `API v1 OpenAPI Specification 2.1.0`  [INFERRED]
  docs/development/single-implementation-development.md → specs/001-daily-activity-plan/contracts/openapi.yaml
- `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` --conceptually_related_to--> `ai_generation_results AI 生成结果预览`  [AMBIGUOUS]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md → specs/001-daily-activity-plan/data-model.md
- `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` --conceptually_related_to--> `background_jobs PostgreSQL 权威异步任务`  [AMBIGUOUS]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md → specs/001-daily-activity-plan/data-model.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Database Schema Entities** — specs_003-desktop-local-first_data_model_app_profile, specs_003-desktop-local-first_data_model_kindergarten_settings, specs_003-desktop-local-first_data_model_class_groups, specs_003-desktop-local-first_data_model_class_areas, specs_003-desktop-local-first_data_model_semesters, specs_003-desktop-local-first_data_model_lesson_plans, specs_003-desktop-local-first_data_model_lesson_plan_versions, specs_003-desktop-local-first_data_model_calendar_overrides, specs_003-desktop-local-first_data_model_ai_configuration, specs_003-desktop-local-first_data_model_prompt_overrides, specs_003-desktop-local-first_data_model_ai_previews, specs_003-desktop-local-first_data_model_agent_action_audits, specs_003-desktop-local-first_data_model_backup_records [EXTRACTED 1.00]
- **Implementation Phases Sequence** — specs_003_desktop_local_first_tasks_phase_1_setup, specs_003_desktop_local_first_tasks_phase_2_foundational, specs_003_desktop_local_first_tasks_phase_3_slice_1_mvp, specs_003_desktop_local_first_tasks_phase_4_slice_2a_ai, specs_003_desktop_local_first_tasks_phase_5_slice_2b_agent_foundation, specs_003_desktop_local_first_tasks_phase_6_slice_3_backup, specs_003_desktop_local_first_tasks_phase_7_agent_write, specs_003_desktop_local_first_tasks_phase_8_slice_4_batch_word, specs_003_desktop_local_first_tasks_phase_9_us1_completion, specs_003_desktop_local_first_tasks_phase_10_us4_desktop_experience, specs_003_desktop_local_first_tasks_phase_11_polish [INFERRED 0.75]
- **SC-001、Slice 1 与 T034 的无计时 Windows 二元验收** — specs_003_desktop_local_first_spec_sc_001, specs_003_desktop_local_first_spec_windows_binary_evidence, specs_003_desktop_local_first_checklists_requirements_validation_6 [INFERRED 0.85]
- **未授权 CDR-01–CDR-08 候选提案，不阻塞现行门禁** — specs_003_desktop_local_first_proposals_desktop_cloud_retirement, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_nonblocking, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_cdr_01, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_cdr_02, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_cdr_03, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_cdr_04, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_cdr_05, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_cdr_06, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_cdr_07, specs_003_desktop_local_first_proposals_desktop_cloud_retirement_cdr_08 [EXTRACTED 1.00]
- **六大核心原则构成宪章治理框架** — specify_memory_constitution_principle_fact_sources, specify_memory_constitution_principle_local_first, specify_memory_constitution_principle_single_teacher, specify_memory_constitution_principle_local_authority, specify_memory_constitution_principle_teacher_control, specify_memory_constitution_principle_verification [EXTRACTED 1.00]
- **桌面技术基线 (Python 3.14 / PySide6 / SQLite / SQLAlchemy / Alembic / uv / Ruff / Pyright / Pytest / chinesecalendar)** — tech_python, tech_pyside6, tech_qt_widgets, tech_sqlite, tech_sqlalchemy, tech_alembic, tech_uv, tech_ruff, tech_pyright, tech_pytest, tech_chinesecalendar [EXTRACTED 1.00]
- **首期交付范围 (一日活动计划、数据与备份、必要设置)** — specify_memory_constitution_daily_activity_plan, specify_memory_constitution_data_backup, specify_memory_constitution_settings [EXTRACTED 1.00]
- **首期一日活动计划完整闭环** — specs_001_daily_activity_plan_spec_secure_initialization, specs_001_daily_activity_plan_spec_necessary_settings, specs_001_daily_activity_plan_spec_manual_lesson_plan_loop, specs_001_daily_activity_plan_spec_prompt_lifecycle, specs_001_daily_activity_plan_spec_four_column_ai_batch, specs_001_daily_activity_plan_spec_group_activity_import, specs_001_daily_activity_plan_spec_fixed_word_export, specs_001_daily_activity_plan_spec_audit_events [EXTRACTED 1.00]
- **Web API Worker 三个独立运行单元** — specs_001_daily_activity_plan_plan_nicegui_web, specs_001_daily_activity_plan_plan_fastapi_api, specs_001_daily_activity_plan_plan_dramatiq_worker [EXTRACTED 1.00]
- **事务化冻结受理模式** — specs_001_daily_activity_plan_plan_postgresql_authoritative_state, specs_001_daily_activity_plan_plan_transactional_reflection_intake, specs_001_daily_activity_plan_plan_transactional_export_intake, specs_001_daily_activity_plan_plan_prompt_test_revision_freeze, specs_001_daily_activity_plan_plan_ai_result_placeholder [INFERRED 0.85]
- **已完成交付范围 T001–T141** — specs_001_daily_activity_plan_tasks_phase_setup, specs_001_daily_activity_plan_tasks_phase_foundational, specs_001_daily_activity_plan_tasks_m2, specs_001_daily_activity_plan_tasks_m3, specs_001_daily_activity_plan_tasks_us2, specs_001_daily_activity_plan_tasks_us3, specs_001_daily_activity_plan_tasks_us4, specs_001_daily_activity_plan_tasks_us5, specs_001_daily_activity_plan_tasks_us6, specs_001_daily_activity_plan_tasks_t001_t008, specs_001_daily_activity_plan_tasks_t009_t012, specs_001_daily_activity_plan_tasks_t013_t019, specs_001_daily_activity_plan_tasks_t020, specs_001_daily_activity_plan_tasks_t021_t025, specs_001_daily_activity_plan_tasks_t026_t034, specs_001_daily_activity_plan_tasks_t035, specs_001_daily_activity_plan_tasks_t036_t039, specs_001_daily_activity_plan_tasks_t040_t044, specs_001_daily_activity_plan_tasks_t045, specs_001_daily_activity_plan_tasks_t046_t051, specs_001_daily_activity_plan_tasks_t052_t060, specs_001_daily_activity_plan_tasks_t061, specs_001_daily_activity_plan_tasks_t062_t072, specs_001_daily_activity_plan_tasks_t073_t085, specs_001_daily_activity_plan_tasks_t086, specs_001_daily_activity_plan_tasks_t087_t097, specs_001_daily_activity_plan_tasks_t098_t109, specs_001_daily_activity_plan_tasks_t110, specs_001_daily_activity_plan_tasks_t111, specs_001_daily_activity_plan_tasks_t112_t117, specs_001_daily_activity_plan_tasks_t118_t125, specs_001_daily_activity_plan_tasks_t126, specs_001_daily_activity_plan_tasks_t127_t132, specs_001_daily_activity_plan_tasks_t133_t140, specs_001_daily_activity_plan_tasks_t141 [EXTRACTED 1.00]
- **M8 ready 与未开始任务 T142–T169** — specs_001_daily_activity_plan_tasks_us7, specs_001_daily_activity_plan_tasks_polish, specs_001_daily_activity_plan_tasks_t142_t149, specs_001_daily_activity_plan_tasks_t150_t157, specs_001_daily_activity_plan_tasks_t158, specs_001_daily_activity_plan_tasks_t159_t162, specs_001_daily_activity_plan_tasks_t163_t166, specs_001_daily_activity_plan_tasks_t167_t169 [EXTRACTED 1.00]
- **固定阶段依赖链** — specs_001_daily_activity_plan_tasks_phase_setup, specs_001_daily_activity_plan_tasks_phase_foundational, specs_001_daily_activity_plan_tasks_m2, specs_001_daily_activity_plan_tasks_m3, specs_001_daily_activity_plan_tasks_m3a, specs_001_daily_activity_plan_tasks_us2, specs_001_daily_activity_plan_tasks_us3, specs_001_daily_activity_plan_tasks_us4, specs_001_daily_activity_plan_tasks_us5, specs_001_daily_activity_plan_tasks_us6, specs_001_daily_activity_plan_tasks_us7, specs_001_daily_activity_plan_tasks_polish [EXTRACTED 1.00]
- **M8 端到端功能验收证据集合** — specs_001_daily_activity_plan_quickstart_settings_acceptance, specs_001_daily_activity_plan_quickstart_manual_plan_acceptance, specs_001_daily_activity_plan_quickstart_ai_job_acceptance, specs_001_daily_activity_plan_quickstart_reflection_acceptance, specs_001_daily_activity_plan_quickstart_docx_security, specs_001_daily_activity_plan_quickstart_word_export_acceptance, specs_001_daily_activity_plan_quickstart_workday_degradation, specs_001_daily_activity_plan_quickstart_audit_privacy, specs_001_daily_activity_plan_quickstart_api_contract, specs_001_daily_activity_plan_quickstart_m8_report [EXTRACTED 1.00]
- **Spec Kit 全生命周期流程 (specify→plan→tasks→implement)** — specify_workflows_speckit_workflow_specify_step, specify_workflows_speckit_workflow_review_spec_gate, specify_workflows_speckit_workflow_plan_step, specify_workflows_speckit_workflow_review_plan_gate, specify_workflows_speckit_workflow_tasks_step, specify_workflows_speckit_workflow_implement_step [EXTRACTED 1.00]
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

## Communities (102 total, 47 thin omitted)

### Community 0 - "System Architecture & Design"
Cohesion: 0.07
Nodes (59): chinesecalendar Library, CSRF & Origin Verification, Daily Reflection, Degraded Operations & Failure Matrix, ADR-0001 Cloud Only, ADR-0002 独立 Web/API/Worker 模块化单体, Data Model Design, Database Schema Design (+51 more)

### Community 1 - "Pre-Coding Review Planning"
Cohesion: 0.09
Nodes (46): codex 实现分支（待授权创建）, main 分支（docs-only 基线）, trae 实现分支（待授权创建）, AI 生成与提示词规则, 班级与教师配置, 一日活动计划, 日期选择与校验, 共同实施路线 (+38 more)

### Community 2 - "Core Database Entities"
Cohesion: 0.08
Nodes (39): Account Invitations, Account Recovery Requests, Age Groups, AI Generation Results, AI Model Profile Capabilities, AI Model Profiles, Audit Events, Background Jobs (+31 more)

### Community 3 - "Repository Branches & Issues"
Cohesion: 0.11
Nodes (35): codex 分支 (历史双实现线), dev 分支 (唯一实现与集成), docs 分支 (文档与契约), main 分支 (稳定发布基线), trae 分支 (历史双实现线), Codex Agent, Dev 本地档位 (端口/Compose/数据库隔离), graphify 知识图谱工具与 graphify-out 输出 (+27 more)

### Community 4 - "Project Charter & Scope"
Cohesion: 0.08
Nodes (35): 幼儿园管理助手项目宪章 (Constitution v4.1.0), ADR (架构决策记录), 可选 AI (OpenAI 兼容边界), 幼儿档案 (Child Profiles, 首期禁止), 操作系统凭据存储, 一日活动计划 (Daily Activity Plan), 数据与备份 (Data & Backup), GitHub Issue (执行范围与验收证据) (+27 more)

### Community 5 - "Acceptance Contracts & Security"
Cohesion: 0.06
Nodes (32): Phase 1 Quickstart 首期实现与验收合同, 四栏目任务 pending_dispatch 重试预览与采用验收, 分页 错误 幂等 expected_version 权限与降级 API 合同, 审计覆盖与秘密正文绝对路径零暴露, 同源 BFF Cookie CSRF 来源头与 Set-Cookie 合同, Alembic 与 init-admin 首位管理员初始化, 10 MiB 50 MiB 1000 条目 200000 字符 DOCX 安全边界, 409 identity.last_admin_recovery_requires_cli 双人恢复 (+24 more)

### Community 6 - "Security & Tech Stack"
Cohesion: 0.12
Nodes (29): ADR-0010 Restricted Public Entry & Passkey Auth, ADR-0011 Password+TOTP Backup Login, ADR-0009 Defer Production Deployment Until Feature Complete, Technology Stack (Python 3.14, NiceGUI, FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic), Security Threat Model, AES-256-GCM Secret Encryption, Argon2id Password Hashing, External AI Service (+21 more)

### Community 7 - "Identity & Backup Auth"
Cohesion: 0.16
Nodes (24): ADR-0010 Identity Rewrite, ADR-0011 Password+TOTP Backup, audit_events Table, authentication_method Enum, backup_auth_credentials Table, backup_auth_enrollments Table, backup_auth_status Enum, M3A: Password+TOTP Backup Login (+16 more)

### Community 8 - "Lesson Plan ADRs"
Cohesion: 0.13
Nodes (24): background_job 权威任务状态机, ADR-0003 PostgreSQL 权威任务状态 + Dramatiq/Redis, ADR-0004 同源 Cookie 认证, 提示词草稿/发布/回滚生命周期, ADR-0005 AI 供应商中立与提示词系统, ADR-0006 固定 Word 模板导出边界, ADR-0007 Caddy/Compose/Secrets（已被取代）, ADR-0008 日期与外部服务本地优先/软降级 (+16 more)

### Community 9 - "Spec Kit Skills"
Cohesion: 0.19
Nodes (21): speckit-analyze Skill, speckit-checklist Skill, speckit-clarify Skill, speckit-constitution Skill, speckit-converge Skill, speckit-implement Skill, speckit-plan Skill, speckit-specify Skill (+13 more)

### Community 10 - "Milestone Status Tracking"
Cohesion: 0.14
Nodes (21): M0 共同基线 c1b363331c5b8d611aa4c8b0e2fb775f5e64ccc7, M6 Review main@b7676c27d07adc5eca1f0c397217780367481e9c→dev@d654b704d1bd0653f7d0209ac58665090a934311 PASS；main@beb8784cd5dd5cb2f1ddd39a46f7d0bff0ab3098；run 30631050997 attempt 2, Issue #12 completed；docs@47eae46c6efec2e7596063bea2fc3352c2ece189；dev@ba9251d2ee74c8959ea53e888cd5a030571fdc69 run 30697998054；main@70ba267fab3a3a0e5c43dc25cb510b4acdd6b244 run 30698318868；729 passed, Issue #10 completed；docs@c9401c5a189fcc10ee2e15903a186c06b94cea30；Review dev@8695b04161ea96bddc31c3bfeab2e0957ef68562 PASS；runs 30235090100/30235439229；main@b7676c27d07adc5eca1f0c397217780367481e9c, US5 dev@32d3c102152848f7488da036ddada461b3d8d3ab；run 30602225731；49 passed、56 passed、完整 666 passed；恶意样本残留 0, US1/M2 安全身份：T021–T035，complete, US1/M3 必要设置：T036–T045，complete, US1/M3A 密码与 TOTP 备用登录：独立 specs/002 T001–T034 (+13 more)

### Community 11 - "Tech Stack Research"
Cohesion: 0.20
Nodes (18): Dramatiq 2 + Redis, FastAPI, HTTPX (外部 HTTP 客户端), NiceGUI 3.x, 旧仓库 adapt_client.py (新增环节参考), 旧仓库 generate_client.py (提示词措辞参考), 旧仓库 lesson_plan_client.py (拆分参考), Psycopg 3 (+10 more)

### Community 12 - "Shell Utility Functions"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 13 - "Data Model Tables"
Cohesion: 0.18
Nodes (17): Data Model Specification, Agent Action Audits Table, AI Configuration Table, AI Previews Table, App Profile Table, Backup Records Table, Calendar Overrides Table, Class Areas Table (+9 more)

### Community 14 - "Desktop Reset Governance"
Cohesion: 0.17
Nodes (15): main、docs、dev 分支职责, 桌面重置与设计阶段边界, 固定 docs SHA 的 Issue 驱动实现门禁, 当前桌面方向与事实来源, docs 发布到 Slice 1 RED 的下一步, 本地优先桌面产品方向重置, 设计确认到新 Issue 的迁移门禁, 有界 Context 与无长期业务记忆 (+7 more)

### Community 15 - "Authentication Tables"
Cohesion: 0.15
Nodes (15): PyJWT (HS256 Access Token), account_invitations 账号邀请, account_recovery_requests 恢复请求, backup_auth_credentials 密码+TOTP 备用材料, backup_auth_enrollments 备用绑定流程, bootstrap_initializations 首位管理员初始化, identity_verification_approvals 身份核验批准, recovery_codes 离线恢复码 (+7 more)

### Community 16 - "Repository Workflow Reset"
Cohesion: 0.27
Nodes (13): Repository Workflow Reset 2026-07-21, Codex Agent, dev Branch (Codex implementation branch), Development Flow (需求→docs→Issue→dev→测试→Review→main), docs Branch (single source of truth), M2 Parent Issue #4 (shared parent → dev acceptance entry), M2 Codex Issue #5 (implementation & acceptance evidence), M2 Trae Issue #6 (closed not planned) (+5 more)

### Community 17 - "Legacy Migration CDRs"
Cohesion: 0.17
Nodes (12): 历史图谱曾将 T042 标为 Windows Manual Acceptance（已纠正）, query memory：编号校正历史记录（非现行规范）, 验证迭代 7：T001–T124 稳定、T034 Windows、T035–T040 Slice 2A clean RED, 桌面默认门禁与旧 Cloud 退役候选工作包, CDR-01 迁移仍适用的教学周、四季、正文与校验行为, CDR-02 迁移供应商中立 AI 结果 Schema 与 hash 断言, CDR-03 迁移适用 Word 模板与确定性 DOCX 断言, CDR-04 补齐最小纯领域规则 (+4 more)

### Community 18 - "Phases & Quality Gates"
Cohesion: 0.18
Nodes (11): Phase 1 Design and Contracts, Graphify 代码增量更新, Pre-M1 至 M8 里程碑门禁, 固定 SHA 的质量与验收证据, Phase 0 Research, Spec Kit 一致性审查, 按用户故事组织的任务生成策略, 测试优先的用户故事纵向切片 (+3 more)

### Community 19 - "Project Phases"
Cohesion: 0.18
Nodes (11): Phase 10: US4 Desktop Experience, Phase 11: Polish & Quality Gates, Phase 1: Setup, Phase 2: Foundational, Phase 3: Slice 1 MVP, Phase 4: Slice 2A AI, Phase 5: Slice 2B Agent Foundation, Phase 6: Slice 3 Backup (+3 more)

### Community 20 - "Dependencies & Core Tables"
Cohesion: 0.20
Nodes (10): chinesecalendar (本地工作日库), cryptography (AES-GCM/Argon2id), age_groups 年龄段, ai_model_profile_capabilities 模型能力, ai_model_profiles AI 模型档案, audit_events 审计事件, kindergartens 园所根表, semesters 学期 (+2 more)

### Community 21 - "Word Export & Lesson Tables"
Cohesion: 0.22
Nodes (10): python-docx (Word 导出), class_areas 班级区域(室内/户外), class_teachers 班级教师关联, classes 班级, daily_activity_plan_authors 教案作者, daily_activity_plan_exports Word 导出记录, daily_activity_plan_snapshots 不可变快照, daily_activity_plans 一日活动计划 (+2 more)

### Community 22 - "Lesson Planning Features"
Cohesion: 0.24
Nodes (10): AI Batch 子任务派生状态, 班级室内与户外区域, 一日活动计划, 四栏一键 AI 批次, 集体活动原始教案导入与生成, 首期必要设置, 受限且可清理的 DOCX 导入, 教师与班级多对多关系 (+2 more)

### Community 23 - "AI Generation Pipeline"
Cohesion: 0.28
Nodes (9): AI 生成与提示词规则 (graphify 源节点), Pydantic 2, Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界, ai_generation_results AI 生成结果预览, background_jobs PostgreSQL 权威异步任务, prompt_test_runs 提示词异步测试, prompt_versions 提示词版本(草稿/不可变发布), 异步 AI 生成管线 (graphify 源节点) (+1 more)

### Community 24 - "AI Workbench UI"
Cohesion: 0.22
Nodes (9): AI 工作台生成当前栏目, 自动保存、版本保存与 Word 导出, AI 工作台生成当前栏目, 自动保存、版本保存与 Word 导出, 深色主题晨间活动编辑, 教案栏目状态侧栏, B Focus 浅色晨间活动编辑界面, 浅色主题晨间活动编辑 (+1 more)

### Community 25 - "Group Activity Editor"
Cohesion: 0.22
Nodes (9): AI 建议对照、重新生成与采用, 集体活动主题、准备、目标、重点、难点与过程字段, AI 建议对照、重新生成与采用, 集体活动主题、准备、目标、重点、难点与过程字段, 今日栏目六项导航, 深色主题集体活动周编辑, C 浅色集体活动周编辑界面, 今日栏目六项导航 (+1 more)

### Community 26 - "Morning Activity Editor"
Cohesion: 0.22
Nodes (9): AI 建议对照、重新生成与采用, AI 建议对照、重新生成与采用, 晨间活动固定项目、集体游戏、自主游戏、重点指导、目标与指导要点字段, 今日栏目六项导航, 深色主题晨间活动周编辑, C 浅色晨间活动周编辑界面, 晨间活动固定项目、集体游戏、自主游戏、重点指导、目标与指导要点字段, 今日栏目六项导航 (+1 more)

### Community 27 - "Platform Services Integration"
Cohesion: 0.31
Nodes (9): OpenAI-Compatible Model Service, FastAPI API (apps/api), Export Storage Seam, Holiday Adapter, Key Source Seam, PostgreSQL, Redis, NiceGUI Web / BFF (apps/web) (+1 more)

### Community 28 - "Schema Migrations & Specs"
Cohesion: 0.43
Nodes (8): Spec Kit Consistency Check (72 FR / 17 SC / T001–T165), Migration 0006 lesson_plans, Migration 0007 ai_prompts_jobs, Migration 0008 ai_generation_results, Migration 0009 group_activity_sources, Migration 0010 word_exports, Query 2026-07-26: T046–T061 与 T062–T086 固定实施顺序, 001 数据模型 data-model.md

### Community 29 - "Implementation Roadmap"
Cohesion: 0.25
Nodes (8): Phase 1 Setup T001–T008 (graphify 源节点), PostgreSQL (业务与任务权威状态), Python 3.14+, Query 2026-07-13: graphify update 与剩余任务, Redis (消息投递/短期协调), 实施顺序 M1–M8 (graphify 源节点), 实现分支授权边界 (graphify 源节点), 首期一日活动计划实现任务清单 (graphify 源节点)

### Community 30 - "AI Task Processing"
Cohesion: 0.29
Nodes (7): 唯一 Pending AI 结果占位, 反思任务单事务受理, 脱敏审计事件, PostgreSQL 权威后台任务, 显式一日活动反思生成, 资源感知幂等作用域, pending_dispatch 投递恢复机制

### Community 31 - "Application Architecture"
Cohesion: 0.17
Nodes (13): 应用用例拥有授权事务幂等与审计, FastAPI API, 健康就绪与功能降级边界, NiceGUI Web, Python 3.14 Monorepo, Repository 不自行提交事务, NiceGUI 同源 BFF, 共享契约包纯契约边界 (+5 more)

### Community 32 - "Prompt Management"
Cohesion: 0.33
Nodes (7): 提示词测试配置修订冻结, AI 模型档案, 外部 AI 数据最小化, 提示词草稿发布历史与回滚, 白名单纯替换提示词语法, 提示词测试冻结上下文与配置修订, 七个稳定 AI 任务

### Community 33 - "Word Export Service"
Cohesion: 0.29
Nodes (7): ExportService freezes snapshots and previews before background rendering; BackupService exposes daily/manual/upload/list/inspect/restore, with final cancellation checks and detailed Word/backup contracts, KMBACKUP1 scope and manifest: whitelist ZIP containing manifest.json plus payload/application.sqlite3, no attachments/PII/secrets, and no sync, incremental merge, automatic-latest choice or remote SQLite, Atomic export and acceptance: same-directory temporary file, reopen/validate/fsync/os.replace, cancellation or failure preserves old target; Microsoft Word on Windows is required evidence, Batch DOCX structure: exactly one document, full template content for each included day, explicit page breaks and style equivalence to single-day output; no ZIP-byte concatenation or secret metadata, Frozen export inputs: DailyPlanExportSnapshot and same-semester BatchExportPreview determine deterministic skip reasons and ascending included dates; background rendering never re-queries changing plans, Word template fidelity invariant: teacherplan.docx is the sole SHA-256-verified source, every export uses a copy and shared render_day/field mapping, with no hardcoded identities or source overwrite, Research decision for Word: python-docx shared template render core, frozen batch preview, one DOCX with page breaks, temporary validation and atomic publication

### Community 35 - "Daily Activity Plan PRD"
Cohesion: 0.33
Nodes (6): 首期一日活动计划实现计划, 首期一日活动计划完整闭环规格, 固定模板 Word 导出, GitHub Issue #12, 一日活动计划 PRD, 固定 Word 教案模板

### Community 36 - "Desktop Activity Editor"
Cohesion: 0.40
Nodes (5): AI 助手生成与预览采用, 自动保存、版本保存与 Word 导出, 班级、日期与教学周选择, 一日活动计划编辑, A Classic 一日活动计划桌面界面

### Community 38 - "Background Job Worker"
Cohesion: 0.50
Nodes (5): Dramatiq Worker, PostgreSQL 权威业务状态, Redis 投递与短期协调, Word 导出单事务冻结受理, 不可变导出历史与独立副本

### Community 39 - "Authentication & BFF"
Cohesion: 0.40
Nodes (5): 同源 BFF 可信来源边界, 密码与 TOTP 双因素备用登录, 密码与 TOTP 备用登录独立规格, 安全初始化与带外核验, WebAuthn 通行密钥认证

### Community 40 - "Access Control & Transactions"
Cohesion: 0.50
Nodes (4): READ、DRAFT、确认 WRITE 权限门禁, Tool-only 业务访问, Application Layer Agent 与 Tool 边界, 冻结 DTO、短事务与失败回滚

### Community 41 - "Batch Word Export"
Cohesion: 0.50
Nodes (4): 按日期范围批量导出, C 批量导出日期范围对话框, 合并导出 Word 并可取消, 跳过日期原因汇总

### Community 42 - "Offline Verification Criteria"
Cohesion: 0.67
Nodes (4): query memory：去计时历史记录（非现行规范）, 验证迭代 6：移除耗时与起止时间，保留二元证据, SC-001 首次启动到第一份教案成功标准（无计时）, 断网 Windows 首次启动、基础设置、第一份教案、重启与 Word 打开的二元证据

### Community 43 - "Task List Scope"
Cohesion: 0.50
Nodes (4): 任务清单不授权文档修改、分支切换、提交、cherry-pick、推送或 PR, 首期一日活动计划完整闭环任务清单, 范围：Roadmap M1–M8；M9 生产部署复审排除, 2026-07-21 工作流重置：后续仅在 dev 实现且 Issue 固定引用 docs SHA

### Community 44 - "Test-Driven Delivery"
Cohesion: 0.50
Nodes (4): 有效 RED→最小实现→快速测试→故事 checkpoint 的增量交付策略, 固定 RED→GREEN 配对范围 T009–T157, RED 仅可在配对实现最终路径创建无业务规则、无副作用的最小 import skeleton, 有效 RED：collect-only 退出 0 且 errors=0，业务断言 failed>0 且 errors=0

### Community 45 - "US4 AI Batch Delivery"
Cohesion: 0.50
Nodes (4): US4 commits：dev@4a9974eaa80ae1e9b0e6a15035512bbb32b6b2d1、dev@a75e05576f8dfae98b199ea3411f29bc7f76466a、dev@9798aa0、dev@386cccb、dev@c83a4f0、dev@9b6809e、dev@d6754cb、dev@9932aa928132152cabedb2e273980f60cdd51f6c, T087–T097：AI batch、预览、Worker、反思、轮询和 Web RED，已完成, T098–T109：AI 结果、生成、执行、采用、反思、路由、Web 和审计实现，已完成, T110：US4 验收，dev@9932aa928132152cabedb2e273980f60cdd51f6c，126 passed，完整 610 passed、1 warning

### Community 46 - "US5 DOCX Import"
Cohesion: 0.50
Nodes (4): T111：确定性安全/恶意 DOCX/ZIP 测试工厂，已完成, T112–T117：DOCX 安全、来源、拆分、新增环节、采用和 Web RED，已完成, T118–T125：来源、OOXML、两阶段 AI、采用、API 和 Web 实现，已完成, T126：US5 独立验收，已完成

### Community 47 - "Backup & Restore"
Cohesion: 0.50
Nodes (4): Consistent backup and envelope: sqlite3.Connection.backup plus integrity/FK/count/hash and atomic package publication; portable/remote packages use scrypt-derived AES-256-GCM with random salt/nonce, AAD and fail-closed tag validation, Remote backup boundary and rotation: immutable encrypted WebDAV/S3 objects, remote failures/retries never block local transactions, daily keeps 30 successes while pre_migration/pre_restore are retained, Restore transaction: teacher explicitly chooses a concrete version; decrypt/validate in staging, reject future schema, create pre_restore protection, stop tasks, atomically replace and rollback on failure, Research decision for backup security: Connection.backup snapshots, KMBACKUP1 authenticated encryption and Windows keyring credentials; WebDAV/S3 are one-way immutable stores, not sync

### Community 48 - "Contribution Guidelines"
Cohesion: 1.00
Nodes (3): CONTRIBUTING.md Contribution Guide, Design → Implement Workflow, Implementation Issue Template

### Community 49 - "AI & Encrypted Backup"
Cohesion: 0.67
Nodes (3): 教师控制的可选 AI 与加密备份, 加密备份与原子恢复, 单向备份而非同步

### Community 50 - "Milestone Reports"
Cohesion: 0.67
Nodes (3): M7 complete M8 ready T142-T169 未开始, M8 命令 环境 浏览器 结果 证据 风险完整报告, 架构 契约 迁移 Repository API Worker Word Web 与标准五命令

### Community 51 - "Foundational Implementation"
Cohesion: 0.67
Nodes (3): T009–T012：依赖、公共契约、健康与事务/Alembic RED，已完成, T013–T019：公共契约、配置、数据库、替身及三运行入口实现，已完成, T020：Foundational 专项、五条质量命令与 Graphify 门禁，已完成

### Community 52 - "Identity Implementation"
Cohesion: 0.67
Nodes (3): T021–T025：WebAuthn、身份迁移、API 契约和浏览器流程 RED，已完成, T026–T034：身份模型、ceremony、限流、状态机、CLI、API 与 Web 实现，已完成, T035：M2 独立验收，已完成

### Community 53 - "Settings Implementation"
Cohesion: 0.67
Nodes (3): T036–T039：Settings 契约、规则、权限和 Web RED，已完成, T040–T044：园所、学期、班级、教师、年龄段和区域实现，已完成, T045：M3 独立验收，已完成

### Community 54 - "Manual Lesson Plan"
Cohesion: 0.67
Nodes (3): T046–T051：手工教案 Schema、持久化、API、日历和 Web RED，已完成, T052–T060：手工教案契约、模型、日历、Repository、服务、API 与 Web 实现，已完成, T061：关闭 AI、Worker 和在线工作日后的 US2 独立验收，已完成

### Community 55 - "AI Feature Implementation"
Cohesion: 0.67
Nodes (3): T062–T072：模型、密钥、SSRF、提示词、任务和 Web RED，已完成, T073–T085：AI 模型、提示词、加密、任务、Worker、API 与 Web 实现，已完成, T086：US3 独立验收，已完成

### Community 56 - "AI Capability Sequencing"
Cohesion: 0.67
Nodes (3): Controlled capability sequence: Slice 1 manual MVP → Slice 2A optional AI preview → Slice 2B Agent Foundation with Context and READ/DRAFT only → Slice 3 backup/restore → Agent WRITE with PlanPatch/Confirmation/audit/transaction → Level 3 deferred, AiGenerationCoordinator remains Slice 2A structured preview; Slice 2B adds Agent Context and READ/DRAFT; confirmation WRITE is only after Slice 3, with Agent transient state in memory, Research decision for controlled Agent: one Application AgentRuntime, Provider port and closed Tool registry; Slice 2B READ/DRAFT zero-write, Slice 3 gate before WRITE and no long-term memory

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
- `幼儿园管理助手 (kindergarten-manager-desktop)` → `旧 Cloud B/S 与 kindergartenManager (历史)`  [AMBIGUOUS]
  .specify/memory/constitution.md · relation: conceptually_related_to

## Knowledge Gaps
- **234 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+229 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `日期选择与校验` (3× useful, score=1.46835702)
- `共同实施路线` (2× useful, score=0.987287691)
- `Web、API 与 Worker 服务边界` (2× useful, score=0.987287691)
- `目标服务架构` (2× useful, score=0.987287691)
- `班级与教师配置` (2× useful, score=0.974900982)
- `教案结构化` (2× useful, score=0.974900982)

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