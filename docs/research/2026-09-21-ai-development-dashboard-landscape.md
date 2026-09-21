# AI 编码时代开发看板开源项目调研

- 日期：2026-09-21
- 范围：AI 编码 Agent 任务看板、多 Agent 并行开发、Git Worktree/分支隔离、会话与开发生命周期管理
- 来源原则：只使用项目官方 GitHub 仓库 README、许可证和仓库元数据

## 结论摘要

GitHub 上已经出现一批“AI 编码 Agent + Kanban/控制台 + Worktree”的开源项目。最接近当前 `wl-git-requirement-flow` 的是 **Vibe Kanban、Agent Console、Agent Taskboard 和 Kangentic**；但截至 2026-09-21，没有一个项目同时覆盖我们的全部约束：

- 以“需求”而不是 Agent 会话为主实体；
- 同需求多分支聚合和主分支选择；
- `master → story → Dev/Beta/master` 单向血缘安全；
- 用户级跨项目 Worktree 生命周期；
- Dev/Beta 测试 SHA 过期识别；
- 上线、清理、最近上线和归档；
- TAPD 标题缓存；
- 只读 Git 扫描和个人本机数据边界。

因此不建议直接替换当前实现。最佳策略是：**保留 `wl-git-requirement-flow` 的领域模型，借鉴 Agent Console/Agent Taskboard/Kangentic 的实时控制台和任务详情交互，参考 Vibe Kanban 的产品模型，但不要以正在 sunset 的 Vibe Kanban 作为长期底座。**

## 项目对比

