# Skill 总目录（install.py 自动生成，勿手改）

共 48 个 · 已验证 48 · 待验证 0

想看深度使用经验 → wiki entity 页；想改行为 → SKILL.md；本目录只回答“它能干什么、边界在哪”。

## 写作
- **baoyu-format-markdown**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— 给纯文本/markdown 自动排版：frontmatter、标题、摘要、加粗、列表、代码块
  边界：只排版不改写内容
- **baoyu-infographic**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— 生成专业信息图：21 种布局 × 22 种视觉风格，自动推荐组合
  边界：依赖图像生成 API；适合单页信息图而非长文
- **baoyu-markdown-to-html**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— markdown 转带主题 HTML，兼容微信公众号；支持代码高亮、数学公式、Mermaid、PlantUML
  边界：Mermaid 转 PNG 需 headless Chrome
- **baoyu-translate**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— 中英互译、精翻、本地化与译后校对
  边界：只翻译润色，不做内容创作
- **writing-beats**（第三方·mattpocock/skills·已验证 2026-08-23）— 写作·exploit：把素材组装成节拍化叙事，先立术语再用
  边界：只管结构节奏，不挖素材
- **writing-fragments**（第三方·mattpocock/skills·已验证 2026-08-23）— 写作·explore：挖掘原始碎片素材，尚无结构
  边界：早期探索阶段，不出成稿
- **writing-shape**（第三方·mattpocock/skills·已验证 2026-08-23）— 写作·exploit：逐段把素材塑形成文章
  边界：偏成稿阶段，需要已有素材

## 协作
- **agent-dag-reporting**（自研·已验证 2026-08-24）— 将多步骤任务的计划、状态、产物和检查点按 agent-dag/v1 上报到 Personal Workbench
  边界：仅负责可观测性上报，不改变任务执行方式；依赖宿主提供对应 MCP 上报工具
- **claude-handoff**（第三方·mattpocock/skills·已验证 2026-08-23）— 把当前对话即时交接给新的后台 agent 继续干
  边界：只管交接，不管任务本身
- **handoff**（第三方·mattpocock/skills·已验证 2026-08-23）— 把当前对话压缩成交接文档，供另一个 agent 接手
  边界：产出文档；要即时交接用 claude-handoff
- **triage**（第三方·mattpocock/skills·已验证 2026-08-23）— issue 和外部 PR 的分诊状态机：分类、验证、追问，产出 agent 可直接执行的简报
  边界：面向开源仓库维护场景

## 图像
- **baoyu-image-gen**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— 多平台 AI 出图：GPT Image、即梦、Seedream、MiniMax 等十几家 API，支持文生图和参考图
  边界：只出图不管文章排版；依赖外部图像 API key
- **baoyu-infographic**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— 生成专业信息图：21 种布局 × 22 种视觉风格，自动推荐组合
  边界：依赖图像生成 API；适合单页信息图而非长文

## 图表
- **diagram**（第三方·312362115/claude·已验证 2026-08-23）— 生成 29 种专业 PNG 图表：流程/时序/架构/ER/甘特 + 柱线饼雷等统计图，统一设计规范
  边界：HTML/SVG+JS 渲染输出 PNG，非矢量源文件
- **excalidraw-diagram-generator**（第三方·p-rp/excalidraw-diagram-generator·已验证 2026-08-23）— 自然语言生成 Excalidraw 图：流程图、架构图、思维导图、关系图
  边界：输出 .excalidraw JSON，需 Excalidraw 打开查看

## 抓取
- **baoyu-url-to-markdown**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— 抓任意 URL 转 markdown，内置 X/YouTube 字幕/Hacker News 等站点适配器
  边界：依赖 baoyu-fetch CLI 和 Chrome CDP

## 效率
- **agent-dag-reporting**（自研·已验证 2026-08-24）— 将多步骤任务的计划、状态、产物和检查点按 agent-dag/v1 上报到 Personal Workbench
  边界：仅负责可观测性上报，不改变任务执行方式；依赖宿主提供对应 MCP 上报工具
