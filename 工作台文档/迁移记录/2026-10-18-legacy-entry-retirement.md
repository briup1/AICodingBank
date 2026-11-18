# 旧入口兼容层退役记录

日期：2026-10-18。依据：用户在岗位制迁移与 claudecode_guide 归位后，授权执行“退役四步”：宿主软链重连 → 用户级引用更新 → 删除仓库兼容项 → 同步测试契约。

## 退役前的现状

```text
~/.claude/skills  (62 个软链) ─┐
~/.agents/skills  (64 个软链) ─┼→ 仓库 skills/<name>（兼容层）→ tools/skills/<分类>/<name>
~/.hermes/skills  (63 个软链) ─┘
skills-on-demand/（5 个软链）、ai_coding_sec_dev_workflow 同理
```

用户级引用仅一处物理文件：`/Users/ziyun/.agents/AGENTS.md`（`/Users/ziyun/.config/opencode/AGENTS.md` 是指向它的软链）。

## 执行与证据

1. **宿主重连**：运行 `python3 install.py`（用户授权，含 vendor 上游同步）。结果：85 个登记、21 个待验证、0 条异常、CATALOG.md 无变化。三个宿主目录重连后：穿过兼容层的链接 0 个，直连 `tools/skills` 各 31 个，vendor 31/33/32 个，断链 0 个。宿主中非本仓库管理的真实目录（grilling、research、wayfinder 等）保持不覆盖。前后链接快照存于 `.local/host-links/`（本机证据，不入 Git）。
2. **用户级引用更新**：`~/.agents/AGENTS.md`（`~/.config/opencode/AGENTS.md` 为其软链）中 `skills/wl-git-flow`、`skills/hgj-git-connect` 改为 `tools/skills/engineering/...`；工作台结构树同步为当前实际（tools/、roles/、best_practices/，移除 skills/、ai_coding_sec_dev_workflow/double_layer_spec、claudecode_guide 旧条目）。删除仓库兼容项后全量测试暴露 4 个指向旧 dev-guard 路径的宿主引用，已随同修复：
   - `~/git-hook/hooks/pre-push`（全局 `core.hooksPath` 的 pre-push，写死旧 `skills/wl-git-flow/scripts/dev-guard/cli.mjs`，导致全机 git push 直接失败）；
   - `~/.config/opencode/plugins/dev-guard.js`、`~/.pi/agent/extensions/dev-guard.js`、`~/.codex/hooks.json`（与 `~/.Codex/hooks.json` 为同一物理文件）中的 dev-guard 适配器路径。
   修复后全量 pytest：124 passed，仅余 1 个既有 harness-pack 模板失败（自基线 `21f2dd6` 起未改动，与本次无关）。
3. **仓库删除**：`skills/`（28 个软链 + 空目录 wl-phase-routing）、`skills-on-demand/`（5 个软链）、根软链 `ai_coding_sec_dev_workflow`，共 34 个追踪项；空目录 `double_layer_spec/`、`.marscode/` 一并清除。
4. **测试契约同步**：`test_compatibility_paths_resolve_without_skill_copies` 重写为“旧入口不存在 + 保留的项目级 langfuse 路径仍解析”；path-map 历史记录不改写，测试对 `skills/`、`skills-on-demand/`、`ai_coding_sec_dev_workflow` 的兼容软链条目按批准退役豁免（与 claudecode_guide 同规则）。

## 保留项

- 仓库 `.agents/skills/langfuse` → `tools/skills/engineering/legacy-snapshots/langfuse`（个项目级加载路径，链锁 `.claude/skills/langfuse`），未在退役范围。
- `skills.yaml` 登记、`skills-lock.json`、CATALOG.md 不变；vendor 缓存内容未删。
- 历史迁移/清理/归位记录不改写。

## 回滚

重跑 `python3 install.py` 可按登记重建宿主链接；仓库删除可用 `git revert` 恢复。退役不涉及第三方源码与验证状态，回滚不改能力语义。

## 未覆盖

宿主链接的功能验证只到“链接可达、无断链”；未逐一运行各宿主验证各 Skill 实际加载，也未改变任何 Skill 的 verified 状态。dev-guard 的 pre-push 钩子已用真实 push 验证恢复，opencode/pi/codex 三个适配器只做了路径存在性核对，未在各自宿主会话中实测加载。
