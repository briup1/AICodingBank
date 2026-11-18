# Hindsight 与 OpenViking 对比调研

> 调研时间：2026-10-17
> 口径：Hindsight 官方文档/源码、OpenViking 官方文档/仓库，以及本机当前服务只读状态。未改变配置，未做性能基准或召回质量对比。

## 结论先行

两者都能把 Agent 的历史内容做成“以后可检索的上下文”，所以表面相似；但主语不同：

- **Hindsight 是专门的 Agent 长期记忆引擎**：重点是把对话/文档提炼成事实、实体、关系、观察和可反思的记忆。
- **OpenViking 是 Agent 上下文数据库/虚拟文件系统**：重点是把资源、记忆、技能统一放入 `viking://` 层级空间，按目录、摘要和原文逐步取上下文。

一句话：

```text
Hindsight：让 Agent 记住“关于谁、发生了什么、为什么、后来如何变化”
OpenViking：让 Agent 找到“哪个资源/记忆/技能在什么位置，先读摘要还是原文”
```

## 1. 端到端链路差异

### Hindsight

```text
对话/文档
  -> retain
  -> LLM 提取结构化事实、实体和关系
  -> 写入 memory bank
  -> 后台 consolidation 形成 observations
  -> recall：语义 + 关键词 + 图 + 时间检索
  -> reflect：按 mental model、observation、事实分层取证并生成回答
```

官方依据：

- Main Methods：<https://hindsight.vectorize.io/developer/api/main-methods>
- Retain：<https://hindsight.vectorize.io/developer/retain>
- Retrieval：<https://hindsight.vectorize.io/developer/retrieval>
- Reflect：<https://hindsight.vectorize.io/developer/reflect>

### OpenViking

```text
资源/对话/技能
  -> 解析并写入 VikingFS / RAGFS
  -> 生成目录 L0 摘要、L1 概览、L2 原文
  -> 向量化并写入向量索引
  -> find：直接检索
     或 search：意图分析 -> TypedQuery -> 层级检索 -> 可选 rerank
  -> Agent 先读摘要，再按需读取完整内容
```

会话记忆另外走：

```text
消息
  -> session commit（或启用自动提交）
  -> 归档
  -> 后台提取 profile/preferences/entities/events/experiences 等记忆
  -> 写入用户或 Peer 的 memories 目录
```

官方依据：

- Architecture：<https://docs.openviking.ai/en/concepts/01-architecture>
- Context Layers：<https://docs.openviking.ai/en/concepts/03-context-layers>
- Retrieval：<https://docs.openviking.ai/en/concepts/07-retrieval>
- Session：<https://docs.openviking.ai/en/concepts/08-session>
- Storage：<https://docs.openviking.ai/en/concepts/05-storage>
- Memory：<https://docs.openviking.ai/en/api/16-memory>

## 2. 核心对象不同

| 对比项 | Hindsight | OpenViking |
|---|---|---|
| 核心隔离单位 | memory bank | `viking://` 用户/资源/技能目录空间 |
| 主要记忆形态 | 事实、观察、实体、关系、mental model、directive | Markdown/文件式 memory 类型、资源、技能、会话归档 |
| 是否有图关系 | 有，实体、语义、时间、因果连接 | 主要是目录层级、URI、相关资源关系和向量索引 |
| 是否有时间语义 | 是，时间检索和时间相关性 | 会话归档和元数据有时间，但不是 Hindsight 那种核心时间检索链 |
| 是否有“性格/处置方式” | 有 disposition：skepticism、literalism、empathy 等，影响 reflect | 没有发现同等定位的内置 disposition 机制 |
| 是否有预计算知识 | observations、mental models | L0/L1 摘要与概览 |

## 3. 检索方式不同

### Hindsight：多路记忆证据融合

Hindsight 的 `recall` 同时执行四类策略：

1. semantic
2. BM25/关键词
3. graph traversal
4. temporal

