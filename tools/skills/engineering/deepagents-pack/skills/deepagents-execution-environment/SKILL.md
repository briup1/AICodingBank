---
name: deepagents-execution-environment
description: 设计或审查 DeepAgents 的 backend、虚拟文件系统、sandbox、shell、解释器和文件权限边界时加载；不负责总体入门、长期记忆建模或子 Agent 拆分。
metadata:
  framework: DeepAgents
  framework-version: "0.7.8"
  generated-from: official-sources
---

# DeepAgents 执行环境

## 先做能力分层

```text
agent tools
  ↓
FilesystemMiddleware
  ↓
BackendProtocol
  ├─ 文件读写/列举/搜索
  └─ SandboxBackendProtocol 才额外提供 execute
       ↓
宿主机、远程 sandbox、LangGraph state/store 或 Context Hub
```

`execute` 是否真实可用由 backend 的协议能力决定；非 sandbox backend 上该工具应返回不可用错误，不能把“工具存在”当成“命令能安全执行”。

## Backend 选择矩阵

| Backend | 数据范围 | 是否跨线程 | 命令执行 | 适用 |
|---|---|---:|---:|---|
| `StateBackend` | LangGraph state 中的虚拟文件 | 否（依赖线程） | 否 | 默认原型和短会话 |
| `FilesystemBackend` | 指定绝对 `root_dir` 下的宿主机文件 | 由磁盘决定 | 否 | 受控本地项目文件 |
| `LocalShellBackend` | 宿主机 root 下文件 | 由磁盘决定 | 是 | 仅受控开发环境；无隔离 |
| `StoreBackend` | LangGraph store | 是 | 否 | 跨线程长期文件/记忆 |
| `ContextHubBackend` | LangSmith Hub repo | 是 | 否 | 不另建 store 的持久化 |
| sandbox backend | 隔离运行环境 | 取决于 provider scope | 是 | 不可信代码、依赖安装和构建 |
| `CompositeBackend` | 按路径路由到多个 backend | 路由分别决定 | 路由分别决定 | 把工作区、memory、临时结果隔离 |

本地 `FilesystemBackend` 的 `root_dir` 必须是绝对路径；通常用 `CompositeBackend` 把内部 offload/对话数据与用户项目目录分开。`LocalShellBackend` 直连宿主机，不具备 sandbox 隔离。

## Sandbox 与解释器

需要执行代码时优先使用实现 `SandboxBackendProtocol` 的 provider，并明确生命周期：默认 thread-scoped；若使用 assistant-scoped，必须额外验证不同线程的数据和进程状态隔离。sandbox 与 agent 有两种集成方式：

- agent-in-sandbox：文件工具和 `execute` 都直接作用于 sandbox。
- sandbox-as-tool：主 agent 通过显式工具调用 sandbox，适合把高权限执行面隔离在少数动作上。

解释器是代码执行能力的实现策略，不等于权限系统。配置解释器时同时审查：可安装依赖、网络、环境变量、文件挂载、超时、资源上限、结果回收和清理；不要把任意 Python/JS 解释器暴露给不可信输入。

## 权限规则

权限规则要绑定 backend 路径，而不是只写自然语言。规则顺序会影响结果：先匹配的规则可能截断后续更严格规则，因此保护 `.env` 等敏感路径时，把 deny 规则放在宽泛 allow 规则之前，并为“工作区外”设置默认拒绝。

高风险操作建议：

```python
permissions = [
    FilesystemPermission(operations=["read", "write"], paths=["/workspace/.env"], mode="deny"),
    FilesystemPermission(operations=["read", "write"], paths=["/workspace/**"], mode="allow"),
    FilesystemPermission(operations=["read", "write"], paths=["/**"], mode="deny"),
]
```

上例使用官方 `FilesystemPermission` 形状表达规则顺序；路径、操作和模式仍应在 0.7.8 API 与目标 backend 上核验后再用于生产。

需要审批时用 `interrupt_on` 或权限的 `"interrupt"` 模式，把审批状态纳入 LangGraph checkpoint；不要用 prompt 约定替代可验证的中断。复合 backend 中，权限会按路由后的 backend 解释；每条路径都要单独验证，不能只测默认路由。

## 安全不变量与边缘测试

- 宿主机 shell ≠ 隔离执行；必须在代码、配置和用户提示中显式标注。
- secrets 不应通过环境变量无条件注入 sandbox；优先短期、最小范围、可轮换凭证。
- 用户可写目录、memory 路径和项目目录分开路由；否则会出现跨范围读写。
- 文件路径使用 backend 的 POSIX 虚拟路径约定；不要把宿主机路径直接拼进模型生成的路径。
- 测试至少覆盖：越界读、越界写、敏感文件 deny、命令注入/危险命令、人审中断恢复、线程间隔离、sandbox 销毁后的 artifact 回收。

排查顺序：

```text
工具调用是否到达
  → FilesystemMiddleware 是否启用
  → 路由到哪个 backend
  → backend 是否实现目标协议
  → permission 是否先命中 deny/interrupt
  → sandbox 是否仍存活且 scope 正确
  → 查看完整调用上下文与 checkpoint，而非只看错误文本
```
