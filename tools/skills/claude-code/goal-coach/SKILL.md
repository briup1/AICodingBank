---
name: goal-coach
description: This skill should be used when the user mentions "/goal", asks whether a task is suitable for /goal, wants help writing a /goal prompt, or needs to generate completion criteria, modification boundaries, stop rules, and parallel subagent breakdown for a coding task. Use it whenever the user is unsure whether to delegate a multi-step coding task to /goal.
version: 0.2.0
---

# /goal 任务教练

Help the user decide whether a coding task is appropriate for the `/goal` command in Claude Code, and if so, generate a complete, ready-to-paste `/goal` prompt in Chinese.

## Core responsibilities

1. If the user has not provided a concrete goal, ask for it first.
2. Analyze the current context (project files, task description) and decide whether `/goal` is suitable.
3. If not suitable, briefly explain why and recommend the next step.
4. If suitable, evaluate whether the task can be executed faster and more safely with multiple parallel subagents, and include that recommendation in the generated prompt.
5. Output a complete `/goal` prompt containing:
   - Goal statement
   - 完成标准 (completion criteria)
   - 修改边界 (modification boundaries)
   - 停止规则 (stop rules)
   - 可选：并行 subagent 拆分建议 (when applicable)

## When /goal is suitable

A task is suitable for `/goal` when all three dimensions are true:

1. **Multi-step / iterative**: The task likely requires several rounds of implementation, checking, and adjustment. One-shot answers are not enough.
2. **Verifiable completion**: There is a concrete way to know the task is done — a test passes, a page renders correctly, a command exits with 0, a file is created, etc.
3. **Bounded scope**: The files, pages, components, or modules that may be changed can be reasonably limited.

If any dimension is weak or missing, `/goal` is probably not the right tool.

## Workflow

### Step 1: Confirm the goal

If the user only says something like `/goal-coach` or "帮我看看这个需求适不适合 goal命令", ask:

> 请描述你想交给 /goal 完成的具体任务是什么？

Wait for the user to provide the goal before proceeding.

### Step 2: Gather context

If project context is available (current working directory, open files, recent changes), briefly inspect it to understand:

- What kind of project this is
- Which files or modules are relevant
- What existing tests, build commands, or verification methods exist

Use Glob, Grep, or Read as needed, but keep inspection lightweight. Do not dig deep unless the task requires it.

### Step 3: Evaluate suitability

Score each of the three dimensions as **强 / 中 / 弱** and explain briefly in 1-2 sentences.

| Dimension | Strong | Medium | Weak |
|-----------|--------|--------|------|
| 多步迭代 | Clearly needs exploration + multiple attempts | Probably multi-step but straightforward | One action or one answer is enough |
| 可验证完成 | Clear pass/fail check available | Verifiable but manual or somewhat subjective | No clear way to confirm done |
| 范围可限定 | Files/modules naturally isolated | Mostly bounded with a few touchpoints | Hard to limit scope; risk of wide refactor |

If two or more dimensions are **弱**, recommend against `/goal`.
If one dimension is **弱** but the other two are strong, mention the risk and suggest how to mitigate it.

### Step 4: Evaluate parallel subagent feasibility

After confirming `/goal` is suitable, decide whether the task should use multiple parallel subagents. Ask these questions:

1. **Can the task be split into clearly independent sub-tasks?** Each subagent must own a distinct slice with minimal overlap or shared mutable state.
2. **Do the sub-tasks have independent verification?** Each subagent should know when it is done without waiting for the others.
3. **Is the coordination cost worth it?** Parallelism helps when there are 3+ distinct workstreams or when investigation can be split by file/module/dimension.

**When to recommend sequential (`/goal` only):**
- One linear chain of changes (e.g., fix a bug in a single flow)
- Sub-tasks tightly coupled and must be done in order
- Total work is small enough that coordination overhead dominates

**When to recommend parallel subagents:**
- Investigation can be split by module, file, or hypothesis
- Multiple independent fixes or refactors are needed
- Cross-cutting concerns (e.g., frontend + backend + tests) can be worked on separately and integrated at the end
- A multi-step verification pipeline where different agents check different dimensions

