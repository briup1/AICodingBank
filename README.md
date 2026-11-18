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
| 按任务找项目、共享能力或验收入口 | [AGENTS.md](AGENTS.md)（[CLAUDE.md](CLAUDE.md) 为指针） |
| 怎么加：Skill、岗位、最佳实践、第三方 | [EXTENDING.md](EXTENDING.md) |
| 术语 | [CONTEXT.md](CONTEXT.md) |
| 能力总览（自动生成，勿手改） | [CATALOG.md](CATALOG.md) |
| 想画图但不知道选哪种图 | [工程图形画册](docs/reference/diagram-atlas.html)（离线 HTML，31 种图形的形态与用法） |
| 岗位手册 | [roles/README.md](roles/README.md) |
| 最佳实践记录规范 | [best_practices/README.md](best_practices/README.md) |
| 每个目录的中文注解 | [docs/reference/工作台目录地图.md](docs/reference/工作台目录地图.md) |

## 常用命令

```bash
python3 install.py --catalog-only   # 刷新 CATALOG.md，不联网、不安装
python3 install.py                  # 同步第三方上游 + 安装已验证 Skill（需授权）
```

- 添加/更新 Skill、收藏第三方、写最佳实践：完整步骤见 [EXTENDING.md](EXTENDING.md)。
- 本机临时停用某个 Skill：写入 Git 忽略的 `skills.local.yaml` 后重跑安装器，不改共享验证状态。

## 换机与本机恢复

1. Clone 工作台和实际需要的项目。恢复或手工重建 Git 忽略的 `personal/projects.local.md`：每项记项目名、用途、主仓库绝对路径；可另记统一 Worktree 根目录，不录临时 Worktree、分支或凭证。账号、密钥、登录态按各工具规范单独恢复。
2. 从工作台根目录开新会话。Pi、Codex 等以 [AGENTS.md](AGENTS.md) 为工作台入口；Claude Code 从 [CLAUDE.md](CLAUDE.md) 转过去。Pi 的用户级按需索引和 [`/pm`](tools/integrations/pi-pm/README.md) 都是可选接入：有用到才恢复，核对本机路径与模板链接；装 Skill 不会替你恢复这些入口。
3. **先只读检查**：在工作台根目录运行 `git check-ignore personal/projects.local.md`；从索引抽一个项目，确认主仓库可访问，再将变量 `repo` 设为其绝对路径，运行 `git -C "$repo" worktree list --porcelain`，核对 Git 登记的副本和选中的项目入口是否可读。若使用了软链，用 `ls -l` 看目标，再用 `test -r` 检查是否可读。开新会话请宿主回报它实际读到的工作台入口；不要把文件存在当成自动加载成功。
4. 只有要装配已验证 Skill 且获得当前授权时，才执行上面的安装命令。缺项目、宿主入口或本机配置时报告缺项；不为验证入口顺带安装、登录或发业务请求。
