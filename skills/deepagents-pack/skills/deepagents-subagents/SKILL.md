---
name: deepagents-subagents
description: 设计 DeepAgents 的同步、动态和异步子 Agent 委派，选择上下文隔离、传输、并发和取消语义时加载；不处理一般 backend 权限或单 Agent 入门。
metadata:
  framework: DeepAgents
  framework-version: "0.7.8"
  generated-from: official-sources
---

# DeepAgents 子 Agent 编排

## 先判断编排形态

```text
任务短、需要结果后再继续
  → 同步 subagents= / task

任务类型运行时才确定、需要上下文隔离
  → 动态 task（明确 name/description/contract）

长时间、并行、需要轮询/取消/中途更新
  → AsyncSubAgent + launch/check/update/cancel/list
```

子 Agent 的首要收益是 **context quarantine**：专家的详细搜索、文件读取和中间推理留在其上下文，supervisor 只接收最终结果。不要为了“并行”把不相关的小任务都拆成子 Agent，也不要让子 Agent 重复拥有不必要的高权限工具。

## 同步子 Agent

`subagents` 接受声明式字典或 `CompiledSubAgent`。声明式配置至少提供：

- `name`：唯一标识，出现在 `task()` 调用、消息 metadata 和 streaming 事件中。
- `description`：具体、行动导向；supervisor 用它决定何时委派。
- `system_prompt`：角色、输入/输出契约、停止条件和不可越过的边界。
- 可选 `tools`、`model`、`middleware`、`skills`、`permissions`、`interrupt_on`、`response_format`。

DeepAgents 默认会提供一个同步 `general-purpose` 子 Agent；要替换它，使用同名配置，不要并行注册两个含义相同的通用 worker。同步子 Agent 默认不继承主 Agent 的 middleware；共享能力要显式配置，避免隐式权限扩散。

推荐契约：

```python
subagents = [{
    "name": "researcher",
    "description": "检索官方资料并返回带来源的事实与未决问题。",
    "system_prompt": "只读外部资料；结果包含结论、证据 URL、冲突和置信边界。",
    "tools": [search_official_docs],
}]
```

把共享状态放在可验证的文件路径或 store，而不是复制完整消息历史；主 Agent 接收 `summary + artifact paths + errors`。

## 动态子 Agent

当 worker 列表、领域或任务参数在运行时才知道时，用动态 `task` 委派。把可选 worker 的 description 写得足够具体，并限制其工具和读写范围。动态 worker 适合一次性隔离任务；需要固定拓扑、强类型输出或独立部署时，改用预声明 `SubAgent`/`CompiledSubAgent`。

不要让模型从任意用户文本拼接 worker 名称、URL、系统提示或权限；worker 配置应来自受控注册表，用户输入只作为任务数据。

## 异步子 Agent

长任务或并行工作流使用 `AsyncSubAgent`。核心操作是：

```text
launch → 返回完整 task_id
  → check / list 获取新状态
  → update 以新指令在同一 task 上重启/继续
  → cancel 终止
  → 汇总各 worker 的最终产物
```

完整 task ID 必须原样保存；不要从对话历史读取旧状态代替 `check`/`list`。异步任务元数据保存在独立的 `async_tasks` state channel，不依赖消息历史，因此能在上下文压缩后继续追踪。

传输与部署：

- `url` 省略：ASGI/in-process，适合同一 LangGraph deployment 的 co-deployed graph，低延迟且默认推荐。
- 提供 `url`：HTTP，适合独立扩缩容、不同资源规格或跨团队维护；认证和超时必须纳入运行环境配置。
- 混合拓扑可按 worker 分别选择；不要因为远程就假定共享 thread、store 或文件系统。

## 并发与失败策略

- 并发数由 worker pool、模型配额、sandbox 数量和下游 API 限制共同决定；supervisor 也占一个 worker slot。
- 每个 worker 任务应幂等，产物带 task ID/版本；重复 launch 不应覆盖正确结果。
- 处理 `success/error/cancelled` 和超时，保留部分结果与失败原因；不要把未完成当成功。
- update 会中断当前 run 并在同一 task 上按新指令重新运行；cancel 后必须验证终态。
- 主 Agent 的输出应标注来源 worker、状态、产物路径和未解决问题。

## 验证矩阵

- 路由：相同请求是否稳定选择正确 worker，description 是否不会互相抢占。
- 隔离：worker 无法读取未授权路径或主 Agent 的私有上下文。
- 同步：异常、超时和空结果能回到 supervisor 的可处理分支。
- 异步：launch 后不立即假设完成；check/list 状态可恢复；update/cancel 生效。
- 传输：ASGI 与 HTTP 分别测试认证、网络失败、线程/任务关联和 trace。
- 负载：至少测试 `supervisor + N workers` 的 worker pool 余量、速率限制和部分失败。

版本敏感的类字段、SDK 方法、事件名和部署配置必须加载 `deepagents-docs` 核验。
