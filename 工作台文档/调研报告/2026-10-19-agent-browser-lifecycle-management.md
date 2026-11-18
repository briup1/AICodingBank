# agent-browser 生命周期与可控性调研

日期：2026-10-19
状态：只读调研与候选方案，未启动 Dashboard、未启动浏览器、未升级或修改配置。源码核验不等于运行验收。

## 1. 问题定义

用户频繁使用本地 agent-browser，但无法方便回答：当前开了几个浏览器、属于哪个任务、是否仍在执行、能否关闭、是否真正关闭。目标不是禁止多会话，而是让浏览器资源可见、可定向停止、有自动收尾与泄漏兜底。

本次本机证据：

- agent-browser 已安装版本为 0.27.0。
- 此前发现三个 headless Chrome 渲染进程，各约 100% CPU；浏览器实例启动约 41 小时，不等于满载 41 小时。
- 按用户授权向三个 Chrome 主进程发送 SIGTERM，主进程及三个满载 Renderer 均退出；没有使用 agent-browser 原生 close。
- 后续 `agent-browser session list --json` 仍返回五个名字，其中包括上述三个；对应 agent-browser daemon 进程仍存在。因此此前停止的是浏览器负载，不是完整会话生命周期。当前未继续关闭其他会话。
- 守护进程、浏览器主进程、Renderer、登录配置是不同对象；关闭验收不能只看其中一项，也不能把会话名列表等同浏览器数量。

未证实事项：具体页面为何跑满 CPU、历史启动入口是否配置过超时、Dashboard 实际运行表现、空闲超时对真实长任务的影响。

## 2. 已有开源能力

### agent-browser 0.27.0：优先复用

本机 `--help`、随包 README 与同版本上游源码交叉核验：

| 需求 | 已有能力 | 边界 |
| --- | --- | --- |
| 看有哪些会话 | `agent-browser session list --json` | 不是浏览器存活与任务活跃性的完整证明 |
| 多任务隔离 | `--session <name>` | 仍需定义可读命名，不能让不同任务共用默认会话 |
| 看执行过程 | `agent-browser dashboard start` | 独立后台服务，默认端口 4848；有实时画面、命令活动、控制台；需要单独停止 |
| 停止指定会话 | `agent-browser --session <name> close` | 仍需检查 daemon 与浏览器进程退出 |
| Dashboard 关闭 | 同版本 session-tree.tsx 有 Close session / Kill session 及确认框 | 源码确认，未在本机运行验收；优先 Close，不默认 Kill |
| 全部关闭 | `agent-browser close --all` | 会影响其他任务，不作为普通任务收尾命令 |
| 空闲自动收尾 | `AGENT_BROWSER_IDLE_TIMEOUT_MS` | 0.27.0 未设置或为 0 时禁用；在 daemon 启动时读取 |
| 持久登录配置 | `--profile <path>`、`--session-name` 等 | 持久化配置不等于保证业务登录不过期；不自动增加明文状态导出 |

0.27.0 的 `cli/src/native/daemon.rs`：

- 115–120 行：从环境读取 `AGENT_BROWSER_IDLE_TIMEOUT_MS`，仅正整数启用。
- 176–188 行：建立 idle timer 与 reset channel。
- 226–235 行：到期获取状态锁，调用浏览器 manager 的 close，退出 daemon 主循环；收到 reset 重置 timer。
- 179–181 行：注释明确说明 close 应走正常退出与析构，避免直接 process::exit 遗留 Chrome。

注意：这是“无命令活动”超时，不是“业务任务已经完成”判断。尚未对所有长命令与锁时序做验证，不保证长任务无影响；不能把它替代任务收尾，也不应通过无意义心跳无限保活。

### 新版本行为：可选升级，不是前置条件

官方 v0.33.1 Release 说明默认开启 1 小时无命令或 Dashboard 输入后的自动关闭，默认豁免 headed / 用户附加浏览器等情形；显式配置超时适用范围不同。它证明上游已经针对漏关问题提供默认防护，但不能把新版本默认行为套用到本机 0.27.0。

当前版本已有关键能力，优先验证当前版本，不为解决本问题强制升级。若升级，需要单独批准并核验现有登录与自动化入口兼容性。

### Browserless：有更强服务端治理，但不是当前首选

官方 Docker 配置文档提供并发上限、队列、总会话超时、重连期限、压力查询及健康阈值等能力。

它适合集中托管浏览器和多客户端共享资源配额。对当前单机问题，引入 Docker 服务、连接方式与 profile 迁移成本较高；部分文档同时覆盖开源与企业版，具体能力的版本、镜像和许可需要逐项核对，不宣称全部免费可用。

