# Dev Guard：Dev 禁止向外流出

## 定位与完成边界

本工具是 `wl-git-flow` 的自动检查层，不是沙箱或服务端强制门禁。用户已确认两道检查：Agent 执行前预判常见 Git 写操作；Git 推送前检查实际目标提交的 Dev 标记血缘。

```text
需求 → Dev                                      允许
同一需求 → Beta                                 允许
Dev → 需求/Beta/release/master                    拒绝
Dev → 临时 X → 需求 → Beta                        推送时拒绝
```

保护是显式登记、按仓库启用的。未登记仓库自动跳过，不因为全局安装就约束所有私人/公司仓库。通过 Git common-dir 识别仓库，一个 clone 的多个 worktree 共用登记；新 clone 需另行登记和同步。

## 安装（必须明确授权）

要求 Node.js 22+、Git、macOS/Linux Bash；无新增 npm 依赖。运行时文件位于 `scripts/dev-guard/`。下面命令在工作台根目录执行：

```bash
# 自动发现本机可执行的 Pi/Codex/OpenCode，仅安装 Agent 入口，不启用具体仓库
node tools/skills/engineering/wl-git-flow/scripts/dev-guard/install.mjs install

# 显式指定目标；沿用已有 hooksPath，不自动修改 Git 配置
node tools/skills/engineering/wl-git-flow/scripts/dev-guard/install.mjs install \
  --targets pi,codex,opencode,git --git-hooks /absolute/path/to/existing/hooks

node tools/skills/engineering/wl-git-flow/scripts/dev-guard/install.mjs status
node tools/skills/engineering/wl-git-flow/scripts/dev-guard/install.mjs uninstall
```

安装生成绝对路径调用入口，源码目录不可随意移动；移动前卸载，移动后重装。代码原位更新立即生效，但更新后 Pi 需 `/reload`，OpenCode 重启，Codex 重启并通过 `/hooks` 审核信任。安装器报告实际宿主版本，低于本机核验基线时拒绝安装；更高版本仍需核对事件兼容性，版本比较不是兼容性认证。本机调研基线：Pi 1.2.0、Codex 0.161.0、OpenCode 1.18.34。

- Pi：用户 `extensions/dev-guard.js`，监听 `tool_call` 与用户 `!` 的 `user_bash`。
- Codex：合并 `hooks.json` 的 `PreToolUse/^Bash$`，保留原配置；拒绝输出明确的 `permissionDecision=deny`，不是用普通异常代替拒绝。
- OpenCode：全局 `plugins/dev-guard.js`，使用 `tool.execute.before`、抛出异常阻止工具执行。当前使用常规插件接口，不混用 V2 setup 接口。
- Git：已有 `pre-push` 移至相邻 `.dev-guard-original`，包装器先检查，再将原参数和完整 stdin 交给原 Hook；非可执行的原 Hook保持不执行。卸载恢复原 Hook。
- 若入口已被外部修改，停止安装/卸载，不覆盖。Codex 卸载只删除自己的 matcher group，保留用户后续配置。
- 配置和标记不随卸载删除。`--home PATH` 与 `DEV_GUARD_STATE_DIR` 支持隔离验收，不用于绕过授权。

默认配置：`$XDG_CONFIG_HOME/dev-guard/config.json`（未设置时 `~/.config/dev-guard/config.json`）。安装记录：`$XDG_STATE_HOME/dev-guard/installation.json`（未设置时 `~/.local/state/dev-guard/installation.json`）。可用 `DEV_GUARD_CONFIG` 和 `DEV_GUARD_STATE_DIR` 指定；不要把这些环境覆盖当成安全隔离。

## 仓库启用和 Dev 标记

### 1. 登记仓库

```bash
node tools/skills/engineering/wl-git-flow/scripts/dev-guard/cli.mjs register --repo /path/to/repo --dev feature/dev
node tools/skills/engineering/wl-git-flow/scripts/dev-guard/cli.mjs status --repo /path/to/repo
```

登记后没有标记时保护状态为未就绪，相关操作拒绝，不静默放行。

### 2. 初始化一代 Dev（单独授权，不包含在安装里）

在检出 Dev 的干净窗口、没有进行中的 Git 操作时：

```bash
node /path/to/dev-guard/cli.mjs init-marker \
  --repo /path/to/dev-worktree --id 20261013-dev --confirm
```

生成一个单父空提交 M，保持 tree 完全相同，原子更新 Dev 分支与 lightweight tag `dev-guard/<id>`。使用 commit-tree/update-ref，不触发公司提交信息 Hook；标记不是需求提交，不含虚构 TAPD ID。登记先落盘，ref 事务失败时保护会报未就绪，需要人工修复，不能伪称初始化成功。

**不推送，不修改 master，不自动 reset，不清理旧污染。**在 Dev 已经有合法登记标记时拒绝重复初始化。Dev 重建到干净基线后创建新标记，保留旧标记登记。初始化后可按另外获得的推送授权发布 Dev 和 marker tag，不能删除/强改旧标记。

保护起点是 M：M 以前的 Dev 历史不会自动带 M，不能承诺追溯覆盖；已存在集成历史的 Dev 上补标记，只保护后续携带该标记的历史。明确引用 `feature/dev`/远端 Dev 名称的反向操作仍直接拒绝。缓存的远端旧 Dev 若位于标记之前，允许本地新标记发布，不能把该旧缓存视为已标记历史。

### 3. 新 clone / 显式同步

