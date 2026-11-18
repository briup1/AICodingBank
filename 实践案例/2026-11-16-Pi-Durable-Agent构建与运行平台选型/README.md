---
title: "Pi Durable：构建 Agent 与选择运行平台"
date: 2026-11-16
date_basis: recorded-date
updated: 2026-11-16
category: 技术
tags: [Pi Durable, Agent, 运行时, 持久化, 故障恢复, 工具调用]
status: partial
source:
  - "https://github.com/earendil-works/pi/tree/main/packages/durable"
  - "https://earendil.com/posts/pi-durable/"
  - "https://developers.cloudflare.com/agents/harnesses/pi/"
  - "https://vercel.com/docs/agent-harnesses/pi"
  - "https://temporal.io/blog/the-immortal-life-of-pi-running-the-pi-coding-agent-on-temporal"
  - "autotariff-agent，commit 0fb572e；项目本地源码及 2026-11-16 测试"
---

# Pi Durable：构建 Agent 与选择运行平台

**一句话：Pi Durable 保存并恢复 Agent 执行；宿主负责进程、唤醒和客户端；业务系统负责业务正确性与外部副作用。** 三者不能互相替代。

## 1. 问题与适用条件

为本地工具、Web 工作台或后台服务构建能够调用模型和工具、记录执行、支持恢复的 Agent。本文帮助决定何时使用本地 Pi Durable，何时引入云运行时或工作流平台；也说明如何借鉴运价抽取项目的业务边界。

适用前提：TypeScript/JavaScript 运行环境，使用 `@earendil-works/pi-durable`；API 与版本相关。Pi Durable 是实验性包，升级前核对官方文档、版本兼容及持久化格式。本文访问和记录日期为 2026-11-16，外部资料会变化。

贯穿示例：用户说「读取运价表，发现抽取差异就修复」。

```text
请求被接收 → Pi 判断并调用工具 → 程序抽取 → 独立检查 → 有差异则修复 → 人工复核
                   ↓               ↓             ↓
                会话任务          文件和账本      业务结论
```

## 2. 三层职责

| 层 | 负责什么 | 不保证什么 |
| --- | --- | --- |
| Pi Durable | Conversation、模型与工具任务、检查点、submission、文档状态、观察 | 自动提供外部系统幂等、多租户鉴权、业务正确性 |
| 运行宿主 | 启动/唤醒进程、路由、访问控制、客户端连接、工作区和隔离 | 只靠重启不保证外部文件和收费动作一致 |
| 业务系统 | 业务状态、权限、预算、产物、审批、对账与独立检查 | 不应把模型自述当业务成功证据 |

`requestId` 用于同一会话的 submission 去重；它不保证邮件、支付、发布等外部动作恰好执行一次。业务副作用必须有自己的幂等键或结果核对流程。

## 3. 核心组件与最小接入

| 组件 | 作用 |
| --- | --- |
| `Storage` | 保存会话、任务、submission 和文档；可使用 SQLite、JSONL 或其他适配器 |
| `Harness` | 在存储上运行 Agent 任务调度 |
| `Conversation` / `root` | 一段对话及其 Agent 配置 |
| `Extension` / `Tool` | 注册提示词、工具、Hook 和自定义任务 |
| `submit` / `wait` | 持久接收输入并等待结果；稳定 `requestId` 可去重 |
| `watch` | 观察会话视图；WebSocket、SSE、轮询或 IPC 由宿主选择 |
| `Document` | 可与 Pi 的 entries、tasks 在同一次 Pi commit 中提交的 JSON 状态 |
| `resume` | 开始恢复未完成的任务；宿主仍须负责重新启动并打开正确的存储 |

最小骨架（说明结构，模型配置和异常处理需按使用版本补全；不是本讲义已独立运行的完整程序）：

```ts
const registry = createRegistry();
registry.install(extension); // 业务工具及其提示词
const storage = await openNodeSqliteStorage("./agent.sqlite");
const harness = await Harness.open(storage, { models, registry }, context);
try {
  const root = await harness.root(context, { agent });
  harness.resume();
  const submission = await root.submit({
    type: "input",
    requestId: "stable-request-42",
    content: "读取运价表，发现抽取差异就修复",
  }, context);
  const result = await submission.wait(context);
  // 应用检查 result，再对外展示已提交的结果。
} finally {
  await harness.close(context);
}
```

`submit()` 或 `wait()` 也可启动调度器；显式 `resume()` 更适合作为需要恢复后台任务的宿主启动步骤。它不负责在机器宕机后重新启动进程，也不自动恢复外部文件系统。

## 4. 四种接法：区别是宿主如何运行和恢复

