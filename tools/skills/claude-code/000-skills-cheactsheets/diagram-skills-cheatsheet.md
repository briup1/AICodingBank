---
title: "Diagram Skills Cheatsheet"
date: 2026-06-21
category: tools
tags: []
status: published
description: "Notes on Diagram Skills Cheatsheet."
---

# diagram Skill 速查表

> 用自然语言描述需求，自动生成专业 PNG 图表，直接嵌入 Markdown 文档。
> 实际路径：`~/.claude/skills/diagram/`
> 版本：`1.7.0`

---

## 我想画… → 用这个图表

| 你想表达什么 | 首选图表 | 一句话判断 |
|-------------|---------|-----------|
| 工作流程、决策步骤 | **流程图（线性）** | 单路径、有先后 |
| 多入口/多出口的依赖关系 | **流程图（DAG）** | 节点互连、像网络 |
| 多角色/跨系统协作 | **泳道图** | 谁、在什么阶段、做什么 |
| API 调用或消息交互 | **时序图** | 对象之间按时间发消息 |
| 系统分层、技术栈 | **架构图** | 从上到下的层次 |
| 容器/系统边界 | **C4 图** | 强调边界和上下文 |
| 数据库表结构 | **ER 图** | 表与表之间的关系 |
| 类与继承/实现 | **类图** | 类结构、关系类型 |
| 状态机、生命周期 | **状态图** | 状态 + 触发条件 |
| Git 分支策略 | **Git Graph** | commit、分支、合并 |
| 选型决策、多分支逻辑 | **决策树** | 层层判断 |
| 知识结构、技能大纲 | **思维导图** | 中心主题向外展开 |
| 项目排期 | **甘特图** | 任务 + 时间轴 |
| 时间线/发展历程 | **时间线** | 按时间顺序的事件 |
| 组织架构 | **组织结构图** | 层级汇报关系 |
| 多维度评分对比 | **雷达图** | 3 个以上维度 |
| 矩阵型数值对比 | **热力图** | 行 × 列的数值 |
| 离散数值对比 | **柱状图** | 柱子比高低 |
| 时间序列趋势 | **折线图** | 走势、波动 |
| 占比构成 | **饼图 / 矩形树图** | 整体中各部分比例 |
| 流量/转化路径 | **桑基图 / 漏斗图** | 从上游到下游的流动 |
| 散点分布/聚类 | **散点图** | X-Y 坐标上的点 |
| 任务阶段管理 | **Kanban** | 待办/进行中/完成 |
| SWOT 分析 | **SWOT 图** | 四象限 |
| 根因分析 | **鱼骨图** | 多因素归因 |
| 用户体验旅程 | **旅程图** | 触点 + 情感曲线 |

---

## 图表类型全表

> 按「结构图 / 统计图 / 专用图」分类。布局方式决定你要手写坐标还是交给 ELKjs。

### 结构图

