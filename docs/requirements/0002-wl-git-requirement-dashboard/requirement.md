---
id: 0002
slug: wl-git-requirement-dashboard
status: approved
created: 2026-09-21
source: 用户确认的多项目 Worktree 与需求生命周期管理诉求
---

# 需求 0002：用户级 Git 需求开发看板

## 需求重定义

**原始诉求**：同时开发三到四个以上需求时，无法快速知道某个需求是否仍在开发、对应哪个 Worktree、处于哪个测试或发布阶段，希望用 HTML 看板统一管理。

**最终目标**：在用户级范围聚合已登记项目的 Git 分支、Worktree、远端同步和祖先关系，以 HTML 展示需求从首次发现到 Dev、Beta、主干、上线、清理和归档的完整生命周期；Git 可证明的状态自动计算，测试和上线等外部事实只保存最小证据。

**约束**：

- 能力继续归属 `wl-git-requirement-flow`，不新增第二个 Skill。
- 源码位于 AICodingBank；不向业务仓库写入看板、状态或配置。
- 运行数据位于用户级 XDG 目录，默认不共享、不上传、不监听网络端口。
- HTML 是只读投影，不直接执行 Git 操作。
- 不扫描整个磁盘；只扫描显式登记或通过本 Skill 使用过的仓库。
- Git 扫描默认不 fetch，避免打开看板产生网络副作用。
- 合入 master 不等于已上线；初版上线状态由用户明确确认。
- Python 固定使用 uv 管理的 3.12.9，不使用系统 Python。

## 用户故事

1. As a **并行需求开发者**, I want 在一个 HTML 中看到所有已登记项目的活跃需求、分支和 Worktree, so that 我不必记住多个目录。
2. As a **需求负责人**, I want Git 可证明的生命周期阶段自动更新, so that 看板不会依赖手工维护表格。
3. As a **测试反馈接收者**, I want Dev/Beta 结果绑定到具体提交 SHA, so that 新提交出现后旧测试结论自动失效。
4. As a **发布跟踪者**, I want 区分“已合主干”和“已上线”, so that 看板不会虚报发布状态。
5. As a **本机工作区维护者**, I want 看板指出 dirty、未推送、detached、临时目录和待清理项, so that Worktree 数量增加后仍能安全回收。
6. As a **长期使用者**, I want 已上线需求先进入最近上线、随后自动隐藏归档，并在出现新提交时重新打开, so that活跃视图保持简洁且历史可追踪。

## 不做什么

- 普通刷新不接入外部系统；允许用户显式调用只读 TAPD 标题同步，不接 GitLab API、Fuxi 或生产环境。
- 不自动判断真实 Dev/Beta 测试是否通过。
- 不把 master merge 自动等同于生产上线。
- 不提供多人协作、账号权限、远程分享或数据库服务。
- 不在 HTML 内提供 merge、push、delete 等写操作按钮。
- 不自动迁移或删除当前 `/private/tmp` Worktree。

## 验收标准

1. `dashboard refresh` 能扫描多个已登记仓库并生成单文件 HTML。
2. HTML 提供 Kanban、表格、项目筛选、文本搜索、活跃/最近上线/归档切换。
3. 每个需求显示项目、需求编号、分支、Worktree、Git 同步、代码阶段、验证状态、当前 SHA、下一步和异常。
4. dirty、ahead/behind、detached、临时目录、测试 SHA 过期和待清理能够自动标记。
5. `start`、`integrate-dev`、`mark-dev-result`、`promote`、`mark-stage`、`remove-worktree` 成功后自动刷新看板。
6. `dashboard open` 先刷新再打开；`dashboard watch` 前台刷新且可通过 Ctrl+C 停止。
7. 已上线需求立即移出活跃区，默认 7 天后进入隐藏归档；新提交或分支重现时自动重新打开。
8. 所有运行时文件只写入用户级配置、状态和数据目录。
9. Compass-Platform 只读扫描验证不会改动其工作区。
10. 同一项目、同一需求编号的多个分支聚合为一张卡片，主分支状态作为需求主状态。
11. 卡片显示需求主题，来源优先级为手工覆盖、TAPD 缓存、Git 提交主题、需求编号。
