# Compass Web 对话 E2E

正式可复用入口。使用 TesterArmy e2e 0.22.0 / @e2e-dev/web 0.15.4，不使用 Ego 或测试侧 AI。记录遵循 [执行约定](../execution-profiles/test-execution.md)。

```text
首次 login → 独立系统 Chrome → 登录 → 验真实身份与企业 → 独立 Context 恢复验证 → 本机加密保存
后续 run → 新进程加载对应环境登录态 → 验身份/页面 → 新会话 → 逐轮问句 → 任务终态/当前轮结果/截图
```

## 日常使用

```bash
cd /Users/ziyun/workdir/self_project/AICodingBank/tools/compass-platform-e2e
./e2e check
./e2e list --env dev
# 首次或过期时登录（不发查价消息）。在独立 Chrome 登录后返回对应查价页。
./e2e login --env dev
./e2e login --env beta
./e2e login --env prod
# 已获当次环境与问句范围授权后运行。默认用例只有上海到洛杉矶，两轮。
./e2e run --env dev --allow-live-queries
./e2e run --env beta --allow-live-queries
./e2e run --env prod --allow-live-queries --allow-production
# 自定义用例和显示浏览器
./e2e run --env dev --cases cases/shanghai-la-two-turn.json --allow-live-queries --headed
./e2e report --run .work/test-runs/<运行编号>
```

默认问句严格固定：`上海到洛杉矶` → `上海到洛杉矶，再查一次`。不自动添加船司、箱型或日期限制。其余历史样例仅在显式 `--cases` 时使用，不删除旧实验。

三个环境是 dev/beta/prod；bot 是被测服务，不是环境。本工具只做真实 Web，不冒充 Bot 直连接口或小程序实测。

## 登录与安全

- 只启动本工具自有系统 Chrome，CDP 仅监听 127.0.0.1；不连接日常浏览器、不提取日常登录态。macOS 需已有 `/Applications/Google Chrome.app`，不自动下载浏览器。
- `login` 默认手动登录。`login --local-account` 仅在明确允许读取本机测试账号时使用，限 dev/beta 的本机账号 1；最多一次自动登录，失败后转手动，不轮换账号、不重试密码。
- 本机账号来源为工作台 Git 忽略的 `personal/compass-test-accounts.local.md`。密码只在内存与子进程环境中传递；不输出、不另存。配置中的 Beta 旧密码已失败，不应再次自动尝试，使用手动登录。
- 经用户明确授权后，登录态按环境 AES-256-GCM 加密保存于 `~/.local/share/compass-platform-e2e/{dev,beta,prod}.json`；密钥同目录 `key.json`。目录 0700、文件 0600，拒绝软链和不安全权限，不入库、不上传。密钥与密文同机不能防止同一系统账号被攻陷。
- 仅保存目标 app origin 的 storage 和必要 HGJ Cookie，固定首次真实用户 ID 与企业 ID（个人账号企业可为空）。后续身份不一致、状态损坏或权限不安全时停止，不覆盖原基线。
- 保存前用独立 Context 验证真实身份、页面和恢复；下一次新进程还会重新验证。缓存失效只提示 `LOGIN_REQUIRED`，使用 login 补登；不承诺永久免登。
- Dev 实测身份入口可能为 iter-apisix，Beta 为 beta-apisix，Prod 为 whale-ingress-ng。严格核对当前业务环境对应的身份 origin/path、HTTP、业务码及真实 userId；输入框存在不等于已登录。
- `login` 不发送查价消息，截图/trace 关闭；失败产物仍可能含页面/账号信息，均仅本机私有。`run` 会创建会话、任务并消耗用量，参数门禁不替代用户授权。
- 不点击订舱、抢舱、求运价、红包或删除历史。用例问句必须人工确认属于获准操作，JSON 校验不等于业务安全审查。

## 可替换的单／多轮用例

每个 scenario 是独立 test 与新会话；turns 一项为单轮，多项共用会话。见 `cases/shanghai-la-two-turn.json`。