| 图表 | 表达什么 | 布局方式 | 生成脚本 | 专属规范 |
|-----|---------|---------|---------|---------|
| 流程图（线性）| 单路径流程、决策 | 手动布局 | `capture.py` | `references/diagrams/flowchart.md` |
| 流程图（DAG）| 多源汇聚、依赖关系 | ELKjs 自动 | `capture.py` | `references/diagrams/flowchart.md` |
| 泳道图 | 多角色协作 | 手动网格 | `capture.py` | `references/diagrams/swimlane.md` |
| 时序图 | API/消息交互 | 手动堆叠 | `capture.py` | `references/diagrams/sequence.md` |
| 架构图 | 系统分层、技术栈 | 手动层堆叠 | `capture.py` | `references/diagrams/architecture.md` |
| C4 图 | 容器/系统边界 | 手动分层 | `capture.py` | `references/diagrams/c4.md` |
| ER 图 | 数据库表结构 | ELKjs 自动 | `capture.py` | `references/diagrams/er.md` |
| 类图 | 类结构与关系 | ELKjs 自动 | `capture.py` | `references/diagrams/class.md` |
| 状态图 | 状态迁移 | ELKjs 自动 | `capture.py` | `references/diagrams/state.md` |
| 网络图 | 网络拓扑 | 手动分层 | `capture.py` | `references/diagrams/network.md` |
| 数据流图 | 数据管道 | 手动分层 | `capture.py` | `references/diagrams/dataflow.md` |
| 决策树 | 多分支决策 | 树形布局 | `capture.py` | `references/diagrams/decision-tree.md` |
| 思维导图 | 知识结构 | 双侧树形 | `capture.py` | `references/diagrams/mindmap.md` |
| 组织结构图 | 组织架构 | 树形布局 | `capture.py` | `references/diagrams/orgchart.md` |
| Git Graph | Git 分支工作流 | 横向分支线 | `capture.py` | `references/diagrams/git-graph.md` |
| 甘特图 | 项目排期 | 日期轴网格 | `capture.py` | `references/diagrams/gantt.md` |
| 时间线 | 发展历程 | 纵向列表 | `capture.py` | `references/diagrams/timeline.md` |
| Kanban | 任务看板 | 竖列卡片 | `capture.py` | `references/diagrams/kanban.md` |
| 旅程图 | 用户体验旅程 | 卡片横向 | `capture.py` | `references/diagrams/journey.md` |

### 统计图

| 图表 | 表达什么 | 生成脚本 | 专属规范 |
|-----|---------|---------|---------|
| 柱状图 | 离散对比 | `bridge.py` | `references/diagrams/bar-chart.md` |
| 折线图 | 趋势变化 | `bridge.py` | `references/diagrams/line-chart.md` |
| 柱线混合图 | 柱状 + 折线 | `bridge.py` | `references/diagrams/combo.md` |
| 饼图 | 占比构成 | `bridge.py` | `references/diagrams/pie-chart.md` |
| 雷达图 | 多维评估 | `bridge.py` | `references/diagrams/radar-chart.md` |
| 热力图 | 矩阵数据 | `bridge.py` | `references/diagrams/heatmap.md` |
| 散点图 | 分布/聚类 | `bridge.py` | `references/diagrams/scatter.md` |
| 桑基图 | 流量路径 | `bridge.py` | `references/diagrams/sankey.md` |
| 漏斗图 | 阶段转化 | `bridge.py` | `references/diagrams/funnel.md` |
| 瀑布图 | 累计增减 | `bridge.py` | `references/diagrams/waterfall.md` |
| 矩形树图 | 层级占比 | `bridge.py` | `references/diagrams/treemap.md` |

### 专用图

| 图表 | 表达什么 | 布局方式 | 生成脚本 | 专属规范 |
|-----|---------|---------|---------|---------|
| SWOT 图 | 优劣势分析 | 四象限卡片 | `capture.py` | `references/diagrams/swot.md` |
| 鱼骨图 | 根因分析 | 鱼骨骨架 | `capture.py` | `references/diagrams/fishbone.md` |
| 文氏图 | 集合关系 | 圆形交叠 | `capture.py` | `references/diagrams/venn.md` |

---

## 拓扑 → 图表决策

> 先判断内容是什么结构，再按读者和场景敲定最终图表。

| 内容结构 | 识别信号 | 可选图表 |
|---------|---------|---------|
| 线性序列 | A → B → C，单一路径 | 流程图（线性）、时序图、时间线、甘特图 |
| 多源汇聚 / DAG | 多入口、多出口、依赖 | 流程图（DAG）、数据流图、网络图、桑基图 |
| 分层堆叠 | 层级、技术栈、容器化 | 架构图、C4 图 |
| 角色协作 | 多角色/跨系统交互 | 泳道图、时序图、C4 |
| 实体关系 | 数据库表、对象关系 | ER 图、类图 |
| 状态迁移 | 状态机、生命周期 | 状态图、Git Graph |
| 树形结构 | 决策、组织、知识层级 | 决策树、组织结构图、思维导图 |
| 矩阵 / 多维评估 | 多维度对比、四象限 | 雷达图、热力图、SWOT、文氏图、矩形树图 |
| 数值比较 | 离散对比、占比、累计 | 柱状图、饼图、漏斗图、瀑布图 |
| 趋势变化 | 时间序列、走势 | 折线图、柱线混合图 |
| 分布关系 | 散点、聚类、相关性 | 散点图 |

