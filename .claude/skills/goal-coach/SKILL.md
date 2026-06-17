---
name: goal-coach
description: This skill should be used when the user mentions "/goal", asks whether a task is suitable for /goal, wants help writing a /goal prompt, or needs to generate completion criteria, modification boundaries, and stop rules for a coding task. Use it whenever the user is unsure whether to delegate a multi-step coding task to /goal.
version: 0.1.0
---

# /goal 任务教练

Help the user decide whether a coding task is appropriate for the `/goal` command in Claude Code, and if so, generate a complete, ready-to-paste `/goal` prompt in Chinese.

## Core responsibilities

1. If the user has not provided a concrete goal, ask for it first.
2. Analyze the current context (project files, task description) and decide whether `/goal` is suitable.
3. If not suitable, briefly explain why and recommend the next step.
4. If suitable, output a complete `/goal` prompt containing:
   - Goal statement
   - 完成标准 (completion criteria)
   - 修改边界 (modification boundaries)
   - 停止规则 (stop rules)

## When /goal is suitable

A task is suitable for `/goal` when all three dimensions are true:

1. **Multi-step / iterative**: The task likely requires several rounds of implementation, checking, and adjustment. One-shot answers are not enough.
2. **Verifiable completion**: There is a concrete way to know the task is done — a test passes, a page renders correctly, a command exits with 0, a file is created, etc.
3. **Bounded scope**: The files, pages, components, or modules that may be changed can be reasonably limited.

If any dimension is weak or missing, `/goal` is probably not the right tool.

## Workflow

### Step 1: Confirm the goal

If the user only says something like `/goal-coach` or "帮我看看这个适不适合 goal", ask:

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

### Step 4a: If not suitable

Respond with:

- A clear verdict: "这个任务不太适合用 /goal。"
- Which dimension(s) are weak and why
- A concrete next-step recommendation, such as:
  - Use a normal prompt for a one-shot answer
  - Use `EnterPlanMode` if the task needs planning first
  - Ask the user 2-3 clarifying questions before deciding
  - Break the task into smaller pieces

Keep the explanation concise.

### Step 4b: If suitable

Generate a complete `/goal` prompt using this exact structure:

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
```

Fill in the bracketed parts based on the user's task and project context. Be specific. Do not leave generic placeholders.

After the prompt, add a short note explaining:

- Why this task fits `/goal`
- Any assumption made about verification
- Any risk the user should watch

## Output rules

- Always respond in Chinese, except YAML frontmatter.
- Do not execute `/goal` yourself; only produce the prompt for the user to paste.
- Keep the evaluation section concise; the generated prompt is the main deliverable.
- If context is insufficient to fill boundaries or verification, state what you assumed and ask the user to confirm.

## Examples

### Example 1: Suitable task

**User:** 帮我看看这个任务适不适合 goal：修复首页登录按钮点击后没反应的问题。

**Output:**

这个任务适合用 `/goal`。

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

### Example 2: Not suitable

**User:** /goal-coach

**Output:**

请描述你想交给 /goal 完成的具体任务是什么？

### Example 3: Weak scope

**User:** 重构整个前端架构。

**Output:**

这个任务不太适合直接用 `/goal`。

- **多步迭代**：强，确实需要多轮推进。
- **可验证完成**：弱，"架构重构完成"没有明确验收标准。
- **范围可限定**：弱，涉及全站文件，边界极难控制。

建议先用 `EnterPlanMode` 把重构拆分成阶段性目标和具体文件清单，再决定是否对其中某一个小阶段使用 `/goal`。
