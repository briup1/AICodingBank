# 03 审计项目的 Agent Harness

**什么时候用**：检查已有项目是否为编码 Agent 提供足够的上下文、约束和验证能力
**什么时候别用**：只需完成业务功能或审查某一段具体代码
**产出**：按优先级排序的项目工作环境改进方案
**来源**：用户提供；参考 OpenAI 的 Harness Engineering 文章：https://openai.com/index/harness-engineering/
**状态**：未实测

---

```text
以 OpenAI 的 Harness Engineering 文章为参考，
审计本项目是否为 Codex 提供了可靠的工作环境：
https://openai.com/index/harness-engineering/

重点检查：
- 作为导航入口的 AGENTS.md
- 环境准备和启动命令
- 测试、Lint 与构建检查
- 架构文档和开发约定
- 验收标准和审查清单
- 可复用脚本
- 反馈与验证闭环

提出改进建议，让后续 Codex 更容易理解项目，
也让关键规则能够得到有效执行或校验。

暂时不要修改文件，先输出按优先级排序的方案。
```

## 英文原文

```text
Audit this project for Codex harness using OpenAI's harness engineering article as a reference:
https://openai.com/index/harness-engineering/

Focus on whether the repo gives Codex a reliable project harness: AGENTS.md as a map, setup commands, tests, lint/build
checks, architecture docs, conventions, acceptance criteria, review checklists, reusable scripts, and feedback loops.

Recommend updates that make the project more legible and enforceable for future Codex runs. Do not edit files yet; return a
prioritized plan first.
```
