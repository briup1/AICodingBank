---
name: hgj-deploy
version: 1.0.0
description: "HGJ CLI: 项目发布与 dev/beta 网关本地代理 — deploy run / proxy set-local / restore"
metadata:
  category: "deployment"
  requires:
    bins: ["hgj", "git"]
---

# hgj deploy — 项目发布管理

迁移自 `hgj-ops` CLI，提供前端项目构建和发布到公司内部发布平台（伏羲/Next-Manage）的完整功能。

## 发布平台说明

本命令对接的是公司内部项目发布系统，后端 API 为 `mixmicro-ops-api`：
- **国内平台**: `http://next-manage.hgj.net`
- **海外平台 (伏羲)**: `http://fuxi.globalhgj.com`

---

## 前置条件

以下任一方式完成 deploy 端认证即可：

```bash
# 方式 1: 手动登录
hgj auth login -e deploy -a <用户名> -p <密码>

# 方式 2: 在 config.json 中预设凭证（推荐）
# 设置后无需手动登录，Token 过期自动重登
hgj config set credentials.deploy-prod.account <用户名>
hgj config set credentials.deploy-prod.password <密码>
```

凭证优先级: CLI 参数 `-u` `-p` > `config.json` credentials > 已保存的 auth session。

---

## 命令实现细节

### `hgj deploy run` — 发布项目

```bash
hgj deploy run [env] [project] [branch] [options]
```

**将指定项目的指定分支发布到目标环境**。

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `env` | positional | 目标环境: `dev` / `beta` | `dev` |
| `project` | positional | 项目名称 (发布平台上注册的 projectName) | 自动从 `git remote origin` 获取 |
| `branch` | positional | 要发布的 Git 分支名 | 当前 `git rev-parse --abbrev-ref HEAD` |

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--global` | 使用海外伏羲平台 | `false` |
| `-u, --username <username>` | 覆盖发布平台用户名 | 来自已保存的 auth 会话 |
| `-p, --password <password>` | 覆盖发布平台密码 | 来自已保存的 auth 会话 |
| `--dry-run` | 仅预览，不实际执行发布 | `false` |

#### 内部执行流程

```
1. 登录发布平台
   POST {baseUrl}/mixmicro-ops-api/login?username={username}
   Headers: { timestamp, content-type: application/json }
   Body: AES-ECB(timestamp + MD5(password) + timestamp, MD5(Base64(username)))
   → 获取 authorization token

2. 查询项目 ID
   GET {baseUrl}/mixmicro-ops-api/v1/{env}/service-configs?configName={projectName}
   Headers: { authorization: token }
   → 从 records[] 中匹配 projectName 获取 id

3. 触发构建发布
   POST {baseUrl}/mixmicro-ops-api/v1/{env}/service-configs/{id}/buildAndPublish/{branch}?lane=&mergeStatus=
   Headers: { authorization: token, content-type: application/json;charset=UTF-8 }
   → 返回 { id: buildId, status: buildStatus }

4. 输出日志链接
   http://filecdn.hgj.com/zsh/log.html?auth={token}&env={env}&buildId={buildId}
```

#### 自动重登机制

当步骤 2 或 3 返回 **HTTP 401** 时：
1. 自动从 config 凭证预设或已保存的 session 中获取账号密码
2. 重新执行步骤 1 登录获取新 token
3. 用新 token 重试失败的请求
4. 无需用户手动介入

#### 项目名自动检测

如果不指定 `project` 参数，自动执行：
```bash
git config --get remote.origin.url
# 提取最后一级路径名，去除 .git 后缀
# 例如: git@github.com:company/my-project.git → my-project
```

#### 分支名自动检测

如果不指定 `branch` 参数，自动执行：
```bash
git rev-parse --abbrev-ref HEAD
# 返回当前所在分支名
```

#### 安全限制

- **`prod` 环境禁止使用 CLI 发布**，会直接拒绝执行并提示使用伏羲平台

---

### `hgj deploy proxy set-local` — 设置 dev/beta 网关本地代理

```bash
hgj deploy proxy set-local [env] [project] --host <本机IP> --port <本地端口>
```

**将指定环境的网关服务流量切到本机节点**。常用于把 dev 或 beta 环境服务代理到本地调试。

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `env` | positional | 目标环境: `dev` / `beta` | `dev` |
| `project` | positional | 项目名 | 自动从 `git remote origin` 获取 |
| `--host <ip>` | option | 本机 IP；不传时自动检测，多个候选时报错 | 自动检测 |
| `--port <port>` | option | 本地服务端口 | 必填 |
| `--service-name <name>` | option | 网关服务名；不传时唯一确认或交互选择 | 自动确认/交互选择 |
| `--cluster-name <name>` | option | 网关集群名；不传时唯一确认或交互选择 | 自动确认/交互选择 |
| `-u, --username <username>` | option | 发布平台用户名 | 来自 deploy 凭证 |
| `-p, --password <password>` | option | 发布平台密码 | 来自 deploy 凭证 |

#### 内部执行流程

```
1. 查询网关集群
   GET {base}/mixmicro-ops-api/v1/{env}/gateway-clusters/page-list?clusterName=&env={env}&pageSize=20&pageIndex=1
   → 用户传 --cluster-name 时精确匹配；否则唯一确认或交互选择

