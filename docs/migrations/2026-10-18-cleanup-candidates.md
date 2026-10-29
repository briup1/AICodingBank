# 旧内容舍弃候选与执行记录

日期：2026-10-18。用户后续批准先删确定可舍弃的内容：C01 的 5 个重复文件、C02 的 7 个零字节文件已删除，删除前再次核对逐字节相同/零字节。C04 已按用户要求保留并提炼；用户随后明确批准删除 C03 的全部 3 个旧日志、C05 会话全文、C06 设备元数据、旧 project_rule.md 和遗漏的空 code-reviewer_zh.md，均已从本机文件中删除。旧 Skill 兼容软链继续保留。移动到新路径不等于舍弃，Git 旧路径删除标记需结合迁移表区分。低频、旧目录名、尚未迁入都不能单独作为删除依据。

本轮不做 Skill 能力重合审查。以下只依据文件内容、完全相同的副本、空文件或与当前结构明显不符的材料判断；不能证明用不上的一律保留或待定。

## A. 推荐优先确认的精确范围

### C01：示例中的完全重复插件副本（5 个文件）

已执行：旧示例目录的下列文件与 plugin_guide/plugin_store 对应文件逐字节相同，删除前复核并保留 plugin_store 的单份正文。原示例不再自包含插件正文，已在原插件示例目录增加 README 指向保留内容。

| 建议舍弃路径（仓库相对） | 保留路径 | SHA-256 前缀 |
| --- | --- | --- |
| claudecode_guide/000_examples/.claude/.claude-plugin/code-review/README.md | claudecode_guide/plugin_guide/plugin_store/code-review/README.md | 1fca74bab696 |
| claudecode_guide/000_examples/.claude/.claude-plugin/code-review/.claude-plugin/plugin.json | claudecode_guide/plugin_guide/plugin_store/code-review/.claude-plugin/plugin.json | 61af303bf05e |
| claudecode_guide/000_examples/.claude/.claude-plugin/code-review/commands/code-review.md | claudecode_guide/plugin_guide/plugin_store/code-review/commands/code-review.md | 7d5a0bc9a41b |
| claudecode_guide/000_examples/.claude/.claude-plugin/code-simplifier/agents/code-simplifier.md | claudecode_guide/plugin_guide/plugin_store/code-simplifier/agents/code-simplifier.md | 2a51e8d21058 |
| claudecode_guide/000_examples/.claude/.claude-plugin/code-simplifier/.claude-plugin/plugin.json | claudecode_guide/plugin_guide/plugin_store/code-simplifier/.claude-plugin/plugin.json | f18fb26b2f03 |

### C02：旧双层规范空壳（优先只舍弃 7 个空文件）

已执行：以下 7 个文件删除前复核均为 0 字节；后续用户也批准删除 project_rule.md，旧双层规范的全部正文现已移除，不再作为当前入口。

- double_layer_spec/AI2AI/前端架构信息.md
- double_layer_spec/AI2AI/后端架构信息.md
- double_layer_spec/AI2AI/协议与数据规范.md
- double_layer_spec/AI2AI/API测试方法.md
- double_layer_spec/ME2AI/任务规划.md
- double_layer_spec/ME2AI/技术约束.md
- double_layer_spec/ME2AI/需求描述.md

project_rule.md 原有旧流程规则，首次清理时保留；本轮按用户明确授权删除。删除表示舍弃旧方案，不表示已证明新链路完全替代。

### C03：旧浏览器运行日志（3 个受版本控制文件）

- .wl-ai-skills/browse/browse-audit.jsonl
- .wl-ai-skills/browse/browse-console.log
- .wl-ai-skills/browse/browse-network.log

已执行：按用户“全部删除旧浏览器日志”的明确授权，删除上述 3 个本机文件，不只是移出版本控制；历史日志不再作为现存证据。目录忽略规则保留，没有停止浏览器进程或清理其他运行数据。

## B. 后续审核决定

### C04：已确认保留——从短提示词提炼项目学习方法

用户明确认为这类内容应保留，分析提示词预期效果并写入最佳实践。已撤销舍弃建议：原文保留，说明页提炼为 [项目学习：先建立简要路线图，再按主题深入研究](../../best_practices/2026-03-24-历史项目学习-生成系统学习文档/README.md)，补充适用场景、两步意图、建议用法和注意事项。未执行实测，状态保持 historical-unverified；不以字数少或没有执行日志认定无价值。

### C05：旧示例项目的完整会话原文（1 个文件）

已执行：按用户明确授权删除 tools/skills/engineering/ai_coding_sec_dev_workflow/examples/UExtract/claude-conversation-2025-12-30-ca46e2b9.md。未额外提炼或复制全文；同包的阶段示例、状态、模板与 Skill 本体均保留，原路径兼容软链未删除。

### C06：旧设备元数据（1 个文件）

已执行：按用户明确授权删除 .marscode/deviceInfo.json；未读取/展示其中设备标识，没有修改其他本机工具配置。未验证 MarsCode 后续行为，不能声称对该工具无影响。

### C07：遗漏的零字节审查手册

已执行：按用户点名删除 claudecode_guide/agent_guide/agents_store/code-reviewer_zh.md；删除前确认其为 0 字节普通文件。其他审查手册不受影响。

## C. 明确保留，不作为本轮可删结论

| 内容 | 原因 |
| --- | --- |
| claudecode_guide 剩余教程、规则模板、插件说明与 Agent 示例 | 提取 Skill 后仍有 91 个真实文件，不是全部无用；尚未逐项证明替代关系，不整目录删除 |
| tools/skills/**/legacy-snapshots 与 on-demand | 已先搬迁；没有做内容重合/来源审计，可能含独有方法，不去重不删除 |
| candidates/ecc（7 个文件，含 LICENSE） | 五个专项 Agent 是候选参考，不代表已安装；存在角色建设参考价值，不因未启用删除 |
| tools/skills/engineering/ai_coding_sec_dev_workflow 其余设计、状态与模板 | 旧调度方式和当前规则有差异，但有独有流程/状态思路；先保留，使用时不能覆盖当前授权边界 |
| .pi/settings.json、.claude 链接与宿主入口 | 有真实运行配置/调用风险，不能按目录形态清理 |
| 所有旧 Skill 兼容软链 | 全局规则和既有加载链接仍引用它们，当前不满足移除前提 |
| vendor、忽略依赖、本机资料、凭证配置与验证证据 | 本轮未授权清理；不得因未纳入新目录就删除 |
| 本项目需求、设计、研究文档与外部知识库 | 历史事实和来源不因新结构失效，继续在原归宿维护 |

## 当前结果

本清单已提出的候选全部有明确去向：C01、C02、C03、C05、C06、C07 已按授权删除；C04 保留并提炼。本轮删除 7 个文件，连同上一轮 12 个，共 19 个；没有递归清理目录、删除其他资料或扩展为 Skill 去重。后续新发现项仍需先列范围并获确认，不由本次批准自动覆盖。
