---
paths:
  - "backend/models/**/*.py"
  - "models/**/*.py"
  - "**/migrations/**/*.py"
---

# 数据库规范

- 使用 SQLAlchemy 操作数据库
- 模型字段必须有类型注解和 docstring
- 外键关系明确标注，避免隐式关联
- 数据库迁移使用版本控制工具（Alembic / Django migrations）
- 复杂查询封装为 Repository 或 Service 层方法
