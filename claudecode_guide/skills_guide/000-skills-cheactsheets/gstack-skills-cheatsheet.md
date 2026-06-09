# gstack Skill 速查表

> 本文档汇总了 gstack 包中所有可用的 skill，按功能场景分类，方便在需要时快速查找。
> 实际路径：`~/.claude/skills/gstack/[skill-name]/SKILL.md`

---

## 快速索引（按场景）

| 场景 | 推荐 Skill | 备注 |
|---|---|---|
| 🐛 调试 Bug | `/investigate` | 好用, 将报错原因贴过来查找根本原因
| 🔍 代码审查 | `/review` |
| 🚀 发布/提交 PR | `/ship` |
| 🧪 测试网站 | `/qa` | 好用, 将url贴过来, 分析问题
| 📊 性能基准 | `/benchmark` |
| 🔒 安全审计 | `/cso` |
| 💡 产品创意 | `/office-hours` |
| 🏗️ 架构评审 | `/plan-eng-review` | 需要重点测试,评估其方案评估能力
| 🎨 设计评审 | `/plan-design-review` | 需要重点测试,评估其方案评估能力
| 📦 部署上线 | `/land-and-deploy` |
| 💾 保存进度 | `/context-save` |
| 📂 恢复进度 | `/context-restore` |
| ⚡ 全流程自动化审查 | `/autoplan` |

---

## 一、调试与排错

### `/investigate` — 系统性调试
**功能：** 四阶段根因排查（调查 → 分析 → 假设 → 修复）。铁律：不找到根因不修复。自动锁定调试范围、查找已知模式、要求回归测试。

**使用时机：**
- "debug this" / "fix this bug"
- "why is this broken" / "root cause analysis"
- 用户报告错误、500、堆栈跟踪、意外行为
- "昨天还好好的" / 排查某功能突然失效

**特点：** 3 次修复失败后自动 STOP 并询问；修复涉及 >5 文件时询问影响范围

---

### `/careful` — 安全警戒模式
**功能：** 在执行 `rm -rf`、`DROP TABLE`、`git push --force`、`git reset --hard` 等破坏性操作前发出警告，用户可逐项覆盖。

**核心机制（Hook 拦截）：**
- 通过 **Hook 拦截** Bash 工具调用，检查命令中的破坏性模式
- 命中危险模式时返回 `permissionDecision: "ask"`，强制用户确认
- **主动激活、按需使用**：不会默认开启，输入 `/careful` 才激活
- **会话级作用域**：仅当前会话有效，新会话需重新运行 `/careful`

**拦截范围：**
| 危险模式 | 示例 |
|---|---|
| `rm -rf` / `rm -r` | `rm -rf /var/data` |
| `DROP TABLE` / `DROP DATABASE` / `TRUNCATE` | SQL 删表/清空 |
| `git push --force` / `-f` | 强推覆盖历史 |
| `git reset --hard` | 丢弃未提交更改 |
| `git checkout .` / `git restore .` | 还原所有文件 |
| `kubectl delete` | 删除 K8s 资源 |
| `docker rm -f` / `docker system prune` | 清理容器/镜像 |

**安全例外（白名单，不拦截）：**
```bash
rm -rf node_modules .next dist build .turbo coverage __pycache__ .cache
```

**使用时机：**
- 操作生产环境或敏感数据前主动激活
- 调试线上系统
- 共享环境中工作
- "be careful" / "warn before destructive"

---

### `/freeze` — 编辑范围锁定
**功能：** 限制当前会话的文件编辑只能在指定目录内，阻止 Edit/Write 越界。

**使用时机：**
- 调试时防止"顺手"修改无关代码
- 只想修改某个模块时
- "freeze" / "only edit this folder"

---

### `/unfreeze` — 解除编辑锁定
**功能：** 清除 `/freeze` 设置的边界，恢复对所有目录的编辑权限。

**使用时机：**
- 需要扩大编辑范围但不想结束会话
- "unfreeze" / "unlock edits"

