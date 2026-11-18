# baoyu Skills 速查表

> 本文档汇总 baoyu-skills 插件包中所有可用的 skill，按实际使用场景分类，方便在内容创作、社媒运营、开发调试等场景中快速查找。
> 
> 实际安装路径：`C:\Users\weilan\.claude\plugins\cache\baoyu-skills\baoyu-skills\441ca307a60c`
> 调用前缀：`baoyu-skills:`（例如 `baoyu-skills:baoyu-translate`）

---

## 快速索引（按场景）

| 场景 | 推荐 Skill | 备注 |
|---|---|---|
| 🎨 通用图片生成 | `baoyu-image-gen` | 多后端统一入口，文生图、参考图、批量生成 |
| 🖼️ 文章封面 | `baoyu-cover-image` | 5 维度生成封面，支持 16:9 / 2.35:1 / 1:1 等比例 |
| 📰 文章配图 | `baoyu-article-illustrator` | 自动分析文章，识别插图位置并生成 |
| 📊 信息图 | `baoyu-infographic` | 21 布局 × 22 风格，高密度信息可视化 |
| 🗯️ 知识漫画 | `baoyu-comic` | 教育/传记/教程漫画，可导出 PDF |
| 📐 技术图表 | `baoyu-diagram` | SVG 架构图、流程图、时序图、思维导图等 |
| 📑 PPT/幻灯片 | `baoyu-slide-deck` | 生成幻灯片图片，可合并为 PPTX/PDF |
| 🃏 社媒图片卡片 | `baoyu-xhs-images` | 小红书/小绿书/微信图文，1-10 张卡片 |
| 📝 Markdown 格式化 | `baoyu-format-markdown` | 自动加标题、摘要、加粗、列表、代码块 |
| 🌐 Markdown 转 HTML | `baoyu-markdown-to-html` | 微信主题兼容，支持 Mermaid/PlantUML |
| 🌍 翻译 | `baoyu-translate` | 快翻 / 普通 / 精翻三模式，支持术语表 |
| 🔗 URL 转 Markdown | `baoyu-url-to-markdown` | 抓取任意网页为 Markdown，支持 X/YouTube/HN |
| 🐦 X 转 Markdown | `baoyu-danger-x-to-markdown` | 推文/线程/X Articles 转 Markdown |
| ▶️ YouTube 字幕 | `baoyu-youtube-transcript` | 下载字幕、翻译、章节、封面图 |
| 🗜️ 图片压缩 | `baoyu-compress-image` | 转 WebP/PNG，支持批量和目录递归 |
| 💬 发布微信公众号 | `baoyu-post-to-wechat` | 文章/贴图，支持 API / 浏览器 / 远程 API |
| 📢 发布微博 | `baoyu-post-to-weibo` | 普通微博/头条文章，浏览器自动化 |
| 🐦 发布 X | `baoyu-post-to-x` | 推文/X Articles，支持 Codex Chrome 插件 |
| 🔧 Electron 源码提取 | `baoyu-electron-extract` | 解包 app.asar，还原 source map |
| 🤖 Gemini Web 客户端 | `baoyu-danger-gemini-web` | 文本/图片生成，多轮对话（需同意反编译 API） |
| 👥 微信群聊摘要 | `baoyu-wechat-summary` | 基于 wx-cli 提取群聊精华，支持毒舌版 |

---

## 一、视觉内容生成

### `baoyu-image-gen` — 通用 AI 图片生成

**功能：** 官方 API 驱动的图片生成统一入口。支持 OpenAI GPT Image 2、Azure OpenAI、Google、OpenRouter、DashScope（通义万象）、Z.AI（智谱）、MiniMax、Jimeng（即梦）、Seedream（豆包）、Replicate、Agnes 等十余个后端。

**使用时机：**
- "生成图片" / "画一张图" / "文生图"
- 需要指定具体模型或后端时
- 批量生成场景（配合 `--batchfile`）
- 其他 baoyu 图片类 skill 的后端兜底