| 项目 | 核心定位 | 看板 UI | Worktree/Git | 多 Agent/会话 | 许可证 | 判断 |
| --- | --- | --- | --- | --- | --- | --- |
| [BloopAI/vibe-kanban](https://github.com/BloopAI/vibe-kanban) | 编排多个 AI 编码 Agent 的任务看板 | 强 | 每任务隔离、PR/任务流 | 支持多种编码 Agent | MIT | 产品最接近，但官方 README 已宣布 sunsetting；适合借鉴，不适合新增长期依赖 |
| [AndyMik90/agent-console](https://github.com/AndyMik90/agent-console) | 本地浏览器控制平面，管理多个 CLI 编码 Agent | 强 | 每任务独立 Worktree、diff/终端 | Provider-agnostic，多会话 | MIT | 最值得借鉴服务/API、实时终端和 Worktree 控制架构；项目仍较早期 |
| [52216108/agent-taskboard](https://github.com/52216108/agent-taskboard) | 本地优先的跨项目任务板和 Agent 任务队列 | 强 | 扫描项目分支、dirty 状态和待办；Worktree 不是核心 | Agent 可认领并回写任务 | 需核对 | 与“用户级跨项目总览”接近；适合参考项目扫描和 Agent claim UX |
| [mloll1/Kangentic](https://github.com/mloll1/Kangentic) | 多 Agent Kanban 编排器 | 强 | 自动 Worktree 隔离、PR 工作流 | 多 Agent 队列和自动循环 | AGPL-3.0 | 与未来的实时按钮、任务运行控制较接近；适合参考 Kanban 和执行队列，直接复用代码需评估许可证 |
| [p-wegner/agentic-kanban](https://github.com/p-wegner/agentic-kanban) | 面向 AI swarm 的实时 Kanban/MCP 服务 | 强 | GitHub/MCP 集成，Worktree 不是核心 | Provider-agnostic、多 Agent | GPL-3.0 | 适合借鉴任务认领、WebSocket 和实时事件；许可证要求使直接复用代码需谨慎 |
| [ntindle/hivemind](https://github.com/ntindle/hivemind) | 以 GitHub Issue 为 mission 的多 Agent 协作层 | 中 | GitHub Issues/任务认领；非个人 Worktree 看板核心 | 多 Agent、CLI/VS Code/Observer | MIT | 适合借鉴 Agent 认领和去重协调，不适合直接替代本地需求生命周期看板 |
| [BradenTerry/agent-worktrees](https://github.com/BradenTerry/agent-worktrees) | 每 Worktree 一个 Agent 会话的本地桌面工作区 | 中 | Worktree 是核心，含 diff/notes/status | 多并行会话 | Apache-2.0 | 领域形状接近，但仓库成熟度信号较弱；适合阅读实现，不建议直接采用 |
| [herdrdev/herdr](https://github.com/herdrdev/herdr) | 面向编码 Agent 的终端复用器和控制面 | 非 Kanban | 原生 Worktree/终端/Agent 生命周期 | 强 | Apache-2.0 | 是执行层补充而不是需求看板替代；当前工作流继续复用 Herdr 很合理 |

## 重点项目

### 1. Vibe Kanban

官方仓库将其描述为可并行编排 Claude Code、Codex、Gemini CLI 等编码 Agent 的任务平台，并提供任务隔离、任务状态、Agent 切换、MCP 和 PR 工作流。它在产品形态上最接近“AI 时代的开发看板”。

但官方 README 当前明确写有 **“Vibe Kanban is sunsetting”**。因此：

- 可以学习其“任务 → Agent 会话 → 隔离开发环境 → PR”的产品模型；
- 可以研究其 Rust/TypeScript 架构与任务编排方式；
- 不应把它作为我们新功能的长期上游依赖或直接迁移目标。

结论：**重点借鉴，不直接采用。**

### 2. Agent Console

Agent Console 把自己定位为运行在浏览器中的本地编码 Agent 控制平面。README 强调：

- 每个任务运行在独立 Git Worktree；
- 可同时运行多个 Agent 会话；
- 有实时终端、diff、文件浏览和任务状态；
- 不绑定单一 Agent provider；
- 本地运行并使用 SQLite。

与我们相比，它更偏“启动和控制 Agent”，而 `wl-git-requirement-flow` 更偏“需求、分支血缘、环境验证和清理生命周期”。

结论：**最适合借鉴未来 `dashboard serve`、实时刷新、任务详情页和终端/diff 接口。**

### 3. Agent Taskboard

Agent Taskboard 是 local-first 的跨项目面板：扫描本机项目，展示当前分支、未提交状态、技术栈与待办，并允许编码 Agent 在项目目录中认领和回写任务。它更接近我们的“用户级项目总览”，但 Worktree 隔离、Dev/Beta 血缘和发布归档不是其核心。

结论：**适合借鉴跨项目发现、任务认领和简洁卡片体验。**

### 4. Kangentic

Kangentic 将 Kanban 与多 Agent 自动执行结合，README 描述了：

- Agent 任务队列；
- 并行 Agent；
- 自动 Worktree 隔离；
- 分支、测试、PR 生命周期；
- CLI Agent 控制；
- 本地运行。

它与我们未来可能的“从看板观察执行”方向非常接近。不过其重点是自动执行和 PR，而我们的重点是已有公司 Git 流程、Dev/Beta/master 血缘安全和个人需求组合管理。

结论：**适合借鉴 Kanban 状态与执行队列，但不替代现有领域状态机。**

### 5. Agentic Kanban

Agentic Kanban 是一个带实时 WebSocket、MCP 接口和多 Agent 任务认领的 Kanban 服务，适合 AI swarm 使用。它提供：

- 任务 claim/complete；
- Agent 活跃状态；
- 实时更新；
- GitHub 集成；
- provider-agnostic CLI。

它解决的是“多个 Agent 不重复做同一任务”，不是“个人跨项目需求分支和 Worktree 生命周期”。另外 GPL-3.0 意味着直接复制/组合代码前需要评估许可证影响。

结论：**只借鉴实时事件和任务认领协议。**

### 6. Hivemind

Hivemind 使用 GitHub Issues 作为任务事实来源，提供 CLI、VS Code 扩展和 observer dashboard，让 Agent 发现、认领和完成 mission，并通过 GitHub 协作。

它适合团队级 Agent 协调，但依赖 GitHub Issue 模型，对公司内部 TAPD、Dev/Beta 分支流和本地 Worktree 组合管理不够贴合。

结论：**适合借鉴任务认领和冲突避免，不适合直接采用。**

### 7. Agent Worktrees

Agent Worktrees 以“一个 Worktree 对应一个 Agent 会话”为核心，提供 diff、notes、terminal、状态和通知。它的模型与我们个人并行需求开发非常接近，但目前仓库规模和活跃度信号较弱。

结论：**适合阅读 Worktree UI 和桌面会话模型，不建议作为核心依赖。**

### 8. Herdr

Herdr 是面向编码 Agent 的终端工作区和 Agent 控制工具，提供 pane、workspace、Agent 生命周期和 Worktree 管理。它不是 Kanban，也不负责需求主题、Dev/Beta 测试或上线归档。

结论：**继续作为执行和并行编排层，与 `wl-git-requirement-flow` 看板互补。**

## 与当前实现的差距

当前开源项目普遍采用：

```text
任务卡 → 启动 Agent → 创建 Worktree → 查看 diff → 创建 PR
```

我们的目标是：

```text
TAPD 需求
  → 主分支与关联分支
  → Worktree 开发
  → Dev/Beta/master 单向晋级
  → 测试 SHA 绑定
  → 上线确认
  → Worktree/本地/远端分支清理
  → 最近上线与归档
```

因此当前实现的差异化不是“也做一个 Kanban”，而是：

1. **需求聚合**：同一个需求的 clean、旧分支、candidate 和 integration 分支属于同一张卡片。
2. **企业分支流**：把共享 Dev 当作集成目标，禁止反向污染需求分支。
3. **验证 SHA**：测试结论绑定提交，新增提交后自动失效。
4. **生命周期清理**：Worktree、local branch、remote branch 分层清理。
5. **用户级跨项目**：不要求业务仓库安装服务或提交看板状态。
6. **TAPD 主题**：标题同步独立于 Git 刷新。

## 建议

### 不建议

- 因 Vibe Kanban 形态接近就直接迁移：其官方已宣布 sunsetting。
- 直接采用任一早期小项目作为核心底座：多数仍在快速变化，且领域模型不匹配。
- 引入 GPL-3.0 项目代码而不评估许可证。
- 为了“AI 味”把看板变成 Agent 启动器，丢失需求和分支血缘的主线。

### 建议借鉴顺序

1. **Agent Console**：本地 HTTP 服务、实时刷新、任务详情、终端/diff API。
2. **Agent Taskboard**：个人看板卡片、Worktree 详情、变更审查。
3. **Kangentic**：Kanban 状态与 Agent 执行队列。
4. **Vibe Kanban**：产品信息架构和多 Agent 抽象，但不依赖其生命周期。
5. **Hivemind/Agentic Kanban**：未来多人或多 Agent 的 claim/event 协议。
6. **Herdr**：保持为实际执行层。

## 最终判断

目前没有一个成熟、持续维护且能直接满足需求的开源项目。最合理的路径是：

- 继续开发轻量的 `wl-git-requirement-flow`；
- 不复制完整 Agent 编排平台；
- 下一阶段只借鉴 Agent Console 的本地实时服务和 Agent Taskboard 的 Worktree 卡片体验；
- 保留当前独特的需求聚合、分支安全、验证 SHA、上线和清理模型；
- 若未来需要从看板直接启动/控制 Agent，再通过 Herdr 或标准 Agent API 接入，而不是把执行器重写进看板。