---

### `/guard` — 完全安全模式
**功能：** `/careful` + `/freeze` 的组合，既有破坏性操作警告，又锁定编辑范围。

**使用时机：**
- 生产环境操作需要最高安全级别
- "guard mode" / "maximum safety"

---

## 二、代码审查

### `/review` — 预合并 PR 审查
**功能：** 对比当前分支与 base 分支的 diff，检查 SQL 注入、LLM 信任边界、竞态条件、副作用等结构性问题。含专家审查团（测试、安全、性能、数据迁移、API 契约、设计）+ 对抗性审查（Claude + Codex 双模型）。

**使用时机：**
- "review this PR" / "code review"
- "pre-landing review" / "check my diff"
- 用户准备合并代码前主动建议

**特点：** Fix-First 流程 — 能自动修的直接修，需判断的批量询问

---

### `/autoplan` — 全自动审查流水线
**功能：** 顺序运行 CEO 审查、设计审查、工程审查、开发者体验审查，自动决策，最终在审批门将品味决策（接近方案、边界范围、Codex 分歧）交给用户。

**使用时机：**
- "run all reviews" / "automatic review pipeline"
- 需要完整审查流水线但不想逐个运行
- 重大功能提交前的全面审查

---

### `/codex` — OpenAI Codex 第二意见
**功能：** 三种模式：代码审查（`codex review`）、对抗挑战（找漏洞）、咨询问答。提供"200 IQ 的自闭症开发者"视角。

**使用时机：**
- 需要独立外部审查意见
- "second opinion" / "outside voice"
- 重大架构决策前交叉验证

---

## 三、发布与部署

### `/ship` — 全自动发布工作流
**功能：** 合并 base 分支 → 运行测试 → 审查 diff → 检查测试覆盖率 → 版本号升级 → 更新 CHANGELOG → 提交 → 推送 → 创建 PR。全自动，无需确认（除非遇到冲突、测试失败、严重问题）。

**使用时机：**
- "ship it" / "create a PR"
- "push to main" / "deploy this"
- 用户说代码准备好了、想部署、想推代码

**特点：** 包含 Review Readiness Dashboard，检查各项审查是否通过

---

### `/land-and-deploy` — 合并并部署
**功能：** 在 `/ship` 创建 PR 后接手：合并 PR → 等待 CI 和部署 → 金丝雀检查验证生产健康。

**使用时机：**
- "merge" / "land" / "deploy"
- "merge and verify" / "ship it to production"

---

### `/setup-deploy` — 部署配置
**功能：** 检测部署平台（Fly.io、Render、Vercel、Netlify、Heroku 等），配置生产 URL、健康检查端点，写入 CLAUDE.md 使后续部署自动。

**使用时机：**
- 新项目首次配置部署
- "configure deploy" / "setup deployment"

---

### `/canary` — 发布后监控
**功能：** 部署后持续监控线上应用，检查控制台错误、性能回归、页面故障。定期截图与部署前基线对比，异常时告警。

**使用时机：**
- "monitor deploy" / "post-deploy check"
- "watch for errors" / "canary"

---

### `/document-release` — 发布后文档更新
**功能：** 读取所有项目文档，对照 diff 更新 README/ARCHITECTURE/CONTRIBUTING/CLAUDE.md，润色 CHANGELOG，清理 TODOS。

**使用时机：**
- "update the docs" / "sync documentation"
- 发布完成后文档同步

---

## 四、测试与 QA

### `/qa` — 系统测试并修复
**功能：** 系统性地测试 Web 应用，发现 bug 后在源码中迭代修复，每个修复原子提交并重新验证。

**使用时机：**
- "qa test this" / "find bugs on site"
- "test the site" / "test and fix"
- 部署前全面测试

---

### `/qa-only` — 仅报告不修复
**功能：** 同 `/qa` 的测试流程，但只生成结构化报告（健康评分、截图、复现步骤），不修改任何代码。

