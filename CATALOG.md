# Skill 总目录（install.py 自动生成，勿手改）

共 69 个 · 已验证 53 · 待验证 16

想看深度使用经验 → wiki entity 页；想改行为 → SKILL.md；本目录只回答“它能干什么、边界在哪”。

## 代码审查
- **wl-requesting-code-review**（自研·已验证 2026-09-01）— 在交付前依据需求、架构、风险与测试证据审查已完成的代码
  边界：用于完整任务或重要功能实现后的代码审查，不用于需求澄清或方案设计

## 写作
- **inspector-docs**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 维护 CopilotKit Inspector 文档与已发布 Pane、Tab、Overlay 行为的一致性
  边界：仅服务 CopilotKit 上游 Inspector 文档维护，不用于 Inspector UI 润色或未发布功能设计
- **writing-beats**（第三方·mattpocock/skills·已验证 2026-08-23）— 写作·exploit：把素材组装成节拍化叙事，先立术语再用
  边界：只管结构节奏，不挖素材
- **writing-fragments**（第三方·mattpocock/skills·已验证 2026-08-23）— 写作·explore：挖掘原始碎片素材，尚无结构
  边界：早期探索阶段，不出成稿
- **writing-shape**（第三方·mattpocock/skills·已验证 2026-08-23）— 写作·exploit：逐段把素材塑形成文章
  边界：偏成稿阶段，需要已有素材

## 前端
- **wl-plan-design-review**（自研·已验证 2026-09-01）— 在编码前审查并完善 UI/UX 实施计划，使交互和视觉决策达到可实施状态
  边界：只审查前端体验与设计计划，不替代工程架构评审或代码实现

## 协作
- **agent-dag-reporting**（自研·已验证 2026-08-24）— 将多步骤任务的计划、状态、产物和检查点按 agent-dag/v1 上报到 Personal Workbench
  边界：仅负责可观测性上报，不改变任务执行方式；依赖宿主提供对应 MCP 上报工具
- **channels-setup**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 从零搭建可在 Slack 或 Microsoft Teams 响应消息的 CopilotKit Channels Agent
  边界：端到端初始化流程会在运行时读取官方在线指南，并依赖 CopilotKit CLI、托管 Channel 与平台配置
- **claude-handoff**（第三方·mattpocock/skills·已验证 2026-08-23）— 把当前对话即时交接给新的后台 agent 继续干
  边界：只管交接，不管任务本身
- **copilotkit-channels**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 编写和定制 CopilotKit 托管 Channel 的声明、常驻 Host 与激活逻辑
  边界：只覆盖 Channel 代码侧；首次创建 Slack App 应改用 setup-slack-channel
- **copilotkit-contribute**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 指导参与 CopilotKit 开源仓库开发：Fork、环境搭建、分支、测试与提交 PR
  边界：仅面向 CopilotKit/CopilotKit 上游贡献，不是业务项目的通用 Git 工作流
- **handoff**（第三方·mattpocock/skills·已验证 2026-08-23）— 把当前对话压缩成交接文档，供另一个 agent 接手
  边界：产出文档；要即时交接用 claude-handoff
- **setup-slack-channel**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 完成 CopilotKit Channels 的 Slack Provider 侧首次配置、Token、托管 Channel 绑定与连通性验证
  边界：只覆盖首次 Slack Provider 配置，且主要适配 OpenTag 或 channels-sdk 示例约定；Channel 代码定制用 copilotkit-channels
- **triage**（第三方·mattpocock/skills·已验证 2026-08-23）— issue 和外部 PR 的分诊状态机：分类、验证、追问，产出 agent 可直接执行的简报
  边界：面向开源仓库维护场景

## 图表
- **diagram**（第三方·312362115/claude·已验证 2026-08-23）— 生成 29 种专业 PNG 图表：流程/时序/架构/ER/甘特 + 柱线饼雷等统计图，统一设计规范
  边界：HTML/SVG+JS 渲染输出 PNG，非矢量源文件
- **excalidraw-diagram-generator**（第三方·p-rp/excalidraw-diagram-generator·已验证 2026-08-23）— 自然语言生成 Excalidraw 图：流程图、架构图、思维导图、关系图
  边界：输出 .excalidraw JSON，需 Excalidraw 打开查看

