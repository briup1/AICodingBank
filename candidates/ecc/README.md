# ECC 候选内容

来自 [everything-claude-code](https://github.com/mit-network/everything-claude-code) 的原样候选快照。

- 来源提交：`5df943ed2bdfaf1297775066d84e1e1e0fc1d579`
- 上游版本：`1.9.0`
- 许可证：MIT
- 状态：仅归档，未安装、未启用、未登记为 Skill

## 已选 Agent

| Agent | 候选用途 |
|---|---|
| `e2e-runner` | 应用可运行后验证关键用户流程 |
| `typescript-reviewer` | TypeScript/React 代码完成后的专项审查；Vue 仅采用通用 TS 部分 |
| `python-reviewer` | Python 代码完成后的专项审查 |
| `java-reviewer` | Java/Spring Boot 代码完成后的专项审查 |
| `database-reviewer` | SQL、PostgreSQL、迁移、索引或事务相关审查 |

项目规范优先于候选内容。候选文件不应直接复制到 Agent 加载目录；验证和适配后再决定是否启用。

## 待处理

React/Vue、Python、Java 的精选 Rules 尚未归档，后续按每批不超过 10 个文件处理。