## 3. 建议方案：原生能力优先，缺口再补

旧链：

```text
任意 Agent 启动 → 默认可常驻 → 任务结束未 close → 用户无法观察 → 发热后查进程
```

新链：

```text
明确命名的任务会话
 → 启动时启用空闲兜底
 → 需要时用原生 Dashboard 查看
 → 成功/失败/取消都 close 指定会话
 → 核验 daemon 和浏览器主进程及子进程
 → 无命令超时兜底回收
```

第一阶段不开发新平台：

1. 使用 `项目-环境-用途-短任务ID` 命名会话，登录 profile 与任务会话名分开；同一 profile 不允许并发独占启动。
2. 对新建的自有短任务会话，建议起始试行 30 分钟无命令回收：`AGENT_BROWSER_IDLE_TIMEOUT_MS=1800000`。这是建议值，不是已应用配置；等待人操作或长异步任务需按任务设置更长的期限。
3. 在实际启动入口注入环境，而不是只修改某个终端配置；已有 daemon 不会因后来设置环境变量而自动改变策略，需要获准后有序关闭并重建。
4. Dashboard 按需启动、按需停止；默认不暴露公网。实时画面和网络/存储信息可能包含敏感内容，只用于本机观察。
5. 收尾优先原生命令 close；核验会话、daemon、浏览器树。关闭失败保留明确失败状态，不报告为已关闭；强制终止前重新核验身份，不用全局 pkill Chrome。
6. 正常任务收尾不使用 close --all，不影响其他 Agent 或普通 Chrome；不删除 profile，不清空登录状态。

本机查看/关闭的原生命令示例（本调研未执行启动或关闭）：

```bash
agent-browser session list --json
agent-browser dashboard start
agent-browser --session <明确会话名> close
agent-browser dashboard stop
```

## 4. 原生能力仍有的缺口

现有证据没有证明原生 Dashboard 已提供任务 owner、业务忙闲、按浏览器树汇总的 CPU/内存、关闭后操作系统级无残留证明、跨 Agent 原子并发限制。

只有试用后确认需要这些信息，再加一个薄的本机入口，复用原生 CLI：记录 owner/用途、汇总进程树、验收关闭。若需要强制配额或租约，必须保证所有调用入口经过该入口；仅写 Skill 规则属于软约束，不能声称强制生效。

不先开发新 Dashboard、不引入常驻 watchdog、不迁移 Browserless。若未来明确需要崩溃后实时告警、持续高 CPU 告警或硬并发上限，再单独设计；空闲超时不是 CPU 限流，也无法处理外部持续发命令保活的情况。

## 5. 实施后的最小验收（尚未执行）

- 两个不同任务可辨识且互不串会话。
- 关闭 A 后，A 的 daemon 和浏览器树退出，B 与普通 Chrome 不受影响。
- 成功、失败、取消三种任务均进入关闭路径。
- 用临时 profile 与短测试超时验证无人发命令后自动退出；不用真实登录 profile 做破坏性测试。
- 验证“页面仍有后台 JS，但无 CLI 命令”的会话可在超时后被回收。
- 长命令、等待人工和明确保留会话不被错误承诺为安全，实际测试策略后再确认。
- 关闭后重新加载 profile 能复用仍有效的登录；profile 未被删除。
- Dashboard 停止后其后台进程和监听退出。

## 来源

1. 本机版本匹配 README：`/Users/ziyun/.node/lib/node_modules/agent-browser/README.md`，Sessions、Observability Dashboard、Architecture。
2. [agent-browser 官方仓库](https://github.com/vercel-labs/agent-browser)
3. [0.27.0 daemon 源码](https://github.com/vercel-labs/agent-browser/blob/v0.27.0/cli/src/native/daemon.rs)（通过 GitHub contents API 读取）
4. [0.27.0 Dashboard 会话树源码](https://github.com/vercel-labs/agent-browser/blob/v0.27.0/packages/dashboard/src/components/session-tree.tsx)（通过 GitHub contents API 读取）
5. [官方 Dashboard 文档](https://agent-browser.dev/dashboard)（滚动文档，新版能力不能直接认定本机具备）
6. [v0.33.1 Release](https://github.com/vercel-labs/agent-browser/releases/tag/v0.33.1)
7. [Browserless Docker 配置](https://docs.browserless.io/enterprise/docker/config)

说明：部分 raw.githubusercontent.com 抓取失败后改用 GitHub API 成功读取指定版本源码；未修改网络配置。未委派子 Agent，不宣称独立审查或运行验收完成。
