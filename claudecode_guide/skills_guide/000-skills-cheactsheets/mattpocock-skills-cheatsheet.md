# Matt Pocock Skills 速查表

> 本文档汇总了 Matt Pocock 技能集合中所有可用的 skill，按使用场景分类，方便快速查找。
> 实际路径：`~/.agents/skills/`
>
> **核心理念**：这些 skill 不是给 Claude 加能力，而是给 Claude 加纪律。它们把软件工程基本功（需求对齐、共享语言、反馈循环、代码设计）固化为可复用的流程。

---

## 安装

```bash
# 用户级别安装（推荐）
npx skills@latest add mattpocock/skills -g --all

# 项目级别安装
npx skills@latest add mattpocock/skills --all
```

首次在某个仓库使用工程类 skill 前，先运行：

```
/setup-matt-pocock-skills
```

---

## 快速索引（按场景）

| 场景 | 推荐 Skill | 备注 |
|---|---|---|
| 🚀 首次配置工程技能 | `/setup-matt-pocock-skills` | 必须第一步运行 |
| 💡 对齐需求（有代码库） | `/grill-with-docs` | 会更新 `CONTEXT.md` 和 ADR |
| 💡 对齐需求（无代码库） | `/grill-me` | 状态化访谈，不留文档 |
| 🐛 调试顽固 Bug | `/diagnosing-bugs` | 六阶段诊断，先建反馈循环 |
| 📝 生成 Spec | `/to-spec` | 把当前对话转成 issue tracker 上的 spec |
| 🔨 拆任务票 | `/to-tickets` | tracer-bullet 垂直切片 |
| ⚙️ 实现功能 | `/implement` | 内部驱动 `/tdd` + `/code-review` |
| ✅ 代码审查 | `/code-code-review` | Standards + Spec 双轴审查 |
| 🔍 处理 issues/PRs | `/triage` | 状态机式分类流转 |
| 🗺️ 大型模糊项目探路 | `/wayfinder` | 先画地图，再逐步决策 |
| 🏗️ 改善架构 | `/improve-codebase-architecture` | 产出可视化 HTML 报告 |
| 🧪 测试驱动 | `/tdd` | 红绿重构，垂直切片 |
| 🎨 做视频/动画 | `/hyperframes` | 所有视频工作的入口和路由 |
| 📚 研究话题 | `/research` | 后台 agent 调研，输出引用文档 |
| 🔄 交接上下文 | `/handoff` | 生成 handoff 文档给新会话 |
| 🎯 不知道用哪个 skill | `/ask-matt` | 路由咨询 |

---

## 一、配置与初始化

### `/setup-matt-pocock-skills` — 工程技能前置配置
**功能：** 配置仓库，让其他工程 skill 知道 issue tracker、标签词汇表、领域文档布局。

**会创建/更新：**
- `docs/agents/issue-tracker.md` — issue tracker 工作流
- `docs/agents/triage-labels.md` — triage 标签映射
- `docs/agents/domain.md` — `CONTEXT.md` / ADR 布局约定
- 在 `CLAUDE.md` 或 `AGENTS.md` 中添加 `## Agent skills` 块

**支持 issue tracker：** GitHub（默认）/ GitLab / Local markdown / 其他

**使用时机：**
- 首次在新仓库使用工程 skills 前
- 切换 issue tracker 时

---

## 二、主流程：idea → ship

这是 Matt Pocock 推荐的标准工作流，大多数功能开发都走这条主线。

```
想法
  │
  ▼
/grill-with-docs  ← 对齐需求，建立共享语言
  │
  ▼
[需要原型验证？] ──YES──► /handoff → /prototype → /handoff 回来
  │ NO
  ▼
[多会话大任务？]
  │
  ├── YES ──► /to-spec → /to-tickets → 逐个 /implement
  │
  └── NO ──► 直接 /implement
                  │
                  ▼
              /tdd（内部驱动）
                  │
                  ▼
              /code-review
                  │
                  ▼
              commit
```

