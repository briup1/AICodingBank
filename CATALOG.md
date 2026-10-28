# Skill 总目录（install.py 自动生成，勿手改）

共 88 个 · 已验证 63 · 待验证 25

想看深度使用经验 → wiki entity 页；想改行为 → SKILL.md；本目录只回答“它能干什么、边界在哪”。

## Docker
- **wl-docker-port-registry**（自研·已验证 2026-10-03）— 用 lsof/docker ps/curl 三板斧查明本机端口占用真身，并按 3000-3099 段 10 位槽位规则为新服务分配宿主端口、登记本机台账并显式写入项目 .env
  边界：只管宿主端口查询、分配与登记；不管理容器生命周期、不改在跑服务端口、不执行清理操作；台账只记分配决策，实时占用以查询为准

## Git
- **hgj-git-connect**（自研·已验证 2026-09-24）— 诊断并切换公司 GitLab 的直连与 SSH 跳板路由，优先用只读检查确认当前可用链路
  边界：仅处理本机 GitLab SSH 连接与路由，不替代需求分支、合并、评审、发布或权限申请；不自动修改 known_hosts、不自动执行 pull/push
- **wl-git-flow**（自研·已验证 2026-09-22）— 从最新 master 安全创建和单向集成需求分支，并以用户级静态/localhost 实时 HTML 看板聚合多项目 Worktree、Git 生命周期与异常
  边界：看板只监控和刷新，不启动 Agent 或执行 Git 写操作；测试和上线结果需真实确认；清理只删除 Worktree 目录，不删除本地或远端分支；Dev 和 Beta 只接收需求分支；上线走 release/yyyymmdd，发布成功后由 CI/CD 合进 master

## SSH
- **hgj-git-connect**（自研·已验证 2026-09-24）— 诊断并切换公司 GitLab 的直连与 SSH 跳板路由，优先用只读检查确认当前可用链路
  边界：仅处理本机 GitLab SSH 连接与路由，不替代需求分支、合并、评审、发布或权限申请；不自动修改 known_hosts、不自动执行 pull/push

## compass-platform
- **wl-compass-local-test**（自研·已验证 2026-10-09）— compass-platform 本地自测环境一站式搭建与验证——本地 jar 起后端、vite 起前端、本地 RocketMQ 隔离 dev MQ，连 dev 库与外部依赖，含鉴权配方与全部已知坑解法
  边界：仅覆盖 compass-platform 后端/前端/Bot 的本地进程+dev 数据自测模式；不替代 dev 部署验收、小程序真机验证、SPOT 实时创建（IP 白名单受限）；dev 库写入只走业务 API

## 代码审查
- **wl-requesting-code-review**（自研·已验证 2026-09-01）— 在交付前依据需求、架构、风险与测试证据审查已完成的代码
  边界：完整实现后的代码审查；主链使用focused-delivery仅核设计偏离和交付阻断，full模式独立可用，委派按wl-herdrs，不用于需求澄清或方案设计

## 企业集成
- **wl-external-enterprise-auth**（自研·已验证 2026-10-17）— 为独立项目接入外部企业账号体系，并把外部身份映射为本地会话、企业归属、执行主体和授权快照
  边界：提供通用接入流程、Provider 契约、安全检查和测试矩阵；不保存凭证，不替代目标项目授权模型，不直接操作外部公司系统

## 写作
- **inspector-docs**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 维护 CopilotKit Inspector 文档与已发布 Pane、Tab、Overlay 行为的一致性
  边界：仅服务 CopilotKit 上游 Inspector 文档维护，不用于 Inspector UI 润色或未发布功能设计
- **wl-req-change-tree**（自研·已验证 2026-10-19）— 把原始需求整理成理解优先的业务变化树，展开交互、逻辑和数据语义并保留来源
  边界：只做文本结构化，不自动进入需求确认、技术设计、开发或测试流程；跨模型稳定性按实测范围判断

## 前端
- **wl-plan-design-review**（自研·已验证 2026-09-01）— 在编码前审查并完善 UI/UX 实施计划，使交互和视觉决策达到可实施状态
  边界：只审查前端体验与设计计划，不替代工程架构评审或代码实现

## 协作
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
- **herdr**（第三方·herdrdev/herdr@v0.8.2·已验证 2026-09-01）— 在 Herdr 管理的终端会话内检查和控制 workspace、tab、pane、命令与编码 Agent
  边界：仅在用户明确提及 Herdr 且 HERDR_ENV=1 时使用；依赖本机 herdr CLI，不替代通用终端或子 Agent 调度
