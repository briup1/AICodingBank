# {项目名} AI 编码约束

> 本文件是项目的"宪法"，AI 参与编码前必须首先读取并严格遵守。
> 位置：**项目根目录 `CLAUDE.md`**（草案期暂存于 docs/harness/，启用时融合到项目根，已有根 CLAUDE.md 则融合不覆盖）。
> 状态：草案（待人工确认）
> 生成：harness-bootstrap | 维护：harness-sync（变更见 docs/harness/changes/）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | {待填} |
| 后端 | {待填} |
| 存储/中间件 | {待填} |

## 红线（不可违反）

> 标注：✅ 项目已遵守 | ⚠️ 现状违反（技术债）| ❓ 新提议。确认后标注保留。

1. {示例：金额字段禁止使用浮点数，使用整数最小单位} 🔴 — {理由}（来源：❓）
2. {示例：缓存 Key 必须统一前缀 `{前缀}:`} 🔴 — {理由}（来源：❓）
3. {示例：消息队列消费者必须幂等} 🔴 — {理由}（来源：❓）
4. {示例：异常必须封装为业务异常体系，禁止底层异常透出到 API 层} 🔴 — {理由}（来源：❓）
5. {示例：禁止字段注入，必须使用构造器注入} 🔴 — {理由}（来源：❓）
6. {示例：事务必须显式声明回滚范围} 🔴 — {理由}（来源：❓）
7. {示例：前端必须使用项目选定语法} 🔴 — {理由}（来源：❓）
8. {示例：API 响应必须统一结构 `{code, message, data}`} 🔴 — {理由}（来源：❓）

## 文件索引

| 文件 | 用途 |
|------|------|
| `CLAUDE.md`（本文件，**项目根**） | 宪法：技术栈、红线、文件索引 |
| `docs/harness/agents/owner.md` | 应用 Owner Agent 定义 |
| `docs/harness/rules/工程结构.md` | 项目目录结构与分层规范 |
| `docs/harness/rules/编码规范.md` | 编码标准与约定 |
| `docs/harness/rules/开发流程规范.md` | 开发流水线与流程 |
| `docs/harness/skills/需求分析/SKILL.md` | 需求分析技能 |
| `docs/harness/skills/编码实现/SKILL.md` | 编码实现技能 |
| `docs/harness/skills/代码审查/SKILL.md` | 代码审查技能 |
| `docs/harness/skills/专家评审/SKILL.md` | 专家评审技能 |
| `docs/harness/skills/单元测试编写/SKILL.md` | 单元测试编写技能 |
| `docs/harness/skills/单元测试CI/SKILL.md` | 单元测试 CI 质量门禁技能 |
| `docs/harness/skills/部署验证/SKILL.md` | 部署验证技能 |
| `docs/harness/wiki/业务模型.md` | 业务模型与领域划分 |
| `docs/harness/wiki/接口协议.md` | API 接口协议定义 |
| `docs/harness/wiki/数据模型.md` | 数据库 Schema 与缓存结构 |
| `docs/harness/wiki/领域术语.md` | 领域术语表（统一语言） |
| `docs/harness/changes/` | 变更追踪 |
