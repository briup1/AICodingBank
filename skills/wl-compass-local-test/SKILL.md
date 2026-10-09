---
name: wl-compass-local-test
description: compass-platform 本地自测环境一站式搭建与验证——本地起新代码后端/前端/Bot，连 dev 库与 dev 外部依赖，绕开 Nacos/Maven/鉴权/SPOT 的所有已知坑。触发词：compass 本地测试、本地起后端、compass 本地联调、路线B、本地自测、dev 数据本地跑、测试我的改动、起 18080。只要用户说"把改动在本地跑起来测"就应使用。
---

# compass-platform 本地自测（本地进程 + dev 数据）

> 2026-10-09 在 H001 免箱需求上全流程验证通过。所有"为什么"都来自真实踩坑记录，不要"优化"掉任何一步。

## 架构：本地进程跑新代码，dev 提供数据与外部依赖

```text
┌─ 本机（新代码）─────────────────────────────┐
│ agents-web vite :9967  (.env.wl-local)      │
│      │ 直接 HTTP（CORS 已放开）              │
│ compass-backend :18080  (java -jar, profile=local)
│      │                                      │
│ ├─ RocketMQ 本地 docker :19876/:10911       │  ← 唯一本地中间件，隔离 dev MQ
│ └─ （可选）assist-bot :8010+                │
└──────┬──────────────────────────────────────┘
       │ JDBC / Mongo / Redis(db3)
       ▼
┌─ dev 环境（共享，只经业务 API 写入）──────────┐
│ MySQL dev-mysql8:3306/compass-freight       │
│ Mongo 10.10.10.145:27017-19/compass-freight │
│ Redis dev-middle:6379 db3（与 dev 实例共享） │
└──────┬──────────────────────────────────────┘
       │ HTTPS（本机直连，无代理坑）
       ▼
┌─ dev 外部依赖（只读/校验类）────────────────┐
│ whale-auth-center（iter-apisix）→ 换身份     │
│ SPOT 接口 → ⚠ 实时创建 403 IP 白名单，见受限  │
│ dev-apisix Bot 网关（后端转发聊天用）         │
└─────────────────────────────────────────────┘
```

与 dev 部署实例的关系：**MQ 完全隔离**（本地 namesrv，consumer 组自动带 `_local` 后缀）；
**Redis db3 共享**（Redisson 锁跨实例协调，SpotPollingPersistence 等 DB-outbox 竞争消费是安全的）；
**MySQL/Mongo 共享**（任务数据真实写入 dev，禁止手改数据，只能走业务 API）；
**Nacos 完全不连**（config/discovery 都关，见下方坑 #3）。

## 端口槽位（已登记 WORKBENCH.local.md 台账；冲突时先查 wl-docker-port-registry）

| 端口 | 用途 |
| --- | --- |
| 19876 / 10911+10909 | 本地 RocketMQ namesrv / broker（容器 wl-rocketmq-*） |
| 18080 | 本地后端（dev 本地后端约定端口，bootstrap-dev 也是它） |
| 9967 | agents-web vite（9966 常被别的任务占用） |
| 8010 | assist-bot 本地（⚠ h008 等任务可能正占用，用时先 lsof） |

## 生成物位置约定（可控 + 定点清理）

所有本地自测产出只落一个根目录，不散落 worktree / /tmp：

```text
${COMPASS_LOCAL_TEST_HOME:-~/.local/state/compass-local-test}/<worktree-slug>/
├── logs/       # 后端/前端日志（统一重定向到这里，禁止 tee 到 .work 或 /tmp）
└── artifacts/  # 测试产物 dump（search/ftq 响应 json、导出 xlsx、UI 截图）
```

- 根目录可用环境变量 `COMPASS_LOCAL_TEST_HOME` 改指到别处（如外接盘）。
- 用完执行 `scripts/local-test-down.sh [slug]` 定点清理：停本需求进程（按端口+命令行特征匹配，
  不误杀别的任务）→ 停 MQ 容器 → 删除该需求生成物根目录（默认把最新一份后端日志
  备份到 `<base>/_last_logs/<slug>/` 再删）。
- `--purge` 额外删除共享 MQ 容器和 volume（下次要按步骤 1 重建）；正常不要 purge，volume 留着复用。
- 不属于"本需求生成物"的：~/.m2（依赖仓库）、pnpm store、wl-rocketmq 镜像——都是复用物，不动。

