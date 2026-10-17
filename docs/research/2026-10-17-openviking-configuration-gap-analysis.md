# OpenViking 配置缺口调研

- 调研日期：2026-10-17
- 本机版本：OpenViking 0.5.0、Python 3.12.9、Codex 0.163.0、Node.js 22.22.0、Pi 1.3.0
- 目标：为主要编码、兼顾文档的本机工作流配置 OpenViking，并明确需要用户提供的模型与接入信息。

## 官方事实

OpenViking 服务端配置位于 `~/.openviking/ov.conf`。模型相关角色不是只有一个：

1. **Embedding**：把资源、记忆、技能和查询转换为向量。向量维度必须与现有索引一致；换模型或维度通常需要重建/重索引。
2. **VLM**：负责文档抽象/概览生成、内容理解、会话摘要和长期记忆提取。纯文本场景也使用这个角色；图片、音频、视频等内容需要模型具备相应的媒体能力。
3. **Query Planner**：在带 session 上下文的智能检索中做意图分析和查询改写。未单独配置时可以回退到 VLM，因此不一定需要第三把 LLM Key。
4. **Rerank**：对召回结果二次排序，可选。未配置时仍可使用向量/关键词/混合检索，但结果没有远程重排。

服务端还需要：本地或远程存储、服务监听地址、认证方式、解析器和内存策略。单机本地开发可以使用本地 workspace、loopback 和 dev auth，不需要 S3、VikingDB、租户认证或公网域名。

官方来源：

- Server configuration：<https://docs.openviking.ai/en/configuration/01-server>
- Configure models and services：<https://docs.openviking.ai/en/guides/01-configuration>
- Retrieval：<https://docs.openviking.ai/en/concepts/07-retrieval>
- Context layers：<https://docs.openviking.ai/en/concepts/03-context-layers>
- Sessions and commit：<https://docs.openviking.ai/en/concepts/08-session>
- Codex integration：<https://docs.openviking.ai/en/agent-integrations/04-codex>
- Pi integration：<https://docs.openviking.ai/en/agent-integrations/11-pi>
- MCP clients：<https://docs.openviking.ai/en/agent-integrations/06-mcp-clients>
- OpenCode integration：<https://docs.openviking.ai/en/agent-integrations/10-opencode>

## 本机现状

当前 `~/.openviking/ov.conf` 只有：

```json
{
  "storage": { "workspace": "/Users/ziyun/.openviking/data" },
  "embedding": {
    "dense": {
      "provider": "local",
      "model": "bge-small-zh-v1.5-f16",
      "dimension": 512
    }
  },
  "server": { "host": "127.0.0.1", "port": 1933 }
}
```

已验证：

- 服务运行在 `127.0.0.1:1933`，健康检查通过。
- 本地 Embedding 模型已存在：`/Users/ziyun/.cache/openviking/models/bge-small-zh-v1.5-f16.gguf`。
- `openviking-server doctor`：Embedding PASS；VLM FAIL，原因是没有配置 VLM provider。
- 当前服务没有 `vlm`，也没有 `query_planner`，因此文档抽象/概览、会话摘要、长期记忆提取和 session-aware 意图检索尚未完整可用。
- 当前没有 `rerank`，因此检索可以运行，但没有二次重排。
- `storage` 使用本地文件和本地向量库，适合单机，不需要存储云 AK/SK。
- 服务未设置 `root_api_key`，实际为本机 dev auth；只绑定 loopback，当前风险边界适合本机使用。
- Codex 已有直接 MCP 配置：`http://127.0.0.1:1933/mcp`。这只提供模型主动调用工具，尚不等于 Codex 的自动 recall/capture/commit 生命周期已经接通。
- Pi 当前没有 OpenViking extension；OpenCode 当前没有 OpenViking plugin 或 MCP 配置。

## 建议的最小完整方案

### 模型

保留当前本地 Embedding，不安装 PyTorch：

