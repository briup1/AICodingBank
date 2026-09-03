---
id: 0001
slug: personal-ai-workbench-foundation
status: approved
created: 2026-09-03
requirement: requirement.md
chosen: A
---

# 方案设计：个人 AI 工作台最小骨架

## 1. 需求↔方案映射

| 需求 | 方案落点 | 覆盖 |
| --- | --- | --- |
| [统一理解工作台](requirement.html#用户故事) | `README.md` 提供人类入口；`WORKBENCH.md` 作为工作台定义的唯一事实来源 | 是 |
| [判断任务阶段](requirement.html#用户故事) | `WORKBENCH.md` 定义六阶段路由、进入条件、退出证据和下一步 | 是 |
| [Agent 使用唯一阶段路由](requirement.html#用户故事) | `AGENTS.md`、`CLAUDE.md` 只保留入口指针，路由规则集中在 `WORKBENCH.md` | 是 |
| [查找项目上下文](requirement.html#用户故事) | `WORKBENCH.local.md` 保存项目指针表；项目真实文件仍是事实来源 | 是 |
| [保护个人上下文](requirement.html#用户故事) | `.gitignore` 忽略真实本地文件；`WORKBENCH.local.example.md` 仅提供无隐私模板 | 是 |
| [保持 Skill 供应链](requirement.html#用户故事) | `skills.yaml`、`skills-lock.json`、`install.py`、`CATALOG.md` 不改接口和行为 | 是 |

## 2. 前后对比

### 用户视角

| BEFORE | AFTER |
| --- | --- |
| 分别记住 AICodingBank、知识库、Goal、Personal Workbench 和各项目的用途 | 从 `README.md` 进入 `WORKBENCH.md`，先看总地图，再按阶段和项目指针进入现有组件 |
| 面对多个 Skill 自行判断先后关系 | 根据请求目标和已有证据选择唯一阶段，再读取该阶段对应的现有 Skill |
| 私人偏好和项目路径散落在机器环境中 | 在被 Git 忽略的 `WORKBENCH.local.md` 中维护轻量个人上下文和项目索引 |

### 系统视角

```text
BEFORE

README -> Skill 管理说明
AGENTS/CLAUDE -> Skill 维护规则
Knowledge / Goal / Workbench / Projects -> 相互并列

AFTER

README ------------------------------+
                                     |
AGENTS.md / CLAUDE.md ---------------+--> [NEW] WORKBENCH.md
                                                |
                      +-------------------------+--------------------+
                      |                         |                    |
              能力控制面                 任务与验证              知识系统
        skills.yaml / CATALOG       Goal / DAG / Review       Knowledge Base
                      |
                      +--> [NEW, LOCAL] WORKBENCH.local.md --> 项目真实目录
```

新增的只是控制骨架和指针，不搬迁下层系统。

## 3. 接口与契约设计

### 3.1 文件接口

| 文件 | 调用者需要知道的接口 | 明确不承担 |
| --- | --- | --- |
| `README.md` | 工作台一句话定位；链接到 `WORKBENCH.md`；保留 AICodingBank 使用说明 | 不重复阶段路由和个人项目表 |
| `WORKBENCH.md` | 工作台边界、系统地图、六阶段路由、组件职责、使用顺序 | 不保存个人路径，不罗列全部 Skill 细节，不执行任务 |
| `WORKBENCH.local.example.md` | 个人上下文和项目索引的字段模板 | 不含真实个人资料，不作为项目事实来源 |
| `WORKBENCH.local.md` | 本机稳定偏好、项目指针和知识入口；存在时供 Agent 读取 | 不保存密钥、会话转录、临时任务状态或项目实现细节 |
| `AGENTS.md` / `CLAUDE.md` | 开始任务时读取 `WORKBENCH.md`；本地文件存在则继续读取；其余保留 Skill 维护红线 | 不复制工作台正文 |
| `.gitignore` | 保证 `WORKBENCH.local.md` 不被跟踪 | 不忽略共享模板 |

### 3.2 阶段路由契约

路由以“用户本次希望得到什么结果”为主，以“已有证据状态”为辅，不按关键词机械匹配。

```text
只想理解当前事实？ ----------------------------> Observe / 观察
想改变行为，但目标或验收尚未确认？ ------------> Confirm / 确认
目标已确认，正在决定怎么做？ ------------------> Design / 设计
方案或边界已稳定，要求产生改动？ --------------> Execute / 执行
已有产物，要求证明是否正确或可交付？ ----------> Verify / 验证
结果已验证，要求保存可复用结论？ --------------> Learn / 沉淀
```

| 阶段 | 进入条件 | 退出证据 | 复用现有能力 |
| --- | --- | --- | --- |
| Observe | 目标是了解现状，不要求产生持久变更 | 基于真实文件、命令或来源的事实结论 | 项目阅读、调研、诊断类能力 |
| Confirm | 提出新需求或行为变化，目标、边界或验收未获确认 | 已批准的需求或清晰、可验收的小任务边界 | `wl-req-confirm`、`wl-brainstorming` |
| Design | 需求已稳定，仍需确定接口、复用、风险或实施路径 | 已批准方案；简单任务则为获批准的最小方法 | `wl-design-doc`、计划及方案审查类 Skill |
| Execute | 方案和修改边界稳定，用户要求落地产物 | 实际改动及执行证据 | `wl-ticket-run`、`wl-subagent-driven-development`、`wl-investigate`、Pi Goal |
| Verify | 已有待检查产物或实现 | 实际测试、审查和验收证据 | `wl-requesting-code-review`、测试和浏览器验证类 Skill |
| Learn | 工作结果已经验证，结论具有跨会话价值 | 写入适当的 Memory、知识库或项目文档 | Memory、知识库流程 |

冲突时采用以下优先级：

```text
用户明确指定阶段
  -> 已批准文档或既有任务状态
  -> 用户希望得到的结果
  -> 无法唯一判断时再问一个澄清问题
```

阶段不是强制把所有任务走满六步。只读问题可在 Observe 结束；提交代码等边界明确的操作可直接进入 Execute；任何阶段都不能伪造其退出证据。

### 3.3 本地项目索引契约

```markdown
## 项目索引

| 项目 | 本地路径 | 用途 | 知识入口 | 常用入口 |
| --- | --- | --- | --- | --- |
| example | /absolute/path | 一句话用途 | wiki/path 或 - | README.md / package.json |
```

- “本地路径”只用于导航，不代表项目归属于当前仓库。
- “用途”只写稳定定位；详细架构留在项目自身或知识库。
- “常用入口”指向真实文件，不复制构建、测试、部署命令。
- 项目路径失效时，删除或修正本地行；不修改共享模板。

### 3.4 隐私契约

允许写入：稳定沟通偏好、项目路径、项目一句话用途、知识入口。

禁止写入：Token、密码、Cookie、私钥、完整连接串、会话原文、客户敏感数据、临时任务进度。

## 4. 历史资产复用分析

| 资产 | 复用方式 | 证据 |
| --- | --- | --- |
| Skill 能力控制面 | 原样保留登记、验证、安装和目录生成职责 | `skills.yaml`、`skills-lock.json`、`install.py`、`CATALOG.md` |
| 人类入口 | 扩展现有说明，不新建门户程序 | `README.md` 已是仓库总入口 |
| Agent 入口 | 在现有规则文件增加短指针，不建立新加载器 | `AGENTS.md`、`CLAUDE.md` 已由当前 Harness 提供给 Agent |
| 需求到交付流程 | 路由到现有 `wl-*` Skill，不新增六个阶段 Skill | `skills/wl-req-confirm/`、`skills/wl-design-doc/`、`skills/wl-ticket-run/` 等 |
| 持续任务 | 将 Pi Goal 视为 Execute 阶段的执行机制 | 当前环境已有 Goal 工具；`skills/goal-coach/` 已提供适用性判断 |
| 任务可观测性 | 将 Personal Workbench 视为状态展示能力 | `skills/agent-dag-reporting/SKILL.md` 已定义计划、状态、产物和检查点上报 |
| 长期知识 | 保持独立知识库，工作台只保存入口 | Knowledge Base 的 `_index.md` 已定义索引、schema 和审计规则 |
| 本机覆盖约定 | 延续“共享配置 + Git 忽略本地覆盖”的现有模式 | `.gitignore` 已忽略 `skills.local.yaml` |
| 项目术语 | 使用项目级 glossary，不把术语散落到方案正文之外 | `CONTEXT.md` |

首期不从零构建运行时，因为现有资产已经覆盖能力、执行、观测和知识；缺口只是一个浅接口背后的清晰路由。

## 5. 多方案并列

| 方案 | 做法 | 优点 | 代价 |
| --- | --- | --- | --- |
| A. 独立控制文档（推荐） | 新增 `WORKBENCH.md` 和本地模板；README、AGENTS、CLAUDE 只放短指针 | 单一事实来源；常驻上下文短；人和 Agent 共用同一地图；以后可独立演进 | 增加一个需要维护的顶层文档 |
| B. 入口文件内嵌 | 把人类说明写入 README，把 Agent 路由分别写入 AGENTS 和 CLAUDE；只新增本地模板 | 少一个顶层文件 | 路由重复三份，容易漂移；AGENTS 常驻上下文膨胀；人和 Agent 看到的系统可能不一致 |

**推荐 A**：它把复杂度集中在一个接口中，删除它会迫使相同信息重新散回三个调用点，因此该文档能提供实际的局部性和复用价值。

方案选定前不进入实现；选定结果写入 frontmatter `chosen`。

## 6. 审查结论（附证据）

| 维度 | 状态 | 结论与证据 |
| --- | --- | --- |
| 可行性 | 通过 | 执行 `test -f AGENTS.md && test -f CLAUDE.md && test -f README.md`，三个既有入口均存在；`WORKBENCH.md`、`WORKBENCH.local.md`、`WORKBENCH.local.example.md` 均无命名冲突。 |
| 路由唯一性 | 通过 | 运行六类请求映射检查，输出 `six canonical requests -> six unique stages: OK`，六个典型请求分别映射到 Observe、Confirm、Design、Execute、Verify、Learn。 |
| 复用性 | 通过 | 实际读取 `skills.yaml` 及主要 `wl-*` Skill，现有能力已覆盖需求、设计、执行、验证；无需新增阶段 Skill。 |
| 规范性 | 通过 | 实际读取 `AGENTS.md`、`README.md`、`at-standards/references/core.md`；方案仅修改需求可追溯文件，不新增依赖，不改变现有接口。 |
| 兼容性 | 通过 | 执行 `python3 -m unittest tests/test_install.py`，结果为 `Ran 8 tests ... OK`；设计不修改安装器输入输出。 |
| 隐私 | 通过 | `git check-ignore -v skills.local.yaml` 证明仓库已有本地覆盖约定；方案复用同一模式，让真实本地上下文进入 `.gitignore`。 |
| 工作区保护 | 通过 | 设计前 `git status --short` 仅显示本需求新增的 `CONTEXT.md` 与 `docs/`，未发现需覆盖的已跟踪修改。 |

## 7. 最小验证

**风险点**：仅靠文档入口，能否让六类典型请求稳定落到唯一阶段，而不需要首期增加路由程序。

**验证方法**：先把六类验收请求映射为六个阶段，检查阶段值是否唯一；同时验证人类和 Agent 的三个既有入口可承载短指针。

**实际输出**：

```text
six canonical requests -> six unique stages: OK
了解现状: Observe
确认需求: Confirm
设计方案: Design
开始实现: Execute
检查结果: Verify
记录经验: Learn

AGENTS.md: present
CLAUDE.md: present
README.md: present
```

安装器回归基线：

```text
........
----------------------------------------------------------------------
Ran 8 tests in 0.004s

OK
```

**结论**：可行。首期不需要路由程序；一个共享控制文档加三个既有入口即可承载阶段判断。

实现后使用 Pi `--no-session --no-extensions --no-skills --tools read -p` 启动全新只读会话验收。新会话实际读取 `WORKBENCH.md` 和被 Git 忽略的 `WORKBENCH.local.md`，并将六类请求依次正确映射到 Observe、Confirm、Design、Execute、Verify、Learn。
