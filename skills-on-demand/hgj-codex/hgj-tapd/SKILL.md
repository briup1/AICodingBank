---
name: hgj-tapd
description: 当用户要求查询或维护 HGJ TAPD 的需求、缺陷、任务、迭代、评论、测试用例、关联关系、待办或工时时使用。
---

# HGJ TAPD

优先使用 TAPD MCP 工具；仅查看单个需求或缺陷时也可使用 `agent-tools tapd`。已有细分技能时按任务继续加载，例如 `hgj-tapd-bug-flow`、`hgj-tapd-story-flow`、`hgj-tapd-timesheet-flow`。

## 操作分级

| 类型 | 示例 | 规则 |
|---|---|---|
| 只读 | 查询需求、缺陷、评论、迭代、待办、附件 | 可直接执行，返回可点击对象链接 |
| 写入 | 创建或更新需求、缺陷、评论、工时、关联关系 | 先展示目标对象和字段，等待明确确认 |
| 状态流转 | 修改需求或缺陷状态 | 先查询工作流允许的流转路径 |

## 标准流程

```text
识别对象类型
  ↓
确定 workspace_id 和对象 ID
  ↓
只读查询并核对当前状态
  ↓
是否写入？── 是 ──> 展示变更摘要并等待确认
  │
  否
  ↓
返回结果、链接和剩余分页数量
```

## CLI 查询

```bash
agent-tools tapd show <bugId>
agent-tools tapd list [options]
agent-tools tapd story <storyId>
```

## 产品知识库关联

TAPD 主要提供进度信息；部分产品项目另有本机 Git 知识库，保存更完整的业务规则、验收标准、原型和需求演进。

遇到 TAPD 需求链接、需求 ID或“介绍/分析相关需求”时：

1. 查询 TAPD 当前详情、工作流状态和评论。
2. 读取 [产品知识库登记表](references/product-repositories.md)，按 `workspace_id` 判断是否关联本地仓库。
3. 命中登记项后，先读取目标仓库根 `AGENTS.md`，再执行只读解析脚本：

```bash
python3 ~/.codex/skills/hgj-tapd/scripts/resolve_product_requirement.py \
  --workspace-id <workspace_id> \
  --tapd-id <story_id> \
  [--local-requirement-id <TAPD描述中明确出现的R-* ID>]
```

4. 脚本先查隐藏映射；缓存未更新时，Agent 只能从刚查询的该条 TAPD 描述中提取明确的本地 `R-*` ID，并通过 `--local-requirement-id` 回退匹配。禁止脚本读取凭证，禁止按标题模糊猜测。
5. 映射成功后按脚本返回路径读取单条 PRD、周总览、根总览及 PRD 明确关联的需求；只有需要判断存量规则时才读取当前线上完整快照。
6. 回答必须分清：
   - **TAPD 当前进度**：状态、负责人、优先级、评论。
   - **产品业务事实**：产品仓库中的规则、边界和验收标准。
   - **冲突或待确认**：两侧不一致、映射失败或信息缺口。

默认只读访问产品仓库：不拉取远端、不切换分支、不修改文件、不执行仓库自动化写入。映射失败时不得根据标题猜测，也不得自动新增映射。

## MCP 规则

- 用户未给 `workspace_id` 时，先调用 `get_user_participant_projects`，过滤 `category=organization`。
- 使用 `custom_field_*` 前必须调用 `get_entity_custom_fields`。
- 查询需求/任务未指定 `limit` 时，同时查询总数并说明剩余数量。
- 更新需求状态前调用 `get_workflows_all_transitions`。
- 工时新增前，按 `owner + spentdate + entity_type + entity_id` 查询已有记录；存在则更新，不重复创建。
- 相对日期必须转换为明确的 `YYYY-MM-DD` 后再确认。

## 凭证异常

TAPD MCP 或 CLI 报认证问题时加载 `hgj-auth`。不要要求用户提供 Token；引导其运行：

```bash
hgj mcp status tapd --format json
hgj mcp configure tapd
hgj mcp doctor tapd --format json
```

## 触发示例

“查这个 TAPD 缺陷”“创建需求”“补昨天工时”“查询我的 TAPD 待办”。

## 反例

不得在未确认 workspace、对象、日期或变更字段时创建、更新或流转 TAPD 数据。
