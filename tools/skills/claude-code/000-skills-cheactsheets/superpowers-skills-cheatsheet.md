---
title: "Superpowers Skills Cheatsheet"
date: 2026-06-21
category: tools
tags: []
status: published
description: "Notes on Superpowers Skills Cheatsheet."
---

# Superpowers Skill 速查表

> 本文档汇总了 Superpowers 插件中所有可用的 skill，按功能场景分类，方便在需要时快速查找。
> 实际路径：`~/.config/superpowers/skills/`
>
> **核心理念**：Superpowers 不是给 Claude 加能力，而是给 Claude 加纪律。每个 skill 本质上是一个 Markdown 文件，用文本"强制执行"工程师该有的纪律。

---

## 快速索引（按场景）

| 场景 | 推荐 Skill | 备注 |
|---|---|---|
| 💡 新功能设计 | `/brainstorming` | 好用, 帮我清晰想法
| 🐛 调试 Bug | `/systematic-debugging` |
| 📝 拆解任务 | `/writing-plans` |
| 🚀 并行开发 | `/subagent-driven-development` | 需重点测试并发效果与能力
| 🔧 串行开发 | `/executing-plans` |
| ✅ 测试驱动 | `/test-driven-development` |
| 🔍 代码审查 | `/requesting-code-review` | 好用, 写完代码进行审查
| 🗣️ 接收审查意见 | `/receiving-code-review` |
| 🧪 完成前验证 | `/verification-before-completion` |
| 🚀 并行派发代理 | `/dispatching-parallel-agents` | 多独立任务并行
| 🌿 工作区隔离 | `/using-git-worktrees` |
| 🏁 收尾工作 | `/finishing-a-development-branch` |
| 🔁 重置上下文 | `/using-superpowers` |
| 🛠️ 编写自定义 Skill | `/writing-skills` |

---

## 一、设计阶段

### `/brainstorming` — 强制性设计
**功能：** 有一道硬门（HARD-GATE），用户未批准设计前，**一行代码都不许写**。完整 9 步流程，产出可执行的 spec 文档。

**9 步流程（必须按序完成）：**
1. 探索项目现状（看文件、commits、文档）
2. 如有视觉问题，提供可视化伴侣
3. 逐条问澄清问题（每次只问一个）
4. 提出 2-3 个方案并给出推荐理由
5. 按章节展示设计方案，每段都要确认
6. 把设计写入 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` 并 commit
7. 自检 spec：扫描 TBD/TODO、内部矛盾、范围、歧义
8. 让用户审阅 spec 文件
9. **移交 `writing-plans`**（唯一终态，不许调用其他 skill）

**HARD-GATE（原文）：**
```markdown
Do NOT invoke any implementation skill, write any code, scaffold any project,
or take any implementation action until you have presented a design
and the user has approved it.
```

**使用时机：**
- 任何新功能开发前
- 重构任务开始前
- "帮我加个功能" / "改一下这个"
- **即使你觉得项目很简单，也必须走流程**（简单项目里的隐含假设，是浪费工作的最大来源）

**最容易踩的坑：**
- 只走到步骤 4-5 就让 Claude 直接写代码 → 设计未落到文档，执行阶段记忆漂移
- 把 brainstorming 当"AI 产品经理"用，停在问答阶段 → 没有 committed spec，后续质量大打折扣

---

## 二、调试阶段

### `/systematic-debugging` — 系统性调试
**功能：** 四阶段根因排查，禁止没有根因就动手。平均耗时从 2-3 小时降到 15-30 分钟。

**铁律（原文）：**
```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

**四阶段（必须按顺序，前一阶段没完成不许进下一阶段）：**

| 阶段 | 内容 |
|---|---|
| **Phase 1：根因调查** | 完整读错误信息；稳定复现步骤；检查最近 git 变更；多组件系统在每个边界打诊断日志，先收集证据再分析 |
| **Phase 2：模式分析** | 找到同一 codebase 里类似的好/坏代码；逐项对比差异（每个差异都列出来，不假设无关）；理解依赖和假设条件 |
| **Phase 3：单假设验证** | 写下一个具体假设（"我认为 X 是根因，因为 Y"）；做最小变更验证；不对则换新假设，**不叠加改动** |
| **Phase 4：实现修复** | 先写能复现问题的测试；只改一处；三次修复失败则 STOP，讨论是否架构问题 |

**三次失败规则：**
> 试了 3 次修复都没解决 → **必须停下来**，不再尝试第四次，退后讨论"是不是架构层面的问题"。
> 不是"不许再改"，而是"讨论后再决定"。

**常见借口 vs 真相：**

| 借口 | 真相 |
|---|---|
| "这个 issue 很简单，不用走流程" | 简单的 bug 也有根因，流程对简单问题反而更快 |
| "紧急情况，没时间调查" | 系统性调试比猜测快多了，"紧急"不是理由 |
| "先试一下再说" | 第一次就确立猜测模式，后面就一直猜 |
| "我已经大概知道问题在哪了" | 知道症状不等于知道根因 |

