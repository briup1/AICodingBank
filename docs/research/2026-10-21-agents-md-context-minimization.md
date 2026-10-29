# AGENTS.md 精简：公开依据与本机优化建议

调研日期：2026-10-21。

> 已实施（2026-10-21）：用户已批准并完成执行分级删除、全局规则精简和 Pi 默认 Skill 收敛。精简验收时根文件 2,632 字符；在本工作台下 Pi 默认可见 20 项 Skill。随后委派规则改为只引用短版 wl-herdrs，允许符合条件的宿主原生备用，详见文末补充。下文原统计和复用 execution-governance 的建议是修改前快照，不是现行入口；最终结果、验证与边界见文末“最终实施与验证”。

范围：公开研究、官方文档，以及当前用户级 AGENTS、直接相关按需文档和 Pi 加载机制的只读核对。仅新增本报告；不修改用户级规则、Skill、宿主配置、记忆或执行门禁，不启动子 Agent，不进行真实开发任务 A/B。

## 结论

**值得精简，但目标不是“字数越少越好”，而是“每次只带必需的约束；专项操作之前能读到正确的细则”。**

当前文件既有高价值的个人约束，也混入了专项操作手册、工作台说明和重复细则。不能据此断言“大部分都是无用 Token”；更准确的说法是：不少内容有用，但不必每次常驻。

推荐第一轮采用低复杂度方案：

```text
现在：每次加载 8,225 字符 → 再按需读已有细则，其中部分重复

建议：加载短的个人底线与路由
        ├─ 直接问答：不读专项手册
        ├─ 测试/Review/委派：执行对应动作前读适用细则
        └─ 使用工作台/知识库/公司工具：只读对应入口
```

先合并重复、移出说明性材料、保留精准触发，不先开发动态规则系统或新增一批 Skill。拟定根文件 2,000—3,000 字符为试写预算，不是已经证明可无损达到的长度或模型性能阈值。

## 一、公开资料支持什么？

### 1. 常驻入口做地图，不做百科全书

OpenAI 的 Harness engineering 实践报告明确描述：曾尝试一份大 AGENTS.md，发现会挤占任务上下文、弱化优先级、积累过期规则，后来改为约 100 行的导航入口，指向结构化文档。[S1]

可借鉴的是职责划分：入口帮助找到规则正文，而不是把全文复述一遍。约 100 行只是该团队实践，不是中文文件、所有模型和所有宿主的统一标准，也不意味着必须复制其目录体系。

### 2. 按需加载：先说明“何时读”，再提供“读什么”

Anthropic 的上下文工程文章主张最小的高信号上下文，并明确说“minimal does not necessarily mean short”；强调即时检索、代表性例子，而非穷举所有边界。[S2]

其 Agent Skills 文章与 Agent Skills 官方最佳实践进一步区分：启动时提供名称/用途，命中任务才读正文，更细的参考再按需读。尤其应写明具体触发条件，而不是仅留一个泛泛的文件链接。[S3][S4]

例子：

```text
弱：更多规则见 execution-governance.md。
好：准备委派时，先读该文件的委派要求；未需要委派的简单问答不读。
```

拆分也有成本：多一次检索、工具调用与等待，路由不清时还可能漏读。因此高频个人偏好、授权底线留在根文件，专项复杂步骤放按需正文；不为每条禁令单建一个文件。

### 3. 实证研究：更多指令会改变行为，不只是增加输入长度

《Evaluating AGENTS.md》当前 v3，更新于 2026-09-29。实验包括 SWE-bench Lite 和 12 个 Python 仓库的 138 个 CTXbench 任务，比较无上下文文件、模型生成文件、开发者文件。[S5]

关键结果：

- 模型生成文件总体未显著改善解题率，在对应实验中成本平均增加约 20% 和 23%。
- 开发者文件相对无文件平均改善约 2.4%，但差异未达统计显著；相对模型生成文件的改善显著。
- 指令常被遵守，却带来更多探索、测试和步骤；成本不是单纯多了几段输入。
- 文件长度与成功率没有显示显著关联，不能从论文推出“越短越成功”。

限制：主要是 Python 编程任务的解题指标，不是用户个人偏好、跨宿主治理、安全合规或 Pi 的专项实验。**不能拿这篇论文当作删掉个人约束、安全底线或测试要求的依据，更不能承诺本机节约同样百分比。**

