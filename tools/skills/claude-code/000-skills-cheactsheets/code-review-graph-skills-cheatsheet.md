---
title: "Code Review Graph Skills Cheatsheet"
date: 2026-06-21
category: tools
tags: []
status: published
description: "Notes on Code Review Graph Skills Cheatsheet."
---

# code-review-graph Skill 速查表

> 本文档汇总了 code-review-graph 包中所有可用的 skill 与 MCP workflow，围绕"构建知识图谱 → 审查 / 调试 / 探索 / 重构 / 合并前检查 / 架构文档 / 新人上手"工作流组织。
>
> **核心定位：把 code-review-graph 当作一个帮你快速获取代码上下文的 Agent 来使用** —— 它先构建代码的结构图谱，再用最小的 token 帮你定位相关函数、调用链、影响面和测试缺口，避免在大型代码库里盲目翻文件。
>
> **两种入口：**
> - 本地 Skill（`~/.claude/skills/code-review-graph/[skill-name]/SKILL.md`）：通过 `/skill-name` 调用
> - MCP Workflow（MCP server 注册 prompts）：通过 `/code-review-graph:workflow_name` 调用

---

## 快速索引（按场景）

| 场景 | 推荐命令 | 类型 | 备注 |
|---|---|---|---|
| 初始化 / 更新知识图谱 | `/build-graph` | Skill | 所有其他命令的前置依赖，先执行 |
| 审查最近一次提交后的改动 | `/review-delta` | Skill | 只关注 changed + blast radius，最省 token |
| 完整 PR / 分支审查 | `/review-pr` | Skill | 可传 PR 编号或分支名，输出结构化审查报告 |
| 通用结构化代码审查 | `/review-changes` | Skill | 按高/中/低风险分级，给出合并建议 |
| 调试 Bug / 追踪调用链 | `/debug-issue` 或 `/code-review-graph:debug_issue` | Skill / MCP | 从报错出发，用图谱定位根因 |
| 探索项目结构 / 新人上手 | `/explore-codebase` | Skill | 从宏观架构逐步深入到具体函数 |
| 安全重构 / 重命名 / 删死代码 | `/refactor-safely` | Skill | 先预览影响面，再应用改动 |
| PR 合并前综合检查 | `/code-review-graph:pre_merge_check` | MCP | 输出 GO/NO-GO 建议 |
| 生成架构文档 / Mermaid 图 | `/code-review-graph:architecture_map` | MCP | 生成架构图与模块耦合说明 |
| 新开发者项目导览 | `/code-review-graph:onboard_developer` | MCP | 统计 + 架构 + 关键执行流 |

---

## 核心原则

### 1. 先建图，后使用
所有 code-review-graph 的 skill 都依赖本地 SQLite 知识图谱（`.code-review-graph/graph.db`）。
- **首次使用**：运行 `/build-graph` 或 `/build-graph full`
- **日常更新**：文件保存 / 提交时 hooks 会自动增量更新，手动重建很少需要
- **怀疑不同步时**：再运行一次 `/build-graph`

### 2. Token 效率优先
每个 skill 的 SKILL.md 都强调：
- 始终先调 `get_minimal_context(task="...")`
- 默认使用 `detail_level="minimal"`，不够再升级到 "standard"
- 目标：≤5 次工具调用，≤800 输出 tokens

### 3. 爆炸半径（Blast Radius）是核心
所有审查/调试/重构 skill 都会用图谱计算"改动会影响哪些函数/文件/执行流"，避免你通读整个代码库。

---

## 一、图谱构建

### `/build-graph [full]`
**功能：** 构建或增量更新持久化的代码知识图谱。

**使用时机：**
- 首次在新仓库使用 code-review-graph
- 大规模重构、切换分支后怀疑图谱不同步
- 图谱自动 hooks 未生效或结果明显缺失

**参数：**
| 参数 | 含义 |
|---|---|
| `full` | 强制全量重建，通常不需要 |

**注意：**
- 图谱存在 `.code-review-graph/graph.db`（SQLite）
- 二进制文件、生成文件、`.code-review-graphignore` 中匹配的文件会被跳过
- 支持语言：Python、TypeScript/JavaScript、Vue、Go、Rust、Java、Scala、C#、Ruby、Kotlin、Swift、PHP、Solidity、C/C++ 等

---

## 二、代码审查

### `/review-delta [file or function name]`
**功能：** 只审查自上次提交以来的改动及其爆炸半径，token 最省。

