---
title: "Readme"
date: 2026-06-21
category: notes
tags: []
status: published
description: "Notes on Readme."
---

# content/ —— 知识内容

本目录存放面向读者与人的知识文章，是博客站点的内容源。

## 目录

- [workflow/](./workflow/)：AI 驱动开发工作流
- [claude-code/](./claude-code/)：Claude Code 使用指南
- [best-practices/](./best-practices/)：最佳实践
- [notes/](./notes/)：个人随笔与未归类笔记

## 新增文章约定

1. 放在对应分类目录下，文件名使用英文 kebab-case。
2. 顶部添加统一 frontmatter：
   ```yaml
   ---
   title: "文章标题"
   date: 2026-06-21
   category: workflow | claude-code | best-practices | notes
   tags: [tag1, tag2]
   status: draft | published | archived
   description: "一句话摘要"
   ---
   ```
3. 在 [MAP.md](../MAP.md) 中登记入口。
