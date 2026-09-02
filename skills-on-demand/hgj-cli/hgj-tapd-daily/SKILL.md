---
name: hgj-tapd-daily
version: 1.0.0
description: "TAPD 日常工作流 — 查看待办、整理今日任务、生成日报/周报。Triggers on: TAPD待办, 今日任务, 日报, 周报, 我的任务, todo"
metadata:
  category: "workflow"
  requires:
    mcp: ["mcp-server-tapd"]
---

# TAPD 日常工作流

用于查询用户 TAPD 待办、整理当日工作、生成日报或周报。

## 工作协议

1. 如果用户没有指定项目，先使用 TAPD MCP 查询用户参与项目，并过滤 `category=organization`。
2. 查询待办时明确对象类型：需求 `story`、任务 `task`、缺陷 `bug`。
3. 汇总时按项目、优先级、状态、到期时间组织，不要编造 TAPD 中不存在的字段。
4. 生成日报时区分：
   - 已完成：状态已结束或用户明确说明已完成。
   - 进行中：仍在处理的需求/任务/缺陷。
   - 风险/阻塞：状态、评论或用户描述里有明确证据。

## 常用 MCP 工具

- `get_user_participant_projects`
- `get_todo`
- `get_stories_or_tasks`
- `get_bug`
- `get_comments`

## 写操作规则

默认只读。只有用户明确要求“写入 TAPD / 发企微 / 添加评论”时，才调用写操作。写操作前必须复述目标项目、对象 ID、写入内容并等待确认。
