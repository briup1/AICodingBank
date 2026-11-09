---
title: "e2e：可靠接入与独立回归使用指南"
date: 2026-11-06
date_basis: practice-date
updated: 2026-11-06
category: 技术
tags: [e2e, 浏览器测试, 登录态, 异步任务, 回归测试]
status: verified
source:
  - "e2e 0.22.0 随包 guide/docs；@e2e-dev/web 0.15.4"
  - "https://e2e.tester.army/docs/authentication"
  - "/Users/ziyun/workdir/private/compass-platform-e2e/reports/dev-freight-final-20261106/verification.md"
---

# e2e：可靠接入与独立回归使用指南

适用于 TesterArmy 的 `e2e` / `@e2e-dev/web`，不是泛指 E2E 测试。目标：换一个页面也能沿同一条链可靠接入。**已验证范围是浏览器确定性回归，不代表 AI、缓存或被测业务已稳定。**

```text
确认环境与操作授权 → 核对安装版 guide → setup 登录并验证业务页
→ 单场景及重复验证 → 独立 test 矩阵 → 读取报告和截图
```

## 六步使用指南

### 1. 先核对版本，不猜 API

复用项目依赖、配置和用例，不默认升级或重新 init。先运行 `e2e guide`，按需读 `guide setup`、`guide writing-tests`、`guide running`、`guide debugging`；完整文档随包在 `node_modules/e2e/docs/`，优先于可能已更新的在线示例。

本次版本需要 Node ≥24.8，或 Node 22 ≥22.22.3。使用 `browser` 时从 `@e2e-dev/web` 导入 `test`，从 `e2e` 导入 `expect`；它不是原生 Playwright Page。先 `e2e list` 确认场景和 setup 能被收集，再真实运行。

### 2. 原生 setup 登录，不共享日常浏览器

用 `test.setup(..., { sessions: ['member'] }, ...)` 登录；业务测试声明 `{ session: 'member' }`。**保存前先验证目标业务接口已登录、页面可操作、无登录弹窗；依赖企业/角色的测试还要核对对应身份。** Cookie 存在或登录中心跳转成功都不够，`session.save` 不检查登录。

账号放配置 `credentials`，密码来自环境变量或延迟读取的本机凭据函数，经 `credentials.user(name).password` 交给 `fill`，不写入代码、命令参数、模型输入或报告。固定语言，或使用实测过的多语言名称。

默认让 runner 启动和回收独立浏览器。每个 run 的 session 临时加密保存、结束清理，只含浏览器态，不含后端业务态。CDP 持久连接恢复会限制 session 保存/恢复，不作为默认登录方案。

### 3. 一场景一 test，额外验证业务隔离

数据循环放在**注册 test 的外层**，不要在一个 test 内跑完整矩阵。初期显式 `workers: 1, retries: 0`，每项独立超时、报告和截图。

新浏览器仍可能恢复服务器上的最近会话。通过页面“新会话”或正式入口创建上下文，并检查：首问不带旧 session，后端返回本场景 session，追问使用同一 session，不同场景 session 不重复。`app.open('/query')` 不等于新会话，不随意编造服务器 ID。

### 4. 固定输入用定位器，完成条件按协议

控件名称来自实际页面或源码，优先 role/name、label，无可用语义时用现有 CSS；e2e 默认文本匹配比 Playwright 严格。固定问句直接 `fill`，不要让测试 Agent 改写。用 `expect` / `expect.poll` 等状态，不靠 sleep 或 `networkidle`。

把**对话结束、异步任务结束、页面可继续输入**分开判断：SSE `done` 不等于查价 COMPLETE，流关闭也不等于成功。要求 COMPLETE 时不能把 ERROR 当通过；只验证第二任务新建，就不声称其全部渠道已完成。

正文检查最终提交版本，不拼接被 reset 的草稿；合法结果卡片可以没有正文。同时验证工具/任务 ID 和页面展示。需要旁路采集 SSE 时，不消费或修改客户端流；自写采集器先自检 done、缺 done、分片和末行。采集脚本是项目特例，不作为通用接入必需品。

### 5. 分层预算，分类处理失败

动作、业务等待、单 test、整套 run、外层命令各有预算。单 test 覆盖顺序步骤预算之和，命令长于 run 加清理；不能只凭一个快场景设所有等待时间，也不无限加总超时。