2. 查询集群服务
   GET {base}/mixmicro-ops-api/v1/clusters/{clusterId}/services/page-list?name={serviceName}&group=&pageSize=10&pageIndex=1&id={clusterId}
   → 用户传 --service-name 时精确匹配；否则根据 project 唯一确认或交互选择

3. 查询服务详情
   GET {base}/mixmicro-ops-api/v1/services/{serviceId}
   → 读取 nodes

4. 保存恢复快照
   写入 ~/.hgj/cache，保存 set-local 前的 service nodes

5. 更新 nodes
   本机 host 节点 weight=1，其他节点 weight=0；本机节点不存在时追加

6. 发布配置
   PUT {base}/mixmicro-ops-api/v1/services/{serviceId}/publish
```

`--dry-run` 会查询并返回变更计划，但不会写快照、不会 PUT、不会 publish。

### `hgj deploy proxy restore` — 恢复网关节点配置

```bash
hgj deploy proxy restore [env] [project]
```

从 `set-local` 保存的本地快照恢复 `nodes`，然后发布配置。恢复时会先读取当前服务详情，只替换 `nodes`，避免覆盖平台上后续变更的其他服务元数据。

如果找不到快照会失败，不会猜测默认权重。

---

### `hgj deploy copy` — 复制项目信息到剪贴板

```bash
hgj deploy copy
```

在 Git 仓库目录下执行。自动收集以下信息并复制到系统剪贴板（macOS pbcopy）：

```
项目名称： <git remote 仓库名>
分支：<当前分支>
提交信息： <最新 commit message>
```

**使用场景**：
- 在群内通知同事已发布某个版本
- 提交发布记录时快速获取项目信息
- 配合发布流程生成发布日志

**内部逻辑**：
1. `git config --get remote.origin.url` → 提取仓库名
2. `git rev-parse --abbrev-ref HEAD` → 当前分支
3. `git log -1 --pretty=format:"%s"` → 最新提交信息
4. `echo "..." | pbcopy` → 复制到剪贴板 (macOS)

**返回值**：
```json
{
  "ok": true,
  "data": {
    "projectName": "my-project",
    "branch": "feature/xxx",
    "latestCommit": "feat(core): add new feature",
    "copied": true,
    "message": "已复制到剪贴板"
  }
}
```

---

## 环境配置

### 国内 vs 海外

| 模式 | BaseURL | 触发方式 |
|------|---------|----------|
| 国内 (默认) | `http://next-manage.hgj.net` | 不加 `--global` |
| 海外 (伏羲) | `http://fuxi.globalhgj.com` | 加 `--global` |

### 海外环境名映射

使用 `--global` 时，环境名会自动映射为海外格式：

| 输入 env | 实际 API env | 说明 |
|----------|-------------|------|
| `dev` | `overseaDev` | 海外开发环境 |
| `beta` | `overseaBeta` | 海外测试环境 |
| `prod` | `overseaProd` | 海外生产环境 (CLI 禁止) |

不使用 `--global` 时，env 直接传给 API，不做映射。

### 密码加密方式

Deploy 平台使用 **AES-ECB + MD5** 加密，不同于 Whale 平台的 RSA：

```
1. MD5(password) → hashedPwd
2. 拼接: timestamp + hashedPwd + timestamp → plaintext
3. Base64(username) → key
4. AES-ECB(plaintext, MD5(key)) → ciphertext
5. 请求头附带 timestamp 字段（用于防重放攻击）
```

---

## API 接口详情

| 接口 | Method | URL 模板 | 用途 |
|------|--------|----------|------|
| 登录 | POST | `{base}/mixmicro-ops-api/login?username={user}` | 获取 authorization |
| 项目列表 | GET | `{base}/mixmicro-ops-api/v1/{env}/service-configs?configName={name}` | 查询 projectId |
| 发布 | POST | `{base}/mixmicro-ops-api/v1/{env}/service-configs/{id}/buildAndPublish/{branch}` | 触发构建 |
| 网关集群 | GET | `{base}/mixmicro-ops-api/v1/{env}/gateway-clusters/page-list` | 查询网关集群 |
| 网关服务列表 | GET | `{base}/mixmicro-ops-api/v1/clusters/{clusterId}/services/page-list` | 查询网关服务 |
| 网关服务详情 | GET | `{base}/mixmicro-ops-api/v1/services/{serviceId}` | 获取 upstream nodes |
| 更新网关服务 | PUT | `{base}/mixmicro-ops-api/v1/services/{serviceId}` | 修改 upstream nodes |
| 发布网关服务 | PUT | `{base}/mixmicro-ops-api/v1/services/{serviceId}/publish` | 发布网关配置 |
| 日志 | GET | `http://filecdn.hgj.com/zsh/log.html?auth={token}&env={env}&buildId={id}` | 查看构建日志 |

---

## AI Agent 调用示例

### 场景 1: 发布当前项目到 dev 环境