**特点：**
- 支持参考图（`--ref`）、多比例（`--ar`）、质量档位（`--quality`）
- 可调用 Codex CLI 作为 provider（`--provider codex-cli`）
- 默认 sequential，批量任务自动并行

---

### `baoyu-cover-image` — 文章封面生成

**功能：** 为文章生成专业封面图。从 Type（hero/conceptual/typography/metaphor/scene/minimal）、Palette（11 种配色）、Rendering（7 种渲染风格）、Text（4 级文字）、Mood、Font 六个维度组合生成。

**使用时机：**
- "生成封面" / "文章封面" / "make cover"
- 公众号、博客、报告封面
- 需要与文章主题风格一致的视觉头图

**特点：**
- 默认比例 16:9，支持 2.35:1、4:3、1:1 等
- `--quick` 可跳过确认直接生成
- 自动生成 prompt 文件并保存到 `cover-image/{topic-slug}/`

---

### `baoyu-article-illustrator` — 文章配图

**功能：** 分析文章结构，自动识别需要视觉辅助的位置，按 Type × Style × Palette 三维度为文章生成系列插图，并自动插入 Markdown 引用。

**使用时机：**
- "为文章配图" / "illustrate article" / "add images"
- 长文需要可视化增强可读性
- 教程/科普/方法论文章

**特点：**
- 先分析、出 outline、再批量生成
- 支持 infographic / scene / flowchart / comparison / framework / timeline 等类型
- 输出目录可配置（`imgs-subdir` / `same-dir` / `independent`）

---

### `baoyu-infographic` — 信息图生成

**功能：** 将内容转为出版级信息图。提供 21 种布局（bento-grid、linear-progression、funnel、hub-spoke、iceberg 等）和 22 种视觉风格（craft-handmade、cyberpunk-neon、corporate-memphis、chalkboard 等）。

**使用时机：**
- "信息图" / "infographic" / "visual summary"
- 高密度知识总结、流程说明、对比分析
- 社交媒体长图、一图读懂

**特点：**
- 先分析内容 → 结构化 → 推荐布局×风格组合 → 确认后生成
- 忠实保留源数据，不擅自总结
- 默认 `bento-grid + craft-handmade`

---

### `baoyu-comic` — 知识漫画

**功能：** 创建原创教育/知识漫画。支持 6 种艺术风格（ligne-claire、manga、realistic、ink-brush、chalk、minimalist）和 7 种色调，最终合并为 PDF。

**使用时机：**
- "知识漫画" / "教育漫画" / "tutorial comic"
- 传记漫画、科普漫画
- 需要叙事性视觉内容

**特点：**
- 生成 storyboard、角色表、分镜 prompt、逐页图片
- 多页漫画自动生成角色一致性参考图
- 支持 `--storyboard-only` / `--prompts-only` 等部分流程

---

### `baoyu-diagram` — SVG 图表生成

**功能：** 生成专业暗色主题 SVG 图表。支持架构图、流程图、时序图、结构图（类图/ER图/组织架构）、思维导图、时间线、状态机、数据流图、概念说明图等。

**使用时机：**
- "画个图" / "架构图" / "流程图" / "时序图"
- 技术文档配图
- 系统/流程/关系可视化

**特点：**
- 输出独立 `.svg` 文件，内嵌样式和字体
- 自动生成对应 `@2x.png`
- 暗色主题，语义化配色

---

## 二、演示与幻灯片

### `baoyu-slide-deck` — PPT/幻灯片生成

**功能：** 将内容转为幻灯片图片，最终合并为 PPTX/PDF。预设 17 种风格（blueprint、corporate、chalkboard、notion、bold-editorial 等），面向阅读与分享而非现场演讲。

**使用时机：**
- "做 PPT" / "生成幻灯片" / "slide deck"
- 内容总结、知识分享、报告
- 需要社媒友好、可滚动阅读的幻灯片

**特点：**
- 自动生成 outline、prompts、单页图片
- 支持 `--outline-only` / `--prompts-only` / `--images-only`
- 单页修改：改 prompt → `--regenerate N` → 重新合并

