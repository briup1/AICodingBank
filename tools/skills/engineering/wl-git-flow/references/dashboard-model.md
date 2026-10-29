# 用户级需求开发看板模型

归属 SKILL.md 第 2 层。本文件只规定看板存什么、显示什么。合并方向和“只删目录”以 SKILL.md 第 1 层、[worktree-lifecycle.md](worktree-lifecycle.md) 为准；改显示不得改那些规则。

## 事实分层

- Git 事实：分支、Worktree、dirty、upstream、ahead/behind、SHA、Dev/Beta/master 祖先关系。
- 外部事实：Dev/Beta 测试结果、上线确认、需求标题和备注。
- 派生状态：代码阶段、验证状态、异常、下一步、可见性和清理建议。

HTML 只展示派生结果，不成为事实来源。

## 需求与分支

主实体是 `projectId + requirementId`，不是分支。`requirementId` 可以是 TAPD 的 `项目ID_需求ID`，也可以是私人项目的本地 slug。同一需求的 clean、旧分支、candidate 等作为 `branches[]` 展示；需求阶段只取主分支。主分支优先使用用户显式选择，其次使用拥有活跃 Worktree 的分支，再回退到规范分支名和最近活动分支。

需求标题优先使用手工覆盖，其次是显式同步并缓存的 TAPD 标题，再回退到 Git 提交主题和需求编号。私人项目可以使用可读的需求 slug，不要求 TAPD；这类需求跳过 TAPD 标题同步。普通看板刷新不联网。

生命周期事件统一写入用户级 `state.json`。历史 `branch.*.requirementFlow*` Git 配置只允许兼容读取并迁移，新的工作流不得继续写入业务仓库 `.git/config`。

## 默认路径

```text
~/.config/wl-git-flow/config.json
~/.local/state/wl-git-flow/state.json
~/.local/share/wl-git-flow/dashboard.html
```

测试和临时运行应使用 XDG 环境变量隔离。

## 项目登记

只扫描登记项目。首次通过本 Skill 操作仓库时可幂等登记；不得递归扫描整台机器。项目删除或暂不可达时保留最后快照并显示错误。

## 状态优先级

```text
online/recent/archive
  > merged-master
  > beta-passed / beta-testing
  > dev-failed / dev-passed / dev-testing
  > ready-dev
  > active / paused
  > missing
```

异常作为独立 badges 叠加。测试通过必须绑定 SHA；SHA 改变后显示 stale-test。

## 可见性

- active：默认展示。
- recently-online：上线后立即进入，默认保留 7 天。
- archived：保留期结束后隐藏，可筛选查看。
- reopened：归档后发现不同 SHA、需求分支或 Worktree 时恢复 active。

## 本地实时模式

实时模式由前台 localhost 服务提供，静态 HTML 仍是降级入口。

```text
GET  /             实时 HTML
GET  /api/state    最近一次快照，不扫描
POST /api/refresh  串行执行只读 Git 扫描
GET  /api/health   服务健康
```

服务固定绑定 `127.0.0.1`，使用随机会话 Token、同源 Origin 校验、POST-only refresh、无 CORS。页面默认手工刷新；自动刷新仅提供关闭/15/30/60 秒且默认关闭，页面隐藏或已有刷新时不重复扫描。实时更新只替换数据，不重置筛选、视图、滚动或分支展开状态。

看板不提供 Agent 启动、终端、Git 写操作、发布或外部系统写入接口。
