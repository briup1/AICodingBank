# CLAUDE.md

## 项目概述
Node.js RESTful API 服务，提供用户认证和数据处理能力。

## 技术栈
- 运行时：Node.js 22
- 框架：Express 5
- 语言：TypeScript 5
- ORM：Prisma 6
- 数据库：PostgreSQL 16
- 认证：JWT（jsonwebtoken）
- 校验：Zod
- 包管理：pnpm

## 项目结构
src/
├── routes/         # 路由定义
├── controllers/    # 控制器（处理请求响应）
├── services/       # 业务逻辑
├── repositories/   # 数据访问层（Prisma）
├── middleware/      # 中间件（认证、错误处理、日志）
├── schemas/        # Zod 校验 Schema
├── utils/          # 工具函数
├── types/          # TypeScript 类型
└── app.ts          # 应用入口

## 编码规范
- 使用 async/await，禁止回调地狱
- 错误处理使用自定义 AppError 类 + 全局错误中间件
- 路由参数和请求体必须用 Zod Schema 校验
- 环境变量使用 dotenv，通过 zod 校验类型安全
- 日志使用 pino，不用 console.log
- API 响应统一格式：{ success, data, error, message }

## 工作流
- 安装依赖：pnpm install
- 开发：pnpm dev
- 构建：pnpm build
- 测试：pnpm test
- 数据库迁移：npx prisma migrate dev
- 数据库生成：npx prisma generate

## 注意事项
- 不要修改 prisma/migrations/ 下的已有迁移文件
- JWT 密钥从环境变量读取，禁止硬编码
- 密码使用 bcrypt 哈希
- 新增路由必须添加认证中间件（公开接口除外）