## 一键启动（推荐）

```bash
~/.agents/skills/wl-compass-local-test/scripts/local-test-up.sh [worktree目录]
# 加 --no-build 复用旧 jar（没改后端代码时）
```

脚本自动完成：dev 网络五连检查 → 端口占用校验（被占会指明 pid 和归属，防误杀）
→ MQ 复用/首建（compose）→ 构建 jar → 起后端并等健康检查 → 起前端并等就绪 → 打印就绪摘要。
生成物按「生成物位置约定」落盘。下面 0-4 步是手动等价流程与原理说明（排障时读）。

## 启动流程（手动等价版，按序执行）

### 0. 前置检查（每次）

```bash
# dev 网络五连（全通才能继续）
for t in "dev-mysql8.hgj.net 3306" "dev-nacos.hgj.net 80" "dev-middle.hgj.net 6379" "dev-middle.hgj.net 9876" "10.10.10.145 27017"; do nc -z -w 2 $t && echo "$t OK" || echo "$t FAIL"; done
# 端口占用（被占就换槽位，别 kill 别人的进程——先 lsof 确认归属）
lsof -nP -iTCP:18080 -sTCP:LISTEN; lsof -nP -iTCP:9967 -sTCP:LISTEN
```

### 1. 本地 RocketMQ（共享件，compose 固化在 skill 内）

```bash
SKILL=~/.agents/skills/wl-compass-local-test
# 首次（写 broker.conf 进 named volume + 起容器）：
docker compose -f $SKILL/scripts/docker-compose.mq.yml --profile init run --rm conf-init
docker compose -f $SKILL/scripts/docker-compose.mq.yml up -d
# 日常：docker compose -f $SKILL/scripts/docker-compose.mq.yml start
```

- **为什么 broker.conf 走 named volume**（本机 Docker Desktop 实测）：单文件 bind 挂载在容器里
  变空目录；目录 bind 有新文件同步延迟，broker 读到目录会启动失败（`Is a directory`）。
  named volume 是本机 VM 内部存储，无同步问题。conf-init 服务（--profile init）负责写入。
- autoCreateTopicEnable=true 是关键：后端 ~15 个 consumer 订阅的 topic 全部自动创建在本地方，
  dev MQ 零接触（即使 topic 名相同也是本机 namesrv 上的独立 topic，且消费组带 `_local` 后缀）。

### 2. 后端（核心：jar 方式，参数必须精确）

```bash
cd backend-service
# 2026-10-09 已修正：~/.m2/settings.xml 的 localRepository 原为 Windows 路径(C:\Users\HGJ)，
# 已改回 /Users/ziyun/.m2/repository 并留注释；正常 mvn 命令不再需要 -Dmaven.repo.local 覆盖。
mvn package -Pdev -Dmaven.test.skip=true -q
LT=${COMPASS_LOCAL_TEST_HOME:-$HOME/.local/state/compass-local-test}/$(basename $(pwd))
mkdir -p "$LT/logs" "$LT/artifacts"
java -jar target/compass-backend-service.jar \
  --spring.profiles.active=local \
  --spring.cloud.nacos.config.enabled=false \
  --spring.cloud.nacos.discovery.enabled=false \
  --server.port=18080 \
  --rocketmq.name-server=127.0.0.1:19876 \
  --spring.data.redis.database=3 \
  > "$LT/logs/backend.log" 2>&1
# 验证：curl -s localhost:18080/actuator/health → {"status":"UP",...,"taskWorker"}
```

- **为什么 nacos 全关**（坑 #3）：项目用了 spring-cloud-starter-bootstrap，Nacos 远程配置
  `addFirst` 优先级高于命令行参数——开着 nacos 时 `--server.port` `--rocketmq.name-server`
  全部被远程配置覆盖（实测端口仍 8090、MQ 仍指向 dev）。`bootstrap-local.yml` 内嵌了
  dev 数据源/Mongo/Redis/SPOT/鉴权地址，货运链路够用。
- **为什么不用 `mvn spring-boot:run -Dspring-boot.run.jvmArguments=...`**（坑 #4）：
  该参数在本项目实测被静默丢弃（进程以 profile=dev 启动）。jar + 命令行参数是唯一确定路径。