### `/grill-me` — 无代码库的需求访谈
**功能：** 通过 relentless interview 把计划或设计磨锋利。

**特点：**
- 状态化：不保存 `CONTEXT.md`
- 适用于没有代码库的场景
- 每次只问一个问题，等用户回答后再继续
- 走到双方达成 shared understanding 为止

**使用时机：**
- 没有代码库的通用计划讨论
- 想快速磨尖一个想法

---

### `/grill-with-docs` — 有代码库的需求访谈
**功能：** 和 `/grill-me` 一样 relentless interview，但会同步更新 `CONTEXT.md` 和 ADR。

**会驱动：** `/grilling` + `/domain-modeling`

**产出：**
- `CONTEXT.md` — 统一领域语言词汇表
- `docs/adr/*.md` — 关键架构决策记录

**使用时机：**
- 任何有代码库的功能开发前
- 重构、架构调整前
- 需要把隐含的领域假设显性化时

---

### `/to-spec` — 把对话转成 Spec
**功能：** 不访谈用户，直接基于已有对话和代码理解生成 spec（PRD），发布到 issue tracker。

**Spec 模板包含：**
1. Problem Statement
2. Solution
3. User Stories（大量、详细）
4. Implementation Decisions
5. Testing Decisions
6. Out of Scope
7. Further Notes

**关键步骤：**
- 探索仓库现状
- 确定测试 seam（越少越好，理想是一个）
- 发布时打 `ready-for-agent` 标签

**使用时机：**
- `/grill-with-docs` 后，多会话任务需要落盘 spec
- 当前对话已经充分讨论了需求

---

### `/to-tickets` — 把 Spec 拆成 Tracer-Bullet Tickets
**功能：** 把 spec、计划或对话拆成垂直切片的 tickets，每个 ticket 声明阻塞关系。

**垂直切片规则：**
- 每个切片切穿所有层（schema、API、UI、tests）
- 完成一个切片即可演示或验证
- 每个切片能放进一个全新上下文窗口
- 先做任何必要的 prefactor

** wide refactor 例外：** 机械式全代码库改动（如重命名列）不按垂直切片，用 expand-contract：
1. Expand：新形式与旧形式并存
2. Migrate：分批迁移调用点
3. Contract：删除旧形式

**产出格式：**
- Local markdown：`.scratch/<feature>/issues/<NN>-<slug>.md`
- 真实 tracker：GitHub/Linear issue + 原生阻塞链接

**使用时机：**
- `/to-spec` 之后
- 需要把大任务拆成可并行的小任务

---

### `/implement` — 基于 Spec/Tickets 实现
**功能：** 根据 spec 或 tickets 实现工作。

**内部流程：**
1. 在预确认的 seam 上用 `/tdd`
2. 定期进行类型检查和单测
3. 最后跑完整测试套件
4. 用 `/code-review` 审查
5. Commit

**使用时机：**
- 单个小任务直接在当前窗口实现
- 多任务场景下逐个 ticket 实现（每次清上下文）

---

### `/tdd` — 测试驱动开发
**功能：** 红 → 绿循环，每次一个垂直切片。

**核心规则：**
- **Red before green**：先写失败的测试，再写最少实现
- **One slice at a time**：一个 seam、一个测试、一个最小实现
- **Refactoring 不在循环内**：重构属于 review 阶段

**测试反模式：**
- ❌ Implementation-coupled（测试内部实现）
- ❌ Tautological（断言和实现同构）
- ❌ Horizontal slicing（先写全部测试再全部实现）

**使用时机：**
- `/implement` 内部
- 单独想用测试优先方式开发一个小功能

---

### `/code-review` — 双轴代码审查
**功能：** 针对固定基准点（commit/branch/tag）做双轴审查，两个子 agent 并行。

**两个轴：**
- **Standards**：是否符合仓库编码规范 + Fowler 代码坏味道基线
- **Spec**：是否忠实实现原始 issue/spec

