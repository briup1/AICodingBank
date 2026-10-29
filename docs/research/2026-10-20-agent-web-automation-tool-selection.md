# Agent 网页自动化工具选型：Playwright / Browser Use / OpenCLI / ego lite

调研日期：2026-10-20。

范围：官方文档、官方仓库与本机只读核对；不安装、升级、卸载或迁移工具，不操作业务页面，不做成功率、速度与成本的横向实测。ego 按 citrolabs/ego-lite 理解；若用户指其他同名产品，需重新核对该部分。

## 结论

针对“我已有 Pi / Codex 等 Agent，希望它替我在已登录网站上查询、点击、填写”的当前目标，建议：

- **OpenCLI：日常网页操作唯一默认入口。** 已安装，并已有工作台入口，不需要先引进新浏览器。
- **Playwright：保留在项目内，承担确定性脚本与回归测试。** 不作为日常操作的另一套随机备选入口。
- **Browser Use：保留安装，暂不承接与 OpenCLI 重叠的任务。** 以后明确需要把自主网页 Agent 嵌入产品或交给托管服务运行时再评估；其 CLI 本身也能服务现有 Agent，并非只能启动第二个 Agent。
- **ego lite：先观察，不安装。** 当“人机抢窗口、任务可见性和人工接管”成为持续阻断，再作为替换日常主入口的候选，不叠在 OpenCLI 后面。
- **agent-browser：现有专用登录与控制台的兼容例外，不新增通用入口。** 未迁移前保留；现有控制台不管理 OpenCLI / Browser Use / Playwright。

这是一条基于现有投入与职责匹配的推荐，不是“OpenCLI 已被实测证明比其他产品更强”。

## 1. 先看一条完整链路

```text
用户提出目标
  → Agent 判断下一步
  → 工具把页面变成可读信息
  → 工具执行点击、填写、选择
  → 浏览器及网站真正运行
  → Agent 回读业务结果
  → 收尾自己创建的标签页或会话
```

关键不是谁有 click / fill，而是谁负责判断、谁提供浏览器、如何使用登录态、谁验结果和收尾。

### Playwright：程序控制浏览器的工具箱

```text
人或 Agent 写步骤 → Playwright 执行 → 浏览器 → 断言/结果
```

Playwright Library 提供启动与控制浏览器的 API；Playwright Test 在此基础上增加测试运行、断言、隔离、报告等。它自身不把自然语言目标变成自主决策循环，但 Agent 可以动态生成并执行 Playwright 代码。定位与自动等待能降低一部分交互不稳定性，不能替代业务结果判断。[S1][S2][S3]

例子：固定流程“打开客户页 → 填固定字段 → 点击保存 → 断言新增行存在”。适合经常重复、步骤明确、要放进 CI 的任务。登录态可以保存和复用，并非“Playwright 天生不能登录”；需要显式管理，不自动继承正在使用的 Chrome 登录态。[S4]

### Browser Use：既有自主 Agent，也有给现有 Agent 用的入口

自主运行方式：

```text
目标 → Browser Use Agent + 模型 → 看页面/决策/动作循环 → 浏览器 → 结果
```

CLI / Browser Harness 方式：

```text
现有 Pi / Codex → Browser Use CLI / Harness → 浏览器 → 现有 Agent 判断
```

官方区分开源库、CLI、云浏览器和托管 Agent。使用云浏览器不等于把 Agent 也托管；本地使用也不必选其云服务。开源库适合把网页自动化 Agent 嵌进自己的软件；CLI 则与 OpenCLI 的日常操作入口重叠。[S5][S6][S7]

本机 0.13.10 的 cli.py 明确标注由 Browser Harness 支撑，依赖中含 cdp-use；不应沿用“Browser Use 永远就是套 Playwright”这样的旧概括。也不应把此版本 CLI 的接口说明与旧版命令混用。

### OpenCLI：给现有 Agent 一个网页操作入口，也可沉淀站点命令

```text
现有 Agent → OpenCLI → 本机 daemon / Browser Bridge 扩展 → 已登录 Chrome
```

有两种工作方式：

1. 没有站点适配器：照样可以读取页面、点击、填写、选择、等待和截图。
2. 流程稳定后：做成某站点的固定命令，减少每次重新找按钮。

因此它不是“只能查热榜或抓数据”，也不是一个完整的自主决策 Agent。官方 README 中的“run Browser Use”语句不能单独作为其依赖 browser-use Python 包的证据；实际架构、包与接口要分别核对。[S8][S9]