```bash
# 如果 config.json 中已配置 credentials.deploy-prod，直接执行:
hgj deploy run dev --format json

# 如果未配置凭证预设:
hgj auth login -e deploy -a username -p password
hgj deploy run dev --format json

# 返回: { buildId, status, logUrl }
```

### 场景 2: 发布指定项目的指定分支

```bash
hgj deploy run beta my-frontend-app feature/new-ui --format json
```

### 场景 3: 发布海外项目

```bash
# 海外 dev 环境（实际调用 overseaDev）
hgj deploy run dev --global --format json
```

### 场景 4: 预览发布操作

```bash
hgj deploy run dev --dry-run --format json
# 返回: { dryRun: true, env, project, branch, message }
# 不实际执行任何请求
```

### 场景 5: 获取项目信息用于沟通

```bash
hgj deploy copy --format json
# 返回: { projectName, branch, latestCommit, copied }
```

### 场景 6: 把 dev 网关服务代理到本机

```bash
hgj deploy proxy set-local dev track-vgm-back --host 192.168.34.231 --port 8091 --format json
# 返回: { env, project, serviceName, clusterId, serviceId, host, port, changedNodes, published, snapshotKey }
```

### 场景 7: 恢复 set-local 前的网关节点

```bash
hgj deploy proxy restore dev track-vgm-back --format json
# 返回: { env, project, serviceName, clusterId, serviceId, restored, published, snapshotKey }
```

### 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `prod 环境请使用伏羲平台发布` | 尝试发布到 prod | 改用 dev 或 beta |
| `请先登录` | 未找到 deploy 凭证 | `hgj auth login -e deploy -a ... -p ...` |
| `未找到项目: xxx` | projectName 不在发布平台 | 检查项目名是否正确注册 |
| `未找到网关集群` | env 下没有指定 clusterName | 检查 `--cluster-name` 或平台配置 |
| `未找到本地代理快照` | restore 前没有执行过 set-local | 先执行 set-local，或手动在平台恢复 |
| `Token 过期，自动重新登录...` | 401 自动恢复 | 无需操作，自动处理 |
| `发布失败: xxx` | 400 业务错误 | 查看 message 排查原因 |

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj deploy run` — 发布项目到指定环境

```bash
hgj deploy run [env] [project] [branch] [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<env>` | argument | ❌ | 目标环境 (dev\|beta) | — |
| `<project>` | argument | ❌ | 项目名 (默认取 git remote) | — |
| `<branch>` | argument | ❌ | 分支名 (默认取当前分支) | — |
| `--global` | option | ❌ | 海外环境 | `false` |
| `-u, --username <username>` | option | ❌ | 发布平台用户名 | — |
| `-p, --password <password>` | option | ❌ | 发布平台密码 | — |

### `hgj deploy proxy set-local` — 将 dev/beta 网关服务代理到本机 IP

查询目标环境的网关集群与服务配置，保存当前 nodes 快照后，将本机节点权重设为 1、其他节点权重设为 0，并发布配置。

```bash
hgj deploy proxy set-local [env] [project] [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<env>` | argument | ❌ | 目标环境 (dev\|beta) | — |
| `<project>` | argument | ❌ | 项目名 (默认取 git remote) | — |
| `--host <ip>` | option | ❌ | 本机 IP，不传则自动检测 | — |
| `--port <port>` | option | ✅ | 本地服务端口 | — |
| `--service-name <name>` | option | ❌ | 网关服务名；不传时自动确认或交互选择 | — |
| `--cluster-name <name>` | option | ❌ | 网关集群名；不传时自动确认或交互选择 | — |
| `-u, --username <username>` | option | ❌ | 发布平台用户名 | — |
| `-p, --password <password>` | option | ❌ | 发布平台密码 | — |

**示例**

```bash
hgj deploy proxy set-local dev track-vgm-back --host 192.168.34.231 --port 8091 --format json
hgj deploy proxy set-local beta --port 3000 --dry-run --format json
```

### `hgj deploy proxy restore` — 恢复 set-local 前保存的网关服务节点配置

读取 set-local 保存的本地快照，将快照中的 nodes 恢复到当前服务配置上，并发布配置。

```bash
hgj deploy proxy restore [env] [project] [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<env>` | argument | ❌ | 目标环境 (dev\|beta) | — |
| `<project>` | argument | ❌ | 项目名 (默认取 git remote) | — |
| `--service-name <name>` | option | ❌ | 网关服务名；不传时自动确认或交互选择 | — |
| `--cluster-name <name>` | option | ❌ | 网关集群名；不传时自动确认或交互选择 | — |
| `-u, --username <username>` | option | ❌ | 发布平台用户名 | — |
| `-p, --password <password>` | option | ❌ | 发布平台密码 | — |

**示例**

```bash
hgj deploy proxy restore dev track-vgm-back --format json
hgj deploy proxy restore beta --dry-run --format json
```

### `hgj deploy copy` — 复制当前项目信息到剪贴板

```bash
hgj deploy copy
```

## 相关技能

- [hgj-auth](../hgj-auth/SKILL.md)
<!-- @hgj:auto:end:commands -->