**使用时机：**
- "just report bugs" / "qa report only"
- 想先了解问题全貌再决定修复策略

---

### `/browse` — 无头浏览器测试
**功能：** 快速无头浏览器，导航任意 URL、与元素交互、验证页面状态、对比操作前后差异、截图、测试表单上传等。约 100ms 每命令。

**使用时机：**
- "browse a page" / "headless browser"
- 需要验证页面行为但不想手动打开浏览器

---

### `/open-gstack-browser` — 可视化浏览器
**功能：** 启动 AI 控制的 Chromium 浏览器（带侧边栏扩展），可实时观看每一步操作，侧边栏显示活动流和聊天，内置反爬虫。

**使用时机：**
- "open gstack browser" / "launch browser"
- 需要可视化调试页面交互

---

### `/setup-browser-cookies` — 导入浏览器 Cookie
**功能：** 从真实 Chromium 浏览器导入 cookie 到无头浏览会话，支持交互式选择要导入的域名。

**使用时机：**
- 测试需要登录的页面
- "import cookies" / "login to the site"

---

### `/scrape` — 网页数据抓取
**功能：** 从网页提取数据。首次调用会探索流程并返回 JSON，后续相同意图直接走固化脚本（约 200ms）。只读，如需填写表单请用 `/browse`。

**使用时机：**
- "scrape this page" / "get data from"
- "extract from" / "pull from"

---

### `/skillify` — 固化抓取脚本
**功能：** 将最近一次成功的 `/scrape` 流程固化为永久浏览器 skill，后续相同意图 200ms 内完成。

**使用时机：**
- "skillify" / "codify this scrape"
- 需要重复执行相同的数据抓取任务

---

### `/pair-agent` — 配对远程 AI Agent
**功能：** 生成配对密钥，让远程 AI Agent（OpenClaw、Hermes、Codex、Cursor 等）连接到你的浏览器，获得独立标签页。

**使用时机：**
- "pair with agent" / "connect remote agent"
- 多人/多 Agent 协作测试

---

## 五、性能与基准

### `/benchmark` — 性能回归检测
**功能：** 使用 browse 守护进程建立页面加载时间、Core Web Vitals、资源大小的基线，每次 PR 对比前后差异，追踪性能趋势。

**使用时机：**
- "performance benchmark" / "check page speed"
- "detect performance regression"
- Lighthouse / Web Vitals 相关

---

### `/benchmark-models` — 跨模型基准
**功能：** 对同一提示词并行运行 Claude、GPT（Codex CLI）、Gemini，比较延迟、token、成本和质量（LLM judge）。

**使用时机：**
- "cross model benchmark" / "compare claude gpt gemini"
- "which model should I use"

---

## 六、安全

### `/cso` — 首席安全官模式
**功能：** 基础设施优先的安全审计：密钥考古、依赖供应链、CI/CD 管道安全、LLM/AI 安全、skill 供应链扫描、OWASP Top 10、STRIDE 威胁建模。两种模式：日常（零噪音，8/10 置信度门限）和深度（全面审计）。

**使用时机：**
- "security audit" / "check for vulnerabilities"
- "OWASP review"
- 定期安全检查或重大发布前

---

## 七、产品与设计

### `/office-hours` — YC 办公时间
**功能：** 两种模式：创业模式（6 个强制性问题揭示需求现实）和构建者模式（设计思维头脑风暴）。保存设计文档。

**使用时机：**
- "brainstorm this" / "is this worth building"
- "help me think through" / 产品创意讨论

---

### `/plan-ceo-review` — CEO/创始人视角计划审查
**功能：** 重新审视问题，寻找 10 星产品，挑战前提，必要时扩大范围。四种模式：范围扩展、选择性扩展、保持范围、范围缩减。

**使用时机：**
- "think bigger" / "expand scope"
- "strategy review" / "rethink this plan"
- 重大产品/业务变更前

---

### `/plan-eng-review` — 工程经理视角计划审查
**核心问题：这个计划技术上靠谱吗？能落地吗？**