## 多智能体
- **wl-subagent-driven-development**（自研·已验证 2026-09-01）— 按已批准计划逐任务调度隔离 Worker，以测试优先、规格审查和质量审查完成开发
  边界：仅在方案已批准后使用；子 Agent 未获授权或不可用时必须在本地执行同等闸门

## 审查
- **wl-plan-design-review**（自研·已验证 2026-09-01）— 在编码前审查并完善 UI/UX 实施计划，使交互和视觉决策达到可实施状态
  边界：只审查前端体验与设计计划，不替代工程架构评审或代码实现
- **wl-plan-eng-review**（自研·已验证 2026-09-01）— 从架构、影响域、接口、数据、安全、性能、迁移、回滚和测试等维度审查实施计划
  边界：只做编码前的工程方案审查，不直接实施计划或替代代码审查

## 开发流程
- **wl-brainstorming**（自研·已验证 2026-09-01）— 将模糊的软件想法或行为变更澄清为经确认、可测试的设计
  边界：用于新功能或显著行为变更的需求与设计定稿，不执行已经批准的实现方案
- **wl-investigate**（自研·已验证 2026-09-01）— 以证据优先和根因分析方式独立复现、定位并修复缺陷或回归
  边界：仅用于缺陷诊断与修复；修复前必须有失败复现，修复后必须验证
- **wl-requesting-code-review**（自研·已验证 2026-09-01）— 在交付前依据需求、架构、风险与测试证据审查已完成的代码
  边界：用于完整任务或重要功能实现后的代码审查，不用于需求澄清或方案设计
- **wl-subagent-driven-development**（自研·已验证 2026-09-01）— 按已批准计划逐任务调度隔离 Worker，以测试优先、规格审查和质量审查完成开发
  边界：仅在方案已批准后使用；子 Agent 未获授权或不可用时必须在本地执行同等闸门
- **wl-writing-plans**（自研·已验证 2026-09-01）— 将已批准规格或稳定需求转换为详细、测试优先的实施计划
  边界：仅用于多步骤工程任务；需求或架构尚未确定时不得使用
- **wl_design-doc**（自研·已验证 2026-08-31）— 方案设计——需求批准后产出可批准的《方案设计文档》（映射/契约/复用分析/多方案/附证据审查/最小验证）
  边界：前置 wl_req-confirm 已批准；只出方案不写实现代码，不替用户拍板选方案
- **wl_req-confirm**（自研·已验证 2026-08-31）— 需求确认——把模糊诉求变成人审批准的《需求确认文档》（重定义需求/用户故事/Out of Scope/验收）
  边界：只回答要什么/为什么/怎么算完成，不回答怎么做（方案设计归 wl_design-doc）
- **wl_ticket-run**（自研·已验证 2026-08-31）— 工单执行——方案批准后拆垂直切片工单（G/W/T 验收），/list 并行调度、/goal 审计执行到验收
  边界：前置 wl_design-doc 已批准；管执行纪律（台账/熔断/停机），不做需求与方案决策

## 效率
- **agent-dag-reporting**（自研·已验证 2026-08-24）— 将多步骤任务的计划、状态、产物和检查点按 agent-dag/v1 上报到 Personal Workbench
  边界：仅负责可观测性上报，不改变任务执行方式；依赖宿主提供对应 MCP 上报工具
- **ask-matt**（第三方·mattpocock/skills·已验证 2026-08-23）— 在 mattpocock 全家桶里帮你选合适的 skill 或流程
  边界：只是路由器，本身不执行具体工作
- **copilotkit-self-update**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 刷新或重装 CopilotKit 官方 Agent Skills，使本地知识与最新 API 保持同步
  边界：只更新 CopilotKit Skills，不升级业务依赖；其官方安装命令会直接写 Agent 加载目录，可能绕过本仓库登记流程
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
- **copilotkit-agui**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 实现和调试 AG-UI 协议、自定义 Agent 后端、SSE 事件流、状态同步与人机协同
  边界：聚焦 Agent 与前端通信协议，不负责 CopilotKit React 界面组件的具体使用
- **copilotkit-integrations**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 通过 AG-UI 将 LangGraph、CrewAI、PydanticAI、Mastra 等外部 Agent 框架接入 CopilotKit
  边界：只处理外部 Agent 框架集成，不覆盖 CopilotKit 前端组件或常规运行时开发
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
- **fastapi**（第三方·fastapi/fastapi·**待验证（未安装）**）— 遵循 FastAPI 官方最佳实践编写 API、Pydantic 模型、依赖注入、流式响应、SSE 与前端资源服务代码
  边界：跟随 FastAPI master 分支的最新模式；用于较旧固定版本时需先核对 API 兼容性，不替代具体业务架构设计