| 方案 | Agent 状态 | 谁负责唤醒 / 接管 | 文件执行环境 | 适用条件与代价 |
| --- | --- | --- | --- | --- |
| 官方 Node + SQLite | 本地 SQLite | 人或进程管理器重启；打开原存储后恢复 | 本机文件系统或自定义执行环境 | 最适合单机起步；需要自己设计自动启动、隔离和备份 |
| Cloudflare Durable Objects | 对象的 SQLite，Pi 表独立 | PiHarness / Lifecycle 用 Alarm 唤醒对象 | 可接 Cloudflare Workspace / Worker | 适合对象式长期会话；依赖平台生命周期与运行限制 |
| Vercel `durable-harness/pi-durable` | Workflow SDK World | `resumeWith` + Queue / Flow Handler 重新打开 Harness | `virtualEnv()` 或 `sandboxEnv()` | 适合 Serverless 聊天产品；需处理会话接管、费用和鉴权 |
| Temporal `pi-temporal` | Temporal History + Pi session 文件 | Temporal 把工作交给可用 Worker | Worker 目录，示例通过共享存储与 Git bundle 同步 | 适合研究跨机器接管；要承担共享存储、租约、部署复杂度 |

**不要混淆：**Temporal `pi-temporal` 是 Pi coding agent + Temporal Workflow 的对照实现，并非直接使用 `@earendil-works/pi-durable` 的同类适配器。Cloudflare 和 Vercel 的对应方案直接使用 Pi Durable。Vercel 另有 `durable-harness/pi`，只接 Pi Agent Loop，不等同于 `durable-harness/pi-durable` 完整 Harness。

三种公开代码入口：

