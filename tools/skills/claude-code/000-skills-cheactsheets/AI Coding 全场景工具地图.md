---
markmap:
  colorFreezeLevel: 2
---

# AI Coding 全场景工具地图（v2 · 场景分层版）

> **使用规则**
> 1. 所有 skill 按 `包名: /skill-name` 记录，避免同名 skill 混淆。
> 2. 包名说明：
>    - `gstack:` = gstack 生态 skill（来源：`gstack-skills-cheatsheet.md`）
>    - `superpowers:` = Superpowers 纪律工作流 skill（来源：`superpowers-skills-cheatsheet.md`）
>    - `opsx:` = OpenSpec / opsx 规格驱动开发包（来源：`openspec-skills-cheatsheet.md`）
>    - `tavily:` = Tavily 搜索/抓取工具包（来源：`tavily-skills-cheatsheet.md`）
>    - `code-review-graph:` = 代码图谱审查包（来源：`code-review-graph-skills-cheatsheet.md`）
>    - `claude-plugin:` = Claude 官方 Plugins（来源：`claude-plugins-cheatsheet.md`）
>    - `standalone:` = 独立 skill，不在上述统一包中（通常位于 `~/.claude/skills/` 或本地 `claudecode_guide/skills_guide/`）
>    - `claude-code:` = Claude Code 官方内置 skill
> 3. 每个 skill 卡片包含：触发条件 → 输入 → 输出 → 推荐度 → 实测状态 → 备胎方案。

---

## 一、快速入口：我现在该用什么？

### Lane 1：产品研发主链路

#### Stage 1：需求澄清 → 产品定义

- `superpowers: /brainstorming` — 把模糊想法变成清晰方案
  - 触发：只有一个 idea，不知道怎么做
  - 输入：想法 / 目标用户 / 约束
  - 输出：问题定义 + 方案轮廓
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /office-hours`

- `opsx: /opsx:explore` — 只探索、不动代码
  - 触发：想先了解选项、风险、可行性
  - 输入：探索主题 / 约束
  - 输出：选项清单 + 风险 + 建议
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`superpowers: /brainstorming`

- `standalone: /user-story` — 生成用户故事与验收标准
  - 触发：需要把需求写成可验收格式
  - 输入：功能描述 / 用户角色
  - 输出：User Story + Gherkin 验收标准
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：OpenSpec specs

- `standalone: /roadmap-planning` — 制定路线图与优先级
  - 触发：需要排期、分里程碑
  - 输入：需求列表 / 资源 / 截止时间
  - 输出：Roadmap + 里程碑
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /office-hours`

- 产品计划多视角审查
  - `gstack: /plan-ceo-review` — CEO 视角
  - `gstack: /plan-design-review` — 设计视角
  - `gstack: /plan-eng-review` — 工程视角
  - `gstack: /autoplan` — 全自动计划

#### Stage 2：PRD 与规格驱动开发

- `opsx: /opsx:propose` — 创建完整规格方案
  - 触发：从 0 到 1 定义一个功能
  - 输入："我想做某功能"
  - 输出：proposal / specs / design / tasks
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`opsx: /opsx:new`

- `opsx: /opsx:ff` — 快速模式
  - 触发：规格简单，需要快速过
  - 输入：简短需求
  - 输出：轻量规格
  - 推荐：⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`opsx: /opsx:propose`

- `opsx: /opsx:continue` — 继续完善 Artifacts
  - 触发：一个 artifact 没写完，需要继续
  - 输入：当前 artifact / 下一步方向
  - 输出：下一个 artifact
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`opsx: openspec status`

- `opsx: /opsx:apply` — 按 tasks 实现
  - 触发：规格已确定，开始编码
  - 输入：change 名称
  - 输出：代码改动
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`superpowers: /executing-plans`

