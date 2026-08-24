# DeepAgents 中文 Skill Pack 生成报告

## 输入与版本

- 框架：DeepAgents
- 目标稳定版：`0.7.8`
- 发布记录：`deepagents==0.7.8`
- 固定源码：`1e261ba201bb1af4dbc5cbc8b6424e709b850ea8`
- 官方文档入口：<https://docs.langchain.com/oss/python/deepagents/overview>
- 官方源码仓库：<https://github.com/langchain-ai/deepagents>
- 生成日期：2026-08-21（Asia/Shanghai）
- 初始输出位置：`.agents/skills/`
- 当前仓库位置：`skills/deepagents-pack/`（通过 `skills.yaml` 安装到 Agent 加载目录）

## 生成内容

| Skill | 独立触发意图 | 主要覆盖 |
|---|---|---|
| `deepagents-getting-started` | 从零采用或设计总体架构 | `create_deep_agent`、middleware stack、checkpointer/store、最小闭环和架构边界 |
| `deepagents-execution-environment` | 设计运行环境和安全边界 | Backend、Composite、sandbox、interpreter、permissions、shell 与失败证据链 |
| `deepagents-context-memory` | 控制上下文增长和持久化记忆 | 上下文分层、offload、skills、thread/user/agent scope、并发写和恢复测试 |
| `deepagents-subagents` | 设计同步/动态/异步委派 | context quarantine、worker 契约、ASGI/HTTP、任务状态、取消和并发 |
| `deepagents-docs` | 核验最新或版本敏感信息 | 官方 `llms.txt`、API/reference、源码 tag、release/changelog 和安全查询流程 |

未单独生成通用 retrieval、streaming、production 或 debugging Skill：它们在当前需求下没有足够清晰的独立触发边界，相关内容保留在领域 Skill 的决策和验证清单中，并由 `deepagents-docs` 负责版本敏感核验。

## 来源与冲突

- 使用官方文档页面、官方 `llms.txt`、官方 API reference、官方 GitHub release/tag 和固定源码提交。
- 未使用 Tavily 或非官方文章；当前官方资料可直接访问且足以支撑目标范围。
- 未发现文档与 0.7.8 固定源码之间的关键冲突。
- `source-manifest.json` 记录了 36 个官方来源、检索时间和 SHA-256；所有 Skill 的 `sources.md` URL 均已关联，未验证 URL 数为 0。

## 验证结果

### 结构与来源

```text
framework-skill-author/scripts/validate_generated_pack.py
→ Skill 数量: 5，错误: 0，警告: 0

skill-creator/scripts/quick_validate.py
→ 5/5 Skill: Skill is valid!

build_source_manifest.py
→ 28 个实际使用来源，0 个未验证 URL
```

### 触发边界矩阵

人工审查每个 Skill 的 2 个应触发、2 个不应触发和 1 个相邻边界请求，共 25 个路由判断：

- 应触发：从零创建 agent、配置 sandbox/权限、设计跨线程记忆、设计 async worker、核对最新 API，各覆盖对应 Skill。
- 不应触发：具体权限问题不触发入门；子 Agent 拓扑不触发执行环境；最新参数不触发稳定上下文 Skill；文档核验不触发子 Agent Skill；总体架构不触发 docs Skill。
- 边界：`skills` 同时属于上下文/记忆域；涉及 Skill 发现与 source precedence 时走 `deepagents-context-memory`，涉及最新字段或行为时再叠加 `deepagents-docs`。

### 最小 E2E / forward test

- 在临时 staging pack 上以未知答案的任务描述进行路由审查，5 个目标任务均能映射到唯一主 Skill。
- 对每个 Skill 运行 frontmatter、目录名、来源文件、URL、占位符和本地链接校验。
- 未运行真实模型、真实 provider、真实 sandbox、外部写操作或生产凭证；这些属于依赖用户环境的人工路径。

## 未覆盖与限制

- 未替用户安装 `deepagents`、配置模型 API key 或部署 LangSmith/sandbox。
- 未验证具体 provider 的实时价格、配额、区域和服务可用性。
- 未把所有 API 参数复制进 Skill；调用前按 `deepagents-docs` 查询官方 reference。
- `model=None` 的兼容路径已标记弃用；升级到 1.0 时应重新审查默认模型和相关 API。

## 刷新方式

当 DeepAgents 发布新版本或官方文档改变时，重新运行来源发现并比较 manifest：

```bash
python3 skills/framework-skill-author/scripts/discover_sources.py \
  --framework DeepAgents \
  --docs https://docs.langchain.com/oss/python/deepagents/overview \
  --repo https://github.com/langchain-ai/deepagents \
  --version <目标版本> \
  --output /tmp/deepagents-sources.json
```

然后只重读受影响领域 Skill，更新对应 `sources.md`、manifest 和本报告；不要覆盖用户对未受影响 Skill 的人工修改。