```json
{
  "schemaVersion": 1,
  "scenarios": [{
    "id": "shanghai-la",
    "turns": [{
      "message": "上海到洛杉矶",
      "expect": {
        "action": "new_search",
        "task": "COMPLETE",
        "ui": "result_or_empty",
        "route": {"pol_code": "CNSHA", "pod_code": "USLAX"}
      }
    }]
  }]
}
```

| 预期 | 检查 |
| --- | --- |
| action=new_search | unified_search、独立新 taskId、任务严格 COMPLETE；ERROR 不通过 |
| action=filter_existing | freight_task_data，无新查价任务 |
| action=status_only | 无 unified_search/freight_task_data 或新任务 |
| action=no_query | 不调用工具、不创建任务 |
| ui=has_results | 当前轮至少一张可见卡片，仍保持严格要求 |
| ui=empty | 当前轮无卡片且有明确空态 |
| ui=result_or_empty | 任务完成后，接口有结果则页面有卡片，接口零结果则页面明确空态；不把任意回复当通过 |
| ui=response | 当前轮有可见回复，不适用于 new_search |
| route/contains（可选） | 核对标准化条件或当前轮文本；不写死模型整句措辞 |

SSE done、任务完成、页面可继续输入分别判断。每轮只支持一个查价任务；多个 unified_search 报错，不静默漏测。确认弹窗、并发多航线、多语言专项不在本版范围。

## 结果与恢复

每次唯一目录 `.work/test-runs/<运行编号>/result.json` 是逐轮事实记录。原生报告、trace 和截图在其 `evidence/runner/` 下。保留原始问句、哈希、sessionId、taskId、脱敏 SSE、轮询、当前轮 DOM、截图引用和错误。

提交前落盘，任务 ID 取得即更新。串行、零自动重试，不实现 resume/last-failed；中断后先回读已有任务，禁止盲目重发。强杀可能留下进行中记录和自有临时 Chrome，需要人工核实，不自动删除业务数据。

每轮新任务必须使用同一场景会话且新 taskId；当前轮 DOM 与任务条数互相核对，不把旧卡片、历史参考价算成本轮结果。采集器仅克隆响应，原 Response 返回页面，不改流或发旁路业务请求。

退出码之外还需读逐轮结果、runner skipped/flaky/error，并实际查看关键截图。截图自动滚动可能只覆盖部分卡片，不能以截图替代完整 DOM 计数；保存不等于已审查。原始产物可能含业务文本和身份信息，分享前检查，不上传外部服务。

## 安装与本机验证

包装器优先本机 Homebrew Node 24，否则 PATH node；可用 `COMPASS_E2E_NODE` 指定。全新机器需要 Node >=24.8、pnpm 10，显式执行 `pnpm install --frozen-lockfile`；依赖已固定版本，不自动升级。

2026-11-11：16 项本地自检通过，覆盖加密状态、环境/身份隔离、文件安全、会话/任务、SSE 分片及中断记录。三个环境均通过首次登录、独立 Context 恢复和后续新进程免手登验证，固定两轮“上海到洛杉矶”均通过（6/6 轮，每轮任务 COMPLETE、新 taskId，同组同一 session）。每环境第二轮截图已实际查看；DOM 摘要卡片数 Dev 4/4、Beta 3/3、Prod 3/3，摘要卡片数不等于全部运价数。

本机证据位于 `.work/test-runs/`：Dev `2026-11-11T02-41-15-641Z-892d2279`，Beta `2026-11-11T02-41-49-195Z-39c559c7`，Prod `2026-11-11T02-44-08-472Z-a08f8918`。这些是一次真实实验，不证明永久免登、整机重启、账号锁定或未来页面变更后仍有效。Beta 旧密码问题没有修改账号密码，而是通过人工确认登录并保存有效状态解决运行阻塞。

历史首版实验及工具接入依据见 [可靠接入与独立回归](../../best_practices/2026-11-06-e2e-可靠接入与独立回归/README.md)。旧项目不再是运行依赖；旧失败、报告和用例保留，不覆盖。