随后使用 RRF 合并，并可用 cross-encoder reranker 再排序。`reflect` 不是简单的 top-k 查询，而是一个有工具的 Agentic Loop：先查 mental models，再查 observations，最后回到原始事实核实，并返回基于哪些记忆的证据。

适合问题：

```text
我之前为什么决定用这个方案？
这个人过去对某功能有什么稳定偏好？
这个项目的决定和哪些实体、事件、因果关系有关？
```

### OpenViking：目录上下文渐进加载

OpenViking 的 `find` 偏简单直接；`search` 可先用 LLM 做意图分析，把一个问题拆为最多若干 TypedQuery，再在指定 context type 的目录范围内做全局检索和层级搜索，最后可选 rerank。

它的关键优势不是“把事实推理得更深”，而是：

```text
先返回目录/文件摘要
  -> Agent 判断哪个目录相关
  -> 再读 L1 概览
  -> 最后只读必要的 L2 原文
```

适合问题：

```text
项目鉴权文档在哪？
哪个 Skill 能处理这个任务？
这个项目的架构说明和相关配置文件是什么？
先给我相关资源摘要，细节需要时再展开。
```

## 4. “记忆自动化”差异

### Hindsight

Hindsight 的典型使用方式是对 Agent 事件调用 `retain`，或者由已经安装的 Agent 插件按会话事件写回。写入后后台会做 observation consolidation。它更偏“事件来了就提炼长期记忆”。

但本机当前配置要特别注意：

```json
{
  "autoSeed": false,
  "gitIngest": "none",
  "retainSessions": false
}
```

因此，本机当前 Hindsight 没有开启自动 Git 摄入，也没有开启会话 transcript 自动写回；不能把“插件已经安装”理解为“所有对话都已经自动保存”。手动调用 Hindsight 工具仍是另一条路径。

### OpenViking

OpenViking 的会话长期记忆需要 `commit`；如果开启自动提交策略，可以由服务根据消息数、token 数等条件触发。`commit` 返回 `accepted` 只表示归档和后台任务已受理，必须继续查询 task 状态并查看 `memory_diff.json`，才能确认记忆实际新增、更新或删除。

这个边界比较明确：

```text
消息进入 session
  != 长期记忆已经完成

commit accepted
  != 记忆提取已经成功
```

## 5. 资料、技能和记忆的覆盖范围

这是两者最实用的分界：

| 需求 | 更贴近的工具 |
|---|---|
| 记住用户长期偏好 | Hindsight / OpenViking 都可；Hindsight 更专注记忆语义，OpenViking 有 preferences 类型 |
| 保存项目文档、代码资料 | OpenViking |
| 管理 Agent Skills 并按需取用 | OpenViking |
| 追踪实体和因果关系 | Hindsight |
| 以“事实证据”回答历史问题 | Hindsight |
| 先摘要、后原文，控制上下文 token | OpenViking |
| 预计算常见问题答案 | Hindsight mental models |
| 统一“资源 + 记忆 + 技能”入口 | OpenViking |
| 作为编程 Agent 的长期记忆后端 | Hindsight 更直接 |

## 6. 存储和部署差异

### Hindsight

官方服务拆分为 API、可选 worker、PostgreSQL 和 Control Plane。API 是核心记忆引擎，状态主要在 PostgreSQL；本地嵌入式路线会带默认本地 Embedding/Reranker，远程模型配置可以减少本地模型依赖。

本机当前已验证：

```text
Hindsight API：127.0.0.1:9077，健康
Control Plane：独立 UI，不自动随 API 启动
```

### OpenViking

OpenViking 使用 VikingFS/RAGFS 保存内容，并用独立向量索引保存检索需要的 URI、向量、摘要和元数据。文件 API 与检索 API 通过 `viking://` 统一访问；可以使用本地文件系统、S3 兼容后端等存储方式。

本机当前已验证：

```text
OpenViking：127.0.0.1:1933，版本 0.5.0，健康
队列：0 pending，0 running，0 errors
模型状态：CLI 报告 VLM/Embedding unknown，未据此推断模型是否本地或远程
```

## 7. 能否互相替代

