# Claude 官方 Plugins 速查表

> 生成于 2026/06/13 | 覆盖 `claude-plugins-official/plugins` 中的官方插件、独立 skill 与 LSP 支持包。
> 实际路径：`claude-plugins-official/plugins/[plugin-name]/`

---

## 快速索引（按场景）

| 场景 | 推荐 Plugin / 命令 | 备注 |
|---|---|---|
| 🚀 开发新功能 | `/feature-dev` | 推荐入口，先探索/提问/设计，再实现 |
| 🧱 创建 Agent SDK 应用 | `/new-sdk-app` | Python / TypeScript Agent SDK 脚手架与验证 |
| ✅ 自动 PR 审查 | `/code-review` | 多 agent 并行审查，过滤低置信度问题 |
| 🔍 深度 PR 审查 | `/review-pr` | 评论、测试、错误处理、类型设计、代码质量 |
| 🧹 简化代码 | `code-simplifier` agent | 保持行为不变，只改善清晰度和一致性 |
| 🔐 安全审查 | `security-guidance` | hooks + LLM diff review + commit review |
| 📝 自动提交 | `/commit` | 分析 diff，生成 commit message 并提交 |
| 📤 提交并开 PR | `/commit-push-pr` | commit + push + create PR |
| 🧭 清理 gone 分支 | `/clean_gone` | 清理远端已删除的本地分支 |
| 🏚️ 遗留系统现代化 | `/modernize-preflight` → `/modernize-*` | 一整套现代化流程，不是一键重写 |
| 🗺️ 生成系统拓扑 | `/modernize-map` | 调用图、数据流、入口点、互动拓扑图 |
| 📜 抽取业务规则 | `/modernize-extract-rules` | 生成 Given/When/Then Rule Cards |
| 🧪 等价迁移模块 | `/modernize-transform` | 单模块 strangler-fig 重写 + 等价测试 |
| 🧠 推荐 Claude 自动化 | `claude-automation-recommender` | 分析项目后推荐 hooks、skills、MCP、agents |
| 📚 维护 CLAUDE.md | `claude-md-improver` / `/revise-claude-md` | 项目记忆维护与会话经验沉淀 |
| 🪝 创建自定义 hook | `/hookify` | 用自然语言生成 `.claude/hookify.*.local.md` 规则 |
| 🧩 创建插件 | `/create-plugin` | plugin-dev 的 8 阶段插件创建流程 |
| 🛠️ 构建 MCP server | `build-mcp-server` skill | 设计 remote HTTP / MCPB / stdio / MCP app |
| 🔌 创建 MCP tunnel | `/create-docker-mcp-tunnel` | 私有 MCP server 通过 Anthropic tunnel 暴露给 Claude |
| 🎨 前端设计实现 | `frontend-design` skill | 高质量 UI/UX，避免模板化 AI 风格 |
| 🕹️ 交互式 HTML 工具 | `playground` skill | 单文件 playground，控件 + 预览 + prompt 输出 |
| 🧮 竞赛数学 | `math-olympiad` skill | 解题 + 对抗式 proof verification |
| 🔁 自循环迭代开发 | `/ralph-loop` | Stop hook 重复同一 prompt，适合可验证重复任务 |
| 📊 使用成本报告 | `session-report` skill | 从 Claude transcripts 生成 token/cache HTML 报告 |
| 💡 解释型输出 | `explanatory-output-style` | SessionStart 注入解释型风格，会增加 token 成本 |
| 🎓 学习模式 | `learning-output-style` | 让用户参与关键代码片段编写 |
| 🧑‍💻 多语言代码智能 | `*-lsp` | TypeScript、Python、Go、Rust、Java、C/C++ 等 LSP |
| 🔧 插件开发参考 | `example-plugin` | 官方示例插件结构 |
| 🧰 创建/优化 Skill | `skill-creator` | 写 skill、跑 eval、优化触发描述 |
| 📟 M5Stack/Cardputer | `/maker-setup` | Code-with-Claude Makers 硬件套件刷机与 app 安装 |

---

## 目录

