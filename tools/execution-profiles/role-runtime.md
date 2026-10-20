# 岗位按需运行与恢复

状态：2026-10-19 已完成真实按需启动、同实例复用及跨命令进程读取验证。范围经用户批准；运行证据见[本次验收](../../docs/requirements/0004-role-runtime/verification.md)。

## 谁在什么时候使用

仅在用户要求长期项目组、跨会话恢复、成员复用与任务历史，或继续已有台账任务时使用本入口。普通委派默认按 [wl-herdrs](../skills/workbench/wl-herdrs/SKILL.md) 直接交代自然语言任务，不以建组、入组、JSON 登记为前置条件。下文命令只适用于选择了持久台账的任务。

项目经理决定是否委派 → 登记任务包 → 查已有任务与实例 → 派单 → 执行岗位保存检查点 → 项目经理核验证据并验收。

下次会话先查看未完成任务，再读取该任务恢复摘要。摘要包括原目标、范围、已完成内容、证据、阻塞和下一步；核对项目事实后显式确认继续。恢复不是自动重放旧命令，也不是复制完整会话。

使用 `tools/scripts/role_runtime.py --help` 查询实际命令。Python 使用本机约定的 uv 管理 3.12.9。

## 最小操作

### 持久项目组：先项目组、后派单

2026-10-19 调整：交付后保留工位，不自动执行leave。先用 `preflight --project /absolute/project` 一次读取本项目未完成任务和未退组成员（只读、不访问Herdr）。已有成员时显式选择并核对实例；没有成员时join可省略member，由工具生成唯一ID，Tab仍只显示岗位名。结果不明先preflight，不重复省略ID启动。

修改命令默认返回短回执；完整记录使用show/group-show/recover，或在子命令前传 `--full`。短回执保留ID、状态、证据和下一步，不改变落盘历史。

新增项目组统一使用下列链路，旧 `dispatch` 仅兼容历史无成员任务。以下 `python` 同样指 uv 管理的 3.12.9。

```bash
python tools/scripts/role_runtime.py group-create --file /absolute/group.json
python tools/scripts/role_runtime.py preflight --project /absolute/project
python tools/scripts/role_runtime.py join requirement-a --role /absolute/ui/ROLE.md --timeout-ms 300000
python tools/scripts/role_runtime.py create --file /absolute/task.json
python tools/scripts/role_runtime.py assign task-id --member <returned-member-id> --timeout-ms 300000
python tools/scripts/role_runtime.py accept task-id --note '已核对成果'
# 到此保留工位，供观察或同项目后续任务使用。
# 只有排障、恢复或明确需要完整记录时才使用 group-show。
```

group.json 字段为 `id/project/goal/inputs`，project 是实际绝对目录，inputs 是必要资料引用数组。入组只加载身份与组资料入口，成员通过生成的 `member-ready` 命令回执；ready 前不派单。具体任务仍使用下方八字段格式，project/role 须与成员一致。

每人独占一个Tab：tab create在调用者工作区创建工位，使用no-focus；返回的根pane用于agent start，后续agent prompt/get/wait协调。不使用pane split。执行者Tab在创建时使用岗位名，例如ui、frontend、tester，不提前改名或事后批量改名。项目经理不修改自己所在Tab的名称。底层唯一Agent标识与项目组成员关联继续保留，不依靠Tab标题识别实例。

启动后第一条独立消息明确为“初始化 ui”（其他岗位同理），要求先读取身份手册，读取失败不得回执ready。完成后显示身份、实际读取文件、职责与边界，并回复“当前没有分配任务，等待项目经理派单”。项目组背景和历史摘要明确标为非任务；项目经理后续通过assign另发工作。重复岗位允许同名Tab，实际定位依靠已登记ID。

当前默认不退组。只有用户另行明确要求关闭指定成员时，才允许 `leave MEMBER --close-tab --summary '交接摘要'`。退组仍要求绑定任务全部验收、无进行中的发送，并核对Tab仅含该成员的根pane且实例身份一致。先落盘摘要再关闭Tab，确认关闭后标left；失败保留needs-reconcile。已退组成员不能复活，换新成员ID；新入组自动带入本组离场摘要和验收成果引用。超时或中断先读group-show核对，再以原命令加 `--resume --confirm-continue` 显式继续；部分启动缺少可靠身份时停下人工核对，不自动重建。

### 历史无成员任务

以下命令均在工作台根目录运行，`python` 指 uv 管理的 3.12.9：

```bash
python tools/scripts/role_runtime.py create --file /absolute/task.json
python tools/scripts/role_runtime.py list
python tools/scripts/role_runtime.py dispatch task-id --direction down --timeout-ms 300000
python tools/scripts/role_runtime.py recover task-id
python tools/scripts/role_runtime.py accept task-id --note '已核对产物和测试证据'
# 交付需返工：只登记，不自动重跑
python tools/scripts/role_runtime.py rework task-id --note '缺少约定结果' --next-action '只补齐缺失结果'
python tools/scripts/role_runtime.py dispatch task-id --resume --confirm-continue --timeout-ms 300000
```

任务包必须包含且只包含 `id/project/role/goal/non_goals/allowed_paths/inputs/acceptance`；后四项为字符串数组，路径用绝对路径。`project` 必须存在；`role` 推荐实际 ROLE.md 绝对路径；`allowed_paths` 与 `acceptance` 不可为空。`inputs` 放已批准依据及必要资料引用。CLI 不代替项目经理判断授权与范围。检查点命令带实例、会话和本轮派单标识，由程序随任务交给岗位，不需手填。

角色身份不等于启动目录：实例在目标项目目录工作。方向由项目经理先看布局选择，不自动改变用户焦点。

## 运行约束

- 只有项目经理派单；执行岗位只更新自己的检查点，协作请求返回项目经理。
- 同一项目同一岗位按需启动并复用，尚未验收的任务不被新任务覆盖；忙碌、身份不符或不可确认时不抢占。
- 执行配置仍为 Herdr → Pi → high；启动时核验就绪与实际参数。保存真实 pane、名称及会话引用，不根据界面顺序推测。
- 空闲是工具状态，submitted 是岗位声明，accepted 是项目经理核验后的任务状态，三者不能混同。
- 发送中断或结果不明先核对现有实例和证据，禁止自动重发；重派前明确下一步，避免重复副作用。
- 实例不自动关闭，尤其不控制未登记的现有实例。跨项目不复用，独立审查不复用参与实现的上下文。
- `.local` 中只存摘要及引用；项目是产物和验收证据来源。CLI 的职责检查不是权限隔离，不能证明执行岗位技术上无法委派。

## 岗位接单与交付

只读取分配岗位的手册、目标项目规则及任务包指向的必要资料。先确认任务能执行；缺少依据或权限时记录 blocked 和需要谁做什么。完成后记录 submitted、产物/证据引用、未覆盖项和下一步；不得自行验收。

验收失败由项目经理补充返工范围及恢复摘要。验收完成后，实例才可接同项目岗位的新任务；历史任务与验收记录保留。