### 4. 长上下文理论提供风险提示，不提供本机损失比例

Lost in the Middle 研究在多文档问答与键值检索任务中观察到：相关信息放在长上下文中间时，表现可能下降。[S6]

它支持“上下文容量不等于有效利用率”的提醒。但研究不是对当前 Pi/网关模型的指令遵守测试，不能据此计算“8,225 字符浪费多少注意力”。“注意力预算”是有用的工程描述，不是本轮实测指标。

### 5. 自动导入、子目录规则、Skill、Hook 不是同一种机制

Claude Code 官方文档建议具体、简洁、一致，并说明：[S7]

- @ 导入帮助组织文件，但被导入的内容仍在启动时加载，不降低上下文成本。
- paths 条件规则才根据匹配文件加载；没有 paths 的规则仍常驻。
- 文本指令是上下文，不是可靠的操作权限隔离；强制阻止动作需使用相应执行控制。

这些是 Claude 的能力，不能直接套给 Pi。官方行数建议也不能变成仅靠重新换行“达标”的游戏。

## 二、当前文件实际长在哪里？

核对对象：`/Users/ziyun/.agents/AGENTS.md`。Pi 入口 `/Users/ziyun/.pi/agent/AGENTS.md` 为其软链接；本次分析的是已更新沟通小节后的版本。

当前 198 行、8,225 字符、18,709 UTF-8 字节。字符统计包含标题、路径和 Markdown，不等于汉字数或 Token 数，未调用对应模型 tokenizer。

| 部分 | 字符 | 占全文 | 建议 |
| --- | ---: | ---: | --- |
| 角色与协作目标 | 63 | 0.8% | 保留 |
| 沟通与输出约束 | 826 | 10.0% | 保留刚确认的行为要求；先不为了省字二次重写 |
| 上下文加载边界 | 680 | 8.3% | 合并同义句，保留真实路径、按需、不可跳过适用规则等关键要求 |
| 执行与验收约束 | 2,722 | 33.1% | 根文件保留交付、范围、授权、停止原则；角色和细则按需 |
| 工程规范与操作入口 | 1,091 | 13.3% | 改成紧凑的“触发 → 真实路径”；保留适用前提与排除条件 |
| 知识库与工作台 | 2,500 | 30.4% | 移除常驻目录树和完整使用说明；只留何时进入及安全底线 |
| OpenViking（Codex） | 335 | 4.1% | 共享底线保留；Codex 专属服务准备条件化，不能在 Pi 每次当成操作步骤 |

### 直接重复证据

对用户级文件与 `/Users/ziyun/.agents/on-demand/execution-governance.md` 做逐行比较，连续匹配至少 3 行的区段合计约 **1,383 字符**，包括范围基准、部分升级条件、测试/Review 和停止规则。统计包含这些区段里的空行，不代表 1,383 字符全部可直接删除。

这说明目前不只是“一份文件长”，而是进入相关流程后可能再次读到相同内容，并产生双份维护和漂移风险。

特别注意：当前细则入口只要求 L2/L3 等场景读取。若把 L1 需要的测试要求移过去，必须同步调整触发，或在根文件保留足够的 L1 原则。**不能只搬正文不修路由。**

### 更大的常驻输入也存在，但不扩成本轮改造

本会话持久化提示词快照中，Skill 列表有 66 项，约 **29,237 字符**；project_context 约 11,907 字符。该快照的若干文本分区总计约 48,892 字符，不包含全部工具 schema、历史或扩展注入。

这只是本轮快照，不代表所有会话恒定值；目录说明不是 Skill 正文，但也是常驻上下文。若后续继续优化，可再查宽触发描述和相邻 Skill 重叠，不能通过不断新增 Skill 来假设常驻成本自动降低。

缓存命中可降低部分重复前缀的处理成本和延迟，但不等于相关文字从上下文消失。本轮未核验当前网关计费、缓存命中与 Token 分词，不能用字符减少比例承诺账单同比下降。

## 三、适合这份文件的具体结构

### 节点 1：根文件保留“每次都要知道”的内容

建议集中成三组，而不是全量手册：

1. 你是谁、回答怎样让你看懂：现有角色与沟通小节。
2. 始终有效的交付与安全底线：原始需求是范围基准、保留用户改动、获准范围内做最小实现和验证、不编造结果、不把外部/破坏性操作当默认授权、不擅自保存或上传敏感信息。
3. 少量高价值加载规则：按任务选择最小资料、用真实路径、不重复读已知正文、不用副本/全局软链接掩盖错误、遵守适用项目规则。

