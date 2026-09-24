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

## 代码样式隔离

行内代码与块级代码必须分别设置背景和文字颜色。禁止只对全局 `code` 设置浅色背景，却不覆盖 `pre > code`：这会导致深色代码块内部出现浅底浅字。

以下规则适用于普通代码块和折叠代码块；如调整类名，必须保留同等作用范围。


```css
/* 行内代码：浅底深字 */
code {
  background: #F0EEE9;
  color: #2F3437;
  padding: 2px 5px;
  border-radius: 4px;
}

/* 普通代码块与折叠代码块：深底浅字 */
pre,
.codefold pre {
  background: #26221E;
  color: #EDE8E0;
}

/* 清除行内代码背景，并继承代码块的文字颜色和字体 */
pre > code,
.codefold pre > code {
  display: block;
  background: transparent;
  color: inherit;
  padding: 0;
  border-radius: 0;
  font: inherit;
}
```

如引入语法高亮，须另外验证内部 token 的颜色；容器颜色正确不代表所有高亮文字可读。不要用全局 `!important` 掩盖作用范围问题。

## HTML 可读性检查

1. 在浏览器中切换到含代码块的章节，展开折叠代码块后检查，不能只检查默认收起状态。
2. 分别检查行内代码、普通代码块和折叠代码块；产物没有某种形态时记为不适用。
3. 检查 `pre` 与内部 `code` 的浏览器计算样式。内部背景透明时沿祖先找到实际背景；不能只比较两个颜色字符串。使用上述默认样式时，应为深底 `#26221E`、浅字 `#EDE8E0`，内部 `code` 不得残留浅色背景。
4. 如有语法高亮、主题切换或其他样式覆盖，检查实际呈现的文字；代码文字与实际背景对比度至少为 4.5:1。
5. 保存展开代码块的截图作为可读性验证证据。浏览器不可用时标注“视觉验证未执行”，说明原因；静态检查或 HTML 解析成功不能代替浏览器渲染验证。

修复此类问题时应更新生成模板/样式来源并重新生成 HTML，保留 Markdown 为内容事实来源，避免只修一次生成物而下次复发。