- **orchestration**（第三方·stablyai/orca@071747853f5995ee233b36751613f09a60007c2b·**待验证（未安装）**）— 通过 Orca 协调多个受监督 Agent，管理消息、任务依赖、决策门禁和结果回收
  边界：依赖本机 Orca CLI 与真实运行态，不替代既有委派授权；已由 skills CLI 定向安装到 Pi/Codex/OpenCode/Hermes 并验证指南读取，未验证多 Agent 调度；工作台安装器尚未启用
- **setup-slack-channel**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 完成 CopilotKit Channels 的 Slack Provider 侧首次配置、Token、托管 Channel 绑定与连通性验证
  边界：只覆盖首次 Slack Provider 配置，且主要适配 OpenTag 或 channels-sdk 示例约定；Channel 代码定制用 copilotkit-channels
- **triage**（第三方·mattpocock/skills·已验证 2026-08-23）— issue 和外部 PR 的分诊状态机：分类、验证、追问，产出 agent 可直接执行的简报
  边界：面向开源仓库维护场景
- **visual-artifact-workbench**（自研·**待验证（未安装）**）— 统一跨项目可视文档的分类、原文证据、审核版本和本机分享处理方案
  边界：提供策略与白名单只读分享脚本，无通用发布CLI、认证或多人审核后台；不替代业务确认，不自动开放局域网
- **wl-herdrs**（自研·已验证 2026-10-10）— 定义一层委派的个人策略，默认 Herdr 启动 Pi/high，不可用时允许当前宿主获准的原生 subagent
  边界：仅定义行为约定；Herdr 通道依赖 HERDR_ENV=1 与当前 CLI，备用通道须实际可用，不绕过用户禁令、审批拒绝或资源访问限制

## 图表
- **diagram**（第三方·312362115/claude·已验证 2026-08-23）— 生成 29 种专业 PNG 图表：流程/时序/架构/ER/甘特 + 柱线饼雷等统计图，统一设计规范
  边界：HTML/SVG+JS 渲染输出 PNG，非矢量源文件
- **excalidraw-diagram-generator**（第三方·p-rp/excalidraw-diagram-generator·已验证 2026-08-23）— 自然语言生成 Excalidraw 图：流程图、架构图、思维导图、关系图
  边界：输出 .excalidraw JSON，需 Excalidraw 打开查看
- **visual-artifact-workbench**（自研·**待验证（未安装）**）— 统一跨项目可视文档的分类、原文证据、审核版本和本机分享处理方案
  边界：提供策略与白名单只读分享脚本，无通用发布CLI、认证或多人审核后台；不替代业务确认，不自动开放局域网

## 多智能体
- **wl-subagent-driven-development**（自研·已验证 2026-09-01）— 可选逐任务隔离执行——按已批准计划以测试优先、逐任务规格审查和质量审查完成开发
  边界：非默认，仅用户或项目规则显式选择此执行粒度且实施获准时使用；不与工作包循环叠加，委派按wl-herdrs，本地执行不冒充独立审查

## 安全
- **wl-external-enterprise-auth**（自研·已验证 2026-10-17）— 为独立项目接入外部企业账号体系，并把外部身份映射为本地会话、企业归属、执行主体和授权快照
  边界：提供通用接入流程、Provider 契约、安全检查和测试矩阵；不保存凭证，不替代目标项目授权模型，不直接操作外部公司系统

## 审查
- **wl-design-reachability-review**（自研·**待验证（未安装）**）— 从已实现的真实原点沿方案流程、状态和契约逐跳思维实验，证明需求终点是否可达
  边界：只发现设计 Gap、对接断点及不成立假设，不做泛化工程评审、不实现代码或扩大需求
- **wl-plan-design-review**（自研·已验证 2026-09-01）— 在编码前审查并完善 UI/UX 实施计划，使交互和视觉决策达到可实施状态
  边界：只审查前端体验与设计计划，不替代工程架构评审或代码实现
- **wl-plan-eng-review**（自研·已验证 2026-09-01）— 从架构、影响域、接口、数据、安全、性能、迁移、回滚和测试等维度审查实施计划
  边界：只做编码前的工程方案审查，不直接实施计划或替代代码审查

## 开发流程
- **wl-auto-delivery**（自研·已验证 2026-10-19）— WL默认主链——按当前阶段衔接需求/用例、独立审查、方案决策、工作包持续开发、聚焦Review与目标环境验收
  边界：只读和简单任务不强制全流程；其他设计/规划/隔离执行路线须显式选择，不叠加第二套流程；不重复有效批准，委托不替代操作授权，历史验证不证明本次优化已实测
