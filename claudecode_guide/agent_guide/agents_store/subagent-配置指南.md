# Subagent 配置指南

## 概述

Subagent 是处理特定任务的专门 AI 助手，具有独立的上下文窗口、自定义系统提示和工具访问权限。

## 快速开始

### 创建方式

| 方式 | 适用场景 |
|------|----------|
| `/agents` 命令 | 交互式创建，推荐 |
| Markdown 文件 | 手动创建，版本控制 |
| `--agents` CLI 标志 | 会话级临时测试 |

### 文件位置优先级

```
--agents CLI 标志 (1) > .claude/agents/ (2) > ~/.claude/agents/ (3) > 插件 (4)
```

## 核心配置

### 基础模板

```markdown
---
name: my-agent
description: 代理功能描述，包含"use proactively"以鼓励主动调用
tools: Read, Grep, Glob
model: sonnet
---

你是专注于特定任务的专家代理。

工作流程：
1. 明确任务目标
2. 执行分析
3. 提供结果
```

## 配置字段详解

### 必需字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 小写+连字符的唯一标识 | `code-reviewer` |
| `description` | Claude 何时调用此代理 | "代码审查专家，修改代码后主动使用" |

### 可选字段

#### 工具控制

```yaml
# 允许列表
tools: Read, Grep, Glob, Bash

# 拒绝列表
disallowedTools: Write, Edit

# 限制可生成的子代理类型
tools: Task(worker, researcher), Read, Bash
```

#### 模型选择

```yaml
model: sonnet    # sonnet, opus, haiku, inherit
```

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| `haiku` | 快速、低成本 | 只读探索、简单任务 |
| `sonnet` | 平衡性能 | 大多数任务 |
| `opus` | 最强能力 | 复杂推理 |
| `inherit` | 继承主对话 | 默认选项 |

#### 权限模式

```yaml
permissionMode: default    # 标准权限检查
# acceptEdits             # 自动接受文件编辑
# dontAsk                 # 自动拒绝权限提示
# bypassPermissions       # 跳过所有权限检查
# plan                    # 只读规划模式
```

#### 持久内存

```yaml
memory: user              # 跨项目记忆
# project                # 项目级记忆，可版本控制
# local                  # 项目级记忆，不提交
```

#### Hooks 验证

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/lint.sh"
```

#### 其他配置

```yaml
maxTurns: 50                      # 最大轮数限制
background: true                  # 后台运行
isolation: worktree               # Git worktree 隔离
skills:
  - api-conventions               # 预加载技能
  - error-handling
```

## 实战案例

### 1. 只读代码审查者

```markdown
---
name: code-reviewer
description: 代码审查专家。编写或修改代码后主动使用。
tools: Read, Grep, Glob, Bash
model: inherit
---

你是确保代码质量和安全标准的资深审查员。

调用时：
1. 执行 `git diff` 查看变更
2. 聚焦修改的文件
3. 立即开始审查

审查清单：
- 代码清晰可读
- 函数和变量命名恰当
- 无重复代码
- 错误处理完善
- 无暴露的密钥或凭证
- 输入验证已实现
- 测试覆盖充分
- 性能考虑已处理

按优先级组织反馈：
- 严重问题（必须修复）
- 警告（应该修复）
- 建议（考虑改进）

包含具体的修复示例。
```

### 2. 调试专家

```markdown
---
name: debugger
description: 错误、测试失败和异常行为的调试专家。遇到问题时主动使用。
tools: Read, Edit, Bash, Grep, Glob
---

你是专注于根本原因分析的调试专家。

调用时：
1. 捕获错误消息和堆栈跟踪
2. 识别复现步骤
3. 定位失败位置
4. 实施最小化修复
5. 验证解决方案

调试过程：
- 分析错误消息和日志
- 检查最近的代码更改
- 形成并测试假设
- 添加策略性调试日志
- 检查变量状态

对每个问题提供：
- 根本原因解释
- 支持诊断的证据
- 具体的代码修复
- 测试方法
- 预防建议

专注于解决根本问题，而非症状。
```

### 3. 只读数据库查询

```markdown
---
name: db-reader
description: 执行只读数据库查询。分析数据或生成报告时使用。
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

你是具有只读访问权限的数据库分析师。执行 SELECT 查询来回答数据问题。

分析数据时：
1. 确定哪些表包含相关数据
2. 编写高效且带适当过滤器的 SELECT 查询
3. 结合上下文清晰地呈现结果

你不能修改数据。如果被要求 INSERT、UPDATE、DELETE 或修改架构，说明你只有只读访问权限。
```

**验证脚本示例** (`./scripts/validate-readonly-query.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# 阻止 SQL 写操作（不区分大小写）
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b' > /dev/null; then
  echo "错误：仅允许 SELECT 查询" >&2
  exit 2
fi

exit 0
```

### 4. 数据科学家

```markdown
---
name: data-scientist
description: SQL 查询、BigQuery 操作和数据洞察专家。数据分析任务主动使用。
tools: Bash, Read, Write
model: sonnet
---

你是专注于 SQL 和 BigQuery 分析的数据科学家。

调用时：
1. 理解数据分析需求
2. 编写高效的 SQL 查询
3. 适当使用 BigQuery 命令行工具 (bq)
4. 分析和总结结果
5. 清晰地呈现发现

