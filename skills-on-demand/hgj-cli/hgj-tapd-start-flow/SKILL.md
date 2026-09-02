---
name: hgj-tapd-start-flow
version: 1.0.0
description: "TAPD 开始任务工作流 — 从当前仓库匹配 TAPD 项目，选择任务，生成并覆盖写入开发计划，开发后验收，使用 TAPD 源码关键字提交并推送。Triggers on: 开始任务, 开始TAPD任务, tapd start, 启动任务, 进入开发, 做任务"
metadata:
  category: "workflow"
  requires:
    mcp: ["mcp-server-tapd"]
---

# TAPD 开始任务工作流

用于用户说“开始任务”时，选择一个 TAPD task，生成开发计划，写回任务详情，然后驱动开发、验收、提交和推送。

## 核心约束

- 先确认项目和任务，再生成计划。
- 开发计划写入 TAPD task 时会**覆盖原 description**，必须先展示覆盖内容并等待用户明确确认。
- 开发完成后只提醒用户验收；用户未明确说“验收通过 / 没问题 / 可以提交”前，不要 commit 或 push。
- commit 前必须调用 `get_commit_msg` 获取 TAPD 源码关键字，并把关键字放入 commit body。
- 不要 force push，不要提交或打印 secrets、tokens、passwords、cookies、private keys。

## 触发输入

用户说“开始任务”时即可触发。用户可以补充项目名、任务 ID、任务关键词；如果上下文中没有这些信息，按流程查询和选择。

## 强制流程

### 1. 确认 TAPD 项目

先从当前仓库收集项目线索：

- 当前目录名
- `package.json` 的 `name`（如存在）
- `git remote -v` 中的仓库名或 path（如存在）

然后调用 `get_user_participant_projects` 查询用户参与项目，并过滤 `category=organization`。

匹配规则：

- 如果用户明确给了 `workspace_id`，直接展示该项目并等待确认。
- 如果当前仓库线索只匹配到一个高可信 TAPD 项目，展示匹配依据并等待用户确认。
- 如果无法确认或匹配到多个项目，列出候选项目，让用户选择。
- 不要在项目不明确时默认选第一个项目。

### 2. 查询并选择任务

项目确认后，优先调用 `get_todo(workspace_id, "task")` 查询用户待办任务。

如果待办为空或用户给了任务关键词，再调用 `get_stories_or_tasks` 查询任务：

```
get_stories_or_tasks(workspace_id, {
  entity_type: "tasks",
  name: "%关键词%",
  fields: "id,name,description,owner,status,workspace_id,effort",
  limit: 20
})
```

向用户展示候选任务的 ID、标题、状态、处理人和摘要，等待用户选择确认。

### 3. 读取任务上下文

用户确认任务后，调用：

```
get_stories_or_tasks(workspace_id, {
  entity_type: "tasks",
  id: taskId,
  fields: "id,name,description,owner,status,workspace_id,effort"
})
```

如需要理解历史讨论，再调用 `get_comments` 查询该任务评论。

### 4. 生成开发计划

基于任务标题、原 description、评论、当前仓库结构生成计划。计划必须具体到可执行步骤，但不要编造 TAPD 中不存在的信息。

推荐写入格式：

```md
## 背景

## 目标

## 开发计划

1. ...

## 验收标准

## 风险与依赖
```

展示完整计划，等待用户修改或确认。

### 5. 覆盖写入 task description

只有用户明确确认计划后，才能调用：

```
update_story_or_task(workspace_id, {
  entity_type: "tasks",
  id: taskId,
  description: confirmedPlan
})
```

写入前必须提示：这会覆盖当前 TAPD task 的原 description，并展示即将写入的完整内容。不要静默覆盖。

### 6. 开始开发并等待验收

按确认后的计划修改代码。开发完成后：

1. 运行与改动相关的验证命令。
2. 汇总改动和验证结果。
3. 提醒用户验收。

用户未明确验收通过前，不要 commit 或 push。

### 7. 验收通过后提交并推送

用户确认验收通过后，先获取 TAPD 源码提交关键字：

```
get_commit_msg(workspace_id, { object_id: taskId, type: "task" })
```

然后执行：

1. `git status` 查看变更文件。
2. `git diff --stat` 确认变更范围。
3. 检查 diff 中没有 secrets、tokens、passwords、cookies、private keys。
4. `git add` 暂存相关文件。
5. `git commit`，格式：

```
type[scope]: 中文描述

{TAPD 源码关键字}
```

6. `git push`；如果当前分支没有远端追踪，使用 `git push -u origin {branch}`。

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 无法确认项目 | 展示参与项目列表，让用户选择 |
| 找不到任务 | 提示用户换关键词或提供任务 ID |
| 多个任务匹配 | 展示候选，等待用户选择 |
| 用户修改计划 | 重新展示修改后的计划并等待确认 |
| 用户不同意覆盖 description | 不写入 TAPD，停在计划确认阶段 |
| 开发验证失败 | 汇报失败命令和错误，不进入验收 |
| 没有代码变更 | 不 commit，说明没有可提交内容 |
| push 失败 | 汇报错误，不自动 force push |

## 常用 MCP 工具

- `get_user_participant_projects`
- `get_todo`
- `get_stories_or_tasks`
- `get_comments`
- `update_story_or_task`
- `get_commit_msg`
