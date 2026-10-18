---
name: hgj-tapd-timesheet-flow
version: 1.0.0
description: "TAPD 工时工作流 — 查询、补录、更新每日工时。Triggers on: 填工时, 补工时, TAPD工时, timesheet, 今日工时"
metadata:
  category: "workflow"
  requires:
    mcp: ["mcp-server-tapd"]
---

# TAPD 工时工作流

用于查询和补录 TAPD 工时。这个流程必须避免同一天重复创建工时。

## 强制流程

1. 确认 `workspace_id`、对象类型、对象 ID、日期、耗时、备注。
2. 调用 `get_timesheets` 查询同一 `owner + spentdate + entity_type + entity_id` 是否已有记录。
3. 如果已有记录，调用 `update_timesheets` 更新该记录。
4. 如果没有记录，调用 `add_timesheets` 新增。
5. 写入前必须让用户确认日期、对象、耗时和备注。

## 日期规则

- 用户说“今天”时，使用当前本地日期。
- 用户说“昨天/明天”等相对日期时，转换成明确的 `YYYY-MM-DD` 后再确认。
- 不要在没有确认日期时写入工时。

## 常用 MCP 工具

- `get_timesheets`
- `add_timesheets`
- `update_timesheets`
- `get_stories_or_tasks`
- `get_bug`

## 写操作规则

工时属于可审计数据，任何新增或更新都必须先确认。不要静默写入。
