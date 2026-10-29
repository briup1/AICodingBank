# 合并回滚 Runbook

## 2026-10-29 `feature/R-20261018-role-workbench` → `main`

- 上线内容：工作台入口收敛为 `AGENTS.md`、个人项目索引归位、岗位/Skill/工具目录整理及相关迁移文档与测试契约更新。
- 合并提交：`8df15b189c8e55465950e87e7f0926a32622d8a7`
- 合并方式：本地 `git merge --no-ff`；本次未推送远端，未执行部署。
- 回滚方式：`git revert -m 1 8df15b189c8e55465950e87e7f0926a32622d8a7` → 重跑 Python/Node 检查 → 复核工作台入口与 Skill 登记。
- 更快手段：无 feature flag；如尚未推送，可将本地 `main` 重置回合并前提交，但不得对共享远端使用强推。
- 限制：这是 merge commit，必须使用 `-m 1`；回滚会一并撤销该分支包含的目录迁移、文档和测试契约变化，执行前需确认是否有后续提交依赖新路径。
- 观察期：本次没有部署或运行服务；后续首次使用新入口时重点核对 `AGENTS.md`、`personal/projects.local.md`、`skills.yaml` 与目标 Skill 路径。
