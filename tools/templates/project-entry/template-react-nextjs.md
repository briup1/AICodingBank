# CLAUDE.md

## 项目概述
基于 Next.js 15 的全栈 Web 应用，使用 App Router 模式。

## 技术栈
- 框架：Next.js 15（App Router）
- 语言：TypeScript 5
- UI：Tailwind CSS 4 + shadcn/ui
- 状态管理：Zustand
- 数据请求：TanStack Query (React Query)
- 表单：React Hook Form + Zod 校验
- 包管理：pnpm
- 测试：Vitest + React Testing Library + MSW (API 模拟)

## 项目结构
src/
├── app/            # Next.js App Router 页面
│   ├── (auth)/     # 认证相关页面组
│   ├── (main)/     # 主业务页面组
│   ├── api/        # API 路由
│   └── layout.tsx  # 根布局
├── components/     # 可复用组件
│   ├── ui/         # shadcn/ui 基础组件
│   └── features/   # 业务功能组件
├── hooks/          # 自定义 Hooks
├── lib/            # 工具函数和配置
├── stores/         # Zustand 状态管理
├── types/          # TypeScript 类型定义
└── styles/         # 全局样式

## 编码规范
- 组件使用函数式组件 + Hooks，禁止 class 组件
- 文件命名：组件用 PascalCase（UserCard.tsx），工具用 camelCase（formatDate.ts）
- 每个组件一个文件，导出使用 named export
- Props 类型定义放在组件文件顶部，使用 interface
- 客户端组件必须添加 "use client" 指令
- 使用 Server Components 优先，只在需要交互时使用 Client Components
- 样式使用 Tailwind CSS 类名，禁止内联 style
- 禁止使用 any 类型

## 工作流
- 安装依赖：pnpm install
- 开发：pnpm dev
- 构建：pnpm build
- 代码检查：pnpm lint
- 类型检查：pnpm type-check
- 安装 shadcn/ui 组件：pnpm dlx shadcn add <component-name>
- 运行测试：pnpm test
- 运行测试（监听模式）：pnpm test:watch

## 注意事项
- 不要修改 tailwind.config.ts 的核心配置
- API 路由必须有错误处理和输入校验
- 图片使用 next/image 组件，禁止<img> 标签
- 环境变量统一在 .env.local 中管理，变量名以 NEXT_PUBLIC_ 开头的暴露给客户端
