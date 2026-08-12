---
type: "query"
date: "2026-08-11T09:30:43.346504+00:00"
question: "T050-T053 如何验证最小 AgentContext、revision 失效、敏感信息排除和 READ/DRAFT 零写入？"
contributor: "graphify"
outcome: "useful"
source_nodes: ["agent-runtime.md", "ADR-0013-controlled-agent-runtime.md", "RuntimeBridge", "redact_mapping()"]
---

# Q: T050-T053 如何验证最小 AgentContext、revision 失效、敏感信息排除和 READ/DRAFT 零写入？

## Answer

图谱导航定位到 agent-runtime 契约、ADR-0013、RuntimeBridge 与日志脱敏边界。随后直接核对固定 docs SHA，确认 T050-T053 应以最小逐 turn Context、实体 revision、scope/超时失效、秘密与绝对路径排除、READ/DRAFT-only 以及无 Agent 状态持久化为 RED 验收边界；图谱只用于导航，不代替原始文档。

## Outcome

- Signal: useful

## Source Nodes

- agent-runtime.md
- ADR-0013-controlled-agent-runtime.md
- RuntimeBridge
- redact_mapping()