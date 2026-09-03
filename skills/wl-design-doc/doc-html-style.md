# 文档 HTML 生成规范 · S1 编辑出版（暖纸）

wl-req-confirm 和 wl-design-doc 的 HTML 产出统一遵守本文件。生成 HTML 前必读。

## 布局：侧边导航式

- 左栏固定（约 280–300px，`position:sticky`）：依次是 eyebrow（等宽大写文档类型）、衬线标题、frontmatter 元信息 chips、编号章节导航（01/02/…）
- 右栏主区**一次只渲染当前章节**：`SEC xx / NN` 面包屑（带 accent 色小圆点）→ 衬线章节标题 → 副标题 → 内容块 → 底部"上一节 / 下一节"翻页卡
- 导航当前项：accent-soft 底色 + 左侧 2px accent 指示条；hover 变浅底
- 章节切换动画：fade-up，`opacity 0 + translateY(12px) → 0`，500ms `cubic-bezier(.16,1,.3,1)`
- 键盘：`↑` `↓` 翻章节；移动端（<860px）退化为上下堆叠单栏
- 长内容块（链路图、接口契约代码等）默认折叠为 `+ / −` 手风琴，点击展开

## 色板（不可偏离）

```
背景       #F7F6F3（暖纸）
表面/卡片  #FFFFFF
正文       #2F3437（禁用纯黑）
次要文字   #787774
弱化文字   #A8A49C
分隔线     #EAE7E0（只用 1px 发丝线）
强调色     #9F2F2D / 浅底 #FDEBEC
通过       #346538 / #EDF3EC
警告       #956400 / #FBF3DB
信息       #1F6C9F / #E1F3FE
代码块     底 #26221E / 字 #EDE8E0
```

## 字体

- 标题（文档题、章节题）：`'Instrument Serif','Songti SC','SimSun',serif`，`letter-spacing:-.02em`
- 正文/UI：`'Plus Jakarta Sans','PingFang SC','Microsoft YaHei',sans-serif`，`line-height:1.7`
- 代码/元数据/编号：`'JetBrains Mono',ui-monospace,monospace`

## 硬性禁令

- 无渐变、无重阴影（阴影不存在或极低透明度）、无玻璃拟态
- 圆角 ≤ 8px（badge/chip 的 999px pill 除外）
- 无 emoji——状态用文字 badge 或简单符号（✓ / — / +）
- 不用大面积主色铺底；颜色只用于语义和小面积点缀

## 组件约定

| 内容 | 呈现 |
|---|---|
| 键值信息（重定义、最小验证） | `dl` 双列：左 130px 粗体标签，右内容 |
| 用户故事 | 左侧 2px accent 竖线 + 白底条，`As a <b>角色</b>…` 角色/能力/价值加粗 accent 色 |
| Out of Scope | 白底 1px 线框条目，`—` 前缀 |
| 前后对比 | BEFORE / AFTER 双栏卡，AFTER 用 accent 描边 + accent-soft 底 |
| 链路图 / 接口契约 | 深棕代码块，外层包手风琴默认折叠 |
| 审查结论 | 维度名 + 状态 badge（通过/未执行=warn）+ 等宽字体浅底证据块 |
| 表格 | 表头等宽大写小字、#FBFAF7 底；单元格 1px 发丝线 |
| badge / status | pastel 底色 pill，11px 大写宽字距 |

## 工程约束

- 单文件 HTML、零构建；字体走 Google Fonts CDN + 系统回退栈
- Markdown 仍是唯一事实来源：HTML 由脚本/agent 从 md 重新生成，绝不手改 HTML
- 数据模型：frontmatter → meta chips；每个 `## 章节` → 一个导航项 + 一个可切换面板