**使用时机：**
- "debug this" / "fix this bug"
- "why is this broken"
- 任何报错、异常行为、测试失败

---

## 三、计划拆解

### `/writing-plans` — 可执行计划
**功能：** 把 brainstorming 产出的 spec 拆成可以被 AI 或人类一步步执行的任务清单。每个步骤粒度 **2-5 分钟**。

**示例粒度：**
```markdown
- [ ] Step 1: 写一个失败的测试
- [ ] Step 2: 跑一下，确认它确实失败了      ← 不是和 Step 1 合并
- [ ] Step 3: 写最小实现让测试通过
- [ ] Step 4: 跑测试，确认通过
- [ ] Step 5: Commit
```

**零占位符规则（以下写法会被认为是计划失败）：**
- ❌ "TBD"、"TODO"、"后续实现"
- ❌ "添加适当的错误处理"（不写具体怎么处理）
- ❌ "写上述内容的测试"（不给测试代码）
- ❌ "类似 Task N"（重复内容，不允许引用）

**产出后的两个执行选项：**

| 选项 | 说明 |
|---|---|
| **选项 1：subagent-driven-development（推荐）** | 每个任务派新 subagent，干净上下文，带两轮审查 |
| **选项 2：executing-plans** | 当前会话串行执行，适合不支持 subagent 的环境 |

**使用时机：**
- brainstorming 完成后（唯一入口）
- 需要把设计转化为可执行任务清单

---

## 四、执行阶段

### `/subagent-driven-development` — 并行子代理开发（推荐）
**功能：** 每个任务 spawn 全新 subagent，干净上下文，两轮审查。

**工作方式：**
1. 每个任务 spawn 一个新 subagent
2. 新 subagent 拿到计划文件和当前任务，**干净上下文**开始工作
3. 两轮审查：先看 spec 合规性，再看代码质量
4. 完成后回报，主 agent 决定是否继续下一个任务

**优势：**
- 上下文干净，不会被之前的错误尝试带偏
- 避免"综合"前面任务时把已通过的测试改坏
- 代码质量显著更高

**代价：**
- 每个任务重新加载 plan 文件，调用开销略高
- 但避免一次返工节省的成本远大于开销

**使用时机：**
- Claude Code / Codex 等支持 subagent 的平台
- 任务数量多、上下文容易漂移
- 复杂功能开发

---

### `/executing-plans` — 串行执行
**功能：** 在当前会话里串行执行所有任务，批量执行，定期设置检查点让你介入。

**工作方式：**
- 上下文累积，会话越来越长
- 批量执行，定期设置检查点

**使用时机：**
- Cursor、不支持 subagent 的环境
- 简单小任务、不想多绕一圈
- 部分任务需要手动操作（如配置环境变量）

---

### 两者对比

| 维度 | `subagent-driven-development` | `executing-plans` |
|---|---|---|
| **上下文** | 每个任务干净 | 累积，越来越长 |
| **平台要求** | 支持 subagent | 任何平台 |
| **代码质量** | 显著更高 | 一般 |
| **调用开销** | 略高 | 低 |
| **适用场景** | 任务多、易漂移 | 简单任务、无 subagent 支持 |
| **能否混用** | 可以，同一个 plan 里部分任务用 subagent，部分手动执行 |

> Superpowers 文档建议：如果你的环境支持 subagent，就用 `subagent-driven-development`。

---

### `/test-driven-development` — 测试驱动开发
**功能：** 贯穿实现阶段的 RED-GREEN-REFACTOR 循环。

**使用时机：**
- 实现阶段的每个任务
- 与 `subagent-driven-development` 或 `executing-plans` 配合使用

---

### `/dispatching-parallel-agents` — 并行派发代理
**功能：** 并行启动多个 agent 处理独立任务。

**使用时机：**
- 多个无依赖任务需要同时执行
- 大规模重构时并行处理不同模块

---

## 五、代码审查

### `/requesting-code-review` — 提审前自检
**功能：** 提交代码审查前的自检流程。

**使用时机：**
- 代码完成后、提交 PR 前
- 自我审查，确保符合 spec 和计划

---

### `/receiving-code-review` — 接收审查意见
**功能：** 处理收到的代码审查反馈，系统性响应每条意见。

**使用时机：**
- 收到 PR review 评论后
- 需要系统性处理反馈时

---

## 六、工作区管理

### `/using-git-worktrees` — 工作区隔离
**功能：** 创建隔离的 git worktree，避免分支切换污染。

**使用时机：**
- 开始新功能开发前
- 需要同时处理多个分支时

---

## 七、收尾阶段

### `/finishing-a-development-branch` — 干净收尾
**功能：** 验证测试 → 确定 base branch → 选择后续动作 → 清理 worktree。

**五步流程：**
1. **验证测试通过**（失败则 STOP，不进入后续步骤）
2. 确定 base branch
3. 给出四个选项：
   - Option 1：本地 merge 回 `<base-branch>`
   - Option 2：Push 并创建 Pull Request
   - Option 3：保留分支（晚点处理）
   - Option 4：丢弃这次工作
