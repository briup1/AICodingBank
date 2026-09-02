---
name: hgj-admin
version: 1.0.0
description: "HGJ CLI: 管理后台工具 — 权限读取、权限新增、业务 diff 权限提取"
metadata:
  category: "admin"
  requires:
    bins: ["hgj", "git"]
---

# hgj admin — 管理后台权限工具

用于统一管理后台权限资源的读取和新增。CLI 只负责调用后台接口；权限 diff 提取、页面关系分析、父级定位和 JSON 入参构造由 AI 在当前业务仓库中完成。
新增权限时，AI 必须先从业务代码 diff 中提取候选权限，再读取后台权限树，最后只把明确需要新增的资源交给 CLI 写入。

## 安全规则

- 不要输出 `manager-session-id`、cookie、access-token、密码或其它敏感值。
- 新增权限前先读取权限树，并用 `hgj --dry-run admin permissions add...` 或 `add-batch...` 预览将要发送的 payload。
- `--dry-run` 只预览 payload，不写后台；确认无误后才去掉 `--dry-run`。
- 写入后提示用户到后台检查权限树位置和名称，检查通过后再提交业务代码。

## 前置条件

1. 已完成 admin 登录，并缓存了当前用户可访问的应用列表：

```bash
hgj auth login -e admin --env dev
```

2. 知道目标后台应用的 `appKey`（可以从当前用户可访问的应用列表中获取）。

## 推荐 AI 工作流

1. 在业务仓库中确定对比基线，例如用户给的 `master`，或当前迭代分支相对目标分支的 merge-base。
2. 分析 `git diff`(查找的是新增代码中是否存新增页面和按钮，如果新增代码中有用户主动添加的权限以用户添加的为准，没有添加页面或者按钮自行构造) 中新增或修改的权限使用点、路由、菜单和操作按钮，可以参考当前页面的权限，不依赖 CLI 猜测。
3. 调用 `hgj admin permissions list` 获取目标应用现有权限树。
4. 根据页面关系和现有权限树确定每个新增权限的 `parentId`、`resourceType`、`permission` 和 `resourceName`。
5. 先排除权限树中已存在的权限，再生成 `.hgj/admin-permissions.json`。
6. 用 `hgj --dry-run admin permissions add-batch ...` 预览；用户确认后去掉 `--dry-run` 写入后台。

## Diff 提取规则

### 推荐命令

```bash
git diff --name-only <base>...HEAD
git diff --unified=0 <base>...HEAD -- '*.vue' '*.ts' '*.tsx' '*.js' '*.jsx'
```

只从新增或修改后的代码提取候选权限。不要把删除行、diff header、注释、测试 fixture、文档示例里的字符串当成待新增权限。

### 应提取的模式

- 根据代码推测是否是需要提取的权限（Vue 指令，权限函数，新增页面的路由名，页面中的功能操作按钮）
- 可参考现有项目的权限体系

### 不应提取的内容

- 普通文案、i18n、接口路径、资源 URL、埋点字段、CSS class、图标名。
- 已删除的旧权限值，除非同一修改行把它替换成新权限；这种情况只提取新值。
- 现有权限树里已经存在的 `permission`。

### 权限值规范化

- 后台权限树保存的 `permission` 必须和前端最终校验值一致。
- 如果代码已经写完整权限值，保持原值。
- 对同一权限的短写和完整写法去重，保留后台实际需要的完整值。

## 父级定位规则

先读取权限树，再把树 flatten 后按 `permission`、`resourceName`、`resourceLink`、页面路由和相邻按钮做交叉匹配。

- 按钮权限：`resourceType = 1`，`parentId` 应该是所属页面或菜单节点的 `id`。
- 菜单或新页面权限：`resourceType = 0`，`parentId` 应该是上级菜单节点；一级菜单才传 `0`。
- 如果新增按钮在已有页面内，优先找同页面已有按钮的父节点，而不是使用根节点或同名相近节点。
- 如果新增页面对应一个新菜单，先确认是否要新增菜单节点；菜单节点通常需要 `resourceLink`。
- 找不到可信父级时必须问用户确认，不要猜一个 `parentId` 写入。

## 字段规则

### JSON 入参形状