**坏味道基线包括：**
Mysterious Name、Duplicated Code、Feature Envy、Data Clumps、Primitive Obsession、Repeated Switches、Shotgun Surgery、Divergent Change、Speculative Generality、Message Chains、Middle Man、Refused Bequest

**使用时机：**
- `/implement` 完成后
- 用户要求审查分支/PR/改动时
- 任意 "review since X" 场景

---

## 三、入口与路由

### `/ask-matt` — 不知道该用哪个 skill
**功能：** 根据用户情况推荐合适的 skill 或流程。

**使用时机：**
- 不确定走哪个流程
- 想快速了解某个场景该用什么 skill

---

## 四、On-Ramps（旁路入口）

这些 skill 处理特定起始情况，然后汇入主流程。

### `/triage` — Issue/PR 分类
**功能：** 把 issue tracker 上的 issues 和外部 PRs 按状态机流转。

**两个 category 角色：**
- `bug` — 有东西坏了
- `enhancement` — 新功能或改进

**五个 state 角色：**
- `needs-triage` — 待评估
- `needs-info` — 等报告者补充信息
- `ready-for-agent` — 已明确，可交给 agent
- `ready-for-human` — 需要人类处理
- `wontfix` — 不处理

**关键规则：**
- 只处理外部流入的 issues/PRs，`/to-tickets` 产生的 ticket 不再 triage
- 每条 triage 评论必须以 `> *This was generated by AI during triage.*` 开头
- 要先验证 bug 是否能复现，再进入 grilling

**使用时机：**
- Bug 报告、功能请求堆积
- 需要把原始 issue 转成 agent-ready brief

---

### `/diagnosing-bugs` — 诊断顽固 Bug
**功能：** 六阶段诊断循环，禁止没有反馈循环就动手修。

**六阶段：**
1. **Build a feedback loop** — 构造一个能复现 bug 的 tight loop（测试、curl、CLI、浏览器脚本等）
2. **Reproduce + minimise** — 确认复现并最小化场景
3. **Hypothesise** — 生成 3-5 个可证伪的假设并排序
4. **Instrument** — 一次只改一个变量，验证假设
5. **Fix + regression test** — 先写回归测试再修，然后跑原始场景
6. **Cleanup + post-mortem** — 清理调试代码，问"什么能预防这个 bug"

**关键规则：**
- 没有 red-capable 的反馈循环，不许进入 Phase 2
- 所有调试日志必须带 `[DEBUG-xxx]` 前缀，最后统一清理
- 如果架构导致没有合适的测试 seam，把发现交给 `/improve-codebase-architecture`

**使用时机：**
- "debug this" / "fix this bug"
- 间歇性 bug、性能回归、复杂故障

---

### `/wayfinder` — 大型模糊项目探路
**功能：** 当任务太大、方向不明时，先在 issue tracker 上画一张"地图"，然后逐个探索决策点。

**核心思想：**
- 产出**决策**，不是交付物
- 每个 ticket 解决一个问题
- 用 `wayfinder:map` 标签的 map issue 做索引
- 永远按名称引用 ticket，不是裸 id

**Ticket 类型：**
- `wayfinder:research` — 调研（AFK）
- `wayfinder:prototype` — 原型验证（HITL）
- `wayfinder:grilling` — 访谈澄清（HITL）
- `wayfinder:task` — 为决策 unblock 的手动工作

**使用时机：**
- 全新项目、超大功能、方向看不清
- "从 A 到 B 的路怎么走还不清楚"

---

## 五、代码库健康

### `/improve-codebase-architecture` — 架构深化
**功能：** 扫描代码库，发现"浅模块"并建议深化机会，生成可视化 HTML 报告。

**流程：**
1. 读 `CONTEXT.md` 和 ADRs
2. 用 `subagent_type=Explore` 走访代码库
3. 生成 HTML 报告（Tailwind + Mermaid）
4. 用户选一个候选后，用 `/grilling` + `/domain-modeling` 深化设计