- **wl-brainstorming**（自研·已验证 2026-09-01）— 独立设计路线——澄清软件想法并形成经确认、可测试的设计
  边界：非默认，仅用户或项目规则显式选择时使用；普通新功能走wl-auto-delivery，不叠加已有需求/方案流程，不执行实现
- **wl-design-doc**（自研·已验证 2026-08-31）— 方案设计——按业务场景组织目标、现状事实、最小例子、业务流程、技术承接、专项适用性与验收，生成可批准的单文件HTML
  边界：需求已批准；只出方案不写实现代码，默认人工批准本版，明确委托且边界与证据齐全时可采用推荐；不授予实施或外部操作权限
- **wl-git-flow**（自研·已验证 2026-09-22）— 从最新 master 安全创建和单向集成需求分支，并以用户级静态/localhost 实时 HTML 看板聚合多项目 Worktree、Git 生命周期与异常
  边界：看板只监控和刷新，不启动 Agent 或执行 Git 写操作；测试和上线结果需真实确认；清理只删除 Worktree 目录，不删除本地或远端分支；Dev 和 Beta 只接收需求分支；上线走 release/yyyymmdd，发布成功后由 CI/CD 合进 master
- **wl-harness-setup**（自研·**待验证（未安装）**）— 调查主要模块、能力与边界，建立能指导新增和修改代码的项目规则与Wiki，并做内容可接手回读
  边界：复用已有Owner、按声明范围调查；结构检查不代替内容验收；不改业务代码、不建账号数据库、不自动提交或安装；个人测试密码只进获准忽略文件
- **wl-harness-sync**（自研·**待验证（未安装）**）— 按本次变化维护规则与Wiki，补齐首次实现使初始化暂缺项失效的资料，并核对受影响任务仍可接手
  边界：不要求先运行setup、不全库审计或重建；共用结构与内容标准；历史异构资料迁移另确认；不改业务代码、不读取真实密码、不自动提交或安装
- **wl-herdrs**（自研·已验证 2026-10-10）— 定义一层委派的个人策略，默认 Herdr 启动 Pi/high，不可用时允许当前宿主获准的原生 subagent
  边界：仅定义行为约定；Herdr 通道依赖 HERDR_ENV=1 与当前 CLI，备用通道须实际可用，不绕过用户禁令、审批拒绝或资源访问限制
- **wl-investigate**（自研·已验证 2026-09-01）— 以证据优先和根因分析方式独立复现、定位并修复缺陷或回归
  边界：仅用于缺陷诊断与修复；修复前必须有失败复现，修复后必须验证
- **wl-prod-db**（自研·已验证 2026-09-23）— 查询海管家生产 MySQL 和生产 Mongo。MySQL 走 opencli yearning，Mongo 走 opencli archery
  边界：不查 dev/beta 日志，不替代 agent-tools fuxi；MySQL 只收带 LIMIT 的 SELECT，Mongo 只收 prd-mongo 上的 find 一类只读语句，返回行数 1 到 1000
- **wl-req-change-tree**（自研·已验证 2026-10-19）— 把原始需求整理成理解优先的业务变化树，展开交互、逻辑和数据语义并保留来源
  边界：只做文本结构化，不自动进入需求确认、技术设计、开发或测试流程；跨模型稳定性按实测范围判断
- **wl-req-confirm**（自研·已验证 2026-08-31）— 需求确认——把模糊诉求变成人审批准的《需求确认文档》（重定义需求/用户故事/Out of Scope/验收）
  边界：只回答要什么/为什么/怎么算完成，不回答怎么做（方案设计归 wl-design-doc）
- **wl-requesting-code-review**（自研·已验证 2026-09-01）— 在交付前依据需求、架构、风险与测试证据审查已完成的代码
  边界：完整实现后的代码审查；主链使用focused-delivery仅核设计偏离和交付阻断，full模式独立可用，委派按wl-herdrs，不用于需求澄清或方案设计
- **wl-subagent-driven-development**（自研·已验证 2026-09-01）— 可选逐任务隔离执行——按已批准计划以测试优先、逐任务规格审查和质量审查完成开发
  边界：非默认，仅用户或项目规则显式选择此执行粒度且实施获准时使用；不与工作包循环叠加，委派按wl-herdrs，本地执行不冒充独立审查