### 同拓扑下的场景选择

| 判断维度 | 优先选择 |
|---------|---------|
| 读者是开发者 | 流程图 / 数据流图（信息密度高），不用桑基图 |
| 读者是评审/管理层 | 桑基图（视觉冲击）、C4 容器视图 |
| 投屏路演 | 桑基图、雷达图、时间线、思维导图 |
| 嵌入 Markdown 文档 | 流程图、ER 图、表格风结构图 |
| 强调动作顺序 | 时序图 > 流程图 |
| 强调容器化/边界 | C4 > 架构图 |
| 强调层叠关系 | 架构图 > C4 |
| 数据维度 ≥ 3 | 雷达图、热力图、散点图 |
| 多分支决策 | 决策树 > 流程图 |
| 单分支线性流程 | 流程图（线性） |

---

## 最小工作流：从一句话到 PNG

结构图和统计图的生成路径不同，别搞混。

### 结构图（HTML → PNG）

```bash
# 1. 创建 HTML 文件（内联 JS + CSS，无外部依赖）
# 2. 截图
python ~/.claude/skills/diagram/scripts/capture.py input.html output.png

# 输出自包含 HTML
python ~/.claude/skills/diagram/scripts/capture.py input.html output.html -f html
```

### 统计图（JSON → PNG）

```bash
# 1. 创建 JSON 配置
# 2. 渲染 + 截图
python ~/.claude/skills/diagram/scripts/bridge.py -c config.json -o output.png

# 输出自包含 HTML
python ~/.claude/skills/diagram/scripts/bridge.py -c config.json -o output.html -f html
```

### 生成步骤

```
1. 读专属规范 → 明确数据结构和布局规则
2. 定义数据（nodes / edges / steps / tables / series）
3. 计算布局 → ELKjs 自动 或 手动按领域规则
4. 渲染 SVG：背景层 → 连线层 → 节点层
5. 写入 HTML（内联 JS + CSS）
6. 用 capture.py / bridge.py 截图
```

> ⚠️ **禁止手动调用 Playwright MCP 截图。** 固化脚本已封装 HTTP 服务、ELKjs 等待、2x 输出、body 定位。

---

## 输出格式怎么选

| 格式 | 适用场景 | 生成方式 |
|-----|---------|---------|
| **PNG（默认）** | Markdown 文档配图 | `capture.py` / `bridge.py` |
| **HTML** | 富文档嵌入、交互展示、可二次编辑 | `capture.py -f html` / `bridge.py -f html` |
| **DSL** | 需要文本可 diff、GitHub/GitLab 原生渲染 | 直接输出 Mermaid 代码块 |

### DSL 支持情况

| 类型 | 是否支持 Mermaid | 不支持时的替代 |
|-----|----------------|--------------|
| flowchart / sequence / class / state / er | ✅ | — |
| gantt / mindmap / timeline / c4 / sankey / journey | ✅ | — |
| architecture / swimlane / network / dataflow / orgchart / decision-tree | ✅（flowchart + subgraph） | — |
| bar / line / pie | ✅ | — |
| radar / heatmap / scatter / funnel / waterfall | ❌ | 用 PNG |
| quadrant / gitGraph / block | ❌ | 用 PNG |

---

## 设计规范要点

### 常用配色