**使用时机：**
- "review my changes"
- "看看我改了什么"
- 提交前快速自检

**输出：**
- Summary（一句话概述）
- Risk level（Low / Medium / High）
- Issues found（bug、风格问题、缺失测试）
- Blast radius（受影响的文件/函数）
- Recommendations（可执行建议）

**优点：**
- 只发送 changed + 2-hop 邻居到模型，比全库审查少 5-10 倍 token
- 自动识别爆炸半径，无需手动翻文件
- 自动标出未测试函数

---

### `/review-pr [PR number or branch name]`
**功能：** 对 PR 或分支 diff 做全面审查，输出带爆炸半径分析的结构化报告。

**使用时机：**
- "review this PR"
- "review branch xxx"
- 提交 PR 前或 review 他人 PR

**不传参数时：** 自动对比当前分支与 `main/master`
**传 PR 编号/分支名时：** 用 `git diff main...<branch>` 获取改动范围

**输出格式：**
- PR 概述
- 整体风险评估
- 逐文件审查
- 缺失测试清单
- 可执行建议

**注意：**
- 大型 PR 优先关注影响面最大的文件（dependents 最多）
- 检查重命名/移动的函数是否更新了所有调用方

---

### `/review-changes`
**功能：** 基于变更检测与影响分析，做风险分级的结构化代码审查。

**使用时机：**
- 需要明确的"高/中/低"风险评级
- 需要合并建议（merge recommendation）
- 想系统检查测试覆盖和潜在问题

**审查流程：**
1. `detect_changes_tool` 获取风险评分
2. `get_affected_flows_tool` 找出受影响执行路径
3. 对每个高风险函数用 `query_graph_tool(pattern="tests_for")` 检查测试覆盖
4. `get_impact_radius_tool` 评估爆炸半径
5. 对未覆盖改动提出具体测试建议

**输出分组：**
- 改了什么、为什么重要
- 测试覆盖状态
- 改进建议
- 整体合并建议

---

### 审查类 Skill 对比

| 你想做的事 | 用哪个 |
|---|---|
| "看看我本地改了什么" | `/review-delta` |
| "review 这个 PR / 分支" | `/review-pr` |
| "给我风险分级和合并建议" | `/review-changes` |
| "提交前快速自查" | `/review-delta` |
| "完整 PR 报告" | `/review-pr` |

---

## 三、调试与排错

### `/debug-issue`
**功能：** 用知识图谱系统化追踪和调试问题。

**使用时机：**
- "debug this"
- "why is this broken"
- "root cause analysis"
- 报错、异常行为、"昨天还好好的"

**调试流程：**
1. `semantic_search_nodes_tool`：定位与问题相关的函数/类
2. `query_graph_tool(callers_of / callees_of)`：向上/向下追踪调用链
3. `get_flow`：查看可疑区域的完整执行路径
4. `detect_changes_tool`：检查最近变更是否是诱因
5. `get_impact_radius_tool`：确认影响面

**关键原则：**
- callers 和 callees 两边都要看
- 优先怀疑最近变更
- 通过 affected flows 找到触发 bug 的入口点

---

## 四、项目探索

### `/explore-codebase`
**功能：** 用知识图谱理解和导航项目结构。

**使用时机：**
- 新人上手
- 切入不熟悉的模块
- "这个项目是怎么组织的"
- "找到处理 XXX 的代码"

**探索流程（从宏观到微观）：**
1. `list_graph_stats_tool`：整体规模（文件、节点、边、语言）
2. `get_architecture_overview_tool`：高层社区/模块结构
3. `list_communities_tool` + `get_community_tool`：逐个模块深入了解
4. `semantic_search_nodes_tool`：定位具体函数或类
5. `query_graph_tool`（`callers_of` / `callees_of` / `imports_of`）：追踪关系
6. `list_flows` + `get_flow`：理解执行路径

**技巧：**
- 先用 `children_of` 看一个文件里的所有函数/类
- 用 `find_large_functions` 识别复杂代码

---

## 五、安全重构

### `/refactor-safely`
**功能：** 基于依赖分析规划和执行安全重构。

**使用时机：**
- 准备重命名函数/类
- 想删除未引用代码
- 大规模重构前评估影响面
- "这个重构安全吗"

**工作流程：**
1. `refactor_tool(mode="suggest")`：社区驱动的重构建议
2. `refactor_tool(mode="dead_code")`：查找未引用代码
3. `refactor_tool(mode="rename")`：预览重命名影响
4. `apply_refactor_tool(refactor_id)`：应用重命名
5. `detect_changes_tool`：验证重构后的影响