1. [Cloudflare Pi Durable 示例](https://github.com/earendil-works/pi-durable-cloudflare)：`src/chat.ts` 定义模型和工具；`src/session.ts` 连接 SQLite、WebSocket、Alarm；`test/` 展示恢复、调度、fork。仓库明确是无鉴权、无限流的示例，不可直接作为公开生产服务。
2. [Cloudflare Agents PiHarness 示例](https://github.com/ethinx/pi-harness-example)：`src/workspace.ts` 将 Workspace 工具接入 Pi，`src/sockets.ts`、`src/view.ts` 管客户端投影；Workspace 的文件与 Pi 会话状态各有职责。
3. [Vercel durable-harness](https://github.com/vercel-labs/durable-harness)：`durable-harness/pi-durable` 配合 `openWorldStorage()`、`resumeWith()`、`chatRoute()`、Queue；也支持自托管 World，实际配置以对应版本文档为准。

Temporal 的 [pi-temporal](https://github.com/temporalio/pi-temporal) 是第四个**对照**案例，不计作上述三个 Pi Durable 直接使用案例。

### 为什么实现不同

```text
Node 进程可由本机管理        → 重新打开 SQLite
Durable Object 可能休眠     → Alarm 唤醒
Serverless Function 可消失  → Queue 投递到新 Function
Worker 可能在另一台机器接管 → Workflow + 共享会话及文件状态
```

Agent 状态恢复不等于工具工作空间恢复。无论选择哪一条链，都要核对新进程能否访问原文件、产物及外部系统。模型调用中断后可能重试并产生费用；部分结果和最终提交之间存在恢复边界。

## 5. 设计工具：先分类，再声明 replay

| 操作 | 建议策略 | 必须验证 |
| --- | --- | --- |
| 查询状态、读取文件 | 可考虑 `replay: "safe"` | 多次读取是否确实无副作用；查询结果变化是否影响判断 |
| 确定性本地生成 | 满足条件时才标 safe | 输入固定、输出隔离或不可变、重复写安全、子进程中断可处理 |
| 远端创建 / 发消息 | 默认不自动重放 | 下游是否支持稳定幂等键、结果是否可查询 |
| 扣费、发布、删除 | 默认不自动重放，结果不明时阻断或对账 | 是否已经生效、审批及补偿措施 |

工具执行成功但结果未提交时，外部动作可能已经发生。**“未看到结果”不等于“没有执行”。** Pi 的安全重放声明由工具作者负责；宿主必须独立核对外部副作用、资源权限和恢复边界。

## 6. 本地项目的实际参考：autotariff-agent

**事实快照**：2026-11-16 检查的代码处于 commit `0fb572e`；本项目依赖锁定的 Pi Durable、Pi AI 和 Chord 均为 1.5.0。项目事实会变化，以当前源码为准。

```text
工作台消息 → 建业务 run → 打开该 run 的 Pi SQLite → submit(requestId)
                                                  ↓
                        业务工具 → 动作账本 → 原件/脚本/报告 → 独立检查
```

- `src/index.ts`：`Harness.open()`、注册扩展、`root.submit()`、`wait()`、`watch()`。
- `src/closure/runtime.ts`：将原文盘点、抽取、后处理和检查注册为 Pi 工具。
- `src/closure/ledger.ts`、`src/closure/controller.ts`：记录业务动作、预算和状态；`ArtifactStore` 保存独立产物并校验摘要。
- Web 会话是产品层对象；终态后的追问创建关联的新 run，历史证据保留，不等同于无限复用同一个 Pi Conversation。
- `src/resume.ts` 是显式业务恢复入口。当前 `runPi` 未显式调用 `harness.resume()`；不能据此宣称完整后台任务自动接管。

参考意义是**分层与验证方法**，不是照搬运价项目的表、状态名、路径或预算规则。Pi SQLite、Closure SQLite、文件产物不共享一个原子提交；需用稳定身份、回执、摘要与协调恢复处理提交间隙。

待验证风险：通用工具包装器统一标记 `replay: "safe"`；Ledger 和不可变产物提供保护，但不能仅凭测试全绿断言每个工具的所有崩溃窗口均安全。需要按工具和故障点验证。

## 7. 从零构建时的检查顺序

1. **划定边界**：一次任务还是长期会话；单用户还是多用户；本地还是云端；是否必须自动接管。
2. **选运行宿主**：先满足执行环境与故障恢复要求，再选 SQLite、对象存储或工作流平台；不用为了“更高级”提前引入分布式系统。
3. **定义会话与身份**：明确用户、session、run、requestId 的对应关系及重试作用域；宿主做鉴权和隔离。
4. **装配 Harness**：注册模型和最小工具集，接入 Storage，明确提交、观察、取消、关闭、恢复的生命周期。
5. **逐个评估工具**：确定权限、执行位置、稳定动作身份、幂等、重放、超时、取消及外部副作用；不把普通工具说明当安全边界。
6. **设计权威事实**：确定业务数据库、Pi 会话、文件产物的所有权；需要跨存储时设计中断后对账，不能声称原子一致。
7. **做故障演练**：提交前后、模型请求中、工具外部动作前后、回执落库前后分别中断；验证同请求重试、旧 Worker 迟到、文件重建及费用上限。
8. **产品化检查**：检查身份鉴权、租户隔离、限流、成本、密钥、日志脱敏、可观测性、备份恢复、升级/回滚与存储兼容。

自动恢复可能重发模型请求；收费和不可逆外部动作如果没有完整回执，先核对再重试。Pi 会话的版本迁移与平台版本兼容应在升级前测试，不能假定旧版本可读取新存储。

## 8. 调查、验证与未覆盖

| 路径 | 已做 | 结论边界 |
| --- | --- | --- |
| Pi 官方 Node SQLite | 阅读官方文档并核对本项目实际调用 | 证明使用了官方核心接口；不证明所有崩溃恢复路径 |
| Cloudflare、Vercel | 阅读官方文档及公开示例 README | 属资料调研；未部署或运行示例 |
| Temporal | 阅读官方博客和公开仓库说明 | 作为其他执行引擎对照；未部署或运行混沌实验 |
| autotariff-agent | 读源码和设计；2026-11-16 `npm run typecheck -- --pretty false` 通过，`npm test -- --reporter=dot` 为 28 个文件、234 项通过 | 是该工作区当时的测试结果；不等于生产、全故障窗口或真实业务准确率验收 |

之前对话曾把“设计合理”表述得过于肯定：更准确的结论是本地受控范围内分层有依据，工具 replay、跨存储协调及自动恢复仍应通过故障注入逐项证明。先前示例中将 Ledger、Pi SQLite 和文件描述为一次原子提交也不准确；三者不共享事务。

未执行新建云服务、第三方项目部署、线上数据操作、收费模型调用，未安装或配置上述平台。外部文档与本机源码可能继续变化。

## 9. 下次使用与失效条件

新项目从第 7 节开始；按实际需求选择第 4 节平台，并回到第 5 节逐工具决策。Pi Durable API、存储格式、平台版本或 Agent 的权限和运行环境变化时重核官方资料并重做相关恢复演练。此记录不授予未来项目访问凭据、发送代码、部署或消费模型费用的权限。

## 10. 来源与修订

- [Pi Durable 官方 README](https://github.com/earendil-works/pi/tree/main/packages/durable)；[官方设计介绍](https://earendil.com/posts/pi-durable/)。
- [Cloudflare Pi Harness 文档](https://developers.cloudflare.com/agents/harnesses/pi/)；[Cloudflare 示例](https://github.com/earendil-works/pi-durable-cloudflare)；[Agents Workspace 示例](https://github.com/ethinx/pi-harness-example)。
- [Vercel Pi 文档](https://vercel.com/docs/agent-harnesses/pi)；[durable-harness 源码](https://github.com/vercel-labs/durable-harness)。
- [Temporal 的 Pi 方案说明](https://temporal.io/blog/the-immortal-life-of-pi-running-the-pi-coding-agent-on-temporal)；[pi-temporal 源码](https://github.com/temporalio/pi-temporal)。
- 本机项目源码：`/Users/ziyun/workdir/remote_project/autotariff-agent/src/index.ts`、`src/closure/runtime.ts`、`src/closure/ledger.ts`、`src/resume.ts`、`docs/design-synthesis.md`。这些本机路径仅供当前机器定位，不保证其他机器存在。

2026-11-16：依据公开资料和本项目代码形成讲义；跨平台部分尚未实际部署，状态为 partial。