- `opsx: /opsx:verify` — 验证实现符合规格
  - 触发：代码写完后验收
  - 输入：当前改动 / 规格
  - 输出：Completeness / Correctness / Coherence 报告
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /review`

- 规格同步与归档
  - `opsx: /opsx:sync-specs` — 同步主规格
  - `opsx: /opsx:archive` — 单个归档
  - `opsx: /opsx:bulk-archive` — 批量归档

- Artifact 类型速查
  - `proposal` — Why / What Changes / Capabilities / Impact
  - `specs` — Requirements / Scenarios
  - `design` — Context / Goals / Decisions / Approach
  - `tasks` — Checkboxed implementation tasks

#### Stage 3：技术设计与架构

- `gstack: /plan-eng-review` — 工程架构评审
  - 触发：已有设计方案，需要工程视角审查
  - 输入：设计方案 / 代码上下文
  - 输出：架构风险 / 执行建议
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /autoplan`

- `standalone: /fullstack-dev` — 全栈架构实践
  - 触发：设计 API / DB / Auth / Error / Logging / Cache / Realtime
  - 输入：功能需求 / 技术栈
  - 输出：架构决策 + 实现模式
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /plan-eng-review`

- 全栈设计子场景
  - API 设计 → `standalone: /fullstack-dev`（关注 URL / 状态码 / 分页 / GraphQL / gRPC）
  - 数据库设计 → `standalone: /fullstack-dev`（关注 schema / index / migration / transaction / N+1）
  - 认证与权限 → `standalone: /fullstack-dev`（关注 JWT / session / RBAC / refresh token / middleware）
  - 生产化设计 → `standalone: /fullstack-dev`（关注 health check / graceful shutdown / env / secrets）

- `gstack: /plan-devex-review` — 开发者体验审查
  - 触发：关注 DX 摩擦点
  - 输入：开发流程 / 工具链
  - 输出：DX 评分 + 摩擦点 + 魔法时刻
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /devex-review`

- `code-review-graph: /code-review-graph:architecture_map` — 代码结构可视化
  - 触发：需要看模块耦合、关键执行流
  - 输入：已构建图谱
  - 输出：Mermaid 架构图 + 模块耦合分析
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`code-review-graph: /explore-codebase`

#### Stage 4：UI 与前端体验

- `standalone: /frontend-dev` — 前端工程实现
  - 触发：实现前端功能
  - 输入：需求 / 设计 / 现有代码
  - 输出：UI 架构 / 组件 / 动效 / 资产 / 质量门禁
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`standalone: /fullstack-dev`

- `gstack: /design-consultation` — 从零设计视觉系统
  - 触发：没有设计师，需要定视觉方向
  - 输入：产品感觉 / 品牌 / 目标用户
  - 输出：设计方向 + 规范
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`standalone: /frontend-dev`

- `gstack: /design-shotgun` — 多方案探索
  - 触发：需要快速看多个设计方向
  - 输入：需求 / 参考 / 约束
  - 输出：多个设计方案
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /plan-design-review`

- `gstack: /design-html` — HTML/CSS 实现
  - 触发：需要静态页面 / 视觉稿还原
  - 输入：设计稿 / 需求
  - 输出：HTML/CSS 页面
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`standalone: /frontend-dev`

- `gstack: /design-review` — 视觉质量检查
  - 触发：页面做完后检查视觉问题
  - 输入：URL / 范围 / 深度
  - 输出：视觉问题清单
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /qa`

- 前端动效选择
  - Framer Motion — UI 进出场 / layout / spring
  - GSAP ScrollTrigger — 滚动叙事 / pin / scrub
  - Lottie — 循环图标
  - Three.js / R3F — 3D / WebGL
  - CSS — hover / focus / native scroll animation

#### Stage 5：移动端开发

- `standalone: /android-native-dev` — Android 原生开发
  - 触发：Android / Gradle / Kotlin / Compose / Material3 / Testing
  - 输入：功能需求
  - 输出：Gradle 配置 / Compose 实现 / 测试方案
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /investigate`

- `standalone: /ios-application-dev` — iOS 原生开发
  - 触发：UIKit / SwiftUI / Accessibility / Permissions
  - 输入：功能需求
  - 输出：iOS 组件和实现规范
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /plan-design-review`