**安全检查清单：**
- 重命名前务必 preview
- 大型重构前检查 `get_impact_radius_tool`
- 用 `get_affected_flows_tool` 确保关键路径没断
- 用 `find_large_functions` 找可拆分的复杂函数

---

## 五、MCP Workflow（通过 `/code-review-graph:xxx` 调用）

除了本地 skill 文件外，code-review-graph 的 MCP server 还注册了 5 个 prompt workflows。其中 `review_changes` 和 `debug_issue` 与本地 skill 功能重叠，`pre_merge_check`、`architecture_map`、`onboard_developer` 只在 MCP workflow 层提供。

### `/code-review-graph:review_changes [base]`
**功能：** 与本地 `/review-changes` 对应，预提交审查工作流。

**流程：**
1. `get_minimal_context(task="review changes against {base}")`
2. 风险低：只调 `detect_changes(detail_level="minimal")`
3. 风险中/高：
   - `detect_changes(detail_level="standard")`
   - 对每个高风险函数调 `query_graph(pattern="callers_of")`
   - 改动函数 >3 个时才调 `get_affected_flows`
4. 总结风险等级、改动内容、测试缺口、改进建议

**参数：** `base`（默认 `HEAD~1`）

**与本地 `/review-changes` 的区别：** MCP prompt 更严格地按风险分级决定调用深度，默认不拉源码片段。

---

### `/code-review-graph:debug_issue [description]`
**功能：** 与本地 `/debug-issue` 对应，引导式调试工作流。

**流程：**
1. `get_minimal_context(task="debug: {description}")`
2. `semantic_search_nodes(query=关键词, limit=5)`
3. 对前 1-2 个结果调 `query_graph(pattern="callers_of")`
4. 如涉及执行流：调 `get_flow(最相关的 flow)`
5. 只有需要追踪特定改动的爆炸半径时，才调 `get_review_context` 或 `get_impact_radius`

**参数：** `description`（问题描述）

**与本地 `/debug-issue` 的区别：** MCP prompt 明确限制只追踪最相关的 1-2 个结果和 1 个执行流，更克制。

---

### `/code-review-graph:pre_merge_check [base]`
**功能：** PR 合并前综合检查，输出 GO/NO-GO 建议。

**流程：**
1. `get_minimal_context(task="pre-merge check")`
2. `detect_changes(detail_level="minimal")` 获取风险评分和测试缺口
3. 风险 > 0.4：调 `get_affected_flows(detail_level="minimal")`
4. 有测试缺口：对最多 3 个未测试函数调 `query_graph(pattern="tests_for")`
5. `refactor_tool(mode="dead_code")` 检查新增死代码
6. 风险 > 0.7：才调 `find_large_functions` 或 `get_impact_radius`
7. 输出：**GO/NO-GO 建议** + 一句话理由 + 必须跟进项

**参数：** `base`（默认 `HEAD~1`）

**使用时机：**
- 合并 PR 前最后把关
- "is this ready to merge"
- 需要自动化的合并就绪报告

---

### `/code-review-graph:architecture_map`
**功能：** 生成架构文档，输出带 Mermaid 图的结构说明。

**流程：**
1. `get_minimal_context(task="map architecture")`
2. `get_architecture_overview(detail_level="minimal")` 社区耦合摘要
3. `list_flows(detail_level="minimal")` 关键执行流名称 + 关键性评分
4. 只对 1-2 个最相关的社区用 `get_community(detail_level="standard")` 深入
5. 产出简明的 **Mermaid 架构图**（社区为框，关键流为箭头）

**参数：** 无

**使用时机：**
- 需要写 ARCHITECTURE.md 或技术文档
- "draw the architecture"
- 新成员需要 30 秒项目结构图

---

### `/code-review-graph:onboard_developer`
**功能：** 新开发者上手导览。

**流程：**
1. `get_minimal_context(task="onboard developer")`
2. `list_graph_stats()` 技术栈概览（文件数、节点数、边数、语言）
3. `get_architecture_overview(detail_level="minimal")` 30 秒心智模型
4. `list_communities(detail_level="minimal")` 模块表格（名称 + 大小）
5. `list_flows(detail_level="minimal")` 突出前 3 个关键执行流
6. 只有开发者询问时才深入具体社区/执行流

**参数：** 无

**使用时机：**
- 新人加入项目
- "how is this project organized"
- 需要快速建立项目心智模型