If parallel is appropriate, specify:
- **Number of subagents**: Recommend 2–4 by default; more only when the workstreams are truly independent.
- **Responsibility per subagent**: Each must have a clear, non-overlapping scope and a concrete deliverable.
- **Integration point**: How the results should be merged or validated together (e.g., run full test suite, review conflicts, one agent does final integration).
- **Execution hint for `/goal`**: Briefly mention that the parallel work can be realized with Claude Code's multi-agent tools — e.g., use `TeamCreate` to set up a team, `TaskCreate` to list independent tasks, and spawn dedicated `Agent` teammates to own each workstream. Keep this as a concise hint inside the generated prompt; `goal-coach` itself does not execute these tools.

If parallel is **not** appropriate, state that explicitly with a one-sentence reason.

### Step 5a: If not suitable

Respond with:

- A clear verdict: "这个任务不太适合用 /goal。"
- Which dimension(s) are weak and why
- A concrete next-step recommendation, such as:
  - Use a normal prompt for a one-shot answer
  - Use `EnterPlanMode` if the task needs planning first
  - Ask the user 2-3 clarifying questions before deciding
  - Break the task into smaller pieces

Keep the explanation concise.

### Step 5b: If suitable

Generate a complete `/goal` prompt using this exact structure. Include the parallel subagent section only when it applies.

```text
/goal 完成【具体任务】。

完成标准：
1. 【可验证的结果 1】
2. 【可验证的结果 2】
3. 完成后说明验证方式，不要只写“已完成”。

修改边界：
- 只允许修改【页面 / 组件 / 文件 / 模块】。
- 不要重构无关部分，不要顺手优化其他页面。
- 文档里出现的“未来”“后续”“可以考虑”“有机会”都不是本次任务，不要实现。

停止规则：
如果同一个问题连续出现 3 次，或者需要删除重要文件、重做页面结构、修改数据库、修改登录/支付相关逻辑，请停止并说明：
1. 已经做了什么
2. 当前卡在哪里
3. 尝试过哪些方法
4. 下一步建议我确认什么

并行执行建议（如适用）：
- 本任务适合拆分为【N】个 subagent 并行执行：
  - Subagent 1：负责【具体工作】，交付【可验证结果】。
  - Subagent 2：负责【具体工作】，交付【可验证结果】。
  - ...
- 各 subagent 之间【耦合关系 / 数据依赖】：
- 建议用 Claude Code 的多 agent 能力实现并行：先用 `TeamCreate` 创建团队，再用 `TaskCreate` 拆分任务，最后为每个子任务 spawn 独立的 `Agent` teammate；各 subagent 完成后由指定 agent 合并结果并运行全量验证。
- 最后由谁整合结果、运行全量验证：
```

If parallel subagents are **not** recommended, omit the entire `并行执行建议` block from the prompt and instead add a short note after the prompt such as:

> 这个任务适合用单个 `/goal` 顺序执行，因为各步骤依赖较强，拆分反而增加协调成本。

Fill in the bracketed parts based on the user's task and project context. Be specific. Do not leave generic placeholders.

After the prompt, add a short note explaining:

- Why this task fits `/goal`
- Whether parallel subagents are recommended and why
- Any assumption made about verification
- Any risk the user should watch

## Output rules

- Always respond in Chinese, except YAML frontmatter.
- Do not execute `/goal` yourself; only produce the prompt for the user to paste.
- Keep the evaluation section concise; the generated prompt is the main deliverable.
- If context is insufficient to fill boundaries or verification, state what you assumed and ask the user to confirm.
- Be honest about parallel feasibility: do not force subagent parallelism when tasks are tightly coupled or too small.

## Examples

### Example 1: Suitable task, sequential

**User:** 帮我看看这个任务适不适合 goal：修复首页登录按钮点击后没反应的问题。

**Output:**

这个任务适合用 `/goal`，但不建议拆成多个 subagent 并行，因为问题集中在单一交互链路上，拆分反而增加协调成本。

