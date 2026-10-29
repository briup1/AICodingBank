# Playwright 测试登录复用（HGJ client / Beta）

本目录是 CLI + Playwright Test fixture，不是新浏览器平台，也不会自动接管任意现有 spec。

```text
首次明确授权 / 人工登录 / 确认账号与企业
  → 新独立环境验证恢复成功
  → 本机私密保存必要状态与预期身份
下一次新 Agent / 新进程
  → consent 检查 → 加载状态 → 独立 Context
  → 真实身份接口、预期账号企业、页面可用性门禁
  → 成功才交给用例 → 只关闭本次资源
```

## 前提与配置

- Node.js >=22，已存在的 `playwright` npm 包（含 `playwright/test`、CLI）及匹配的 Chromium 缓存。没有新增依赖、自动安装、下载或升级。
- 本机配置固定在 `~/.config/playwright-auth/config.json`；目录0700、文件0600。**真实运行时路径只放这里，不写入仓库**。
- `~/.local/share/playwright-auth/` 目录0700。`hgj-client-beta.json` 保存必要 Cookie、目标 origin localStorage/IndexedDB 与当前预期身份副本；`expected.json` 独立保留首次确认的账号/企业基线，补登不得自动换成别的身份。文件均0600；这不是加密存储，本机同一系统账号仍可读取，磁盘备份应按凭证保护。
- 首次登记必须有用户明确的站点、账号/企业及持久保存授权；本轮允许当前专用 A 为登记来源。`consent:true` 仅记录已有授权，不自行创造授权。

配置示意（路径由操作者填本机已有位置；示意不能直接运行）：

```json
{
  "consent": true,
  "environment": "hgj-client-beta",
  "version": "<已安装 playwright 版本>",
  "runtime": "<绝对路径：playwright 包目录>",
  "executable": "<绝对路径：匹配 Chromium 可执行文件>"
}
```

若使用 npm 缓存中的现有 runtime，缓存清理后会返回 `RUNTIME_UNAVAILABLE`。**本能力不是独立安装稳定的 Playwright**；需人工配置另一个已安装且已验证的稳定路径，不自动下载。源码不扫描其他项目或回退到任意版本。

安全目录检查拒绝符号链接、不正确 owner、组/其他用户可写祖先以及私密叶子的宽权限；不通过自动 chmod 修补已有不安全状态。单文件原子替换失败不破坏旧文件。配置与状态需位于本机规定位置，不能通过 CLI 任意指定状态路径。

## 命令

以下相对路径命令在仓库根运行；跨项目、换 Agent 会话或重启后应使用 `cli.mjs` 的实际绝对路径。没有 `--env prod`、额外 project/config 或 runner 参数透传。

### 重新开机后直接调用

下面 `/absolute/AICodingBank` 是仓库绝对位置占位，不是运行时依赖路径；调用者替换为本机真实仓库路径即可，不需要旧浏览器、旧 CDP 或上轮 Agent 上下文：

```sh
node /absolute/AICodingBank/tools/integrations/playwright-auth/cli.mjs check
node /absolute/AICodingBank/tools/integrations/playwright-auth/cli.mjs run \
  --spec /absolute/project/example.spec.mjs \
  --output /absolute/private-evidence/new-empty-run-directory
# 明确 LOGIN_REQUIRED 后，人工补登；保留首次已确认的账号/企业预期：
node /absolute/AICodingBank/tools/integrations/playwright-auth/cli.mjs login
```

`check` 仍必须验证真实身份；状态文件存在不算成功。服务/网络错误不应直接转成重新登录。整机重启尚待用户实际执行后验证，不能将新进程证据当作已测关机开机。

### 首次登记（一次受控导入）

```sh
node tools/integrations/playwright-auth/cli.mjs bootstrap \
  --source-cdp http://127.0.0.1:<本任务自有端口> --establish-expected
```

仅适用于已获用户确认的专用测试浏览器，不能对日常 Chrome 使用。只接入本机回环 HTTP 端口；读 A 的真实身份并在独立新浏览器验证恢复后才保存。不会关闭 A。仅首次可使用 `--establish-expected`；已有状态/基线时拒绝重建，不把错误账号覆盖成新预期。

### 人工首次登录 / 后续补登

```sh
node tools/integrations/playwright-auth/cli.mjs login --establish-expected
# 后续补登，保留原预期账号/企业：
node tools/integrations/playwright-auth/cli.mjs login --wait-seconds 300
```

必须从交互终端运行。在自有可见窗口完成登录和企业选择，回到 Beta 业务页面后在终端按 Enter；不要在终端输入密码。然后门禁验证并尝试独立恢复；成功才保存。无状态/损坏状态可依靠独立 expected.json 补登，身份不符、服务故障不会更新状态。

取消/超时/失败不保存、不进入用例；窗口保留供用户检查，CLI 明确报告并等待用户自己关闭该窗口后退出。不是常驻服务。账号切换/重新登记不提供自动覆盖命令，需新的明确授权和人工处理旧基线。本版不读取密码 vault、不代填密码。

### 日常只读检查 / 新进程恢复

```sh
node tools/integrations/playwright-auth/cli.mjs check
node tools/integrations/playwright-auth/cli.mjs check --count 3
node tools/integrations/playwright-auth/cli.mjs check --parallel 2
```

每次命令新启动 headless 浏览器；每个检查新建、关闭独立 Context，结束关闭自有浏览器，不使用任何源 CDP。不发送业务写请求，页面自动 POST 遥测也拦截；并发仅两个身份检查，不是查价并发。

