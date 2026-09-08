# {项目名} Agent 工作入口

> 状态：草案（待人工确认）
> 本文件只作为目标宿主的最薄入口；项目事实和规则优先引用已有唯一来源。

<!-- harness-pack:begin -->
## 项目索引

| 内容 | 唯一事实源 | 适用范围 | 验证方式 |
|------|------------|----------|----------|
| 项目概述与技术栈 | {已有 AGENTS/README/配置路径} | {范围} | {配置/构建证据} |
| 架构与依赖约束 | `docs/harness/rules/工程结构.md` 或已有架构文档 | {范围} | {测试/lint/人工} |
| 编码规范 | `docs/harness/rules/编码规范.md` 或已有配置 | {范围} | {formatter/lint/test} |
| 开发流程 | `docs/harness/rules/开发流程规范.md` | {范围} | 人工/已验证自动化 |

## 已确认强约束

| 规则 ID | 要求 | 作用范围 | 来源 | 验证方式 |
|---------|------|----------|------|----------|
| {RULE-ID} | {仅填写已确认规范} | {目录/模块} | {项目指令/用户决策} | {测试/CI/人工} |

> 事实、技术债和提议不混入强约束；分别在其唯一事实源记录。提议不参与门禁，存量债务只阻断新增或扩大。

## 按需上下文

| 任务类型 | 读取入口 |
|----------|----------|
| 需求与影响分析 | `docs/harness/skills/需求分析/SKILL.md` |
| 编码实现 | `docs/harness/skills/编码实现/SKILL.md` |
| 代码/高风险评审 | `docs/harness/skills/代码审查/SKILL.md`、`专家评审/SKILL.md` |
| 测试与验证 | 相关测试 playbook 和项目真实命令 |
| Harness 同步 | `harness-sync`（仅在有规范增量时） |

> `docs/harness/skills/` 默认是人工 playbook；只有记录了真实 Router、Hook 或 CI/CD 证据的步骤才属于自动化。
<!-- harness-pack:end -->