- **wl-ticket-run**（自研·已验证 2026-08-31）— 工单执行——引用已确认用例拆垂直 Ticket，按耦合组合工作包，由持续负责人开发、聚焦测试和Review后在约定环境验收
  边界：前置本版方案人工批准或合法委托采用且实施获准；不重做需求/方案决策，不默认一票一Agent，goal/list可选，提交发布另需授权
- **wl-writing-plans**（自研·已验证 2026-09-01）— 可选详细规划——将已批准规格或稳定需求转换为测试优先的实施计划
  边界：非默认，仅用户或项目规则显式选择此计划格式时使用；复用已有清单，不默认串接隔离Worker执行，未决需求/架构回实际来源阶段

## 效率
- **ask-matt**（第三方·mattpocock/skills·已验证 2026-08-23）— 在 mattpocock 全家桶里帮你选合适的 skill 或流程
  边界：只是路由器，本身不执行具体工作
- **copilotkit-self-update**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 刷新或重装 CopilotKit 官方 Agent Skills，使本地知识与最新 API 保持同步
  边界：只更新 CopilotKit Skills，不升级业务依赖；其官方安装命令会直接写 Agent 加载目录，可能绕过本仓库登记流程
- **deepagents-subagents**（自研·已验证 2026-08-21）— 设计 DeepAgents 同步、动态和异步子 Agent 委派及并发取消语义
  边界：不处理一般 backend 权限或单 Agent 入门
- **find-skills**（第三方·vercel-labs/skills@v1.7.4·已验证 2026-10-24）— 根据需求搜索开放 Skill 生态，核对来源并提供安装建议
  边界：依赖 Node.js、npx skills 和联网；已实测搜索，只定向安装到 Pi，安装其他技能仍需用户授权，不批量更新
- **goal-coach**（自研·已验证 2026-08-23）— 判断任务是否适合 /goal，并生成完整中文 /goal prompt（完成标准/边界/停止规则）
  边界：只服务 Claude Code 的 /goal 命令场景
- **herdr**（第三方·herdrdev/herdr@v0.8.2·已验证 2026-09-01）— 在 Herdr 管理的终端会话内检查和控制 workspace、tab、pane、命令与编码 Agent
  边界：仅在用户明确提及 Herdr 且 HERDR_ENV=1 时使用；依赖本机 herdr CLI，不替代通用终端或子 Agent 调度
- **visual-artifact-workbench**（自研·**待验证（未安装）**）— 统一跨项目可视文档的分类、原文证据、审核版本和本机分享处理方案
  边界：提供策略与白名单只读分享脚本，无通用发布CLI、认证或多人审核后台；不替代业务确认，不自动开放局域网
- **wl-harness-sync**（自研·**待验证（未安装）**）— 按本次变化维护规则与Wiki，补齐首次实现使初始化暂缺项失效的资料，并核对受影响任务仍可接手
  边界：不要求先运行setup、不全库审计或重建；共用结构与内容标准；历史异构资料迁移另确认；不改业务代码、不读取真实密码、不自动提交或安装
- **wl-herdrs**（自研·已验证 2026-10-10）— 定义一层委派的个人策略，默认 Herdr 启动 Pi/high，不可用时允许当前宿主获准的原生 subagent
  边界：仅定义行为约定；Herdr 通道依赖 HERDR_ENV=1 与当前 CLI，备用通道须实际可用，不绕过用户禁令、审批拒绝或资源访问限制

## 教学
- **deepagents-getting-started**（自研·已验证 2026-08-21）— 提供 DeepAgents 0.7.8 的最小闭环、总体架构和核心组件选型规则
  边界：不处理具体后端安全、子 Agent 拆分或版本敏感 API 查询
- **scaffold-exercises**（第三方·mattpocock/skills·已验证 2026-08-23）— 脚手架生成练习目录：分节、题目、答案、讲解，过 lint
  边界：面向课程/教学内容制作
- **teach**（第三方·mattpocock/skills·已验证 2026-08-23）— 在工作区内教会你一个技能或概念
  边界：教学对话，不产出工程代码

## 数据库
- **wl-prod-db**（自研·已验证 2026-09-23）— 查询海管家生产 MySQL 和生产 Mongo。MySQL 走 opencli yearning，Mongo 走 opencli archery
  边界：不查 dev/beta 日志，不替代 agent-tools fuxi；MySQL 只收带 LIMIT 的 SELECT，Mongo 只收 prd-mongo 上的 find 一类只读语句，返回行数 1 到 1000

## 未分类
- **langfuse**（第三方·langfuse/skills·**待验证（未安装）**）—

