---
name: hgj-auth
version: 2.0.0
description: "HGJ CLI: 多端鉴权管理 — 客户端/后台/发布平台统一认证，获取后端鉴权信息、后端请求头、access-token 和 whale-identity"
metadata:
  category: "authentication"
  requires:
    bins: ["hgj"]
---

# hgj auth — 多端鉴权管理

管理 client (客户端)、admin (后台)、deploy (发布平台) 三端认证。

**【重要】这是调用公司任何业务 API 的前置条件！**

## 覆盖产品范围

登录 client/admin 后可访问以下产品 API：
- **国内舱单**：上海舱单、青岛舱单、天津舱单、大连舱单、深圳舱单、南沙舱单、厦门舱单
- **海外舱单**：ICS2、ENS、MPCI、AMS、HBL、ISF、EM&ACI、AFR
- **VGM**：VGM 发送平台、VGM 申报
- **货运保险**：货运保险申报
- **订舱服务**：全口岸订舱、SPOT 电商、AI 订舱
- **报关拖车**：在线报关、HAI 关通、集卡派车、E集运
- **国内进口**：青岛换单、青岛押箱、上海换单、上海清关
- **海外目的港**：美国目的港、加拿大目的港
- **美金快付**：海付通
- **工具类**：订箱宝、货车定位、船舶定位
- **AI 相关**：AI 询报价

---

## 三端差异

| 特性 | client (客户端) | admin (后台) | deploy (发布平台) |
|------|----------------|-------------|-------------------|
| 环境 | dev / beta / prod | dev / beta / prod | 仅 prod |
| 登录方式 | 密码 + 微信二维码 | 密码 | 密码 |
| Token Header | `access-token` | `manager-session-id` | `authorization` |
| 登录后流程 | 选择企业 → accessToken | doLoginV2 → manager-session-id | 直接获取 auth |

---

## 标准登录流程

### 凭证预设（免手动输入）

在 `~/.hgj/config.json` 中预设凭证后，登录和 API 调用时无需手动传账号密码：

```json
{
  "credentials": {
    "client-prod": { "account": "13800138000", "password": "xxx" },
    "admin-prod": { "account": "admin_user", "password": "xxx" },
    "admin-beta": { "account": "admin_user", "password": "xxx" },
    "admin-dev": { "account": "admin_user", "password": "xxx" },
    "deploy-prod": { "account": "ops_user", "password": "xxx" }
  }
}
```

- key 格式: `<endpoint>-<env>`
- 设置后 `hgj auth login -e deploy` 不传 `-a` `-p` 即可自动登录
- 设置后 `hgj auth login -e admin --env dev` 不传 `-a` `-p` 即可自动登录
- CLI 参数 `-a` `-p` 优先级高于预设

### 流程 A: 密码登录 (三端通用)

```
1. hgj auth login -e <endpoint> --env <env> -a <账号> -p <密码>
   ↓
2. 如果返回 status=needChooseEnterprise (client)
   → hgj auth enterprise choose <enterpriseId>
   ↓
3. 登录完成，Token 已保存
```

### 流程 B: 微信二维码登录 (仅 client)

```
1. hgj auth qrcode --env <env>
   → 返回 qrCodeUrl + sessionId
   → 展示二维码给用户扫描
   ↓
2. hgj auth qrcode-check --session <sessionId>
   → 轮询此命令检查状态 (建议每 2 秒)
   ↓
3. 状态流转:
   - pending:  等待扫码 → 继续轮询
   - scanned:  已扫码等待确认 → 继续轮询
   - needChooseEnterprise: → hgj auth enterprise choose <id>
   - success:  登录完成
   - expired:  过期 → 重新 hgj auth qrcode
   - needRegister: 新用户需先注册 → 改用密码登录
   ↓
4. 二维码有效期：60 秒
```

### 流程 C: deploy 登录后发布

```
1. hgj auth login -e deploy -a <用户名> -p <密码>
   ↓
2. hgj deploy run <env> [project] [branch]
   → 自动使用已保存的 Token
   → 401 时自动重新登录
```

---

## 命令实现细节

### `hgj auth login` — 登录

