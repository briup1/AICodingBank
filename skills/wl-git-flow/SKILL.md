---
name: wl-git-flow
description: 安全创建、推送、集成和清理需求分支及 Git Worktree，并用用户级 HTML 看板聚合多个项目的需求生命周期。用户提到从 master 建需求分支、合入 Dev/Beta、检查污染、测试反馈、Worktree 回收、查看并行需求或打开需求看板时使用；同时兼容 TAPD 项目和没有 TAPD 的私人项目；不用于普通提交、代码评审或无需求分支语义的临时 Git 操作。
---

# WL Git Flow

两层分开维护，互不改写对方的规则。

1. **Git 原则**：需求分支怎么建、怎么合、目录什么时候删。合并、推送、清理只读这一层，以及 [references/worktree-lifecycle.md](references/worktree-lifecycle.md)。
2. **看板**：把第 1 层已经发生的状态画出来。用户要看进度、登记项目或打开页面时再读这一层，以及 [references/dashboard-model.md](references/dashboard-model.md)。

看板不新增 Git 规则，也不代替第 1 层做决定。

## 1. Git 原则

需求分支只合进 `feature/dev` 和本期 Beta。不把需求分支、`feature/dev` 或整支 Beta 直接合进 `master`。要上线的内容从本期 Beta 切到 `release/yyyymmdd`，生产发布这条 release；发布成功后由 CI/CD 把它合进 `master`，人不要自己合。目录只是同一个仓库的窗口。

```text
同一个仓库。分支指针在仓库里，不在某个文件夹里。
主目录检出哪条，文件夹就只显示哪条。
在别的窗口里合并，主目录的文件不变，但马上能看见那条分支。
不要为了「体现到主目录」把正在开发的主目录切走。

① 切出需求窗口（一个需求只开这一个）
   从当次 origin/master 建需求分支并打开目录
   不从本地 master、Dev、Beta 切
   只在这里改、提交、推送

② 合 Dev：走到 feature/dev 的共用窗口
   新的 origin/feature/dev 出现后、第一次合需求前，窗口必须已经在
   站在那里 merge --no-ff 需求分支；需求分支的 SHA 不变
   这个窗口不会被合进别的分支
   需求窗口留着等实测
   失败就回需求窗口改，再合一次
   Dev 通过后可以删需求窗口，分支留下；还要改就不删
   feature/dev 被删掉重拉：
     旧窗口干净、没有合到一半 → 删旧窗口
     本地 feature/dev 先对齐新的 origin/feature/dev
     再开新窗口，然后才能合需求

③ 合 Beta：走到本期 feature/yyyymmdd 的共用窗口
   这个日期的分支出现后、第一次合需求前，窗口必须已经在
   再 merge --no-ff 同一条需求分支
   不把 feature/dev 整支合进来
   不把这个窗口或整支 Beta 合进 master
   分支指针前进后，主目录立刻能看到这条分支
   主目录的文件仍是它自己检出的那条
   这个日期不再接收需求时删窗口
   下一期开新窗口，不把旧窗口切过去

④ 上生产：不把任何需求分支直接合进 master
   不把 feature/dev 或整支 Beta merge 进 master
   从本期 Beta 划出要上线的内容，放到 release/yyyymmdd
   生产发布的是这条 release，不是 master，也不是 Beta 窗口
   发布成功后，CI/CD 把 release/yyyymmdd 合并进 master
   人不要自己做这一步
   master 指针前进后，主目录的文件仍不变
   主目录只有自己检出 master，文件才会换成那份内容

⑤ 清的是目录，不是分支
   需求窗口：最早 Dev 通过后就能删，不必等到 Beta 或生产
   要同时满足：目录干净、提交已在远端、没有进行中的 Git 操作、没在等重测
   环境窗口：这条线被重拉，或这个日期不再接收需求时才删
   不跟单个需求走，也不按需求再复制一份
   本地分支和远端分支都留下
   以后用原分支名 git worktree add 可以再打开
```

合 Dev、合 Beta 时，先走到那条线的共用目录，再把需求分支 `merge --no-ff` 进去。不要检出需求分支后把 `feature/dev` 或 Beta 合进来，也不要把整支 Dev 或 Beta 合进另一个环境。上生产不走这条合入：切到 `release/yyyymmdd` 再发布，master 只等 CI/CD。方向看当前检出的分支，不看“合并某分支”这句口头语。

### 开始前

1. 读取目标仓库的 `AGENTS.md`、`CLAUDE.md` 和 Git 状态；项目规则优先。
2. 明确四个值：需求分支、基线 `origin/master`、Dev 目标（通常 `feature/dev`）、本次 Beta 目标。要上生产时再加 `release/yyyymmdd`：它承接从 Beta 切出的内容，不是把需求分支合进 `master` 的目标。
3. 优先运行 `scripts/wl-git-flow.sh`，不要用裸 `git pull` 猜测上游。
4. 推送、合入共享远端分支必须来自用户当前明确意图；禁止自动强推或绕过保护分支。清理只删除 Worktree 目录，不删除本地或远端分支。

### 分支和 Worktree 约定

