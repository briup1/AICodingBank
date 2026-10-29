# 验证范围

状态：v3 已修改，待按下述最小复验重新验证。v2 的历史验证仍保留作对照，不代表 v3 已通过。Skill v2 曾在同一模型、同一思考级别 high、两个全新 Herdr/Pi 会话中，以同一 H001 原文作为唯一业务材料完成首次产出。首轮 v1 的两个会话也已保留，作为修订依据；v1 曾出现一个输出过度碎片化和适用条件扩大问题，未标为通过。

## 最小复验

1. 冻结本包内容，记录版本/文件摘要。
2. 两个全新 Agent 会话，只接收本 Skill 路径与同一份 H001 原文路径；运行边界另行指定，不提供 H001 分组答案、历史产物或补充内容指导。
3. 每个会话保存首次完整结果。按 Skill 的七项标准检查，不由负责人修改结果后计通过；修订 Skill 后重测是新一轮。除原有六项外，必须逐个核对每个主要变化包是否显式包含“场景、对象、从、到、结果/边界”，且没有编造未说明的旧状态。
4. 核对实际读取资料和模型/思考级别，记录上下文限制。
5. 实测通过只证明对应输入、模型和宿主范围，不等于跨模型、跨需求和任何 Agent 的确定性保证。

## v2 验证记录

- 输入：`/Users/ziyun/workdir/self_project/AICodingBank/tools/skills/engineering/wl-req-change-tree/SKILL.md` 及其 `references/output-template.md`、`references/examples.md`、`references/validation.md`，原始需求 `/Users/ziyun/workdir/remote_project/ai-agent/版本管理/周迭代/20261008/需求/R-20261008-H001.md`。
- 会话 A：`/Users/ziyun/.pi/agent/sessions/--Users-ziyun-workdir-self_project-AICodingBank--/2026-10-19T12-59-42-392Z_01a1543f-13b7-715c-92d6-8c70beeb64f2.jsonl`；首次结果保存于 `/Users/ziyun/workdir/self_project/AICodingBank/.local/records/wl-req-change-tree/v2-h001/first-output-a.md`。
- 会话 B：`/Users/ziyun/.pi/agent/sessions/--Users-ziyun-workdir-self_project-AICodingBank--/2026-10-19T13-01-57-422Z_01a15441-232e-774a-b8c2-6b20734ed81d.jsonl`；首次结果保存于 `/Users/ziyun/workdir/self_project/AICodingBank/.local/records/wl-req-change-tree/v2-h001/first-output-b.md`。
- 两份结果均停留在理解层，均识别出多入口录入、统一校验、船期补全、直接编辑/草稿批量编辑、筛选查询等核心变化；分组数量不同（4 与 8）但不影响方法目标。
- 两份结果均将未读取的关联需求标为待补读，没有把数据库字段、接口或测试用例当作本次产物。
- 限制：只验证了当前模型和 H001 一个复杂样本；未验证跨模型、跨需求、长上下文截断或宿主不提供 Herdr 时的加载行为。不能据此宣称确定性复现。

## v3 新增验收门槛

- 每个主要变化包是否都有独立的“变化定位”段，而不是只在总变化或后文零散提及。
- “从”和“到”是否是原文有依据的状态；新增能力或旧状态未知时是否明确标为未知，而不是反推旧流程。
- 状态链是否同时保留直接结果、保持不变项、适用范围和禁止副作用；是否避免把变化定位扩写成测试用例。
- 读者只看某个 C 节点，是否能回答“什么场景、哪个对象、从什么状态到什么状态、结果是什么”。

## 观察重点

- 是否直接得到业务变化主树及具体交互/逻辑/数据表现。
- 是否需要负责人临场补充提示或润色。
- 是否编造旧行为，是否为填表进入实现设计或完整验收。
- 是否大量重复原文，是否缺失会改变结果的关键规则。

结果及可复核证据在实际执行后更新。