**使用术语：** module、interface、depth、seam、adapter、leverage、locality（来自 `/codebase-design`）

**使用时机：**
- 代码库变成泥球
- 有空就运行，保持代码库健康
- `/diagnosing-bugs` 发现没有好 seam 时

---

### `/request-refactor-plan` — 重构计划
**功能：** 通过访谈收集信息，把重拆计划写成 GitHub issue。

**产出模板：**
1. Problem Statement
2. Solution
3. Commits（极小的提交序列）
4. Decision Document
5. Testing Decisions
6. Out of Scope
7. Further Notes

**使用时机：**
- 想规划一次重构
- 要写重构 RFC

---

## 六、词汇层（可被其他 skill 调用）

### `/grilling` — 无情访谈（模型触发）
**功能：** `/grill-me` 和 `/grill-with-docs` 的底层实现。

**规则：**
- 每次只问一个问题
- 能查代码的事实就不问
- 用户确认达成 shared understanding 前不执行计划

**使用时机：**
- 其他 skill 需要访谈用户时
- 用户想 stress-test 计划

---

### `/domain-modeling` — 领域建模
**功能：** 主动构建和打磨项目的领域模型。

**职责：**
- 用 `CONTEXT.md` 挑战模糊术语
- 提出规范化术语
- 用具体场景 stress-test 领域关系
- 对照代码发现矛盾
- Inline 更新 `CONTEXT.md`
- 只在满足三条件时创建 ADR：难以逆转、没有上下文会令人惊讶、真实权衡后的结果

**使用时机：**
- `/grill-with-docs` 内部
- 用户想明确领域术语
- 需要记录架构决策

---

### `/codebase-design` — 深层模块设计词汇
**功能：** 提供设计深层模块的共享词汇和原则。

**核心术语：**
- **Module**：有接口和实现的东西（函数、类、包、切片）
- **Interface**：调用者必须知道的一切（签名、不变量、顺序约束、错误模式等）
- **Implementation**：模块内部
- **Depth**：小接口隐藏大实现
- **Seam**：可以在不编辑该处的情况下改变行为的位置
- **Adapter**：在 seam 处满足接口的具体实现
- **Leverage**：调用者从深度中获得的能力
- **Locality**：维护者从深度中获得的集中性

**设计原则：**
- 深度是接口的属性
- 删除测试：删除模块后复杂度是消失了还是分散了？
- 接口就是测试面
- 一个 adapter = 假设 seam；两个 adapter = 真实 seam

**使用时机：**
- 设计或改进模块接口
- 找深化机会
- `/improve-codebase-architecture` 和 `/tdd` 都会用它

---

### `/design-an-interface` — 设计接口两次
**功能：** 用并行子 agent 生成 3+ 种截然不同的接口设计，然后比较。

**流程：**
1. 收集需求
2. 并行生成激进不同的设计
3. 逐一展示
4. 按接口简单性、通用性、实现效率、深度、易用性比较
5. 综合最佳方案

**使用时机：**
- 设计 API
- 探索模块形状
- 用户说 "design it twice"

---

## 七、跨会话工具

### `/handoff` — 上下文交接
**功能：** 把当前对话压缩成 handoff 文档，供新 agent 继续。

**保存位置：** 用户 OS 临时目录（不在工作区）

**必须包含：**
- 当前状态摘要
- 建议使用的 skills
- 引用已有产物（spec、ADR、issue、diff）而不是复制
- 敏感信息脱敏

**使用时机：**
- 上下文快满，需要新会话继续
- 要分支去做 `/prototype` 再回来

---

### `/claude-handoff` — 启动后台 agent 交接
**功能：** 和 `/handoff` 类似，但直接启动一个后台 agent 继续工作。

**命令形式：** `claude --bg --name "Fix login bug" "<handoff summary>"`

**使用时机：**
- 需要后台继续执行
- 用户用 `claude agents` 管理后台任务

---

## 八、独立技能