“模型应该知道一般怎么测试”不是删除你个人边界的理由。你的“别无限扩大 Review、别顺手修历史问题”等纠偏信息有实际价值，应压成清楚原则而不是抹掉。

### 节点 2：重复执行规则归并为一句原则＋一个按需入口

旧：根文件分别展开任务范围、测试范围、Review 范围、L0—L3、角色必要性和多次停止要求。

建议根文件概括，例如：

> 默认由负责人直接完成最小实现和必要验证；测试/Review 只覆盖本次变更及其直接影响。范围外观察只记录，不自动处理或阻断；目标成立、必要验证通过且无直接阻断后停止。需要独立验证、委派或高风险操作时，先读取适用执行细则，授权不因升级自动扩大。

这只是表达示意，不是已完成无损替换的正式稿。完整 L0—L3 定义、工作包、角色与详细验收使用已有 `/Users/ziyun/.agents/on-demand/execution-governance.md`，不另造一份重复流程。若测试分类等完整细则确实是所有测试必需，再将“测试/Review”列为入口触发，不继续只写 L2/L3。

结果：普通解释不用携带角色配置；真实需要时仍须先加载，不降低安全或验证标准。

### 节点 3：工作台正文留工作台，根文件只指路

旧：全局文件内嵌约 20 行目录树、使用场景、五步使用方式、能力登记和信息归宿说明。

建议保留：

```text
要使用或拓展个人工作台
  → 读取工作台 AGENTS.md
  → 按其路由选择 WORKBENCH.md / EXTENDING.md
  → 仅需要本机资料时读取 local 对应部分
```

唯一入口仍是 `/Users/ziyun/workdir/self_project/AICodingBank/AGENTS.md`。目录职责和登记细节已由该仓库文档维护，无需每个普通业务项目会话都带着整张地图。

不要把每轮都必须知道的沟通偏好也藏到工作台入口后面；否则普通项目会话可能根本不触发它。

### 节点 4：专项规则按“动作之前”触发，不只看文件后缀

保留当前已有真实入口，而非新建大量子文件：

| 任务/动作 | 读什么 | 不应顺便加载什么 |
| --- | --- | --- |
| 查公司配置、数据库、日志、TAPD | `/Users/ziyun/.agents/on-demand/fuxi.md` | 不因只读 Git 状态加载 |
| 需海管家规范的实现/设计/Review | `/Users/ziyun/.agents/on-demand/hgj-coi.md` | 不因同仓库含多技术栈全读 |
| 委派/独立验证/高风险执行 | `/Users/ziyun/.agents/on-demand/execution-governance.md` 及原委派入口 | 不因存在子 Agent 能力而组队 |
| 需求分支、集成、污染审计、回收等 | 原 wl-git-flow 入口 | 普通 status/log/diff 不触发完整流程 |
| 公司 Git SSH/路由故障 | 原 hgj-git-connect 入口 | 连接正常时不加载 |
| 知识库读写 | 原索引，写入前原 schema | 不把每次聊天当入库 |
| Codex 本机 OpenViking 使用 | 保留原服务准备与本机策略入口，指明宿主条件 | Pi 不执行 Codex 专属准备步骤 |

路径触发有盲点：用户要求“查库”尚未读取任何 .sql；执行 shell 也可能部署或连数据库。因此采用“意图/动作/文件”组合，不把别的宿主 paths 机制当作万能路由。

### 节点 5：CodeGraph 等项目条件规则保留短触发

例如：仓库有 `.codegraph/` 且问题涉及结构、调用或影响时优先使用；纯 Git 分支关系不触发。完整命令与使用方法留对应工具文档。

这类特殊约定模型很难从一般训练知识推断，不能为了删字直接拿掉。

## 四、Pi 里怎样拆才真的减少加载？

本机安装文档与 `dist/core/resource-loader.js` 核对结果：[L1—L3]

- 用户级指令与当前目录、父目录的适用上下文文件进入提示词。
- 同目录 AGENTS.override.md 替换同目录其他候选，不清除其他目录或用户级规则。
- loader 对文件正文直接读取；普通 Markdown 链接不会在这段基础 loader 中自动递归展开。不据此排除其他扩展改变上下文的可能。
- Skill 名称、描述、位置常驻；正文靠匹配后读取，官方文档也提醒模型可能漏读。

