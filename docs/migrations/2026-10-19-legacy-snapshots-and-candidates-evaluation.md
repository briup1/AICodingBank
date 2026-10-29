# 迁入快照与候选目录评估及收口记录

日期：2026-10-19。依据：结构收敛收尾验收后，用户对“待定夺残留项”要求统一评估，并批准执行档位“删 17 项（15 个快照包 + 2 个候选目录），保留 langfuse 与媒体两项”。删除均经该批准，缓存清理为顺手动作。

## 评估基准

来源是否可再取、是否与已登记能力重复、是否有独有内容、是否有使用证据。迁移时的底线“不能无证据丢掉独有内容”在本次逐项评估后由用户决定去留。

## 逐项结论

### A 组：Anthropic 官方插件副本（8 个，删）

code-review、code-simplifier、feature-dev、frontend-design、pr-review-toolkit、ralph-wiggum、plugin-dev（engineering）、agent-browser（shared）。

作者证据：plugin.json 标注 Anthropic / Boris Cherny / Daisy Hollman；官方插件市场可重装。重复关系：at-review、codex-simplify、wl-* 开发流程、已登记 taste-skill、wl-web-auto（opencli 为既定浏览器主线）。

### B 组：来源可再取的第三方（3 包，删）

- playwright-skill（lackeyjb，MIT）：重复 at-test 的 playwright 模式。
- opencode/openspec×4：来自示例项目，从未接入流程。
- brainstorming（superpowers 系）：重复自研 wl-brainstorming。

### C 组：来源未标注、与主栈错配的大包（4 个，删）

frontend-dev（React/Next/GSAP 方向，98 文件）、fullstack-dev（Express/Node 方向）、android-native-dev、ios-application-dev。用户前端为 Vue/Nuxt、后端为 Java/Spring，无移动开发场景；包内无来源标注，无法登记验证。

### D 组：媒体向 2 包（保留，未验证候选）

- hot_topics（热搜榜单，作者 vikiboss，MIT，API 60s.viki.moe）：媒体内容组方向相关。
- remotion-best-practices（Remotion 官方最佳实践）：视频线参考。

无使用证据，保留为“媒体候选”，不安装、不提升验证状态。

### E 组：langfuse（保留）

项目级加载链在用：`.agents/skills/langfuse`（及 `.claude/skills/langfuse`）→ `tools/skills/engineering/legacy-snapshots/langfuse`。skill-lock 中登记为待验证，与上游差异未核对。

### candidates（2 目录 10 文件，删）

- ecc ×5（everything-claude-code @5df943e，v1.9.0，MIT）：与 at-review 重合；“精选 Rules 待归档”计划自此终止。
- agent-definitions ×5：通用示例（code-reviewer、db-reader×2、debugger×2）；db-reader 的只读校验 hook 思路已由工作台权限体系覆盖。

## 执行内容

1. 删除 15 个快照包与 candidates 两目录，共 249 个追踪文件；`tools/skills/shared/legacy-snapshots/` 目录随删除消失，`tools/skills/engineering/legacy-snapshots/` 只保留 langfuse，媒体目录保留 hot_topics 与 remotion-best-practices。
2. 引用同步：插件收录登记.md 转为索引（副本清除说明、重装方式、维护记录）、插件使用与开发指南.md、tools/integrations/README.md、tools/skills/README.md、tools/skills/shared/README.md、AGENTS.md 红线、skills-cheatsheets 工具地图。
3. 测试契约：path-map 测试对 15 个已退快照目标改为“不存在”断言；插件清理测试的 5 个文件断言翻转；归位测试移除 debugger.md 存在断言并新增保留项断言。
4. 缓存清理：`__pycache__`、`.pytest_cache`（Git 忽略，可再生）。

## 回滚

`git revert` 可整体恢复。再取方式：A 组走 Claude Code 插件市场；playwright-skill 取 lackeyjb 上游；brainstorming 取 superpowers；openspec 取 OpenSpec 项目；ecc 取 everything-claude-code @5df943e。

## 未覆盖

未逐文件比对快照与上游差异（按“可再取”原则处理，不视为证据缺失）；保留的媒体两项未做功能验证；langfuse 与上游差异仍待核对。