### `/prototype` — 可丢弃原型
**功能：** 用可丢弃代码回答一个设计问题。

**两个分支：**
- **Logic**：交互式终端应用，验证状态机/业务逻辑
- **UI**：单路由多个 UI 变体，用 URL param 切换

**规则：**
- 从第一天起就是 throwaway
- 一个命令运行
- 默认不持久化
- 不做测试、错误处理、抽象
- 最后把验证的决策折叠进真实代码，原型提交到独立分支

**使用时机：**
- 状态模型是否靠谱需要验证
- UI 长什么样需要看效果

---

### `/research` — 后台调研
**功能：** 启动后台 agent 调研问题，输出带引用的 Markdown 文件。

**要求：**
- 只使用高信任的一手来源（官方文档、源码、spec、一手 API）
- 每个 claim 都要引用来源
- 放在仓库已有的笔记位置

**使用时机：**
- 需要查文档、API 事实
- 想把阅读工作委托给后台 agent

---

### `/teach` — 多会话教学
**功能：** 在当前目录建立教学 workspace，多会话教授某个概念。

**工作区文件：**
- `MISSION.md` — 学习目标
- `RESOURCES.md` — 资源列表
- `./lessons/*.html` — 课程
- `./reference/*.html` — 参考资料
- `./learning-records/*.md` — 学习记录
- `./assets/*` — 可复用组件

**教学原则：**
- 区分 fluency strength 和 storage strength
- 用 retrieval practice、spacing、interleaving 促进长期记忆
- 每节课一个小而完整的胜利

**使用时机：**
- 用户想系统学习某个技能/概念

---

### `/writing-great-skills` — 写好 skill 的参考
**功能：** 教授如何写好和编辑 skill。

**核心概念：**
- **Predictability** 是 root virtue
- **Model-invoked** vs **User-invoked** 的权衡
- **Information hierarchy**：in-skill step / in-skill reference / external reference
- **Leading words**：用模型已有的紧凑概念锚定行为
- **Failure modes**：premature completion、duplication、sediment、sprawl、no-op、negation

**使用时机：**
- 写自定义 skill 时
- 想理解 skill 设计原则

---

## 九、Git 与工程工具

### `/resolving-merge-conflicts` — 解决合并冲突
**功能：** 处理进行中的 git merge/rebase 冲突。

**步骤：**
1. 查看当前状态和历史
2. 找到每个冲突的 primary sources，理解原意
3. 解决每个 hunk，尽量保留双方意图
4. 运行自动化检查（typecheck、test、format）
5. 完成 merge/rebase

**原则：** 永远 resolve，不 `--abort`。

---

### `/git-guardrails-claude-code` — Git 安全护栏
**功能：** 设置 PreToolUse hook，拦截危险 git 命令。

**默认拦截：**
- `git push`（含 `--force`）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

**可安装范围：**
- 项目级：`.claude/settings.json` + `.claude/hooks/`
- 全局：`~/.claude/settings.json` + `~/.claude/hooks/`

**使用时机：**
- 防止 agent 误执行破坏性 git 操作

---

### `/setup-pre-commit` — 配置 Pre-Commit Hooks
**功能：** 配置 Husky + lint-staged + Prettier + typecheck + test。

**会安装：**
- `husky`、`lint-staged`、`prettier`
- `.husky/pre-commit`
- `.lintstagedrc`
- `.prettierrc`（如果不存在）

**使用时机：**
- 新项目需要提交时检查
- 想统一代码风格

---

### `/setup-ts-deep-modules` — TypeScript 深层模块
**功能：** 用 dependency-cruiser 强制每个 package 成为深层模块。

**强制结构：**
```
src/packages/<name>/
  index.ts       ← entry point（公开）
  client.ts      ← 另一个 entry point
  lib/           ← 实现（私有）
  tests/         ← 测试（私有）
```

**四条规则：**
1. Entry-point boundary：外部只能 import entry points
2. Intra-package freedom：包内自由 import
3. Tests through entry points：测试也只能走 entry points
4. No cycles：禁止循环依赖