- [一、日常开发与 Git 工作流](#一日常开发与-git-工作流)
- [二、代码审查、质量与安全](#二代码审查质量与安全)
- [三、遗留系统现代化](#三遗留系统现代化)
- [四、Claude Code 配置、记忆与 Hooks](#四claude-code-配置记忆与-hooks)
- [五、插件、Skill 与 MCP 开发](#五插件skill-与-mcp-开发)
- [六、领域型插件](#六领域型插件)
- [七、输出风格、学习与循环](#七输出风格学习与循环)
- [八、LSP 语言服务器支持](#八lsp-语言服务器支持)
- [九、典型组合工作流](#九典型组合工作流)

---

## 一、日常开发与 Git 工作流

### `/feature-dev` — 结构化功能开发
**核心问题：我想做一个功能，但不希望 Claude 直接莽进实现。**

**功能：** 提供完整功能开发流程：需求理解 → 代码库探索 → 澄清问题 → 架构设计 → 实现 → 质量 review。配套 `code-explorer`、`code-architect`、`code-reviewer` agents。

**使用时机：**
- "实现这个新功能"
- 需求涉及多个文件、多个模块
- 需求还有歧义，需要先问问题
- 想让 Claude 先理解现有代码模式再动手

**特点：**
- 强调先探索、再设计、再实现
- 会要求读取 agents 找到的关键文件
- 适合中大型功能，不适合一两行小改动

---

### `/new-sdk-app` — 创建 Claude Agent SDK 应用
**核心问题：我要从零创建一个 Claude Agent SDK 项目。**

**功能：** 交互式创建 Python 或 TypeScript Agent SDK 应用，检查最新 SDK 版本，生成项目文件、环境变量样例、构建/类型检查配置，并调用 verifier agent 检查。

**使用时机：**
- 新建 Agent SDK app
- 想要一个最小 Hello World 或带常见功能的 agent 项目
- 需要 Python / TypeScript SDK 最佳实践

**配套 agents：**
| Agent | 作用 |
|---|---|
| `agent-sdk-verifier-py` | 检查 Python SDK 依赖、配置、环境变量、安全和 SDK 用法 |
| `agent-sdk-verifier-ts` | 检查 TypeScript SDK、ESM、tsconfig、类型检查和构建脚本 |

---

### `/commit` — 自动生成并创建 Git commit
**核心问题：我改完代码了，帮我整理成一个 commit。**

**功能：** 分析当前 git status、staged/unstaged diff 和历史 commit 风格，生成 commit message，stage 相关文件并提交。

**使用时机：**
- 完成一组相关改动
- 想让 commit message 跟仓库风格一致
- 不想手动梳理 diff

**注意：**
- 工作区有多组无关改动时，先明确告诉 Claude 只提交哪些文件
- 它会改变 git 状态，运行前最好先看 `git status`

---

### `/commit-push-pr` — 提交、推送并创建 PR
**核心问题：这组改动已经完成，帮我推上去并开 PR。**

**功能：** 在 `/commit` 的基础上继续 push 分支，并创建 pull request。

**使用时机：**
- 功能完成，准备进入 PR review
- 想把 commit、push、PR 创建合成一个流程

**注意：**
- 依赖远端仓库和常见 PR 工具配置
- PR 前建议先跑 `/code-review` 或 `/review-pr`

---

### `/clean_gone` — 清理 gone 分支
**核心问题：本地有很多远端已删除的分支。**

**功能：** 清理 tracking remote 已经 gone 的本地分支。

**使用时机：**
- 本地分支太多
- `git branch -vv` 里有大量 `gone`

**注意：**
- 清理前确认没有需要保留的本地-only 分支

---

## 二、代码审查、质量与安全

### `/code-review` — 自动化 PR 审查
**核心问题：这个 PR 有没有高置信度问题？**

**功能：** 多 agent 并行审查 PR：CLAUDE.md 合规、明显 bug、git blame/history 相关问题。每个发现打 0-100 置信度，默认只保留 80+ 的高置信度问题。

**使用时机：**
- PR 准备提交或合并前
- 想要快速自动审查
- 需要减少低质量 review 噪音

**特点：**
- 会跳过 closed、draft、trivial 或已审查 PR
- 输出偏向 actionable findings

---

### `/review-pr` — 综合 PR Review Toolkit
**核心问题：我要从多个角度深入检查这个 PR。**

**功能：** 启动一组专门 agents 对 PR 做专项审查。可指定 review aspects：`comments`、`tests`、`errors`、`types`、`code`、`simplify`、`all`。

**Agents：**
| Agent | 重点 |
|---|---|
| `comment-analyzer` | 注释准确性、完整性、是否会 comment rot |
| `pr-test-analyzer` | 测试覆盖质量、关键路径和边界情况 |
| `silent-failure-hunter` | 吞错、静默失败、不合理 fallback |
| `type-design-analyzer` | 类型封装、不变量表达和约束强度 |
| `code-reviewer` | 通用代码质量和项目规范 |
| `code-simplifier` | 合并前简化和整理 |

**使用时机：**
- 重要 PR
- 变更涉及错误处理、类型设计、测试或复杂业务逻辑
- 希望审查结果按领域分工更清晰

---

### `code-simplifier` — 保持行为不变的代码简化
**核心问题：代码能不能更清晰，但不要改变功能。**

**功能：** 对最近修改代码做简化和整理：降低嵌套、移除冗余、改善命名、合并相关逻辑、遵守项目 CLAUDE.md 风格。

**使用时机：**
- 刚完成一个功能或 bugfix
- 代码可读性一般，但测试已经通过
- 想在 commit 前做 polish

**边界：**
- 不应改变行为
- 不追求行数最少，优先可读性

---

### `security-guidance` — Claude 生成代码安全护栏
**核心问题：Claude 写代码时会不会引入安全漏洞？**

**功能：** 三层安全保护：

1. **Pattern warnings**：编辑时检查危险模式，如 `pickle.load`、`yaml.load`、raw `innerHTML`、硬编码 secrets。
2. **LLM diff review**：Stop hook 时对 diff 做安全审查，把高严重问题反馈给 Claude。
3. **Agentic commit review**：`git commit` 时跨文件追踪数据流，查 IDOR、auth bypass、SSRF 等。

**使用时机：**
- Web/API/认证/权限相关代码
- 涉及用户输入、文件上传、网络请求、反序列化
- 团队希望默认安全审查 Claude 产物

**注意：**
- 会增加额外模型调用和 token 成本
- 发现应作为高价值提示，仍需要人工判断

---

## 三、遗留系统现代化

### `code-modernization` — 遗留系统现代化工作流
**核心问题：我要系统性理解、规划并逐步现代化一个老系统。**

**功能：** 提供从环境检查到分析、拓扑、业务规则、方案、重写和安全加固的完整流程：

```text
preflight -> assess -> map -> extract-rules -> brief -> reimagine | transform -> harden
```

**重要判断：** 它是“一站式现代化工作流工具”，不是“一键自动重构整个项目的按钮”。它帮你把现代化拆成可审查、可验证、可恢复的阶段。

---

### `/modernize-preflight` — 现代化前置检查
**核心问题：这个环境能不能开始分析和改造？**

**功能：** 检测 legacy stack、分析工具、构建工具链、源码完整性、部署描述文件、telemetry 等，输出 `analysis/<system>/PREFLIGHT.md`。

**使用时机：**
- 现代化项目第一步
- 不确定源码是否完整
- 不确定工具链是否能编译/运行旧系统

**特点：**
- 会给每个后续命令 Ready / Ready-with-gaps / Not-ready 判断
- 能提前暴露缺 copybook、schema、部署配置等问题

---

### `/modernize-assess` — 盘点与评估
**核心问题：这个旧系统有多大、多复杂、风险在哪里？**

**功能：** 统计语言、LOC、复杂度、构建系统、集成点、技术债、安全姿态、文档缺口和 COCOMO 工作量估算，输出 `ASSESSMENT.md` 和架构图。

**使用时机：**
- 想做现代化立项评估
- 想比较多个系统的迁移优先级
- 需要给管理层一个初步工程量和风险视图

**模式：**
- 单系统：`/modernize-assess billing`
- 组合评估：`/modernize-assess --portfolio <parent-dir>`

---

### `/modernize-map` — 依赖拓扑与数据流
**核心问题：系统到底怎么连在一起？入口在哪里？数据怎么流？**

**功能：** 构建调用图、数据 lineage、入口点、dead-end candidates、关键 persona flows。输出可重跑提取脚本、`topology.json`、互动 `TOPOLOGY.html` 和 Mermaid 图。

**使用时机：**
- 不敢动代码，因为不知道依赖关系
- 想找迁移切入点
- 需要和业务/架构团队解释系统结构

**特点：**
- 不只 grep 直接调用，还要求处理 dispatcher、路由表、DI、配置映射等动态入口
- 适合遗留主机、老 Java、单体 Web 等

---

### `/modernize-extract-rules` — 抽取业务规则
**核心问题：旧代码里到底藏了哪些业务规则？**

**功能：** 从计算、校验/资格、状态/生命周期三条线并行抽取规则，输出 Given/When/Then 风格 Rule Cards 和 `DATA_OBJECTS.md`。

**使用时机：**
- 老系统没人能完整讲清业务逻辑
- 重写前需要明确哪些行为必须保留
- 想把代码里的隐性规则变成可测试规格

**Rule Card 包含：**
- Category / Priority
- Source `file:line`
- Plain English
- Given / When / Then specification
- Parameters / edge cases / confidence

---

### `/modernize-brief` — 现代化方案门禁
**核心问题：工程团队和管理层批准的现代化方案是什么？**

**功能：** 汇总 `ASSESSMENT.md`、`topology.json`、`BUSINESS_RULES.md`，生成 `MODERNIZATION_BRIEF.md`：目标架构、阶段计划、业务 walkthrough、行为契约、验证策略、风险和审批块。

**使用时机：**
- discovery 做完，准备进入实际迁移
- 需要方案评审和批准
- 需要把技术分析翻译成业务能读懂的计划

**特点：**
- 输入缺失会停止，要求先跑 discovery 命令
- 是 human-in-the-loop gate

---

### `/modernize-reimagine` — 从业务意图重新设计
**核心问题：我不想机械翻译旧系统，而是基于业务规则重新设计。**

**功能：** 从旧系统抽取 intent，生成 AI-native spec 和目标架构，经过 `architecture-critic` 对抗评审后，在 `modernized/<system>-reimagined/` 下脚手架新系统。

**使用时机：**
- 旧系统结构本身已经不值得保留
- 想转向事件驱动、微服务、现代框架
- 业务允许重新设计流程

**注意：**
- 更依赖人类架构判断
- 不适合要求逐行等价迁移的场景

---

### `/modernize-transform` — 单模块等价迁移
**核心问题：先迁移一个模块，证明新旧行为一致。**

**功能：** 对指定 module 做 strangler-fig 式重写：先规划，写 characterization/equivalence tests，再生成目标实现，跑测试证明等价，输出 `TRANSFORMATION_NOTES.md`。

**使用时机：**
- 找到一个边界清晰的模块
- 需要保留旧行为
- 想用小步迁移降低风险

**格式：**
```bash
/modernize-transform billing interest-calc java-spring
```

---

### `/modernize-harden` — 遗留系统安全加固
**核心问题：旧系统还要继续跑，先把高危漏洞处理掉。**

**功能：** 扫描 OWASP/CWE、dependency CVEs、secrets、注入风险，输出 `SECURITY_FINDINGS.md` 和可审阅 patch。不会直接编辑 `legacy/`。

**使用时机：**
- 迁移周期长，旧系统仍在生产
- 需要先降低安全风险
- 想把 Critical/High findings 做最小修复

**注意：**
- raw secrets 会进入隔离文件或 local patch，避免写入可共享报告
- patch 需要人工审阅后再应用

---

### `/modernize-status` — 现代化进度检查
**核心问题：我上次做到哪一步？哪些 artifact 过期了？**

**功能：** 只读检查 workflow artifact、时间戳、staleness、secrets hygiene，并推荐下一条最有价值命令。

**使用时机：**
- 中断后恢复现代化项目
- 多人协作时确认当前状态

---

### code-modernization Agents 速查

| Agent | 使用场景 | 关注点 |
|---|---|---|
| `legacy-analyst` | 读旧系统、做 discovery | 入口、数据结构、真实行为、缺口 |
| `business-rules-extractor` | 抽业务规则 | 计算、校验、资格、状态流转 |
| `architecture-critic` | 审目标架构/重写结果 | 反过度设计、边界、故障模式 |
| `security-auditor` | 安全审计 | OWASP、CWE、secrets、依赖 CVE |
| `test-engineer` | 写等价测试 | characterization、contract、equivalence |

---

## 四、Claude Code 配置、记忆与 Hooks

### `claude-automation-recommender` — 推荐自动化配置
**核心问题：这个项目应该配置哪些 Claude Code 自动化？**

**功能：** 只读扫描代码库，推荐 hooks、subagents、skills、plugins、MCP servers 和 slash commands。

**使用时机：**
- 新项目第一次接入 Claude Code
- 想提高 Claude Code 工作流效率
- 不知道该用 context7、Playwright、hooks 还是 agents

**特点：**
- 不修改文件
- 每类通常推荐 1-2 个，避免过载

---

### `claude-md-improver` — 审计和改进 CLAUDE.md
**核心问题：我的 CLAUDE.md 是否真的帮 Claude 理解项目？**

**功能：** 扫描项目中的 CLAUDE.md / `.claude.local.md`，按质量标准评估命令、架构、测试、gotchas、约定，并在用户确认后定向更新。

**使用时机：**
- CLAUDE.md 过旧
- 项目结构变了
- Claude 经常忘记项目命令或规则

**注意：**
- 会写 CLAUDE.md，需要先展示质量报告和修改建议

---

### `/revise-claude-md` — 从当前会话沉淀经验
**核心问题：这次会话发现的经验以后还会用到，帮我记下来。**

**功能：** 回顾当前会话，提取缺失上下文、命令、测试方式、环境 gotchas、代码风格等，写入合适的 CLAUDE.md 或 `.claude.local.md`。

**使用时机：**
- 会话结束前
- 刚发现一个环境坑
- Claude 反复需要同样提醒

**原则：**
- 简短、一行一个概念
- 避免写入一次性信息

---

### `/hookify` — 从自然语言创建 Hook 规则
**核心问题：我想防止 Claude 以后重复犯某类错误。**

**功能：** 分析用户描述或最近对话，生成 `.claude/hookify.{rule-name}.local.md` 规则。通用 hooks 会在 Bash、文件编辑、Stop、Prompt submit 等事件上匹配规则。

**使用时机：**
- "不要再改这个目录"
- "运行 rm -rf 前提醒我"
- "提交前必须跑测试"
- 发现 Claude 反复犯同一类错误

**规则结构：**
```markdown
---
name: warn-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
---

警告消息...
```

---

### `/configure`、`/list`、`/help` — Hookify 管理命令
**功能：**

| 命令 | 作用 |
|---|---|
| `/configure` | 交互式启用/禁用 hookify 规则 |
| `/list` | 列出全部 `.claude/hookify.*.local.md` 规则 |
| `/help` | 解释 hookify 工作机制和规则语法 |

**使用时机：**
- 想临时关闭某条规则
- 想查看当前会话有哪些护栏
- 手写规则前先看格式

---

## 五、插件、Skill 与 MCP 开发

### `/create-plugin` — 端到端创建 Claude Code 插件
**核心问题：我要写一个自己的 Claude Code plugin。**

**功能：** plugin-dev 的 guided workflow，覆盖 discovery、组件规划、详细设计、目录创建、组件实现、验证、测试、文档。

**使用时机：**
- 创建新插件
- 把一组 commands/agents/skills/hooks 打包
- 想按官方结构组织插件

**配套 skills：**
| Skill | 作用 |
|---|---|
| `plugin-structure` | 插件目录、manifest、组件发现 |
| `command-development` | slash command 编写 |
| `agent-development` | subagent 定义 |
| `skill-development` | skill 结构和触发描述 |
| `hook-development` | hooks API 和事件 |
| `mcp-integration` | `.mcp.json` 和 MCP server 集成 |
| `plugin-settings` | `.claude/plugin-name.local.md` 配置模式 |

**配套 agents：**
- `agent-creator`
- `plugin-validator`
- `skill-reviewer`

---

### `mcp-server-dev` — 构建 MCP Server
**核心问题：我要把一个 API、数据库或本地工具做成 MCP server。**

**功能：** 引导选择部署模型和工具设计方式，支持 remote HTTP、MCP app、MCPB、本地 stdio 原型。

**Skills：**
| Skill | 作用 |
|---|---|
| `build-mcp-server` | 入口，选择部署模型和 tool pattern |
| `build-mcp-app` | 构建带聊天内 UI widgets 的 MCP app |
| `build-mcpb` | 打包本地 stdio server，让用户无需安装 Node/Python |

**使用时机：**
- 想给 Claude 接一个内部 API
- 想把本地 CLI/文件能力包装成 MCP
- 想发布可安装 MCPB

---

### `/create-docker-mcp-tunnel` — 创建 Anthropic MCP Tunnel
**核心问题：Claude 需要访问我内网里的 MCP server，但我不想开放公网端口。**

**功能：** 用 Docker Compose 启动 mcp-proxy、cloudflared 和可选 sample server。引导用户在 Claude Console 创建 tunnel、上传 CA、配置证书和 upstream。

**使用时机：**
- 本地/内网 MCP server 需要被 Claude 调用
- 不想配置公网入站、防火墙或 IP allowlist
- 做 MCP tunnel quickstart

**注意：**
- Research preview
- 涉及 Docker、证书、Cloudflare tunnel 和凭据
- 不建议直接承载生产敏感流量，需审安全模型

---

### `skill-creator` — 创建、测试和优化 Skill
**核心问题：我想把某个流程沉淀成可复用 skill。**

**功能：** 帮你定义 skill 目标、写草稿、设计测试 prompts、运行评估、分析结果、迭代 skill，并优化 description 触发准确率。

**使用时机：**
- 从零创建 skill
- 已有 skill 触发不准或效果不稳定
- 想给 skill 加 eval/benchmark

**特点：**
- 强调 test prompts 和定性/定量评估
- 适合把个人流程产品化

---

### `example-plugin` — 官方示例插件
**核心问题：Claude Code plugin 到底应该长什么样？**

**功能：** 展示 `.claude-plugin/plugin.json`、`.mcp.json`、`commands/`、`skills/` 等结构。

**使用时机：**
- 学习插件结构
- 写新插件前找模板
- 对比 legacy command 格式和 skill command 格式

---

## 六、领域型插件

### `frontend-design` — 高质量前端设计实现
**核心问题：我要 Claude 写出有审美、有区分度的前端，而不是默认 AI 风格。**

**功能：** 指导 Claude 选择明确 aesthetic direction，生成 production-grade UI：字体、颜色、布局、动效、空间、背景细节都要服务于产品语境。

**使用时机：**
- 做页面、组件、dashboard、landing page、settings panel
- 想要更强视觉风格
- 想避免紫色渐变、Inter、模板卡片堆叠等常见 AI slop

**注意：**
- 它是设计指导 skill，不等于浏览器 QA
- 实现后仍建议用 Playwright/浏览器截图验证

---

### `playground` — 生成交互式 HTML Playground
**核心问题：我想把复杂选择变成一个可视化探索工具。**

**功能：** 生成单文件 HTML：控件、live preview、prompt 输出和 copy 按钮。

**使用时机：**
- 设计参数探索
- 数据查询/正则/API 构建器
- 概念图/知识范围探索
- 文档 critique 工作台

**特点：**
- 输出是可打开的单 HTML 文件
- 适合“输入空间很大、纯文字难表达”的场景

---

### `math-olympiad` — 竞赛数学与证明验证
**核心问题：这个竞赛数学证明到底可靠吗？**

**功能：** 解 IMO、Putnam、USAMO、AIME 等竞赛数学题，并使用 fresh-context adversarial verifier 攻击证明。

**使用时机：**
- "solve this IMO problem"
- "verify this olympiad proof"
- "find a counterexample"
- 需要高置信度数学证明

**特点：**
- 不只是自我检查
- 低置信度时倾向 abstain，不硬编证明

---

### `/maker-setup` — Code-with-Claude Makers Cardputer
**核心问题：我要把 M5Stack/Cardputer 设备刷好并装 Claude Buddy。**

**功能：** 克隆 `build-with-claude`，检测设备，刷 UIFlow 2.0 固件，安装 Claude Buddy、Hello、Snake app bundle。

**Skills：**
| Skill | 作用 |
|---|---|
| `m5-onboard` | 检测 USB、识别型号、刷固件、安装 apps |
| `cardputer-buddy` | 已刷机后 push 单文件、tail serial、REPL |

**使用时机：**
- 新 Cardputer/Cardputer-Adv 设备接入
- 想继续开发 MicroPython app
- 想看串口日志或快速推送 app

---

## 七、输出风格、学习与循环

### `explanatory-output-style` — 解释型输出风格
**核心问题：我希望 Claude 写代码时顺便解释关键实现选择。**

**功能：** 通过 SessionStart hook 注入说明，鼓励 Claude 在实现前后给出简短教育性解释。

**使用时机：**
- 学习项目代码模式
- 希望 Claude 解释为什么这样实现

**注意：**
- 安装后每个 session 自动生效
- 会增加 token 成本

---

### `learning-output-style` — 互动学习模式
**核心问题：我想参与关键代码，而不是只看 Claude 全自动写完。**

**功能：** SessionStart hook 注入学习模式，让 Claude 在业务逻辑、错误处理、算法、数据结构、UX 决策等位置邀请用户写 5-10 行关键代码。

**使用时机：**
- 学习一个代码库或技术栈
- 想训练自己而不是只要结果
- pair programming 教学场景

**注意：**
- 互动性强，不适合追求最快交付
- 也包含 explanatory-output-style 的解释能力

---

### `/ralph-loop` — 自循环迭代开发
**核心问题：这个任务可以让 Claude 多轮重复改进，直到满足明确验收条件。**

**功能：** 用 Stop hook 拦截 Claude 退出，把同一个 prompt 再喂给 Claude。Claude 会看到上一轮写入的文件和 git 历史，继续改进。

**使用示例：**
```bash
/ralph-loop "补齐测试直到 npm test 通过" --max-iterations 10 --completion-promise "TESTS PASS"
```

**使用时机：**
- 补测试、修 lint、完善文档、批量机械改进
- 任务有明确完成信号
- 可以接受多轮自主执行

**不适合：**
- 需求不清楚
- 需要频繁人工产品判断
- 生产/敏感/破坏性操作

**管理命令：**
| 命令 | 作用 |
|---|---|
| `/ralph-loop` | 启动循环 |
| `/cancel-ralph` | 删除 loop 状态文件，取消循环 |
| `/help` | 解释 Ralph Loop 工作方式 |

---

### `session-report` — Claude Code 使用报告
**核心问题：最近 Claude Code token 花在哪了？cache 命中率如何？哪些 prompt 最贵？**

**功能：** 从 `~/.claude/projects` transcripts 分析 session 使用情况，生成自包含 HTML 报告：tokens、cache、subagents、skills、cache breaks、top prompts。

**使用时机：**
- 想优化 Claude 使用成本
- 想知道哪个项目/skill/subagent 最耗 token
- 想排查 cache 命中率低的问题

**输出：**
```text
session-report-YYYYMMDD-HHMM.html
```

---

## 八、LSP 语言服务器支持

### LSP 支持包总览
**核心问题：让 Claude Code 获得语言级代码智能、诊断、跳转和引用能力。**

| 目录 | 语言 / Server | 扩展名 | 安装方式简述 |
|---|---|---|---|
| `typescript-lsp` | TypeScript/JavaScript language server | `.ts` `.tsx` `.js` `.jsx` `.mts` `.cts` `.mjs` `.cjs` | `npm install -g typescript-language-server typescript` |
| `pyright-lsp` | Python Pyright | `.py` `.pyi` | `npm install -g pyright` 或 `pipx install pyright` |
| `gopls-lsp` | Go gopls | `.go` | `go install golang.org/x/tools/gopls@latest` |
| `rust-analyzer-lsp` | Rust Analyzer | `.rs` | `rustup component add rust-analyzer` |
| `clangd-lsp` | C/C++ clangd | `.c` `.h` `.cpp` `.cc` `.cxx` `.hpp` 等 | `brew install llvm` / 系统包管理器 |
| `jdtls-lsp` | Java Eclipse JDT.LS | `.java` | `brew install jdtls` 或手动安装 |
| `csharp-lsp` | C# csharp-ls | `.cs` | `dotnet tool install --global csharp-ls` |
| `kotlin-lsp` | Kotlin LSP | `.kt` `.kts` | `brew install JetBrains/utils/kotlin-lsp` |
| `lua-lsp` | Lua Language Server | `.lua` | `brew install lua-language-server` |
| `php-lsp` | PHP Intelephense | `.php` | `npm install -g intelephense` |
| `ruby-lsp` | Ruby LSP | `.rb` `.rake` `.gemspec` `.ru` `.erb` | `gem install ruby-lsp` |
| `swift-lsp` | SourceKit-LSP | `.swift` | 随 Swift toolchain / Xcode 提供 |

**使用时机：**
- 大型代码库导航
- 想让 Claude 做更准确的 rename、引用查找、诊断
- 多语言项目需要语言级上下文

**注意：**
- 多数 LSP 目录只有 README，没有 `.claude-plugin/plugin.json`
- 需要用户自己安装对应 language server 并确保在 PATH 中

---

## 九、典型组合工作流

### 新功能开发

```text
/feature-dev
    ↓
实现功能
    ↓
/review-pr 或 /code-review
    ↓
code-simplifier
    ↓
/commit 或 /commit-push-pr
```

**适合：** 中大型 feature、跨模块改动、需要设计和审查的功能。

---

### 遗留系统现代化

```text
/modernize-preflight
    ↓
/modernize-assess
    ↓
/modernize-map
    ↓
/modernize-extract-rules
    ↓
/modernize-brief
    ↓
/modernize-transform 或 /modernize-reimagine
    ↓
/modernize-harden
```

**适合：** COBOL、老 Java/C++、传统单体 Web、长期缺文档系统。

**关键原则：** 先理解和证明，再改造。不要直接让 Claude “重写整个项目”。

---

### Claude Code 项目优化

```text
claude-automation-recommender
    ↓
claude-md-improver
    ↓
/hookify
    ↓
session-report
```

**适合：** 让 Claude 在某个项目里更稳定、更省 token、更少犯重复错误。

---

### 插件 / Skill / MCP 开发

```text
/create-plugin
    ↓
plugin-dev skills
    ↓
skill-creator
    ↓
mcp-server-dev（需要外部工具时）
    ↓
/create-docker-mcp-tunnel（需要内网访问时）
```

**适合：** 把团队流程产品化，或给 Claude Code 接内部系统。

---

### 学习和实验

```text
learning-output-style
    ↓
explanatory-output-style
    ↓
/ralph-loop（仅用于可验证重复任务）
```

**适合：** 学代码、做实验、让 Claude 多轮自主改进。

---

## 附：安装方式速查

官方插件通常通过 Claude Code 插件市场安装：

```bash
/plugin install <plugin-name>@claude-plugins-official
```

示例：

```bash
/plugin install feature-dev@claude-plugins-official
/plugin install code-modernization@claude-plugins-official
/plugin install commit-commands@claude-plugins-official
/plugin install security-guidance@claude-plugins-official
```

---

## 附：选择建议

| 你现在的目标 | 优先选 |
|---|---|
| 快速完成日常功能 | `feature-dev` + `commit-commands` |
| PR 合并前把关 | `code-review` 或 `pr-review-toolkit` |
| 降低 Claude 写出安全问题的概率 | `security-guidance` |
| 老项目重构/迁移 | `code-modernization` |
| 让 Claude 更懂本项目 | `claude-md-management` |
| 防止 Claude 重复犯错 | `hookify` |
| 自己做 Claude Code 扩展 | `plugin-dev` + `skill-creator` |
| 接外部/内部工具 | `mcp-server-dev` + `mcp-tunnels` |
| 做前端页面 | `frontend-design` |
| 需要代码智能 | 对应 `*-lsp` |

