# OpenViking：已有项目开发与跨会话记忆——使用实践调研

- 核验日期：2026-10-11。
- 限定场景：AI 在已有代码项目中改功能/修 Bug，并在后续会话复用项目知识、决策和排障经验。
- 范围：只筛选非官方、作者本人安装/测试的博客；不重复官方 coding-agent 博客、插件文档或 Codex 文档。
- 检索预算实际使用：3 次 web search 调用（共 4 条查询）、打开 2 篇候选文章（含同一候选的只读 HTTP 重试）；随后停止。
- 未安装、未执行任何文章命令、未运行测试；只作公开资料筛选。

## 结论

**本轮未找到达到限定场景及一手亲测证据门槛的可靠第三方博客，严格推荐数量为 0。**
这只是本轮有限检索的结果，不代表互联网不存在此类文章，也不代表 OpenViking 无法用于该场景。
“教程有安装命令”“标题写实战”“平台标原创”均不等于作者实际跑过。

## 候选 1：可作背景阅读，不是亲测最佳实践

- 标题：OpenViking Setup: Long-Term Memory for Claude Code and Codex。
- URL：https://genztech.blog/p/openviking-setup-guide/
- 作者：Kore D；页面署名 Founder, CEO & Writer。
- 发布日期：2026-08-20（原文日期，搜索摘要曾显示“上月”，以原文为准）。
- 阅读状态：已打开正文。
- 是否一手：**未找到作者本人安装/测试的明确证据；归为官方资料整理＋作者分析，不列为亲测。**
- 有用信息：作者明确把 LoCoMo / tau2-bench 数字归为厂商报告；适合提醒读者不要将它们当独立复现结果。文章也讨论了维护服务与模型端点的额外负担，以及单项目本地 Markdown 记忆与多项目服务化记忆的取舍。
- 可复核依据：正文“Primary sources”列出官方仓库、Release、Quick Start、插件和官方 benchmark；“Our take”是观点分析。虽提供安装/验证步骤，没有给出本人执行日志、自己的测试数据或修 Bug 前后对照。
- 证据缺口：没有具体已有项目、功能修改/缺陷、首次会话沉淀内容、新会话召回内容及代码/测试结果；不能证明复用记忆改善开发效果。
- 时效限制：文章围绕当时 v0.4.15，不能把安装命令、默认行为或架构描述直接视为 2026-10-11 的现状；本任务未再次核验其技术步骤。

## 候选 2：确认是平台 AIGC，不推荐

- 标题：Claude Code 长时记忆评测实战：基于 OpenViking 的 LoCoMo 四路径复现与对比指南。
- URL：https://blog.gitcode.com/5f40991029c1acdf66817bea433a059a.html
- 作者/生产方：页面未见具名测试作者，版权声明明确为 AtomGit 博客平台 AIGC 生成并经审核发布。
- 发布日期：2026-09-08 22:33:31（页面原文）。
- 阅读状态：web 初次打开超时，后用只读 HTTP 获取同一文章 HTML；页面可见版权声明，嵌入的正文围绕官方 benchmark 源文件讲解。
- 是否一手：**不属于具名作者本人安装/测试的报告；确认排除。** 标“原创”不改变其平台 AIGC 身份。
- 有用信息：介绍 benchmark/locomo/claudecode 的四条评测路径及运行流程，只能作官方套件解读，不能充当独立复现实验结果。
- 证据缺口：没有作者本人运行日志、自己测得的结果或已有代码项目改功能/修 Bug 的前后验收；LoCoMo 长对话问答不等于代码仓库开发效果。

## 被排除的近似候选（未打开）

- 标题：Claude Code 长期记忆集成指南：OpenViking 记忆插件的安装、配置与工作原理。
- URL：https://blog.gitcode.com/1d5c3d57b20515260210c2e1f951a420.html
- 作者：未核实；搜索摘要显示发布日期 2026-09-09 21:35:25，并标“原创”。
- 分类：摘要主要介绍官方插件安装、配置和 Hook；没有可见的本人测试结果。“原创”不能充当亲测证据，因此不推荐。

## 第三方证据缺口

现有第三方候选不能补上这条实测链：已有仓库真实任务 → 首轮解决并沉淀项目知识/经验 → 关闭会话 → 新会话召回正确项目记忆 → 完成后续修改/排障 → 测试或变更记录证明结果。
若需要宣称“第三方验证的最佳实践”，还需这条链及失败/误召回案例；本轮没有找到，不用教程或厂商数字补位。

## 官方最佳实践与可复现实验（负责人补充）

### 推荐阅读

