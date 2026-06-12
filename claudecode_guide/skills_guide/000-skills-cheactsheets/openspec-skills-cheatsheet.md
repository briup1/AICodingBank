# OpenSpec Skills 速查表

> 生成于 2026/06/02 | 覆盖 11 个 OpenSpec 相关 skill
> OpenSpec 是一个基于 artifact 的结构化变更管理工作流，通过 `openspec` CLI 管理变更（change）的全生命周期。

---

## 快速索引（按场景）

| 场景 | 推荐 Skill | 备注 |
|---|---|---|
| ✨ 创建并生成完整方案 | `/opsx:propose` | 推荐入口 |
| 📝 逐步创建 change | `/opsx:new` |
| ⚡ 快速生成 artifacts | `/opsx:ff` |
| 🔍 只探索不实现 | `/opsx:explore` |
| 🚀 继续现有 change | `/opsx:continue` |
| 💻 按 tasks 实现代码 | `/opsx:apply` |
| 🔄 同步 delta 规格 | `/opsx:sync-specs` |
| ✅ 验证实现 | `/opsx:verify` |
| 📦 归档单个 change | `/opsx:archive` |
| 📦 批量归档 | `/opsx:bulk-archive` |
| 🎓 首次入门引导 | `/opsx:onboard` |

---

## 目录