#### Stage 6：开发计划与编码实现

- `superpowers: /writing-plans` — 拆解可执行计划
  - 触发：需要把需求拆成步骤
  - 输入：需求 / 约束
  - 输出：分步执行计划
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：OpenSpec tasks

- `superpowers: /executing-plans` — 串行执行
  - 触发：简单任务 / 不支持 subagent 的环境
  - 输入：计划
  - 输出：当前会话完成实现
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`superpowers: /subagent-driven-development`

- `superpowers: /subagent-driven-development` — 并行子代理开发
  - 触发：多模块 / 多页面 / 独立任务
  - 输入：任务列表
  - 输出：多代理实现 / 多分支结果
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`superpowers: /dispatching-parallel-agents`

- `superpowers: /test-driven-development` — 测试驱动开发
  - 触发：业务规则复杂 / 边界多 / 历史 bug 多
  - 输入：需求 / 现有测试
  - 输出：失败测试 + 实现
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`superpowers: /verification-before-completion`

- 编码实现按技术栈选择
  - 前端 → `standalone: /frontend-dev`
  - 全栈 → `standalone: /fullstack-dev`
  - Android → `standalone: /android-native-dev`
  - iOS → `standalone: /ios-application-dev`

#### Stage 7：调试与排错

- `gstack: /investigate` — 查 Bug 根因
  - 触发：有错误日志 / 复现步骤
  - 输入：错误日志 / 复现步骤
  - 输出：根因 + 最小修复
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`superpowers: /systematic-debugging`

- `code-review-graph: /debug-issue` — 用代码图谱辅助调试
  - 触发：需要定位调用链、相关函数
  - 输入：错误描述 / 异常现象
  - 输出：调用链 / 相关函数 / 根因定位
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`code-review-graph: /explore-codebase`

- `superpowers: /systematic-debugging` — 系统性调试流程
  - 触发：复杂 bug，需要按阶段推进
  - 流程：Phase1 根因调查 → Phase2 模式分析 → Phase3 单假设验证 → Phase4 实现修复
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /investigate`

- Web 页面复现
  - `gstack: /browse` — 无头浏览器
  - `gstack: /qa` — 自动 QA 并修复
  - `gstack: /open-gstack-browser` — 可视化浏览器

- Android 构建错误
  - 首选：`standalone: /android-native-dev`
  - 辅助：`gstack: /investigate`

- 安全地调试
  - `gstack: /freeze` — 编辑范围限定
  - `gstack: /unfreeze` — 解除范围
  - `gstack: /careful` — 危险操作警戒
  - `gstack: /guard` — 完全安全模式

#### Stage 8：测试与质量验证

- `gstack: /qa` — Web 自动 QA 并修复
  - 触发：Web 功能做完，需要自动测试 + 修复
  - 输入：URL / 登录状态 / 范围
  - 输出：bug 列表 + 修复
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /setup-browser-cookies`

- `gstack: /qa-only` — Web 只报告不修复
  - 触发：只需要 QA 报告，不动代码
  - 输入：URL / 范围
  - 输出：QA 报告
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /browse`

- 浏览器自动化测试
  - 无头：`gstack: /browse`
  - 可视化：`gstack: /open-gstack-browser`
  - Cookie：`gstack: /setup-browser-cookies`

- `gstack: /benchmark` — 性能回归检测
  - 触发：需要性能对比
  - 输入：测试用例 / 版本
  - 输出：性能对比
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /benchmark-models`

- `superpowers: /verification-before-completion` — 完成前验证
  - 触发：提交前最后检查
  - 输入：改动 / 测试
  - 输出：验证结果 + 质量仪表板
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /health`

- 移动端测试
  - Android：Unit / JUnit / Robolectric / Compose UI / Espresso / UI Automator
  - iOS：UIKit / SwiftUI 检查 / Accessibility / Lifecycle / Permissions

#### Stage 9：代码审查与安全

- `superpowers: /requesting-code-review` — 提交前自审
  - 触发：代码写完后自己先审一遍
  - 输入：diff / 测试结果
  - 输出：审查意见
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /review`

