# Worktree 生命周期

归属 SKILL.md 第 1 层。本文件只规定目录什么时候删、分支为什么留。看板上的阶段名称若要改显示，同时改 [dashboard-model.md](dashboard-model.md)；清理动作仍以本文件为准。

Worktree 是分支的本地工作目录，不是分支本身。清理只删除这个目录。本地分支名和远端分支都保留，需求进了 Dev、Beta 或 master 之后也一样。

## 状态机

需求 Worktree 在切出、Dev、Beta、生产、清除时站在哪，以 SKILL.md 第 1 层的生命周期图为准。下面只标目录能不能删。

```text
created
  │ 开发、提交
  ▼
active
  │ 本地检查完成并推送需求分支
  ▼
checkpointed
  │ 需求分支 -> feature/dev，并推送 Dev
  ▼
dev-testing ──失败──> dev-failed ──修改/推送/再合入 Dev──> dev-testing
  │
  └─通过──> dev-passed
              │
              ├─ 目录可删，分支保留
              │
              └─ 需求分支 -> Beta
                    │
                    └─ 切出 release/yyyymmdd
                          │ 发布成功，CI 合进 master
                          ▼
                       released
                          │
                          └─ 目录可删，分支仍保留
```

合入箭头的起点在 Dev 和 Beta 始终是需求分支。`feature/dev` 和 Beta 只作为检出后的目标，不作为被合进去的分支。`master` 不接收需求分支，也不接收整支 Beta；上线内容在 `release/yyyymmdd`，发布成功后由 CI/CD 合进 `master`。

## 自动识别能做什么

脚本可从 Git 自动判断：

- Worktree 是否注册、是否干净；
- 分支是否有 upstream；
- 本地是否领先/落后远端；
- 当前需求 SHA 是否已进入 Dev、Beta 或 master；
- 当前 SHA 是否仍等于最近一次记录的 Dev 通过 SHA；
- 是否存在未完成 merge/rebase/cherry-pick；
- 是否满足安全移除 Worktree 目录的技术前提。

脚本无法仅从 Git 判断：

- Dev 环境是否真的发布成功；
- 产品、测试人员是否确认通过；
- 是否马上还要本地调试；
- 远端需求分支是否仍被其他人使用。

因此删目录采用“自动识别 + 人工确认”，不做静默删除。

## 清理：只删目录

适用情况：

- 开发已完成，或用户明确说清理、暂停；
- Worktree 干净；
- 本地提交全部存在于同名远端分支；
- 没有进行中的 Git 操作。

Dev 已通过、已进入 Beta，或当前 SHA 已进入 `origin/master`，都适用同一动作。

结果：

- 删除工作目录；
- 保留本地分支和远端分支；
- 后续用原来的分支名 `git worktree add <path> <branch>` 恢复。

不要提议删除分支，也不要给 `remove-worktree` 加上删除分支的参数。

## 不应删除目录的时机

以下任一成立就保留 Worktree：

- 有未提交或未跟踪内容；
- 本地有未推送提交；
- 正在 merge/rebase/cherry-pick；
- Dev 正在测试或测试失败；
- Dev 通过后需求分支又新增提交，尚未重测；
- 用户仍在这个目录里继续改；
- 无法确认 Worktree 对应的真实分支。

## 建议提问文案

目录已经可以删：

> 工作区干净，提交已在远端。可以删掉本地 Worktree 目录，本地和远端分支都保留。现在删目录吗？

还要继续进 Beta 或接着改时，直接留着目录，不必为了清理再问一次。