- 默认需求分支：`feature/story/<需求标识>`，使用小写路径。TAPD 项目继续使用 `<项目ID>_<需求ID>`；私人项目可使用可读 slug，例如 `login-redesign`。
- 创建前立即 fetch，并从当次 `origin/master` 创建；不要从本地 master、Dev、Beta 创建。
- 默认 Worktree 根目录：`${GIT_REQUIREMENT_WORKTREE_ROOT:-$HOME/workdir/worktrees}`。
- 路径：`<root>/<repo>/story-<需求标识>`；长期需求 Worktree 不放 `/tmp` 或 `/private/tmp`。
- 需求标识只能包含小写字母、数字、点、下划线和短横线，且不能以分隔符开头；这同时防止路径穿越和不可预测的分支名。
- 一个活跃分支只对应一个 Worktree。一个需求只开自己的那一个。`feature/dev` 和本期 `feature/yyyymmdd` 各留一份共用目录来接收需求分支。`release/yyyymmdd` 只承接从 Beta 切出的上线内容。`master` 不是合入窗口。线换了就换目录，不要按需求复制，也不要把环境目录或 release 目录合并进别的分支。

创建示例：

```bash
skills/wl-git-flow/scripts/wl-git-flow.sh start \
  --repo /path/to/repo \
  --id 44973445_1073308

# 私人项目：不需要 TAPD，使用本地可读 slug

skills/wl-git-flow/scripts/wl-git-flow.sh start \
  --repo /path/to/private-repo \
  --id login-redesign
```

私人项目会使用同一 Worktree 根目录，例如：

```text
分支：feature/story/login-redesign
Worktree：$HOME/workdir/worktrees/private-repo/story-login-redesign
```

脚本不会要求私人项目提供 TAPD。看板上的标题从哪来，见第 2 层。

### 90% 检查点与 Dev 集成

“开发到约 90%”不是清理点，而是 **checkpoint**：

1. 需求 Worktree 内完成最小测试，提交所有有意保留的修改。
2. 确认无意外未跟踪文件、敏感信息或其他任务改动。
3. 将需求分支推送到同名远端分支。
4. 在 Dev 目标 Worktree 中更新 `origin/feature/dev`，再把需求分支合入 Dev。
5. 推送 Dev 目标后记录 `dev-testing`；需求 Worktree继续保留，等待真实环境反馈。
6. 合并前后需求分支 SHA 必须不变；目标分支必须包含该 SHA。

```bash
scripts/wl-git-flow.sh integrate-dev \
  --repo /path/to/repo \
  --source feature/story/44973445_1073308 \
  --target feature/dev \
  --target-worktree /path/to/dev-worktree \
  --push-source --push-target
```

如发生冲突，只能在已检出的 Dev 目标 Worktree 解决。若发现需求自身需要修改，回需求分支提交，再把需求分支合进 Dev。

### 测试反馈循环

Dev 结果不是 Git 能自动推断的事实。用户表达“测试通过/失败”时记录结果：

```bash
scripts/wl-git-flow.sh mark-dev-result \
  --repo /path/to/repo \
  --branch feature/story/44973445_1073308 \
  --result passed
```

- `failed`：保留 Worktree，回需求分支修改、提交、推送、重新合入 Dev。
- `passed`：记录通过的需求 SHA。之后若需求分支新增提交，原测试结论自动视为过期，必须重测。

发布成功后，CI/CD 才会把 `release/yyyymmdd` 合进 `master`。主目录上看见这次提交，只说明 CI 已经合过，不能代替发布证据：

```bash
scripts/wl-git-flow.sh dashboard mark-online \
  --repo /path/to/repo \
  --branch feature/story/44973445_1073308 \
  --evidence "发布确认"
```

这些记录给后续清理判断用。页面可以显示它们，但不能从页面改测试结论或上线结论。

### Worktree 生命周期与自动清理判断

详见 [references/worktree-lifecycle.md](references/worktree-lifecycle.md)。每次 Dev 结果、Beta 合入、master 发布或用户说“暂停/清理”时运行：

```bash
scripts/wl-git-flow.sh cleanup-plan \
  --repo /path/to/repo \
  --branch feature/story/44973445_1073308 \
  --dev feature/dev \
  --beta <本次Beta分支>
```

脚本只给出技术判断，不自动删除。这里的清理只删除本地 Worktree 目录；本地分支和远端分支都留下，进了 Dev、Beta 或 master 也不删，也不要主动提议删分支。

开发完成后可以删目录，前提是目录干净、提交已在远端、没有进行中的 Git 操作。下面任一成立就留着目录：

- 有未提交内容，或本地还有没推送的提交，或远端落后/领先。
- 正在 merge、rebase 或 cherry-pick。
- 正在 Dev 测试、测试失败，或通过之后又有新提交还没重测。
- 用户还要在这个目录里继续改。

用户同意删目录后执行，不要加删除分支的参数，也不要直接 `rm -rf`：

```bash
scripts/wl-git-flow.sh remove-worktree \
  --repo /path/to/repo \
  --worktree /path/to/story-worktree \
  --confirm
```

目录删掉后，用原来的分支名 `git worktree add` 可以再打开。