- **framework-skill-author**（自研·已验证 2026-08-21）— 基于框架官方文档、API、版本记录和源码创建、刷新或审计可追溯的中文 Skill Pack
  边界：不用于普通文档摘要，也不接受非官方资料作为核心依据
- **improve-codebase-architecture**（第三方·mattpocock/skills·已验证 2026-08-23）— 扫描代码库找架构深化机会，生成可视化 HTML 报告并逐项追问
  边界：偏 TS/JS 项目语境
- **runtime**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 使用 @copilotkit/runtime 搭建服务端 CopilotRuntime、AgentRunner、工具、Intelligence 与语音转录
  边界：聚焦服务端运行时，不负责 React 前端组件；优先采用 fetch-native handler 而非旧适配器
- **setup-ts-deep-modules**（第三方·mattpocock/skills·已验证 2026-08-23）— 接入 dependency-cruiser，强制 TS 包深模块化、隐藏内部实现
  边界：仅 TS monorepo
- **wl-plan-eng-review**（自研·已验证 2026-09-01）— 从架构、影响域、接口、数据、安全、性能、迁移、回滚和测试等维度审查实施计划
  边界：只做编码前的工程方案审查，不直接实施计划或替代代码审查

## 测试
- **migrate-to-shoehorn**（第三方·mattpocock/skills·已验证 2026-08-23）— 把测试文件里的 as 类型断言迁移到 @total-typescript/shoehorn
  边界：仅 TS 测试数据场景
- **tdd**（第三方·mattpocock/skills·已验证 2026-08-23）— 测试驱动开发：red-green-refactor，集成测试优先
  边界：需要项目已有测试基建
- **wl-browse**（自研·已验证 2026-09-01）— 通过真实浏览器完成页面导航、DOM 快照、表单交互、截图、响应式检查和端到端验证
  边界：仅负责浏览器自动化与视觉验证；使用自带 CLI，不依赖 gstack
- **wl-investigate**（自研·已验证 2026-09-01）— 以证据优先和根因分析方式独立复现、定位并修复缺陷或回归
  边界：仅用于缺陷诊断与修复；修复前必须有失败复现，修复后必须验证
- **wl-subagent-driven-development**（自研·已验证 2026-09-01）— 按已批准计划逐任务调度隔离 Worker，以测试优先、规格审查和质量审查完成开发
  边界：仅在方案已批准后使用；子 Agent 未获授权或不可用时必须在本地执行同等闸门
- **wl-writing-plans**（自研·已验证 2026-09-01）— 将已批准规格或稳定需求转换为详细、测试优先的实施计划
  边界：仅用于多步骤工程任务；需求或架构尚未确定时不得使用

## 浏览器
- **wl-browse**（自研·已验证 2026-09-01）— 通过真实浏览器完成页面导航、DOM 快照、表单交互、截图、响应式检查和端到端验证
  边界：仅负责浏览器自动化与视觉验证；使用自带 CLI，不依赖 gstack

## 研究
- **deepagents-docs**（自研·已验证 2026-08-21）— 查询并核验 DeepAgents 官方文档、API、版本差异和长尾问题
  边界：不替代入门、执行环境、上下文记忆或子 Agent 的稳定决策规则
- **framework-skill-author**（自研·已验证 2026-08-21）— 基于框架官方文档、API、版本记录和源码创建、刷新或审计可追溯的中文 Skill Pack
  边界：不用于普通文档摘要，也不接受非官方资料作为核心依据
- **research**（第三方·mattpocock/skills·已验证 2026-08-23）— 对着高可信一手资料做调研，结论落盘为 repo 里的 markdown
  边界：需要网络访问；不做观点创作

## 编程
- **a2ui-renderer**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 在 CopilotKit v2 中接入和渲染 A2UI 声明式界面，覆盖运行时、Provider、主题与动作桥接
  边界：仅处理 A2UI 渲染链路，不替代通用前端设计；依赖 CopilotKit v2 与对应 npm 包
- **channels-setup**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 从零搭建可在 Slack 或 Microsoft Teams 响应消息的 CopilotKit Channels Agent
  边界：端到端初始化流程会在运行时读取官方在线指南，并依赖 CopilotKit CLI、托管 Channel 与平台配置