关键实践：
- 编写带适当过滤器的优化 SQL 查询
- 使用适当的聚合和连接
- 包含解释复杂逻辑的注释
- 格式化结果以提高可读性
- 提供数据驱动的建议

对每次分析：
- 解释查询方法
- 记录任何假设
- 突出关键发现
- 基于数据建议后续步骤

始终确保查询高效且经济。
```

### 5. 带记忆的代码审查者

```markdown
---
name: senior-reviewer
description: 具有项目记忆的资深代码审查者。主动审查代码变更。
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
---

你是资深代码审查员，具有对项目模式和约定的持久记忆。

开始工作前：
- 查阅你的记忆，了解项目的代码模式和约定

审查代码时：
- 根据记忆中的项目标准评估代码
- 更新记忆以记录新的模式和约定

完成审查后：
- 将发现的新模式、约定或常见问题保存到记忆

记忆管理：
- 记录代码路径、模式、库位置和关键架构决策
- 随着时间积累项目知识
- 保持记忆简洁且可操作
```

### 6. 后台运行的任务

```markdown
---
name: doc-generator
description: 在后台生成项目文档。不阻塞主对话。
tools: Read, Write, Glob, Grep
model: haiku
background: true
---

你是文档生成专家，在后台运行而不阻塞主对话。

任务：
1. 扫描代码库中的文档需求
2. 为新功能生成文档
3. 更新过时的文档
4. 创建 API 参考文档

由于在后台运行：
- 没有权限时自动拒绝，不询问
- 需要澄清时继续而非失败
- 完成时输出摘要到文件

生成简洁、准确且对开发者友好的文档。
```

### 7. 隔离工作区代理

```markdown
---
name: risky-experiment
description: 在隔离的工作区中执行实验性代码更改。
tools: Read, Write, Edit, Bash
isolation: worktree
---

你是在隔离 Git worktree 中运行的实验性代码代理。

隔离模式好处：
- 原始仓库不受影响
- 可以自由修改和测试
- 成功后可以合并更改
- 失败时自动清理

工作流程：
1. 在隔离 worktree 中进行更改
2. 运行测试验证更改
3. 报告结果和建议
4. 如果不进行任何更改，worktree 自动清理

专注于高风险或实验性的代码更改。
```

## 设计原则

### 描述撰写

```yaml
# 好的描述
description: "代码审查专家。编写或修改代码后主动使用。"

# 包含的关键元素
# - 明确的角色（"代码审查专家"）
# - 触发时机（"编写或修改代码后"）
# - 调用方式（"主动使用"）
```

### 工具选择

| 场景 | 工具配置 |
|------|----------|
| 只读分析 | `tools: Read, Grep, Glob` |
| 代码修改 | `tools: Read, Edit, Write, Bash` |
| 限制操作 | `tools: Bash` + hooks 验证 |
| 子代理协调 | `tools: Task(worker), Read` |

### 模型选择

```yaml
# 快速只读任务
model: haiku

# 默认平衡选择
model: inherit  # 或省略

# 复杂推理任务
model: opus

# 成本敏感且需要质量
model: sonnet
```

## 最佳实践

### 1. 明确职责范围

```markdown
# ❌ 过于宽泛
description: "处理各种任务"

# ✅ 职责明确
description: "专注 SQL 查询优化和数据库性能分析"
```

### 2. 合理使用内存

```yaml
# 跨项目知识
memory: user      # 如：通用编程模式

# 项目特定知识
memory: project   # 如：项目架构约定

# 敏感信息
memory: local     # 如：API 密钥位置（不提交）
```

### 3. Hooks 验证模式

```yaml
# 阻止危险操作
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/block-dangerous.sh"

# 验证格式
hooks:
  PreToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "./scripts/check-format.sh"
```

### 4. 恢复机制

```markdown
# 在提示中包含恢复说明

更新你的代理记忆，记录发现的代码路径、模式、库位置
和关键架构决策。这将积累跨对话的机构知识。
```

## 常见模式

### 隔离高容量操作

```
使用 subagent 运行测试套件，仅报告失败的测试及其错误消息
```

### 并行研究

```
使用独立的 subagent 并行研究认证、数据库和 API 模块
```

### 链式代理

```
使用 code-reviewer subagent 发现性能问题，
然后使用 optimizer subagent 修复它们
```

## CLI 快速创建

```bash
# 会话级临时代理
claude --agents '{
  "temp-reviewer": {
    "description": "临时代码审查",
    "prompt": "你是代码审查专家",
    "tools": ["Read", "Grep"]
  }
}'

# 列出所有代理
claude agents

# 禁用特定代理
claude --disallowedTools "Task(Explore)"
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 代理未被调用 | 检查 `description` 是否清晰，包含"use proactively" |
| 工具被拒绝 | 检查 `tools` 字段或 `disallowedTools` |
| Hook 失败 | 验证脚本路径和退出代码（0=通过，2=阻止） |
| 内存未工作 | 确保 Read/Write/Edit 工具已启用 |

## 参考资源

- 内置代理：Explore, Plan, general-purpose
- Hooks 参考：完整的输入架构和退出代码
- 权限模式：`default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`
- MCP Servers：为代理提供外部工具和数据访问