因此可先采用自然语言精准路由，不需要为了精简马上写扩展。但要区分：

```text
“当准备执行 X 时先读 Y”
  → 仍依赖模型遵守，需行为测试

在工具执行边界实际检查/阻止
  → 才可能提供更强保证，且需逐宿主验证
```

不能把“文件搬走、链接存在、静态测试通过”写成已验证强制生效。也不把 Pi 的可扩展接口宣称为已部署的条件规则系统。

## 五、如何证明精简没把约束弄丢？

建议下一步先做规则映射，批准后再改：

1. 对每条现有要求标注：保留、合并、移到已有正文、或删除重复；给出目标与触发。
2. 校验入口真实存在、不回环、不出现“每次先读全部”，并覆盖 L1 与复杂场景；不能随意改变旧规则适用范围。
3. 用小组原任务比较旧版和候选：不是本轮已经执行的测试。

建议样本：

- “谁提交的”：直接回答，不读执行治理和公司环境专项正文。
- “解释三端续查”：保留结论、同一最小场景和动作链，不进入实现/测试流水线。
- “普通单文件修改”：能直接实现并验证，不因新手册把简单任务升级组队。
- “独立 Review / 派 Agent”：行动前读到适用规则，Pi/Herdr/high 等原要求仍成立。
- “公司 SSH 错误”和“纯分支比较”：一个触发专项，一个不误触发。
- “知识库写入或公司侧写操作”：读到原必要前提，未获授权不得靠省 Token 绕过。

比较指标：常驻文本/对应 tokenizer 的 Token、实际加载的手册、非必要工具调用、完成时间、用户纠正次数与是否违反约束。真实高风险动作只做无副作用模拟或经过明确批准的验证，不为测提示词执行生产写入。

根文件若从 8,225 改到 2,000—3,000 字符，单文件文本可减少约 64%—76%；**这是预算算术，不是已实现结果，不等于整场上下文或总成本节约同样比例。** 命中专项后仍会读细则，衡量的是没有命中的普通任务是否不再白带。

## 六、资料与证据

### 公开来源

- [S1] OpenAI，Harness engineering: leveraging Codex in an agent-first world： https://openai.com/index/harness-engineering/ 。本轮直接抓取 403，使用 web_search 返回的官方页面索引正文；不是完整页面逐段核验。主要采用“百科→目录、约100行、机械验证”原文段落，不将完整项目实践当作本机必需架构。
- [S2] Anthropic，Effective context engineering for AI agents： https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents 。直接抓取并核对相关段落。
- [S3] Anthropic，Equipping agents for the real world with Agent Skills： https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills 。直接抓取；启动元信息、按需正文和参考层级。
- [S4] Agent Skills，Best practices for skill creators： https://agentskills.io/skill-creation/best-practices 。直接抓取；关注模型未知信息、适度详细、明确读取时机、校准控制与评估。
- [S5] Gloaguen 等，Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents? v3： https://arxiv.org/html/2602.11988v3 ；版本记录 https://arxiv.org/abs/2602.11988 。直接抓取，核对方法、主要结果、统计显著性及限制。
- [S6] Liu 等，Lost in the Middle，TACL 2024： https://aclanthology.org/2024.tacl-1.9/ 。直接抓取摘要，限用其上下文位置效应结论，不泛化为当前模型精确损失。
- [S7] Claude Code，How Claude remembers your project： https://code.claude.com/docs/en/memory 。直接抓取并核对 imports、条件 rules、指令非强制配置等段落。属于当前在线文档，不代表本机 Claude 版本已具备全部能力。

另尝试 OpenAI Codex AGENTS 指南 https://developers.openai.com/codex/guides/agents-md ，直接请求 403；搜索命中 https://learn.chatgpt.com/docs/agent-configuration/agents-md 的官方说明，但不据此将 Codex 机制套用到 Pi。部分额外检索失败，未改变浏览器或联网配置以绕过。

### 本机直接依据