```bash
hgj auth login -e <endpoint> [--env <env>] -a <account> -p <password> [--global]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `-e, --endpoint` | 端点: `client` / `admin` / `deploy` | ✅ |
| `--env` | 环境: `dev` / `beta` / `prod`（默认 prod） | ❌ |
| `-a, --account` | 账号（手机号/邮箱/用户名），不传则从 config 凭证预设读取 | ❌ |
| `-p, --password` | 密码（明文，自动加密），不传则从 config 凭证预设读取 | ❌ |
| `--global` | 海外环境（仅 deploy） | ❌ |
| `--dry-run` | 预览模式 | ❌ |

**client 密码加密**: RSA 公钥加密，自动处理
**admin 密码加密**: AES-ECB + MD5，自动处理，成功后保存 `manager-session-id`
**deploy 密码加密**: AES-ECB + MD5，自动处理

**账号格式自动识别**:
- 11位数字 → 手机号登录 (loginType=0)
- 含@符号 → 邮箱登录 (loginType=1)

**返回值**:
- `status=4`: 直接登录成功，Token 已保存
- `status=needChooseEnterprise`: 需要选择企业（见下方 enterprise 命令）
- admin 登录成功后保存 `manager-session-id` 到 `~/.hgj/auth/admin-<env>.json`

---

### `hgj auth qrcode` — 微信扫码登录 (仅 client)

```bash
hgj auth qrcode [--env <env>]
```

**返回值**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `qrCodeUrl` | string | 微信二维码 URL |
| `sessionId` | string | 会话 ID (用于 qrcode-check) |

**注意**: `qrCodeUrl` 是微信内部链接，不能直接浏览器访问。需要渲染为二维码图片后扫描。

---

### `hgj auth qrcode-check` — 检查扫码状态

```bash
hgj auth qrcode-check --session <sessionId> [--env <env>]
```

**状态码**:
| 状态 | 说明 | 后续操作 |
|------|------|----------|
| `pending` | 等待扫码 | 继续轮询（2秒间隔） |
| `scanned` | 已扫码等待确认 | 继续轮询 |
| `needChooseEnterprise` | 需要选择企业 | `hgj auth enterprise choose <id>` |
| `success` | 登录成功 | Token 已保存 |
| `expired` | 过期 | 重新 `hgj auth qrcode` |
| `needRegister` | 需注册 | 改用密码登录 |

---

### `hgj auth enterprise list` — 列出可选企业

```bash
hgj auth enterprise list [-e <endpoint>] [--env <env>]
```

**使用场景**:
- 仅 client 端使用
- 登录后（login 返回 `needChooseEnterprise`）查看可选企业列表
- 查看当前用户关联的所有企业 ID 和名称

---

### `hgj auth enterprise choose` — 选择企业完成登录

```bash
hgj auth enterprise choose <enterpriseId> [-e <endpoint>] [--env <env>]
```

**【client 登录后必须步骤】** 当 login 返回 `needChooseEnterprise` 时:
1. 此命令将 login 阶段的临时 `secret` 转换为正式的 `accessToken`
2. `accessToken` 自动保存到会话文件

**重要限制**:
- 只能在首次登录后立即使用（依赖 secret）
- 如果 secret 过期，需要重新登录

---

### `hgj auth status` — 查看认证状态

```bash
hgj auth status [-e <endpoint>] [--format table]
```

**返回**: 所有端点的认证状态概览，包含:
- endpoint / env / authenticated / account / enterprise / createdAt

---

### `hgj auth whale-identity` — 生成 whale-identity 请求头

```bash
hgj auth whale-identity [--env <env>] [--app-name <appName>]
hgj auth whale-identity --env <env> -a <account> -p <password> --enterprise-id <enterpriseId>
```

**使用场景**:
- 用户说“给我一个后端鉴权信息”“获取后端请求头”“获取 whale-identity”时，优先使用此命令
- 需要本地请求后端服务，并同时拿到 `access-token` 与 `whale-identity`
- 默认读取 `~/.hgj/auth/client-<env>.json` 中的 `access-token`
- 也可通过 `--account`、`--password`、`--enterprise-id` 做一次性登录生成，不写入本地 session
- 通过用户中心 `GET /whale/user/get-user-detail-info` 换取用户详情后生成 `whale-identity`
- 默认输出两行可直接复制的请求头: `access-token` 与 `whale-identity`

**常用方式**:
```bash
hgj auth whale-identity --env beta
hgj auth whale-identity --env beta -a 13800138000 -p mypassword --enterprise-id <enterpriseId>
hgj auth whale-identity --env beta --format json
```

---

### `hgj auth logout` — 退出登录

```bash
hgj auth logout -e <endpoint> [--env <env>]
hgj auth logout --all    # 退出所有端点
```

---

## 多环境说明

- **不同环境的 Token 互不影响**，`client-prod` 和 `client-dev` 各自独立
- 切换环境不需要退出重登，可以同时保持多个环境的 Token
- Token 存储路径: `~/.hgj/auth/<endpoint>-<env>.json`
- 文件权限: `0600` (仅当前用户可读写)
- Token 过期时，如果 `config.json` 中有对应的凭证预设，CLI 自动重登并重试请求

## 环境 BaseURL

| 端点 | 环境 | BaseURL |
|------|------|---------|
| client | prod | `https://whale-ingress-ng.hgj.com/whale-user-center` |
| client | beta | `https://beta-apisix.hgj.com/whale-user-center` |
| client | dev | `https://iter-apisix.hgj.com/whale-user-center` |
| admin | prod | `http://manage.hgj.net` |
| admin | beta | `http://beta-manage.hgj.net` |
| admin | dev | `http://dev-manage.hgj.net` |
| deploy | default | `http://next-manage.hgj.net` |
| deploy | global | `http://fuxi.globalhgj.com` |