1. OpenViking Team，《Memory That Follows You: OpenViking × Agent Harness》，2026-09-07。两独立 Python 项目、Claude Code → Codex，比较关闭/开启记忆，追踪实际记忆文件与注入内容；含中文指南与约一小时录屏。录屏 15:55 开始跨工具实验。文章也披露无 OpenViking 时 Codex 曾读取相邻项目找回偏好，所以只看配置结果不能证明是记忆生效。
   - https://blog.openviking.ai/post/openviking-agent-harness/
2. tosaki，《OpenViking for Claude Code & Codex: Give Your Coding Agent Persistent Memory》，2026-05-20 发布，2026-10-04 更新。讲 Hooks 自动召回/捕获、MCP 主动操作、归档提取、项目作用域及故障排查；是官方一手工程文章，不是独立第三方效果评测。
   - https://blog.openviking.ai/post/openviking-coding-agent/
3. 当前 Codex 接入文档。实际安装以本文及对应发行版本为准，不沿用旧博客或搜索摘要中的插件名/命令。
   - https://docs.openviking.ai/en/agent-integrations/04-codex
   - https://github.com/volcengine/OpenViking/blob/main/docs/en/agent-integrations/04-codex.md
4. 客户端配置（写入项目身份与召回范围不是一回事）。
   - https://docs.openviking.ai/en/configuration/02-client
5. OpenAI 官方 Hooks 文档（安装插件不等于信任其 Hooks）。
   - https://learn.chatgpt.com/docs/hooks

### 当前使用链路

进入项目启动 Codex → SessionStart 注入用户资料/索引 → 每次 UserPromptSubmit 召回相关记忆 → Agent 查当前源码、修改并验证 → Stop 捕获会话 → PreCompact/正常 SessionEnd 等事件提交 → 服务器异步提取长期记忆 → 下一次会话继续召回。

只有 MCP 工具可用，不代表自动读写链路启用；专用插件的 Hooks 必须经审核、信任且启用。

### 手动接入（仅说明，未执行）

- 前置：运行中的 OpenViking 服务、可用模型配置、连接 URL 和适用的用户凭证；不要用 root key 代替用户身份。
- 当前 main 文档：Node.js >=22，手动安装最低 Codex >=0.130；若依赖正常退出的 SessionEnd，则要求 >=0.145。
- 连接文件：`/Users/ziyun/.openviking/ovcli.conf`，至少配置服务连接及凭证。
- 当前命令：

```bash
codex plugin marketplace add volcengine/OpenViking
codex plugin add openviking-memory@openviking
```

- 在 `/hooks` 审核并启用所需 Hooks，在 `/plugins` 确认插件启用。当前 OpenViking 文档仍提及 `plugin_hooks` 特性开关；OpenAI 当前 Hooks 文档描述 `hooks` 开关，不能在未核验具体 Codex 版本时擅自把其中一个配置键当成通用正确值。
- 调试可设 `OPENVIKING_DEBUG=1`，查看 `/Users/ziyun/.openviking/logs/codex-hooks.log`。
- 当前插件的正常 SessionEnd 不覆盖崩溃、kill 或直接关闭终端；这类会话依赖后续空闲恢复扫描。提交返回受理仍不代表提取完成。

### 针对本用户的最小试验建议（未实测）

1. 保留现有 AGENTS.md/知识库/Skills，不迁移全部资料；先试一个不含敏感资料的仓库。
2. 先用同一仓库跨新会话验证一条已确认的排障/决策结论，避免刚上手就同时验证多项目、多人、跨工具。
3. 先限制自动召回为 `OPENVIKING_RECALL_PEER_SCOPE=actor`（当前项目＋用户级记忆），避免其它项目的技术结论干扰；此配置不是权限边界。
4. 当前默认项目 peer 根据 Git origin 归一化生成，因此同仓库 clone/worktree 通常共用项目记忆；无远程仓库或需要显式分组时再配置稳定 peer id。
5. 每次沉淀写清结论、适用条件、验证证据和未验证部分；关键操作仍回当前源码/原始资料验证。
6. 成功标准：记忆文件实际存在＋新会话有该 URI 的召回记录＋后续代码/测试正确；“模型口头说记住了”或“最终答案碰巧正确”不够。
7. 对照试验避免 AGENTS.md、相邻项目或其它记忆插件含同一条测试信息，否则不能归因于 OpenViking。

### 验证与风险

本次只核对在线官方文档、官方演示和第三方来源质量，没有检查本机 Codex/Node 版本、安装插件、运行服务器或执行跨会话试验。专用插件可能将对话、回答及工具调用/输出发送到配置的服务，应用前应核对可接收的数据范围；生成的记忆仍可能错误，不能替代当前源码和已确认规则。
