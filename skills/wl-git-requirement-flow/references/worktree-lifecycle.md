# Worktree 生命周期

Worktree 是分支的本地工作目录，不是需求状态本身。清理 Worktree 不等于删除分支；但按当前个人约定，需求最终进入 master 后不再保留本地或远端需求分支。

## 状态机

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
dev-testing ──失败──> dev-failed ──修改/推送/重合──> dev-testing
  │
  └─通过──> dev-passed
              │
              ├─可选：移除 Worktree、保留分支
              │
              └─需求分支 -> Beta -> master
                                  │
                                  ▼
                               released
                                  │
                                  └─最终退役：确认后移除 Worktree、本地分支和远端需求分支
```

## 自动识别能做什么

脚本可从 Git 自动判断：

- Worktree 是否注册、是否干净；
- 分支是否有 upstream；
- 本地是否领先/落后远端；
- 当前需求 SHA 是否已进入 Dev、Beta 或 master；
- 当前 SHA 是否仍等于最近一次记录的 Dev 通过 SHA；
- 是否存在未完成 merge/rebase/cherry-pick；
- 是否满足安全移除 Worktree 的技术前提。

脚本无法仅从 Git 判断：

- Dev 环境是否真的发布成功；
- 产品、测试人员是否确认通过；
- 是否马上还要本地调试；
- 远端需求分支是否仍被其他人使用。

因此清理采用“自动识别 + 人工确认”，不做静默删除。

## 两级清理

### 软清理：移除 Worktree，保留分支

适用情况：

- Dev 已通过，或用户明确暂停；
- Worktree 干净；
- 本地提交全部存在于同名远端分支；
- 没有进行中的 Git 操作。

结果：

- 删除工作目录；
- 保留本地分支和远端分支；
- 后续可通过 `git worktree add <path> <branch>` 恢复。

这是 Dev 通过后、尚未进入 master 时唯一默认允许的清理。

### 最终退役：移除 Worktree和本地分支

适用情况：

- 当前需求 SHA 已经进入最终目标，通常是 `origin/master`；
- Worktree 干净且远端同步；
- 用户确认不再需要本地分支。

按当前约定，最终退役默认同时删除远端需求分支，但仍需用户对本次最终清理明确确认；Dev/Beta 阶段不得提前删除。

## 不应清理的时机

以下任一成立就保留 Worktree：

- 有未提交或未跟踪内容；
- 本地有未推送提交；
- 正在 merge/rebase/cherry-pick；
- Dev 正在测试或测试失败；
- Dev 通过后需求分支又新增提交，尚未重测；
- 用户仍在连续调试，移除后很快需要重建；
- 无法确认 Worktree 对应的真实分支。

## 建议提问文案

Dev 通过但尚未进入 Beta：

> 当前需求 SHA 已完成 Dev 测试，Worktree 干净且全部提交已推送。技术上可以移除 Worktree并保留需求分支；如果马上还要进 Beta，保留会更方便。现在移除还是保留到 Beta 完成？

需求进入 master：

> 当前需求 SHA 已进入 origin/master，Worktree 干净且远端同步。建议执行最终退役：移除 Worktree，并删除本地和远端需求分支。是否执行？

暂停开发：

> 当前修改已全部推送，Worktree 可以安全移除并在以后重建。是否进行软清理？
