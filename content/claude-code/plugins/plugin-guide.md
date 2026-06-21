---
title: "Plugin Guide"
date: 2026-06-21
category: claude-code
tags: []
status: published
description: "Notes on Plugin Guide."
---

# Claude Code 插件使用与开发指南

## 目录

- [什么是插件](#什么是插件)
- [插件 vs 独立配置](#插件-vs-独立配置)
- [插件结构](#插件结构)
- [使用现有插件](#使用现有插件)
- [开发新插件](#开发新插件)
- [插件最佳实践](#插件最佳实践)
- [常见问题](#常见问题)

---

## 什么是插件

**插件（Plugin）**是 Claude Code 中最高级别的扩展机制，用于将命令、代理、Skills、钩子、MCP、LSP 等能力打包、版本化、共享和分发。

### 核心理念

> **插件 = 一组可复用的 Claude Code 扩展能力集合**

一个插件可以包含：
- **斜杠命令（Slash Commands）** - 自定义命令快捷方式
- **子代理（Agents）** - 专用 AI 助手
- **Skills（能力）** - 教会 Claude 何时使用某种能力
- **Hooks（钩子）** - 事件驱动的自动化
- **MCP 服务器** - 外部工具/服务集成
- **LSP 服务器** - 代码智能增强

### 插件的核心目标

让 Claude Code 的能力像工具箱一样被复用，而不是每个项目重复配置。

---

## 插件 vs 独立配置

Claude Code 支持两种扩展方式：

| 方式 | 命令形式 | 适合场景 |
|------|----------|----------|
| **独立配置** (`.claude/`) | `/hello` | 个人使用、单项目、快速实验 |
| **插件** (`.claude-plugin/`) | `/plugin-name:hello` | 团队共享、跨项目、版本化 |

### 什么时候用独立配置？

- 只在当前项目使用
- 个人工作流定制
- 尚未稳定的实验性配置
- 想要简短命令名（如 `/review`）

### 什么时候用插件？

- 要在**多个项目复用**
- 要**分享给团队或社区**
- 需要**版本控制、升级、回滚**
- 计划通过市场分发
- 可以接受命名空间命令（避免冲突）

> **最佳实践**：先在 `.claude/` 中迭代 → 稳定后打包为插件

---

## 插件结构

### 最小结构

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json     # 插件清单（必需）
├── commands/           # 斜杠命令（可选）
├── agents/             # 子代理（可选）
├── skills/             # Skills（可选）
├── hooks/              # 钩子（可选）
├── .mcp.json           # MCP 配置（可选）
├── .lsp.json           # LSP 配置（可选）
└── README.md           # 说明文档（推荐）
```

### 重要规则

- `.claude-plugin/` 目录中**只能放 `plugin.json`**
- 其他目录必须在插件根目录
- 所有组件（命令、代理等）使用插件名作为命名空间

### plugin.json 清单文件

插件的"身份证"，定义插件的基本信息：

```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "email": "your@email.com"
  }
}
```

| 字段 | 作用 | 必需 |
|------|------|------|
| name | 唯一标识 + 命令命名空间 | 是 |
| description | 插件市场中展示的描述 | 是 |
| version | 语义化版本控制 | 否 |
| author | 作者信息 | 否 |

---

## 使用现有插件

### 插件管理命令

```bash
/plugin                  # 打开插件管理器
/plugin install          # 安装插件
/plugin uninstall        # 卸载插件
/plugin enable/disable   # 启用/禁用插件
/plugin marketplace add  # 添加插件市场
/plugin marketplace rm   # 移除插件市场
```

### 安装插件

1. **从官方市场安装**：
```bash
/plugin install plugin-name@claude-plugins-official
```

2. **从本地目录加载**（开发测试用）：
```bash
claude --plugin-dir ./my-plugin
```

3. **同时加载多个插件**：
```bash
claude --plugin-dir ./plugin-a --plugin-dir ./plugin-b
```

### 插件安装范围

| 范围 | 说明 | 推荐用途 |
|------|------|----------|
| 用户范围 | 仅你自己，所有项目 | 个人效率工具 |
| 项目范围 | 当前仓库，团队共享 | 团队工具 |
| 本地范围 | 当前仓库，仅你 | 临时测试 |

### 使用插件命令

插件命令使用 `插件名:命令名` 的格式：

```bash
# 使用 feature-dev 插件的命令
/feature-dev:Add user authentication

# 使用 code-review 插件的命令
/code-review

# 使用 plugin-dev 的命令
/plugin-dev:create-plugin
```

### 触发插件代理

插件中的代理会根据上下文自动触发：

```
"Launch code-explorer to trace how authentication works"
→ 自动触发 feature-dev 插件的 code-explorer 代理

"Review the error handling"
→ 自动触发 pr-review-toolkit 的 silent-failure-hunter 代理

"Simplify this code"
→ 自动触发 code-simplifier 代理
```

---

## 开发新插件

### 快速开始步骤

#### 1. 创建插件目录结构

```bash
mkdir my-plugin
cd my-plugin
mkdir .claude-plugin commands agents skills hooks
```

#### 2. 创建 plugin.json

```bash
cat > .claude-plugin/plugin.json << 'EOF'
{
  "name": "my-plugin",
  "description": "我的第一个 Claude Code 插件",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
EOF
```

#### 3. 创建斜杠命令（可选）

创建 `commands/hello.md`：

```markdown
---
description: 向用户打招呼
---

你好！欢迎使用 Claude Code。有什么我可以帮助你的吗？
```

对应命令：`/my-plugin:hello`

#### 4. 创建代理（可选）

创建 `agents/my-agent.md`：

```markdown
---
name: my-agent
description: 分析代码质量和提供改进建议
---

你是一个代码质量分析专家。分析提供的代码，识别潜在问题并提供改进建议。
```

#### 5. 本地测试

```bash
claude --plugin-dir ./my-plugin
```

### 插件组件详解

#### 1. 斜杠命令（Commands）

**定义方式**：
- 位于 `commands/` 目录
- 每个命令 = 一个 Markdown 文件
- 文件名 = 命令名

**命令内容示例**：

```markdown
---
description: Greet the user with a friendly message
---

Greet the user warmly and ask how you can help them today.
```

**使用参数**：
```markdown
Greet the user named "$ARGUMENTS" warmly.
```

调用：`/my-plugin:hello Alex`

#### 2. 子代理（Agents）

**定义方式**：
- 位于 `agents/` 目录
- YAML frontmatter + system prompt

**代理示例**：

```markdown
---
name: code-explorer
description: 深度分析现有代码库功能，追踪执行路径
model: haiku
color: blue
---

你是一个代码库探索专家...

# 职责
- 追踪代码执行流程
- 分析架构层次和模式
- 识别关键组件和依赖关系
```

#### 3. Skills（能力）

**定义方式**：
- 位于 `skills/` 目录
- 每个技能一个子目录
- 包含 SKILL.md 和相关资源

**目录结构**：
```
skills/my-skill/
├── SKILL.md              # 核心 API 文档
├── references/           # 详细参考文档
├── examples/             # 使用示例
└── scripts/              # 实用脚本
```

**SKILL.md 示例**：
```markdown
---
name: my-skill
description: 教会 Claude 如何执行特定任务
---

This skill should be used when...
```

#### 4. Hooks（钩子）

**定义方式**：
- 位于 `hooks/` 目录
- `hooks.json` 定义钩子配置
- 钩子脚本处理具体逻辑

**hooks.json 示例**：
```json
{
  "preToolUse": [
    {
      "pattern": "Write|Edit",
      "command": "${CLAUDE_PLUGIN_ROOT}/hooks/validate-write.sh"
    }
  ]
}
```

**可用钩子事件**：
- `PreToolUse` - 工具使用前
- `PostToolUse` - 工具使用后
- `Stop` - 会话停止
- `SessionStart` - 会话开始
- `SessionEnd` - 会话结束
- `UserPromptSubmit` - 用户提交提示

#### 5. MCP 集成

**配置方式**：
- 项目根目录创建 `.mcp.json`
- 或在 `plugin.json` 中配置

**.mcp.json 示例**：
```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server/dist/index.js"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

**服务器类型**：
- **stdio** - 本地进程通信
- **SSE** - HTTP Server-Sent Events
- **HTTP** - REST API
- **WebSocket** - 实时双向通信

### 高级开发技巧

#### 1. 使用 ${CLAUDE_PLUGIN_ROOT}

在所有配置中使用此变量确保路径可移植：

```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/scripts/myscript.sh"
}
```

#### 2. 插件设置模式

创建 `.claude/plugin-name.local.md` 存储用户配置：

```markdown
---
setting: true
---
apiKey: sk-xxxx
```

使用 bash 解析配置：

```bash
source ${CLAUDE_PLUGIN_ROOT}/scripts/parse-frontmatter.sh
get_setting "apiKey"
```

#### 3. 渐进式文档

为 Skills 使用三层文档结构：

1. **元数据**（始终加载）- 简洁描述 + 强触发器
2. **SKILL.md**（触发时加载）- 核心 API 参考
3. **参考资料**（按需加载）- 详细指南和示例

#### 4. AI 辅助代理生成

使用 `plugin-dev` 的 `agent-creator` 代理：

```
"Launch agent-creator to help me create a new testing agent"
```

### 插件发布

#### 1. 准备发布清单

- [ ] 所有组件测试通过
- [ ] README.md 完整
- [ ] version 更新
- [ ] 许可证文件

#### 2. 发布到市场

```bash
# 添加自定义市场
/plugin marketplace add https://github.com/your-org/marketplace

# 推送插件到市场仓库
git push
```

#### 3. 版本管理

使用语义化版本：
- **MAJOR.MINOR.PATCH**
- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的功能添加
- PATCH: 向后兼容的问题修复

---

## 插件最佳实践

### 1. 安全第一

- 在 hooks 中验证所有输入
- MCP 服务器使用 HTTPS/WSS
- 凭证通过环境变量传递
- 遵循最小权限原则

### 2. 可移植性

- 始终使用 `${CLAUDE_PLUGIN_ROOT}`
- 只使用相对路径
- 支持环境变量替换

### 3. 测试

- 部署前验证配置
- 用示例输入测试 hooks
- 使用调试模式 (`claude --debug`)

### 4. 文档

- 清晰的 README 文件
- 记录所有环境变量
- 提供使用示例
- 包含故障排除部分

### 5. 命名规范

- 插件名使用 kebab-case（如 `my-plugin`）
- 命令名描述性且简短
- 代理名清晰表达功能
- 避免与内置功能冲突

---

## 典型插件分类

### 1. 代码智能（LSP）

提供特定语言的代码智能：
- TypeScript、Python、Go、Rust 等
- 功能：跳转定义、引用查找、类型检查

需要本地安装对应语言服务器

### 2. 外部集成（MCP）

连接外部服务和 API：
- GitHub / GitLab
- Jira / Notion
- Slack / Figma
- Vercel / Supabase

本质：**插件 = MCP 服务器 + 配置**

### 3. 开发工作流

自动化开发流程：
- Git 提交、PR 管理
- 代码审查代理
- 构建和测试验证

### 4. 功能开发

特定领域的专业工具：
- 数据库操作
- API 开发
- UI 组件生成

---

## 常见问题

### Q: 如何调试插件？

```bash
# 启用调试模式
claude --debug --plugin-dir ./my-plugin

# 查看插件加载日志
# 检查 hooks 输出
```

### Q: 插件命令找不到？

1. 确认 plugin.json 中 name 正确
2. 检查命令文件在 commands/ 目录
3. 使用完整格式：`/plugin-name:command`
4. 确认插件已启用

### Q: 如何更新插件？

```bash
# 如果从市场安装
/plugin update plugin-name

# 本地开发：直接修改文件，重启 Claude Code
```

### Q: 插件与独立配置冲突？

插件配置优先生效。可以删除 `.claude/` 中的重复配置避免冲突。

### Q: 如何分享插件？

1. 发布到 Git 仓库
2. 添加到插件市场
3. 或直接分享目录，他人用 `--plugin-dir` 加载

### Q: 迁移 .claude/ 到插件？

| 原来 | 迁移后 |
|------|--------|
| `.claude/commands` | `plugin/commands` |
| `.claude/agents` | `plugin/agents` |
| `settings.json hooks` | `plugin/hooks/hooks.json` |

---

## 参考资源

### 官方文档

- [Claude Code 插件文档](https://www.runoob.com/claude-code/claude-code-plugins.html)
- [Claude Code GitHub](https://github.com/anthropics/claude-code)

### 示例插件

- **feature-dev** - 功能开发工作流
- **code-review** - 自动代码审查
- **plugin-dev** - 插件开发工具包
- **pr-review-toolkit** - PR 审查代理集合

### 本项目插件目录

```
claudecode_guide/plugin_guide/plugin_store/
├── code-review/          # 代码审查插件
├── code-simplifier/      # 代码简化插件
├── feature-dev/          # 功能开发插件
├── plugin-dev/           # 插件开发工具包
├── pr-review-toolkit/    # PR 审查工具包
└── superpowers/          # 超级能力插件
```

---

**最后更新**: 2026-03-03