---

## 三、社媒图片卡片

### `baoyu-xhs-images` — 小红书/小绿书/微信图文卡片

**功能：** 将内容拆解为 1-10 张适合社交媒体传播的图片卡片。12 种风格 × 8 种布局 × 3 种配色，支持故事驱动、信息密集、视觉优先三种策略。

**使用时机：**
- "小红书图片" / "小绿书" / "微信图文" / "image cards"
- 种草、知识卡、清单、测评、教程
- 需要系列化社媒素材

**特点：**
- 自动生成封面 + 内容页 + 结尾页
- image-1 作为 anchor 引用，保证系列风格一致
- 提供 30+ 预设（`knowledge-card`、`cute-share`、`warning` 等）

---

## 四、内容处理与转换

### `baoyu-format-markdown` — Markdown 格式化

**功能：** 将纯文本或 Markdown 整理为结构清晰、易读的 Markdown。自动添加 frontmatter、标题、摘要、加粗、列表、代码块、表格等，但不增删改写原内容。

**使用时机：**
- "格式化 Markdown" / "美化文章" / "整理排版"
- 从网页粘贴的原始文本需要结构化
- 给文章加标题、摘要、重点加粗

**特点：**
- 输出 `{filename}-formatted.md`
- 运行 CJK 间距、 emphasis 修复等排版脚本
- 提供标题候选供用户选择

---

### `baoyu-markdown-to-html` — Markdown 转 HTML

**功能：** 将 Markdown 转为带内联 CSS 的美观 HTML，针对微信公众号优化。支持代码高亮、数学公式、Mermaid（渲染为 PNG）、PlantUML、脚注、alert、信息图、底部引用。

**使用时机：**
- "md 转 html" / "微信外链转底部引用"
- 准备公众号文章 HTML
- 需要离线可读的样式化 HTML

**特点：**
- 4 套主题：default、grace、simple、modern
- `--cite` 将普通外链转为文末引用（适合微信）
- Mermaid 通过 headless Chrome 渲染为本地 PNG

---

### `baoyu-translate` — 翻译

**功能：** 三模式翻译：quick（直接翻译）、normal（分析后翻译）、refined（出版级：分析 → 翻译 → 审校 → 润色）。支持自定义术语表、受众、风格。

**使用时机：**
- "翻译" / "translate" / "精翻" / "本地化"
- 翻译文章、文档、字幕
- 需要术语一致性的长文

**特点：**
- 长文自动分块，用 subagent 并行翻译保证一致性
- 支持翻译后提醒图片文字是否需要本地化
- 完成normal后可回复 "继续润色" / "refine" 进入 refined 后段

---

### `baoyu-url-to-markdown` — URL 转 Markdown

**功能：** 使用 Chrome CDP + 站点适配器抓取任意 URL 转为 Markdown。内置 X/Twitter、YouTube 字幕、Hacker News、通用网页适配器。支持登录/CAPTCHA 交互等待。

**使用时机：**
- "保存网页" / "URL 转 Markdown" / "网页抓取"
- 备份文章、整理资料
- 需要处理需要登录的页面

**特点：**
- 支持 `--download-media` 下载图片视频
- `--wait-for interaction` 处理登录/CAPTCHA
- 默认输出到 `./url-to-markdown/{domain}/{slug}/`

---

### `baoyu-danger-x-to-markdown` — X/Twitter 转 Markdown

**功能：** 将 X（Twitter）推文、线程、X Articles 转为带 YAML front matter 的 Markdown。使用反向工程 API，首次使用需用户同意。

**使用时机：**
- "X to markdown" / "tweet to markdown" / "保存推文"
- 备份推文线程、引用推文内容
- 整理 X Articles 长文

**特点：**
- 支持下载媒体到本地 `imgs/` / `videos/`
- 首次使用有同意流程
- 支持 `X_AUTH_TOKEN`、`X_CT0` 或 Chrome 登录

---

### `baoyu-youtube-transcript` — YouTube 字幕与封面

