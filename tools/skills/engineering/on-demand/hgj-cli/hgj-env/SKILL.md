---
name: hgj-env
version: 1.0.0
description: "HGJ CLI: 环境管理 — 环境变量查看、健康检查"
metadata:
  category: "environment"
  requires:
    bins: ["hgj"]
---

# hgj env — 环境管理

## 安全规则

- 包含 TOKEN/SECRET/KEY 的变量值会自动脱敏
- `hgj env list` 默认仅显示 `HGJ_*` 和 `NODE_ENV`
- 使用 `--all` 显示所有环境变量

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj env list` _(aliases: ls)_ — 列出当前 HGJ 相关环境变量

```bash
hgj env list [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--all` | option | ❌ | 显示所有环境变量 (不仅限 HGJ_*) | `false` |

### `hgj env check` — 检查环境健康状态

```bash
hgj env check
```

### `hgj env init` — 在当前目录创建 .env 文件模板

```bash
hgj env init [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--force` | option | ❌ | 覆盖已有 .env 文件 | `false` |
<!-- @hgj:auto:end:commands -->