- [一、OpenSpec 概述](#一openspec-概述)
- [二、创建与规划](#二创建与规划)
- [三、持续推进](#三持续推进)
- [四、收尾与归档](#四收尾与归档)
- [五、规格同步](#五规格同步)
- [六、探索与入门](#六探索与入门)
- [七、技能对比与决策](#七技能对比与决策)
- [八、完整工作流图](#八完整工作流图)
- [九、CLI 命令速查](#九cli-命令速查)
- [十、Artifact 类型说明](#十artifact-类型说明)

---

## 一、OpenSpec 概述

OpenSpec 用 **artifact-driven workflow** 管理代码变更。每个 change 是一个目录 `openspec/changes/<name>/`，包含按 schema 定义的 artifact 文件。典型 schema（spec-driven）的 artifact 顺序：

```
proposal → specs → design → tasks
    │          │       │        │
    ▼          ▼       ▼        ▼
   WHY       WHAT    HOW     DO IT
```

**核心前提**：需要先安装 `openspec` CLI。

---

## 二、创建与规划

### `/opsx:new` — 创建新 change（逐步创建 artifact）
**核心问题：我要开始一个新功能/修复，想一步一步来**

**功能：** 创建 change 目录，展示第一个 artifact 的模板和指令，然后 **STOP 等待用户**。一次只创建一个 artifact，让用户参与每个步骤。

**使用时机：**
- "我想做一个新功能"
- "我要修复某个 bug"
- 用户想要参与每个 artifact 的创建过程
- 需要与用户反复确认的需求

**Steps：**
1. 确认需求 → 推导 kebab-case 名称
2. `openspec new change "<name>"` → 创建目录
3. `openspec status --change "<name>"` → 查看 artifact 状态
4. `openspec instructions <first-artifact> --change "<name>"` → 获取模板
5. **STOP** — 展示模板，等待用户指令

**关键特性：**
- 一次只创建一个 artifact
- 不自动写入任何内容
- 如果 change 已存在，建议用 `/opsx:continue`

**不适合：**
- 想快速生成所有 artifacts（用 `/opsx:ff` 或 `/opsx:propose`）
- 已有 change 要继续（用 `/opsx:continue`）

---

### `/opsx:ff` — 快速创建所有 artifacts（一步到位）
**核心问题：我要快速生成所有 artifacts，马上进入实现**

**功能：** 创建 change 后，按依赖顺序自动创建所有 `applyRequires` 定义的 artifact，直到可以开始实现。用 TodoWrite 跟踪进度，逐个读取依赖、创建文件。

**使用时机：**
- "帮我生成 proposal、specs、design、tasks"
- 需求明确，不需要逐步确认
- 想尽快拿到完整的实现计划

**关键特性：**
- 自动创建所有 artifact，直到 apply-ready
- 遇到不清楚的地方会询问用户
- 每次创建后重新检查状态

**不适合：**
- 需求不明确，需要反复讨论（用 `/opsx:new` 或 `/opsx:explore`）
- 已有 change 要继续（用 `/opsx:continue`）

---

### `/opsx:propose` — 创建 change 并生成全部 artifacts（推荐）
**核心问题：描述一下我想做什么，帮我生成完整的提案**

**功能：** `/opsx:ff` 的增强版。同样的自动 artifact 创建流程，但文案和定位更偏向"从描述到完整方案"。生成的 artifacts：proposal.md + design.md + tasks.md。

**使用时机：**
- "我想加一个用户认证系统"
- "帮我设计一下这个功能的实现方案"
- 最常见的入口 skill

**和 `/opsx:ff` 的区别：**
| 对比项 | `/opsx:propose` | `/opsx:ff` |
|---|---|---|
| 定位 | 从描述到完整方案 | 快速 artifact 生成 |
| 触发词 | "我想做..." / "帮我设计..." | "快速生成 artifacts" |
| 输出风格 | 更完整、教学性更强 | 更简洁、进度导向 |

**不适合：**
- 只是想思考不实现（用 `/opsx:explore`）

---

## 三、持续推进

### `/opsx:continue` — 继续创建下一个 artifact
**核心问题：我之前创建的 change 还没完成，继续下一步**

**功能：** 检查现有 change 的状态，找到第一个 `status: "ready"` 的 artifact，获取指令并创建它，然后 STOP。一次只创建一个 artifact。

**使用时机：**
- "继续"
- "继续刚才的 change"
- 创建完 proposal 后，继续创建 specs

**关键特性：**
- 自动选择第一个 ready 的 artifact
- 读取已完成 artifact 作为依赖上下文
- 如果所有 artifact 都完成，提示可以 implement 或 archive

**Guardrails：**
- 不猜测 change 名称，总是让用户选择（多 change 时）
- 不跳过 artifact 顺序
- `context` 和 `rules` 是给你的约束，不写入文件

**不适合：**
- 直接进入实现（用 `/opsx:apply`）
- 创建新 change（用 `/opsx:new`）

---

### `/opsx:apply` — 实现 change 中的 tasks
**核心问题：开始写代码，按 tasks 清单执行**

**功能：** 读取 change 的 artifacts（尤其是 tasks.md），逐个完成任务中的 checkbox。实施代码修改，标记任务完成，循环直到做完或遇到阻塞。

**使用时机：**
- "开始实现"
- "帮我写这个功能的代码"
- 已有 tasks，需要执行

**Steps：**
1. 选择 change（推断或让用户选）
2. `openspec status --change "<name>" --json` → 了解 schema
3. `openspec instructions apply --change "<name>" --json` → 获取 apply 指令和 contextFiles
4. 读取 contextFiles（proposal/specs/design/tasks 等）
5. 逐个实现 pending task：
   - 展示当前 task
   - 修改代码
   - 标记 `- [ ]` → `- [x]`
   - 继续下一个

**暂停条件：**
- Task 不清楚 → 询问
- 实现揭示设计问题 → 建议更新 artifact
- 遇到错误或阻塞 → 报告并等待

**不适合：**
- 没有 tasks（先用 `/opsx:continue` 创建）
- artifact 不全被阻塞（提示用 `/opsx:continue`）
- 只是探索想法（用 `/opsx:explore`）

---

## 四、收尾与归档

### `/opsx:archive` — 归档完成的 change
**核心问题：这个 change 做完了，归档起来**

**功能：** 检查 artifact 和 task 完成状态，可选同步 delta specs 到 main specs，然后将 change 移动到 `openspec/changes/archive/YYYY-MM-DD-<name>/`。

**使用时机：**
- "归档"
- "这个做完了"
- 所有 tasks 已完成

**Steps：**
1. 选择 change
2. 检查 artifact completion（未完成会警告并确认）
3. 检查 task completion（未完成会警告并确认）
4. 检查 delta specs → 可选 sync 到 main specs
5. `mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-DD-<name>/`

**Guardrails：**
- 不阻塞归档（只是警告+确认）
- 保留 `.openspec.yaml`
- 如果归档目录已存在，报错

**不适合：**
- 还有未完成的任务且不想归档

---

### `/opsx:bulk-archive` — 批量归档多个 change
**核心问题：好几个 change 都完成了，一起归档**

**功能：** 一次归档多个 change，智能检测 delta spec 冲突（多个 change 修改同一个 capability），通过检查代码库来确定实际实现情况，按时间顺序解决冲突。

**使用时机：**
- "归档所有完成的 change"
- 并行开发多个功能后统一收尾

**冲突解决策略：**
| 情况 | 处理方式 |
|---|---|
| 只有一个 change 实现了 | 只 sync 那个 |
| 两个都实现了 | 按时间顺序应用（老的先，新的覆盖）|
| 都没实现 | 跳过 sync，警告用户 |

**Guardrails：**
- 总是让用户选择要归档的 change（多选）
- 显示 consolidated status table 后统一确认
- 某个 change 失败不影响其他

**不适合：**
- 只有一个 change（用 `/opsx:archive`）

---

### `/opsx:verify` — 验证实现是否符合 artifacts
**核心问题：实现完了，检查一下对不对**

**功能：** 三维验证报告，检查实现是否完整、正确、一致。

**验证维度：**

| 维度 | 检查内容 | 问题等级 |
|---|---|---|
| **Completeness** | tasks 是否全部完成、spec requirements 是否都有实现 | CRITICAL |
| **Correctness** | requirement 实现是否匹配 intent、scenario 是否被覆盖 | WARNING |
| **Coherence** | 是否遵循 design 决策、代码风格是否一致 | SUGGESTION |

**使用时机：**
- "检查一下实现"
- "验证一下"
- 归档前做最终检查

**输出：** Summary Scorecard + 分级问题列表（CRITICAL/WARNING/SUGGESTION），每项带具体推荐和文件引用。

**Graceful Degradation：**
- 只有 tasks → 只检查 task completion
- 有 tasks + specs → 检查 completeness + correctness
- 全套 artifact → 三维全检

**不适合：**
- 还没有实现（用 `/opsx:apply`）

---

## 五、规格同步

### `/opsx:sync-specs` — 同步 delta specs 到 main specs
**核心问题：把 change 里的规格更新合并到主规格**

**功能：** Agent-driven 的智能合并。读取 change 的 delta specs，智能应用到 `openspec/specs/<capability>/spec.md`，支持增量更新（如只加一个 scenario，不需要复制整个 requirement）。

**Delta Spec 操作类型：**

| 操作 | 行为 |
|---|---|
| **ADDED** | 新增 requirement（已存在则更新）|
| **MODIFIED** | 修改现有 requirement（加 scenario、改描述等）|
| **REMOVED** | 删除整个 requirement block |
| **RENAMED** | FROM → TO 重命名 |

**使用时机：**
- 用户想在不归档的情况下更新 main specs
- 归档前选择 sync
- 多个 change 的规格需要整合

**关键原则：Intelligent Merging**
- Delta 代表 **intent**，不是 wholesale replacement
- 可以 partial update（只加 scenario）
- 幂等操作 — 跑两次结果一致

**不适合：**
- 没有 delta specs 的 change

---

## 六、探索与入门

### `/opsx:explore` — 探索模式（只思考不实现）
**核心问题：我想想想这个问题，不急着写代码**

**功能：** 思考伙伴模式。可以读代码、画 ASCII 图、比较方案、提问挑战假设，但 **绝不写应用代码**。可以创建 OpenSpec artifacts（这是记录思考，不是实现）。

**The Stance：**
- Curious, not prescriptive — 自然提问，不照本宣科
- Visual — 大量使用 ASCII 图
- Grounded — 基于实际代码库探索
- Patient — 不急于下结论

**使用时机：**
- "我想想想..."
- "帮我分析一下..."
- "这个该怎么设计？"
- 实现前需要理清思路
- 卡住了需要重新审视

**OpenSpec 集成：**
- 检查现有 change 并引用其 artifacts
- 当洞察形成时，主动提出"要记录到某个 artifact 吗？"
- 不自动 capture，只 offer

**Guardrails：**
- **绝不实现** — 不写应用代码
- 不假装理解 — 不清楚就深挖
- 不强制结构 — 让模式自然浮现

**不适合：**
- "帮我实现..."（提醒先退出 explore 模式）

---

### `/opsx:onboard` — 引导完成首个完整工作流
**核心问题：我第一次用 OpenSpec，带我走一遍完整流程**

**功能：** 教学体验。扫描代码库找 small improvement（TODO/FIXME/missing tests 等），选一个小任务，完整演示：Explore → New → Proposal → Specs → Design → Tasks → Apply → Archive 的完整周期。

**Phase 流程：**

```
Phase 1: Welcome      → 介绍完整流程（~15-20 分钟）
Phase 2: Task Selection → 扫描代码库，提供 3-4 个建议
Phase 3: Explore Demo → 快速探索模式演示
Phase 4: Create Change → 创建 change 目录
Phase 5: Proposal     → WHY（用户确认后保存）
Phase 6: Specs        → WHAT（WHEN/THEN/AND 格式）
Phase 7: Design       → HOW（Goals/Non-Goals/Decisions）
Phase 8: Tasks        → DO（checkboxed task list）
Phase 9: Apply        → 实现每个 task
Phase 10: Archive     → 归档
Phase 11: Recap       → 总结 + 命令速查
```

**Guardrails：**
- 遵循 EXPLAIN → DO → SHOW → PAUSE 模式
- 使用真实代码库任务
- 温和引导选择小任务（用户可 override）
- 用户可随时退出， graceful exit

**不适合：**
- 已有经验的用户（直接用其他 skill）

---

## 七、技能对比与决策

### 一句话区分

| Skill | 一句话 | 阶段 |
|---|---|---|
| `/opsx:propose` | **描述需求 → 生成完整方案（推荐入口）** | 开始 |
| `/opsx:new` | **创建 change，只展示第一个 artifact 模板** | 开始 |
| `/opsx:ff` | **快速生成所有 artifacts，一步到位** | 开始 |
| `/opsx:explore` | **思考伙伴，只分析不实现** | 开始/中间 |
| `/opsx:continue` | **继续现有 change，创建下一个 artifact** | 推进 |
| `/opsx:apply` | **按 tasks 清单执行代码实现** | 推进 |
| `/opsx:sync-specs` | **把 change 的 delta specs 合并到主规格** | 推进/收尾 |
| `/opsx:verify` | **三维验证实现是否符合 artifacts** | 收尾 |
| `/opsx:archive` | **归档单个完成的 change** | 收尾 |
| `/opsx:bulk-archive` | **批量归档多个 change，智能解决冲突** | 收尾 |
| `/opsx:onboard` | **手把手教你完成第一个完整 workflow** | 入门 |

### 快速决策

| 你想做的事 | 用哪个 |
|---|---|
| "我想做 xxx 功能，帮我设计一下" | `/opsx:propose` |
| "新建一个 change，一步一步来" | `/opsx:new` |
| "快速生成所有 artifacts" | `/opsx:ff` |
| "继续刚才的 change" | `/opsx:continue` |
| "开始写代码实现" | `/opsx:apply` |
| "检查一下实现对不对" | `/opsx:verify` |
| "做完了，归档" | `/opsx:archive` |
| "好几个做完了，一起归档" | `/opsx:bulk-archive` |
| "把规格更新合并到主规格" | `/opsx:sync-specs` |
| "帮我分析一下这个问题" | `/opsx:explore` |
| "第一次用，带我一圈" | `/opsx:onboard` |

### 选择入口 skill

```
你有需求想实现
    │
    ├── 第一次用 OpenSpec ───────────→ /opsx:onboard
    │
    ├── 想先想想/分析 ───────────────→ /opsx:explore
    │
    ├── 需求明确，想快速拿到方案 ─────→ /opsx:propose（推荐）
    │                                   或 /opsx:ff
    │
    └── 想一步一步参与创建 ──────────→ /opsx:new
```

---

## 八、完整工作流图

### 单 Change 生命周期

```
                    ┌─────────────┐
                    │   有需求    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │/opsx:new│  │/opsx:ff │  │/opsx:pro│
        │(逐步)   │  │(快速)   │  │(ose)    │
        └────┬────┘  └────┬────┘  └────┬────┘
             │            │            │
             └────────────┼────────────┘
                          ▼
              ┌───────────────────────┐
              │  openspec/changes/    │
              │      <name>/          │
              │  ├── proposal.md      │
              │  ├── specs/           │
              │  ├── design.md        │
              │  └── tasks.md         │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  /opsx:continue       │
              │  逐个创建 artifacts   │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  /opsx:apply          │
              │  按 tasks 实现代码    │
              │  - [ ] → - [x]        │
              └───────────┬───────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
        ┌─────────────┐         ┌─────────────┐
        │  实现中遇到  │         │  实现完成    │
        │  问题/卡住了 │         │              │
        └──────┬──────┘         └──────┬──────┘
               │                       │
               ▼                       ▼
        ┌─────────────┐         ┌─────────────┐
        │/opsx:explore│         │ /opsx:verify│
        │ 重新思考     │         │ 三维验证     │
        └─────────────┘         └──────┬──────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
              ┌──────────┐      ┌──────────┐      ┌──────────┐
              │ 有警告   │      │ 全部通过 │      │ 需要更新 │
              │ 修复后继续│      │          │      │ main specs│
              └────┬─────┘      └────┬─────┘      └────┬─────┘
                   │                 │                 │
                   └─────────────────┼─────────────────┘
                                     ▼
                          ┌─────────────────┐
                          │  /opsx:archive  │
                          │  (或 bulk)      │
                          └────────┬────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ openspec/changes/archive/    │
                    │   YYYY-MM-DD-<name>/         │
                    └──────────────────────────────┘
```

### 批量归档与冲突解决

```
多个 change 要归档
    │
    ▼
┌──────────────────────────┐
│  /opsx:bulk-archive      │
│  1. 列出所有 active      │
│  2. 用户多选             │
│  3. 批量验证状态         │
│  4. 检测 spec 冲突       │
│  5. 检查代码库解决冲突   │
│  6. 显示汇总表           │
│  7. 统一确认             │
│  8. 逐个归档 + sync      │
└──────────────────────────┘
```

---

## 九、CLI 命令速查

### 变更管理

| 命令 | 作用 |
|---|---|
| `openspec new change "<name>"` | 创建新 change |
| `openspec status --change "<name>" --json` | 查看 artifact 状态 |
| `openspec instructions <artifact-id> --change "<name>" --json` | 获取 artifact 模板 |
| `openspec instructions apply --change "<name>" --json` | 获取 apply 指令和 contextFiles |
| `openspec list --json` | 列出所有 change |
| `openspec archive "<name>"` | 归档 change |

### 状态字段

| 状态 | 含义 |
|---|---|
| `blocked` | 依赖未满足，还不能创建 |
| `ready` | 依赖已满足，可以创建 |
| `done` | 已完成 |

### 目录结构

```
openspec/
├── changes/
│   ├── <change-name>/
│   │   ├── .openspec.yaml      # change 元数据
│   │   ├── proposal.md         # WHY
│   │   ├── specs/
│   │   │   └── <capability>/
│   │   │       └── spec.md     # WHAT (delta)
│   │   ├── design.md           # HOW
│   │   └── tasks.md            # DO (checkboxes)
│   └── archive/
│       └── YYYY-MM-DD-<name>/  # 归档的 change
└── specs/
    └── <capability>/
        └── spec.md             # 主规格 (main specs)
```

---

## 十、Artifact 类型说明

### spec-driven schema 默认 artifact 序列

| Artifact | 文件 | 内容 | 关键约束 |
|---|---|---|---|
| **proposal** | `proposal.md` | Why、What Changes、Capabilities、Impact | Capabilities 列表决定需要几个 spec |
| **specs** | `specs/<capability>/spec.md` | Requirements (WHEN/THEN/AND)、Scenarios | 每个 capability 一个 spec |
| **design** | `design.md` | Context、Goals/Non-Goals、Decisions、Approach | 技术决策记录 |
| **tasks** | `tasks.md` | Checkboxed implementation tasks | 驱动 apply 阶段 |

### Delta Spec 格式

```markdown
## ADDED Requirements
### Requirement: New Feature
Description...
#### Scenario: Basic case
- **WHEN** user does X
- **THEN** system does Y

## MODIFIED Requirements
### Requirement: Existing Feature
#### Scenario: New scenario to add
- **WHEN** user does A
- **THEN** system does B

## REMOVED Requirements
### Requirement: Deprecated Feature

## RENAMED Requirements
- FROM: `### Requirement: Old Name`
- TO: `### Requirement: New Name`
```

---

## 补充：重要 Guardrails

### Artifact 创建
- `context` 和 `rules` 是给 AI 的约束，**绝不写入 artifact 文件**
- 总是读取依赖 artifact 后再创建新 artifact
- 不跳过 artifact 顺序
- 验证文件写入成功后再继续

### Apply 阶段
- 保持代码修改 minimal 且 focused
- 每个 task 完成后立即更新 checkbox
- 遇到 unclear/block/error 时 pause，不猜测
- 实现揭示设计问题时，建议更新 artifact

### Archive 阶段
- 不阻塞归档（只是警告+确认）
- 归档目录名格式：`YYYY-MM-DD-<name>`
- 保留 `.openspec.yaml`
