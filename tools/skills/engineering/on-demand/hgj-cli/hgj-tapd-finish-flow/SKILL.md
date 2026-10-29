---
name: hgj-tapd-finish-flow
version: 1.0.0
description: "TAPD 任务收尾工作流 — 关闭任务、填写工时、使用 TAPD 源码关键字提交并推送代码。Triggers on: 完成任务, 关闭任务, tapd finish, 提交代码, 开发完成收尾, 完成tapd任务, 任务收尾"
metadata:
  category: "workflow"
  requires:
    mcp: ["mcp-server-tapd"]
---

# TAPD 任务收尾工作流

开发完成后一键收尾：关闭任务 → 填写工时 → 提交代码 → 推送远端。

## 输入

用户触发任务收尾时需提供任务 ID（短 ID，如 `1066535`）。如果上下文中已有明确的任务 ID，可以直接使用。

## 强制流程

必须**严格按顺序**执行以下步骤，不可跳过或合并：

### 1. 获取任务详情

调用 `get_stories_or_tasks`，使用完整 ID（`11{workspace_id}0{short_id}` 格式）获取：
- `effort`（预估工时）
- `owner`（处理人）
- `name`（任务名）
- `workspace_id`

```
get_stories_or_tasks(workspace_id, { entity_type: "tasks", id: fullTaskId, fields: "id,name,effort,owner,workspace_id,status" })
```

### 2. 关闭任务

调用 `update_story_or_task` 将状态设为 `done`：

```
update_story_or_task(workspace_id, { entity_type: "tasks", id: fullTaskId, status: "done" })
```

### 3. 填写工时

使用 `add_timesheets`，实际工时 = 预估工时（effort 字段值），日期为今天：

```
add_timesheets(workspace_id, {
  entity_type: "task",
  entity_id: fullTaskId,
  timespent: effort值,
  owner: task.owner,
  spentdate: "YYYY-MM-DD"  // 今天
})
```

**防重复**：先调用 `get_timesheets` 查询同一 `owner + spentdate + entity_id` 是否已有记录。已有则调用 `update_timesheets` 更新。

### 4. 获取源码提交关键字（不可跳过）

> **必须先获取关键字再 commit，否则 commit 信息无法关联 TAPD 任务。**

```
get_commit_msg(workspace_id, { object_id: fullTaskId, type: "task" })
```

将返回值保存到变量，下一步 commit 时作为 body 使用。

### 5. Git Commit

1. `git status` 查看变更文件
2. `git diff --stat` 确认变更范围
3. `git add` 暂存相关文件
4. `git commit`，格式：

```
type[scope]: 中文描述

{TAPD 源码关键字}
```

- type/scope 根据实际改动推断（feat/fix/refactor 等）
- 中文描述为任务名的核心内容
- **TAPD 关键字必须作为 body 第二行，不可遗漏**

### 6. Git Push

推送当前分支到远端：

```
git push
```

如果当前分支没有远端追踪，使用 `git push -u origin {branch}`。

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 任务 ID 找不到 | 提示用户确认 ID |
| 任务已是 done 状态 | 跳过关闭步骤，继续后续流程 |
| effort 为空或 0 | 提示用户输入实际工时 |
| 没有未提交的变更 | 跳过 commit 步骤，直接 push |
| push 失败 | 提示错误信息，不自动 force push |

## 确认规则

工时填写前必须向用户确认（防误写），其余步骤自动执行。确认格式：

> 将为任务 `{任务名}` 填写 `{effort}` 小时工时（{today}），确认吗？

## 完成后汇报

执行完毕后输出汇总：

```
✓ 任务已关闭: {任务名}
✓ 工时已填写: {effort}h
✓ 代码已提交: {commit hash}
✓ 已推送到远端: {branch}
```
