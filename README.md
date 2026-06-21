# AICodingBank

AI 驱动开发的个人知识库与工具箱。

## 双轨结构

本仓库采用「双轨」组织方式：

- **`content/`** —— 面向读者与人的知识内容，未来可直接发布为博客。
- **`tools/`** —— 面向 AI 的工具资产（Skill、Prompt、Agent、Rules），供 Claude / Cursor / Codex 等使用。
- **`examples/`** —— 项目示例、报告与配置参考。
- **`site/`** —— 静态站点配置（预留）。

## 快速入口

| 入口 | 说明 |
|------|------|
| [MAP.md](./MAP.md) | 知识地图，按主题浏览全部内容 |
| [content/README.md](./content/README.md) | 知识内容目录 |
| [tools/README.md](./tools/README.md) | 工具资产目录 |
| [examples/README.md](./examples/README.md) | 示例与报告目录 |

## 使用约定

1. **新增知识文章**：放 `content/{分类}/`，添加 frontmatter，在 MAP.md 中登记。
2. **新增 AI 工具**：放 `tools/{skills|prompts|agents|rules}/`，重建 `.claude/skills/` 符号链接。
3. **Skill 同步博客**：在 `content/` 下写对应的人本化文章，并在 skill frontmatter 中关联 `related-post`。

## 状态

重构中，MAP.md 与分类仍在持续完善。
