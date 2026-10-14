# OpenViking 调研

> 核验口径：截至 **2026-10-11 官方 `volcengine/OpenViking` main 的文档/源码核验，未运行验证**。
> 本次读到的 main 提交：`4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5`，提交时间 `2026-10-10T14:46:50Z`。记忆章节按该源码快照核验；功能、检索和存储章节按当日官方站核验。未做运行或性能验证。
> 官方仓库树中没有 `docs/en/concepts/memory.md`、`docs/en/concepts/session.md`、`docs/en/design/memory-design.md`；本次实际采用编号路径 `docs/en/api/16-memory.md`、`docs/en/concepts/08-session.md`、`docs/en/concepts/02-context-types.md` 及当前相关源码。[M0][M1][M2][M3]

## 记忆：会话到长期记忆

### 1. commit 是否需要显式触发

**默认不能把“消息已加入会话”当成“长期记忆已提取”。应用需要触发提交；配置自动提交后，可由系统触发，不要求调用方每次手动 `commit()`。** 服务器自动提交总开关 `memory.session_auto_commit.enabled` 的配置默认是 `false`；创建会话也支持显式提供 `auto_commit_policy`，按待提交 token 数、消息数等条件触发。空闲扫描仍依赖服务器总开关。这里说的是配置类默认值，不代表所有部署的实际配置。[M2][M4]

```text
应用创建会话并追加消息
  -> 手动 commit()，或已配置的自动提交触发
  -> 请求内完成消息归档、保留消息处理，并排队后台任务
  -> 返回 accepted + task_id（只是受理，不是记忆完成）
  -> 后台读取归档消息和已有记忆，提出新增/更新/删除操作
  -> 校验作用域、类型与操作，按字段规则合并并写回
  -> 查看后台任务终态及 memory_diff.json，确认实际变化
```

上述流程由 Sessions API 和 `Session.commit_async()` / `_run_memory_extraction()` 对应实现支撑。[M2][M5][M7]

关键返回边界：[M2][M3]

- 有消息真正归档：返回 `status: accepted`、`task_id`；调用返回时长期记忆可能尚未生成。
- 空会话或所有消息都被保留、没有生成归档：通常返回 `status: skipped`、`task_id: null`、`archived: false`，不能把它算成一次记忆提取成功。
- 应等待任务进入终态；一次 `get_task()` 不是等待完成。失败、取消、超时不等于成功。
- `memory_diff.json` 的 adds / updates / deletes 才表示实际记忆变化；`skipped_operations` 是被跳过的提议，不是已经写入。即使任务完成，也可能没有新增记忆。

**提交与提取的开关相互独立：** `memory.extraction_enabled` 默认 `true`；设为 `false` 时仍可归档，但不提取长期记忆。`memory_policy.working_memory.enabled` 默认 `false`，只控制会话摘要/检查点摘要，并不关闭长期记忆。源码将摘要与长期记忆提取作为可分别启用的后台工作，并非“必须先有摘要才能提取”。[M4][M5][M6][M8]

最小例子：追加“我偏好简短回复”还不是持久偏好；提交后仍要等待后台任务，并查看 preferences 的实际变更。关闭 working memory 后，这条长期偏好仍有机会被提取；关闭 extraction 后，则只有归档、不产生这一提取结果。例子用于说明开关含义，不是运行结果。[M3][M4][M5][M6]

Memory 专页还提及“explicit extraction”，但本轮没有核实该表述对应的当前公开调用入口，不提供猜测的 API 名称。[M1]

### 2. 两层 scope 与记忆类别

**当前 main 不能再按“用户记忆一套目录、Agent 记忆另一套目录”描述。** Context Types 明确说明：记忆位于当前 User 或 Peer 命名空间，不在单独的 `viking://agent/memories` 中。当前需要区分的是 **Self（当前用户空间）与 Peer（该用户空间下的稳定对话对象）**；身份/人格/执行经验也是记忆内容类别，不代表另一个 Agent 私有根目录。[M1][M3]

| 作用域 | 当前路径 | 已核验的边界 |
| --- | --- | --- |
| Self | `viking://user/{user_id}/memories/`，别名 `viking://~/memories/` | 当前认证用户的空间；`memory_policy.self.enabled` 控制是否允许写入 |
| Peer | `viking://user/{user_id}/peers/{peer_id}/memories/` | 属于当前用户的 Peer 子空间；要求类型支持 Peer、策略允许且 peer_id 在允许范围内，不能任意跨用户写入 |

