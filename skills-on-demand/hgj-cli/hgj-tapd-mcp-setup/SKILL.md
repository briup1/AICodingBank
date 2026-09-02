---
name: hgj-tapd-mcp-setup
version: 1.0.0
description: "HGJ TAPD MCP 安装引导 — 帮用户通过 hgj 配置 TAPD MCP 并注册到 Codex / Claude。Triggers on: 安装TAPD MCP, 配置TAPD, tapd setup, tapd mcp setup"
metadata:
  category: "workflow"
  requires:
    bins: ["hgj", "uvx"]
---

# TAPD MCP 安装引导

当用户要安装或修复 TAPD MCP 时，按这个流程执行。不要让用户把 token、password、secret 粘贴到聊天中。

如果用户还没有运行过初始化，优先建议：

```bash
hgj init --ai-profile team
```

该预设会安装 HGJ 基础 skills、TAPD 安装引导、TAPD 工作流，并进入 TAPD MCP 配置、doctor 检查和 Agent 注册流程。

## 标准流程

1. 检查 HGJ MCP 命令是否可用：

```bash
hgj mcp --help
```

2. 检查 TAPD 当前状态：

```bash
hgj mcp status tapd --format json
```

3. 如果配置不完整，引导用户在本地终端运行交互式配置：

```bash
hgj mcp configure tapd
```

交互提示会先确认 `TAPD Base URL`，再要求用户填写 `TAPD Access Token`。提示中会给出 token 生成地址：
`https://www.tapd.cn/personal_settings/index?tab=personal_token`。用户填写 token 后，后续兼容字段会自动使用默认值并跳过。

4. 配置完成后检查：

```bash
hgj mcp doctor tapd --format json
```

5. 如果 doctor 没有缺失项，再注册到用户选择的 Agent：

```bash
hgj mcp install tapd --agent codex
hgj mcp install tapd --agent claude
hgj mcp install tapd --agent codex,claude
```

6. 提醒用户重启 Codex / Claude，使新增 MCP 生效。

7. 重启后让用户在新会话里确认 TAPD 工具可见，再开始执行 TAPD 工作流。

## 失败处理

- `uvx` 不存在：提示先安装 uv，或联系维护者确认环境基线。
- `missing` 中出现配置项：重新运行 `hgj mcp configure tapd`。
- Agent 注册失败：先用 `codex mcp --help` 或 `claude mcp --help` 判断本机是否安装对应 Agent。
- 当前会话看不到 TAPD MCP：重启 Agent；MCP 注册一般不会热加载到已打开会话。

## 禁止事项

- 不要输出 TAPD token、API password。
- 不要把 TAPD 凭证直接写入 `~/.codex/config.toml` 或 `~/.claude.json`。
- 不要使用 shell history 会记录明文的 `hgj config set ...token...` 方式。