| 用途 | 色值 | 说明 |
|-----|------|------|
| 背景 | `#FFFFFF` | 画布白底 |
| 标题文字 | `#0F172A` | N-8 |
| 主文字 | `#1E293B` | N-7 |
| 次级文字/图例 | `#64748B` | N-6 |
| 主色/信息 | `#3B82F6` | C-1 Blue |
| 成功 | `#10B981` | C-2 Emerald |
| 警告 | `#F59E0B` | C-3 Amber |
| 错误 | `#F43F5E` | C-4 Rose |

主题色序列完整版见 `references/design-system.md`。

### 节点类型速查

| 类型 | 形状 | 用途 |
|-----|------|------|
| Process | 圆角矩形 | 处理步骤 |
| Decision | 菱形 | 判断分支 |
| Terminal Start/End | 跑道形 | 开始/结束 |
| Data Store | 圆柱 | 数据库 |
| External | 虚线矩形 | 外部系统 |
| Highlight | 实心矩形 | 关键节点 |
| Success / Error | 浅底矩形 | 成功/错误状态 |

### 关键间距

- 画布 padding：`24px`
- 纵向步骤间距：`36px`
- 含判断节点间距：`48px`
- 横向节点间距：`48px`
- 分支间距：`≥60px`
- 连线转角半径：`10px`

基础单位 `4px`，所有间距必须是 4 的倍数。

### 渲染顺序

```
1. 背景层（容器、泳道）
2. 连线层（箭头、关系线）
3. 节点层（矩形、文字、图标）
```

---

## 触发规则

### 触发词

- `/diagram`
- 自然语言：画图、画一个、生成图表、流程图、架构图、时序图、柱状图、对比图、关系图
- 任何涉及可视化展示的需求（流程、架构、数据对比、关系）都应触发

### 标题默认行为

| 调用场景 | 是否带标题 |
|---------|-----------|
| 用户直接请求画图 | ✅ 标题 + 副标题 |
| deep-research 报告配图 | ❌ 不带 |
| writing skill 嵌入文档配图 | ❌ 不带 |
| writing skill 路演/评审 HTML 配图 | ✅ 大字标题 + 副标题，其他按内容评估 |
| 用户说"画评审版/路演图" | 进入 review-grade 评估 |
| 用户说"不要标题" | ❌ 跳过 |

---

## 文件索引

| 用途 | 路径 |
|------|------|
| 主技能文档 | `~/.claude/skills/diagram/SKILL.md` |
| 公共设计规范 | `~/.claude/skills/diagram/references/design-system.md` |
| 公共工具函数 | `~/.claude/skills/diagram/references/diagram-utils.md` |
| 图表专属规范 | `~/.claude/skills/diagram/references/diagrams/<type>.md` |
| HTML 模板 | `~/.claude/skills/diagram/templates/html/<type>.html` |
| 公共 CSS | `~/.claude/skills/diagram/templates/html/lib/base.css` |
| 公共 JS | `~/.claude/skills/diagram/templates/html/lib/utils.js` |
| ELKjs | `~/.claude/skills/diagram/templates/html/lib/elk.bundled.js` |
| 结构图截图 | `~/.claude/skills/diagram/scripts/capture.py` |
| 统计图生成 | `~/.claude/skills/diagram/scripts/bridge.py` |

---

## 附录：Mermaid / Graphviz 转换

发现 ` ```mermaid ` 或 ` ```dot ` 代码块时，解析结构后用统一模板重新渲染：

| 源格式 | 映射目标 |
|--------|---------|
| `graph TD` / `flowchart` | flowchart 模板 |
| `sequenceDiagram` | sequence 模板 |
| `classDiagram` | class 模板 |
| `stateDiagram` | state 模板 |
| `erDiagram` | er 模板 |
| `gantt` | gantt 模板 |
| `pie` | pie 模板 |
| `journey` | journey 模板 |
| DOT `digraph` | flowchart / state / class |
| DOT `graph` | er / network |

> 不是调用 Mermaid/Graphviz 工具渲染，而是理解结构后用 design-system 统一风格重绘。

---

*文档生成时间：2026/06/13*  
*diagram 路径：`~/.claude/skills/diagram/`*