来源：[M1][M3][M8][M9]。`MemoryPolicy` 的 self / peer 默认均为 `true`，但 peer 开关为 true 不代表任意 Peer 都可写：源码仍校验允许的 Peer、消息归属和范围。源码会以认证上下文填入 user_id，不把模型输出的任意 user_id 当作写入授权。[M8][M9]

当前 Memory 专页列出的内置类别如下；这是当前文档的类别映射，不是本轮实际生成的记忆清单。[M1][M3]

| 类别 | 内容用途 |
| --- | --- |
| profile | 用户基本信息 |
| preferences | 按主题保存偏好 |
| entities | 人、项目等实体事实 |
| events | 重要事件、决定与里程碑 |
| identity | 助手身份、自我介绍与人格 |
| soul | 助手原则、边界、风格与连续性 |
| cases | 用于训练/评估的任务案例 |
| trajectories | 从任务轨迹提炼的执行契约/轨迹 |
| experiences | 可复用的执行经验 |
| tools | 工具使用知识；默认禁用 |
| skills | 技能执行经验；默认禁用，不等同于独立 SKILL.md 资源 |

类别表显示的是 Self 路径；支持 Peer 的类型可写入 Peer 路径，不应推断所有类型都支持 Peer。[M1][M9]

`memory_policy.memory_types` 可限制本次提取类型。包含 `experiences` 会联动加入 `cases`、`trajectories`；不包含 experiences 时，单独填写 cases / trajectories 会被忽略。Agent Evolution 还需要有效 `agent_evolution.enabled`，其配置类默认 `false`。所以“内置有这些类型”不等于默认每次提交都生成全部类型。[M2][M8][M10]

### 3. 提取、合并、去重与纠错

**这不是把整段聊天原样当成永久记忆：模型结合归档消息和已有记忆，提出文件级操作；系统再校验并执行。** 会话专页明确列出 create / edit / merge / delete，源码 `ExtractLoop` 组织模型调用和输出修复，`MemoryUpdater` 应用实际操作。[M7][M11][M12]

```text
新消息：“我现在偏好详细回复” + 已有“偏好简短回复”
  -> 模型读取已有记忆并提出更新
  -> 对内容字段执行 schema 指定的 patch / replace 等规则
  -> 写回长期记忆，并记录 before / after
  -> 后续使用的是修改后的记忆内容，而不是模型参数被修改
```

此例说明已经核实的更新能力；**是否正确识别并消解这次矛盾，未运行验证，不保证。** preferences 模板的 user / topic 字段为 immutable，content 为 patch；不可变字段已有值时会保留原值，patch 支持 SEARCH/REPLACE 或 DELETE，replace 是全量内容替换。因此不能把“支持纠错”理解成“任意字段都能自动改正确”。[M13][M14][M15][M16]

合并与去重边界：

- **同一性优先，而非内容相近就合并。** 共享合并策略要求实体/事件是同一对象或同一次发生，偏好需同一所有者、同一行为选择维度；身份不确定时保留分离。合并前应为每个独立事实找到保留位置。[M17]
- **提交提取不保证全库永久没有重复。** 官方另有显式 memory consolidation：在已有记忆中去重、合并、拆分和压缩，说明重复与同一对象分散成多个文件是实际需要处理的情况。它不是每次 commit 后必定自动执行的全库清理。[M18]
- consolidation 的 instruction 是模型软提示；文档“不编造、不丢事实”是行为约束，不等于本轮证明模型绝不会出错。该规则主要依赖模型遵循合并提示，本次没有语义正确性运行证据。[M17][M18]
- 已核实部分删除保护：同一批刚写入的 URI 不再删除；替代文件写失败或关联迁移失败时会跳过相关删除。这只能证明这些具体保护存在，不能升级为“一切合并都原子成功、可以自动回滚”。[M12]

### 4. 已确认的边界与文档差异