| 失败 | 下一步 |
| --- | --- |
| 登录失败 | 停在 setup，依赖测试跳过，不继续真实查价 |
| 控件或采集器错误 | 先读 `trace.md`，修正证据覆盖的错误，只跑受影响项 |
| 正常任务仍 CHECKING | 保留最后状态，核对业务时限；后来变快不能证明根因已解决 |
| 业务断言失败 | 保留实际行为，不放宽断言、不重试到绿 |

重复验证用 `--repeat-each` 单独计数，不能用最后一次通过抹去偶发失败。

### 6. 读报告，不只看退出码

检查 `report.json` 的 run ID、时间、status、exitCode、summary 和每项结果。退出码 0 可能包含 skipped/flaky。用 `list,markdown` 看摘要，失败读 `results/<test>/trace.md`，实际查看关键截图；`--debug` 区分业务等待和工具开销。

完整运行使用唯一 output。`--last-failed` 必须指向**同一 output**；其摘要/退出码仅代表本次选中项，未解决项还需看 `run.carried`。普通运行可能清理旧结果，长期证据保留完整目录；业务标识另留最小脱敏摘要。

Secret 不等于全链路脱敏：Cookie token、视频、普通页面文字和应用日志仍可能含敏感信息。原始产物默认本机私有，分享前检查，不上传账号页或原始报告到外部知识库。

## 本机复用入口

```bash
cd /Users/ziyun/workdir/private/compass-platform-e2e
export E2E_TELEMETRY_DISABLED=1
# ./node24 是此项目已有运行入口，其他项目按自身工具链执行。
./node24 ./node_modules/.bin/e2e guide writing-tests
./node24 ./node_modules/.bin/e2e list --config e2e.dev.config.ts tests/dev-freight-followup.e2e.ts
# 先 canary；完整运行去掉 --grep。新完整运行换一个 output。
./node24 ./node_modules/.bin/e2e run --config e2e.dev.config.ts tests/dev-freight-followup.e2e.ts \
  --grep '^R01 ' --output reports/my-canary --reporter list,markdown
# 续跑失败项沿用同一 output；不把选择性重跑当成全套通过。
./node24 ./node_modules/.bin/e2e run --config e2e.dev.config.ts tests/dev-freight-followup.e2e.ts \
  --last-failed --output reports/my-canary --reporter list,markdown
```

## 实测依据与边界

2026-11-06，macOS / Node 24.22.2 / e2e 0.22.0 / web 0.15.4：Dev 运价首问/追问 **15/15 通过**，setup 1/1，**324.15 秒**，无自动重试。天津→釜山独立重复 **3/3 通过**，约 63 秒含 setup；采集器本地自检 3/3。R01/R07/R13 截图已查看，不是全面视觉验收。

关键修正：原生 setup/session、独立 test、后端会话核对、对话/任务分层等待。早期整套 360 秒超时、英文页面定位错误、90 秒 CHECKING 超时均保留为经验。

**R13“为什么没有结果”此前重复两次一过一败，失败时错误创建新查价任务；最终单次通过不代表已修复。** 工具接入可用与业务稳定性分开判断。未覆盖多企业身份校验、并发、CI、跨浏览器或第二任务所有渠道结束。

测试侧未调用 `agent.*`，未验证 AI 操作和 replay cache 收益。官方建议确需 AI 时一条 `act` 一个目标并立即断言；`assert/waitFor/extract` 仍需模型。先读 `guide agent` 并确认模型、外部成本授权，另做 canary，不强行把固定步骤改成 AI。

## 来源、失效条件与修订

- 官方：[登录](https://e2e.tester.army/docs/authentication)、[测试 API](https://e2e.tester.army/docs/reference/test)、[运行](https://e2e.tester.army/docs/reference/cli)、[安全](https://e2e.tester.army/docs/security)；实际 API 以安装版 guide/docs 为准。
- 私有项目：`/Users/ziyun/workdir/private/compass-platform-e2e/`；完整结果、任务标识和历史偏差见 `reports/dev-freight-final-20261106/verification.md`，原始报告/截图留在项目，不复制到工作台。
- e2e/engine/Node 升级，登录/身份/语言、完成协议或数据变化时，重新核对对应 guide 并跑 canary。不照抄此项目路径、CSS 或超时数值；旧授权不继承，不自动安装、启服务、提交、发布或删测试数据。
- 2026-11-06：依据官方随包文档、真实矩阵及重复运行形成首版。