- `code-review-graph: /review-delta` — 基于代码图谱的审查
  - 触发：需要结构化风险审查
  - 输入：diff / 分支 / PR
  - 输出：风险分级 + 爆炸半径 + 测试缺口 + GO-NOGO
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`code-review-graph: /review-changes`

- `code-review-graph: /review-pr` — 完整 PR 审查
  - 触发：审查整个 PR
  - 输入：PR 链接 / 分支
  - 输出：完整审查报告
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`code-review-graph: /code-review-graph:pre_merge_check`

- `code-review-graph: /code-review-graph:pre_merge_check` — 合并前检查
  - 触发：合并前的最后一道关卡
  - 输入：分支 / PR
  - 输出：合并建议
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /review`

- `gstack: /review` — 预合并 PR 审查
  - 触发：常规 PR 审查
  - 输入：diff / PR
  - 输出：bug / 风险 / 测试缺口
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /codex`

- `superpowers: /receiving-code-review` — 接收审查意见
  - 触发：需要处理别人给的 review comments
  - 输入：审查意见
  - 输出：修复计划 + 确认项
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：手动处理

- `gstack: /cso` — 安全审计
  - 触发：关注权限 / 基础设施 / 数据 / 依赖 / 密钥
  - 输入：代码 / 架构
  - 输出：安全审计报告
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /guard`

- `superpowers: /using-git-worktrees` — 工作区隔离
  - 触发：需要独立工作区处理多个任务
  - 输入：分支 / 任务
  - 输出：独立 worktree
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /context-save`

#### Stage 10：发布与部署

- `gstack: /ship` — 完整提交发布
  - 触发：功能完成，准备发 PR / 合并 / 发布
  - 输入：当前分支 / 测试状态
  - 输出：PR / 合并 / 发布准备
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`superpowers: /finishing-a-development-branch`

- `gstack: /land-and-deploy` — 合并并部署
  - 触发：合并后需要部署
  - 输入：分支 / 部署配置
  - 输出：部署完成
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /setup-deploy`

- `gstack: /canary` — 发布后监控
  - 触发：上线后观察异常
  - 输入：服务 / 指标
  - 输出：线上异常报告
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /health`

- `gstack: /document-release` — 发布文档
  - 触发：需要写 Release docs
  - 输入：变更列表
  - 输出：Release docs
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /make-pdf`

- OpenSpec 发布收尾
  - `opsx: /opsx:verify`
  - `opsx: /opsx:sync-specs`
  - `opsx: /opsx:archive`

#### Stage 11：项目上下文与知识管理

- `gstack: /context-save` — 保存上下文
  - 触发：需要中断工作，保存当前状态
  - 输入：当前任务状态
  - 输出：可恢复上下文
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /learn`

- `code-review-graph: /build-graph` — 构建代码图谱
  - 触发：需要理解代码库结构
  - 输入：代码库
  - 输出：图谱统计 / 模块结构 / 调用关系
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`code-review-graph: /explore-codebase`

- `code-review-graph: /explore-codebase` — 探索代码库
  - 触发：需要找代码、理解模块
  - 输入：查询 / 代码库
  - 输出：相关文件 / 调用关系
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：直接 Glob/Grep

- `code-review-graph: /refactor-safely` — 重构分析
  - 触发：计划重构，需要评估影响面
  - 输入：重构目标
  - 输出：影响面分析 / 安全建议
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`code-review-graph: /code-review-graph:architecture_map`

- `code-review-graph: /code-review-graph:onboard_developer` — 新人上手
  - 触发：新成员加入，需要快速了解项目
  - 输入：代码库
  - 输出：项目概览 / 关键模块 / 上手路径
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`code-review-graph: /explore-codebase`