注意：适配器可能直接读取接口数据，不一定真的走了可见 UI；这种结果可以证明查询完成，不能自动证明页面交互验收通过。

### ego lite：把浏览器本身也做成人机协作的产品

```text
现有 Agent → ego-browser JS 工具 → ego lite 浏览器中的 TaskSpace → 页面
人使用自己的 Space，并在需要时接管 Agent 的任务
```

官方提供 Chromium 浏览器应用与配套 Agent 工具，主打任务空间、可见控制与登录数据迁移。它不是“给现有 Chrome 多装一个扩展”；采用它意味着引入另一款浏览器及其数据管理方式。[S10]

仓库的自动化工具层与 Skill 开源；浏览器应用本身是独立闭源程序，不能把仓库的 MIT 许可证当作整个浏览器开源的证据。[S11]

其 JS API 并不等于 Playwright API，名称相近也不能直接照搬 Playwright 代码。官方文档要求普通 DOM 操作优先用页面快照和语义选择器，并支持截图、人工交接与 TaskSpace 收尾；不是只能盲点坐标。[S12]

官方声称的速度、Token 和成功率提升属于厂商测试，未在用户任务上复现，本报告不据此选型。Space 的任务组织也不自动等于企业身份/权限隔离；采用前需另验。[S10][S12]

## 2. 本机实际证据

| 项目 | 已观察到的事实 | 不能据此宣称 |
| --- | --- | --- |
| OpenCLI | npm 全局包 @jackwener/opencli 1.8.8；本机 help 显示浏览器命令与扩展更新提示 | 扩展连接、目标账号和真实填表链路当前健康 |
| Browser Use | uv tool 登记 browser-use 0.13.10；包和 CLI 源码存在 | 所有 shell 都能直接找到命令，或浏览器已连通 |
| Playwright | 本地上下文登记 MediaCrawler 使用 1.61.0；ms-playwright 缓存有多个 Chromium revision | 各项目依赖版本已统一、所有浏览器当前均能启动 |
| agent-browser | npm 全局包 0.27.0；现有控制台源码及应用入口存在 | 它能控制其他浏览器工具，或控制台当前运行健康 |
| ego lite | 常规 /Applications 与用户 Applications 目录未找到名称匹配项 | 已彻底排除所有自定义路径安装 |

检查入口：`npm list -g --depth=0`、`uv tool list`、`opencli --version`、`opencli browser --help`、包元数据、缓存目录和工作台现有文件。未读取 Cookie、口令或业务页面。

### 已存在的入口分叉

- `/Users/ziyun/workdir/self_project/AICodingBank/tools/skills/shared/wl-web-auto/SKILL.md`：指定网页操作使用 OpenCLI。
- `/Users/ziyun/.agents/skills/hgj-session/SKILL.md`：专用登录链路仍引用 agent-browser。
- `/Users/ziyun/workdir/self_project/AICodingBank/tools/integrations/browser-console/README.md`：macOS 入口包装的是 agent-browser Dashboard，不是所有浏览器工具的统一控制台。

### 一个具体版本错位

现有 wl-web-auto 文本提到 `--session` 参数，而本机 OpenCLI 1.8.8 help 要求 session 位置参数：

```text
本机 1.8.8：opencli browser work open https://example.com
当前 main 文档：opencli browser open https://example.com --session work
```

本机版本对应的官方 tag 文档也使用位置参数。[S8] 这不证明现有入口完全不可用，但说明执行前必须按本机 help 核对，不能把滚动文档命令直接套到旧安装上。本次只记录，不修 Skill，不升级。

## 3. 为什么会“打架”

安装多个工具通常不会自己冲突；冲突出现在执行与规则层：

1. 多个 Skill 都声称“凡是浏览器都默认用我”，Agent 每次选不同入口。
2. 多个驱动同时操作同一标签页，A 正在填写，B 把页面导航走。
3. 多套登录 profile 并存，A 工具登录成功，不代表 B 工具使用同一账号。
4. 控制台只能看到一种工具，却被当作“整个电脑的自动化总览”。
5. 看到点击返回成功就重试提交，实际第一次已写入，造成重复业务操作。

同一登录 profile 的多个 tab/session 不等于账号隔离。公司切企业、权限和登录上下文必须按实际浏览器 profile 与站点规则核验；不能只靠任务名区分。

## 4. 如何选一个并用精

### 当前主线