- 当前根规则：`/Users/ziyun/.agents/AGENTS.md`。
- 现有细则：`/Users/ziyun/.agents/on-demand/execution-governance.md`，本轮只读比较相关章节，不将分析行为当执行治理任务升级。
- 工作台拓展目标：`/Users/ziyun/workdir/self_project/AICodingBank/EXTENDING.md`，已有“入口只指路、按场景加载”的确认目标；本轮建议沿用而非重复设计。
- 现有渐进加载调研：`/Users/ziyun/workdir/self_project/AICodingBank/docs/research/2026-10-19-progressive-loading-host-audit.md`，只按需参考已有核验，宿主结论以本轮文档/源码为准。
- [L1] `/Users/ziyun/.node/lib/node_modules/@earendil-works/pi-coding-agent/docs/configuration.md`。
- [L2] `/Users/ziyun/.node/lib/node_modules/@earendil-works/pi-coding-agent/docs/skills.md` 与 `docs/how-pi-works.md`（同一 docs 目录）。
- [L3] `/Users/ziyun/.node/lib/node_modules/@earendil-works/pi-coding-agent/dist/core/resource-loader.js`，115—195 行。

未使用 OpenViking 检索：当前目标文件、既有会话证据和公开来源足以完成本轮调研；没有新读资源 URI 或向记忆库写入。没有宣称独立审查或新版本行为验收。

## 后续决定与补充核验

### 已实施：删除分级细则，不搬家重建

用户通过结构化确认选定“删除分级和细则，保留基本底线”。已完成：

- 删除 `/Users/ziyun/.agents/on-demand/execution-governance.md`。
- 将 `/Users/ziyun/.agents/AGENTS.md` 的“执行与验收约束”长节替换为“执行与交付底线”，移除 L0—L3、强制四步及对应角色细则和两处文件引用。
- 保留目标与范围、最小验证、保留用户改动、操作授权、证据真实性及原 Herdr/Pi/high 委派约束；未把取消分级解释为扩大授权或自动组队。
- 移除“OpenViking（Codex）”全节，将“不擅自写入对话、代码或记忆”的通用底线保留在执行底线，而不是把本机服务启动脚本继续留在全局提示词。
- 沟通小节逐字未改；其他无关章节不变。根文件从 8,225 减至 5,489 字符，减少约 33.3%。Pi 软链接与源文件读取一致。

本机修改前备份：`/tmp/agents-simplify-20261021-7ZVYYJ/`，权限 0700，备份文件 0600。该临时备份不属于 Agent 自动加载入口。历史调研和聊天中提到被删文件的内容不做全量改写；当前检查的活动入口没有残留引用。

### “专项操作”的具体判断

不增加一个新的任务分类体系，直接看“下一步要干什么”：

```text
问某个提交是谁写的 → 查 Git，无需公司数据库操作说明
查 Dev 表中一条记录 → 查库前读已有查库要求
把需求合入 Beta → 合并前读已有 Git 集成要求
启动页面用例 → 启动前读浏览器/测试入口
```

一个任务可能经历多个具体动作，到了哪个动作才查对应说明。动作不存在就不加载；不要求用户先判断类型，也不要求每轮宣告分类。原先“专项操作”只是这个含义，不是被删除的 L0—L3 的改名替代。

### OpenViking：官方已有能力，不在 AGENTS 复述产品手册

直接核对来源：

1. 官方通用 Skill： https://raw.githubusercontent.com/volcengine/OpenViking/main/examples/skills/openviking-memory/SKILL.md ，抓取成功。官方提供何时检索、如何 search/find/read、记忆作用域及使用边界。
2. 官方 Codex 集成： https://docs.openviking.ai/en/agent-integrations/04-codex ，抓取成功，说明 Codex Memory Plugin 提供 lifecycle hooks、MCP proxy，并打包 openviking-memory、openviking-skills、ov-experience-memory。
3. 官方 MCP 接入： https://docs.openviking.ai/en/agent-integrations/06-mcp-clients 与 https://docs.openviking.ai/en/guides/06-mcp-integration ，抓取成功。服务暴露 `/mcp`，Streamable HTTP 客户端可直接连接。只接 MCP 不等于自动召回/采集已经启用。
4. 官方 openviking-skills 原文单独抓取超时；其随包事实由 Codex 官方集成页佐证，不声称本轮取得了该远程 Skill 的全文。

