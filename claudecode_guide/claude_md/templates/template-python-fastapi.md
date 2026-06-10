# CLAUDE.md

## 项目概述
基于 FastAPI 的数据处理 API 服务，提供数据导入、清洗和查询接口。

## 技术栈
- 语言：Python 3.12
- 框架：FastAPI 0.115
- ORM：SQLAlchemy 2.0（异步模式）
- 数据库：PostgreSQL 16
- 数据校验：Pydantic v2
- 任务队列：Celery + Redis
- 包管理：uv（替代 pip + venv，支持 pyproject.toml）

## 项目结构
app/
├── api/            # API 路由
│   └── v1/         # 版本化路由
├── core/           # 核心配置
│   ├── config.py   # 环境配置
│   └── security.py # 认证授权
├── models/         # SQLAlchemy 模型
├── schemas/        # Pydantic 模型（请求/响应）
├── services/       # 业务逻辑
├── crud/           # 数据库 CRUD 操作
├── utils/          # 工具函数
└── main.py         # 应用入口

## 编码规范
- 使用 type hints 标注所有函数参数和返回值
- 异步优先：数据库操作使用 async/await
- 依赖注入使用 FastAPI 的 Depends
- 配置使用 pydantic-settings，从 .env 读取
- 路由函数只做参数校验和调用 service，不写业务逻辑
- 异常使用自定义异常类，通过 exception_handler 统一处理
- 使用 Python 标准库的 logging 模块，不用 print

## 工作流
- 创建虚拟环境：uv venv
- 激活环境：source .venv/bin/activate
- 安装依赖：uv pip install -r requirements.txt
- 开发：uv run uvicorn app.main:app --reload
- 测试：uv run pytest
- 代码检查：uv run ruff check .

## 注意事项
- 不要修改 alembic/ 目录下的已有迁移文件
- 新增 API 必须添加 OpenAPI 描述（summary、description）
- 数据库操作必须使用 async session
- 密码使用 bcrypt 哈希，禁止明文存储