- **code-review**（第三方·mattpocock/skills·已验证 2026-08-23）— 从固定点（commit/branch/tag）起审 diff：编码规范 + 是否符合 spec 双轴并行
  边界：只审不改
- **copilotkit-agui**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 实现和调试 AG-UI 协议、自定义 Agent 后端、SSE 事件流、状态同步与人机协同
  边界：聚焦 Agent 与前端通信协议，不负责 CopilotKit React 界面组件的具体使用
- **copilotkit-channels**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 编写和定制 CopilotKit 托管 Channel 的声明、常驻 Host 与激活逻辑
  边界：只覆盖 Channel 代码侧；首次创建 Slack App 应改用 setup-slack-channel
- **copilotkit-contribute**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 指导参与 CopilotKit 开源仓库开发：Fork、环境搭建、分支、测试与提交 PR
  边界：仅面向 CopilotKit/CopilotKit 上游贡献，不是业务项目的通用 Git 工作流
- **copilotkit-develop**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 使用 CopilotKit v2 开发聊天界面、前端工具、上下文共享、Agent 中断与运行时能力
  边界：面向已有或正在建设的 v2 功能；首次初始化和版本迁移分别使用 setup、upgrade Skill
- **copilotkit-integrations**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 通过 AG-UI 将 LangGraph、CrewAI、PydanticAI、Mastra 等外部 Agent 框架接入 CopilotKit
  边界：只处理外部 Agent 框架集成，不覆盖 CopilotKit 前端组件或常规运行时开发
- **copilotkit-setup**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 在现有项目接入 CopilotKit 或从零初始化，完成依赖、运行时、Provider 与首个聊天链路
  边界：用于首次搭建；CopilotKit v1 到 v2 的存量迁移应使用 copilotkit-upgrade
- **copilotkit-upgrade**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 将 CopilotKit v1 应用迁移到 v2，处理包导入、废弃 API、组件与 AG-UI 运行时变更
  边界：仅适用于 v1 到 v2 迁移，不负责新项目初始化或普通依赖升级
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
- **fastapi**（第三方·fastapi/fastapi·**待验证（未安装）**）— 遵循 FastAPI 官方最佳实践编写 API、Pydantic 模型、依赖注入、流式响应、SSE 与前端资源服务代码
  边界：跟随 FastAPI master 分支的最新模式；用于较旧固定版本时需先核对 API 兼容性，不替代具体业务架构设计
- **framework-skill-author**（自研·已验证 2026-08-21）— 基于框架官方文档、API、版本记录和源码创建、刷新或审计可追溯的中文 Skill Pack
  边界：不用于普通文档摘要，也不接受非官方资料作为核心依据
- **git-guardrails-claude-code**（第三方·mattpocock/skills·已验证 2026-08-23）— 给 Claude Code 配 git 安全 hook，拦截 push/reset --hard/clean 等危险命令
  边界：只防 git 危险操作，不管其他命令
- **implement**（第三方·mattpocock/skills·已验证 2026-08-23）— 按 spec 或 ticket 实现具体工作
  边界：需要已有 spec/ticket，不做需求澄清
- **inspector-docs**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 维护 CopilotKit Inspector 文档与已发布 Pane、Tab、Overlay 行为的一致性
  边界：仅服务 CopilotKit 上游 Inspector 文档维护，不用于 Inspector UI 润色或未发布功能设计
- **migrate-to-shoehorn**（第三方·mattpocock/skills·已验证 2026-08-23）— 把测试文件里的 as 类型断言迁移到 @total-typescript/shoehorn
  边界：仅 TS 测试数据场景
- **prototype**（第三方·mattpocock/skills·已验证 2026-08-23）— 快速搭一次性原型，验证状态模型逻辑或 UI 感觉
  边界：是 throwaway 代码，别当正式实现
- **react-core**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 使用 @copilotkit/react-core/v2 接入 Provider、聊天组件、Agent、线程、工具、附件与渲染器
  边界：只覆盖 React 前端核心 API，不处理服务端 CopilotRuntime 或外部 Agent 框架集成
- **resolving-merge-conflicts**（第三方·mattpocock/skills·已验证 2026-08-23）— 解决进行中的 git merge/rebase 冲突
  边界：只管冲突解决这一步
