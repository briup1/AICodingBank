# 渐进加载：宿主能力核验与 Python 试点方案

日期：2026-10-19。状态：只读核验与方案；未安装适配器、未完成运行时验收。

## 目标与范围

已确认原则以 ../../EXTENDING.md 的“已确认的目标：沿执行链路渐进加载”为准。项目经理接单读取简短董事长资料；专项正文只在相关文件、动作或意图触发时加载。当前不新增 preferences.local.md，不迁移既有规则。

本次交付：本机版本与可用机制的证据、现有加载问题、一个隔离 Python 试点方案。未修改用户级配置、启动子 Agent、安装插件或访问公司环境。

## 本机核验

执行 `command -v claude opencode codex pi` 及各 CLI 的 `--version`：

| 宿主 | 本机结果 | 已核实机制 | 尚未证明 |
| --- | --- | --- | --- |
| OpenCode | /Users/ziyun/.opencode/bin/opencode；1.19.3 | 官方文档描述 AGENTS 入口、instructions 合并加载、tool.execute.before 插件 | 本版本完整的递送/阻止/重试顺序；子会话继承 |
| Claude Code | 当前 shell 找不到 claude | 当前官方文档描述 paths 条件规则、工具前 Hook；路径规则可由读/写/编辑匹配文件触发 | 本机安装位置、版本、启用状态、实际触发；不能据此宣称未安装 |
| Codex | /Users/ziyun/.node/bin/codex；0.163.0 | 本机用户级 AGENTS 路由在当前调查上下文已有证据 | 官方 AGENTS 页面请求 403；GitHub 对应文档只跳转同页。条件规则、执行前注入能力待核验，不判断为不支持 |
| Pi | /Users/ziyun/.node/bin/pi；1.3.0 | 安装包文档说明上下文目录加载；扩展 tool_call 可阻止/修改调用，before_agent_start 可加入消息，context 可变换消息 | 组合后能否在原动作前让模型重新决策、压缩/重启与独立实例行为 |

本次不是全量插件审计；发现目录或配置不等于确认实际启用。也未因宿主提供接口就将本机标为已支持完整目标。

## 直接证据

### OpenCode

- https://opencode.ai/docs/rules/ ：instructions 中的 glob 匹配的是要加载的说明文件，所有匹配说明与 AGENTS 合并；不能当作 Claude paths 式的目标文件触发。
- https://opencode.ai/docs/plugins/ ：项目 .opencode/plugins 与用户级 plugins；tool.execute.before 可修改参数，示例通过抛错阻止读取；这不能单独证明模型在原工具执行前收到新正文并重新推理。
- /Users/ziyun/.config/opencode/plugins/ 当前包含 coding-metrics.ts、dev-guard.js。读取 dev-guard.js 确认其指向工作台既有 dev-guard 适配器，未审计其实现。
- /Users/ziyun/.config/opencode/opencode.jsonc 中 .py 的配置是 pyright LSP extensions；语言服务匹配不是规则注入。
- 当前会话实际收到用户级 AGENTS 和大量 Skill 描述。描述不等于正文，但也是常驻上下文成本；仅迁移 WORKBENCH.local.md 不足以解决整体问题。

### Claude Code

- https://code.claude.com/docs/en/memory#path-specific-rules ：paths 支持 glob，Read/Write/Edit 以及部分单文件 Bash 读取会触发；无 paths 则启动加载。
- 同页说明自然语言“请读 AGENTS”依赖模型主动打开；@ 导入属于自动展开且启动加载。当前仓库 CLAUDE 指针不能直接视为自动导入。
- 同页区分指令上下文和 Hook 执行控制；本次未进一步验证本机 Hook 契约。

### Pi（与安装版本一起分发的文档）

- /Users/ziyun/.node/lib/node_modules/@earendil-works/pi-coding-agent/docs/configuration.md:41-47：从 agent 目录、工作目录及父目录加载上下文。
- 同包 docs/extensions.md:104-106：before_agent_start 消息与 tool_call 修改/阻止。
- 同包 docs/extensions.md:116-125：context 变换、同一模型消息的工具调用可并行，不可假定兄弟调用先后顺序。
- /Users/ziyun/.pi/agent/extensions/ 存在 coding-metrics、dev-guard、herdr-agent-state、openviking 入口；仅核对目录，不据此推断其触发方式。

## 已发现的入口问题

1. WORKBENCH.local.md 将沟通偏好、Python 环境约束、工具接入、端口台账混放；根 AGENTS 使用入口要求读取该文件，容易一次加载全部。
2. 用户级 AGENTS 中仍有整体本机文件指针及专项工具说明。宿主启动已注入的正文，靠下游“不要读”无法移除。
3. 阶段路由不等于动作触发：编辑 .py、执行 uv、通过脚本启动容器是不同动作。
4. 工具前回调发生时模型已经生成工具参数。把正文交给回调后继续原命令，不等于模型依据规则重新决策。

