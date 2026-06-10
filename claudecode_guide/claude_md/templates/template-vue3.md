# CLAUDE.md

## 项目概述
基于 Vue 3 的企业管理后台系统，使用 Composition API + script setup 语法。

## 技术栈
- 框架：Vue 3.4 + Vue Router 4
- 语言：TypeScript 5
- 构建：Vite 6
- 包管理：pnpm
- 状态管理：Pinia
- UI 库：Element Plus
- 样式：UnoCSS
- HTTP：Axios
- 类型检查：vue-tsc
- 代码检查：ESLint + Prettier

## 项目结构
src/
├── api/            # API 请求封装
├── assets/         # 静态资源
├── components/     # 公共组件
├── composables/    # 组合式函数（自定义 Hooks）
├── layouts/        # 布局组件
├── pages/          # 页面组件
├── router/         # 路由配置
├── stores/         # Pinia 状态管理
├── styles/         # 全局样式
├── types/          # TypeScript 类型
└── utils/          # 工具函数

## 编码规范
- 必须使用 <script setup lang="ts"> 语法
- 组件命名使用 PascalCase
- 组合式函数命名以 use 开头（useUserList、usePermission）
- Props 使用 defineProps<T>() 泛型语法
- 事件使用 defineEmits<T>() 定义类型
- API 请求统一在 api/ 目录封装，禁止在组件中直接调用 axios
- 列表页面使用分页，默认每页 20 条

## 工作流
- 安装依赖：pnpm install
- 开发：pnpm dev
- 构建：pnpm build
- 代码检查：pnpm lint
- 类型检查：vue-tsc --noEmit

## 注意事项
- 不要修改 vite.config.ts 中的代理配置
- 路由必须配置 name 和 meta（title、icon、permission）
- Element Plus 组件按需引入，不要全局注册
- 禁止使用 any 类型