本机：Pi 的 OpenViking 扩展自带上述三条 Skill，当前会话也实际有 OpenViking 工具声明。本轮未调用服务工具或检查服务健康，不把“工具已声明”说成“连接已验证”。Codex 配置存在 `openviking` MCP 条目，但当前读取的插件配置键中未发现官方 openviking-memory 插件；不能据此称其已经安装/启用，也不执行安装。移除全局说明不改变现有 MCP、服务与本机准备脚本。服务自动拉起和本机连接策略是配置/集成责任，不保证官方 Skill 会替代现有启动脚本。

### 66 个 Skill：处理可见范围，不删除能力库

本轮实际提示词目录：66 项、约 29,237 字符。按 location 分类：57 项来自 `/Users/ziyun/.agents/skills/`，6 项来自 Pi Ponytail 包，3 项来自 OpenViking 扩展。不是 66 份 Skill 全文已加载，也不是全部由工作台安装器管理。

本机 Pi 配置已有 5 项 DeepAgents Skill 排除，说明可以在 Pi 层控制可见列表，不必改共享 Skill 原文或运行全量安装器。

建议链路：

```text
启动仅展示少量跨项目常用入口
  → 普通任务用当前入口完成
  → 需要某种低频能力时查工作台 CATALOG
  → 读取实际 Skill 路径，或在对应项目启用
```

按三组处理，不先承诺固定保留数量：

- 常用且跨项目：如实际在用的浏览器、委派组合、记忆能力，核对后保留；配套入口可能互补，不因名字相似判重复。
- 项目专用或低频：如 compass 本地测试、企业身份接入、harness 初始化、脚手架/课程练习，考虑仅在相关项目可见或按目录查找；不卸载、不删除正文。
- 多种替代方法：例如 at-review、code-review、ponytail-review、wl-requesting-code-review，以及 diagnosing-bugs、wl-investigate。这里只是需比较触发重叠的候选，不表示功能完全相同；应确定默认入口，其他手动/按需使用，不让同一意图触发全部工作流。

Pi 已核对的机制：

- `/Users/ziyun/.node/lib/node_modules/@earendil-works/pi-coding-agent/docs/settings.md` 说明 skills 资源支持排除/包含路径；优先用 Pi 专属资源排除，避免删共享软链接影响其他宿主。对扩展动态发现的 Skill 是否同样被具体排除规则覆盖，须实际验证。
- 同包 `dist/core/skills.js` 的 formatSkillsForPrompt 会过滤 disableModelInvocation；自研 Skill 可按批准用 `disable-model-invocation: true` 做显式调用入口。它改变触发语义，不能直接批改第三方 Skill；目录路由或用户显式调用仍要可达。
- 不把关闭 enableSkillCommands 当省上下文措施；它控制命令发现，不代表移除目录描述。
- 不为少用能力全量上传 OpenViking；大量条目依赖本机命令、软链接或插件，上传不是本轮授权，也不是通用压缩手段。

本阶段原建议为先分类再批准调整；随后用户明确批准“以上建议立即实现”，已按下节实施。此前未修改 Skill 配置的状态不再代表当前状态。当前会话已注入的旧目录和旧规则不会因磁盘修改而自动从历史里消失。

## 最终实施与验证

用户批准后实施，未安装/卸载依赖、未修改第三方 Skill 正文、未上传能力或操作记忆库、未启动子 Agent、模型请求、浏览器或服务。

### 变更位置

- `/Users/ziyun/.agents/AGENTS.md`：从上一轮 5,489 压到 2,632 字符；相对最初 8,225 字符减少约 68.0%。沟通小节与执行底线逐字保留，合并加载纪律，将工作台目录树/说明改为入口导航，原必要知识库要求保留短句。Skill 查找加入本机索引，不强制读取全文。
- `/Users/ziyun/.pi/agent/settings.json`：在共享用户 Skill 根使用默认排除＋16 个明确常用入口包含；已有 5 个 DeepAgents 排除保留。Ponytail 包改用资源过滤，只自动展示主 Skill，其他配套 Skill 不卸载。模型、思考级别、工具、主题和其他包声明不变。
- `/Users/ziyun/.pi/agent/skill-index.local.md`：本机按需索引，覆盖此前 66 项及已被原配置排除的 6 项，共 72 项。逐条给名称、用途、真实路径和默认/按需状态；文件名不是自动注入的上下文候选，不默认全文加载。隐藏项用真实路径读取，不承诺隐藏后仍支持 `/skill:name`。
- `/Users/ziyun/workdir/self_project/AICodingBank/WORKBENCH.local.md`：补充 Pi 可见性配置与索引位置，并明确代码审查默认 at-review、排障默认 wl-investigate。该文件 Git 忽略，不把本机名单复制进共享 CATALOG，不修改 skills.yaml 或全局共享软链接。