1. **不是大模型权重训练。** 本次已核实的会话记忆主链路是模型推理后更新记忆文件。内部 `train/` 的 policy optimizer 将语义梯度/patch 合成为更新计划，policy updater 实施文件 upsert / delete。就本轮核验到的链路而言，优化对象是记忆/策略内容，不是基础模型权重；不能因出现 train、gradient、case 就宣称会话会微调模型。内部训练框架也不是公开训练 API。[M7][M19][M20]
2. **有作用域和格式保护，但不等于事实核验。** 源码可拒绝或跳过类型超范围、Self/Peer 禁写、非法/未授权 Peer、无效消息范围、归属不明确等操作；ExtractLoop 有格式、定位和 patch 修复机会。没有据此证明记忆内容必真、能完全抵抗恶意会话污染，或具有通用的人审批准门禁。[M9][M11]
3. **敏感数据保护不能扩大解释。** Privacy 专页针对技能正文的敏感值识别与占位替换，并明确依赖模型、不能保证发现全部敏感值。本轮没有证据证明所有会话、所有长期记忆在提取前都会脱敏；不能把 Skill 隐私功能当成记忆全链路保证。[M21]
4. **效果统计不是因果证明。** Agent Evolution API 记录某 Experience 被读取的轨迹及结果分布；官方明确说读取不证明 Agent 真正遵循了经验，也不证明结果由该经验造成。[M22]
5. **后台提取可失败。** Sessions API 说明前序归档失败且没有 `.done` 时，后续提交可因前置条件不满足被拒绝。必须区分提交受理、后台完成、操作实际生效这三件事。[M2]

**已确认的文档差异：** `docs/en/concepts/08-session.md` 的 compression flow 仍把“生成摘要 → 提取记忆”列成固定后台步骤；但当前 Sessions API、`working-memory-default-off.md`、MemoryPolicy 和 Session 源码明确：摘要默认关闭，长期记忆提取不依赖本次摘要生成；两者启用时也可以并行。应以当前 API/默认开关指南与源码为准，不把概念页流程图解读为无条件保证。[M2][M5][M6][M7][M8]

### 记忆章节来源

以下均为官方一手来源。main URL 用于浏览；固定提交 URL 用于复核本次快照。每条结论上方的 `[M编号]` 对应此处，不以旧 README 的宣传代替当前记忆专页。

- [M0] 官方 main 提交与仓库树：
  - https://api.github.com/repos/volcengine/OpenViking/commits/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5
  - https://api.github.com/repos/volcengine/OpenViking/git/trees/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5?recursive=1
- [M1] `docs/en/api/16-memory.md`
  - https://github.com/volcengine/OpenViking/blob/main/docs/en/api/16-memory.md
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/docs/en/api/16-memory.md
- [M2] `docs/en/api/05-sessions.md`
  - https://github.com/volcengine/OpenViking/blob/main/docs/en/api/05-sessions.md
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/docs/en/api/05-sessions.md
- [M3] `docs/en/concepts/02-context-types.md`
  - https://github.com/volcengine/OpenViking/blob/main/docs/en/concepts/02-context-types.md
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/docs/en/concepts/02-context-types.md
- [M4] `openviking_cli/utils/config/memory_config.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking_cli/utils/config/memory_config.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking_cli/utils/config/memory_config.py
- [M5] `openviking/session/session.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/session.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/session.py
- [M6] `docs/en/guides/working-memory-default-off.md`
  - https://github.com/volcengine/OpenViking/blob/main/docs/en/guides/working-memory-default-off.md
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/docs/en/guides/working-memory-default-off.md
- [M7] `docs/en/concepts/08-session.md`
  - https://github.com/volcengine/OpenViking/blob/main/docs/en/concepts/08-session.md
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/docs/en/concepts/08-session.md
- [M8] `openviking/session/memory_policy.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory_policy.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/memory_policy.py
- [M9] `openviking/session/memory/memory_isolation_handler.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory/memory_isolation_handler.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/memory/memory_isolation_handler.py
- [M10] `openviking_cli/utils/config/agent_evolution_config.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking_cli/utils/config/agent_evolution_config.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking_cli/utils/config/agent_evolution_config.py
- [M11] `openviking/session/memory/extract_loop.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory/extract_loop.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/memory/extract_loop.py
- [M12] `openviking/session/memory/memory_updater.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory/memory_updater.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/memory/memory_updater.py
- [M13] `openviking/prompts/templates/memory/preferences.yaml`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/prompts/templates/memory/preferences.yaml
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/prompts/templates/memory/preferences.yaml
- [M14] `openviking/session/memory/merge_op/immutable.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory/merge_op/immutable.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/memory/merge_op/immutable.py
- [M15] `openviking/session/memory/merge_op/patch.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory/merge_op/patch.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/memory/merge_op/patch.py
- [M16] `openviking/session/memory/merge_op/replace.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory/merge_op/replace.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/memory/merge_op/replace.py
- [M17] `openviking/session/memory/merge_policy.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory/merge_policy.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/memory/merge_policy.py
- [M18] `docs/en/context-compilation/06-memory-consolidation.md`
  - https://github.com/volcengine/OpenViking/blob/main/docs/en/context-compilation/06-memory-consolidation.md
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/docs/en/context-compilation/06-memory-consolidation.md
- [M19] `openviking/session/train/components/policy_optimizer.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/train/components/policy_optimizer.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/train/components/policy_optimizer.py
- [M20] `openviking/session/train/components/policy_updater.py`
  - https://github.com/volcengine/OpenViking/blob/main/openviking/session/train/components/policy_updater.py
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/openviking/session/train/components/policy_updater.py
- [M21] `docs/en/concepts/13-privacy.md`
  - https://github.com/volcengine/OpenViking/blob/main/docs/en/concepts/13-privacy.md
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/docs/en/concepts/13-privacy.md
- [M22] `docs/en/api/19-agent-evolution.md`
  - https://github.com/volcengine/OpenViking/blob/main/docs/en/api/19-agent-evolution.md
  - https://github.com/volcengine/OpenViking/blob/4c9a755bff4d31fd9bd9a3be1a19a6054ef3cea5/docs/en/api/19-agent-evolution.md

