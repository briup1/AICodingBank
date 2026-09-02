---
name: hgj-config
version: 1.0.0
description: "HGJ CLI: 配置管理 — 读取、写入和初始化 CLI 配置"
metadata:
  category: "configuration"
  requires:
    bins: ["hgj"]
---

# hgj config — 配置管理

## 配置键名

使用 dot notation 访问嵌套配置:

```bash
hgj config get output.format      # 获取输出格式
hgj config set output.color false  # 禁用颜色
hgj config get api.baseUrl         # 获取 API 地址
```

## 安全规则

- **不要** 在输出中包含 API token 或密码
- 使用 `hgj config get` 获取敏感配置时会自动脱敏
- 配置文件默认存储在 `~/.hgj/config.json`

## 凭证预设

`config.json` 中的 `credentials` 字段用于预存各端点的账号密码，CLI 需要认证时自动读取：

```json
{
  "credentials": {
    "client-prod": { "account": "13800138000", "password": "xxx" },
    "admin-dev": { "account": "admin_user", "password": "xxx" },
    "deploy-prod": { "account": "ops_user", "password": "xxx" }
  }
}
```

- key 格式: `<endpoint>-<env>`，如 `client-prod`、`admin-beta`、`deploy-prod`
- 设置后 `hgj auth login -e deploy` 无需再传 `-a` `-p`
- 设置后 `hgj auth login -e admin --env dev` 无需再传 `-a` `-p`
- `hgj deploy run` 等 API 调用时，Token 过期自动用预设凭证重登
- CLI 参数 `-a` `-p` 优先级高于预设

```bash
# 通过 CLI 设置凭证
hgj config set credentials.deploy-prod.account ops_user
hgj config set credentials.deploy-prod.password your_pwd
hgj config set credentials.admin-dev.account admin_user
hgj config set credentials.admin-dev.password your_pwd
```

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj config get` — 获取配置值

```bash
hgj config get <key> [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<key>` | argument | ✅ | 配置键名 (支持 dot notation, 如 api.baseUrl) | — |
| `--show-sensitive` | option | ❌ | 显示敏感配置值（默认脱敏） | `false` |

### `hgj config set` — 设置配置值

```bash
hgj config set <key> <value>
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<key>` | argument | ✅ | 配置键名 | — |
| `<value>` | argument | ✅ | 配置值 | — |

### `hgj config list` _(aliases: ls)_ — 列出所有配置

```bash
hgj config list [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--show-sensitive` | option | ❌ | 显示敏感配置值（默认脱敏） | `false` |

### `hgj config init` — 初始化配置文件

```bash
hgj config init [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--force` | option | ❌ | 强制覆盖已有配置 | `false` |
<!-- @hgj:auto:end:commands -->
