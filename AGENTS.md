# AICodingBank

## 找项目或接续任务

- 从本机索引 `personal/projects.local.md` 找项目主仓库；索引只维护稳定入口，不登记每个 Worktree。索引缺失时看 [换机与本机恢复](README.md#换机与本机恢复)，不猜路径。
- 接续指定任务：先从用户说明或已有任务记录确认需求编号／分支，再运行 `git -C "$repo" worktree list --porcelain`（`repo` 为主仓库绝对路径），按 Git 登记匹配。统一 Worktree 根目录是放置约定，不是筛选条件；根目录外的已登记副本也算。
- 动手前，核对选中的目录实际存在、Git 顶层和当前分支与任务一致。跨仓逐仓区分「只读参考」与「允许修改」。任务副本找不到或有歧义时，列出候选和缺项，不默认回主目录。定位不创建、切换、移动或清理副本。
- 确定副本后，先读目标项目适用的 Agent 入口，按项目导航读取相关需求、Wiki、构建配置或记录。业务规则与验证结论留在项目，不在工作台复制。

## 找共享能力

- 找 Skill：`CATALOG.md`（能力与使用边界）；Pi 本机按需路由见可选的 `~/.pi/agent/skill-index.local.md`，不替代 Skill 触发条件或更高优先级规则。
- 找岗位：`roles/README.md`；明确需要 PM 时见 `roles/project-manager/ROLE.md`。
- 找模板或辅助材料：`tools/templates/`、`tools/prompt-library/README.md`；选图见 `docs/reference/diagram-atlas.html`，换思路见 `docs/reference/thinking-atlas.html`；可视文档管理见 `tools/skills/shared/visual-artifact-workbench/SKILL.md`。

## 找执行或验收入口

- 找调研、开发与验收方法：`docs/SOP入口.md`；找工具或宿主接入：`tools/README.md`、`tools/execution-profiles/README.md`。
- 要执行或回读测试：`tools/execution-profiles/test-execution.md`；Compass 业务规则、页面证据与 Agent 行为评估的分工见 `docs/reference/Compass跨仓回归导航.md`。

## 维护工作台

- 增改 Skill、岗位与最佳实践：`EXTENDING.md`；查术语：`CONTEXT.md`；查本机记录：`.local/README.md`（工作台记录，不是各项目的证据目录）。
- 换机或检查本机接入：`README.md`；找完整目录及参考资料：`docs/reference/工作台目录地图.md`。