官方文档站对应入口（本文事实核验以以上仓库快照为准）：

- Memory：https://docs.openviking.ai/en/api/16-memory
- Session：https://docs.openviking.ai/en/concepts/08-session
- Context Types：https://docs.openviking.ai/en/concepts/02-context-types
- Sessions API：https://docs.openviking.ai/en/api/05-sessions

**未验证项：** 本次没有安装、启动 OpenViking、执行 commit、检查真实任务/记忆输出、测试去重或纠错质量、验证权限攻击和数据脱敏；所有示例都是解释性示例。本章不下检索算法或存储结论，相关补充见后文。

## 工具定位与功能

OpenViking 是给 AI Agent 用的上下文数据库，不是大模型，也不是完整 Agent 编排框架：业务文档、用户/Agent 记忆和技能可以统一组织在 `viking://` 路径空间，应用再检索、读取并送入模型。

- 资源：导入文件、目录、网页和代码资料；文档解析后存入结构化资源目录。[资源管理][S1]
- 层级阅读：目录有 L0 概述（`.abstract.md`）、L1 综述（`.overview.md`），L2 是目录中的完整文件；它们不是“每个文件都有三份副本”。[上下文层级][S2]
- 检索：`find` 做直接检索，`search` 结合会话与意图分析；当前实现是在限定作用域内做全局向量搜索，可配置 rerank，不是递归目录遍历。`HierarchicalRetriever` 这个类名仍保留，不能凭名字判断算法。[检索文档][S3]、[检索源码][S4]
- 技能：可以导入技能说明与配套内容，供 Agent 检索读取；是否执行以及如何执行仍由接入方负责。[技能管理][S5]
- 排查：能观察请求、队列、存储、向量处理、VLM 等状态，并查看检索中的候选和处理过程；不等于自动证明答案正确。[可观测性][S6]

## 推荐用法（根据官方能力推导，尚未实测）

1. 先试一个明确场景，例如“查项目文档+记住个人开发偏好”，不要一开始把全部历史资料塞进去；官方快速示例覆盖添加资源、目录访问、概述与检索。[S7]
2. 项目资源按稳定目录分区，例如 `viking://resources/payment` 和 `viking://resources/support`，调用时指定 `target_uri`，减少不同项目混搜。[S1][S3]
3. 区分长期资料、用户/Agent 记忆和可执行流程；不要把整段聊天不加筛选当作确定业务规则。[S7]
4. 先看概述，再看综述，最终回答需要细节时回到原文；三层提供阅读选择，不保证应用自动完成全部阅读策略。[S2]
5. 刚导入后就要检索时，使用 `wait=True` 或 `wait_for_processing()` 等待解析/摘要/向量处理完成；不要把后台尚未完成误判为检索失败。[S1]
6. 准备固定真实问题，对比找到的出处、答案是否正确、token、时延及成本；不要把项目宣传中的单个 benchmark 当作自己业务的收益保证。[评估指南][S8]

## 实现链路

### 资料入库