- **ask-matt**（第三方·mattpocock/skills·已验证 2026-08-23）— 在 mattpocock 全家桶里帮你选合适的 skill 或流程
  边界：只是路由器，本身不执行具体工作
- **deepagents-subagents**（自研·已验证 2026-08-21）— 设计 DeepAgents 同步、动态和异步子 Agent 委派及并发取消语义
  边界：不处理一般 backend 权限或单 Agent 入门
- **goal-coach**（自研·已验证 2026-08-23）— 判断任务是否适合 /goal，并生成完整中文 /goal prompt（完成标准/边界/停止规则）
  边界：只服务 Claude Code 的 /goal 命令场景

## 教学
- **deepagents-getting-started**（自研·已验证 2026-08-21）— 提供 DeepAgents 0.7.8 的最小闭环、总体架构和核心组件选型规则
  边界：不处理具体后端安全、子 Agent 拆分或版本敏感 API 查询
- **scaffold-exercises**（第三方·mattpocock/skills·已验证 2026-08-23）— 脚手架生成练习目录：分节、题目、答案、讲解，过 lint
  边界：面向课程/教学内容制作
- **teach**（第三方·mattpocock/skills·已验证 2026-08-23）— 在工作区内教会你一个技能或概念
  边界：教学对话，不产出工程代码

## 架构
- **codebase-design**（第三方·mattpocock/skills·已验证 2026-08-23）— 深模块设计方法论：设计模块接口、找深化机会、定接缝位置
  边界：是词汇表/方法论，不是自动化工具
- **deepagents-context-memory**（自研·已验证 2026-08-21）— 设计 DeepAgents 上下文分层、文件化 offload、checkpoint 和跨线程长期记忆
  边界：不处理 sandbox 权限细节或子 Agent 拓扑
- **deepagents-execution-environment**（自研·已验证 2026-08-21）— 设计 DeepAgents backend、虚拟文件系统、sandbox、shell 和权限边界
  边界：不负责总体入门、长期记忆建模或子 Agent 拆分
- **deepagents-getting-started**（自研·已验证 2026-08-21）— 提供 DeepAgents 0.7.8 的最小闭环、总体架构和核心组件选型规则
  边界：不处理具体后端安全、子 Agent 拆分或版本敏感 API 查询
- **deepagents-subagents**（自研·已验证 2026-08-21）— 设计 DeepAgents 同步、动态和异步子 Agent 委派及并发取消语义
  边界：不处理一般 backend 权限或单 Agent 入门
- **domain-modeling**（第三方·mattpocock/skills·已验证 2026-08-23）— 打磨项目领域模型：统一术语、CONTEXT.md、ADR
  边界：偏讨论与文档产出，不写实现代码
- **framework-skill-author**（自研·已验证 2026-08-21）— 基于框架官方文档、API、版本记录和源码创建、刷新或审计可追溯的中文 Skill Pack
  边界：不用于普通文档摘要，也不接受非官方资料作为核心依据
- **improve-codebase-architecture**（第三方·mattpocock/skills·已验证 2026-08-23）— 扫描代码库找架构深化机会，生成可视化 HTML 报告并逐项追问
  边界：偏 TS/JS 项目语境
- **setup-ts-deep-modules**（第三方·mattpocock/skills·已验证 2026-08-23）— 接入 dependency-cruiser，强制 TS 包深模块化、隐藏内部实现
  边界：仅 TS monorepo

## 测试
- **migrate-to-shoehorn**（第三方·mattpocock/skills·已验证 2026-08-23）— 把测试文件里的 as 类型断言迁移到 @total-typescript/shoehorn
  边界：仅 TS 测试数据场景
- **tdd**（第三方·mattpocock/skills·已验证 2026-08-23）— 测试驱动开发：red-green-refactor，集成测试优先
  边界：需要项目已有测试基建