## 本地测试
- **wl-compass-local-test**（自研·已验证 2026-10-09）— compass-platform 本地自测环境一站式搭建与验证——本地 jar 起后端、vite 起前端、本地 RocketMQ 隔离 dev MQ，连 dev 库与外部依赖，含鉴权配方与全部已知坑解法
  边界：仅覆盖 compass-platform 后端/前端/Bot 的本地进程+dev 数据自测模式；不替代 dev 部署验收、小程序真机验证、SPOT 实时创建（IP 白名单受限）；dev 库写入只走业务 API

## 本机工具
- **hgj-git-connect**（自研·已验证 2026-09-24）— 诊断并切换公司 GitLab 的直连与 SSH 跳板路由，优先用只读检查确认当前可用链路
  边界：仅处理本机 GitLab SSH 连接与路由，不替代需求分支、合并、评审、发布或权限申请；不自动修改 known_hosts、不自动执行 pull/push
- **wl-docker-port-registry**（自研·已验证 2026-10-03）— 用 lsof/docker ps/curl 三板斧查明本机端口占用真身，并按 3000-3099 段 10 位槽位规则为新服务分配宿主端口、登记本机台账并显式写入项目 .env
  边界：只管宿主端口查询、分配与登记；不管理容器生命周期、不改在跑服务端口、不执行清理操作；台账只记分配决策，实时占用以查询为准

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
- **wl-design-reachability-review**（自研·**待验证（未安装）**）— 从已实现的真实原点沿方案流程、状态和契约逐跳思维实验，证明需求终点是否可达
  边界：只发现设计 Gap、对接断点及不成立假设，不做泛化工程评审、不实现代码或扩大需求
- **wl-harness-setup**（自研·**待验证（未安装）**）— 调查主要模块、能力与边界，建立能指导新增和修改代码的项目规则与Wiki，并做内容可接手回读
  边界：复用已有Owner、按声明范围调查；结构检查不代替内容验收；不改业务代码、不建账号数据库、不自动提交或安装；个人测试密码只进获准忽略文件
- **wl-plan-eng-review**（自研·已验证 2026-09-01）— 从架构、影响域、接口、数据、安全、性能、迁移、回滚和测试等维度审查实施计划
  边界：只做编码前的工程方案审查，不直接实施计划或替代代码审查

## 测试
- **qa-test-planner**（第三方·softaworks/agent-toolkit·**待验证（未安装）**）— 为 wl-qa-test-planner 提供上游测试用例模板与设计参考
  边界：仅作为按需来源缓存，不全局安装；个人入口只读取测试用例模板，不启用 Bug 报告、Figma、排期或脚本
- **tdd**（第三方·mattpocock/skills·已验证 2026-08-23）— 测试驱动开发：red-green-refactor，集成测试优先
  边界：需要项目已有测试基建
- **wl-browse**（自研·已验证 2026-09-01）— 通过真实浏览器完成页面导航、DOM 快照、表单交互、截图、响应式检查和端到端验证
  边界：仅负责浏览器自动化与视觉验证；使用自带 CLI，不依赖 gstack
- **wl-investigate**（自研·已验证 2026-09-01）— 以证据优先和根因分析方式独立复现、定位并修复缺陷或回归
  边界：仅用于缺陷诊断与修复；修复前必须有失败复现，修复后必须验证
- **wl-qa-test-planner**（自研·已验证 2026-10-20）— 根据需求生成带页面入口、场景、具体数据和编号树步骤的简洁手工用例，每步紧跟预期并保留需求追踪
  边界：仅生成用例、覆盖缺口及文档静态校验；不执行业务测试或写入，不猜页面地址，不做排期、Bug 报告或Figma校验；上游模板按需读取
- **wl-subagent-driven-development**（自研·已验证 2026-09-01）— 可选逐任务隔离执行——按已批准计划以测试优先、逐任务规格审查和质量审查完成开发
  边界：非默认，仅用户或项目规则显式选择此执行粒度且实施获准时使用；不与工作包循环叠加，委派按wl-herdrs，本地执行不冒充独立审查
- **wl-web-auto**（自研·**待验证（未安装）**）— 使用 Ego TaskSpace/Page 执行网页探索、查询、填表和核验，支持后台页面操作与独立任务并发，保留身份核对、测试记录、截图与人工交接
  边界：依赖本机 ego-browser Skill 与原生控制权规则；本地双页已验证，真实站点待验证；同页串行，并发受资源与网站业务配额限制，不设通用数字上限；业务写入需明确授权，不静默回退其他驱动或接管历史空间
