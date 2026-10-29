---
name: hgj-tapd-bug-flow
version: 1.0.0
description: "TAPD 缺陷工作流 — 创建缺陷、补充复现步骤、关联需求。Triggers on: 创建缺陷, 提bug, TAPD bug, 缺陷复现, bug关联需求"
metadata:
  category: "workflow"
  requires:
    mcp: ["mcp-server-tapd"]
---

# TAPD 缺陷工作流

用于把问题描述整理成 TAPD 缺陷，并在确认后创建或更新。

## 创建缺陷前必须确认

- `workspace_id`
- 缺陷标题
- 复现步骤
- 实际结果
- 期望结果
- 严重程度：`fatal` / `serious` / `normal` / `prompt` / `advice`
- 优先级
- 处理人
- 关联需求 ID（如有）

## 推荐缺陷描述结构

```md
## 环境

## 复现步骤

## 实际结果

## 期望结果

## 附件/日志
```

## 常用 MCP 工具

- `create_bug`
- `update_bug`
- `get_bug`
- `get_related_bugs`
- `entity_relations`
- `get_entity_attachments`
- `get_image`

## 写操作规则

创建缺陷、更新缺陷、关联需求前必须先复述对象和字段，等待用户确认。