## 研究
- **baoyu-url-to-markdown**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— 抓任意 URL 转 markdown，内置 X/YouTube 字幕/Hacker News 等站点适配器
  边界：依赖 baoyu-fetch CLI 和 Chrome CDP
- **deepagents-docs**（自研·已验证 2026-08-21）— 查询并核验 DeepAgents 官方文档、API、版本差异和长尾问题
  边界：不替代入门、执行环境、上下文记忆或子 Agent 的稳定决策规则
- **framework-skill-author**（自研·已验证 2026-08-21）— 基于框架官方文档、API、版本记录和源码创建、刷新或审计可追溯的中文 Skill Pack
  边界：不用于普通文档摘要，也不接受非官方资料作为核心依据
- **research**（第三方·mattpocock/skills·已验证 2026-08-23）— 对着高可信一手资料做调研，结论落盘为 repo 里的 markdown
  边界：需要网络访问；不做观点创作

## 编程
- **code-review**（第三方·mattpocock/skills·已验证 2026-08-23）— 从固定点（commit/branch/tag）起审 diff：编码规范 + 是否符合 spec 双轴并行
  边界：只审不改
- **deepagents-context-memory**（自研·已验证 2026-08-21）— 设计 DeepAgents 上下文分层、文件化 offload、checkpoint 和跨线程长期记忆
  边界：不处理 sandbox 权限细节或子 Agent 拓扑
- **deepagents-docs**（自研·已验证 2026-08-21）— 查询并核验 DeepAgents 官方文档、API、版本差异和长尾问题
  边界：不替代入门、执行环境、上下文记忆或子 Agent 的稳定决策规则
- **deepagents-execution-environment**（自研·已验证 2026-08-21）— 设计 DeepAgents backend、虚拟文件系统、sandbox、shell 和权限边界
  边界：不负责总体入门、长期记忆建模或子 Agent 拆分
- **deepagents-getting-started**（自研·已验证 2026-08-21）— 提供 DeepAgents 0.7.8 的最小闭环、总体架构和核心组件选型规则
  边界：不处理具体后端安全、子 Agent 拆分或版本敏感 API 查询
- **deepagents-subagents**（自研·已验证 2026-08-21）— 设计 DeepAgents 同步、动态和异步子 Agent 委派及并发取消语义
  边界：不处理一般 backend 权限或单 Agent 入门
- **framework-skill-author**（自研·已验证 2026-08-21）— 基于框架官方文档、API、版本记录和源码创建、刷新或审计可追溯的中文 Skill Pack
  边界：不用于普通文档摘要，也不接受非官方资料作为核心依据
- **git-guardrails-claude-code**（第三方·mattpocock/skills·已验证 2026-08-23）— 给 Claude Code 配 git 安全 hook，拦截 push/reset --hard/clean 等危险命令
  边界：只防 git 危险操作，不管其他命令
- **implement**（第三方·mattpocock/skills·已验证 2026-08-23）— 按 spec 或 ticket 实现具体工作
  边界：需要已有 spec/ticket，不做需求澄清
- **migrate-to-shoehorn**（第三方·mattpocock/skills·已验证 2026-08-23）— 把测试文件里的 as 类型断言迁移到 @total-typescript/shoehorn
  边界：仅 TS 测试数据场景
- **prototype**（第三方·mattpocock/skills·已验证 2026-08-23）— 快速搭一次性原型，验证状态模型逻辑或 UI 感觉
  边界：是 throwaway 代码，别当正式实现
- **resolving-merge-conflicts**（第三方·mattpocock/skills·已验证 2026-08-23）— 解决进行中的 git merge/rebase 冲突
  边界：只管冲突解决这一步
- **setup-pre-commit**（第三方·mattpocock/skills·已验证 2026-08-23）— 配置 Husky pre-commit：lint-staged、Prettier、类型检查、测试
  边界：仅 JS/TS 仓库
- **setup-ts-deep-modules**（第三方·mattpocock/skills·已验证 2026-08-23）— 接入 dependency-cruiser，强制 TS 包深模块化、隐藏内部实现
  边界：仅 TS monorepo