```text
旧：目标 → Agent 临时挑工具 → 不同浏览器/账号/结果标准 → 难追踪
新：目标 → 现有 Agent → OpenCLI → 明确 profile + 独占 tab
         → 回读业务结果 → 只释放/关闭自己创建的资源
```

例子：“把客户资料填好，先别提交”。Agent 应先确认页面与账号，再填姓名、手机号、下拉候选，最后回读实际表单值并停在提交前。不能因工具具备 submit 能力就扩大授权。

例子：“按已确认规则新增客户”。提交后应回读新增客户或回执；超时则先查是否成功，不能直接再点一次。

### 第一轮只练三类任务

| 任务 | 真正通过标准 |
| --- | --- |
| 查询与跨页整理 | 指定账号、正确条件、正确结果和来源 |
| 复杂填写但不提交 | 文本、异步下拉、日期或表格的实际值正确，未越权提交 |
| 一次获授权的提交 | 得到业务回执或可回读记录，异常不重复写，任务结束资源收尾 |

先在安全夹具、获准测试环境或用户明确授权的目标内验证。记录能否完成、耗时/调用开销、是否需人工接管、有无重复提交与遗留标签；没有具体失败证据，不增加第二个默认工具。

### 重复后固化，不是叠工具

```text
低频/变化多：Agent → OpenCLI 读页面并决定
高频/稳定：Agent → 同一 OpenCLI 下的站点命令
项目回归：测试任务 → Playwright 固定脚本与断言
```

固定脚本也需要版本维护，Agent 自动生成代码不等于无需维护。API 型命令不拿来替代必须验证真实点击/填写的 UI 用例。

### 何时考虑换主线

- 若持续卡在人机抢控制、人工接管或可见任务管理：拿相同的代表任务单独试 ego lite，结果更好再替换日常入口。
- 若在开发一个能自主收任务、运行网页工作并回传结构化结果的产品：评估 Browser Use 开源 Agent 或托管方案；它不是当前日常助手的必需层。
- 若流程已完全明确并要求可靠重复或 CI：进入项目内 Playwright 脚本路线，不必每轮都让模型重新规划。

当前无需卸载。先统一任务路由比删除包更有价值；专用登录与控制台要先核对直接调用方，再另行授权迁移。

## 5. 边界与未验证项

- 没有横向运行四个工具，没有得出客观性能排名。
- 没有验证 OpenCLI 扩展与实际网站兼容性，当前推荐需通过上述代表任务确认。
- 没有声称“本地浏览器数据”意味着模型请求不出机器；发给模型的页面文本/截图另受模型与配置影响。
- 不自动迁移普通 Chrome 数据，不清理现有浏览器会话，不把旧登录链路强切到新工具。
- 本轮只新增调研文档；不改默认规则、Skill、服务或工具安装。
- 通过已加载 OpenViking MCP 读取了自动化浏览器使用偏好与控制台历史方案；Experience 定向检索无命中，未向 OpenViking 主动写入资料。历史只作背景，安装状态以本轮本机证据为准。实际读取的资源：
  - `viking://user/default/peers/github.com-briup1-aicodingbank/memories/preferences/yuxi/自动化浏览器使用体验.md`
  - `viking://user/default/peers/github.com-briup1-aicodingbank/memories/events/2026/10/19/自动化浏览器控制台产品化方案.md`

## 来源

以下滚动来源按 2026-10-20 获取；涉及本机版本的行为优先参考 tag 与本机 help。

- [S1] Playwright Library：https://playwright.dev/docs/library
- [S2] Playwright Test：https://playwright.dev/docs/intro
- [S3] Playwright actionability / auto-waiting：https://playwright.dev/docs/actionability
- [S4] Playwright authentication：https://playwright.dev/docs/auth
- [S5] Browser Use 本机对应版本 README：https://github.com/browser-use/browser-use/blob/0.13.10/README.md
- [S6] Browser Use 当前产品与用法说明：https://github.com/browser-use/browser-use
- [S7] Browser Harness：https://github.com/browser-use/browser-harness
- [S8] OpenCLI 1.8.8 README：https://github.com/jackwener/OpenCLI/blob/v1.8.8/README.md
- [S9] OpenCLI 当前 README：https://github.com/jackwener/OpenCLI
- [S10] ego lite README：https://github.com/citrolabs/ego-lite
- [S11] ego lite 仓库范围与架构：https://github.com/citrolabs/ego-lite/blob/main/AGENTS.md
- [S12] ego-browser 当前 API 与任务生命周期：https://github.com/citrolabs/ego-lite/blob/main/package/ego-browser/skill-body/SKILL.md