### 分类与结果

当前工作台的默认 20 项：at-review、at-standards、at-test、ego-browser、goal-coach、herdr、hgj-session、wl-auto-delivery、wl-design-doc、wl-git-flow、wl-herdrs、wl-investigate、wl-qa-test-planner、wl-req-confirm、wl-ticket-run、wl-web-auto、ponytail，以及 OpenViking 的三条 Skill。

其余此前可见的 46 项改为按需：项目专用（如 Compass 本地测试、企业身份、harness）、低频（如练习脚手架/工具安装）、替代方法（如 code-review、ponytail-review、diagnosing-bugs、旧浏览器入口）。不表示这些能力冗余或已废弃，也没有批量修改其触发描述。

具体项目自己的 `.pi/skills`、`.agents/skills` 及项目包仍能按原机制加载。本次只约束用户共享根与 Ponytail 包，不擅自在其他项目写配置；因此其他项目的总数量可能超过 20，这属于项目能力叠加，不是本次规则失效。

### 可重复的离线加载验证

使用当前安装 Pi 的真实 DefaultPackageManager、SettingsManager、loadSkills/formatSkillsForPrompt 和 DefaultResourceLoader：

1. 使用内存 settings 存储，分别读取修改前和实际磁盘配置；缺少包立即失败，不允许自动安装，`PI_OFFLINE=1`。
2. 加载工作台原有项目排除（langfuse）。最初遗漏项目配置时得到 67，修正测试后与原会话 66 一致，没有修改项目排除。
3. 真实资源 loader 关闭扩展执行，先解析出 17 项，再用已安装 OpenViking 的 `resources_discover` 同形输入补入3条 Skill；不执行插件或服务，结果20项、无诊断错误。
4. 真实上下文 loader 读取到精简后的根文件；确认 Pi 软链接、沟通与底线不变、执行分级/已删除细则没有复活。
5. 逐条检查原66项均可从索引定位；72项原文件哈希与实际链接目标核对通过，未更改正文。核对设置只改变 skills/packages 资源过滤，未更改其他配置。

同一格式化函数的目录文本：29,220 → 9,962 字符，减少约 65.9%。与原会话统计29,237有少量包装文字差异，比较使用相同函数，不混用分母。这是文本量，不是实测 Token、成本、成功率或延迟改善。

证据和回退备份：`/tmp/pi-context-minimize-20261021-w3EML3/`；含 AGENTS/settings/local 原件、分类、来源哈希和 verification.json。目录0700；原配置备份及证据0600。临时备份不是长期版本管理，不自动修改/提交任何其他仓库。

### 生效与未覆盖

- 开启新 Pi 会话，或按 Pi 文档执行 `/reload` 后重新检查；磁盘变更本身不会删除本会话历史注入的正文。不要把 reload 当成清空所有旧上下文。
- 已验证真实加载器的离线结果，未发起新模型会话、未测试66种业务能力，也未执行真实插件生命周期。当前活动会话和其他正在运行的会话何时重新加载需由其自身处理，本轮不强制重启。
- 没有修改 Codex、Claude、共享 Skill 原文、OpenViking 配置或服务；不保证其他宿主的默认目录也已减少。
- 自动采集/无关记忆注入和工具 schema 的成本未在本轮处理，不能把本次文本削减说成整体上下文已经最优。

### 后续：委派策略只保留默认与备用

用户随后批准将 wl-herdrs 精简为短策略：默认 Herdr → Pi/high、一层委派、独立Tab；Herdr 因环境、工具或宿主执行限制不可用时，允许当前宿主实际支持且获准的原生 subagent，不强套 Pi/Tab 要求。用户禁令、组织策略、审批拒绝和资源访问限制不可借此绕过；状态不明先核查，不重复派发。

全局入口、PM手册、统一执行导航及自动交付 Skill 均引用同一策略；删除旧兼容参数表，未新增无依据的 Pi YOLO 参数。此前快照中的“无备用通道”不再有效；本次不启动真实 Agent，不能称原生备用路径已实测。原 Skill 验证日期属于历史验证，不表示新增备用路径完成运行验收。
