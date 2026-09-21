---
id: 0002
slug: wl-git-requirement-dashboard
status: approved
created: 2026-09-21
requirement: requirement.md
chosen: A
---

# 方案设计：用户级 Git 需求开发看板

## 1. 方案选择

选择 **A：Skill 内置扫描器 + 用户级状态 + 静态 HTML**。

| 方案 | 结论 | 原因 |
| --- | --- | --- |
| A. Skill 内置扫描器生成静态 HTML | 采用 | 无服务、跨项目、可复用现有生命周期脚本，成本与需求匹配 |
| B. 手工 Markdown | 拒绝 | 容易漂移，不能自动发现 Git 异常 |
| C. 独立本地服务和数据库 | 暂缓 | 当前没有交互写入、多用户或实时 API 需求 |

## 2. 组件与边界

```text
业务 Git 仓库（只读）
  ├─ refs / worktrees / status / ancestry
  └─ 旧 branch.*.requirementFlow* 仅兼容读取并迁移，不再写入
                  │
                  ▼
 dashboard.py 扫描与状态计算
  ├─ config.json：仓库登记与策略
  ├─ state.json：外部事实、最后快照、归档
  └─ dashboard-template.html：只读视图
                  │
                  ▼
 dashboard.html（单文件、用户级、本机打开）
```

- `wl-git-requirement-flow.sh` 是唯一命令入口。
- `dashboard.py` 使用 Python 标准库，不增加运行依赖。
- Dev/Beta/清理事件以用户级 `state.json` 为权威；旧 `.git/config` 字段只作一次性兼容来源。
- HTML 内嵌当前 JSON 数据、CSS 和 JavaScript，不依赖 CDN。
- 业务仓库扫描默认不 fetch，不写文件，不更改 refs。

## 3. 用户级文件契约

| 类型 | 默认路径 | 权威内容 |
| --- | --- | --- |
| 配置 | `~/.config/wl-git-requirement-flow/config.json` | 登记仓库、分支角色、匹配规则、保留期 |
| 状态 | `~/.local/state/wl-git-requirement-flow/state.json` | 测试/上线证据、首次/最后发现、最后 Git 快照、归档 |
| HTML | `~/.local/share/wl-git-requirement-flow/dashboard.html` | 当前只读投影，可随时重建 |

测试通过 `XDG_CONFIG_HOME`、`XDG_STATE_HOME`、`XDG_DATA_HOME` 隔离。

## 4. 状态模型

### Git 代码阶段

`active → ready-dev → dev-testing/dev-failed/dev-passed → beta-testing/beta-passed → merged-master → cleaned`

异常状态优先展示，但不覆盖原阶段：dirty、unpushed、behind、detached、temporary-path、stale-test、missing-repository、duplicate-worktree。

### 验证与发布状态

- Dev/Beta 结果绑定提交 SHA。
- 当前 SHA 与通过 SHA 不一致时自动标记过期。
- `merged-master` 自动产生 `待上线`，不能自动产生 `已上线`。
- `mark-online` 保存时间、最终 SHA 和可选证据。
- 看板按 `projectId + requirementId` 聚合分支；显式主分支优先，其次选择有活跃 Worktree 的分支。
- 标题优先级：手工覆盖 > TAPD 缓存 > Git 提交主题 > 需求编号。普通 refresh 不访问 TAPD。

### 可见性

- 默认：活跃与需要关注。
- 已上线：立即进入 `recently-online`。
- 到达 `recentlyOnlineDays`：进入 `archived`，默认隐藏。
- 已归档记录发现新分支、Worktree 或不同 SHA：重新打开。

## 5. HTML 交互

- 顶部显示活跃、需关注、Dev、Beta、待上线、最近上线数量。
- Kanban 与表格视图共享同一数据。
- 支持项目、状态、异常和文本筛选。
- 最近上线和归档默认折叠/隐藏，可显式查看。
- 页面不发网络请求，不提供 Git 写按钮。
- 页面展示生成时间和仓库扫描错误，避免把旧数据当实时事实。

## 6. 命令契约

```text
dashboard register --repo PATH [--name NAME]
dashboard refresh
dashboard open
dashboard watch [--interval 10]
dashboard mark-online --repo PATH --branch BRANCH [--evidence TEXT]
dashboard archive --repo PATH --branch BRANCH
dashboard show-path
dashboard set-primary --repo PATH --requirement ID --branch BRANCH
dashboard set-title --repo PATH --requirement ID --title TEXT
dashboard sync-titles [--repo PATH] [--requirement ID] [--force]
```

所有既有成功写操作结束后调用一次无网络的 dashboard sync；刷新失败只警告，不回滚已完成 Git 操作。

## 7. 安全、性能与兼容

- 配置、状态、HTML 使用用户权限目录并原子写入。
- HTML 对所有 Git 文本进行 JSON/HTML 安全编码。
- 单仓库扫描使用有限 Git 子进程；状态检查只针对已登记需求 Worktree。
- 仓库不可达时保留最后快照并显示错误，不删除记录。
- 配置和状态包含 `version`，未知版本拒绝覆盖。
- 运行时无第三方 Python 包；浏览器端无外部资源。

## 8. 回滚

删除用户级 config/state/data 目录即可完全停用看板，不影响业务仓库。代码回滚只需恢复 Skill 文件；既有分支和 Worktree 流程继续可用。