- `gstack: /context-restore` — 恢复上下文
  - 触发：从保存点恢复工作
  - 输入：上下文 ID
  - 输出：恢复后的任务状态
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /landing-report`

- `gstack: /learn` — 项目学习记录
  - 触发：需要沉淀决策 / 经验 / 事实
  - 输入：项目信息
  - 输出：决策/经验/事实库
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：手动记录

- `gstack: /retro` — 工程复盘
  - 触发：阶段性复盘
  - 输入：git history / 变更
  - 输出：周报 / 经验沉淀
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：手动复盘

- `gstack: /health` — 质量仪表板
  - 触发：需要看项目整体健康度
  - 输入：项目
  - 输出：质量指标
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：手动检查

- `gstack: /make-pdf` — Markdown 转 PDF
  - 触发：需要输出 PDF 文档
  - 输入：Markdown 文件
  - 输出：PDF
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：其他 PDF 工具

---

### Lane 2：研究与信息获取

#### 搜索最新资料 / 竞品 / API

- `tavily: /tavily-search` — 基础搜索
  - 触发：需要最新资料
  - 输入：查询词 / 时间范围 / 域名限制
  - 输出：精简搜索结果
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`tavily: /tavily-dynamic-search`

- `tavily: /tavily-dynamic-search` — 动态搜索
  - 触发：需要多轮/深度搜索
  - 输入：查询词
  - 输出：搜索结果
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`tavily: /tavily-search`

#### 抓取单个网页内容

- `tavily: /tavily-extract` — 网页内容提取
  - 触发：需要单页内容
  - 输入：URL / query / chunks
  - 输出：markdown / text
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /scrape`

- `gstack: /scrape` — 通用网页抓取
  - 触发：tavily extract 不可用
  - 输入：URL
  - 输出：页面内容
  - 推荐：⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`tavily: /tavily-extract`

#### 发现网站文档页面

- `tavily: /tavily-map` — 发现站点页面
  - 触发：需要列出某站点所有文档页
  - 输入：站点 URL / 路径过滤
  - 输出：URL 清单
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`tavily: /tavily-crawl`

- `tavily: /tavily-crawl` — 抓取站点内容
  - 触发：需要把站点内容拉到本地
  - 输入：站点 URL
  - 输出：本地文档集
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`tavily: /tavily-map`

#### 系统性调研报告

- `tavily: /tavily-research` — 系统性调研
  - 触发：需要带引用的研究报告
  - 输入：研究问题 / 引用格式
  - 输出：带引用研究报告
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`standalone: /company-research`

#### SDK / 第三方集成调研

- `tavily: /tavily-best-practices` — 最佳实践调研
  - 触发：需要集成方式 / API 用法
  - 输入：SDK / 服务名
  - 输出：集成方式 + API 用法
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`tavily: /tavily-cli`

- `tavily: /tavily-cli` — Tavily CLI 入口
  - 触发：习惯命令行
  - 输入：tvly 命令
  - 输出：搜索结果 / 抓取内容
  - 推荐：⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`tavily: /tavily-search`

---

### Lane 3：画图与可视化

#### 代码架构/结构可视化

- `code-review-graph: /code-review-graph:architecture_map` — 代码架构图
  - 触发：需要看代码架构
  - 输入：已构建图谱
  - 输出：Mermaid 架构图
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`code-review-graph: /explore-codebase`

#### 通用图表生成

- `diagram: /diagram` — 专业图表生成
  - 触发：需要流程图 / 架构图 / 时序图 / 统计图等
  - 输入：图表需求 / 数据
  - 输出：PNG / HTML / DSL
  - 推荐：⭐⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：手动画图

#### 手绘风格草图

- `excalidraw: /excalidraw-diagram-generator` — 生成 Excalidraw 文件
  - 触发：需要手绘风格流程图 / 架构图 / 思维导图
  - 输入：自然语言描述
  - 输出：.excalidraw JSON
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`diagram: /diagram`

---

### Lane 4：写作与内容生产

#### 发布与产品文档

- `gstack: /document-release` — 发布后文档更新
  - 触发：发布完成后同步 README / CHANGELOG / 文档
  - 输入：diff / 变更列表
  - 输出：更新后的项目文档
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`gstack: /make-pdf`