**功能：** 下载 YouTube 字幕/字幕、封面图、元数据。支持多语言、翻译、章节分段、说话人识别。无需 API Key，优先使用 YouTube InnerTube API，失败时回退 yt-dlp。

**使用时机：**
- "YouTube 字幕" / "下载字幕" / "视频封面"
- 转录视频、翻译字幕
- 获取视频章节结构

**特点：**
- 自动缓存，重复格式转换不重新下载
- 输出 `transcript.md` / `transcript.srt`
- `--speakers` 模式需要 AI 后处理说话人识别

---

### `baoyu-compress-image` — 图片压缩

**功能：** 将图片压缩为 WebP（默认）或 PNG。自动选择最佳工具（sips → cwebp → ImageMagick → Sharp），支持单文件、目录、递归处理。

**使用时机：**
- "压缩图片" / "转 webp" / "optimize image"
- 批量压缩素材、减小图片体积
- 发布前图片预处理

**特点：**
- 默认 quality 80
- 支持 `--keep` 保留原图、`--recursive` 递归目录
- JSON 输出便于脚本集成

---

## 五、社交媒体发布

### `baoyu-post-to-wechat` — 发布微信公众号

**功能：** 将 Markdown/HTML/纯文本发布到微信公众号。支持文章（长文）和贴图/图文（1-9 张图）。提供 API、浏览器、远程 API 三种发布方式。

**使用时机：**
- "发布公众号" / "微信公众号" / "贴图"
- 文章排版后一键发布
- 需要远程服务器 IP 白名单时

**特点：**
- Markdown 默认将外链转为底部引用（微信友好）
- 支持多账号、主题、颜色、评论控制
- 远程 API 模式通过 SSH SOCKS5 隧道解决 IP 白名单问题

---

### `baoyu-post-to-weibo` — 发布微博

**功能：** 通过真实 Chrome 浏览器发布微博。支持普通微博（文字+图片/视频，最多 18 个文件）和头条文章（Markdown 长文）。

**使用时机：**
- "发微博" / "发布微博" / "微博头条文章"
- 内容同步到微博
- 需要绕过反爬的浏览器自动化

**特点：**
- 脚本自动填充内容，用户手动确认发布
- 头条文章标题限 32 字，导语限 44 字
- 首次登录后 session 持久化

---

### `baoyu-post-to-x` — 发布 X/Twitter

**功能：** 发布推文、视频、引用推文和 X Articles 长文。在 Codex 中优先使用 Codex Chrome 插件，其次 Chrome Computer Use，最后 CDP 脚本。

**使用时机：**
- "post to X" / "tweet" / "publish to Twitter"
- 同步内容到 X
- 发布 X Articles 长文

**特点：**
- Markdown 文件默认转为 X Article
- 支持 Chrome 插件、Computer Use、CDP 三种模式
- 不自动点击发布，需要用户最终确认

---

## 六、开发者工具

### `baoyu-electron-extract` — Electron 应用源码提取

**功能：** 解包已安装 Electron 应用的 `app.asar`。如有 `.js.map` 则还原原始源码；否则用 Prettier 格式化压缩代码。跳过 `node_modules`，支持 macOS 和 Windows。

**使用时机：**
- "提取 Electron 应用" / "看源码" / "反编译 Electron"
- 研究 Codex、Cursor、Discord、Slack、Notion 等桌面应用
- 分析 Electron 应用打包结构

**特点：**
- 支持 app 名称或绝对路径
- `--dry-run` 预览发现结果
- 输出 `extracted/`、`restored/`、`extract-report.json`

---

### `baoyu-danger-gemini-web` — Gemini Web 客户端

**功能：** 通过反向工程 Gemini Web API 进行文本生成、图片生成、参考图视觉输入、多轮对话。首次使用需用户同意。

**使用时机：**
- "Gemini 图片生成" / "Gemini 文本生成"
- 需要 vision-capable 的免费/低成本生成后端
- 其他 skill 需要 Gemini 作为图片生成后端时