**审查内容：**
- **架构审查**：模块拆分是否合理？数据流是否清晰？依赖关系是否正确？
- **边界情况**：异常处理、空状态、竞态条件、错误恢复路径
- **测试覆盖**：单元测试、集成测试、E2E 测试策略和覆盖范围
- **性能考量**：大数据量处理、高并发场景、渲染性能、资源占用
- **风险评估**：技术债积累、第三方依赖风险、回滚策略

**使用时机：**
- "review architecture" / "eng plan review"
- "check the implementation plan"
- 架构设计完成后、锁定方案前

**不适合：**
- 还没有技术方案时（先写方案再审查）
- 纯视觉设计问题（用 `/plan-design-review`）
- 面向开发者的 API/工具设计（用 `/plan-devex-review`）

---

### `/plan-design-review` — 设计师视角计划审查
**核心问题：这个设计能打几分？离满分差在哪？**

**审查内容：**
- **设计评分**：为设计维度 0-10 打分（不是代码质量，是设计质量）
- **差距分析**：解释如何从当前分数提升到 10 分
- **修复计划**：给出具体的改进建议和优先级排序

> ⚠️ **注意**：这是**计划阶段**的审查，审查的是"设计方案/规划"。如果你已经实现了页面，想审查实际视觉效果，用 `/design-review`。

**使用时机：**
- "design plan review" / "review UX plan"
- "check design decisions"
- 设计师出稿后、开发实现前

**不适合：**
- 审查已上线的实际页面（用 `/design-review`）
- 审查技术架构（用 `/plan-eng-review`）
- 审查开发者工具体验（用 `/plan-devex-review`）

---

### `/plan-devex-review` — 开发者体验计划审查
**核心问题：开发者用这个产品/工具会爽吗？**

> **DX（Developer Experience）是什么？**
> DX 是"开发者体验"，类比 UX（用户体验），但面向的是**使用你产品的开发者**。好的 DX 意味着开发者能快速理解、安装、配置、集成和调试你的工具/API/SDK。DX 差的典型表现：文档不全、报错信息模糊、安装步骤繁琐、缺乏示例代码、 breaking change 不说明迁移路径。

**审查内容：**
- **开发者画像**：目标开发者是谁？他们的技术水平？核心痛点？
- **竞品基准**：同类产品的 DX 对比（如 Vercel vs Netlify 的 CLI 体验）
- **魔法时刻**：设计中有没有让开发者"哇"的瞬间？
- **摩擦点追踪**：安装、配置、调试、文档中的卡点和阻力

**三种模式：**
- **DX 扩展**：当前 DX 不错，如何更进一步？
- **DX 打磨**：有明显摩擦点，需要系统打磨
- **DX 分类**：系统性梳理 DX 现状，分类问题优先级

**使用时机：**
- "developer experience review" / "dx plan review"
- "check developer onboarding"
- 你的产品/工具面向开发者（CLI、SDK、API、框架、文档站）

**不适合：**
- 面向终端消费者的产品（用 `/plan-design-review`）
- 内部技术架构决策（用 `/plan-eng-review`）

---

### 三者对比速查

| 维度 | `/plan-eng-review` | `/plan-design-review` | `/plan-devex-review` |
|---|---|---|---|
| **核心关注点** | 能不能做、怎么做 | 做得好不好看、好不好用 | 开发者用起来顺不顺 |
| **审查内容** | 架构、数据流、边界情况、测试、性能 | 设计质量评分(0-10)、如何达到10分 | 开发者画像、竞品DX基准、摩擦点 |
| **产出** | 执行计划锁定、架构图、风险评估 | 设计评分卡、改进建议 | DX 评分卡、魔法时刻设计 |
| **介入时机** | 架构设计完成后 | 设计规划阶段 | 面向开发者的产品规划阶段 |
| **典型问题** | "这个架构合理吗？" | "这个设计能打几分？" | "开发者用这个会爽吗？" |