## 推荐试点：OpenCode 项目级隔离适配

选择理由：当前使用宿主、本机版本可定位、官方有执行前接口。能力仍须验证，不先改全局插件。

### 最小结构

使用系统允许的临时目录内独立夹具，避开真实项目规则迁移。正式实现前核对 customize-opencode 指引与当前版本插件类型定义。

- 触发登记：规则 ID、事件类型、匹配条件、唯一正文路径；匹配器读取登记，不把整份登记递送模型。
- 两份试验规则：Python 文件编辑要求、Python 执行环境要求。使用无害标记验证递送；真实版本约束仍以现有本机规则为准。
- 项目级适配器：识别文件工具（含 apply_patch 的目标路径）与 bash 执行动作；首批仅覆盖明确声明的工具形态。
- 事件记录：会话/调用 ID、规则 ID 与版本、命中原因、递送、阻止、重试和执行时点。避免记录凭证或完整命令输出。

### 时序要求

原调用 → 匹配命中 → 本上下文尚未有该版本规则 → 中止原动作且递送命中正文 → 模型下一次决策 → 新调用满足已加载条件 → 执行。

第一轮先验证 OpenCode 能否可靠完成该时序；若只能抛错但无法递送可靠正文或引发下一轮，记录机制缺口，不宣称实现。不静默替换用户命令，也不自动执行原调用。

加载状态按会话与规则版本区分。不能因为第一次调用已匹配就立刻对同批并行兄弟调用放行；需证明模型已经经过新一轮获取正文。压缩、恢复、子会话均不得复用未经验证的“已加载”标记。

文件规则和执行规则分开。只读取 .py 是否需要编码正文按规则用途明确；执行版本约束不因只读源文件而触发。匹配执行命令时不能用包含 python 的子串判断，例如 `echo python` 不应触发。env 前缀、绝对解释器路径、多段 shell 和 uv 子命令分别列出支持范围；复杂封装不冒充完整覆盖。

### 验收场景

| 场景 | 预期 |
| --- | --- |
| 修改普通 Markdown | 两份 Python 正文均不递送 |
| 编辑 .py（含 apply_patch） | 修改前递送编辑规则，模型重新决策后才修改；不递送执行规则 |
| 未打开 .py，直接执行 Python 或 uv run | 原执行暂停，先递送环境规则，再由模型形成后续调用 |
| echo 中提到 python、Markdown 中谈 Python | 不触发执行规则 |
| 同一轮并行首次编辑与执行 | 每个相关动作在所需规则生效前都不执行 |
| 同会话再次执行 | 不无谓重复正文；规则版本变化时重新递送 |
| 新会话/压缩后 | 不错误复用旧加载状态；无关规则仍不预载 |

证据必须同时有：实际递送到模型的内容、后续模型轮次、工具执行顺序、最终夹具结果。仅适配器日志“matched”不足以验收。

隔离试验需区分既有全局指令影响，确保测试命中不是模型从原 WORKBENCH.local.md 提前获知。若无法隔离用户级配置，则运行结果标记受污染，不作为按需加载成立的证据。

## 后续门槛与未覆盖

### 2026-10-19 原型进展

新增 tools/integrations/progressive-loading-pilot/ 的零依赖回调原型，按本机插件类型定义验证了 6 个模拟契约测试，全部通过。覆盖无关排除、编辑/运行分离、并行首次调用、会话隔离。此结果不等于实际模型加载验收。

真实宿主测试需要启动另一 Agent 会话，与本机统一经 Herdr/Pi/high 启动的约束存在冲突；未自行运行 OpenCode 子会话。等待确认隔离宿主测试进程的例外后，继续隔离配置与实际递送时序验证。原型 README 记录复现命令与明确未覆盖项。

- 当前只完成证据调研和试点设计，没有运行模型试验、改全局入口或安装插件。
- 试点成功后再决定正文落点与迁移，并修复全局入口的提前加载。无需先新建完整规则平台。
- Codex 机制、本机 Claude 版本与位置、所有宿主的子会话继承均待核验；不阻止先验证 OpenCode，但阻止宣称跨宿主完成。
- Docker、OpenViking、公司环境随后按相同机制扩展。公司环境触发用模拟调用验证，不访问真实公司环境。
- Personal Workbench MCP 上报工具未在当前会话提供；任务状态使用本会话 Todo，未声称完成 MCP 上报。