- 想纯旁观不抢 dev 任务：追加 `--task-center.accept-enabled=false --task-center.worker-enabled=false`。

### 3. 前端 agents-web

```bash
cd agents-web
# .env.wl-local 已由 up 脚本从 skill assets 拷入；手动时从
# ~/.agents/skills/wl-compass-local-test/assets/env.wl-local 复制：
cp ~/.agents/skills/wl-compass-local-test/assets/env.wl-local .env.wl-local
LT=${COMPASS_LOCAL_TEST_HOME:-$HOME/.local/state/compass-local-test}/$(basename $(pwd))
pnpm dev -- --mode wl-local --port 9967 --no-open > "$LT/logs/frontend.log" 2>&1
```

- 坑 #5：`APP_API_GATEWAY` 必须是完整 URL。设成空串走 `/api` fallback 会拼出
  `/api/api/v1/...`（ofetch 直接字符串拼接），全 404。
- 不用 vite proxy：`WebConfig` 已 `addAllowedOriginPattern("*")`，跨域直连即可；
  登录回调用 `?token=` 回跳 localhost 也是项目原生支持的（`runInLocal` 分支跳 dev-login）。
- 首次 `pnpm install --prefer-offline` 约 10s（本机 store 有缓存）。

### 4.（可选）assist-bot 本地

```bash
cd assist-bot
FREIGHT_SERVER_BASE_URL=http://127.0.0.1:18080 APP_ENV=dev uv run python main.py   # 端口 8010
```

## 鉴权配方（第二大坑，API 级测试必备）

本地没有 APISIX 网关代劳身份头，必须自己构造：

```bash
# ① 拿真实 dev C 端登录态（一次性人工登录，profile 记住 14 天）：
#    agent-browser 需 npm i -g agent-browser；wl-browse 在 macOS 不可用（dist 是 Linux ELF）。
#    用 hgj-session 的 capture 思路：系统 Chrome + profile ~/.hgj-session/profiles/hgj-client-dev 打开
#    https://dev-login.hgj.com/login ，人工登录（注意：capture 脚本的 headless 自检与
#    agent-browser 0.27 不兼容会误报，直接手动 open + cookies get 即可）。
# ② 从 profile 读 cookie：真正用于 API 的是 .hgj.com 的 sso_sessionid（不是 hgj-dev-access-token）。
# ③ 换身份：whale-identity = base64(JSON)，JSON 来自：
curl -s -X POST "http://iter-apisix.hgj.com/whale-auth-center/auth" \
  -H "Content-Type: application/json" -d '{"accessToken":"<sso_sessionid>"}'
#    → data.whaleIdentity 整体 base64（个人用户 enterpriseInfo 为空，后端兜底 enterpriseId=userId）
# ④ 每个请求带三个头：
#    access-token: <sso_sessionid>
#    whale-identity: <base64 JSON>
#    app-name: smart-agent
# 401 排查顺序：未授权( requireTaskOwner 缺上下文→whale-identity 没生效) → 缺少 whale-identity(过滤器层没传)
```

## 本机浏览器联调鉴权代理（显式启用）

本地前端直连 `127.0.0.1:18080` 时不会经过 APISIX，浏览器请求必须由本机临时代理补充三个身份头。为避免改业务仓库，Skill 提供可选脚本：

```bash
PROXY=~/.agents/skills/wl-compass-local-test/scripts/local-auth-proxy.mjs

# 当前 shell 中准备凭证；不要写入仓库或日志
export COMPASS_LOCAL_ACCESS_TOKEN="<sso_sessionid>"
export COMPASS_LOCAL_WHALE_IDENTITY="$(printf %s '<whaleIdentity JSON>' | base64 | tr -d '\n')"

# 仅监听本机 127.0.0.1，不默认启动
node "$PROXY" start --listen 127.0.0.1:18081 --target http://127.0.0.1:18080

# 以本机代理为前端接口地址（只影响当前启动的前端进程）
APP_API_GATEWAY=http://127.0.0.1:18081 \
  pnpm exec vite --mode wl-local --host 0.0.0.0 --port 9967 --no-open

# 结束后清理
node "$PROXY" stop
```

注意：认证中心返回的 `data.whaleIdentity` 是对象，必须先将整个 JSON 对象 Base64 编码后再放入请求头。