- **wl-writing-plans**（自研·已验证 2026-09-01）— 可选详细规划——将已批准规格或稳定需求转换为测试优先的实施计划
  边界：非默认，仅用户或项目规则显式选择此计划格式时使用；复用已有清单，不默认串接隔离Worker执行，未决需求/架构回实际来源阶段

## 浏览器
- **wl-browse**（自研·已验证 2026-09-01）— 通过真实浏览器完成页面导航、DOM 快照、表单交互、截图、响应式检查和端到端验证
  边界：仅负责浏览器自动化与视觉验证；使用自带 CLI，不依赖 gstack
- **wl-prod-logs**（自研·**待验证（未安装）**）— 用户主动调用时使用 Ego 只读查询伏羲生产服务 Loki 日志并分析
  边界：不自动调用、不依赖 wl-web-auto、不发布或修改生产；仅指定范围，未证实分页完整及其他筛选能力
- **wl-web-auto**（自研·**待验证（未安装）**）— 使用 Ego TaskSpace/Page 执行网页探索、查询、填表和核验，支持后台页面操作与独立任务并发，保留身份核对、测试记录、截图与人工交接
  边界：依赖本机 ego-browser Skill 与原生控制权规则；本地双页已验证，真实站点待验证；同页串行，并发受资源与网站业务配额限制，不设通用数字上限；业务写入需明确授权，不静默回退其他驱动或接管历史空间

## 研究
- **deepagents-docs**（自研·已验证 2026-08-21）— 查询并核验 DeepAgents 官方文档、API、版本差异和长尾问题
  边界：不替代入门、执行环境、上下文记忆或子 Agent 的稳定决策规则
- **framework-skill-author**（自研·已验证 2026-08-21）— 基于框架官方文档、API、版本记录和源码创建、刷新或审计可追溯的中文 Skill Pack
  边界：不用于普通文档摘要，也不接受非官方资料作为核心依据
- **research**（第三方·mattpocock/skills·已验证 2026-08-23）— 对着高可信一手资料做调研，结论落盘为 repo 里的 markdown
  边界：需要网络访问；不做观点创作

## 端口管理
- **wl-docker-port-registry**（自研·已验证 2026-10-03）— 用 lsof/docker ps/curl 三板斧查明本机端口占用真身，并按 3000-3099 段 10 位槽位规则为新服务分配宿主端口、登记本机台账并显式写入项目 .env
  边界：只管宿主端口查询、分配与登记；不管理容器生命周期、不改在跑服务端口、不执行清理操作；台账只记分配决策，实时占用以查询为准

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
- **high-end-visual-design**（第三方·Leonxlnx/taste-skill·已验证 2026-08-14）— 为现有或新建网站应用高端设计规范，统一字体、间距、阴影、卡片和动效质感
  边界：只提供视觉设计约束与实现指导，不负责业务逻辑、品牌资产授权或可用性研究
- **implement**（第三方·mattpocock/skills·已验证 2026-08-23）— 按 spec 或 ticket 实现具体工作
  边界：需要已有 spec/ticket，不做需求澄清
- **inspector-docs**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 维护 CopilotKit Inspector 文档与已发布 Pane、Tab、Overlay 行为的一致性
  边界：仅服务 CopilotKit 上游 Inspector 文档维护，不用于 Inspector UI 润色或未发布功能设计
- **minimalist-ui**（第三方·Leonxlnx/taste-skill·已验证 2026-08-14）— 生成暖色单色、编辑排版、扁平 Bento 网格和低饱和点缀的极简界面
  边界：是特定审美风格规范，不适用于需要强品牌色、渐变、重动效或高密度后台的场景
- **prototype**（第三方·mattpocock/skills·已验证 2026-08-23）— 快速搭一次性原型，验证状态模型逻辑或 UI 感觉
  边界：是 throwaway 代码，别当正式实现
- **react-core**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 使用 @copilotkit/react-core/v2 接入 Provider、聊天组件、Agent、线程、工具、附件与渲染器
  边界：只覆盖 React 前端核心 API，不处理服务端 CopilotRuntime 或外部 Agent 框架集成
- **redesign-existing-projects**（第三方·Leonxlnx/taste-skill·已验证 2026-08-14）— 审查并重设计现有网站或应用，在不破坏功能的前提下提升视觉品质
  边界：用于已有前端的视觉改造，不替代需求分析、业务重构或完整产品设计流程
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
- **ui-ux-pro-max**（第三方·nextlevelbuilder/ui-ux-pro-max-skill@v2.15.0·已验证 2026-10-26）— 检索 UI/UX 风格、配色、字体、交互及框架指导，生成可供 AI 实施的设计规范建议
  边界：仅定向安装到 Pi；已验证本地检索与设计建议生成，不代表页面验收通过；匹配可能偏题，须核对适用性；依赖 Python 3，Pi 按 Skill 实际目录解析脚本，不使用 Claude 专用环境变量