### 审查流水线流程

```
你要做一个新功能/项目
        │
        ▼
┌─────────────────┐
│  先过 CEO 审查   │  ← /plan-ceo-review（战略对不对？做不做、做多大）
└─────────────────┘
        │
        ▼
┌─────────────────┐     ┌─────────────────┐
│ 工程经理审查     │     │ 设计师审查       │
│ /plan-eng-review │  +  │ /plan-design-review│
│ "能不能做"       │     │ "做得好不好"     │
└─────────────────┘     └─────────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌─────────────────┐
        │  开发者体验审查   │  ← /plan-devex-review（面向开发者产品时）
        │  "开发者爽不爽"   │
        └─────────────────┘
                    │
                    ▼
        ┌─────────────────┐
│  全部通过后 /ship  │  ← /ship 发布
└─────────────────┘
```

**快速决策：**
| 你想问的问题 | 用哪个 |
|---|---|
| "这个架构合理吗？" | `/plan-eng-review` |
| "这个设计能打几分？" | `/plan-design-review` |
| "开发者用这个会爽吗？" | `/plan-devex-review` |
| "全都审查一遍" | `/autoplan`（自动跑完全部）|

---

### `/design-consultation` — 设计系统咨询
**核心问题：我的产品应该长什么样？用什么颜色、字体、间距？**

**功能：** 从零建立完整的设计系统。理解产品定位 → 研究竞品风格 → 提出设计方向（美学/字体/颜色/布局/间距/动效）→ 生成字体+颜色预览页 → 创建 DESIGN.md。

**使用时机：**
- "design system" / "create a brand"
- 新项目从零开始需要设计系统
- 现有项目设计混乱，想统一规范
- 品牌升级/改版

**不适合：**
- 已经有设计系统，只是改某个页面（用 `/design-shotgun` 或 `/design-review`）
- 设计系统已确定，要生成具体页面的代码（用 `/design-html`）

---

### `/design-shotgun` — 设计 shotgun（多方案探索）
**核心问题：我想看看不同风格的效果，选最好的那个**

**功能：** 生成多个 AI 设计变体 → 打开对比看板并排展示 → 收集你的结构化反馈 → 迭代优化直到满意。

**使用时机：**
- "explore designs" / "show me options"
- "design variants" / "visual brainstorm"
- "I don't like how this looks"
- 不确定设计方向，想快速看多种可能性
- A/B 测试前的设计方向探索

**不适合：**
- 还没有任何设计概念（先用 `/design-consultation` 确定方向）
- 已有明确设计系统，只需按规范实现（用 `/design-html`）
- 审查已实现的页面质量（用 `/design-review`）

---

### `/design-review` — 设计 QA（实时网站）
**核心问题：我的页面实现后有没有视觉问题？**

**功能：** 通过无头浏览器访问实际网页，发现视觉不一致、间距问题、层级问题、AI slop 模式、慢交互，然后在源代码中迭代修复，每次修复原子提交并重新截图验证。

> ⚠️ **需要提供网页 URL，不是代码文件。** `/design-review` 通过 `/browse` 访问页面截图分析，只有浏览器渲染后的结果才能暴露真实视觉问题。

**三种使用方式：**

| 方式 | 场景 | 示例 |
|---|---|---|
| **直接提供 URL** | 最常用 | `/design-review https://myapp.com` |
| **Feature branch 自动模式** | 不填 URL，自动检测 | `/design-review` → 自动进入 diff-aware mode |
| **Main/master 询问模式** | 不填 URL，会主动问你 | `/design-review` → "请提供要审查的 URL" |

**参数说明：**

| 参数 | 默认 | 示例 |
|---|---|---|
| `Target URL` | 自动检测或询问 | `https://myapp.com`, `http://localhost:9966` |
| `Scope` | 全站 | `Focus on the settings page` |
| `Depth` | 标准（5-8 页）| `--quick`（首页+2 页）/ `--deep`（10-15 页）|
| `Auth` | 无 | 需登录时先 `/setup-browser-cookies` |