**使用时机：**
- TypeScript monorepo 需要模块边界
- 想把每个 package 做成 deep module

---

## 十、领域语言与文档

### `/ubiquitous-language` — 提取统一语言
**功能：** 从当前对话中提取 DDD 风格的统一语言词汇表，保存到 `UBIQUITOUS_LANGUAGE.md`。

**识别问题：**
- 同一个词指不同概念
- 不同词指同一个概念
- 模糊或超载的术语

**输出包含：**
- 分组术语表（Term / Definition / Aliases to avoid）
- 概念关系
- 示例对话
- 标记的歧义

**使用时机：**
- 用户想定义领域术语
- 提到 "domain model" 或 "DDD"

---

### `/wizard` — 生成交互式 Bash 向导
**功能：** 把手动流程变成一步步 bash 向导，自动打开 URL、捕获值、写入 `.env` 和 GitHub secrets。

**适用场景：**
- 第三方服务配置
- 一次性迁移
- A→B 状态转换

**基于 template.sh：** 进度、确认门、跨平台 URL 打开、密码隐藏输入、幂等 `.env` upsert。

**使用时机：**
- 有繁琐的手动设置流程
- 希望下次不复述给 AI

---

### `/obsidian-vault` — Obsidian 笔记管理
**功能：** 在 Obsidian vault 中搜索、创建、管理笔记，使用 wikilinks 和 index notes。

**Vault 位置：** `/mnt/d/Obsidian Vault/AI Research/`

**约定：**
- 标题式命名
- 无文件夹，用链接和 index notes 组织
- 底部链接相关笔记

**使用时机：**
- 用户想管理 Obsidian 笔记

---

### `/qa` — QA 会话
**功能：** 交互式 QA 会话，用户口语化报告 bug，agent 探索代码并创建 GitHub issues。

**步骤：**
1. 听并 lightly clarify（最多 2-3 个问题）
2. 后台用 Explore agent 理解相关领域
3. 判断是单个 issue 还是拆分
4. 用 `gh issue create` 创建 issues

**Issue 规则：**
- 不写文件路径和行号
- 使用项目领域语言
- 描述行为而不是代码
- 必须有复现步骤

**使用时机：**
- 用户想口语化报 bug
- 需要做 QA session

---

### `/scaffold-exercises` — 脚手架练习
**功能：** 创建课程练习目录结构：sections、problems、solutions、explainers，并确保通过 linting。

**使用时机：**
- 搭建课程练习
- 创建新的课程 section

---

### `/migrate-to-shoehorn` — 迁移到 Shoehorn
**功能：** 把测试文件中的 `as` 类型断言迁移到 `@total-typescript/shoehorn`。

**使用时机：**
- 用户提到 shoehorn
- 想用 partial test data

---

## 十一、视频 / 动画 / HyperFrames 生态

`/hyperframes` 是所有视频请求的入口。它根据输入类型路由到不同 workflow。

### 路由速查

| 输入/意图 | 使用 Skill |
|---|---|
| 产品/SaaS 推广视频 | `/product-launch-video` |
| 普通网站展示/导览 | `/website-to-video` |
| 概念/话题讲解（无产品） | `/faceless-explainer` |
| GitHub PR 讲解 | `/pr-to-video` |
| 给现有说话视频加字幕 | `/embedded-captions` |
| 给现有说话视频加图形覆盖层 | `/talking-head-recut` |
| 短动态图形（<10s，无旁白） | `/motion-graphics` |
| 音乐驱动视频 | `/music-to-video` |
| 演示文稿/幻灯片 | `/slideshow` |
| 其他/自定义长视频 | `/general-video` |
| Remotion 迁移到 HyperFrames | `/remotion-to-hyperframes` |

### 领域技能

