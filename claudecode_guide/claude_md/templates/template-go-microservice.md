# CLAUDE.md

## 项目概述
基于 Go 的微服务后端，提供用户管理和订单处理能力。

## 技术栈
- 语言：Go 1.23
- 框架：Gin 1.10
- ORM：GORM 2.0
- 数据库：MySQL 8.0
- 缓存：Redis（go-redis）
- 消息队列：NATS
- 配置：Viper
- 日志：Zap

## 项目结构
.
├── cmd/             # 应用入口
│   └── server/
│       └── main.go
├── internal/        # 私有代码
│   ├── handler/     # HTTP 处理器
│   ├── service/     # 业务逻辑
│   ├── repository/  # 数据访问层
│   ├── model/       # 数据模型
│   ├── middleware/   # 中间件
│   └── config/      # 配置加载
├── pkg/             # 可复用公共包
├── api/             # API 定义（Proto/OpenAPI）
└── configs/         # 配置文件

## 编码规范
- 遵循 Effective Go 和 Go Code Review Comments
- 错误处理不使用 panic，使用 error 返回值
- 接口定义在消费方，不在实现方
- 使用 context.Context 传递请求上下文和超时
- 依赖注入使用构造函数，不使用全局变量
- 日志使用结构化日志（Zap），不用 fmt.Println
- 并发安全：共享状态必须使用 channel 或 sync 原语保护

## 工作流
- 编译：go build -o bin/server ./cmd/server
- 运行：go run ./cmd/server
- 测试：go test ./...
- 代码检查：golangci-lint run
- 格式化：gofmt -w .

## 注意事项
- 不要修改 go.mod 中的 Go 版本号
- 新增 API 路由必须添加中间件（认证、限流、日志）
- 数据库连接使用连接池，设置合理的 MaxOpenConns 和 MaxIdleConns
- 禁止使用 _ 忽略 error 返回值
