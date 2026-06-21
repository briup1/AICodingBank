---
title: "Readme"
date: 2026-06-21
category: tools
tags: []
status: published
description: "Notes on Readme."
---

# tools/ —— AI 工具资产

本目录存放面向 AI 的工具资产，供 Claude Code、Cursor、Codex 等使用。

## 目录

- [skills/](./skills/)：Skill 定义（`SKILL.md`）
- [prompts/](./prompts/)：阶段提示词与 Prompt 模板
- [agents/](./agents/)：子代理定义
- [rules/](./rules/)：项目规则与约束

## 新增工具约定

1. Skill 放 `skills/{domain}/{skill-name}/`，必须包含 `SKILL.md`。
2. Prompt 放 `prompts/{domain}/`，使用 `.prompt.md` 后缀。
3. Agent 放 `agents/`，使用 `.md` 后缀。
4. Skill 更新后，同步更新 `.claude/skills/` 中的符号链接。
5. 若 Skill 有对应博客文章，在 `SKILL.md` frontmatter 中填写 `related-post`。

## Claude Code 符号链接说明

`.claude/skills/` 已加入 `.gitignore`，不会被提交。它应通过符号链接指向 `tools/skills/` 下的 Skill 目录。当前本地链接已建立，Claude Code 可正常加载。在新环境克隆后，需要重新创建链接：

```bash
ln -s ../../tools/skills/{domain}/{skill-name} .claude/skills/{skill-name}
```

（Windows 用户可使用 junction 或复制目录。）
