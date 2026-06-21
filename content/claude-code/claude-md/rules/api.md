---
paths:
  - "backend/**/*.py"
  - "app/api/**/*.py"
  - "routers/**/*.py"
---

# API 接口规范

- 使用 Pydantic 做请求/响应模型定义和参数校验
- 返回格式统一为 `{ "code": int, "data": any, "message": str }`
- 错误码遵循 HTTP 标准（400/401/403/404/500）
- 使用依赖注入管理数据库会话和认证
- 接口按业务模块划分路由文件