```json
[
  {
    "parentId": 15405,
    "resourceType": 1,
    "permission": "transport:szrbBacksignPdf",
    "resourceName": "水浙人保批单PDF提示",
    "resourceLink": "",
    "extra": "",
    "orderValue": 0,
    "icon": "",
    "status": 1
  }
]
```

`add-batch` 文件可以是数组，也可以是 `{ "resources": [...] }`。单条 `add --json` 传对象；命令行字段用 `--name`，JSON 字段用 `resourceName`。

字段说明：

- `appId`: 不需要写在 JSON 中；CLI 会根据 `--app-key` 和 admin 登录缓存自动补充。
- `parentId`: 父级权限 ID；按钮必须指向所属页面/菜单节点，一级菜单才传 `0`。
- `resourceType`: `0` 表示菜单，`1` 表示按钮。
- `permission`: 后台权限标识，必须和前端最终校验值一致；保险后台注意补齐 `insurance:` 前缀。
- `resourceName`: 权限树展示名称，优先取按钮文案、菜单标题或业务动作名；不确定时问用户。
- `resourceLink`: 菜单可传路由路径；按钮通常传空字符串。
- `extra`、`icon`: 没有明确值时传空字符串。
- `orderValue`: 排序值，默认传 `0`。
- `status`: 启用状态，默认传 `1`。

## 校验清单

写入前必须确认：

- 每个候选权限都来自本次业务 diff 的新增或修改后的权限使用点。
- 每个 `permission` 都已按项目规则规范化，并且不在现有权限树中。
- 每个 `parentId` 都能解释到具体页面/菜单节点。
- `resourceType` 与实际用途一致：页面/菜单为 `0`，按钮/操作为 `1`。
- dry-run 输出的 payload 与计划一致，且用户已确认可以真实写入。

## 常用示例

```bash
hgj admin permissions list --env dev --app-key saas_insurance

hgj admin permissions add \
  --env dev \
  --app-key saas_insurance \
  --parent-id 15405 \
  --type button \
  --permission transport:szrbBacksignPdf \
  --name 水浙人保批单PDF提示

hgj --dry-run admin permissions add-batch \
  --env dev \
  --app-key saas_insurance \
  --file .hgj/admin-permissions.json

hgj admin permissions add-batch --env dev --app-key saas_insurance --file .hgj/admin-permissions.json
```

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj admin permissions list` _(aliases: ls)_ — 获取后台应用权限树

```bash
hgj admin permissions list [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--env <env>` | option | ❌ | admin 环境 (dev\|beta\|prod) | `dev` |
| `--app-key <appKey>` | option | ✅ | 后台应用 appKey | — |

### `hgj admin permissions add` — 新增后台权限资源

```bash
hgj admin permissions add [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--env <env>` | option | ❌ | admin 环境 (dev\|beta\|prod) | `dev` |
| `--app-key <appKey>` | option | ✅ | 后台应用 appKey | — |
| `--json <json>` | option | ❌ | 权限资源 JSON 对象 | — |
| `--parent-id <id>` | option | ❌ | 父级权限 ID，一级菜单可传 0 | — |
| `--type <type>` | option | ❌ | 权限类型: menu/button/0/1 | — |
| `--permission <permission>` | option | ❌ | 权限标识 | — |
| `--name <name>` | option | ❌ | 权限名称 | — |
| `--resource-link <link>` | option | ❌ | 资源链接 | `` |
| `--extra <extra>` | option | ❌ | 扩展字段 | `` |
| `--order-value <value>` | option | ❌ | 排序值 | `0` |
| `--icon <icon>` | option | ❌ | 图标 | `` |
| `--status <status>` | option | ❌ | 状态 | `1` |

### `hgj admin permissions add-batch` — 从 JSON 文件批量新增后台权限资源

```bash
hgj admin permissions add-batch [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--env <env>` | option | ❌ | admin 环境 (dev\|beta\|prod) | `dev` |
| `--app-key <appKey>` | option | ✅ | 后台应用 appKey | — |
| `--file <path>` | option | ✅ | 权限资源 JSON 文件 | — |

## 相关技能

- [hgj-auth](../hgj-auth/SKILL.md)
<!-- @hgj:auto:end:commands -->
