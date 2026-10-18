---
name: hgj-git
version: 2.0.0
description: "HGJ CLI: Git 工作流增强 — 规范化提交、仓库信息查看、GitLab 项目管理"
metadata:
  category: "development"
  requires:
    bins: ["hgj", "git"]
---

# hgj git — Git 工作流增强 + GitLab 集成

## 提交规范 (element-plus 风格)

格式: `type(scope): message`

```bash
hgj git commit --type feat --scope core --message "添加缓存模块"
# → feat(core): 添加缓存模块

hgj git commit -t fix -m "修复配置加载"
# → fix: 修复配置加载

hgj git commit -t docs -s readme -m "更新安装说明" --all
# → git add -A && git commit -m "docs(readme): 更新安装说明"
```

---

## GitLab 集成

搜索、克隆、查看公司私有 GitLab 项目。需先在 `~/.hgj/config.json` 配置：

```json
{
  "gitlab": {
    "baseUrl": "https://gitlab.company.com",
    "token": "glpat-xxxxxxxxxxxx"
  }
}
```

通过 `hgj config set` 设置：

```bash
hgj config set gitlab.baseUrl https://gitlab.company.com
hgj config set gitlab.token glpat-xxxxxxxxxxxx
```

**Token 获取**: GitLab → Settings → Access Tokens → 勾选 `read_api` 权限 → 生成

---

## AI Agent 调用示例

### 场景 1: 找到并克隆一个项目
```bash
hgj git search my-project --format json
# → 返回匹配项目列表，取 path 字段

hgj git clone group/my-project --format json
# → SSH 克隆到当前目录
```

### 场景 2: 查看项目详情和分支
```bash
hgj git project group/my-project --branches --format json
# → 返回项目信息 + 分支列表
```

### 场景 3: 不知道项目完整路径
```bash
hgj git search keyword --format json
# → 模糊搜索，返回 id/path/name/url
```

---

## 命令实现细节

### `hgj git search` — 搜索 GitLab 项目

调用 `GET /api/v4/projects?search=<keyword>`，返回匹配项目列表。

### `hgj git clone` — 克隆 GitLab 项目

1. 调用 GitLab API 获取项目详情（支持路径 `group/name` 或数字 ID）
2. 从返回数据中取 `ssh_url_to_repo` 或 `http_url_to_repo`
3. 执行 `git clone <url> [directory]`

默认使用 SSH，加 `--https` 切换为 HTTPS。

### `hgj git project` — 查看项目详情

调用 `GET /api/v4/projects/:id`，加 `--branches` 时额外调用分支列表 API。

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj git info` — 查看当前 Git 仓库信息

```bash
hgj git info
```

### `hgj git commit` — 规范化提交 (element-plus 风格: type(scope): message)

```bash
hgj git commit [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `-t, --type <type>` | option | ✅ | 提交类型 (feat\|fix\|docs\|style\|refactor\|perf\|test\|build\|ci\|chore\|revert) | — |
| `-s, --scope <scope>` | option | ❌ | 影响范围 (如 cli, core, plugin) | — |
| `-m, --message <message>` | option | ✅ | 提交信息 | — |
| `--all` | option | ❌ | 自动 git add -A | `false` |

### `hgj git log` — 查看最近提交记录

```bash
hgj git log [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `-n, --count <count>` | option | ❌ | 显示条数 | `10` |

### `hgj git types` — 列出所有提交类型 (element-plus 规范)

```bash
hgj git types
```

### `hgj git search` — 搜索 GitLab 项目

```bash
hgj git search <keyword> [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<keyword>` | argument | ✅ | 搜索关键词 | — |
| `--page <page>` | option | ❌ | 页码 | `1` |
| `--per-page <n>` | option | ❌ | 每页条数 | `20` |

### `hgj git clone` — 克隆 GitLab 项目 (按路径或 ID)

```bash
hgj git clone <project> [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<project>` | argument | ✅ | 项目路径 (group/name) 或 ID | — |
| `--https` | option | ❌ | 使用 HTTPS (默认 SSH) | `false` |
| `-d, --directory <dir>` | option | ❌ | 目标目录 | — |

### `hgj git project` — 查看 GitLab 项目详情

```bash
hgj git project <id> [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<id>` | argument | ✅ | 项目 ID 或路径 (group/name) | — |
| `--branches` | option | ❌ | 同时列出分支 | `false` |
<!-- @hgj:auto:end:commands -->
