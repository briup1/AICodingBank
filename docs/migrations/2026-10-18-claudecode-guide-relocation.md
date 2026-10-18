# claudecode_guide 内容归位记录

日期：2026-10-18。依据：用户在完成岗位制结构迁移提交后选定“提交迁移，再做 claudecode_guide 归位”。搬迁与引用更新**未删除任何内容**；归位后剩余空壳（兼容软链、空目录、过时说明文件）经用户单独批准后删除，见文末。

## 变更链

旧教程目录 `claudecode_guide/` 按内容性质拆到四个归宿，原目录退化为空壳：

```text
claudecode_guide/
├── prompt/ ────────────────→ best_practices/（3 条历史提示词记录，保留原文）
├── claude_md/ ─────────────→ tools/templates/project-entry/（模板 + 样例 + rules）
│                             + best_practices/（生成提示词）
├── agent_guide/ ───────────→ tools/integrations/（配置指南）
│                             + candidates/agent-definitions/（5 个候选 agent 定义）
├── plugin_guide/ ──────────→ tools/integrations/（两份指南）
│                             + tools/skills/engineering/legacy-snapshots/（5 个插件副本）
├── skills_guide/ ──────────→ docs/reference/skills-cheatsheets/（速查表 17 文件）
└── 000_examples/ + claude_setting/ + claudeignore/
    └───────────────────────→ tools/integrations/examples/（示例配置）
```

## 路径表

| 旧位置 | 新位置 |
| --- | --- |
| `claudecode_guide/prompt/100_一个具体的goal任务.md` | `best_practices/2026-06-16-任务编排-目标驱动的多角色任务提示词/prompt.md` |
| `claudecode_guide/prompt/103_轻量化的任务描述提示词.md` | `best_practices/2026-10-09-任务描述-轻量化任务描述模板/prompt.md` |
| `claudecode_guide/prompt/101_AGENTS.md生成提示词.md` | `best_practices/2026-06-10-项目入口规则-生成CLAUDE.md与AGENTS.md提示词/生成AGENTS.md提示词.md` |
| `claudecode_guide/prompt/102_AGENTS.md生成提示词_分层优化版.md` | 同上目录，`生成AGENTS.md提示词-分层优化版.md` |
| `claudecode_guide/claude_md/生成-claude.md-prompt.md` | 同上目录，`生成CLAUDE.md提示词.md` |
| `claudecode_guide/claude_md/templates/`（11 文件） | `tools/templates/project-entry/`（README 为索引，10 个技术栈模板） |
| `claudecode_guide/claude_md/用户级-claude.md`、`项目级-claude.md`、`claude.md` | `tools/templates/project-entry/samples/` |
| `claudecode_guide/claude_md/rules/`（4 文件） | `tools/templates/project-entry/rules/` |
| `claudecode_guide/agent_guide/agents_store/subagent-配置指南.md` | `tools/integrations/subagent-配置指南.md` |
| `claudecode_guide/agent_guide/agents_store/` 其余 5 个 agent 定义 | `candidates/agent-definitions/`（未安装、未启用的候选） |
| `claudecode_guide/plugin_guide/插件使用与开发指南.md`、`插件收录登记.md` | `tools/integrations/`（登记内路径已更新） |
| `claudecode_guide/plugin_guide/plugin_store/` 5 个插件副本 | `tools/skills/engineering/legacy-snapshots/`（code-review、code-simplifier、feature-dev、pr-review-toolkit、ralph-wiggum） |
| `claudecode_guide/skills_guide/000-skills-cheactsheets/`（17 文件） | `docs/reference/skills-cheatsheets/` |
| `claudecode_guide/000_examples/`、`claude_setting/`、`claudeignore/` 示例配置 | `tools/integrations/examples/claude-code/`、`examples/opencode/` |

全部搬迁使用 `git mv`，Git 显示为 R（重命名），历史不丢。三条最佳实践记录按 [统一规范](../../best_practices/STANDARD.md) 写入 README，原文未改、状态 historical-unverified；提示词的分析结论只引用原文内容，不冒充实测。

## 引用更新

- `README.md` 结构块与迁移说明段
- `tests/test_workbench_migration.py`：插件副本断言指向 legacy-snapshots；新增归位契约测试
- `tools/integrations/插件收录登记.md`：目录路径、加载示例、新增流程说明
- `tools/integrations/插件使用与开发指南.md`：插件目录树
- `docs/reference/skills-cheatsheets/AI Coding 全场景工具地图.md`：standalone skills 位置说明

未改动：历史迁移记录（role-workbench-migration.md、cleanup-candidates.md、path-map.json）、用户级配置、任何宿主加载位置。

## 剩余空壳（已按批准删除）

`claudecode_guide/` 归位后仅剩：

- 15 个兼容软链（skills_guide 7、plugin_guide/playwright-skill 1、plugin_store 3、000_examples/.opencode/skills 4），全部指向 `tools/skills/*/legacy-snapshots/`；
- 1 个真文件 `000_examples/.claude/.claude-plugin/README.md`（C01 去重时的指向说明，目标内容已再次迁位，说明过时）；
- 空目录若干。

用户批准后已于 2026-10-18 整体删除（含空目录），Git 中软链记录同时消失，15 个软链目标在 `tools/skills/*/legacy-snapshots/` 仍可达。相关测试断言同步更新为“旧目录不存在”；path-map 作为历史记录不改写，测试对其中 claudecode_guide 兼容软链条目按批准删除豁免。`legacy-snapshots` 里的 5 个插件副本与其余历史快照保留，后续统一评估，不在本轮删除范围。

## 验证与边界

最小验证：`tests/test_workbench_migration.py` 与 `tests/test_role_workbench_structure.py`。没有上传 OpenViking、没有启动 Agent、没有推送、没有改用户级配置。