**特点：**
- 支持 gemini-3-pro / flash / flash-thinking / 3.1-pro-preview
- 首次使用浏览器登录 Google，cookie 自动缓存
- 支持 `--reference` 参考图和 `--sessionId` 多轮对话

---

## 七、社群运营

### `baoyu-wechat-summary` — 微信群聊精华摘要

**功能：** 使用本地 `wx-cli` 读取微信群聊记录，提炼为结构化摘要。默认生成正常版，可选毒舌版（roast）。维护群历史、群友画像、群级事实记忆。

**使用时机：**
- "总结群聊" / "群聊精华" / "帮我看看 XX 群最近聊了什么"
- 活跃群聊的信息降噪与归档
- 定期生成群聊日报/周报

**特点：**
- 基于 wx-cli，需要 WeChat 运行并登录
- 支持增量模式（"从上次开始"）
- 自动更新群友 profiles 和群记忆 `memory.md`
- 毒舌版通过 "毒舌版" / "roast" 等关键词触发

---

## 附：内容创作工作流参考

### 文章从 0 到发布（微信公众号为例）

```
素材/草稿
    │
    ▼
┌─────────────────────┐
│ baoyu-translate      │  ← 外文素材先翻译（可选）
│ 翻译/精翻            │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ baoyu-format-markdown│  ← 整理结构、标题、摘要
│ Markdown 格式化      │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐     ┌─────────────────────┐
│ baoyu-cover-image    │  +  │ baoyu-article-illustrator│
│ 生成封面             │     │ 文章配图             │
└─────────────────────┘     └─────────────────────┘
    │                       │
    └───────────┬───────────┘
                ▼
┌─────────────────────┐
│ baoyu-markdown-to-html│  ← 转换为微信友好 HTML
│ md 转 html          │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ baoyu-post-to-wechat │  ← 发布到公众号
│ 微信公众号发布       │
└─────────────────────┘
```

### 社媒多平台分发

```
原始内容
    │
    ├───→ baoyu-xhs-images ──→ 小红书/小绿书/微信图文
    │
    ├───→ baoyu-infographic ──→ 一图读懂/信息图长图
    │
    ├───→ baoyu-slide-deck ──→ PPT/PDF（适合微博/LinkedIn/即刻）
    │
    ├───→ baoyu-post-to-weibo ──→ 微博头条文章
    │
    └───→ baoyu-post-to-x ──→ X/Twitter / X Articles
```

### 快速决策

| 你想做的事 | 用哪个 Skill |
|---|---|
| 画一张通用 AI 图 | `baoyu-image-gen` |
| 给文章做封面 | `baoyu-cover-image` |
| 给长文自动配图 | `baoyu-article-illustrator` |
| 做一图读懂/信息图 | `baoyu-infographic` |
| 做知识漫画 | `baoyu-comic` |
| 画架构图/流程图 | `baoyu-diagram` |
| 做 PPT | `baoyu-slide-deck` |
| 做小红书/小绿书卡片 | `baoyu-xhs-images` |
| 翻译文章 | `baoyu-translate` |
| 整理/格式化 Markdown | `baoyu-format-markdown` |
| 转微信公众号 HTML | `baoyu-markdown-to-html` |
| 保存网页为 Markdown | `baoyu-url-to-markdown` |
| 保存推文 | `baoyu-danger-x-to-markdown` |
| 下载 YouTube 字幕 | `baoyu-youtube-transcript` |
| 压缩图片 | `baoyu-compress-image` |
| 发微信公众号 | `baoyu-post-to-wechat` |
| 发微博 | `baoyu-post-to-weibo` |
| 发 X | `baoyu-post-to-x` |
| 提取 Electron 应用源码 | `baoyu-electron-extract` |
| 用 Gemini Web 生成 | `baoyu-danger-gemini-web` |
| 总结微信群聊 | `baoyu-wechat-summary` |

---

*文档生成时间：2026/06/14*  
*baoyu-skills 安装路径：`C:\Users\weilan\.claude\plugins\cache\baoyu-skills\baoyu-skills\441ca307a60c`*
