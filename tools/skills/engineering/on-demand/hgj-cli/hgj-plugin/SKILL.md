---
name: hgj-plugin
version: 1.1.0
description: "HGJ CLI: 插件管理 — 查看、搜索插件"
metadata:
  category: "management"
  requires:
    bins: ["hgj"]
---

# hgj plugin — 插件管理

## 插件来源

| 来源 | 说明 |
|------|------|
| 内置插件 | config, plugin, auth, create, git, env, skills, deploy |
| 项目依赖 | 当前项目 `node_modules` 下的 `@hgj/plugin-*` 或 `hgj-plugin-*` |
| 全局安装 | 全局安装目录下的 `@hgj/plugin-*` 或 `hgj-plugin-*` |
| 自定义路径 | config.plugins.paths 中指定 |
| 远程 registry | Nexus 私有仓库上的 `@hgj/plugin-*` 包 |

## 搜索远程插件

```bash
# 搜索所有可用的远程插件
hgj plugin search

# 按关键词过滤
hgj plugin search tapd
```

未安装的插件会标记 `installed: false`，使用 `pnpm add <name>` 安装。

## 开发自定义插件

```bash
hgj create my-plugin --template hgj-plugin
```

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj plugin list` _(aliases: ls)_ — 列出所有已注册插件

```bash
hgj plugin list
```

### `hgj plugin search` — 搜索远程 registry 上的可用插件

```bash
hgj plugin search [keyword]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<keyword>` | argument | ❌ | 搜索关键词 | — |
<!-- @hgj:auto:end:commands -->
