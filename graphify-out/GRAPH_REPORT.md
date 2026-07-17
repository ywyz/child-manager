# Graph Report - child-manager  (2026-07-17)

## Corpus Check
- 185 files · ~101,382 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2524 nodes · 2719 edges · 745 communities (174 shown, 571 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 55 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `38ff8ee2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_health.py
- Child Manager 产品与工程路线图
- Python 质量门禁 Job
- M0 阻塞项统一修复执行方案（Codex + Trae）
- Child Manager 2026-07-14 编码前审查解决方案
- Tasks: 首期一日活动计划完整闭环
- Phase 1 数据模型：首期一日活动计划完整闭环
- AI 生成与提示词规则
- Phase 0 研究：首期一日活动计划完整闭环
- observability.py
- README.md
- Child Manager Agent 开发规则
- ContractModel
- Child Manager 项目上下文
- proxy_request
- Functional Requirements
- test_foundation.py
- 2026-07-14 仓库与分支状态
- Tasks: [FEATURE NAME]
- SKILL.md
- Child Manager 幼儿园教育管理系统
- ADR-0001：只交付 Cloud 版本，首期单园运行并保留园所隔离边界
- ADR-0007：采用 Caddy、Docker Compose 与文件挂载 Secrets
- 5. 端点目录
- Child Manager 双 Agent 独立开发协议
- M1 工程骨架与质量基线 Issue 草稿与执行记录
- test_local_development_profiles.py
- 6. 浏览器验收路径
- common.sh
- Execution Steps
- Implementation Plan: 首期一日活动计划完整闭环
- Child Manager 一日活动计划 OpenAPI 3.1
- ADR-0003：PostgreSQL 保存任务权威状态，Dramatiq 与 Redis 负责异步执行
- Child Manager 数据模型设计
- ADR-0005：AI 供应商中立，并建立管理员专用提示词系统
- Child Manager 系统架构设计
- Feature Specification: [FEATURE NAME]
- ADR-0006：一日活动计划采用固定 Word 模板导出边界
- ADR-0008：日期与外部服务采用本地优先和软降级
- Child Manager 双实现本地开发环境
- Core Principles
- 后台任务状态机与 AI 采用契约
- SKILL.md
- SKILL.md
- SKILL.md
- ADR-0002：采用独立 Web、API、Worker 运行单元的模块化单体
- ADR-0004：采用同源入口、HttpOnly Cookie 与 API 统一授权
- Child Manager PostgreSQL 数据库 Schema
- 教案管理 PRD（首期：一日活动计划）
- Core Principles
- transactional_session
- Child Manager 文档交叉审计合并结论
- 右侧列
- 这是一份word表格
- 18. 验收标准
- Implementation Plan: [FEATURE]
- SKILL.md
- SKILL.md
- SKILL.md
- 3. 总体建模原则
- 9. 一日活动计划模型
- 3. 二十六项问题的最终结论
- 3.9 Codex 交叉审计事项
- 10. 教案栏目与格式
- 13. AI 生成流程
- 右侧列
- 右侧列
- 右侧列
- 右侧列为两行：
- 右侧列为两行：
- test_openapi_document.py
- 完整 SDD 工作流
- env.py
- 5. 园所与身份模型
- 6. 教学设置模型
- 3. PostgreSQL 物理约定
- 5. 园所与身份 Schema
- 6. 教学设置 Schema
- 9. 一日活动计划 Schema
- 9. 后台任务架构
- 12. AI 模型与提示词管理
- 7. 首期必要设置
- 9. 日期与上下文规则
- SKILL.md
- SKILL.md
- 21. 测试与验收
- 5. 代码组织与依赖方向
- 8. 数据架构
- 3.2 模板说明与业务规则
- 4. 项目文档更新矩阵
- 11. 计划管理流程
- 14. Word 导出
- 17. 非功能要求
- Q: 请阅读以上内容和现有的AGENTS.MD,还有ywyz/kindergartenManager.git的AGENTS.MD，你认为i还需要再加入点什么？
- Q: 请阅读以上内容和现有的README.md,AGENTS.md,还有ywyz/kindergartenManager.git的文档，你认为CONTEXT.md需要再加入点什么？
- Q: 请根据现有文档，和旧仓库的文件思考如何撰写 docs/PRD/lesson-management.md
- Q: 接下来需要生成什么文件呢
- Q: 系统架构文档应如何定义目标服务架构、服务边界、共享契约、部署拓扑与首期实施顺序？
- Q: 哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？
- Q: 一日活动计划系统的数据实体、关系、唯一约束、历史版本、异步任务和安全边界是什么？
- Q: 请使用/graphify update. 进行更新，同时使用子代理进行语义更新，然后思考还需要完成什么任务
- create-new-feature.sh
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- 15. 数据快照边界
- 22. 后续扩展边界
- 2. 设计来源与旧系统取舍
- 8. 提示词模型
- 8. 提示词 Schema
- 10. AI 与提示词架构
- 6. 请求、认证与授权
- 3.3 数据模型、保留与任务关系
- 3.7 API 与页面信息架构
- 5. 用户与权限
- 8. 核心业务对象
- Child Manager OpenAPI v1
- FakeCalendar
- clock.py
- redis.py
- 11. 后台任务与 AI 结果
- 16. 外键与删除行为
- 4. 模型总览
- 7. AI 模型档案
- 10. 后台任务与 AI 结果 Schema
- 12. 系统支撑 Schema
- 2. 事实来源与旧仓库取舍
- 7. AI 模型档案 Schema
- 11. Word 与文件架构
- 13. 配置、密钥与安全
- 15. 生产部署延后边界
- 4. 架构总览
- 7. API 与契约
- 3.5 API、任务状态与幂等
- 3.6 测试与可访问性
- 3.8 编辑与 AI 采用
- 15. 安全、隐私与审计
- 4. 产品目标
- FakeAiClient
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- check-prerequisites.sh
- setup-plan.sh
- setup-tasks.sh
- __init__.py
- 检测与分析报告
- 需求与任务语义清单
- Spec Kit 跨制品分析
- 澄清焦点与生成清单
- 需求写作的单元测试
- Spec Kit 需求检查清单
- 歧义与覆盖扫描
- 逐问逐答与增量回写
- Spec Kit 规格澄清
- Spec Kit 宪章维护
- 宪章同步影响报告
- 语义版本与依赖模板同步
- 只追加收敛任务
- 意图清单与代码差距评估
- Spec Kit 实现收敛
- 实施前检查清单门禁
- 分阶段任务执行与验证
- 阶段一数据模型、契约与验证指南
- 阶段零研究与消歧
- 规格质量清单迭代验证
- 功能目录与可测试规格生成
- 依赖、并行与独立验收校验
- 按用户故事生成可执行任务
- 规范化 Issue 创建
- GitHub 远端匹配与任务去重门禁
- Spec Kit 任务转 GitHub Issue
- 真实验证证据与生产部署延后
- 服务、园所与事务边界
- 教师控制、AI 与 Word 保真
- 检查清单模板
- 项目宪章模板
- 宪章检查与两阶段设计门禁
- 实施计划模板
- 功能规格模板
- 用户故事、需求与可度量结果
- 设置、基础、故事与收尾阶段
- 用户故事任务模板
- AI 预览与教师采用
- AI 预览显式采用
- 归档只读与恢复编辑
- 审计只记录必要元数据
- 一日活动计划业务不变量
- 同班同日唯一当前教案
- 日期校验只软提示
- 确定性与风险相称测试
- AI Key 加密与数据最小化
- 事实来源冲突时停止固化实现
- 固定 Word 模板完整性
- graphify、Spec Kit 与工程技能规则
- 园所数据隔离
- Repository 园所隔离
- 最小实现边界
- 一键生成四栏目
- 乐观锁禁止静默覆盖
- 生产部署延后
- 生产部署延后至功能验收后
- 提示词白名单与发布版本
- Web API Worker 服务边界
- 历史快照触发边界
- 教师班级权限与管理员全园访问
- 教学周按周一递增
- Web、API、Worker 依赖方向
- Codex 分支内 M1：T004–T020 已完成
- uv run pyright
- uv run pytest
- uv run ruff check .
- uv run ruff format --check .
- uv sync --locked
- Issue #2 最终证据回填
- M1 共享父阶段仍为 in_progress
- 共享双环境同时启动门禁
- 五条标准质量命令
- T008 分支独立验收
- 2026-07-13 M0 修复方案历史执行快照
- 避免日期专用文档提交
- Codex 实现子 Issue
- 共同基线分支创建
- 冲突冻结
- 双 Agent 启动前检查清单
- GitHub Issue 创建阶段
- graphify 完整性验收
- graphify 工作区修改处置
- 独立授权边界
- 实时基线证据
- M1 出口门禁
- M1 Issue 结构
- 非破坏性工作区保留
- 生产部署非目标
- 只读交叉评审
- 推荐执行顺序
- 共享文档同步
- M1 共享父 Issue
- 启动清单循环措辞澄清
- 执行停止条件
- T003 共享授权与分支门禁
- T004-T020 实现任务
- TDD 驱动的 M1 实现
- Trae 实现子 Issue
- 2026-07-14 只读编码前收敛审查报告
- 分支操作授权门禁
- Canonical 阶段状态一致性
- 当前不能进入编码
- combined-audit.md
- 有条件进入 M1 Issue 设计与草拟阶段
- 宪章约束已进入计划与任务
- CONTEXT.md
- 双 Agent 开发协议
- Git 与 GitHub 基线
- 新报告 Graphify 语义更新待确认
- 既有 Graphify 工作区修改
- I-01 Issue 粒度与任务映射
- I-02 启动清单循环措辞
- I-03 工作区基线清洁
- I-04 状态日期
- 实现授权门禁
- GitHub Issue 操作授权门禁
- M0-G1 至 M0-G8 已关闭
- M1 Codex 实现子 Issue
- M1 父子 Issue 层级
- M1 共享父 Issue
- M1 Trae 实现子 Issue
- M9 生产部署延后
- plan.md
- 双 Agent 只读交叉评审
- docs/ROADMAP.md
- spec.md
- Spec Kit 需求与任务完整覆盖
- T003 双实现分支任务
- T004 至 T020 有序执行清单
- tasks.md
- 仅允许本地开发与测试最小依赖
- 继续有效的安全结果
- age_groups
- ai_generation_results
- ai_model_profile_capabilities
- ai_model_profiles
- AI 模型档案
- audit_events
- background_jobs
- class_areas
- class_teachers
- classes
- daily_activity_plan_snapshots
- daily_activity_plans
- 园所与身份模型
- 停用、归档与不可变历史
- PostgreSQL 权威后台任务
- 后台任务状态集合
- kindergartens
- lesson_plan_sources
- Alembic 迁移顺序
- 总体建模原则
- 学期外教学周次双空
- 关系表头与 JSONB 正文
- 教案六大正文栏目
- AI 结构化预览与采用
- prompt_definitions
- 提示词模型
- prompt_test_runs
- prompt_versions
- 文档目的
- refresh_tokens
- 数据保留与清理
- roles
- JSONB Schema 演进
- semesters
- 教案、AI、审计与日志快照边界
- 首期 24 张表总览
- 教学设置模型
- 园所隔离与组合外键
- 时间与日期语义
- user_roles
- users
- UUIDv7 主键
- 数据模型测试与验收
- Word 导出模型
- workday_cache
- Schema 验收测试
- age_groups
- ai_generation_results
- ai_model_profile_capabilities
- ai_model_profiles
- Alembic 迁移序列
- 审计只插入约束
- audit_events
- background_jobs
- class_areas
- class_teachers
- classes
- daily_activity_plan_authors
- daily_activity_plan_exports
- daily_activity_plan_snapshots
- daily_activity_plans
- 导出快照、文件与状态约束
- 园所组合外键矩阵
- 后台任务状态、幂等与租约约束
- kindergartens
- lesson_plan_sources
- 学期外周次双空检查约束
- 部分唯一索引与排他约束
- PostgreSQL 物理约定
- 教案乐观锁更新
- PostgreSQL 与 SQLite 验证矩阵
- AI 结果采用、拒绝与清理约束
- prompt_definitions
- prompt_test_runs
- prompt_versions
- refresh_tokens
- roles
- 24 表 Schema 总览
- semesters
- 园所组合外键规则
- 应用事务不变量
- user_roles
- users
- workday_cache
- 供应商中立 AI 适配器
- AI 预览采用边界
- API 与共享契约
- 架构目标
- 架构级验证
- 同源 Web BFF
- 工作日与日期服务
- 深模块用例接口
- 后端模块单向依赖
- 生产部署延后边界
- 投递、租约、幂等与恢复扫描
- DOCX 上传与立即清理
- Dramatiq Worker 运行单元
- 故障与降级矩阵
- FastAPI API 运行单元
- 实施顺序 M1–M8
- 最小跨进程任务契约
- 后台任务状态机
- 逻辑架构视图
- NiceGUI Web 运行单元
- 可观测性与审计
- PostgreSQL 权威存储
- 提示词服务与确定性渲染
- Redis 投递协调
- 配置、密钥与安全边界
- Cookie 会话、CSRF 与来源信任
- 1–2 秒短轮询
- 园所与班级授权
- 事务所有权
- Word 模板、临时文件与原子输出
- main codex trae 分支所有权
- 冲突与高影响歧义共同冻结
- 双 Agent 独立开发协议
- M1 编码前有序启动流程
- 只读交叉评审
- 独立实现子 Issue
- 共享文档独立提交同步
- 共享父 Issue
- 正文
- 标题
- Codex M1 授权与 T004–T020 验收已完成
- AI 重试分类与三次上限
- 归档教案仍占唯一键
- 审计至少保留一年
- 集体活动先拆分后新增
- 导出前必须成功保存
- 首期容量与响应目标
- 历史恢复保留恢复前内容
- 独立导出历史与私有副本
- 最后一个有效管理员不可停用
- 班级区域有序且分类校验
- Redis 故障时保留 pending_dispatch
- 创建后活动日期不可修改
- 预览仅随实际输入变化失效
- 生产恢复指标延后验收
- 反思三字段与 200 码点限制
- 管理员与教师权限矩阵
- 七个稳定任务级提示词
- 各实现分支内 M1 验证
- M1 共享同机并行门禁
- M1 三个独立运行入口
- 10. M4：AI 模型与提示词基础 / 交付范围
- 10. M4：AI 模型与提示词基础 / 出口门禁
- 11. M5：无 AI 教案手工闭环 / 交付范围
- 11. M5：无 AI 教案手工闭环 / 出口门禁
- 12. M6：AI 异步生成与人工采用 / 交付范围
- 12. M6：AI 异步生成与人工采用 / 出口门禁
- 13. M7：固定 Word 导出与历史 / 交付范围
- 13. M7：固定 Word 导出与历史 / 出口门禁
- 14. M8：首期功能验收 / 验收范围
- 14. M8：首期功能验收 / 出口门禁
- 15. M9：生产安全与部署复审 / 必须另行决定
- 15. M9：生产安全与部署复审 / 出口门禁
- 6. M0：共享设计基线 / 完成后的授权动作
- 6. M0：共享设计基线 / 已具备
- 6. M0：共享设计基线 / 出口门禁
- 6. M0：共享设计基线 / 目标
- 7. M1：工程骨架与质量基线 / 交付范围
- 7. M1：工程骨架与质量基线 / 出口门禁
- 7. M1：工程骨架与质量基线 / 明确不做
- 8. M2：认证、授权与身份审计 / 交付范围
- 8. M2：认证、授权与身份审计 / 出口门禁
- 9. M3：首期必要设置 / 交付范围
- 9. M3：首期必要设置 / 出口门禁
- 内容门禁与操作授权分离
- combined-audit 审计事实基线
- 最终 docs-only main 共享基线
- Child Manager 20260713 编码前审查报告
- FR-031 快照原因码与恢复顺序
- Git 历史隐私清理
- M0 complete
- M0-G1 至 M0-G8 门禁体系
- M1 ready
- Q13 客户端幂等 scope 与 fingerprint
- T002 Pre-M1 一致性审查
- T003 双 Agent 同基线分支流程
- 模板说明契约一致性
- AI 生成边界
- 班级与教师配置
- 日期选择与校验
- 需要直接比较文件
- AGENTS.md 补充建议查询
- Word 格式边界
- AI 教案结构化
- 配置
- 区分已确认设计与已实现状态
- 日期选择与校验
- CONTEXT.md 补充建议查询
- 集成式 NiceGUI 架构
- 不继承旧仓库架构
- 本地优先架构
- MySQL
- Word 导出格式控制
- 一日活动计划 PRD 范围结论
- 一日活动计划 PRD 查询记录
- 下一份文档查询记录
- 系统架构文档作为下一步
- 系统架构定义查询记录
- Web API Worker 架构与实施顺序
- 旧图谱未覆盖最新架构
- ADR 划分查询记录
- 修正后的一日活动计划数据模型结论
- 数据模型边界查询记录
- child-manager
- Cloud-only 三服务架构
- 固定 Word 模板导出
- 规格质量检查清单
- 五轮一致性验证记录
- 待确认、采用、拒绝与过期
- ai.batch 父任务聚合
- 受理、投递、租约与恢复
- 执行状态机
- 集体活动部分成功
- 任务幂等契约
- 各任务输入快照
- 任务类型
- AI 预览有效性
- 模型调用与重试分类
- Web 轮询契约
- 统一响应与错误
- 提示词测试冻结输入 Schema
- Cookie 安全方案
- 教案快照 Schema
- API v1 契约总则
- 审计端点
- 认证与用户端点
- BFF 与可信上下文
- 分页、错误与 Request ID
- 契约演进
- Cookie CSRF 会话契约
- Cookie、令牌与 CSRF
- Word 导出端点
- Idempotency-Key 契约
- 幂等异步任务契约
- 任务与 AI 预览端点
- 乐观锁契约
- 乐观锁与预览失效校验
- 权限矩阵
- 教案端点
- 提示词端点
- 设置端点
- 稳定错误码
- ai_generation_results 预览
- AI 模型与提示词实体组
- audit_events 白名单元数据
- background_jobs 任务头
- 通用数据规则
- daily_activity_plan_exports 导出快照
- 必测数据行为
- 园所与身份实体组
- 六阶段迁移顺序
- 学期外周次双空
- PlanContentV1 六栏目
- 24 表关系总览
- Phase 1 数据模型
- 教学设置实体组
- 快照创建与不可变规则
- 关键事务不变量
- workday_cache 三类 TTL
- API 运行入口：python -m apps.api
- init-admin 真实行为由 T034 实现
- M1 运行入口契约
- Web 运行入口：python -m apps.web
- Worker 运行入口：python -m apps.worker
- Quickstart 五条完整质量门禁
- init-admin 首次初始化验收合同
- 隔离自动化测试数据库
- T035 后启用 CSRF 业务端点检查
- 三个独立进程启动验收
- 研究文档中的 M1 状态
- Web/API/Worker 三个独立运行单元
- 首期一日活动计划功能规格
- FR-001–FR-006 身份权限与园所边界
- FR-007–FR-012 首期必要设置
- FR-013–FR-020 模型与提示词
- FR-021–FR-033 手工教案与历史
- FR-034–FR-043 异步 AI 与采用
- FR-044–FR-048 集体活动
- FR-049–FR-056 Word 导出
- FR-057–FR-072 安全审计与质量
- Requirements
- SC-001–SC-003 离线访问与并发
- SC-004–SC-006 提示词与 AI 可靠性
- SC-007–SC-011 Word 性能与安全
- SC-012–SC-017 韧性契约与端到端
- Success Criteria
- User Scenarios & Testing
- User Story 1 管理员安全初始化与必要设置
- User Story 2 教师纯手工教案闭环
- User Story 3 管理员配置模型与提示词
- User Story 4 教师按栏目使用 AI
- User Story 5 集体活动原始教案
- User Story 6 固定 Word 导出
- User Story 7 审计与可降级服务
- Foundational 完成门禁
- M8 完整验收门禁
- Parallel Foundation
- Parallel US1 / US2
- Parallel US3 / US4 / US5
- Parallel US6 / US7 / Polish
- Phase 10 Polish & Cross-Cutting Concerns
- Phase 1 Setup
- Phase 2 先写失败测试
- Phase 2 Foundational
- Phase 2 实现共享基础
- Tests for User Story 1
- Phase 3 User Story 1
- Tests for User Story 2
- Phase 4 User Story 2
- Tests for User Story 3
- Phase 5 User Story 3
- Tests for User Story 4
- Phase 6 User Story 4
- Tests for User Story 5
- Phase 7 User Story 5
- Tests for User Story 6
- Phase 8 User Story 6
- Tests for User Story 7
- Phase 9 User Story 7
- Setup 完成门禁
- T004
- T005
- T006
- T007
- T008
- T009
- T010
- T011
- T012
- T013
- T014
- T015
- T016
- T017
- T018
- T019
- T020
- 首期一日活动计划任务清单
- 表格第二行：星期与日期
- 表格第七行：下午户外游戏
- 文件第二行：班级与教师
- 表格第八行：一日活动反思
- 表格第五行：集体活动
- 表格第六行：室内区域游戏
- 编号、句号、问号与换行格式
- 表格第三大行：晨间活动
- 表格第四行：晨间谈话
- 仅 AI 新增集体环节标红
- 一日活动计划 Word 系统说明
- 表格第一行：教学周次
- 文件第一行：园所与学期月份范围
- Cloud 教育管理系统定位
- Cloud-only 与部署延后基线
- Codex 分支 M1 五条命令及 61 项测试通过
- 不可误读的已确认决策
- 当前状态与交接入口
- CONTEXT 状态更新规则
- 一日活动计划首期闭环
- 一日活动计划业务不变量
- 首期非目标
- 设计编码前固定阅读顺序
- 高风险点与缓解措施
- 旧仓库仅作经验参考
- 首期必要设置
- 管理员教师角色与 API 授权
- Web API Worker 与园所数据边界
- M1 至 M9 共同实施路线
- 共享 M1 双环境门禁下一步
- 系统架构基线
- 实现分支验证基线
- 固定 Word 模板导出规则
- Codex 分支验收证据要求
- Codex 实现子 Issue #2
- Codex T004 至 T020 完成清单
- Codex 红绿测试与最小实现原则
- 双 Agent 协作边界
- Codex 与 Trae 共同提交基线
- 草稿基线与 graphify 处置记录
- M1 入口条件
- M1 工程骨架 Issue 草稿与执行记录
- M1 草稿只读复核清单
- M1 共同出口门禁
- M1 共同工程骨架目标
- M1 共享父 Issue #1
- M1 共享事实来源
- T003 与 T004 至 T020 任务映射
- Trae 实现子 Issue #3
- 共享草稿不镜像 Trae 实时提交与验收
- Trae 状态以 Issue #3 与 trae 分支实时证据为准
- Trae T004 至 T020 独立执行清单
- Trae 红绿测试与最小实现原则
- API 契约快速检查
- API CHILD_MANAGER_BIND_HOST 必须为回环地址
- 审计与敏感信息验收
- 初始化登录与会话验收
- 自动化质量门禁
- 浏览器验收路径
- M8 完整验收记录要求
- 数据库迁移与首次管理员初始化
- 存活就绪与依赖降级语义
- 锁定安装与本地依赖
- 纯手工教案闭环验收
- Phase 1 首期实现与验收合同
- Quickstart 前提与反目标
- 本地开发档位隔离变量
- Web 启动使用 CHILD_MANAGER_WEB_PORT 档位变量
- 一日活动反思生成验收
- 可靠 AI 任务与栏目级采用
- 集体活动安全 DOCX 处理
- Web 同源 BFF 转发契约
- 必要设置与权限验收
- API Worker Web 三个独立进程
- Web --host 必须为回环地址
- Word 导出与历史副本验收
- Word 模板哈希与原件状态检查
- 工作日判断与软降级
- 正文
- MemoryLoginThrottle
- ports.py
- build_health_dependencies
- Python 质量门禁 Job
- middleware.py
- 正文
- 正文
- app.py
- CI PostgreSQL 服务
- 0001_identity_and_audit.py
- test_0001_identity.py
- _run_cli
- GitHub Actions 质量工作流
- 3.4 加密与密钥
- NOTICE.md
- Docker 镜像构建延后到 M9 并由新部署 ADR 定义
- M1 至 M8 每次推送门禁：依赖锁定、Ruff、Pyright、Pytest
- test_identity_isolation.py

## God Nodes (most connected - your core abstractions)
1. `IdentityRepository` - 35 edges
2. `IdentityError` - 34 edges
3. `ContractModel` - 31 edges
4. `IdentityService` - 30 edges
5. `create_app()` - 25 edges
6. `AuditRepository` - 24 edges
7. `SessionUser` - 24 edges
8. `Child Manager 数据模型设计` - 24 edges
9. `教案管理 PRD（首期：一日活动计划）` - 22 edges
10. `Child Manager 系统架构设计` - 22 edges

## Surprising Connections (you probably didn't know these)
- `CI PostgreSQL 服务` --semantically_similar_to--> `PostgreSQL 本地服务`  [INFERRED] [semantically similar]
  .github/workflows/quality.yml → compose.dev.yaml
- `PostgreSQL 18 Alpine 固定 Digest` --semantically_similar_to--> `PostgreSQL 18 Alpine 固定 Digest`  [INFERRED] [semantically similar]
  .github/workflows/quality.yml → compose.dev.yaml
- `create_app()` --indirect_call--> `IdentityError`  [INFERRED]
  apps/api/app.py → packages/backend/identity/service.py
- `HealthDependencies` --uses--> `IdentityError`  [INFERRED]
  apps/api/dependencies.py → packages/backend/identity/service.py
- `HealthDependencies` --uses--> `IdentityService`  [INFERRED]
  apps/api/dependencies.py → packages/backend/identity/service.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **M1 分支独立验收** — context_codex_m1_t004_t020_complete, context_t008_branch_independent_acceptance, docs_roadmap_m1_branch_local_gate, specs_001_daily_activity_plan_quickstart_isolated_test_database, specs_001_daily_activity_plan_quickstart_five_commands [EXTRACTED 1.00]
- **M1 共享父门禁** — context_m1_parent_in_progress, context_shared_dual_environment_gate, docs_roadmap_m1_shared_parallel_gate, specs_001_daily_activity_plan_research_m1_status [EXTRACTED 1.00]
- **M1 双 Agent 共同基线与独立实现治理** — context_shared_implementation_route, docs_development_m1_issue_drafts_shared_parent_issue, docs_development_m1_issue_drafts_common_baseline, docs_development_m1_issue_drafts_codex_issue, docs_development_m1_issue_drafts_trae_issue [EXTRACTED 1.00]
- **档位隔离下的三服务回环启动与就绪验收** — context_service_and_data_boundaries, specs_001_daily_activity_plan_quickstart_profile_isolation, specs_001_daily_activity_plan_quickstart_api_loopback_binding, specs_001_daily_activity_plan_quickstart_web_loopback_binding, specs_001_daily_activity_plan_quickstart_three_independent_processes, specs_001_daily_activity_plan_quickstart_health_readiness_semantics [INFERRED 0.95]
- **状态证据到 M1 门禁再到完整验收的验证链** — context_verification_baseline, context_codex_61_tests_verification, docs_development_m1_issue_drafts_shared_exit_gate, docs_development_m1_issue_drafts_codex_acceptance_evidence, specs_001_daily_activity_plan_quickstart_automated_quality_gate, specs_001_daily_activity_plan_quickstart_complete_acceptance_record [INFERRED 0.95]
- **M1 T004–T020 工程基础** — specs_001_daily_activity_plan_tasks_t004, specs_001_daily_activity_plan_tasks_t005, specs_001_daily_activity_plan_tasks_t006, specs_001_daily_activity_plan_tasks_t007, specs_001_daily_activity_plan_tasks_t008, specs_001_daily_activity_plan_tasks_t009, specs_001_daily_activity_plan_tasks_t010, specs_001_daily_activity_plan_tasks_t011, specs_001_daily_activity_plan_tasks_t012, specs_001_daily_activity_plan_tasks_t013, specs_001_daily_activity_plan_tasks_t014, specs_001_daily_activity_plan_tasks_t015, specs_001_daily_activity_plan_tasks_t016, specs_001_daily_activity_plan_tasks_t017, specs_001_daily_activity_plan_tasks_t018, specs_001_daily_activity_plan_tasks_t019, specs_001_daily_activity_plan_tasks_t020 [EXTRACTED 1.00]
- **七个用户故事规格任务映射** — specs_001_daily_activity_plan_spec_user_story_1, specs_001_daily_activity_plan_spec_user_story_2, specs_001_daily_activity_plan_spec_user_story_3, specs_001_daily_activity_plan_spec_user_story_4, specs_001_daily_activity_plan_spec_user_story_5, specs_001_daily_activity_plan_spec_user_story_6, specs_001_daily_activity_plan_spec_user_story_7, specs_001_daily_activity_plan_tasks_phase_3_user_story_1, specs_001_daily_activity_plan_tasks_phase_4_user_story_2, specs_001_daily_activity_plan_tasks_phase_5_user_story_3, specs_001_daily_activity_plan_tasks_phase_6_user_story_4, specs_001_daily_activity_plan_tasks_phase_7_user_story_5, specs_001_daily_activity_plan_tasks_phase_8_user_story_6, specs_001_daily_activity_plan_tasks_phase_9_user_story_7 [EXTRACTED 1.00]
- **需求与成功标准可追踪性** — specs_001_daily_activity_plan_spec_fr_001_006_identity_authorization, specs_001_daily_activity_plan_spec_fr_007_012_required_settings, specs_001_daily_activity_plan_spec_fr_013_020_models_prompts, specs_001_daily_activity_plan_spec_fr_021_033_manual_plans_history, specs_001_daily_activity_plan_spec_fr_034_043_async_ai_adoption, specs_001_daily_activity_plan_spec_fr_044_048_collective_activity, specs_001_daily_activity_plan_spec_fr_049_056_word_export, specs_001_daily_activity_plan_spec_fr_057_072_security_quality, specs_001_daily_activity_plan_spec_sc_001_003_offline_access_concurrency, specs_001_daily_activity_plan_spec_sc_004_006_prompt_ai_reliability, specs_001_daily_activity_plan_spec_sc_007_011_word_performance_security, specs_001_daily_activity_plan_spec_sc_012_017_resilience_contract_e2e [INFERRED 0.85]
- **M1 三个独立运行单元** — specs_001_daily_activity_plan_plan_api_entry, specs_001_daily_activity_plan_plan_worker_entry, specs_001_daily_activity_plan_plan_web_entry, specs_001_daily_activity_plan_plan_m1_entry_contract [EXTRACTED 1.00]
- **M1 共享父子 Issue 结构** — docs______20260714_____m1_shared_parent_issue, docs______20260714_____m1_codex_child_issue, docs______20260714_____m1_trae_child_issue [EXTRACTED 1.00]
- **M1 独立授权门禁序列** — docs______20260714_____issue_operation_authorization, docs______20260714_____branch_operation_authorization, docs______20260714_____implementation_authorization [EXTRACTED 1.00]
- **Canonical 阶段状态证据链** — docs______20260714_____roadmap, docs______20260714_____context, docs______20260714_____spec, docs______20260714_____plan, docs______20260714_____tasks, docs______20260714_____combined_audit [EXTRACTED 1.00]
- **M1 一父两子 Issue 结构** — docs_20260714_shared_parent_issue, docs_20260714_codex_implementation_child_issue, docs_20260714_trae_implementation_child_issue [EXTRACTED 1.00]
- **Issue 分支编码独立授权流** — docs_20260714_github_issue_creation_stage, docs_20260714_common_baseline_branch_creation, docs_20260714_tdd_m1_implementation [EXTRACTED 1.00]
- **运行单元与权威状态** — docs_design_system_architecture_nicegui_web, docs_design_system_architecture_fastapi_api, docs_design_system_architecture_dramatiq_worker, docs_design_system_architecture_postgresql, docs_design_system_architecture_redis [EXTRACTED 1.00]
- **Word 一日活动计划栏目** — templates_teacherplan_morning_activity, templates_teacherplan_morning_talk, templates_teacherplan_group_activity, templates_teacherplan_indoor_area_game, templates_teacherplan_afternoon_outdoor_game, templates_teacherplan_daily_reflection [EXTRACTED 1.00]
- **Specify Plan Tasks Implement 全周期** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **宪章到规格计划任务模板的治理传播** — _specify_templates_plan_template_plan_template, _specify_templates_spec_template_spec_template, _specify_templates_tasks_template_tasks_template [INFERRED 0.85]
- **一日活动计划范围、架构与数据边界知识链** — graphify_out_memory_query_20260711_020708_docs_prd_lesson_management_m_prd_scope, graphify_out_memory_query_20260711_024218_service_architecture_sequence, graphify_out_memory_query_20260712_071357_corrected_data_model [INFERRED 0.75]
- **AI 预览与教师最终控制** — agents_ai_preview_explicit_adoption, docs_prd_lesson_management_preview_validity_by_actual_inputs, docs_prd_lesson_management_ai_retry_taxonomy [EXTRACTED 1.00]
- **教案任务预览快照导出持久化链路** — docs_design_data_model_daily_activity_plans, docs_design_data_model_background_jobs, docs_design_data_model_ai_generation_results, docs_design_data_model_daily_activity_plan_snapshots [EXTRACTED 1.00]

## Communities (745 total, 571 thin omitted)

### Community 0 - "test_health.py"
Cohesion: 0.06
Nodes (57): create_app(), _error_response(), _login_throttle(), Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), _ai_unconfigured() (+49 more)

### Community 1 - "Child Manager 产品与工程路线图"
Cohesion: 0.04
Nodes (49): 10. M4：AI 模型与提示词基础, 11. M5：无 AI 教案手工闭环, 12. M6：AI 异步生成与人工采用, 13. M7：固定 Word 导出与历史, 14. M8：首期功能验收, 15. M9：生产安全与部署复审, 16. 当前状态快照, 17. Roadmap 更新规则 (+41 more)

### Community 2 - "Python 质量门禁 Job"
Cohesion: 0.13
Nodes (16): CHILD_MANAGER_DATABASE_NAME 强制变量, Compose 项目隔离 PostgreSQL 卷, 本地依赖 Compose 清单, PostgreSQL 健康检查, PostgreSQL 回环绑定, CHILD_MANAGER_POSTGRES_PASSWORD 外部变量, CHILD_MANAGER_POSTGRES_PORT 强制变量, PostgreSQL 本地服务 (+8 more)

### Community 3 - "M0 阻塞项统一修复执行方案（Codex + Trae）"
Cohesion: 0.05
Nodes (42): 1. 联合结论, 2.1 文档状态, 2.2 已确认满足的规则, 2. 当前文档与已满足规则, 3.1 模型与契约, 3.2 模板说明, 3.3 状态、证据与分支流程, 3.4 静态验证、图谱、历史与最终基线 (+34 more)

### Community 4 - "Child Manager 2026-07-14 编码前审查解决方案"
Cohesion: 0.05
Nodes (41): 1. 结论, 2.1 Git 与 GitHub, 2.2 当前阶段状态, 2.3 M0-G1～G8 最终汇总, 2. 审查基线, 3.1 指标, 3.2 覆盖与宪章, 3. Spec Kit 非破坏性一致性审查 (+33 more)

### Community 5 - "Tasks: 首期一日活动计划完整闭环"
Cohesion: 0.04
Nodes (47): Dependencies & Execution Order, Foundation, Implementation for User Story 2, Implementation for User Story 3, Implementation for User Story 4, Implementation for User Story 5, Implementation for User Story 6, Implementation for User Story 7 (+39 more)

### Community 6 - "Phase 1 数据模型：首期一日活动计划完整闭环"
Cohesion: 0.05
Nodes (37): 10. 迁移顺序, 11. 必测数据行为, 1. 通用规则, 2. 关系总览, 3.1 `kindergartens`, 3.2 `users`, 3.3 `roles`, 3.4 `user_roles` (+29 more)

### Community 8 - "Phase 0 研究：首期一日活动计划完整闭环"
Cohesion: 0.05
Nodes (37): 10. 已排除范围, 1. 研究方法与决策优先级, 2.1 首期使用一套 Spec Kit 文档, 2.2 独立运行单元与模块化单体, 2.3 技术基线与依赖, 2. Feature 与架构, 3.1 当前学期和学期外日期, 3.2 区域按目标栏目校验 (+29 more)

### Community 9 - "observability.py"
Cohesion: 0.05
Nodes (51): Actor, main(), load_job(), Broker, 只接收 job_id 的 M1 Dramatiq actor。, 验证最小消息；后续里程碑将从 PostgreSQL 加载权威上下文。, register_actors(), build_redis_broker() (+43 more)

### Community 10 - "README.md"
Cohesion: 0.11
Nodes (21): Child Manager 架构决策记录, 与旧仓库 ADR 的关系, 决策索引, 新增 ADR 的判断标准, 状态约定, Content Quality, Feature Readiness, Notes (+13 more)

### Community 11 - "Child Manager Agent 开发规则"
Cohesion: 0.06
Nodes (35): 10. 一日活动计划业务不变量, 11.1 模型访问, 11.2 提示词管理, 11.3 生成行为, 11. AI 与提示词规则, 12. Word 模板与导出, 13. 安全与隐私硬性规则, 14. 审计、日志与错误处理 (+27 more)

### Community 12 - "ContractModel"
Cohesion: 0.24
Nodes (10): AuditRepository, Connection, UUID, 首位管理员初始化必须在单一数据库事务内完成。, AuthResult, AuditEventReference, IdentityAuditEventCode, ResourceReference (+2 more)

### Community 13 - "Child Manager 项目上下文"
Cohesion: 0.06
Nodes (31): 10. 当前共同下一步, 11.1 文档职责与工具基线, 11. 高风险点, 12. 系统架构基线, 13. 验证基线, 14. CONTEXT 更新规则, 1. 本文档的用途, 2. 固定阅读顺序 (+23 more)

### Community 14 - "proxy_request"
Cohesion: 0.07
Nodes (43): BffResponse, proxy_request(), NiceGUI 服务端 BFF 客户端的公开接缝。, 按固定 allowlist 转发请求，并保留响应原始多值头。, NiceGUI 页面与同源 API BFF 装配。, register_web(), navigation_for_capabilities(), 按 API capabilities 生成导航。 (+35 more)

### Community 15 - "Functional Requirements"
Cohesion: 0.07
Nodes (29): AI 模型与提示词, Assumptions, Clarifications, Dependencies, Edge Cases, Feature Specification: 首期一日活动计划完整闭环, Functional Requirements, Key Entities (+21 more)

### Community 16 - "test_foundation.py"
Cohesion: 0.17
Nodes (13): admin_session(), current_session(), identity_service(), CurrentSessionDependency, IdentityServiceDependency, Cookie, Exception, IdentityError (+5 more)

### Community 18 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 19 - "SKILL.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 20 - "Child Manager 幼儿园教育管理系统"
Cohesion: 0.09
Nodes (23): AI 提示词管理子系统, AI 生成规则, Child Manager 幼儿园教育管理系统, Word 导出, 一键生成与分栏目生成, 分支协作规范, 后续子系统, 基本规则 (+15 more)

### Community 21 - "ADR-0001：只交付 Cloud 版本，首期单园运行并保留园所隔离边界"
Cohesion: 0.10
Nodes (21): 1. 产品只交付 Cloud 版本, 2. 首期一个运行实例只服务一所幼儿园, 3. 从首期保留园所隔离边界, 4. Cloud 不等于公网开放, 5. 生产数据语义统一采用 PostgreSQL, ADR-0001：只交付 Cloud 版本，首期单园运行并保留园所隔离边界, Cloud 版本必须直接开放公网, 代价与风险 (+13 more)

### Community 22 - "ADR-0007：采用 Caddy、Docker Compose 与文件挂载 Secrets"
Cohesion: 0.10
Nodes (21): 备选方案, 背景, 首期接入云厂商密钥管理服务, 后果, 决策, ADR-0007：采用 Caddy、Docker Compose 与文件挂载 Secrets, 将所有 Secrets 放入 .env, 实施约束 (+13 more)

### Community 23 - "5. 端点目录"
Cohesion: 0.10
Nodes (21): 1. 边界与可信上下文, 2. Cookie、令牌与 CSRF, 3.1 Request ID, 3.2 分页, 3.3 统一错误, 3.4 乐观锁, 3.5 Idempotency-Key, 3. 通用请求与响应 (+13 more)

### Community 24 - "Child Manager 双 Agent 独立开发协议"
Cohesion: 0.10
Nodes (20): 10. 禁止事项, 11. 启动前检查清单, 1. 文档目的, 2. 事实来源与优先级, 3. 分支模型与所有权, 4.1 共享父 Issue, 4.2 实现子 Issue, 4.3 纵向拆分 (+12 more)

### Community 25 - "M1 工程骨架与质量基线 Issue 草稿与执行记录"
Cohesion: 0.18
Nodes (11): 0. 草稿基线与 graphify 处置记录, 2. Codex 实现子 Issue 草稿, 4. 草稿只读复核清单, M1 工程骨架与质量基线 Issue 草稿与执行记录, T004～T020 有序执行清单, 关联与边界, 实施原则, 标题 (+3 more)

### Community 26 - "test_local_development_profiles.py"
Cohesion: 0.14
Nodes (14): _compose_config(), Any, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_test_database_url_requires_an_explicit_profile(), block_external_network(), isolated_database_url() (+6 more)

### Community 27 - "6. 浏览器验收路径"
Cohesion: 0.11
Nodes (18): 1. 前提与反目标, 2. 锁定安装与本地依赖, 3. 数据库与首次初始化, 4. 启动三个独立进程, 5. 自动化质量门禁, 6.1 初始化、登录与会话, 6.2 必要设置与权限, 6.3 纯手工教案 (+10 more)

### Community 28 - "common.sh"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 29 - "Execution Steps"
Cohesion: 0.12
Nodes (15): 1. Initialize Convergence Context, 2. Load Artifacts (Progressive Disclosure), 3. Build the Intent Inventory, 4. Assess the Codebase and Classify Findings, 5. Assign Severity, 6. Present the In-Session Findings Summary, 7. Append Convergence Tasks (or report converged), 8. Provide Next Actions (Handoff) (+7 more)

### Community 30 - "Implementation Plan: 首期一日活动计划完整闭环"
Cohesion: 0.12
Nodes (16): API 与任务契约, Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: 首期一日活动计划完整闭环, Milestone Gates, Phase 0: Research, Phase 1: Design & Contracts (+8 more)

### Community 31 - "Child Manager 一日活动计划 OpenAPI 3.1"
Cohesion: 0.13
Nodes (15): Audit API, 脱敏审计 Schema, Auth API, 不可变导出输入与文件 Schema, Exports API, Health API, Job 与 batch 投影 Schema, Jobs API (+7 more)

### Community 32 - "ADR-0003：PostgreSQL 保存任务权威状态，Dramatiq 与 Redis 负责异步执行"
Cohesion: 0.14
Nodes (13): ADR-0003：PostgreSQL 保存任务权威状态，Dramatiq 与 Redis 负责异步执行, API 同步执行 AI 和 Word, Celery + Redis, PostgreSQL 直接充当轮询任务队列, Redis 作为任务最终状态存储, 决策, 后果, 备选方案 (+5 more)

### Community 33 - "Child Manager 数据模型设计"
Cohesion: 0.14
Nodes (14): 10. JSONB Schema 演进, 12.1 `daily_activity_plan_exports`, 12. Word 导出模型, 13.1 `workday_cache`, 13. 工作日缓存, 14.1 `audit_events`, 14. 审计模型, 17. 索引原则 (+6 more)

### Community 34 - "ADR-0005：AI 供应商中立，并建立管理员专用提示词系统"
Cohesion: 0.15
Nodes (12): ADR-0005：AI 供应商中立，并建立管理员专用提示词系统, AI 直接写入教案当前内容, 允许提示词定义输出 Schema, 决策, 只配置一个全局模型, 后果, 备选方案, 复审触发条件 (+4 more)

### Community 35 - "Child Manager 系统架构设计"
Cohesion: 0.15
Nodes (13): 12. 节假日与日期服务, 14. 可观测性与审计, 16. 性能与扩展, 17. 故障与降级, 18. 测试与架构验证, 19. 关键架构决策摘要, 1. 文档目的, 20. 实施顺序 (+5 more)

### Community 36 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 37 - "ADR-0006：一日活动计划采用固定 Word 模板导出边界"
Cohesion: 0.17
Nodes (11): ADR-0006：一日活动计划采用固定 Word 模板导出边界, UI 直接修改模板并下载, 从零生成 Word 排版, 决策, 只向浏览器返回临时文件, 后果, 备选方案, 复审触发条件 (+3 more)

### Community 38 - "ADR-0008：日期与外部服务采用本地优先和软降级"
Cohesion: 0.17
Nodes (11): ADR-0008：日期与外部服务采用本地优先和软降级, 决策, 后果, 在线节假日 API 优先, 备选方案, 复审触发条件, 外部服务失败时默认普通工作日, 实施约束 (+3 more)

### Community 39 - "Child Manager 双实现本地开发环境"
Cohesion: 0.17
Nodes (12): 1. 文档目的, 2. 事实来源与边界, 3. 工作树隔离, 4.1 Codex 档位, 4.2 Trae 档位, 4. 固定本地档位, 5. Compose、数据与文件隔离, 6. 技术栈与中国大陆网络边界 (+4 more)

### Community 40 - "Core Principles"
Cohesion: 0.17
Nodes (11): Child Manager 项目宪章, Core Principles, Governance, I. 事实来源与范围忠实, II. 服务边界与单向依赖, III. 园所隔离与服务端授权（NON-NEGOTIABLE）, IV. 权威状态、事务与可恢复性, V. 教师控制、AI 与 Word 保真 (+3 more)

### Community 41 - "后台任务状态机与 AI 采用契约"
Cohesion: 0.19
Nodes (8): IdentityRepository, Connection, datetime, UUID, 所有查询都显式绑定 kindergarten_id 的身份 Repository。, RefreshRecord, _user(), UserRecord

### Community 42 - "SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, Key rules, Mandatory Post-Execution Hooks, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases (+2 more)

### Community 43 - "SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, For AI Generation, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, Quick Guidelines, Section Requirements (+2 more)

### Community 44 - "SKILL.md"
Cohesion: 0.18
Nodes (10): Checklist Format (REQUIRED), Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Phase Structure, Pre-Execution Checks, Task Generation Rules (+2 more)

### Community 45 - "ADR-0002：采用独立 Web、API、Worker 运行单元的模块化单体"
Cohesion: 0.07
Nodes (64): AdminSessionDependency, _allowed_origins(), change_password(), _clear_auth_cookies(), _cookie_secure(), csrf(), login(), logout() (+56 more)

### Community 46 - "ADR-0004：采用同源入口、HttpOnly Cookie 与 API 统一授权"
Cohesion: 0.18
Nodes (11): ADR-0004：采用同源入口、HttpOnly Cookie 与 API 统一授权, Web 自行维护独立权限系统, 决策, 后果, 备选方案, 复审触发条件, 实施约束, 浏览器使用 localStorage 保存 Bearer Token (+3 more)

### Community 47 - "Child Manager PostgreSQL 数据库 Schema"
Cohesion: 0.18
Nodes (11): 11.1 `daily_activity_plan_exports`, 11. Word 导出 Schema, 13. 组合外键矩阵, 14. 应用事务不变量, 15. Alembic 迁移顺序, 16. PostgreSQL 与 SQLite 验证矩阵, 17. 必须实现的 Schema 验收测试, 18. 实现时禁止的捷径 (+3 more)

### Community 48 - "教案管理 PRD（首期：一日活动计划）"
Cohesion: 0.18
Nodes (11): 16. 异常与降级, 19. 风险与缓解, 1. 文档目的, 20. 实施依赖, 21. 架构设计引用, 2. 事实来源, 3. 产品背景, 6.1 包含范围 (+3 more)

### Community 49 - "Core Principles"
Cohesion: 0.18
Nodes (10): Core Principles, Governance, [PRINCIPLE_1_NAME], [PRINCIPLE_2_NAME], [PRINCIPLE_3_NAME], [PRINCIPLE_4_NAME], [PRINCIPLE_5_NAME], [PROJECT_NAME] Constitution (+2 more)

### Community 50 - "transactional_session"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 51 - "Child Manager 文档交叉审计合并结论"
Cohesion: 0.20
Nodes (10): 1. 合并范围与事实来源, 2. 状态与操作类别, 5. M0 阻断项, 6. 建议执行顺序, 7. 验证要求, 8.1 已完成的检查面, 8.2 敏感信息处理边界, 8.3 操作与交付边界 (+2 more)

### Community 52 - "右侧列"
Cohesion: 0.20
Nodes (10): 右侧列, 填写说明, 左侧列, 第一行, 第三行：, 第二行：, 第五行：, 第六行： (+2 more)

### Community 53 - "这是一份word表格"
Cohesion: 0.20
Nodes (10): 填写说明, 填写说明：, 填写说明：, 填写说明：, 文件第一行, 文件第二行, 注意事项：, 表格第一行 (+2 more)

### Community 54 - "18. 验收标准"
Cohesion: 0.22
Nodes (9): 18.1 账号与权限, 18.2 设置, 18.3 教案管理, 18.4 日期规则, 18.5 提示词与 AI, 18.6 集体活动, 18.7 Word 导出, 18.8 运维与安全 (+1 more)

### Community 55 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 56 - "SKILL.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 57 - "SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 58 - "SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 59 - "3. 总体建模原则"
Cohesion: 0.29
Nodes (7): 3.1 PostgreSQL 是生产事实来源, 3.2 UUIDv7 主键, 3.3 园所隔离, 3.4 时间与日期, 3.5 字符串、枚举和规范化, 3.6 停用、归档与不可变历史, 3. 总体建模原则

### Community 60 - "9. 一日活动计划模型"
Cohesion: 0.29
Nodes (7): 9.1 关系表头与 JSONB 正文, 9.2 `daily_activity_plans`, 9.3 `content` 结构边界, 9.4 `daily_activity_plan_authors`, 9.5 `daily_activity_plan_snapshots`, 9.6 `lesson_plan_sources`, 9. 一日活动计划模型

### Community 61 - "3. 二十六项问题的最终结论"
Cohesion: 0.29
Nodes (7): 3.1 文档命名与 ADR 状态, 3.5 API、任务状态与幂等, 3. 二十六项问题的最终结论, Q12：任务状态机缺少 `expired`, Q13：幂等键定义, Q1：ADR-0001 文件命名, Q2：ADR-0007 被 ADR-0009 取代的标记

### Community 62 - "3.9 Codex 交叉审计事项"
Cohesion: 0.29
Nodes (7): 3.9 Codex 交叉审计事项, Q21：Word 模板真实个人信息, Q22：canonical 数据模型与 Spec Kit 漂移, Q23：生产备份和部署, Q24：对象存储接口预建, Q25：M0 与实现分支启动, Q26：首期时区权限

### Community 63 - "10. 教案栏目与格式"
Cohesion: 0.29
Nodes (7): 10.1 晨间活动, 10.2 晨间谈话, 10.3 集体活动, 10.4 室内区域游戏, 10.5 下午户外游戏, 10.6 一日活动反思, 10. 教案栏目与格式

### Community 64 - "13. AI 生成流程"
Cohesion: 0.29
Nodes (7): 13.1 一键生成, 13.2 分栏目生成, 13.3 集体活动, 13.4 输入上下文, 13.5 异步状态, 13.6 重试策略, 13. AI 生成流程

### Community 65 - "右侧列"
Cohesion: 0.29
Nodes (7): 一日活动反思填写说明, 右侧列, 左侧列, 第一行, 第三行, 第二行, 表格第八行

### Community 66 - "右侧列"
Cohesion: 0.29
Nodes (7): 右侧列, 填写说明, 左侧列, 第一行, 第三行, 第二行, 表格第六行

### Community 67 - "右侧列"
Cohesion: 0.29
Nodes (7): 右侧列, 填写说明, 左侧列, 第一行, 第三行, 第二行, 表格第七行

### Community 68 - "右侧列为两行："
Cohesion: 0.29
Nodes (7): 右侧列为两行：, 填写说明, 填写说明：, 左侧列, 第一行：, 第二行：, 表格第三大行

### Community 69 - "右侧列为两行："
Cohesion: 0.29
Nodes (7): 右侧列为两行：, 填写说明：, 填写说明：, 左侧列, 第一行：, 第二行：, 表格第四行：

### Community 70 - "test_openapi_document.py"
Cohesion: 0.43
Nodes (6): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_document_is_valid_31(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 71 - "完整 SDD 工作流"
Cohesion: 0.33
Nodes (6): Spec Kit 任务实施, Spec Kit 实施规划, Spec Kit 功能规格生成, Spec Kit 任务生成, 规格与计划评审门禁, 完整 SDD 工作流

### Community 72 - "env.py"
Cohesion: 0.24
Nodes (9): DeclarativeBase, AuditEvent, Base, Kindergarten, 园所、账号、角色与 Refresh token ORM 模型。, RefreshToken, Role, User (+1 more)

### Community 73 - "5. 园所与身份模型"
Cohesion: 0.33
Nodes (6): 5.1 `kindergartens`, 5.2 `users`, 5.3 `roles`, 5.4 `user_roles`, 5.5 `refresh_tokens`, 5. 园所与身份模型

### Community 74 - "6. 教学设置模型"
Cohesion: 0.33
Nodes (6): 6.1 `age_groups`, 6.2 `classes`, 6.3 `class_teachers`, 6.4 `semesters`, 6.5 `class_areas`, 6. 教学设置模型

### Community 75 - "3. PostgreSQL 物理约定"
Cohesion: 0.33
Nodes (6): 3.1 Schema、扩展与命名, 3.2 通用类型与默认值, 3.3 园所隔离与组合外键, 3.4 规范化列与状态代码, 3.5 不可变与不使用触发器, 3. PostgreSQL 物理约定

### Community 76 - "5. 园所与身份 Schema"
Cohesion: 0.33
Nodes (6): 5.1 `kindergartens`, 5.2 `users`, 5.3 `roles`, 5.4 `user_roles`, 5.5 `refresh_tokens`, 5. 园所与身份 Schema

### Community 77 - "6. 教学设置 Schema"
Cohesion: 0.33
Nodes (6): 6.1 `age_groups`, 6.2 `classes`, 6.3 `class_teachers`, 6.4 `semesters`, 6.5 `class_areas`, 6. 教学设置 Schema

### Community 78 - "9. 一日活动计划 Schema"
Cohesion: 0.33
Nodes (6): 9.1 `daily_activity_plans`, 9.2 `daily_activity_plan_authors`, 9.3 `daily_activity_plan_snapshots`, 9.4 `lesson_plan_sources`, 9.5 `content` JSONB 物理边界, 9. 一日活动计划 Schema

### Community 79 - "9. 后台任务架构"
Cohesion: 0.33
Nodes (6): 9.1 选型与用途, 9.2 状态机, 9.3 投递、幂等与恢复, 9.4 AI 重试与反馈, 9.5 状态获取, 9. 后台任务架构

### Community 80 - "12. AI 模型与提示词管理"
Cohesion: 0.33
Nodes (6): 12.1 七个任务级提示词, 12.2 系统默认提示词, 12.3 自定义提示词生命周期, 12.4 变量白名单, 12.5 提示词测试运行, 12. AI 模型与提示词管理

### Community 81 - "7. 首期必要设置"
Cohesion: 0.33
Nodes (6): 7.1 幼儿园信息, 7.2 学期管理, 7.3 班级与教师, 7.4 班级区域, 7.5 AI 模型档案, 7. 首期必要设置

### Community 82 - "9. 日期与上下文规则"
Cohesion: 0.33
Nodes (6): 9.1 活动日期, 9.2 学期与周次, 9.3 星期与日期格式, 9.4 季节, 9.5 工作日, 9. 日期与上下文规则

### Community 83 - "SKILL.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 84 - "SKILL.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 85 - "21. 测试与验收"
Cohesion: 0.40
Nodes (5): 21.1 单元测试, 21.2 Repository 与 PostgreSQL 集成测试, 21.3 迁移测试, 21.4 安全测试, 21. 测试与验收

### Community 86 - "5. 代码组织与依赖方向"
Cohesion: 0.40
Nodes (5): 5.1 建议目录, 5.2 后端模块内部方向, 5.3 模块边界, 5.4 深模块接口, 5. 代码组织与依赖方向

### Community 87 - "8. 数据架构"
Cohesion: 0.40
Nodes (5): 8.1 数据所有权, 8.2 一致性边界, 8.3 事务所有权, 8.4 SQLite 使用边界, 8. 数据架构

### Community 88 - "3.2 模板说明与业务规则"
Cohesion: 0.40
Nodes (5): 3.2 模板说明与业务规则, Q3：集体活动新增环节标记, Q4：反思结构与长度, Q5：自然周起始日, Q6：学期首周边界

### Community 89 - "4. 项目文档更新矩阵"
Cohesion: 0.40
Nodes (5): 4.1 必须更新的事实来源, 4.2 Spec Kit 与契约同步, 4.3 只需核验或增加导航的事项, 4.4 FAQ 整理, 4. 项目文档更新矩阵

### Community 90 - "11. 计划管理流程"
Cohesion: 0.40
Nodes (5): 11.1 首页与查询, 11.2 创建或打开计划, 11.3 保存, 11.4 归档, 11. 计划管理流程

### Community 91 - "14. Word 导出"
Cohesion: 0.40
Nodes (5): 14.1 导出前检查, 14.2 模板规则, 14.3 文件名与存储, 14.4 导出历史, 14. Word 导出

### Community 92 - "17. 非功能要求"
Cohesion: 0.40
Nodes (5): 17.1 容量与性能, 17.2 生产可用性与恢复（延后验收）, 17.3 兼容性, 17.4 可测试性, 17. 非功能要求

### Community 93 - "Q: 请阅读以上内容和现有的AGENTS.MD,还有ywyz/kindergartenManager.git的AGENTS.MD，你认为i还需要再加入点什么？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请阅读以上内容和现有的AGENTS.MD,还有ywyz/kindergartenManager.git的AGENTS.MD，你认为i还需要再加入点什么？, Source Nodes

### Community 94 - "Q: 请阅读以上内容和现有的README.md,AGENTS.md,还有ywyz/kindergartenManager.git的文档，你认为CONTEXT.md需要再加入点什么？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请阅读以上内容和现有的README.md,AGENTS.md,还有ywyz/kindergartenManager.git的文档，你认为CONTEXT.md需要再加入点什么？, Source Nodes

### Community 95 - "Q: 请根据现有文档，和旧仓库的文件思考如何撰写 docs/PRD/lesson-management.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请根据现有文档，和旧仓库的文件思考如何撰写 docs/PRD/lesson-management.md, Source Nodes

### Community 96 - "Q: 接下来需要生成什么文件呢"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 接下来需要生成什么文件呢, Source Nodes

### Community 97 - "Q: 系统架构文档应如何定义目标服务架构、服务边界、共享契约、部署拓扑与首期实施顺序？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 系统架构文档应如何定义目标服务架构、服务边界、共享契约、部署拓扑与首期实施顺序？, Source Nodes

### Community 98 - "Q: 哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？, Source Nodes

### Community 99 - "Q: 一日活动计划系统的数据实体、关系、唯一约束、历史版本、异步任务和安全边界是什么？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 一日活动计划系统的数据实体、关系、唯一约束、历史版本、异步任务和安全边界是什么？, Source Nodes

### Community 100 - "Q: 请使用/graphify update. 进行更新，同时使用子代理进行语义更新，然后思考还需要完成什么任务"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请使用/graphify update. 进行更新，同时使用子代理进行语义更新，然后思考还需要完成什么任务, Source Nodes

### Community 102 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 103 - "15. 数据快照边界"
Cohesion: 0.50
Nodes (4): 15.1 教案展示快照, 15.2 AI 输入快照, 15.3 快照不是重复日志, 15. 数据快照边界

### Community 104 - "22. 后续扩展边界"
Cohesion: 0.50
Nodes (4): 22.1 年级组长和园级检查, 22.2 照片与视觉子系统, 22.3 多园 SaaS, 22. 后续扩展边界

### Community 105 - "2. 设计来源与旧系统取舍"
Cohesion: 0.50
Nodes (4): 2.1 事实来源, 2.2 从旧系统吸收的经验, 2.3 明确不继承的旧模型, 2. 设计来源与旧系统取舍

### Community 106 - "8. 提示词模型"
Cohesion: 0.50
Nodes (4): 8.1 `prompt_definitions`, 8.2 `prompt_versions`, 8.3 `prompt_test_runs`, 8. 提示词模型

### Community 107 - "8. 提示词 Schema"
Cohesion: 0.50
Nodes (4): 8.1 `prompt_definitions`, 8.2 `prompt_versions`, 8.3 `prompt_test_runs`, 8. 提示词 Schema

### Community 108 - "10. AI 与提示词架构"
Cohesion: 0.50
Nodes (4): 10.1 AI 适配器, 10.2 提示词服务, 10.3 结果采用边界, 10. AI 与提示词架构

### Community 109 - "6. 请求、认证与授权"
Cohesion: 0.50
Nodes (4): 6.1 同源访问, 6.2 会话链路, 6.3 园所与班级隔离, 6. 请求、认证与授权

### Community 110 - "3.3 数据模型、保留与任务关系"
Cohesion: 0.50
Nodes (4): 3.3 数据模型、保留与任务关系, Q7：历史恢复快照原因, Q8：AI 结果清理与一年审计, Q9：后台任务父子与重试外键

### Community 111 - "3.7 API 与页面信息架构"
Cohesion: 0.50
Nodes (4): 3.7 API 与页面信息架构, Q16：API 端点文档, Q17：前端页面信息架构, Q18：前端 `kindergarten_id`

### Community 112 - "5. 用户与权限"
Cohesion: 0.50
Nodes (4): 5.1 角色, 5.2 账号规则, 5.3 教师与班级, 5. 用户与权限

### Community 113 - "8. 核心业务对象"
Cohesion: 0.50
Nodes (4): 8.1 一日活动计划, 8.2 历史快照, 8.3 导出记录, 8. 核心业务对象

### Community 114 - "Child Manager OpenAPI v1"
Cohesion: 0.50
Nodes (4): 认证与用户 API, Child Manager OpenAPI v1, 教案任务与导出 API, 设置与提示词 API

### Community 119 - "11. 后台任务与 AI 结果"
Cohesion: 0.67
Nodes (3): 11.1 `background_jobs`, 11.2 `ai_generation_results`, 11. 后台任务与 AI 结果

### Community 120 - "16. 外键与删除行为"
Cohesion: 0.67
Nodes (3): 16.1 数据库删除规则, 16.2 跨行事务不变量, 16. 外键与删除行为

### Community 121 - "4. 模型总览"
Cohesion: 0.67
Nodes (3): 4.1 首期表清单, 4.2 核心关系图, 4. 模型总览

### Community 122 - "7. AI 模型档案"
Cohesion: 0.67
Nodes (3): 7.1 `ai_model_profiles`, 7.2 `ai_model_profile_capabilities`, 7. AI 模型档案

### Community 123 - "10. 后台任务与 AI 结果 Schema"
Cohesion: 0.67
Nodes (3): 10.1 `background_jobs`, 10.2 `ai_generation_results`, 10. 后台任务与 AI 结果 Schema

### Community 124 - "12. 系统支撑 Schema"
Cohesion: 0.67
Nodes (3): 12.1 `workday_cache`, 12.2 `audit_events`, 12. 系统支撑 Schema

### Community 125 - "2. 事实来源与旧仓库取舍"
Cohesion: 0.67
Nodes (3): 2.1 事实来源, 2.2 旧仓库经验, 2. 事实来源与旧仓库取舍

### Community 126 - "7. AI 模型档案 Schema"
Cohesion: 0.67
Nodes (3): 7.1 `ai_model_profiles`, 7.2 `ai_model_profile_capabilities`, 7. AI 模型档案 Schema

### Community 127 - "11. Word 与文件架构"
Cohesion: 0.67
Nodes (3): 11.1 导出流程, 11.2 上传 `.docx`, 11. Word 与文件架构

### Community 128 - "13. 配置、密钥与安全"
Cohesion: 0.67
Nodes (3): 13.1 配置分级, 13.2 安全边界, 13. 配置、密钥与安全

### Community 129 - "15. 生产部署延后边界"
Cohesion: 0.67
Nodes (3): 15.1 当前阶段, 15.2 功能完成后的复审, 15. 生产部署延后边界

### Community 130 - "4. 架构总览"
Cohesion: 0.67
Nodes (3): 4.1 逻辑视图, 4.2 运行单元, 4. 架构总览

### Community 131 - "7. API 与契约"
Cohesion: 0.67
Nodes (3): 7.1 API 原则, 7.2 跨进程任务契约, 7. API 与契约

### Community 132 - "3.5 API、任务状态与幂等"
Cohesion: 0.09
Nodes (36): MemoryLoginThrottle, datetime, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision, Redis, csrf_headers(), identity_client() (+28 more)

### Community 133 - "3.6 测试与可访问性"
Cohesion: 0.67
Nodes (3): 3.6 测试与可访问性, Q14：并发、故障和恢复测试, Q15：WCAG 覆盖范围

### Community 134 - "3.8 编辑与 AI 采用"
Cohesion: 0.67
Nodes (3): 3.8 编辑与 AI 采用, Q19：新增集体活动环节的插入位置, Q20：自动保存失败

### Community 135 - "15. 安全、隐私与审计"
Cohesion: 0.67
Nodes (3): 15.1 敏感数据, 15.2 审计事件, 15. 安全、隐私与审计

### Community 136 - "4. 产品目标"
Cohesion: 0.67
Nodes (3): 4.1 首期目标, 4.2 成功标准, 4. 产品目标

### Community 719 - "正文"
Cohesion: 0.07
Nodes (30): 0. 草稿事实与授权边界, 1. 共享父 Issue 草稿, 2. Codex 实现子 Issue 草稿, 3. Trae 实现子 Issue 草稿, 4. 草稿只读复核清单, M2 认证、授权与身份审计 Issue 草稿与执行记录, T021～T035 有序执行清单, T021～T035 有序执行清单 (+22 more)

### Community 720 - "MemoryLoginThrottle"
Cohesion: 0.29
Nodes (12): _native_url(), 身份用例：实时授权、会话轮换、撤销与最后管理员保护。, create_access_token(), decode_access_token(), generate_refresh_token(), hash_refresh_token(), Any, datetime (+4 more)

### Community 721 - "ports.py"
Cohesion: 0.16
Nodes (11): _calendar_library_available(), AiClient, Clock, DependencyCheck, JobBroker, date, datetime, UUID (+3 more)

### Community 722 - "build_health_dependencies"
Cohesion: 0.23
Nodes (10): initialize_admin(), _native_url(), 返回 True 表示创建成功，False 表示系统已经初始化。, _init_admin(), main(), normalize_phone(), normalize_username(), test_invalid_phone_is_rejected() (+2 more)

### Community 723 - "Python 质量门禁 Job"
Cohesion: 0.25
Nodes (11): 1. 共享父 Issue 草稿, 标题, uv 锁定安装门禁, OpenAPI 规格校验门禁, Pyright 类型门禁, Pytest 测试门禁, Python 3.14 运行时, Python 质量门禁 Job (+3 more)

### Community 724 - "middleware.py"
Cohesion: 0.25
Nodes (10): hash_password(), password_violations(), Path, verify_password(), _weak_passwords(), Path, test_password_is_argon2id_hashed_and_verified(), test_password_length_is_15_to_128_unicode_characters() (+2 more)

### Community 725 - "正文"
Cohesion: 0.20
Nodes (10): 任务映射, 入口条件, 共享事实来源, 共同出口门禁, 共同目标, 协作边界, 实现子 Issue, 当前状态与基线 (+2 more)

### Community 726 - "正文"
Cohesion: 0.25
Nodes (8): 3. Trae 实现子 Issue 草稿, T004～T020 有序执行清单, 关联与边界, 实施原则, 标题, 正文, 非目标, 验收证据

### Community 727 - "app.py"
Cohesion: 0.18
Nodes (11): ADR-0002：采用独立 Web、API、Worker 运行单元的模块化单体, NiceGUI 一体化进程, React/TypeScript 独立前端, 从首期开始全面微服务化, 决策, 前端直接访问数据库或共享 Repository, 后果, 备选方案 (+3 more)

### Community 728 - "CI PostgreSQL 服务"
Cohesion: 0.29
Nodes (7): PostgreSQL 18 Alpine 固定 Digest, PostgreSQL 镜像覆盖变量, 每次运行动态 CI 数据库密码, PostgreSQL 18 Alpine 固定 Digest, PostgreSQL 健康门禁, CI PostgreSQL 服务, 隔离 PostgreSQL 测试 URL

### Community 729 - "0001_identity_and_audit.py"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 730 - "test_0001_identity.py"
Cohesion: 0.47
Nodes (5): migrated_database(), Connection, MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent()

### Community 731 - "_run_cli"
Cohesion: 0.50
Nodes (4): CompletedProcess, MonkeyPatch, _run_cli(), test_init_admin_is_single_transaction_non_echoing_and_idempotent()

### Community 732 - "GitHub Actions 质量工作流"
Cohesion: 0.50
Nodes (4): 只读仓库内容权限, Pull Request 触发器, main、codex、trae 推送触发器, GitHub Actions 质量工作流

### Community 733 - "3.4 加密与密钥"
Cohesion: 0.67
Nodes (3): 3.4 加密与密钥, Q10：AI Key 加密算法, Q11：主加密密钥来源

### Community 744 - "test_identity_isolation.py"
Cohesion: 0.47
Nodes (10): identity_database(), _insert_kindergarten(), _insert_user(), Connection, MonkeyPatch, UUID, test_cross_kindergarten_role_assignment_is_rejected_by_composite_foreign_key(), test_refresh_replacement_cannot_cross_kindergarten() (+2 more)

## Knowledge Gaps
- **1432 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+1427 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **571 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.835731442)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `教案管理 PRD（首期：一日活动计划）` connect `教案管理 PRD（首期：一日活动计划）` to `13. AI 生成流程`, `15. 安全、隐私与审计`, `4. 产品目标`, `README.md`, `12. AI 模型与提示词管理`, `5. 用户与权限`, `7. 首期必要设置`, `8. 核心业务对象`, `9. 日期与上下文规则`, `18. 验收标准`, `11. 计划管理流程`, `14. Word 导出`, `17. 非功能要求`, `10. 教案栏目与格式`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `M1 工程骨架与质量基线 Issue 草稿与执行记录` connect `M1 工程骨架与质量基线 Issue 草稿与执行记录` to `README.md`, `Python 质量门禁 Job`, `正文`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `这是一份word表格` connect `这是一份word表格` to `右侧列`, `右侧列`, `右侧列`, `右侧列为两行：`, `右侧列为两行：`, `README.md`, `右侧列`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `IdentityError` (e.g. with `create_app()` and `HealthDependencies`) actually correct?**
  _`IdentityError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `ContractModel` (e.g. with `AuditEventReference` and `IdentityAuditEventCode`) actually correct?**
  _`ContractModel` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `IdentityService` (e.g. with `HealthDependencies` and `AuditRepository`) actually correct?**
  _`IdentityService` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `create_app()` (e.g. with `RequestContextMiddleware` and `IdentityError`) actually correct?**
  _`create_app()` has 2 INFERRED edges - model-reasoned connections that need verification._