安全边界：代理只允许绑定 `127.0.0.1`，目标只允许本机 HTTP 服务；token 只从当前进程环境读取，不落盘、不打印；缺少凭证时拒绝启动。该能力默认关闭，不影响其他本地测试。

## 验证链路（API 级 smoke，5 分钟）

```bash
H="-H access-token:$TOK -H whale-identity:$ID -H app-name:smart-agent -H Content-Type:application/json"
# 0. 约定：响应 dump 与导出文件统一放 $LT/artifacts/（见「生成物位置约定」）
# 1. 建任务（⚠ 要测追问/导出必须首查带 freeTimeConditions，否则 retainAllCandidates=false，
#    free-time-query 会报 400"旧任务未保存完整候选"——这是设计，不是 bug）
curl -s -X POST localhost:18080/api/v1/freight/search $H -d '{"channel":"web","limit":50,"routes":[{"polCode":"CNSHA","podCode":"USLAX","containerTypes":["20GP"],"free_time_conditions":[{"direction":"ANY","feeMode":"DET","days":14,"operator":"GTE","containerTypes":["20GP"]]}]}'
# 2. 追问（改条件）：POST /api/v1/freight/tasks/{taskId}/free-time-query
#    带 expectedFreeTimeViewRevision，成功 revision+1；旧 revision 报 31004 版本冲突（CAS ✓）
# 3. 三态检查：免箱字段 freight_rate_dnd_detail_responses / free_period_responses
#    会呈现 null(来源未覆盖)/[](显式无数据)/[明细] 三种形态
# 4. 导出：POST /api/v1/freight/export {"taskId":"..."} → xlsx
# 5. 老任务/缓存命中任务被 free-time-query 拒绝是符合设计的兜底
```

推荐测试航线：**CNSHA → USLAX，20GP**（SPOT 取证授权航线，dev 有真实数据，MSK 有 24 条 DND 明细）。

## 已知受限项（不要当 bug 修）

1. **SPOT 实时创建 403** `Your IP address is not allowed`——SPOT 侧 IP 白名单只放行公司服务器，
   本机 IP 创建不了实时报价任务。读路径验证用已上架/缓存数据足够。
2. **export 在来源未收口时 400**"结果查询中"——SPOT 403 后观察到，待任务来源全部收口再导出。
3. **agents-mp 小程序无法本地测**（需微信开发者工具 + 真机）。
4. **dev 库写入是真实写入**；本地 worker 开着会领取 dev 任务中心的任务（新代码处理，结果仍写 dev，
   合法）。测完即停本地进程。
5. 免费箱期存量数据大多为空（AI 补空是独立需求），追问筛选返回 0 条常常是**正确结果**。

## 用完清理（定点）

```bash
~/.agents/skills/wl-compass-local-test/scripts/local-test-down.sh [worktree-slug]
# 或彻底连 MQ 一起删（下次需重建）: local-test-down.sh --purge
```

## 故障速查表

| 症状 | 原因 | 解法 |
| --- | --- | --- |
| 编译报"程序包 xxx 不存在"几百条 | settings.xml 曾被写入 Windows localRepository（2026-10-09 已修正并留注释防回潮） | 已根治；若从同事机器重新同步 settings.xml 需复查该行；worktree 里误入的 `C:\Users\HGJ` 目录可删 |
| 端口被占/指向 dev MQ（开着 nacos 时） | nacos 远程配置 addFirst 压过命令行 | nacos config+discovery 都 disabled |
| `mvn spring-boot:run` 参数没生效 | jvmArguments 被静默丢弃 | 用 jar 方式 |
| 401 未授权 / 缺少 whale-identity | 没构造身份头 | 见「鉴权配方」 |
| free-time-query 400 旧任务未保存完整候选 | 首查没带免箱条件，或缓存命中老任务 | 首查带 free_time_conditions 重新建任务 |
| 前端全部 404 | APP_API_GATEWAY 设成空串 | 必须完整 URL（坑 #5） |
| broker 起不来 "Is a directory" | bind 挂载单文件在 Docker Desktop 不可用 | named volume（见步骤 1） |
| 登录浏览器被误报 headless | capture 脚本检测与 agent-browser 0.27 不兼容 | 手动 open + cookies get 提 token |
