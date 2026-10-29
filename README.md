# AICodingBank

个人 AI 工作台的控制入口，也是 AI Coding 兵工厂：管理岗位、Skill 能力、执行配置与工作记录，让你跨项目、跨 AI 工具地获得"组织化产能"——你只出目标、取舍和授权，AI 按岗位接单、按纪律交付、全程可查账。

## 设计理念

- **四层分离**：岗位定义职责，Skill 定义方法，执行配置定义模型与工具，会话承载一次具体工作；四层互不复制。见[岗位名册](roles/README.md)、[能力目录](CATALOG.md)、[执行配置说明](tools/execution-profiles/README.md)。
- **单点控制面**：能力只有一份正文、一次登记（`skills.yaml` / `skills-lock.json`），由 `install.py` 软链装配到各宿主；登记、验证、安装、停用都可核对。
- **留痕契约**：结构变动写[迁移记录](docs/migrations/)，目录与引用由测试锁定；不靠记忆和口头约定。

工作台资源入口见 [AGENTS.md](AGENTS.md)；每个目录的中文注解见[目录中文地图](docs/reference/工作台目录地图.md)。

## 文档导航

| 要看什么 | 去哪里 |
| --- | --- |
| 工作台资源入口 | [AGENTS.md](AGENTS.md)（[CLAUDE.md](CLAUDE.md) 为指针） |
| 怎么加：Skill、岗位、最佳实践、第三方 | [EXTENDING.md](EXTENDING.md) |
| 术语 | [CONTEXT.md](CONTEXT.md) |
| 能力总览（自动生成，勿手改） | [CATALOG.md](CATALOG.md) |
| 岗位手册 | [roles/README.md](roles/README.md) |
| 最佳实践记录规范 | [best_practices/README.md](best_practices/README.md) |
| 每个目录的中文注解 | [docs/reference/工作台目录地图.md](docs/reference/工作台目录地图.md) |

## 常用命令

```bash
python3 install.py --catalog-only   # 刷新 CATALOG.md，不联网、不安装
python3 install.py                  # 同步第三方上游 + 安装已验证 Skill（需授权）
```

- 新机器：`git clone` 本仓库后运行 `python3 install.py`。
- 添加/更新 Skill、收藏第三方、写最佳实践：完整步骤见 [EXTENDING.md](EXTENDING.md)。
- 本机临时停用某个 Skill：写入 Git 忽略的 `skills.local.yaml` 后重跑安装器，不改共享验证状态。