### Beta 前污染审计

```bash
scripts/wl-git-flow.sh audit \
  --repo /path/to/repo \
  --branch feature/story/44973445_1073308 \
  --base origin/master \
  --dev origin/feature/dev
```

审计至少检查：

- 分支名；
- 相对 master 的 merge commit 非第一父是否已经属于 master；
- Dev 是否成为需求分支祖先；
- 独有提交和 diff 摘要；
- 当前 SHA 是否与已通过 Dev 测试的 SHA 一致。

审计失败时不进入 Beta。已污染分支应从最新 `origin/master` 重建干净分支，并只 cherry-pick 经审计的需求提交；不要用 revert 假装清理血缘，也不要未经确认 reset/强推。

审计通过后，在已检出的 Beta 目标 Worktree 里合入需求分支。不要把 `feature/dev` 合进 Beta：

```bash
scripts/wl-git-flow.sh promote \
  --repo /path/to/repo \
  --source feature/story/44973445_1073308 \
  --target <本次Beta分支> \
  --target-worktree /path/to/beta-worktree \
  --push-target
```

Beta 实测通过时可记录 `beta-passed`；暂停开发时可记录 `paused`。这些状态只辅助清理判断，不替代 Git 祖先关系检查。

### 和看板的接缝

只允许这三处从第 1 层碰到第 2 层：

1. 生命周期写操作成功后可以刷新看板。刷新失败只报告警告，不回滚已经成功的 Git 操作。
2. 测试、暂停、上线是外部事实，在本层按当前 SHA 或明确证据记录。
3. 看板只读这些事实。不从页面执行合并、推送、删目录或删分支。

### 完成时报告

说明：

- source、target 和各自最终 SHA；
- 是否推送；
- Dev/Beta 测试状态及对应需求 SHA；
- Worktree 当前阶段、是否达到清理条件；
- 若未清理，下一次自动评估的触发点。

## 2. 看板

看板把已登记仓库里第 1 层的状态聚到本机页面。它不决定分支怎么合，也不决定目录删不删。运行时文件不写入业务仓库：

```text
~/.config/wl-git-flow/config.json
~/.local/state/wl-git-flow/state.json
~/.local/share/wl-git-flow/dashboard.html
```

Git 分支、Worktree、dirty、upstream、ahead/behind 和 Dev/Beta/master 祖先关系由扫描自动计算。数据模型、状态优先级和页面接口见 [references/dashboard-model.md](references/dashboard-model.md)；那里不重写第 1 层的合并和清理规则。

### 命令

```bash
# 首次登记项目并生成看板
scripts/wl-git-flow.sh dashboard register --repo /path/to/repo

# 扫描所有登记项目并刷新 HTML
scripts/wl-git-flow.sh dashboard refresh

# 刷新后打开默认浏览器
scripts/wl-git-flow.sh dashboard open

# 推荐：启动仅 localhost 的前台实时模式并打开浏览器
scripts/wl-git-flow.sh dashboard serve --port 0 --open

# 前台周期刷新；Ctrl+C 停止，不安装常驻服务
scripts/wl-git-flow.sh dashboard watch --interval 10 --open
```

非 `master`/`feature/dev` 项目可在登记时显式传 `--base-ref`、`--dev-ref`、`--worktree-root` 和重复的 `--pattern`。这只改变后续扫描认哪条基线，不改变第 1 层的合并方向。

同一需求的多个分支聚合为一张卡片。需要纠正主分支或补充主题时使用：

```bash
scripts/wl-git-flow.sh dashboard set-primary --repo /path/to/repo --requirement 44973445_1073445 --branch feature/story/44973445_1073445-clean-20260920
scripts/wl-git-flow.sh dashboard set-title --repo /path/to/repo --requirement 44973445_1073445 --title "航线代码和运输条款展示与查询"
scripts/wl-git-flow.sh dashboard sync-titles --repo /path/to/repo
```

`sync-titles` 是显式只读 TAPD 操作；普通 `refresh/open/watch` 不访问 TAPD。标题优先级为手工覆盖、TAPD 缓存、Git 提交主题、需求编号。只有显式运行 `dashboard sync-titles` 时，数字格式的需求标识才会尝试读取 TAPD；私人 slug 会保留 Git 标题或手工标题。

上线确认的命令和判定在第 1 层，不在这里重复。

### 实时模式边界

`dashboard serve --open` 是日常推荐入口：页面可点击“刷新状态”，也可临时选择 15/30/60 秒自动刷新（默认关闭）。服务固定监听 `127.0.0.1`、随机端口、前台运行，`Ctrl+C` 停止；它只暴露看板 state/refresh/health，不提供 Agent、terminal、push、merge、branch delete 或发布接口。

`dashboard open` 保持静态降级语义。静态页面显示“静态快照”，按钮只能重新加载已有文件，并提示使用 `serve --open` 执行真实 Git 扫描。

### 上线后的显示

需求上线后立即移入“最近上线”，默认 7 天后进入隐藏归档；若归档后发现不同 SHA、需求分支或 Worktree，自动重新打开。显示规则的细节只改 [references/dashboard-model.md](references/dashboard-model.md)。