## 联调
- **wl-compass-local-test**（自研·已验证 2026-10-09）— compass-platform 本地自测环境一站式搭建与验证——本地 jar 起后端、vite 起前端、本地 RocketMQ 隔离 dev MQ，连 dev 库与外部依赖，含鉴权配方与全部已知坑解法
  边界：仅覆盖 compass-platform 后端/前端/Bot 的本地进程+dev 数据自测模式；不替代 dev 部署验收、小程序真机验证、SPOT 实时创建（IP 白名单受限）；dev 库写入只走业务 API

## 自动化
- **wl-browse**（自研·已验证 2026-09-01）— 通过真实浏览器完成页面导航、DOM 快照、表单交互、截图、响应式检查和端到端验证
  边界：仅负责浏览器自动化与视觉验证；使用自带 CLI，不依赖 gstack
- **wl-git-flow**（自研·已验证 2026-09-22）— 从最新 master 安全创建和单向集成需求分支，并以用户级静态/localhost 实时 HTML 看板聚合多项目 Worktree、Git 生命周期与异常
  边界：看板只监控和刷新，不启动 Agent 或执行 Git 写操作；测试和上线结果需真实确认；清理只删除 Worktree 目录，不删除本地或远端分支；Dev 和 Beta 只接收需求分支；上线走 release/yyyymmdd，发布成功后由 CI/CD 合进 master
- **wl-web-auto**（自研·**待验证（未安装）**）— 使用 Ego TaskSpace/Page 执行网页探索、查询、填表和核验，支持后台页面操作与独立任务并发，保留身份核对、测试记录、截图与人工交接
  边界：依赖本机 ego-browser Skill 与原生控制权规则；本地双页已验证，真实站点待验证；同页串行，并发受资源与网站业务配额限制，不设通用数字上限；业务写入需明确授权，不静默回退其他驱动或接管历史空间

## 规划
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
- **orchestration**（第三方·stablyai/orca@071747853f5995ee233b36751613f09a60007c2b·**待验证（未安装）**）— 通过 Orca 协调多个受监督 Agent，管理消息、任务依赖、决策门禁和结果回收
  边界：依赖本机 Orca CLI 与真实运行态，不替代既有委派授权；已由 skills CLI 定向安装到 Pi/Codex/OpenCode/Hermes 并验证指南读取，未验证多 Agent 调度；工作台安装器尚未启用
- **to-spec**（第三方·mattpocock/skills·已验证 2026-08-23）— 把当前对话直接综合成 spec 并发布到 issue tracker
  边界：不做采访式追问（那是 grill 系的事）
- **to-tickets**（第三方·mattpocock/skills·已验证 2026-08-23）— 把计划/spec 拆成带依赖边的 tracer-bullet tickets，发布到 tracker
  边界：需要先配置 issue tracker
- **wayfinder**（第三方·mattpocock/skills·已验证 2026-08-23）— 把超过单个会话的大工程拆成 decision ticket 地图，逐个解决直到路径清晰
  边界：小任务用它杀鸡用牛刀
- **wl-auto-delivery**（自研·已验证 2026-10-19）— WL默认主链——按当前阶段衔接需求/用例、独立审查、方案决策、工作包持续开发、聚焦Review与目标环境验收
  边界：只读和简单任务不强制全流程；其他设计/规划/隔离执行路线须显式选择，不叠加第二套流程；不重复有效批准，委托不替代操作授权，历史验证不证明本次优化已实测
- **wl-design-reachability-review**（自研·**待验证（未安装）**）— 从已实现的真实原点沿方案流程、状态和契约逐跳思维实验，证明需求终点是否可达
  边界：只发现设计 Gap、对接断点及不成立假设，不做泛化工程评审、不实现代码或扩大需求
- **wl-harness-setup**（自研·**待验证（未安装）**）— 调查主要模块、能力与边界，建立能指导新增和修改代码的项目规则与Wiki，并做内容可接手回读
  边界：复用已有Owner、按声明范围调查；结构检查不代替内容验收；不改业务代码、不建账号数据库、不自动提交或安装；个人测试密码只进获准忽略文件
