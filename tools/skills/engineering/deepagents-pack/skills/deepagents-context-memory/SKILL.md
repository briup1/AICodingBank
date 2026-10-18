---
name: deepagents-context-memory
description: 设计 DeepAgents 的上下文工程、文件化 offload、skills、短期 checkpoint 与跨线程长期记忆时加载；不处理 sandbox 权限细节或子 Agent 拓扑。
metadata:
  framework: DeepAgents
  framework-version: "0.7.8"
  generated-from: official-sources
---

# DeepAgents 上下文与记忆

## 先区分四类状态

```text
输入上下文：system prompt / 用户消息 / 工具定义 / runtime context
运行状态：当前消息、任务规划、文件工具结果、模型调用过程
线程持久化：checkpointer + thread_id，恢复同一会话
长期记忆：store 或持久化 backend，跨 thread / user / agent scope
```

不要把“写入 `/memories/` 文件”自动等同于长期记忆：它是否跨线程取决于实际 backend 和路由。先确定 scope，再选存储。

## 上下文预算策略

1. system prompt 只保留稳定规则、边界和输出契约；用户/运行时变化放在输入或 runtime context。
2. 大型工具结果和中间产物写入虚拟文件系统，以路径、摘要和下一步读取方式交接；不要把完整内容重复塞进每轮消息。
3. 用 `skills=` 提供按需加载的领域知识；Skill 的 metadata 常驻发现，正文和 resources 在匹配后渐进式读取。
4. 让框架的 summarization/overflow 机制处理长轨迹，但先定义哪些事实必须落盘，避免压缩丢失关键约束。
5. 子 Agent 使用独立上下文窗口，只传递任务契约、必要文件路径和验收标准；不要复制整个主 Agent 历史。

## 记忆选型

| 目标 | 机制 | 验证 |
|---|---|---|
| 同一 thread 的对话恢复 | LangGraph `checkpointer` + 稳定 `thread_id` | 重新 invoke 后能读到该 thread 状态 |
| agent 级长期规则/事实 | agent-scoped store 或 backend | 不同 thread 能读取，其他 agent 不越权 |
| user 级偏好 | user-scoped namespace/store | 同一用户跨 thread 可见，不同用户不可见 |
| 对话/事件总结 | episodic memory + 后台 consolidation | 只写入允许的 scope，失败可重试且不重复污染 |
| 项目领域知识 | `skills=`、references 或检索工具 | 只在相关任务加载，来源可追踪 |

内存可读写范围要显式设计：只读 memory 适合稳定规范；可写 memory 必须有 schema、来源、更新时间、冲突合并、并发写策略和人工删除路径。多个 agent 并发写同一 memory 时，不要假定最后写入就是正确结果。

## 让上下文可恢复

```text
原始输入/工具结果
  → 摘要（保留事实、来源、未决问题）
  → 写入虚拟文件或 store
  → 主上下文只保留索引与下一步
  → 恢复时按路径/namespace 读取
  → 最终回答引用可验证的产物
```

持久化前检查：

- 是否含密钥、个人数据或不应跨线程的数据。
- 文件/namespace 是否属于正确的 user、assistant、thread scope。
- 是否有版本、来源和过期策略。
- 写入是否幂等，重试是否会追加重复事实。
- 是否需要人工审批才能把模型生成内容升级为长期规则。

## Skills 与本项目 Skill Pack

DeepAgents 的 Skill 是通过 `SKILL.md` frontmatter 发现、按需读正文的资源。source 可以是一个路径，也可以是 `(path, label)`；多来源同名 Skill 按来源顺序覆盖，后加载者优先。将本项目生成的 Skill 放在明确的项目级 source 路径，不要把仓库密钥或未审查脚本作为 Skill 资源。

每个 Skill 的 description 应具体说明“做什么 + 何时触发 + 边界”，否则会出现错误匹配和上下文膨胀。长 API、排障和迁移内容放 `references/`，入口只保留决策规则。

## 上下文隔离测试

- 长工具结果：确认模型上下文只收到摘要/路径，文件内容可按需恢复。
- 压缩后：关键事实、拒绝规则、未完成任务和来源仍可恢复。
- thread 隔离：A thread 写入的数据不应出现在 B thread。
- user/agent scope：验证同一 scope 可见、相邻 scope 不可见。
- 并发写：模拟两个 writer，检查冲突、版本或幂等行为。
- Skill 失败：缺失、格式错误、过大或不可读时，agent 应告知可恢复错误，不得静默把错误内容当规则。

实时 API、memory backend 构造参数和版本差异必须加载 `deepagents-docs`；不要凭记忆补全版本敏感字段。