原始文件/网页/目录 → 解析为临时目录结构 → 原始内容写入 RAGFS 并入队 → 异步生成目录概述与综述 → Embedding 模型生成向量 → 摘要写回内容层、向量写入索引。[S1][S9]

当前官网描述的 RAGFS 是 Rust 内容文件系统层，可使用本地或其他存储后端，并同时支持 HTTP 与嵌入式路径；不要把旧版 AGFS（Go）介绍当成当前唯一实现。嵌入式、本地/HTTP 客户端和服务端模式面向不同集成方式。[S9]

### 取回资料

用户问题 → `find`（直接）或 `search`（会话增强、意图分析）→ 指定范围内的全局向量搜索 → 可选 rerank → 返回候选路径与摘要 → Agent/应用按需读取目录综述和原文 → 模型生成回答。[S3][S4]

“文件系统式组织”解决可管理和可访问，“向量检索”解决找相关资料，“三级内容”解决阅读成本；这三个机制不能混成“沿文件树递归检索”。

### 工程分工

Python 实现客户端、解析、会话及业务编排；当前官网使用 Rust 的 RAGFS 内容文件系统层；向量索引负责持久化和召回。真正的理解工作还依赖配置的 VLM/LLM 和 Embedding 模型，OpenViking 负责串流程和存储检索，不是靠数据库自己训练模型。[S9][S10]

## 验证范围与限制

- 本次只做官方文档与源码静态核验，未安装、运行、测压或验证实际召回效果。
- 官网与 GitHub `main` 会变化；此笔记的读取日期是 2026-10-11，不代表锁定某个发布包或后续版本。
- 摘要和提取出的记忆都可能有误；用于代码实现或关键业务决策时应回到原始证据。
- 开源自托管不等于零运行成本；模型调用、索引和存储都需要配置及资源。[S7][S9]

## 本次补充来源

[S1]: https://docs.openviking.ai/en/guides/01-resource-management
[S2]: https://docs.openviking.ai/en/concepts/03-context-layers
[S3]: https://docs.openviking.ai/en/concepts/07-retrieval
[S4]: https://github.com/volcengine/OpenViking/blob/main/openviking/retrieve/hierarchical_retriever.py
[S5]: https://docs.openviking.ai/en/guides/03-skill-management
[S6]: https://docs.openviking.ai/en/guides/09-observability
[S7]: https://docs.openviking.ai/en/getting-started/01-introduction
[S8]: https://docs.openviking.ai/en/getting-started/06-evaluate
[S9]: https://docs.openviking.ai/en/concepts/01-architecture
[S10]: https://github.com/volcengine/OpenViking

## 长期记忆上限与保留（2026-10-11补充）

> 仅核验容量、保留时间与久远召回。使用当前官方 `.ai` 文档、main 源码/配置；复用本文件前文已核验的合并证据。未运行 OpenViking、未安装、未做年限或容量实测。
> 本轮 4 次 search 调用、4 个不同官方页面/文件读取；未穷尽全部配置、后端服务或清理调用链。

### 一句话结论

**没有查到可据此承诺的统一“最多存多少条/多少 GB”或“默认保存多少天”；也不能说无限或永不丢失。旧记忆在仍被保存、可检索且查询匹配时可以被召回，但不保证某条多年前记忆必定进入本次 prompt。** [L1–L5]

### 容量：持久存储与单次 prompt 是两回事

- **持久容量/配额：未确认。** 本轮检索官方配置及读取 main `RetrievalConfig`，未取得长期记忆总条数、总字节数、账号容量配额或写满后的默认淘汰数字。这个“未查到”不是“没有限制”，还需按实际部署核对磁盘及所用后端的额度。[L2][L4]
- **普通检索：** `find.limit` 默认 **10**；`search` list 模式默认 **每个规划查询 10**，不是整个记忆库只能存 10 条。[L1]
- **上下文组装：** `search(mode="context").max_tokens` 默认 **1600**，为估算 token 预算；无 quota 分桶时 `limit` 默认 **10**。使用 `purpose="coding"` 时预设六类候选额度合计 **10**（events 1、entities 2、preferences 1、experiences 1、resources 3、skills 2），这是当次候选预算，不是纯记忆条数或存储配额。显式 quotas 可覆盖这些额度。[L1]
- **命中也不等于全文进入模型：** 大条目可能退到更短的层级或仅 URI；预算限制的是本次送入的内容，而不是删除持久文件。[L1]

