# UExtract 项目开发规范

## 开发环境提示
- Python包管理使用uv，安装包的唯一途径：`cd backend && source .venv/bin/activate && uv add <package>`，永远不要直接编辑uv.lock，pyproject.toml文件。
- 所有Python脚本执行都必须在虚拟环境下：`cd backend && source .venv/bin/activate && python xxx`
- 前端开发使用npm，在frontend目录下运行相关命令

## Make命令使用说明
项目提供统一的Make脚本来管理服务，所有可用命令：
- `make up` - 启动所有服务 (前端 + 后端)
- `make down` - 停止所有服务
- `make restart` - 重启所有服务
- `make backend` - 仅启动后端服务 (使用本地uv环境)
- `make frontend` - 仅启动前端服务 (使用本地npm)
- `make help` - 显示所有可用命令的帮助信息

## 测试说明
- 所有测试脚本的顶级目录为：`./tests`
- 使用Make脚本进行服务起停，无需重新编写shell代码
- 运行测试前确保服务已启动：`make up`
- 在backend目录下运行测试：`cd backend && source .venv/bin/activate && pytest`
- 运行特定测试：`cd backend && source .venv/bin/activate && pytest tests/api/routes/test_items.py`
- 查看测试覆盖率：`cd backend && source .venv/bin/activate && pytest --cov=app`
- 修复所有测试错误，确保整个测试套件通过
- 修改代码后，即使没有明确要求，也要添加或更新相应的测试
- 测试用户信息：`username: admin@example.com` `password: admin123456`

## 代码提交说明
- 提交前确保所有测试通过：`cd backend && source .venv/bin/activate && pytest`
- 提交前运行代码检查：`cd backend && source .venv/bin/activate && ruff check .`
- 提交信息格式：[功能模块] 简短描述

## 项目结构说明
- backend/ - 后端代码目录，使用FastAPI框架
- frontend/ - 前端代码目录，使用React框架
- backend/tests/ - 后端测试脚本目录
- docs/ - 项目文档目录


## 识别项目开发阶段并遵守相应的开发规范
### 从0开始开发基本原则
1. 可测试性优先（Testability First）
2. 关注点分离（Separation of Concerns）     
3. 开闭原则（Open/Closed Principle）
4. 渐进式演进（Progressive Elaboration）
5. 显式优于隐式（Explicit over Implicit）
6. 契约驱动（Contract-Driven Design）
7. 可观测性内建（Observability by Design）


### 项目二次开发基本原则
1. 尊重原有架构与设计风格
2. 最小侵入原则（Low Coupling / Minimal Impact）
3. 充分理解现有代码
4. 严格遵守测试策略
5. 版本控制与协作规范
6. 配置与依赖管理
7. 复用日志、监控与可观测性
8. 安全与合规
9. 性能与资源考量
10. 文档同步更新


## 代码规范
- @.sec_dev_workflow/coding_rules/python_fastapi_pydantic_orm.md

## 统一测试用户
- 用户名：admin@example.com
- 密码：admin123456