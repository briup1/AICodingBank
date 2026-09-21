# 0002 开发进度

更新：2026-09-21

| 工作包 | 状态 | 产物 | 验证 |
| --- | --- | --- | --- |
| A. 用户级配置、状态与多仓库 Git 扫描 | 完成 | `scripts/dashboard.py` | scanner/lifecycle/安全测试通过 |
| B. 静态 HTML 看板 | 完成 | `assets/dashboard-template.html` | 占位符、无外链、JS 语法、桌面/窄屏真实渲染 |
| C. 既有生命周期命令集成 | 完成 | `wl-git-requirement-flow.sh`、`SKILL.md` | Bash 语法与流程 E2E 通过 |
| D. 文档、真实扫描与回归 | 完成 | requirement/design/plan、Compass 用户级实例 | 聚焦 28 passed；一级 tests 42 passed、1 个既有无关失败 |

## 交付证据

- 用户级 HTML：`~/.local/share/wl-git-requirement-flow/dashboard.html`。
- Compass 已登记为首个项目；分支按需求聚合后当前展示 3 个需求和 8 项需关注事实。
- `44973445_1073445` 的两个分支已聚合为一张卡片，活跃 clean Worktree 自动成为主分支，旧分支进入 Dev 作为子项展示。
- 已显式同步 Compass 的 TAPD 标题；普通 refresh 仍然不联网。
- Compass 扫描前后 `git status --short --branch` 一致。
- Compass 主 index 和 linked Worktree index 的 SHA-256 与 mtime 在扫描前后均未变化。
- 远端历史需求分支不会进入活跃看板；只展示本地分支、Worktree 或已管理记录。
- 生命周期事件写入用户级 `state.json`；旧 `.git/config` 字段只一次性兼容迁移。
- 软清理保留生命周期；最终退役显式记录 pending 与 cleaned，软清理后可不重建 Worktree直接退役分支。
- 独立审查提出的 Git 可选锁、linked Worktree 重复登记、分支失联、清理事件等问题已修复并补测试。

## 已知无关失败

`pytest -q tests` 当前结果为 42 passed、1 failed。失败来自既有 `harness-pack` 模板测试：`assets/harness-template/rules/工程结构.md` 缺少测试要求的“后端”文本，与本需求无关，本次未修改该模块。