```text
已保存的长期记忆
  -> 本次查询选出有限候选
  -> 受预算限制组装较短内容
  -> Agent 得到本次上下文
“这次没注入”不能直接推成“旧记忆已被清除”。
```

### 保存多久、TTL 与自动遗忘

- **长期记忆默认 TTL/年龄删除：未查到明确数字或已核实的通用自动删除规则。** 本轮不能给“30 天”“一年”之类期限，也不能承诺一直保存。[L2][L3][L4]
- main `memory_lifecycle.py` 的 `DEFAULT_HALF_LIFE_DAYS = 7.0` 是热度统计的时间衰减参数：函数计算分数供 cold/warm/hot 分类，未执行过期删除。**7 天不是保存期限，也不是超过 7 天自动遗忘。** [L3]
- Retrieval API 的 `events_time_decay_protection` 默认 **null**，表示不启用事件时间衰减；显式启用是查询评分行为，不能据此推出持久记忆 TTL。[L1]
- 配置中确有 **临时上传 TTL 默认 43200 秒（12 小时）**，以及 shared 临时上传最大 **536870912 字节（512 MiB）**；这两项分别限制临时上传保留时间和上传大小，**不是长期记忆寿命或总容量上限**。[L4]
- **插件 TTL 不作为长期记忆 TTL 证据。** 主 Agent 补充核验：COMMITTED_TTL 的 30 天针对已提交会话的本地 transcript cursor 状态退休；IDLE_TTL 的 30 分钟针对孤儿会话提交/回收，不是遗忘长期记忆。本 Agent 未重复打开该页面；此项标为主 Agent 提供的核验信息，不作本轮独立复核结论。[L6]

### 归档、删除与合并是否丢旧知识

- Sessions API 明确：`delete_session()` 删除会话目录，包括消息、归档和会话审计记录；已经提取到长期记忆目录的内容仍保留，需要另行删除其 URI。**因此会话/归档寿命与长期记忆寿命不能混用；会话删除没有自动撤销。** [L5]
- 合并策略要求同一对象才能合并，并保留所有独立事实；consolidation 文档规定只整理已有记忆、不新增事实、只压缩重复措辞。这是模型行为约束，**不等于已经证明合并绝不漏事实**。[L7][L8]
- 记忆可被后续更新、合并或显式删除；“旧知识有机会继续存在”不等于“旧版本与所有原始聊天永久可还原”。本轮未核实自动按年龄清理归档、归档数量上限、全局默认保存天数和完整版本恢复能力。[L5][L7][L8]

### 能否召回很久以前

- Retrieval API 的 `since` / `until` 默认 **None**，支持绝对日期/时间过滤；本轮资料未显示默认只查最近 N 天。**据此可判断没有这个接口层面的默认时间窗口，不代表召回率已获实测保证。** [L1]
- 旧记忆是否被使用，还取决于内容有没有实际保存/提取、是否已被修改删除、检索是否匹配、调用是否另设时间/分数过滤，以及本次候选和上下文预算。[L1][L5][L7][L8]
- **未验证：** 数年跨度召回率、百万条规模容量/延迟、实际部署配额、后台清理完整调用链，以及长期运行后合并是否漏掉事实。

### 本补充官方来源

- [L1] https://docs.openviking.ai/en/api/06-retrieval （find/search 默认参数、context 的预算与 quota）
- [L2] https://github.com/volcengine/OpenViking/blob/main/openviking_cli/utils/config/retrieval_config.py （当前检索配置；不作为全库容量无限的证据）
- [L3] https://github.com/volcengine/OpenViking/blob/main/openviking/retrieve/memory_lifecycle.py （7 天热度半衰期，仅计算统计分数）
- [L4] https://docs.openviking.ai/en/guides/01-configuration （本轮搜索结果中的临时上传配置；未额外打开全文）
- [L5] https://docs.openviking.ai/en/api/05-sessions （delete_session 与长期记忆保留边界）
- [L6] https://docs.openviking.ai/en/agent-integrations/04-codex （插件 TTL 的准确对象与时长由主 Agent 补充核验，本 Agent 未重复读取）
- [L7] https://github.com/volcengine/OpenViking/blob/main/openviking/session/memory/merge_policy.py （复用前文已核验源码）
- [L8] https://github.com/volcengine/OpenViking/blob/main/docs/en/context-compilation/06-memory-consolidation.md （复用前文已核验文档）