### OpenViking 替代 Hindsight：部分可以，不能视为等价

如果需求只是：

```text
把历史内容、项目资料、技能放起来
  -> 以后搜索并读取
```

OpenViking 可以覆盖很大一部分。

但如果需求是：

```text
从多次对话中提炼稳定事实
  -> 识别人和项目实体
  -> 建立因果/时间关系
  -> 形成 observations
  -> 按 disposition reflect 并返回证据
```

这不是 OpenViking 的同一抽象，替换后需要自己补提取、合并、图关系、回答编排等能力。

### Hindsight 替代 OpenViking：也只能部分可以

如果只想保存和检索对话记忆，Hindsight 更合适；但它不是文件系统式资源库，也不是以 Skill 和项目目录为中心的渐进式上下文加载系统。把整个项目文档和 Skill 库都塞成 Hindsight 记忆，会失去目录、原文、摘要层级和资源管理能力。

## 8. 是否应该同时使用

可以，但不应让两者同时无边界地摄入同一批对话，否则会形成双写、双重摘要和事实版本不一致。

合理分工可以是：

```text
OpenViking
  -> 项目文档、代码资料、Skills、可复用上下文

Hindsight
  -> 用户偏好、项目决策、历史原因、实体关系、长期经验

Agent
  -> 根据问题类型选择一个主检索入口
```

例如：

```text
“鉴权接口文档在哪？”
  -> OpenViking

“我们为什么不用原来的鉴权方案？”
  -> Hindsight

“按项目规范实现这个接口，并记住这次决策”
  -> OpenViking 取规范 + Hindsight 取历史决策
```

本次没有找到官方提供的 Hindsight ↔ OpenViking 直接连接器，因此上面的组合是架构分工建议，不是已验证的官方集成。

## 9. 针对当前本机的建议

当前不要急着卸载其中一个。先按用途分工：

1. **OpenViking 继续作为资料/Skill/项目上下文库**，因为它已经有本机健康服务和 `viking://` 统一入口。
2. **Hindsight 只保留真正需要的长期记忆**，例如偏好、决策、为什么、实体关系；不要让它自动摄入整个代码仓库和全部会话。
3. 若不想承担 Hindsight 本地 PyTorch/模型，优先把 Hindsight 的 Embedding/Reranker 改成远程，或使用精简后端；这不影响 OpenViking 的职责。
4. 做一次小规模 A/B 验证：同一批 10 条事实、5 个项目文档问题，分别检查“记忆是否被保存、是否找到正确出处、返回 token、时延、第三方调用成本”。不要仅凭产品宣传判断哪个更好。

## 官方来源

### Hindsight

- https://hindsight.vectorize.io/developer/api/main-methods
- https://hindsight.vectorize.io/developer/retain
- https://hindsight.vectorize.io/developer/retrieval
- https://hindsight.vectorize.io/developer/reflect
- https://hindsight.vectorize.io/developer/services
- https://hindsight.vectorize.io/developer/configuration

### OpenViking

- https://docs.openviking.ai/en/concepts/01-architecture
- https://docs.openviking.ai/en/concepts/02-context-types
- https://docs.openviking.ai/en/concepts/03-context-layers
- https://docs.openviking.ai/en/concepts/05-storage
- https://docs.openviking.ai/en/concepts/07-retrieval
- https://docs.openviking.ai/en/concepts/08-session
- https://docs.openviking.ai/en/api/05-sessions
- https://docs.openviking.ai/en/api/16-memory
- https://github.com/volcengine/OpenViking

## 本地验证说明

本轮使用了 OpenViking 本机 CLI 回退路径：

```text
/Users/ziyun/.local/share/openviking/ensure-service.py
/Users/ziyun/.local/share/openviking/venv/bin/ov health
/Users/ziyun/.local/share/openviking/venv/bin/ov status
```

服务已健康，未读取任何具体 `viking://` 资源，也未执行写入操作。当前会话没有使用 OpenViking MCP。Hindsight 只读取了本机配置状态，没有修改配置或启动新服务。