- **wl-plan-eng-review**（自研·已验证 2026-09-01）— 从架构、影响域、接口、数据、安全、性能、迁移、回滚和测试等维度审查实施计划
  边界：只做编码前的工程方案审查，不直接实施计划或替代代码审查
- **wl-writing-plans**（自研·已验证 2026-09-01）— 可选详细规划——将已批准规格或稳定需求转换为测试优先的实施计划
  边界：非默认，仅用户或项目规则显式选择此计划格式时使用；复用已有清单，不默认串接隔离Worker执行，未决需求/架构回实际来源阶段

## 设计
- **prototype**（第三方·mattpocock/skills·已验证 2026-08-23）— 快速搭一次性原型，验证状态模型逻辑或 UI 感觉
  边界：是 throwaway 代码，别当正式实现
- **wl-brainstorming**（自研·已验证 2026-09-01）— 独立设计路线——澄清软件想法并形成经确认、可测试的设计
  边界：非默认，仅用户或项目规则显式选择时使用；普通新功能走wl-auto-delivery，不叠加已有需求/方案流程，不执行实现
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
  边界：完整实现后的代码审查；主链使用focused-delivery仅核设计偏离和交付阻断，full模式独立可用，委派按wl-herdrs，不用于需求澄清或方案设计

## 跨项目复用
- **wl-external-enterprise-auth**（自研·已验证 2026-10-17）— 为独立项目接入外部企业账号体系，并把外部身份映射为本地会话、企业归属、执行主体和授权快照
  边界：提供通用接入流程、Provider 契约、安全检查和测试矩阵；不保存凭证，不替代目标项目授权模型，不直接操作外部公司系统

## 身份认证
- **wl-external-enterprise-auth**（自研·已验证 2026-10-17）— 为独立项目接入外部企业账号体系，并把外部身份映射为本地会话、企业归属、执行主体和授权快照
  边界：提供通用接入流程、Provider 契约、安全检查和测试矩阵；不保存凭证，不替代目标项目授权模型，不直接操作外部公司系统

## 运维
- **copilotkit-self-update**（第三方·CopilotKit/CopilotKit·**待验证（未安装）**）— 刷新或重装 CopilotKit 官方 Agent Skills，使本地知识与最新 API 保持同步
  边界：只更新 CopilotKit Skills，不升级业务依赖；其官方安装命令会直接写 Agent 加载目录，可能绕过本仓库登记流程
- **deepagents-execution-environment**（自研·已验证 2026-08-21）— 设计 DeepAgents backend、虚拟文件系统、sandbox、shell 和权限边界
  边界：不负责总体入门、长期记忆建模或子 Agent 拆分
- **git-guardrails-claude-code**（第三方·mattpocock/skills·已验证 2026-08-23）— 给 Claude Code 配 git 安全 hook，拦截 push/reset --hard/clean 等危险命令
  边界：只防 git 危险操作，不管其他命令
- **herdr**（第三方·herdrdev/herdr@v0.8.2·已验证 2026-09-01）— 在 Herdr 管理的终端会话内检查和控制 workspace、tab、pane、命令与编码 Agent
  边界：仅在用户明确提及 Herdr 且 HERDR_ENV=1 时使用；依赖本机 herdr CLI，不替代通用终端或子 Agent 调度
- **setup-matt-pocock-skills**（第三方·mattpocock/skills·已验证 2026-08-23）— 首次使用 mattpocock 工程 skill 前的仓库初始化：issue tracker、标签词表、文档布局
  边界：每个仓库只需跑一次
- **setup-pre-commit**（第三方·mattpocock/skills·已验证 2026-08-23）— 配置 Husky pre-commit：lint-staged、Prettier、类型检查、测试
  边界：仅 JS/TS 仓库
- **wizard**（第三方·mattpocock/skills·已验证 2026-08-23）— 生成交互式 bash 向导，引导人完成只有人能做的步骤：配密钥、CI secrets、第三方后台
  边界：agent 自己能干的活别用它
- **wl-prod-logs**（自研·**待验证（未安装）**）— 用户主动调用时使用 Ego 只读查询伏羲生产服务 Loki 日志并分析
  边界：不自动调用、不依赖 wl-web-auto、不发布或修改生产；仅指定范围，未证实分页完整及其他筛选能力

## 需求分析
- **wl-brainstorming**（自研·已验证 2026-09-01）— 独立设计路线——澄清软件想法并形成经确认、可测试的设计
  边界：非默认，仅用户或项目规则显式选择时使用；普通新功能走wl-auto-delivery，不叠加已有需求/方案流程，不执行实现