- **tdd**（第三方·mattpocock/skills·已验证 2026-08-23）— 测试驱动开发：red-green-refactor，集成测试优先
  边界：需要项目已有测试基建

## 翻译
- **baoyu-translate**（第三方·jimliu/baoyu-skills·已验证 2026-08-23）— 中英互译、精翻、本地化与译后校对
  边界：只翻译润色，不做内容创作

## 规划
- **agent-dag-reporting**（自研·已验证 2026-08-24）— 将多步骤任务的计划、状态、产物和检查点按 agent-dag/v1 上报到 Personal Workbench
  边界：仅负责可观测性上报，不改变任务执行方式；依赖宿主提供对应 MCP 上报工具
- **goal-coach**（自研·已验证 2026-08-23）— 判断任务是否适合 /goal，并生成完整中文 /goal prompt（完成标准/边界/停止规则）
  边界：只服务 Claude Code 的 /goal 命令场景
- **grill-me**（第三方·mattpocock/skills·已验证 2026-08-23）— 无情追问，把你的计划或设计逼问到无懈可击
  边界：只提问施压，不产出文档
- **grill-with-docs**（第三方·mattpocock/skills·已验证 2026-08-23）— 追问打磨方案，同时沉淀 ADR 和术语表
  边界：grill-me 的带文档产出版
- **grilling**（第三方·mattpocock/skills·已验证 2026-08-23）— 压力测试你的想法、决策或计划
  边界：偏触发词路由，与 grill-me 同族
- **loop-me**（第三方·mattpocock/skills·已验证 2026-08-23）— 在本工作区内追问你想构建的 workflow 的 spec
  边界：限当前 workspace
- **to-spec**（第三方·mattpocock/skills·已验证 2026-08-23）— 把当前对话直接综合成 spec 并发布到 issue tracker
  边界：不做采访式追问（那是 grill 系的事）
- **to-tickets**（第三方·mattpocock/skills·已验证 2026-08-23）— 把计划/spec 拆成带依赖边的 tracer-bullet tickets，发布到 tracker
  边界：需要先配置 issue tracker
- **wayfinder**（第三方·mattpocock/skills·已验证 2026-08-23）— 把超过单个会话的大工程拆成 decision ticket 地图，逐个解决直到路径清晰
  边界：小任务用它杀鸡用牛刀

## 设计
- **prototype**（第三方·mattpocock/skills·已验证 2026-08-23）— 快速搭一次性原型，验证状态模型逻辑或 UI 感觉
  边界：是 throwaway 代码，别当正式实现

## 调试
- **diagnosing-bugs**（第三方·mattpocock/skills·已验证 2026-08-23）— 疑难 bug 和性能回退的结构化诊断循环
  边界：针对难治问题；简单 bug 不必动用

## 运维
- **deepagents-execution-environment**（自研·已验证 2026-08-21）— 设计 DeepAgents backend、虚拟文件系统、sandbox、shell 和权限边界
  边界：不负责总体入门、长期记忆建模或子 Agent 拆分
- **git-guardrails-claude-code**（第三方·mattpocock/skills·已验证 2026-08-23）— 给 Claude Code 配 git 安全 hook，拦截 push/reset --hard/clean 等危险命令
  边界：只防 git 危险操作，不管其他命令
- **setup-matt-pocock-skills**（第三方·mattpocock/skills·已验证 2026-08-23）— 首次使用 mattpocock 工程 skill 前的仓库初始化：issue tracker、标签词表、文档布局
  边界：每个仓库只需跑一次
- **setup-pre-commit**（第三方·mattpocock/skills·已验证 2026-08-23）— 配置 Husky pre-commit：lint-staged、Prettier、类型检查、测试
  边界：仅 JS/TS 仓库
- **wizard**（第三方·mattpocock/skills·已验证 2026-08-23）— 生成交互式 bash 向导，引导人完成只有人能做的步骤：配密钥、CI secrets、第三方后台
  边界：agent 自己能干的活别用它
