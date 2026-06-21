---
title: "Template Java Springboot"
date: 2026-06-21
category: claude-code
tags: []
status: published
description: "Notes on Template Java Springboot."
---

# CLAUDE.md

## 项目概述
基于 Spring Boot 3.x 的 RESTful API 服务，面向企业管理后台提供后端接口。

## 技术栈
- 语言：Java 17（使用 var、record、switch 表达式等新特性）
- 框架：Spring Boot 3.3 + Spring Security + Spring Validation
- ORM：MyBatis-Plus 3.5
- 数据库：MySQL 8.0
- 缓存：Redis 7（使用 Spring Data Redis）
- 构建工具：Maven 3.9
- 辅助工具：Lombok
- API 文档：SpringDoc OpenAPI (Swagger)

## 项目结构
src/main/java/com/example/project/
├── controller/     # REST 接口层，只做参数校验和转发
├── service/        # 业务逻辑层，核心逻辑在这里
│   └── impl/       # 实现类
├── mapper/         # MyBatis-Plus Mapper 接口
├── entity/         # 数据库实体类（@TableName）
├── dto/            # 数据传输对象（请求/响应）
├── config/         # 配置类（Security、Redis、CORS 等）
├── common/         # 公共组件
│   ├── result/     # 统一返回 Result<T>
│   ├── exception/  # 全局异常处理
│   └── constant/   # 常量定义
└── util/           # 工具类

## 编码规范
- 使用 Lombok 简化 POJO（@Data、@Builder、@NoArgsConstructor）
- 统一返回 Result<T>，禁止直接返回 Map 或裸对象
- REST 接口命名：资源名用复数名词，如 /api/users、/api/orders
- 日志使用 @Slf4j 注解，禁止 System.out.println
- 异常使用自定义 BizException，通过 GlobalExceptionHandler 统一处理
- DTO 字段校验使用 jakarta.validation 注解（@NotNull、@Size 等）
- 优先使用 Java Stream API 处理集合
- 严格遵循 SOLID 原则

## 数据库规范
- 表名后缀：_config（配置表）、_info（信息表）、_log（日志表）
- 所有表必须包含：id（BIGINT 自增主键）、created_at、updated_at
- 逻辑删除字段：is_deleted（TINYINT，0 未删除，1 已删除）

## 工作流
- 编译：mvn clean compile
- 打包：mvn clean package -DskipTests=true
- 测试：mvn test
- 启动：mvn spring-boot:run

## 注意事项
- 不要修改 src/main/resources/db/migration/ 下的已有迁移文件
- 新增接口必须添加 Swagger 注解（@Tag、@Operation）
- 敏感配置使用环境变量，不要硬编码到 application.yml
- Controller 层不写业务逻辑，只做参数校验和调用 Service