**Feature branch diff-aware mode：**
- 自动检测本地开发服务器（如 `http://localhost:9966`）
- 对比当前 branch 与 base branch 的改动范围
- 重点审查修改过的页面，不浪费时间在无关页面

**使用示例：**
```bash
/design-review https://dev-login.hgj.com           # 审查线上站点
/design-review http://localhost:9966                 # 审查本地开发服务器
/design-review http://localhost:9966 --quick         # 快速模式，只查首页+2页
/design-review http://localhost:9966 "Focus on chat" # 限定范围
```

**使用时机：**
- "visual design audit" / "design QA"
- "fix design issues"
- 开发完成后上线前的视觉验收
- 发现页面"看起来不对"但说不清哪里不对

**不适合：**
- 还没有代码实现，只有设计稿（用 `/plan-design-review`）
- 想从零建立设计系统（用 `/design-consultation`）
- 想探索多种设计风格（用 `/design-shotgun`）

---

### `/design-html` — 设计实现（HTML/CSS）
**核心问题：我有设计稿了，怎么把它变成代码？**

**功能：** 将设计转化为生产级 HTML/CSS。读取设计输入（`/design-shotgun` 的 mockup、`/plan-design-review` 的结果、或你提供的设计稿）→ 生成语义化、可维护、响应式的前端代码 → 与设计系统对齐。

**使用时机：**
- "build the design" / "code the mockup"
- "make design real"
- 设计确定后，需要前端代码实现
- 快速原型开发

**不适合：**
- 还没有设计稿（先用 `/design-consultation` 或 `/design-shotgun`）
- 想审查代码实现的质量（用 `/design-review`）
- 已有代码，要调整细节（直接 Edit 代码即可）

---

### 设计流水线流程

```
项目启动
    │
    ▼
┌─────────────────────┐
│ /design-consultation │  ← 建立设计系统（颜色/字体/间距/动效）
│ "我的产品应该长什么样" │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  /design-shotgun     │  ← 探索多个视觉方案，选最好的
│ "看看不同风格的效果"  │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│   /design-html       │  ← 把选定的设计变成 HTML/CSS
│   "设计稿转代码"      │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│   /design-review     │  ← 检查实现后的页面质量
│   "有没有视觉问题"    │
└─────────────────────┘
    │
    ▼
    ✅ 上线
```

**设计类 Skill 快速决策：**

| 你想做的事 | 用哪个 |
|---|---|
| "从零设计一套 UI 规范" | `/design-consultation` |
| "给我几个不同的设计看看" | `/design-shotgun` |
| "检查页面有没有视觉 bug" | `/design-review` |
| "把设计稿写成 HTML/CSS" | `/design-html` |
| "设计稿能打几分" | `/plan-design-review`（计划阶段）|

---

### `/devex-review` — 实时开发者体验审计
**功能：** 实际测试开发者体验：导航文档、尝试入门流程、计时 TTHW、截图错误信息、评估 CLI 帮助文本。产出 DX 评分卡。

**使用时机：**
- "live DX audit" / "test developer experience"
- "measure onboarding time"

---

## 八、项目规划与上下文

### `/context-save` — 保存工作上下文
**功能：** 捕获 git 状态、已做决策、剩余工作，使未来任何会话都能无缝接续。

**使用时机：**
- "save progress" / "save state"
- "save my work" / 长时间工作前保存
- 与 `/context-restore` 配对使用

---

### `/context-restore` — 恢复工作上下文
**功能：** 加载 `/context-save` 保存的状态，接续之前的工作。跨 Conductor workspace 交接可用。

**使用时机：**
- "resume" / "restore context"
- "where was I" / "pick up where I left off"

---

### `/learn` — 管理项目学习记录
**功能：** 查看、搜索、修剪、导出 gstack 跨会话积累的学习记录。

**使用时机：**
- "what have we learned" / "show learnings"
- "prune stale learnings" / "export learnings"