```text
/goal 修复首页登录按钮点击后没反应的问题。

完成标准：
1. 在首页输入邮箱和密码后，点击登录按钮，能够正常跳转到后台首页。
2. 如果密码错误，页面显示明确的错误提示。
3. 完成后说明你是怎么验证的，不要只写“已完成”。

修改边界：
- 只允许修改首页登录按钮相关代码及对应的事件处理逻辑。
- 不要重构无关部分，不要顺手优化其他页面。
- 文档里出现的“未来”“后续”“可以考虑”“有机会”都不是本次任务，不要实现。

停止规则：
如果同一个问题连续出现 3 次，或者需要删除重要文件、重做页面结构、修改数据库、修改登录/支付相关逻辑，请停止并说明：
1. 已经做了什么
2. 当前卡在哪里
3. 尝试过哪些方法
4. 下一步建议我确认什么
```

说明：完成标准可以通过手动点击验证，范围基本限定在首页登录逻辑，适合 `/goal` 自主迭代。

### Example 2: Suitable task, parallel

**User:** 帮我看看这个任务适不适合 goal：为项目添加用户资料的 CRUD 页面，包括列表页、详情页和对应的 API 接口，并补充单元测试。

**Output:**

这个任务适合用 `/goal`，并且可以拆分为 3 个 subagent 并行执行，最后由其中一个负责整合。

```text
/goal 为项目添加用户资料的 CRUD 功能，包括列表页、详情页、API 接口和单元测试。

完成标准：
1. 用户资料列表页可以分页展示用户数据。
2. 用户资料详情页可以查看和编辑单个用户。
3. API 接口支持创建、读取、更新、删除用户资料，并通过接口测试验证。
4. 单元测试覆盖主要业务逻辑，测试命令可以全部通过。
5. 完成后说明你是怎么验证的，不要只写“已完成”。

修改边界：
- 只允许新增或修改用户资料（User Profile）相关的前端页面、API 接口和测试文件。
- 不要重构无关部分，不要顺手优化其他页面。
- 文档里出现的“未来”“后续”“可以考虑”“有机会”都不是本次任务，不要实现。

停止规则：
如果同一个问题连续出现 3 次，或者需要删除重要文件、重做页面结构、修改数据库、修改登录/支付相关逻辑，请停止并说明：
1. 已经做了什么
2. 当前卡在哪里
3. 尝试过哪些方法
4. 下一步建议我确认什么

并行执行建议：
- 本任务适合拆分为 3 个 subagent 并行执行：
  - Subagent 1：负责后端 API 接口（CRUD + 路由 + 数据库模型），交付可独立通过的接口测试。
  - Subagent 2：负责前端列表页（分页、搜索、跳转），交付可渲染并与 mock 数据或真实 API 交互的页面。
  - Subagent 3：负责前端详情页（查看、编辑、表单校验），交付可渲染并调用 API 的页面。
- 各 subagent 之间依赖：API 契约（字段名、路由路径）需要在开始前约定；各 subagent 先按约定开发，最后统一对接。
- 建议用 Claude Code 的多 agent 能力实现并行：先用 `TeamCreate` 创建团队，再用 `TaskCreate` 拆分上述 3 个任务，然后为每个任务 spawn 独立的 `Agent` teammate；Subagent 1 完成后公布最终 API 契约，Subagent 2/3 按契约调整后由 Subagent 1 或一个独立整合 agent 合并代码并运行全量测试。
- 最后由 Subagent 1 或一个独立的整合 subagent 合并结果、运行全量测试并处理接口契约冲突。
```

说明：列表页、详情页和 API 接口是相对独立的工作流，拆分后可以并行推进；但 API 契约需要先对齐，避免最后整合时大量返工。

### Example 3: Not suitable

**User:** /goal-coach

**Output:**

请描述你想交给 /goal 完成的具体任务是什么？

### Example 4: Weak scope

**User:** 重构整个前端架构。

**Output:**

这个任务不太适合直接用 `/goal`。

- **多步迭代**：强，确实需要多轮推进。
- **可验证完成**：弱，"架构重构完成"没有明确验收标准。
- **范围可限定**：弱，涉及全站文件，边界极难控制。

建议先用 `EnterPlanMode` 把重构拆分成阶段性目标和具体文件清单，再决定是否对其中某一个小阶段使用 `/goal`。