---

## AI Agent 调用示例

### 场景 1: 需要调用客户端业务 API
```bash
# 步骤 1: 检查是否已登录
hgj auth status -e client --format json

# 步骤 2: 如果未登录 → 密码登录
hgj auth login -e client --env prod -a 13800138000 -p mypassword

# 步骤 3: 如果返回 needChooseEnterprise → 选择企业
hgj auth enterprise choose <enterpriseId> -e client --env prod

# 步骤 4: 登录完成，获取认证头用于 API 调用
# Token 文件: ~/.hgj/auth/client-prod.json
# 请求头: { "access-token": "<token>" }

# 如本地后端服务还需要 whale-identity：
hgj auth whale-identity --env prod
```

### 场景 2: 需要发布项目
```bash
# 方式 A: 手动登录
hgj auth login -e deploy -a username -p password

# 方式 B: 凭证预设后直接使用（config.json 中配置了 credentials.deploy-prod）
hgj deploy run dev
# → 自动登录 + Token 过期自动重登，无需手动介入
```

### 场景 3: 需要调用后台业务 API
```bash
hgj auth status -e admin --format json
hgj auth login -e admin --env dev -a username -p password

# Token 文件: ~/.hgj/auth/admin-dev.json
# 请求头: { "manager-session-id": "<token>" }
```

### 场景 4: 当业务 API 返回 401/403
```bash
# 先检查 Token 状态
hgj auth status -e client --env prod

# 如果 Token 过期 → 重新登录
hgj auth logout -e client --env prod
hgj auth login -e client --env prod -a 13800138000 -p mypassword
```

<!-- @hgj:auto:commands -->
## 命令参考

### `hgj auth login` — 登录 (支持 client/admin/deploy 三端)

```bash
hgj auth login [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `-e, --endpoint <endpoint>` | option | ✅ | 鉴权端点 (client\|admin\|deploy) | — |
| `--env <env>` | option | ❌ | 环境 (dev\|beta\|prod) | `prod` |
| `-a, --account <account>` | option | ❌ | 账号 (手机号/邮箱/用户名) | — |
| `-p, --password <password>` | option | ❌ | 密码 | — |
| `--global` | option | ❌ | 海外环境 (仅 deploy) | `false` |

### `hgj auth logout` — 退出登录

```bash
hgj auth logout [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `-e, --endpoint <endpoint>` | option | ✅ | 鉴权端点 | — |
| `--env <env>` | option | ❌ | 环境 | `prod` |
| `--all` | option | ❌ | 退出所有端点 | `false` |

### `hgj auth status` — 查看认证状态

```bash
hgj auth status [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `-e, --endpoint <endpoint>` | option | ❌ | 指定端点 (不传则显示全部) | — |

### `hgj auth whale-identity` — 生成 whale-identity 请求头值

```bash
hgj auth whale-identity [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--env <env>` | option | ❌ | client 环境 (dev\|beta\|prod) | `prod` |
| `--app-name <appName>` | option | ❌ | 用户中心 app-name | `whale_common_pc` |
| `-a, --account <account>` | option | ❌ | 一次性登录账号，不写入本地 session | — |
| `-p, --password <password>` | option | ❌ | 一次性登录密码，不写入本地 session | — |
| `--enterprise-id <enterpriseId>` | option | ❌ | 一次性登录需要选择的企业 ID | — |

### `hgj auth qrcode` — 二维码扫码登录 (仅 client)

```bash
hgj auth qrcode [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--env <env>` | option | ❌ | 环境 | `prod` |

### `hgj auth qrcode-check` — 检查二维码扫码状态

```bash
hgj auth qrcode-check [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `-s, --session <sessionId>` | option | ✅ | 二维码会话 ID | — |
| `--env <env>` | option | ❌ | 环境 | `prod` |

### `hgj auth enterprise list` — 列出可选企业

```bash
hgj auth enterprise list [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `-e, --endpoint <endpoint>` | option | ❌ | 端点 (client) | `client` |
| `--env <env>` | option | ❌ | 环境 | `prod` |

### `hgj auth enterprise choose` — 选择企业并完成登录

```bash
hgj auth enterprise choose <enterpriseId> [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<enterpriseId>` | argument | ✅ | 企业 ID | — |
| `-e, --endpoint <endpoint>` | option | ❌ | 端点 (client) | `client` |
| `--env <env>` | option | ❌ | 环境 | `prod` |

### `hgj auth enterprise switch` — 切换企业 (已登录用户)

```bash
hgj auth enterprise switch <enterpriseId> [options]
```

| 名称 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `<enterpriseId>` | argument | ✅ | 企业 ID | — |
| `-e, --endpoint <endpoint>` | option | ❌ | 端点 (client) | `client` |
| `--env <env>` | option | ❌ | 环境 | `prod` |
<!-- @hgj:auto:end:commands -->
