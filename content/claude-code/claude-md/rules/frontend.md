---
paths:
  - "src/components/**/*.vue"
  - "src/views/**/*.vue"
  - "src/stores/**/*.ts"
---

# 前端组件规范

- 组件使用 `<script setup lang="ts">` 语法
- Props 使用 `defineProps<T>()` 定义，必须有类型声明
- 使用 Pinia 管理全局状态，避免分散的响应式数据
- API 调用统一使用 axios 或 fetch 封装
- 组件按功能划分：基础组件（Base*）、业务组件、页面组件