成功输出只有环境、sameIdentity/sameEnterprise、context 计数、耗时；失败仅稳定状态码，不输出 raw error/身份/鉴权。HTTP200、按钮存在、文件存在都不算成功。

### 运行真正 Playwright Test

spec 必须是可信本地 `.spec.mjs`。本版只接受简单、可判定的迁移形式：**第一个语句必须为未起别名的 `import { test }` 或 `import { test, expect }`，来源是本目录真实 `fixture.mjs`**，正文至少一个直接 `test(...)`。不支持其他 import、helper 导入、re-export、动态 import/require、test 别名/重绑定；保守词法检查也可能拒绝含这些词的注释/字符串，返回 `UNSUPPORTED_SPEC_FORM`，不猜测运行语义。expect-only 导入不能通过。复杂旧 spec 需先改为该简单形式，不承诺无改动迁移。

示例：

```js
import { test, expect } from '/本机仓库绝对路径/tools/integrations/playwright-auth/fixture.mjs';
test('page ready', async ({ page }) => {
  await expect(page.locator('textarea')).toBeEditable();
});
```

```sh
node tools/integrations/playwright-auth/cli.mjs run \
  --spec /absolute/project/example.spec.mjs \
  --output /absolute/private-evidence/new-empty-run-directory
```

`--output` 必须不存在，父目录为本用户私密目录。CLI 使用固定 config、workers=1/retries=0、trace/screenshot/video=off；没有任意参数透传。运行 stdout/stderr 不回传 raw runner 输出，临时 runner output 在结束后移除，仅输出 PASS/TEST_FAILED、exit code、所选 spec 的 basename 和发现/完成测试数（失败细节应由可信用例设计脱敏报告）。不删除调用者原有目录。

fixture 的 auto gate 在测试正文前启动独立 context，验证真实身份，再将同一个已验证 page 交给正文；门禁失败不会进入测试。默认 headless。门禁期间拦截写操作，通过后解除拦截，由**另行获准**的可信用例负责后续行为。保存登录不授权以后查价或写业务。

**限制**：这不是 JS 安全沙箱。import 检查仅避免误用裸 Playwright，不防恶意 spec、自行启动浏览器或主动覆写 fixture；信任 spec 的代码是前提。任意未引用本 fixture 的既有 spec 不能宣称已受保护。fixture 不暴露认证状态路径或 Token 到 testInfo/reporter。

## 失败分流

| 状态 | 含义 / 下一步 |
| --- | --- |
| CONSENT_REQUIRED | 不读取真实状态。用户撤回时将 config.consent 设 false；不自动删除状态 |
| STATE_MISSING / STATE_CORRUPT | 状态不可用，不进入用例；使用既有身份基线人工补登 |
| LOGIN_REQUIRED | 身份接口明确未认证，用户人工补登 |
| IDENTITY_MISMATCH | 错账号/企业，停止，不自动重建预期 |
| IDENTITY_UNCONFIRMED | 成功码但缺标识/响应非法，不能证明身份，不自动要求重登 |
| ACCESS_DENIED | 权限问题，不能假定重新登录能修复 |
| SERVICE_UNAVAILABLE / PAGE_UNAVAILABLE | 网络、服务或页面不可用，不误报为凭证过期 |
| ENVIRONMENT_REJECTED | 非 HGJ client/Beta 或存储 origin 越界 |
| UNSAFE_* | 文件系统安全前提不成立，停止；不打印原始路径/数据 |
| RUNTIME_UNAVAILABLE | 本机路径失效/版本不符；人工修正配置，不自动安装 |

身份门禁仅接受 `https://beta-apisix.hgj.com/whale-user-center/whale/user/get-user-detail-info` 的真实页面 GET 响应；先检查业务码，再比较 `userId`、`enterpriseDetailResponse.enterpriseId`，拒绝缺值。顶层导航只允许 Beta app/login/identity 域，CDN 静态 GET 可加载。只持久保存目标 app origin 的 localStorage/IndexedDB；不使用 sessionStorage。

## 聚焦自测与验收边界

```sh
node --test tools/integrations/playwright-auth/tests/auth.test.mjs
# 下项会真实只读访问 Beta，需已获准且配置有效：
node tools/integrations/playwright-auth/cli.mjs run \
  --spec "$PWD/tools/integrations/playwright-auth/tests/identity.spec.mjs" \
  --output /absolute/private-evidence/new-fixture-output
```

本地夹具覆盖身份缺失/不符/失效/权限/服务分流、可信登录跳转无身份请求与网络故障对照、可信响应 origin/path、存储边界、consent 拒绝、缺失/损坏、symlink/owner/权限、原子保存失败保留旧态、门禁失败不进正文和参数覆盖拒绝。

`tests/runner.test.mjs` 还包含真正本地 Test runner 负例：expect-only + 旧 helper 的误配置被 CLI 拒绝；合法共用 test 在隔离 HOME 缺状态时，runner发现/完成1项失败，明确 STATE_MISSING，正文副作用标记不存在。运行该负例需显式提供本机已安装 runtime/executable 路径（不读或修改真实配置/状态）：

```sh
PW_AUTH_TEST_RUNTIME=/absolute/existing/playwright \
PW_AUTH_TEST_EXECUTABLE=/absolute/existing/chromium \
node --test tools/integrations/playwright-auth/tests/*.test.mjs
```

未提供这两个环境变量时本地 runner 负例显示 skipped，不能当成已验证。没有恶意 JS 沙箱或大 parser。

真实结果以本次脱敏证据为准；新进程恢复不等于整机关机重启。实际整机重启仅由用户自行执行后另验；不承诺永久免登、其他站点/admin/跨设备同步。所有资源均仅管理本任务创建部分。