- `gstack: /make-pdf` — Markdown 转 PDF
  - 触发：需要出版级 PDF
  - 输入：Markdown 文件
  - 输出：PDF
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：其他 PDF 工具

#### 营销与叙事内容

- `standalone: /press-release` — 新闻稿撰写
  - 触发：产品发布、重大更新需要新闻稿
  - 输入：产品 / 功能 / 亮点
  - 输出：新闻稿
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：手动撰写

- `standalone: /storyboard` — 故事板
  - 触发：需要把用户流程视觉化
  - 输入：用户场景 / 流程
  - 输出：故事板
  - 推荐：⭐⭐⭐⭐
  - 状态：待你填写
  - 备胎方案：`diagram: /diagram`

#### 待补充

> 你提到还有很多写作 skill，建议按内容类型继续拆分：
> - 技术文档 / README
> - Release Note / Changelog
> - 博客 / 公众号文章
> - 邮件 / 汇报

---

### Lane 5：代码库治理与理解

- `code-review-graph: /build-graph` — 构建代码图谱
- `code-review-graph: /explore-codebase` — 探索代码库
- `code-review-graph: /refactor-safely` — 安全重构分析
- `code-review-graph: /code-review-graph:onboard_developer` — 新人上手
- `code-review-graph: /code-review-graph:architecture_map` — 架构可视化
- `code-review-graph: /review-delta` — 变更风险审查
- `gstack: /context-save` / `gstack: /context-restore` — 上下文保存与恢复
- `gstack: /learn` — 项目知识沉淀
- `gstack: /retro` — 工程复盘
- `gstack: /health` — 质量仪表板

---

### Lane 6：工具与技能建设

- `tavily: /tavily-cli` — Tavily CLI 总入口
  - tvly search / extract / map / crawl / research

- `gstack: /setup-gbrain` — gbrain 配置
- `gstack: /sync-gbrain` — gbrain 同步
- `gstack: /gstack-upgrade` — gstack 升级
- `gstack: /plan-tune` — 提问策略调优
- `gstack: /skillify` — 固化抓取流程为 skill
- `superpowers: /writing-skills` — 编写自定义 skill
- `claude-plugin: skill-creator` — skill 创建辅助

---

## 二、推荐组合 Workflow

### 新功能开发
1. `superpowers: /brainstorming`
2. `tavily: /tavily-research`
3. `opsx: /opsx:propose`
4. `gstack: /plan-eng-review`
5. `opsx: /opsx:apply`
6. `superpowers: /requesting-code-review`
7. `opsx: /opsx:verify`
8. `gstack: /ship`

### 前端体验开发
1. `standalone: /frontend-dev`
2. `gstack: /design-consultation`
3. `gstack: /design-shotgun`
4. `gstack: /design-html`
5. `gstack: /qa`
6. `gstack: /design-review`
7. `gstack: /benchmark`

### 全栈生产功能
1. `opsx: /opsx:propose`
2. `standalone: /fullstack-dev`
3. `gstack: /plan-eng-review`
4. `superpowers: /test-driven-development`
5. `opsx: /opsx:apply`
6. `gstack: /review`
7. `gstack: /ship`
8. `gstack: /canary`

### Bug 修复
1. `gstack: /investigate`
2. `superpowers: /systematic-debugging`
3. `code-review-graph: /debug-issue`
4. `superpowers: /test-driven-development`
5. `superpowers: /verification-before-completion`
6. `superpowers: /requesting-code-review`

### 代码库理解与重构
1. `code-review-graph: /build-graph`
2. `code-review-graph: /explore-codebase`
3. `code-review-graph: /refactor-safely`
4. `code-review-graph: /code-review-graph:architecture_map`

### 发布上线
1. `gstack: /review`
2. `code-review-graph: /review-pr`
3. `code-review-graph: /code-review-graph:pre_merge_check`
4. `opsx: /opsx:verify`
5. `gstack: /ship`
6. `gstack: /land-and-deploy`
7. `gstack: /canary`
8. `gstack: /document-release`
9. `opsx: /opsx:archive`

