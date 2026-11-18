---
title: "项目入口文件：生成 CLAUDE.md 与 AGENTS.md 的提示词（含四层 steering）"
date: 2026-06-10
date_basis: first-repository-record
updated: 2026-10-18
category: 技术
tags: [AGENTS.md, CLAUDE.md, 项目入口, 提示词, steering]
status: historical-unverified
source:
  - "git:2807c1f:claudecode_guide/claude_md/生成-claude.md-prompt.md"
  - "git:3915381:claudecode_guide/prompt/101_AGENTS.md生成提示词.md"
  - "git:acc2d0b:claudecode_guide/prompt/102_AGENTS.md生成提示词_分层优化版.md"
---

# 项目入口文件：生成 CLAUDE.md 与 AGENTS.md 的提示词（含四层 steering）

## 主题与预期效果

新项目或老项目要让 AI “打开即理解、改完即验证”，入口文件（CLAUDE.md / AGENTS.md）是第一步，但手写容易两个极端：写成大段介绍没人维护，或几乎不写全靠现场猜。这三份提示词把“生成入口文件”变成可复用流程：喂项目信息 → 按固定区块成稿 → 质量检查 → 给出下沉建议。

链路：

```text
项目信息（必填：一句话描述、技术栈带版本、仓库结构）
  → 按需选区块生成（不要凑齐所有章节）
  → 质量检查（≤200 行、条目化、版本号具体、禁止项带替代方案、安全红线）
  → 下沉建议（rules / skills / hooks）
  → 项目根目录的 CLAUDE.md 或 AGENTS.md
```

三份原文是一次演进：CLAUDE.md 版（06-10）→ AGENTS.md 基线版（06-30）→ 分层优化版（07-11，新增**四层 steering**）。

## 原文意图

- [生成CLAUDE.md提示词.md](生成CLAUDE.md提示词.md)：最早的版本，定位是“让 AI 从通用助手变成懂项目的资深同事”，已包含必填/可选信息清单和质量要求。
- [生成AGENTS.md提示词.md](生成AGENTS.md提示词.md)：迁移到 AGENTS.md 命名，明确“AGENTS.md 不是手册，而是地图，细节通过链接指向 docs/”。
- [生成AGENTS.md提示词-分层优化版.md](生成AGENTS.md提示词-分层优化版.md)：核心增量是**四层 steering 路由表**——`AGENTS.md` 放常驻硬事实、`rules/*.md` 放某类文件的专属约束（按 paths 触发）、`skills` 放多步骤流程（按任务语义触发）、`settings.json` hooks 放漏一次代价很大的强制动作。规律一句话：**能推断的不写；低频的下沉；必须强制的交给 hooks。** 该版本还给了负面示例（通用 AI 礼仪、大段描述、模糊规则、不可执行验证）。

## 建议用法（尚未实测）

1. 用分层优化版作为主提示词；基线版和 CLAUDE.md 版留作对照，理解设计取舍。
2. 生成前先自查“必填三项”（项目一句话、技术栈带版本、仓库结构），缺失项按 `[推断]` 标注，后续人工核。
3. 成稿后按原文质量检查清单过一遍，重点看：禁止事项是否带替代方案、验证命令是否独立可执行、长度是否 ≤200 行。
4. 配套模板在本项目维护：10 个技术栈模板、用户级/项目级样例、rules 样本见 [project-entry 模板目录](../../tools/templates/project-entry/README.md)。
5. 四层 steering 与本工作台的组织方式同源：常驻规则进 AGENTS.md、岗位流程进各 `SKILL.md`、强制卡点交给 hooks/测试；给新项目建入口文件时可直接沿用这套分层。

## 注意事项

- 提示词假设“用户提供信息”齐全度不可控，导致生成质量波动；信息缺口要显式标注而不是让模型编。
- 分层路由表是推荐结构，项目没有 rules/skills/hooks 机制时（如部分宿主不识别）需要退化处理。
- 原文没有执行记录，生成文件的实际效果是方法分析，不是实测结论。

## 验证与来源

三份原文档分别由 `2807c1f`（2026-06-10）、`3915381`（2026-06-30）、`acc2d0b`（2026-07-11）首次入库。本次只读取原文、分析演进并整理用法，没有新执行验证，因此保持 historical-unverified；后续真实使用时记录：生成文件是否长期维护、下沉建议是否被采纳、AI 对入口文件的实际遵循程度，再更新状态。记录规则见 [统一规范](../STANDARD.md)。
