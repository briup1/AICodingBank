---
name: hgj-dev-download
description: 路由本机 Downloads 中的 hgj-dev skills 文档包；按需读取团队规范、TAPD 需求解析、需求分析 HTML、测试联调和中文写作规则。
---

# hgj-dev skills 本机按需包

这是一个本机外部文档包，不是由工作台安装器管理的第三方仓库。源目录固定为：

`/Users/ziyun/Downloads/hgj-dev-skills-docs`

## 何时加载

根据任务命中下面的子能力时，只读取对应的 HTML；不要一次性加载全部文档。

| 子能力 | 读取文件 | 触发场景 |
|---|---|---|
| 团队工程规范 | `hgj-dev-standards.html` | 要写 Java、Vue/Nuxt、接口、数据库结构或数据模型 |
| TAPD 需求解析 | `hgj-tapd-parse.html` | 要解析、补全或更新 TAPD 需求 |
| 需求分析 HTML | `hgj-req-html.html` | 要生成、批注或继续维护需求分析 HTML |
| 测试与联调验证 | `hgj-dev-test.html` | 要写测试、跑联调、做页面/后端验收或 E2E |
| 中文写作：说人话 | `skills/keben-writing-style/SKILL.md` | 要润色、改写、代写中文材料或去 AI 味 |

`keben-writing-style` 的配套参考资料按需读取：

- `skills/keben-writing-style/references/ai-patterns.md`
- `skills/keben-writing-style/references/scenes.md`

## 使用顺序

软件开发任务默认按下面的链路判断，不是每次全加载：

```text
TAPD 粗需求
  -> hgj-tapd-parse
  -> hgj-req-html
  -> hgj-dev-standards
  -> 编码
  -> hgj-dev-test
```

写总结、群消息或说明文档时，再单独加载 `keben-writing-style`。

## 边界

- 这个登记只提供本机路径和路由，不代表已经全局安装到 `~/.agents/skills` 或 `~/.claude/skills`。
- 四个 HTML 是文档导出，不是可直接复制安装的完整 Skill 源码；README 说明它们已包含在 hgj-dev 中。
- `keben-writing-style` 是该目录中唯一完整的 Skill 文件夹，但当前仍以 Downloads 中的本机源码作为来源。
- 不要因为加载了需求分析或测试文档，就自动执行 TAPD 写入、外部系统写入、部署或有副作用操作；这些动作仍需按当前任务的授权规则确认。

## 以后怎么引用

用户可以直接说：

- “按 hgj-dev 的团队规范做这个开发任务。”
- “用 hgj-tapd-parse 帮我整理这个 TAPD 需求。”
- “生成一份 hgj-req-html 风格的需求分析 HTML。”
- “用 hgj-dev-test 做接口联调和验收。”
- “用 keben-writing-style 把这段话改得像人说的。”

Agent 命中这些说法后，从本文件定位到 Downloads 中的对应材料。