---

## 三、包名来源参考表

| 包名 | 来源 | 说明 |
|---|---|---|
| `gstack:` | `gstack-skills-cheatsheet.md` | gstack 生态，覆盖调试、审查、发布、QA、设计、上下文管理等 |
| `superpowers:` | `superpowers-skills-cheatsheet.md` | 强制纪律工作流，覆盖设计、计划、执行、审查、收尾 |
| `opsx:` | `openspec-skills-cheatsheet.md` | OpenSpec 规格驱动变更管理 |
| `tavily:` | `tavily-skills-cheatsheet.md` | Tavily 搜索/抓取/研究工具 |
| `code-review-graph:` | `code-review-graph-skills-cheatsheet.md` | 代码知识图谱审查、调试、重构 |
| `claude-plugin:` | `claude-plugins-cheatsheet.md` | Claude 官方 Plugins，如 `skill-creator` |
| `standalone:` | `.claude/skills/` 或本地 `claudecode_guide/skills_guide/` | 独立 skill，不属于上述统一包 |
| `claude-code:` | Claude Code 官方内置 | 官方 skill，如 `/verify` |

### 已校正技能清单

**gstack 包**：`/office-hours` `/plan-ceo-review` `/plan-design-review` `/plan-eng-review` `/autoplan` `/design-consultation` `/design-shotgun` `/design-html` `/design-review` `/devex-review` `/learn` `/retro` `/document-release` `/skillify` `/scrape` `/cso` `/review` `/codex` `/investigate` `/qa` `/qa-only` `/browse` `/setup-browser-cookies` `/open-gstack-browser` `/benchmark` `/benchmark-models` `/guard` `/freeze` `/unfreeze` `/careful` `/context-save` `/context-restore` `/landing-report` `/health` `/make-pdf` `/ship` `/land-and-deploy` `/setup-deploy` `/canary` `/setup-gbrain` `/sync-gbrain` `/gstack-upgrade` `/plan-tune`

**superpowers 包**：`/brainstorming` `/writing-plans` `/executing-plans` `/subagent-driven-development` `/dispatching-parallel-agents` `/test-driven-development` `/systematic-debugging` `/verification-before-completion` `/requesting-code-review` `/receiving-code-review` `/using-git-worktrees` `/finishing-a-development-branch` `/writing-skills`

**opsx 包**：`/opsx:propose` `/opsx:ff` `/opsx:new` `/opsx:explore` `/opsx:continue` `/opsx:apply` `/opsx:sync-specs` `/opsx:verify` `/opsx:archive` `/opsx:bulk-archive`

**tavily 包**：`/tavily-search` `/tavily-dynamic-search` `/tavily-extract` `/tavily-map` `/tavily-crawl` `/tavily-research` `/tavily-best-practices` `/tavily-cli`

**code-review-graph 包**：`/build-graph` `/review-delta` `/review-pr` `/review-changes` `/debug-issue` `/explore-codebase` `/refactor-safely` `/code-review-graph:pre_merge_check` `/code-review-graph:architecture_map` `/code-review-graph:onboard_developer`

**claude-plugin**：`skill-creator`

**standalone 独立包**：`/frontend-dev` `/fullstack-dev` `/android-native-dev` `/ios-application-dev` `/user-story` `/roadmap-planning` `/company-research` `/press-release` `/storyboard`

---

## 四、后续迭代建议

1. **验证 standalone 包归属**：`frontend-dev` / `fullstack-dev` / `android-native-dev` / `ios-application-dev` 等独立 skill 若后续发现属于某个统一包，请批量调整包名。
2. **填充实测状态**：给每个 skill 打上 ✅ / ⚠️ / ❌，并补充踩坑备注。
3. **补全 Lane 4 写作**：把你实际拥有的写作 skill 按内容类型拆分填入。
4. **删除低频 skill**：如果长期不用，直接删掉或移到附录，避免地图臃肿。
5. **建立个人评分**：推荐度按你的真实使用频率调整，不要照搬官方描述。