| 能力 | Skill |
|---|---|
| HTML composition 契约 | `/hyperframes-core` |
| 动画/运动设计 | `/hyperframes-animation` |
| seek-safe keyframes | `/hyperframes-keyframes` |
| 创意方向/设计 spec | `/hyperframes-creative` |
| 音频/媒体资源 | `/hyperframes-media` |
| 媒体 resolve（BGM/SFX/图片） | `/media-use` |
| CLI 开发循环 | `/hyperframes-cli` |
| Registry blocks/components | `/hyperframes-registry` |
| Figma 导入 | `/figma` |

---

## 十二、写作技能

| Skill | 用途 |
|---|---|
| `/edit-article` | 编辑和改进文章 |
| `/writing-fragments` | 挖掘原始片段，无结构 |
| `/writing-beats` | 把素材组装成节奏旅程 |
| `/writing-shape` | 把素材塑造成文章 |

---

## 十三、完整工作流

```
开始新功能
    │
    ▼
┌─────────────────────────────┐
│ /setup-matt-pocock-skills   │  ← 首次配置（issue tracker、标签、领域文档）
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ /grill-with-docs            │  ← 对齐需求，更新 CONTEXT.md + ADR
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ [需要原型验证？]            │
│   YES → /handoff → /prototype → /handoff
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ [多会话/大任务？]           │
│   YES → /to-spec → /to-tickets
│   NO  → 直接 /implement
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ /implement                  │  ← 驱动 /tdd，垂直切片实现
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ /code-review                │  ← Standards + Spec 双轴审查
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ commit                      │
└─────────────────────────────┘
```

**插入点（按需）：**
- 遇到 bug → 插入 `/diagnosing-bugs`
- issues/PRs 堆积 → 插入 `/triage`
- 方向不明的大项目 → 插入 `/wayfinder`
- 代码库变泥球 → 插入 `/improve-codebase-architecture`
- 上下文满了 → 插入 `/handoff` 或 `/claude-handoff`

---

## 十四、常见问题

**Q：什么时候用 `/grill-me` 而不是 `/grill-with-docs`？**
> A：有代码库用 `/grill-with-docs`（会更新 CONTEXT.md/ADR）；没代码库或只是通用计划讨论用 `/grill-me`。

**Q：`/to-spec` 和 `/to-tickets` 的区别？**
> A：`/to-spec` 把对话变成 PRD/spec；`/to-tickets` 把 spec/plan 拆成可执行的 tracer-bullet tickets。

**Q：可以直接用 `/tdd` 而不用 `/implement` 吗？**
> A：可以。`/tdd` 适合单独一个小功能测试优先开发；`/implement` 是完整实现流程，内部会驱动 `/tdd`。

**Q：`/code-review` 的双轴是什么意思？**
> A：Standards 轴检查代码规范和坏味道；Spec 轴检查是否实现了需求。两者并行，避免互相掩盖。

**Q：视频请求该用哪个 skill？**
> A：先喊 `/hyperframes`，它会根据输入类型自动路由到正确 workflow。不要自己猜。

**Q：这些 skill 会自己触发吗？**
> A：有些会（model-invoked，如 `/tdd`、`/code-review`、`/hyperframes`）；有些只能你手动触发（user-invoked，如 `/grill-me`、`/implement`、`/to-spec`）。

---

## 十五、两个经常踩的坑

### 坑一：跳过 `/setup-matt-pocock-skills`
其他工程 skill 都假设仓库已经配置好 issue tracker、标签和领域文档布局。没配置就用 `/to-tickets` 或 `/triage` 会不知道往哪里写。

**解法：** 新仓库第一步运行 `/setup-matt-pocock-skills`。

### 坑二：把 `/grill-with-docs` 当问答机用
访谈的价值在于产出 committed spec 和更新后的领域文档。如果停在问答阶段，后续 `/implement` 没有明确依据，质量大打折扣。

**解法：** 确保走到 spec/tickets，且 `CONTEXT.md` 和 ADR 被及时更新。

---

*文档基于 mattpocock/skills 全局安装后的 SKILL.md 整理*
*安装路径：`~/.agents/skills/`*
