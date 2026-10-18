# 生成 Skill 契约

## 必需结构

每个 Skill 至少包含：

```text
skill-name/
├── SKILL.md
└── sources.md
```

只有确有用途时才添加：

```text
references/  长 API、架构模式、排障、迁移
scripts/     可重复且需要确定性的操作
assets/      最终产物需要复用的模板或资源
agents/      UI 元数据和调用策略
```

禁止创建空目录、占位文件和与 Skill 使用无关的 README。

## Frontmatter

```yaml
---
name: framework-capability
description: 用一句话说明能力、触发时机和必要边界。
metadata:
  framework: "框架名"
  framework-version: "目标版本"
  generated-from: "official-sources"
---
```

要求：

- `name` 使用小写字母、数字和连字符，且与目录名一致。
- description 应可独立完成自动发现，不使用 catch-all 表述。
- metadata 值使用字符串，版本未知时不要伪造。
- 默认正文为中文；API、代码和命令保留官方拼写。

## SKILL.md 内容

只写会改变 Agent 行为的内容：

- 适用和不适用边界。
- 架构选择和决策标准。
- 框架特有工作流。
- 已验证的不变量与风险边界。
- 验证结果的方法。
- 何时读取哪个 reference。
- 何时调用 docs Skill 核验版本敏感信息。

不要写：

- 大段文档摘要。
- 通用编码常识。
- 未经来源支持的绝对规则。
- 完整 API 清单。
- 仅用于展示的冗长示例。
- 与用户授权无关的远程写操作。

## references

每个 reference 在 `SKILL.md` 中必须有明确读取条件。推荐按任务拆分：

```text
architecture.md     架构关系和生命周期
patterns.md         经过官方资料支持的组合模式
api-map.md          版本化 API 索引，不复制全文
troubleshooting.md  症状、证据、根因、修复和验证
migration.md        版本差异和升级检查表
```

避免 references 多层嵌套；如果文件没有被入口指引或真实任务使用，应删除。

## sources.md

采用可机器提取的 URL 列表：

```markdown
# 官方来源

- https://official.example/docs/overview
- https://github.com/official/framework/tree/v1.2.3
```

可以在 URL 后补充简短用途，但每行只放一个主要 URL。仅列出实际用于该 Skill 的来源。

## Docs Skill

当框架 API 变化快或文档规模大时生成 `framework-docs`：

- 先读取官方 `llms.txt` 或 sitemap 定位页面。
- 对 API 签名、默认值、CLI、实验功能和 latest 行为实时核验。
- 优先目标版本页面；无法定位版本时明确说明。
- 返回结论时记录页面 URL 和版本。
- 不重复领域 Skill 已经稳定编译的决策知识。

## 生成报告

Pack 根目录的 `generation-report.md` 至少记录：

- 输入范围、框架版本、源码 tag/commit 和生成日期。
- 生成、合并、排除的 Skill 及原因。
- 来源冲突和处理结果。
- 执行过的结构、脚本、示例和 E2E 测试。
- 未覆盖领域、已知限制和刷新命令。

## 更新保护

refresh 时：

- 先读取现有 Skill 和 manifest。
- 只修改来源发生变化且结论受影响的文件。
- 保留无法由生成器证明来源的人工修改，并报告冲突。
- 不因格式偏好重写未受影响文件。
