---
name: deepagents-getting-started
description: 为首次采用 DeepAgents 或设计其总体架构的任务提供 0.7.8 的最小闭环、分层关系和选型约束；不处理具体后端安全策略、子 Agent 拆分或版本敏感 API 查询。
metadata:
  framework: DeepAgents
  framework-version: "0.7.8"
  generated-from: official-sources
---

# DeepAgents 入门架构

## 何时加载

- 用户要从零创建 DeepAgents agent、选择 `create_deep_agent` 参数或解释其架构。
- 用户需要判断何时使用内置 filesystem、规划、子 Agent、技能、记忆和 LangGraph 持久化。

不要因为“使用 LangChain”就加载本 Skill；已有 DeepAgents 代码的后端、记忆、子 Agent 或实时 API 问题应路由到对应专项 Skill。

## 定位与边界

DeepAgents 是构建在 LangChain agent 与 LangGraph runtime 之上的 agent harness，负责把工具调用、虚拟文件系统、上下文管理、任务规划、子 Agent 委派和长期记忆组合成可编排的运行图。它不替代模型供应商、外部 sandbox、数据库、权限系统或文档检索服务。

核心关系：

```text
create_deep_agent(...)
        ↓ 组装并编译
DeepAgents middleware stack
        ├─ filesystem tools + execute（由 backend 决定能力）
        ├─ 任务规划
        ├─ skills / memory（按参数启用）
        ├─ subagent task（按 subagents 启用）
        └─ human-in-the-loop / custom middleware
        ↓
LangGraph runnable
        ├─ checkpointer：线程内状态恢复
        └─ store：跨线程长期存储
```

## 最小闭环

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",  # 使用 provider:model；也可传已初始化的 BaseChatModel
    tools=[my_tool],
    system_prompt="你是一个遵守项目边界的助手。",
)
result = agent.invoke({"messages": [{"role": "user", "content": request}]})
```

执行前确认三件事：

1. 模型标识与供应商集成已安装、凭证由运行环境提供；不要把密钥写入 Skill、代码或提示词。
2. 只把业务工具放入 `tools`；它们会与内置 filesystem、`execute`、`task` 工具合并，不会自动删除内置工具。
3. 若需要跨调用恢复，显式配置 LangGraph `checkpointer`；若需要跨线程持久化，使用 `store` 或持久化 backend，不能把线程内 state 当长期记忆。

## 关键选型

| 需求 | 优先选择 | 不要误用 |
|---|---|---|
| 单线程、短任务、快速原型 | 默认 `StateBackend` + `agent.invoke` | 直接给宿主机目录写权限 |
| 需要跨线程共享文件或记忆 | `StoreBackend`、`ContextHubBackend` 或路由后的持久化 backend | 只配置 checkpointer |
| 需要安全执行代码 | 实现 `SandboxBackendProtocol` 的 sandbox | 把 `LocalShellBackend` 当隔离环境 |
| 需要可审查的高风险动作 | `interrupt_on` / permissions + 人工审批 | 只在 system prompt 中要求“先确认” |
| 需要专家并行处理 | `subagents=` 或动态 `task` | 让主 Agent 把全部上下文复制给每个专家 |
| 需要按需装载领域规则 | `skills=` | 把所有规则常驻 system prompt |

## 稳定不变量

- `create_deep_agent` 返回可调用的 LangGraph runnable；实际执行语义受 backend、checkpointer、store、middleware 和模型适配器共同决定。
- `model=None` 在 0.7.8 仍是兼容路径但已被官方标记为弃用；新代码显式传模型，避免 1.0 移除默认模型后失效。
- `tools` 是增量注册；要移除内置工具必须使用官方 profile/排除机制，而不是传空列表。
- 线程隔离、跨线程持久化和宿主机访问是三个不同边界，设计文档和测试必须分别说明。
- 任何可写文件系统、shell、外部网络和跨线程 store 都应视为能力边界，必须配合权限、隔离和最小权限验证。

## 推荐工作流

```text
确认用户目标与数据边界
  → 选择模型与 LangGraph 持久化层
  → 选择 backend / sandbox / permissions
  → 只注册必要工具
  → 决定是否启用 skills、memory、subagents
  → 用最小输入运行 invoke/stream
  → 用拒绝路径、线程隔离和恢复测试验证
```

## 验证清单

- [ ] `import deepagents` 与 `create_deep_agent` 可导入。
- [ ] 最小 agent 能在无真实外部写操作的 mock 工具上完成一次 `invoke`。
- [ ] 配置 checkpointer 后，第二次调用使用同一 `thread_id` 能恢复预期线程状态；不同 thread 不互相读取。
- [ ] 需要跨线程的数据通过 store/backend 验证，而不是只检查单次返回值。
- [ ] 任何 `execute`、写文件或外部网络调用都有明确的权限/隔离测试。

API 签名、默认值、模型供应商支持和 0.7.x→1.0 的变化必须加载 `deepagents-docs` 实时核验。