```text
Embedding = local/bge-small-zh-v1.5-f16, dimension=512
```

配置一套第三方 OpenAI-compatible 模型作为：

```text
VLM = 第三方文本/视觉模型
Query Planner = 先复用 VLM
```

如果该模型只是文本模型：编码项目、Markdown、会话记忆仍可工作；图片、扫描 PDF、音视频理解不完整。若要完整处理这些内容，需要能接受图片/媒体输入的 VLM。

Rerank 建议第二阶段再接入。它不是 OpenViking 基本运行的硬前置；需要单独的 rerank API，不应把普通 chat completion endpoint 当成 rerank endpoint。若第三方平台提供 OpenAI-compatible rerank API，需要确认具体 provider、URL、模型名和协议。

### 主机接入

要实现“自动使用”而不是仅仅“有 MCP 工具”，应分别完成：

- Codex：安装并启用 OpenViking Memory Plugin，审核并信任 hooks；保留现有 MCP 作为补充或由插件管理。
- Pi：安装 OpenViking 官方 Pi extension，配置后自动 recall、turn capture、commit，并注册 MCP 工具。
- OpenCode：安装 OpenViking plugin，并增加原生 `mcp` 配置；确认插件 hooks 已启用。

自动链路是：

```text
启动会话
  → 注入 profile / skills / 项目记忆
  → 每次提问前 recall
  → 每轮捕获对话和工具结果
  → Stop / PreCompact / SessionEnd 触发提交
  → 后台 VLM 生成摘要并提取长期记忆
  → 下一次会话召回
```

`session.commit` 返回 accepted 不代表记忆已经生成；必须等待后台 task 完成并检查 archive 下的 `memory_diff.json`。

## 需要用户提供的信息

### 必填：VLM / Query Planner

如果复用现有公司 OpenAI-compatible 服务，需要提供或确认：

```text
provider：openai 还是其他兼容 provider
api_base：完整 base URL，例如 https://.../v1
api_key：不要直接发在聊天正文，可在确认配置时按安全方式提供
model：模型名
是否支持图片输入：是 / 否 / 不确定
```

Query Planner 默认复用同一模型，不需另一个 Key。若希望分离成本或性能，再额外提供 planner 的 provider、base URL、模型和 Key。

### 必填确认：Embedding

当前已有本地模型，不需要 Key。只需确认：

```text
保留 local/bge-small-zh-v1.5-f16，512 维
```

不建议在已有数据开始写入后随意更换 Embedding 模型或维度。

### 可选：Rerank

如果要启用，请提供：

```text
provider：vikingdb / cohere / openai / litellm / jev
api_base 或 host：按 provider 的接口形式
model 或 model_name：模型名
api_key，或 vikingdb 所需的 AK/SK
```

若暂时没有明确的 Rerank API，建议先不启用，先验证向量检索和自动记忆链路。

### 可选：多主机接入范围

默认建议接入：

```text
Pi + Codex + OpenCode
```

如果只想先做一个验收，建议先 Codex 或 Pi 其中一个，先验证“新会话能召回上一会话结论”，再扩展到其他宿主。

### 可选：认证和访问范围

当前是 loopback + dev auth：

```text
仅本机使用：继续保留，无需 root_api_key
需要局域网/公网访问：必须改为 api_key，并配置 HTTPS/反向代理等安全边界
```

## 当前结论

当前最重要的缺口只有三个：

1. 没有 VLM，所以长期记忆和文档语义层没有完整闭环。
2. 没有 Rerank，所以检索结果没有二次排序；这是可选增强，不是启动硬阻塞。
3. Agent 主机还没有完成 OpenViking 自动生命周期接入；Codex 的裸 MCP 不能替代 hooks/plugin。

当前本地 Embedding、存储、服务端口和 Python 运行环境已经可用，不需要再提供 Embedding Key，也不需要为 OpenViking 额外安装 PyTorch。