- **runtime**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 使用 @copilotkit/runtime 搭建服务端 CopilotRuntime、AgentRunner、工具、Intelligence 与语音转录
  边界：聚焦服务端运行时，不负责 React 前端组件；优先采用 fetch-native handler 而非旧适配器
- **setup-pre-commit**（第三方·mattpocock/skills·已验证 2026-08-23）— 配置 Husky pre-commit：lint-staged、Prettier、类型检查、测试
  边界：仅 JS/TS 仓库
- **setup-slack-channel**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 完成 CopilotKit Channels 的 Slack Provider 侧首次配置、Token、托管 Channel 绑定与连通性验证
  边界：只覆盖首次 Slack Provider 配置，且主要适配 OpenTag 或 channels-sdk 示例约定；Channel 代码定制用 copilotkit-channels
- **setup-ts-deep-modules**（第三方·mattpocock/skills·已验证 2026-08-23）— 接入 dependency-cruiser，强制 TS 包深模块化、隐藏内部实现
  边界：仅 TS monorepo
- **tdd**（第三方·mattpocock/skills·已验证 2026-08-23）— 测试驱动开发：red-green-refactor，集成测试优先
  边界：需要项目已有测试基建

## 自动化
- **wl-browse**（自研·已验证 2026-09-01）— 通过真实浏览器完成页面导航、DOM 快照、表单交互、截图、响应式检查和端到端验证
  边界：仅负责浏览器自动化与视觉验证；使用自带 CLI，不依赖 gstack

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
- **wl-plan-eng-review**（自研·已验证 2026-09-01）— 从架构、影响域、接口、数据、安全、性能、迁移、回滚和测试等维度审查实施计划
  边界：只做编码前的工程方案审查，不直接实施计划或替代代码审查
- **wl-writing-plans**（自研·已验证 2026-09-01）— 将已批准规格或稳定需求转换为详细、测试优先的实施计划
  边界：仅用于多步骤工程任务；需求或架构尚未确定时不得使用

## 设计
- **prototype**（第三方·mattpocock/skills·已验证 2026-08-23）— 快速搭一次性原型，验证状态模型逻辑或 UI 感觉
  边界：是 throwaway 代码，别当正式实现
- **wl-brainstorming**（自研·已验证 2026-09-01）— 将模糊的软件想法或行为变更澄清为经确认、可测试的设计
  边界：用于新功能或显著行为变更的需求与设计定稿，不执行已经批准的实现方案
- **wl-plan-design-review**（自研·已验证 2026-09-01）— 在编码前审查并完善 UI/UX 实施计划，使交互和视觉决策达到可实施状态
  边界：只审查前端体验与设计计划，不替代工程架构评审或代码实现

## 调试
- **copilotkit-agui**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 实现和调试 AG-UI 协议、自定义 Agent 后端、SSE 事件流、状态同步与人机协同
  边界：聚焦 Agent 与前端通信协议，不负责 CopilotKit React 界面组件的具体使用
- **copilotkit-debug**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 诊断 CopilotKit 连接、流式响应、工具调用、转录、版本及 AG-UI 事件问题
  边界：聚焦故障定位，不负责首次接入、功能开发或 v1 到 v2 迁移
- **diagnosing-bugs**（第三方·mattpocock/skills·已验证 2026-08-23）— 疑难 bug 和性能回退的结构化诊断循环
  边界：针对难治问题；简单 bug 不必动用
- **wl-investigate**（自研·已验证 2026-09-01）— 以证据优先和根因分析方式独立复现、定位并修复缺陷或回归
  边界：仅用于缺陷诊断与修复；修复前必须有失败复现，修复后必须验证

## 质量
- **wl-requesting-code-review**（自研·已验证 2026-09-01）— 在交付前依据需求、架构、风险与测试证据审查已完成的代码
  边界：用于完整任务或重要功能实现后的代码审查，不用于需求澄清或方案设计

## 运维
- **copilotkit-self-update**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 刷新或重装 CopilotKit 官方 Agent Skills，使本地知识与最新 API 保持同步
  边界：只更新 CopilotKit Skills，不升级业务依赖；其官方安装命令会直接写 Agent 加载目录，可能绕过本仓库登记流程
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

## 需求分析
- **wl-brainstorming**（自研·已验证 2026-09-01）— 将模糊的软件想法或行为变更澄清为经确认、可测试的设计
  边界：用于新功能或显著行为变更的需求与设计定稿，不执行已经批准的实现方案
