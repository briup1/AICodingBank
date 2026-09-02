---
name: hgj-create
version: 1.0.0
description: "HGJ CLI: 项目脚手架 — 从模板创建新项目"
metadata:
  category: "scaffolding"
  requires:
    bins: ["hgj"]
---

# hgj create — 项目脚手架

## 可用模板

| 模板 | 说明 |
|------|------|
| `vanilla` | 原生 HTML/CSS/JS |
| `node-ts` | Node.js + TypeScript |
| `hgj-plugin` | HGJ CLI 插件模板 |

## 示例

```bash
hgj create my-app                        # 使用默认模板 (node-ts)
hgj create my-site --template vanilla     # HTML/CSS/JS 项目
hgj create my-plugin --template hgj-plugin # 创建 CLI 插件
hgj create --list                         # 列出所有模板
hgj create my-app --dry-run               # 预览
```

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj create` — 从模板创建新项目

```bash
hgj create [name] [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<name>` | argument | ❌ | 项目名称 | — |
| `-t, --template <template>` | option | ❌ | 项目模板 (vanilla\|node-ts\|hgj-plugin) | `node-ts` |
| `-l, --list` | option | ❌ | 列出可用模板 | — |
<!-- @hgj:auto:end:commands -->