---

## 六、Skill vs MCP Workflow 对照

| 功能 | 本地 Skill | MCP Workflow | 推荐用哪个 |
|---|---|---|---|
| 构建图谱 | `/build-graph` | 无 | `/build-graph` |
| 审查当前 diff | `/review-delta` | 无 | `/review-delta` |
| 审查 PR | `/review-pr` | 无 | `/review-pr` |
| 结构化风险审查 | `/review-changes` | `/code-review-graph:review_changes` | 本地 skill 输出更完整 |
| 调试 | `/debug-issue` | `/code-review-graph:debug_issue` | 本地 skill 步骤更全 |
| 探索代码库 | `/explore-codebase` | 无 | `/explore-codebase` |
| 安全重构 | `/refactor-safely` | 无 | `/refactor-safely` |
| 合并前检查 | 无 | `/code-review-graph:pre_merge_check` | **只能用 MCP** |
| 架构图 | 无 | `/code-review-graph:architecture_map` | **只能用 MCP** |
| 新人上手 | `/explore-codebase` | `/code-review-graph:onboard_developer` | MCP 输出更聚焦 |

---

### 首次使用
```
/build-graph
```

### 日常开发
```
改完代码 → /review-delta
或        → /review-changes
```

### 提 PR 前
```
/review-pr [branch-name]
```

### 遇到 Bug
```
/debug-issue
```

### 准备重构
```
/refactor-safely
```

### 新接手项目
```
/explore-codebase
```

---

## 七、何时图谱帮不上忙 / 注意事项

1. **首次使用前必须先 `/build-graph`**，否则所有 skill 都会缺少上下文。
2. **单文件微小改动**可能反而比直接读文件更费 token，因为图谱要返回结构元数据。
3. **Flow detection 对非 Python 语言较弱**（JS/Go 入口识别不够稳定）。
4. **Impact radius 是保守估计**，会故意多标一些可能受影响的文件，宁可误报也不漏报。
5. **图谱不是 git 替代品**，重大分支切换后建议重新 build。
6. **支持语言有限制**，自定义语言需要配置 `.code-review-graph/languages.toml`。

---

## 八、CLAUDE.md 路由规则示例

建议在项目 `CLAUDE.md` 中添加以下内容，让 Claude Code 自动路由到对应 skill：

```markdown
## Skill routing for code-review-graph

- 构建/更新代码知识图谱 → invoke /build-graph
- 审查本地 diff → invoke /review-delta
- 审查 PR 或分支 → invoke /review-pr
- 需要风险分级和合并建议 → invoke /review-changes
- 调试 Bug / 根因分析 → invoke /debug-issue 或 /code-review-graph:debug_issue
- 探索项目结构 / 新人上手 → invoke /explore-codebase 或 /code-review-graph:onboard_developer
- 重构前影响分析 → invoke /refactor-safely
- PR 合并前最后把关 → invoke /code-review-graph:pre_merge_check
- 生成架构文档 / Mermaid 图 → invoke /code-review-graph:architecture_map
```

---

## 九、底层 MCP 工具速查

| MCP 工具 | 用途 |
|---|---|
| `build_or_update_graph_tool` | 构建 / 增量更新知识图谱 |
| `detect_changes_tool` | 变更风险分析 |
| `get_affected_flows_tool` | 受影响的执行路径 |
| `get_impact_radius_tool` | 爆炸半径分析 |
| `get_review_context_tool` | 带源码片段的审查上下文 |
| `get_minimal_context_tool` | 任何任务开始前先调用，节省 token |
| `query_graph_tool` | 调用关系、依赖、测试覆盖查询 |
| `semantic_search_nodes_tool` | 语义搜索函数/类 |
| `refactor_tool` | 重构建议 / 死代码 / 重命名预览 |
| `apply_refactor_tool` | 应用重命名 |
| `list_communities_tool` / `get_community_tool` | 模块社区分析 |
| `list_flows` / `get_flow` | 执行路径分析 |
| `find_large_functions` | 识别复杂函数 |

---

*文档生成时间：2026/06/13*  
*code-review-graph 路径：`~/.claude/skills/code-review-graph/`*  
*本包共 7 个本地 skill：`build-graph`、`debug-issue`、`explore-codebase`、`refactor-safely`、`review-changes`、`review-delta`、`review-pr`*  
*MCP server 额外提供 5 个 workflow prompt：`review_changes`、`architecture_map`、`debug_issue`、`onboard_developer`、`pre_merge_check`*
