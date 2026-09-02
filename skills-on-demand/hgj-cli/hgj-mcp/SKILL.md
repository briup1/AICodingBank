---
name: hgj-mcp
version: 1.0.0
description: "HGJ CLI: MCP 服务管理 — 配置 TAPD MCP 并注册到 Codex / Claude"
metadata:
  category: "configuration"
  requires:
    bins: ["hgj", "uvx"]
---

# hgj mcp — MCP 服务管理

用于把内部 MCP 服务接入 AI Agent。TAPD 配置统一保存在 `~/.hgj/config.json`，Codex / Claude 只注册 `hgj mcp run tapd`，避免 token 分散在多个 Agent 配置中。

## 安全规则

- 不要在对话、日志、命令行参数中展示 TAPD token、password、secret。
- 配置 TAPD 凭证时优先运行交互式命令：`hgj mcp configure tapd`。
- `hgj config get/list` 默认会脱敏敏感字段；不要要求用户使用 `--show-sensitive`，除非用户明确要本地查看。
- 安装到 Agent 前先用 `hgj mcp status tapd --format json` 或 `hgj mcp doctor tapd --format json` 检查状态。

## 常用流程

```bash
hgj mcp configure tapd
hgj mcp status tapd --format json
hgj mcp install tapd --agent codex,claude
hgj mcp doctor tapd --format json
```

## TAPD MCP 使用说明

### `hgj mcp configure tapd`

交互式写入 TAPD MCP 配置到 `~/.hgj/config.json`。
流程会先确认 `TAPD Base URL`，随后询问 `TAPD Access Token`，提示中包含生成地址：
`https://www.tapd.cn/personal_settings/index?tab=personal_token`。用户填写 Access Token 后会使用默认 TAPD API 地址并跳过后续兼容字段。

### `hgj mcp install tapd`

注册 TAPD MCP 到 Codex / Claude。

```bash
hgj mcp install tapd --agent codex
hgj mcp install tapd --agent claude
hgj mcp install tapd --agent codex,claude
```

### `hgj mcp run tapd`

供 MCP 客户端以 stdio 方式启动 TAPD MCP。一般不要手动运行。

### `hgj mcp status tapd`

查看配置是否完整、是否已在 HGJ 配置中启用。

### `hgj mcp doctor tapd`

检查 `uvx` 是否可用，并返回 TAPD 配置缺失项。输出不包含敏感值。

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj mcp configure` — 交互式配置 MCP 服务

```bash
hgj mcp configure <server>
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<server>` | argument | ✅ | MCP 服务名，目前支持 tapd | — |

### `hgj mcp install` — 将 MCP 服务注册到 Codex / Claude

```bash
hgj mcp install <server> [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<server>` | argument | ✅ | MCP 服务名，目前支持 tapd | — |
| `--agent <agent>` | option | ❌ | 目标 AI Agent: codex \| claude \| codex,claude | `codex,claude` |

### `hgj mcp remove` — 从 Codex / Claude 移除 MCP 服务注册

```bash
hgj mcp remove <server> [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<server>` | argument | ✅ | MCP 服务名，目前支持 tapd | — |
| `--agent <agent>` | option | ❌ | 目标 AI Agent: codex \| claude \| codex,claude | `codex,claude` |

### `hgj mcp status` — 查看 MCP 服务配置状态

```bash
hgj mcp status <server>
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<server>` | argument | ✅ | MCP 服务名，目前支持 tapd | — |

### `hgj mcp doctor` — 检查 MCP 服务运行依赖和配置

```bash
hgj mcp doctor <server>
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<server>` | argument | ✅ | MCP 服务名，目前支持 tapd | — |

### `hgj mcp run` — 启动 MCP 服务进程（供 AI Agent stdio 调用）

```bash
hgj mcp run <server>
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<server>` | argument | ✅ | MCP 服务名，目前支持 tapd | — |
<!-- @hgj:auto:end:commands -->