4. 按选择执行
5. 清理 worktree（选 1 和 4 才清理，选 2 和 3 保留）

**安全设计：**
> 丢弃选项（Option 4）需要**手动输入 "discard"** 才能执行，防止误操作。

**使用时机：**
- 所有任务完成后
- "完成了" / "可以提交了" / "推上去吧"
- **不要直接 commit 或 merge，走这个 skill**

---

## 八、验证与质量

### `/verification-before-completion` — 完成前验证
**功能：** 在标记任务完成前，强制验证输出是否符合预期。

**使用时机：**
- 任务声称"完成"前
- 对输出质量有疑虑时
- 插入到执行流程中作为检查点

---

## 九、元技能

### `/using-superpowers` — 重置 Skill 优先级
**功能：** 帮 Claude "重置"，重新建立 skill 优先级。解决长时间会话后 Claude "忘记"自己有 skill 可以用的问题。

**使用时机：**
- Claude 开始按默认模式行事（跳过测试、直接猜 bug、不问设计就写代码）
- "reset" / "回到 superpowers 模式"
- 上下文漂移时

---

### `/writing-skills` — 编写自定义 Skill
**功能：** 教 Claude 怎么创建新 skill。支持在 `~/.config/superpowers/skills/` 目录下建立个人 skill 库。

**使用时机：**
- 需要为团队定制 skill（如公司代码审查规范、部署流程约束）
- "create a new skill" / "custom skill"

---

## 完整工作流

```
开始新功能
    │
    ▼
┌─────────────────┐
│  /brainstorming │  ← 设计阶段，产出 spec 文档（HARD-GATE：未批准不许写代码）
└─────────────────┘
    │
    ▼
┌─────────────────────┐
│ /using-git-worktrees │  ← 创建隔离工作区
└─────────────────────┘
    │
    ▼
┌─────────────────┐
│ /writing-plans  │  ← 把 spec 拆成 2-5 分钟的可执行任务，零占位符
└─────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ /subagent-driven-development    │  ← 并行执行（推荐）
│         或                      │     或
│ /executing-plans                │  ← 串行执行
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ /test-driven-development │  ← RED-GREEN-REFACTOR（贯穿实现阶段）
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ /requesting-code-review  │  ← 提审前自检
└─────────────────────────┘
    │
    ▼
┌───────────────────────────────────┐
│ /finishing-a-development-branch   │  ← merge/PR/保留/丢弃，清理 worktree
└───────────────────────────────────┘
```

**插入点（按需）：**
- 遇到 bug → 插入 `/systematic-debugging`
- 验证有疑问 → 插入 `/verification-before-completion`
- 上下文漂移 → 插入 `/using-superpowers`

---

## 常见问题

**Q：Superpowers 适合小项目吗？感觉流程太重。**
> A：brainstorming 的 spec 可以很短，一个改动只需要几句话的设计文档。问题不是"项目大不大"，而是"你能不能接受返工"。很多"5 分钟小改动"，因为没有设计直接上手，结果改了三轮花了两小时。

**Q：subagent-driven-development 和 executing-plans 可以混用吗？**
> A：可以。同一个 plan 里，某些任务用 subagent，某些任务手动执行。这在部分任务需要你实际操作（如手动配置环境变量）时很有用。

**Q：systematic-debugging 的"三次失败规则"是绝对的吗？**
> A：不是"不许再改了"，而是"在第三次失败后，必须停下来讨论是不是架构问题，而不是继续猜"。讨论后确认方向，可以继续——但要在讨论之后，不是直接冲第四次。

**Q：整套流程跑一遍要多久？**
> A：中等复杂功能（4-6 个任务）：brainstorming 30-40 分钟，writing-plans 15-20 分钟，execution 因任务而异。前两次比直接写慢，第三次开始返工率断崖下降，总时间反而更短。

**Q：skill 能自定义吗？**
> A：可以。`/writing-skills` 就是教 Claude 创建新 skill 的。`~/.config/superpowers/skills/` 支持个人 skill 库。

---

## 两个经常踩的坑

### 坑一：上下文漂移
长时间会话里，Claude 会逐渐"忘记"自己有 skill 可以用，开始按默认模式行事：跳过测试、直接猜 bug、不问设计就写代码。

**解法：** 显式喊 `/using-superpowers`，重置 skill 优先级。

### 坑二：把 brainstorming 当问答机用
brainstorming 问问题是为了做设计，不是"帮你想清楚功能"。如果停在问答阶段，没有走到 spec 文档和 writing-plans，后面执行阶段 Claude 拿不到明确的设计依据，质量大打折扣。

**解法：** brainstorming 的价值在于产出一个 **committed spec**，这是后续所有质量的基础。必须走到第 9 步移交 writing-plans。

---

*文档参考：Superpowers v5.1.0（2026 年 5 月）*
*项目地址：GitHub 185,000 stars*
