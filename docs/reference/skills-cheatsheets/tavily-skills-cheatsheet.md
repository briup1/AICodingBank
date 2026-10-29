# Tavily Skills 速查表

> 生成于 2026/06/02 | 覆盖 8 个 tavily 相关 skill
> Tavily 是一个为 LLM 设计的搜索 API，提供实时网络数据访问能力。

---

## 快速索引（按场景）

| 场景 | 推荐 Skill | 备注 |
|---|---|---|
| 🔎 快速网页搜索 | `/tavily-search` |
| 🧹 搜索并过滤 | `/tavily-dynamic-search` | Python 沙箱压缩上下文 |
| 📄 提取 URL 内容 | `/tavily-extract` |
| 🗺️ 发现网站页面 | `/tavily-map` |
| 🕷️ 批量爬取站点 | `/tavily-crawl` |
| 📚 深度研究报告 | `/tavily-research` |
| 🔧 SDK 集成参考 | `/tavily-best-practices` |
| 📖 CLI 总入口 | `/tavily-cli` |

---

## 目录

- [一、核心搜索技能](#一核心搜索技能)
- [二、内容提取技能](#二内容提取技能)
- [三、高级/深度技能](#三高级深度技能)
- [四、集成与最佳实践](#四集成与最佳实践)
- [五、技能对比与决策](#五技能对比与决策)
- [六、安装与认证](#六安装与认证)
- [七、工作流程与升级路径](#七工作流程与升级路径)

---

## 一、核心搜索技能

### `/tavily-search` — 快速网页搜索
**核心问题：我想在网上找某个主题的信息**

**功能：** 搜索网页，返回 LLM 优化的结果（含内容摘要、相关度分数、元数据）。支持域名过滤、时间范围、搜索深度控制。无需特定 URL。

**使用时机：**
- "search for" / "find me" / "look up" / "what's the latest on"
- 没有具体 URL，需要发现信息源
- 快速事实查找（vs 深度研究用 `/tavily-research`）

**常用选项：**

| 选项 | 说明 | 示例 |
|---|---|---|
| `--depth` | 搜索深度：`ultra-fast`/`fast`/`basic`/`advanced` | `--depth advanced` |
| `--max-results` | 结果数量 0-20 | `--max-results 10` |
| `--topic` | 主题：`general`/`news`/`finance` | `--topic news` |
| `--time-range` | 时间：`day`/`week`/`month`/`year` | `--time-range week` |
| `--include-domains` | 限定域名 | `--include-domains sec.gov` |
| `--include-raw-content` | 包含完整页面内容 | `--include-raw-content --max-results 3` |

**示例：**
```bash
tvly search "AI code assistants 2025" --depth advanced --max-results 10 --json
tvly search "SEC filings" --include-domains sec.gov --time-range month --json
```

**不适合：**
- 有具体 URL 要提取内容（用 `/tavily-extract`）
- 需要处理大量搜索结果并过滤（用 `/tavily-dynamic-search`）

---

### `/tavily-dynamic-search` — 编程式搜索（上下文隔离）
**核心问题：我要搜索，但不想让原始 HTML 垃圾污染我的上下文**

**功能：** 在 Python 沙箱中执行搜索，只让过滤后的 `print()` 输出进入上下文窗口。典型的 `--include-raw-content` 返回 ~300K 字符的原始 HTML，通过 Python 过滤后只保留 1-3K 纯净信号 —— **100-200x 上下文压缩**。

> 核心规则：**绝不裸跑 `tvly`**。总是通过 Python 处理输出。

**使用时机：**
- 任何需要网络研究但上下文有限的情况
- "search and filter" / "find the important parts" / "extract the key details"
- 默认的 web research skill（当触发词是 "search for", "look up", "find", "research" 时）

**为什么重要：**
```bash
# ❌ WRONG — 原始结果淹没上下文
tvly search "quantum computing 2025" --json

# ✅ RIGHT — 只有 print() 输出进入上下文
tvly search "quantum computing 2025" --json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data['results']:
    print(f'[{r[\"score\"]:.2f}] {r[\"title\"]}')
    print(f'  {r[\"url\"]}')
"
```

**使用工具：** Bash(tvly *), Bash(python3 *), Bash(uv run *), Bash(jq *)

**不适合：**
- 单次简单搜索，不需要过滤（用 `/tavily-search`）
- 有具体 URL 要提取内容（用 `/tavily-extract`）

---

## 二、内容提取技能

### `/tavily-extract` — 单 URL 内容提取
**核心问题：我有一个 URL，想要它的干净内容**

**功能：** 从 1-20 个 URL 提取干净的 markdown/text。支持 JavaScript 渲染页面、query-focused chunking（按查询提取相关段落）。

**使用时机：**
- "extract" / "grab the content from" / "pull the text from" / "get the page at"
- 有具体 URL，需要其内容（而非搜索结果）
- 从 JS 渲染页面提取内容

**常用选项：**

| 选项 | 说明 | 示例 |
|---|---|---|
| `--query` | 按查询相关性重新排序块 | `--query "authentication API"` |
| `--chunks-per-source` | 每 URL 返回的块数 1-5 | `--chunks-per-source 3` |
| `--extract-depth` | `basic`（默认）或 `advanced`（JS 页面）| `--extract-depth advanced` |
| `--format` | `markdown`（默认）或 `text` | `--format text` |
| `--include-images` | 包含图片 URL | `--include-images` |
| `-o` | 保存到文件 | `-o article.md` |

**示例：**
```bash
tvly extract "https://example.com/article" --json
tvly extract "https://example.com/docs" --query "authentication API" --chunks-per-source 3 --json
tvly extract "https://app.example.com" --extract-depth advanced --json
```

**不适合：**
- 还没有 URL，需要先搜索（用 `/tavily-search`）
- 需要整站内容（用 `/tavily-crawl`）

---

### `/tavily-map` — 网站 URL 发现
**核心问题：我知道有这个网站，但不知道具体页面在哪**

**功能：** 发现网站所有 URL，**不提取内容**。比爬取更快，只返回 URL 列表。适合先了解站点结构，再决定提取哪些页面。

**使用时机：**
- "map the site" / "find the URL for" / "what pages are on" / "list all pages"
- 在大网站上找特定子页面
- 爬取前先了解站点结构

**常用选项：**

| 选项 | 说明 | 示例 |
|---|---|---|
| `--max-depth` | 深度 1-5 | `--max-depth 3` |
| `--max-breadth` | 每页链接数 | `--max-breadth 20` |
| `--limit` | 最大 URL 数 | `--limit 200` |
| `--instructions` | 自然语言过滤 | `--instructions "Find API docs"` |
| `--select-paths` | 正则包含路径 | `--select-paths "/docs/.*"` |
| `--exclude-paths` | 正则排除路径 | `--exclude-paths "/blog/.*"` |
| `--allow-external` | 包含外部链接 | `--allow-external` |

**示例：**
```bash
tvly map "https://docs.example.com" --json
tvly map "https://docs.example.com" --instructions "Find API docs and guides" --json
tvly map "https://example.com" --select-paths "/blog/.*" --limit 500 --json
```

**不适合：**
- 需要页面内容（用 `/tavily-extract` 或 `/tavily-crawl`）
- 已经有具体 URL（用 `/tavily-extract`）

---

## 三、高级/深度技能

### `/tavily-crawl` — 批量爬取
**核心问题：我要整个文档区/站点的内容**

**功能：** 爬取网站多页面，支持保存为本地 markdown 文件。支持深度/广度控制、路径过滤、语义指令（提取相关内容而非全页）。

**使用时机：**
- "crawl" / "get all the pages" / "download the docs"
- "extract everything under /docs"
- 需要整个站点/文档区的离线内容

**常用选项：**

| 选项 | 说明 | 示例 |
|---|---|---|
| `--max-depth` | 深度 1-5 | `--max-depth 2` |
| `--max-breadth` | 每页链接数 | `--max-breadth 20` |
| `--limit` | 总页数上限 | `--limit 50` |
| `--instructions` | 语义聚焦（需 `--chunks-per-source`）| `--instructions "Find auth docs"` |
| `--chunks-per-source` | 每页块数 1-5 | `--chunks-per-source 3` |
| `--select-paths` | 正则包含 | `--select-paths "/api/.*,/guides/.*"` |
| `--exclude-paths` | 正则排除 | `--exclude-paths "/blog/.*"` |
| `--output-dir` | 保存为本地 markdown | `--output-dir ./docs/` |
| `--extract-depth` | `basic` 或 `advanced` | `--extract-depth advanced` |

**示例：**
```bash
tvly crawl "https://docs.example.com" --json
tvly crawl "https://docs.example.com" --output-dir ./docs/
tvly crawl "https://docs.example.com" --max-depth 2 --limit 50 --json
tvly crawl "https://example.com" --select-paths "/api/.*" --exclude-paths "/blog/.*" --json
```

**不适合：**
- 只需要几个具体 URL（用 `/tavily-extract`）
- 只需要 URL 列表（用 `/tavily-map`）

---

### `/tavily-research` — 深度研究
**核心问题：我要一份带引用的深度分析报告**

**功能：** AI 驱动的深度研究。自动收集多源信息、分析、产出带引用的结构化报告。耗时 30-120 秒。

**使用时机：**
- "research" / "investigate" / "analyze in depth" / "compare X vs Y"
- "what does the market look like for"
- 需要多源综合分析和明确引用
- 市场调研、文献综述、竞品对比

**常用选项：**

| 选项 | 说明 | 示例 |
|---|---|---|
| `--model` | `mini`/`pro`/`auto`（默认）| `--model pro` |
| `--stream` | 实时流式输出 | `--stream` |
| `--no-wait` | 异步，立即返回 request_id | `--no-wait` |
| `--citation-format` | `numbered`/`mla`/`apa`/`chicago` | `--citation-format apa` |
| `--timeout` | 最大等待秒数 | `--timeout 600` |
| `-o` | 保存报告到文件 | `-o report.md` |
| `--json` | JSON 输出（供 agent 使用）| `--json` |

**示例：**
```bash
tvly research "competitive landscape of AI code assistants"
tvly research "electric vehicle market analysis" --model pro
tvly research "AI agent frameworks comparison" --stream
tvly research "fintech trends 2025" --model pro -o fintech-report.md
```

**不适合：**
- 快速事实查找（用 `/tavily-search`，更快更轻）
- 有具体 URL 要提取（用 `/tavily-extract`）

---

## 四、集成与最佳实践

### `/tavily-best-practices` — SDK 集成最佳实践
**核心问题：如何在代码中集成 Tavily API？**

**功能：** 生产级 Tavily 集成参考文档。涵盖 Python (`tavily-python`) 和 JavaScript (`@tavily/core`) SDK 的完整用法、初始化、参数说明、RAG 系统集成、agentic workflow 集成。

**使用时机：**
- 在 Python/JS 代码中集成 Tavily
- 构建 RAG 系统、自主 agent、agentic workflows
- 需要 SDK 的完整参数参考

**SDK 选择：**

| 场景 | 方法 |
|---|---|
| Web search | `client.search()` |
| 特定 URL 内容 | `client.extract()` |
| 整站内容 | `client.crawl()` |
| URL 发现 | `client.map()` |
| AI 深度研究 | `client.research()` |

**安装：**
```bash
pip install tavily-python          # Python
npm install @tavily/core           # JavaScript
```

**不适合：**
- CLI 工具使用（用 `/tavily-cli` 或具体子 skill）
- 单次搜索任务（用 `/tavily-search`）

---

### `/tavily-cli` — Tavily CLI 总入口
**核心问题：Tavily 有哪些功能？怎么安装？**

**功能：** Tavily CLI 的总括性 skill。涵盖 search/extract/map/crawl/research 全部命令的安装、认证、基本用法。当不确定用哪个子 skill 时，从此开始。

**安装：**
```bash
curl -fsSL https://cli.tavily.com/install.sh | bash
# 或: uv tool install tavily-cli / pip install tavily-cli
```

**认证：**
```bash
tvly login --api-key tvly-YOUR_KEY
# 或: export TAVILY_API_KEY=tvly-YOUR_KEY
# 或: tvly login  (浏览器 OAuth)
```

**验证：**
```bash
tvly --status
```

**工作流升级路径：**

| 步骤 | 命令 | 场景 |
|---|---|---|
| 1. Search | `tvly search` | 没有 URL，找信息 |
| 2. Extract | `tvly extract` | 有 URL，取内容 |
| 3. Map | `tvly map` | 大网站找页面 |
| 4. Crawl | `tvly crawl` | 批量取整站内容 |
| 5. Research | `tvly research` | 深度研究带引用 |

**不适合：**
- 本地文件操作、git 命令、部署、代码编辑（明确不触发）
- 已明确知道用哪个子命令（用对应的子 skill）

---

## 五、技能对比与决策

### 一句话区分

| Skill | 一句话 | 关键输入 |
|---|---|---|
| `/tavily-search` | **在网上搜某个主题** | 查询词 |
| `/tavily-dynamic-search` | **搜完用 Python 过滤，只留精华** | 查询词 + 过滤逻辑 |
| `/tavily-extract` | **给 URL，返回干净内容** | 1-20 个 URL |
| `/tavily-map` | **列出网站所有页面地址** | 网站域名 |
| `/tavily-crawl` | **批量下载整个文档区** | 网站域名 + 过滤规则 |
| `/tavily-research` | **生成带引用的深度报告** | 研究主题 |
| `/tavily-best-practices` | **代码里怎么集成 Tavily** | SDK 文档 |
| `/tavily-cli` | **Tavily CLI 总览** | 安装/认证/命令参考 |

### 快速决策

| 你想做的事 | 用哪个 |
|---|---|
| "搜索一下某某的最新消息" | `/tavily-search` |
| "帮我研究一下这个领域" | `/tavily-research` |
| "把这个网页的内容抓下来" | `/tavily-extract` |
| "这个网站有哪些页面？" | `/tavily-map` |
| "把整个文档站下载下来" | `/tavily-crawl` |
| "搜索结果太多，帮我过滤重点" | `/tavily-dynamic-search` |
| "怎么在代码里调用 Tavily API" | `/tavily-best-practices` |
| "Tavily CLI 怎么安装/怎么用" | `/tavily-cli` |

---

## 六、安装与认证

### CLI 安装（所有 skill 共用）

```bash
# 方式 1：官方脚本（推荐）
curl -fsSL https://cli.tavily.com/install.sh | bash

# 方式 2：uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install tavily-cli

# 方式 3：pip
pip install tavily-cli
```

### 认证（三选一）

```bash
# 方式 1：命令行直接指定
tvly login --api-key tvly-YOUR_KEY

# 方式 2：环境变量
export TAVILY_API_KEY=tvly-YOUR_KEY

# 方式 3：浏览器 OAuth
tvly login
```

### 验证安装

```bash
tvly --status
# 期望输出：
# tavily v0.1.0
# > Authenticated via OAuth (tvly login)
```

---

## 七、工作流程与升级路径

### CLI 工作流程（由简到繁）

```
没有 URL，先搜索
    │
    ▼
┌─────────────────────┐
│  /tavily-search      │  ← 搜索主题，发现信息源
│  "在网上找相关内容"   │
└─────────────────────┘
    │
    ├── 搜索结果有 URL → 用 /tavily-extract 提取内容
    │
    ├── 知道网站但不知道页面 → 用 /tavily-map 发现 URL
    │
    ├── 需要整站/文档区内容 → 用 /tavily-crawl 批量爬取
    │
    └── 需要深度分析报告 → 用 /tavily-research

每一步都可以切换到 /tavily-dynamic-search
来过滤结果、减少上下文噪音
```

### 开发集成路径

```
在代码中集成 Tavily
    │
    ▼
┌─────────────────────┐
│ /tavily-best-practices│  ← SDK 安装、初始化、方法选择
│ "代码里怎么用"        │
└─────────────────────┘
    │
    ├── 需要搜索 → client.search()
    ├── 需要提取 → client.extract()
    ├── 需要爬取 → client.crawl()
    ├── 需要发现 → client.map()
    └── 需要研究 → client.research()
```

### 上下文隔离决策

```
搜索任务
    │
    ├── 结果少 / 简单搜索 ──────→ /tavily-search（直接输出）
    │
    └── 结果多 / 需要过滤 ──────→ /tavily-dynamic-search（Python 过滤）
              300K chars 原始数据
                    │
                    ▼
              Python 沙箱处理
                    │
                    ▼
              1-3K chars 纯净信号
                    │
                    ▼
              进入上下文窗口
```

---

## 补充：常用参数速查

### 所有命令通用

| 参数 | 说明 | 适用命令 |
|---|---|---|
| `--json` | 结构化 JSON 输出 | 全部 |
| `-o, --output` | 保存到文件 | 全部 |
| `--timeout` | 超时秒数 | search/extract/map/crawl |

### Search 专用

| 参数 | 取值 | 说明 |
|---|---|---|
| `--depth` | `ultra-fast` → `fast` → `basic` → `advanced` | 搜索深度递增 |
| `--max-results` | 0-20 | 结果数量 |
| `--topic` | `general`/`news`/`finance` | 主题分类 |
| `--time-range` | `day`/`week`/`month`/`year` | 时间范围 |

### Extract 专用

| 参数 | 说明 |
|---|---|
| `--query` | 按查询过滤内容块 |
| `--chunks-per-source` | 每 URL 返回的块数（需 `--query`）|
| `--extract-depth` | `basic` 或 `advanced`（JS 页面）|
| `--include-images` | 包含图片 URL |

### Crawl/Map 专用

| 参数 | 说明 | Crawl | Map |
|---|---|---|---|
| `--max-depth` | 深度 1-5 | ✅ | ✅ |
| `--max-breadth` | 每页链接数 | ✅ | ✅ |
| `--limit` | 总量上限 | ✅ | ✅ |
| `--instructions` | 自然语言语义指导 | ✅ | ✅ |
| `--select-paths` | 正则包含路径 | ✅ | ✅ |
| `--exclude-paths` | 正则排除路径 | ✅ | ✅ |
| `--output-dir` | 保存为本地 markdown | ✅ | ❌ |
| `--chunks-per-source` | 每页提取块数 | ✅ | ❌ |

### Research 专用

| 参数 | 说明 |
|---|---|
| `--model` | `mini`/`pro`/`auto` |
| `--stream` | 实时流式输出 |
| `--no-wait` | 异步模式 |
| `--citation-format` | `numbered`/`mla`/`apa`/`chicago` |
| `--poll-interval` | 轮询间隔（默认 10s）|
| `--timeout` | 最大等待（默认 600s）|
