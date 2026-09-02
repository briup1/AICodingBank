---
name: hgj-shared
version: 1.0.0
description: "HGJ CLI: 共享参考 — 认证、全局选项、输出格式、命令语法约定。Triggers on: 全局选项, 输出格式, output format, verbose, dry-run, quiet, format"
metadata:
  category: "shared"
  requires:
    bins: ["hgj"]
---

# hgj — 共享参考

## 安装

```bash
npm install -g @hgj/cli
```

`hgj` 需要在 `$PATH` 上可用。

## 命令语法

```bash
hgj <command> [subcommand] [options]
```

## 全局选项

| 选项 | 短选项 | 说明 | 默认值 |
|------|--------|------|--------|
| `--format <format>` | `-f` | 输出格式: `json`, `table`, `yaml`, `plain` | `json` |
| `--verbose` | `-v` | 详细日志输出 | `false` |
| `--dry-run` | | 预览模式，不执行实际操作 | `false` |
| `--no-color` | | 禁用彩色输出 | `false` |
| `--quiet` | `-q` | 静默模式 (仅显示错误) | `false` |
| `--config <path>` | `-c` | 指定配置文件路径 | 自动发现 |
| `--version` | `-V` | 显示版本号 | |
| `--help` | `-h` | 显示帮助信息 | |

## 输出格式

所有命令默认输出结构化 JSON:

```json
{
  "ok": true,
  "data": { ... }
}
```

错误输出到 stderr:

```json
{
  "ok": false,
  "error": {
    "code": 1,
    "type": "GENERAL_ERROR",
    "message": "错误描述"
  }
}
```

## 退出码

| 退出码 | 含义 |
|--------|------|
| `0` | 成功 |
| `1` | 通用错误 |
| `2` | 用法错误 |
| `3` | 验证错误 |
| `4` | 认证错误 |
| `5` | 网络错误 |
| `6` | 插件错误 |

## 安全规则

- **不要** 在输出中包含 API keys, tokens 或密码
- **始终** 在执行写入/删除操作前确认
- 对破坏性操作优先使用 `--dry-run`

## 配置

配置文件搜索顺序:
1. `--config` 指定的路径
2. 环境变量 `HGJ_*`
3. 项目目录 `.hgjrc.json` / `.hgjrc.yaml`
4. 用户目录 `~/.hgj/config.json`

### 完整配置结构

```jsonc
// ~/.hgj/config.json
{
  "output": { "format": "json", "color": true },
  "api": { "baseUrl": "https://api.company.com", "timeout": 30000 },
  "credentials": {
    "client-prod": { "account": "13800138000", "password": "xxx" },
    "admin-dev": { "account": "admin_user", "password": "xxx" },
    "deploy-prod": { "account": "ops_user", "password": "xxx" }
  },
  "plugins": { "enabled": [], "disabled": [], "paths": [] }
}
```

### 凭证预设 (`credentials`)

按 `<endpoint>-<env>` 预存账号密码，登录和 API 调用时自动使用：
- 不传 `-a` `-p` 时自动读取
- Token 过期时自动重登重试
- CLI 参数优先级高于预设

```bash
hgj config set credentials.deploy-prod.account ops_user
hgj config set credentials.deploy-prod.password your_pwd
hgj config set credentials.admin-dev.account admin_user
hgj config set credentials.admin-dev.password your_pwd
```

## 示例

```bash
# 查看版本
hgj --version

# 初始化配置
hgj config init

# 查看所有配置 (表格模式)
hgj config list --format table

# 设置配置值
hgj config set api.baseUrl https://api.company.com

# 获取配置值
hgj config get api.baseUrl
```