```bash
node /path/to/dev-guard/cli.mjs register --repo /path/to/clone
node /path/to/dev-guard/cli.mjs sync-markers --repo /path/to/clone --remote origin --confirm
```

只显式 fetch `refs/tags/dev-guard/*`，不强改本地已有标记；校验 tag 为直接指向单父空提交、与登记 SHA 一致。只信任经确认的远端，tag 不是签名认证。旧标记已登记但对象/tag缺失时拒绝；远端新标记尚未同步无法凭空发现，每代初始化/重建必须同步后再操作。标记同步不是自动全量 fetch Dev 分支，远端跟踪引用需按正常流程更新。

## 两个检查入口

### 执行前

```bash
printf '%s' '{"cwd":"/path/to/repo","command":"git merge origin/feature/dev"}' \
  | node /path/to/dev-guard/cli.mjs check-command

node /path/to/dev-guard/cli.mjs check-ref \
  --repo /path/to/repo --target feature/story/a --source temporary-x
```

支持明确写法的 merge、branch、switch/checkout 创建分支、reset、rebase、worktree -b、cherry-pick；检测分支名、SHA、转手来源的标记。切换已有 Dev 分支、路径恢复、正常需求提交不拦。明确 `--squash` / cherry-pick 带标记来源也提前拒绝，但无法追查改写后提交的原始来源。

- 支持 `git -C`、绝对 Git 路径、静态 `cd PATH && git ...`。
- 一条命令最多一次相关 Git 状态变化，避免 `switch dev && merge ...` 在旧状态下预判。`add && commit`允许。
- 已登记仓库的所有 `pull`（包括看似正常的 master pull）要求拆成 fetch 后 merge/rebase 明确引用：远端未来 tip 不能靠本地缓存保证安全。`fetch && merge`也拆成两次调用。
- 动态引用、管道、未知 Git 选项、Git alias、底层 update-ref/symbolic-ref/read-tree 等相关操作提示拆开/人工审查；不执行命令来猜结果。
- 非 Git 命令快速跳过。隐藏在任意脚本/解释器、Shell alias、MCP/远端执行中的 Git操作不保证被识别；推送端兜底保留血缘的结果。
- 现有 `start`、`integrate-dev`、`promote`、`audit` 在配置存在时调用共用 `check-ref`；未配置不改变原流程。

### 推送前

读取 Git 的原生 pre-push 四字段，按**远端目标引用**与**待推送 SHA**检查，与当前分支和本地引用名无关。拒绝标记进入所有非 Dev 分支；普通 release tags/其他 refs 也不允许携带标记；只有已登记且 SHA 匹配的 Dev marker tag 可以发布。删除操作跳过本项血缘检查，不代表授权删除分支/tag。Dev 目标也必须携带已登记标记，不允许推送未标记的 Dev 历史来替换它。

祖先查询返回 0=命中，1=未命中，其他=检查失败并拒绝。每次操作/推送检查的 Git 查询共用 3 秒预算，超时明确拒绝（Codex 外层为 5 秒）；浅克隆、缺对象、配置错误、标记/tag改写均不给出通过结论。检查禁用 Git replace-object 替代，避免基于替换历史判祖先。每次 push 加载一次配置和就绪状态，检查结果仅在单次调用去重，不跨调用缓存分支状态，不联网。

## 测试与证据

```bash
node --test tools/skills/engineering/wl-git-flow/tests/dev-guard.test.mjs

# 可选：调用已安装 Pi 的真实 Extension loader（不调用模型、不改真实配置）
DEV_GUARD_PI_ROOT=/absolute/path/to/pi-coding-agent \
  node --test tools/skills/engineering/wl-git-flow/tests/dev-guard.test.mjs
```

用临时仓库、bare origin、隔离 HOME/配置测试普通需求、直接/间接污染、SHA/refspec、worktree、Dev重建、缺失标记、配置合并与卸载恢复、原 Hook stdin转交。测试结束删除自己的临时目录。末尾输出实际耗时采样，不用时间阈值伪装性能保证。

## 无破坏可视化实验

```bash
node tools/skills/engineering/wl-git-flow/scripts/dev-guard/demo.mjs
# 输出本机证据 HTML/JSON 的绝对路径；可以用 --output PATH 指定证据目录
```

实验只创建临时仓库和本机 bare origin，所有远端操作限制为 file 协议，不访问业务仓库或网络远端。使用已安装 pre-push（没有安装时仅在临时目录接入），临时配置/登记与真实配置完全分离。五个场景：正常需求进入 Beta、三适配层前置拒绝、直接污染推送拒绝、转手污染推送拒绝、无 Hook 对照分支确实进入 Dev 内容。污染候选通过可快进断言，避免借 Git 自身非快进拒绝冒充 Hook 生效。结束后删除临时仓库，并核对真实配置/入口文件指纹没有改变。

默认产物在 `~/.local/state/dev-guard/demo/`：`index.html` 内嵌真实结果，离线可打开；`evidence.json` 包含原始命令/返回码/前后 SHA/文件列表。HTML 只提供场景切换和证据回放，不执行 Git、不启动服务；要重新做真实实验需重新运行脚本。示例数据中 `dev-only.txt` 代表不应进入 Beta 的 Dev 专属内容。

适配层协议测试不是完整宿主端到端：Codex/OpenCode 的真实加载、信任、完整会话仍需单独授权验收。工具不能防用户禁用 Hook、修改配置、`--no-verify`（Agent 明确写法会拒绝，人工仍可绕过）或抹掉血缘的内容复制；团队强制保障需服务端。源码/配置与 Agent同权限，不是安全边界。
