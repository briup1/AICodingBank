---
paths:
  - "tests/**/*.py"
  - "backend/tests/**/*.py"
  - "src/__tests__/**/*.ts"
---

# 测试规范

- 后端使用 pytest，测试文件以 `test_` 前缀命名
- 前端使用 Vitest，测试文件以 `.spec.ts` 或 `.test.ts` 后缀命名
- 测试覆盖：单元测试、接口测试、关键业务流程测试
- 使用 fixture 管理 测试数据和数据库状态
- Mock 外部服务依赖，保证测试隔离性
