# CLAUDE.md

## 项目概述
跨平台移动应用（iOS + Android），使用 Flutter 3 + Dart 3。

## 技术栈
- 框架：Flutter 3.29
- 语言：Dart 3.7
- 状态管理：Riverpod 2
- 路由：GoRouter
- 网络请求：Dio
- 本地存储：Hive
- 序列化：freezed + json_serializable
- 代码生成：build_runner
- 包管理：pub（flutter pub）

## 项目结构
lib/
├── core/           # 核心基础设施
│   ├── network/    # Dio 配置和拦截器
│   ├── storage/    # 本地存储
│   ├── theme/      # 主题配置
│   └── utils/      # 工具函数
├── features/       # 功能模块（按业务划分）
│   ├── auth/       # 认证模块
│   │   ├── data/   # 数据层（Repository 实现、API）
│   │   ├── domain/ # 领域层（Entity、Repository 接口）
│   │   └── presentation/ # 表现层（Page、Widget、Provider）
│   └── home/
├── shared/         # 共享组件和模型
└── main.dart       # 应用入口

## 编码规范
- 使用 clean architecture 分层（data / domain / presentation）
- 状态管理使用 Riverpod，Provider 定义使用 @riverpod 注解
- 模型类使用 freezed 生成不可变对象
- 路由使用 GoRouter，新页面必须在路由表中注册
- Widget 拆分原则：单个 Widget 不超过 200 行
- 使用 const 构造函数优化性能
- 字符串统一放在 lib/core/l10n/，支持国际化

## 工作流
- 获取依赖：flutter pub get
- 代码生成：dart run build_runner build --delete-conflicting-outputs
- 开发运行：flutter run
- 构建 APK：flutter build apk
- 构建 iOS：flutter build ios
- 代码检查：dart analyze
- 格式化：dart format .

## 注意事项
- 不要修改 android/app/build.gradle 中的签名配置
- iOS 权限配置在 ios/Runner/Info.plist 中
- 新增依赖包后执行 flutter pub get
- 图片资源放在 assets/images/，并在 pubspec.yaml 中注册
