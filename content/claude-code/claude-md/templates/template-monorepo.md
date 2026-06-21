---
title: "Template Monorepo"
date: 2026-06-21
category: claude-code
tags: []
status: published
description: "Notes on Template Monorepo."
---

# CLAUDE.md

## 项目概述
全栈 Monorepo 项目，前端 Next.js + 后端 Node.js API + 共享类型包。

## 技术栈
- 包管理：pnpm workspace
- 构建工具：Turborepo
- 前端：Next.js 15 + Tailwind CSS
- 后端：Node.js + Express + Prisma
- 共享包：TypeScript 类型、工具函数
- 语言：TypeScript 5（全栈统一）

## 项目结构
.
├── apps/
│   ├── web/           # Next.js 前端应用
│   └── api/           # Express API 服务
├── packages/
│   ├── shared/        # 共享类型和工具
│   ├── ui/            # 共享 UI 组件
│   └── config/        # 共享配置（ESLint、TS）
├── turbo.json         # Turborepo 配置
└── pnpm-workspace.yaml

## 编码规范
- 包间依赖使用 workspace:* 协议
- 共享类型定义放在 packages/shared/src/types/
- API 请求/响应类型从 @workspace/shared 导入
- 每个 app/ 和 package/ 有自己独立的 tsconfig.json
- UI 组件放在 packages/ui/，确保 web 和未来的其他端可复用
- 遵循各子项目的独立编码规范

## 工作流
- 安装所有依赖：pnpm install
- 开发（全栈）：turbo dev
- 构建（全栈）：pnpm turbo build
- 代码检查（全栈）：pnpm turbo lint
- 只开发前端：pnpm --filter web dev
- 只开发后端：pnpm --filter api dev

## 注意事项
- 修改 packages/shared 后，依赖它的包会自动更新（Turborepo 增量构建）
- 不要在 apps/ 之间建立直接依赖
- 新增包必须在 pnpm-workspace.yaml 中注册