---

### `/retro` — 工程周报回顾
**功能：** 分析提交历史、工作模式、代码质量指标，持久化历史和趋势追踪。团队感知：按人分解贡献，表扬和成长建议。

**使用时机：**
- "weekly retro" / "what did we ship"
- "engineering retrospective"
- 每周/每两周团队回顾

---

### `/landing-report` — 发布队列仪表板
**功能：** 只读的 VERSION 槽位占用情况，显示哪些 PR 占用了版本号、哪些 workspace 即将发布、下一个可用槽位。

**使用时机：**
- "landing report" / "version queue"
- "what version comes next"
- "show open PR versions"

---

### `/make-pdf` — Markdown 转 PDF
**功能：** 将任何 markdown 文件转为出版级 PDF：1 英寸边距、智能分页、页码、封面、页眉、弯引号、可点击目录、对角线 DRAFT 水印。

**使用时机：**
- "make a PDF" / "export to PDF"
- "generate PDF"

---

### `/health` — 代码质量仪表板
**功能：** 包装现有项目工具（类型检查、linter、测试运行器、死代码检测、shell linter），计算 0-10 加权综合评分，追踪趋势。

**使用时机：**
- "code health check" / "quality dashboard"
- "how healthy is codebase"
- "run all checks"

---

## 九、配置与工具

### `/setup-gbrain` — 配置 gbrain
**功能：** 安装 gbrain CLI、初始化本地 PGLite 或 Supabase brain、注册 MCP、捕获信任策略。从零到可用的一条命令。

**使用时机：**
- "setup gbrain" / "install gbrain"
- "connect gbrain" / "start gbrain"

---

### `/sync-gbrain` — 同步 gbrain
**功能：** 保持 gbrain 与当前仓库代码同步，刷新 CLAUDE.md 中的搜索指导。可重复运行，幂等。

**使用时机：**
- "sync gbrain" / "refresh gbrain"
- "reindex repo" / "update gbrain"

---

### `/gstack-upgrade` — 升级 gstack
**功能：** 检测全局安装 vs vendored 安装，运行升级，展示更新内容。

**使用时机：**
- "upgrade gstack" / "update gstack version"
- "get latest gstack"

---

### `/plan-tune` — 调整提问策略
**功能：** 审查 gstack skill 中哪些 AskUserQuestion 会触发，设置每个问题的偏好（永不询问 / 总是询问 / 仅单向询问），查看开发者画像。

**使用时机：**
- "tune questions" / "stop asking me that"
- "too many questions" / "show my profile"
- "developer profile" / "show my vibe"

---

## 十、其他独立 Skill（非 gstack 包）

以下 skill 也在 `.claude/skills/` 中可用，但来自其他包：

| Skill | 功能 | 使用时机 |
|---|---|---|
| `/frontend-dev` | 前端开发指导 | 前端架构、组件设计 |
| `/fullstack-dev` | 全栈开发指导 | 端到端功能实现 |
| `/android-native-dev` | Android 原生开发 | Android 项目 |
| `/ios-application-dev` | iOS 应用开发 | iOS 项目 |
| `/company-research` | 公司研究 | 竞品分析、市场调研 |
| `/tavily-search` | Tavily 搜索 | 深度网络研究 |
| `/tavily-research` | Tavily 研究 | 系统性调研 |
| `/user-story` | 用户故事编写 | 需求梳理 |
| `/roadmap-planning` | 路线图规划 | 产品规划 |
| `/brainstorming` | 头脑风暴 | 创意发散 |
| `/press-release` | 新闻稿撰写 | 产品发布 |
| `/storyboard` | 故事板 | 用户流程设计 |

---

## 附：gstack 官方 Skill 路由规则

建议在项目 `CLAUDE.md` 中添加以下内容，让 gstack 自动路由：

```markdown
## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
```

---

*文档生成时间：2026/06/02*  
*gstack 路径：`~/.claude/skills/gstack/`*
