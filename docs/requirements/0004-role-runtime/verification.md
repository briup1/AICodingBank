# 岗位运行验证

## 项目组与独立Tab增量验收

2026-10-19 完成：负责人重新运行47项运行测试（含原27项），全部通过。

真实项目组 group-smoke-20261019：

| 成员 | 独立Tab | 实际交付 | 最终状态 |
| --- | --- | --- | --- |
| ui-1 | wM:t9 | group-ui-spec.md 五项页面约定 | accepted，left，Tab关闭 |
| frontend-1 | wM:tA | group-page.html 按约定实现 | accepted，left，Tab关闭 |
| tester-1 | wM:tB | group-test-result.md 静态核对5/5 | accepted，left，Tab关闭 |
| ui-2 | wM:tC | 新成员入组带历史摘要，读取岗位并回执ready | 无新任务，left，Tab关闭 |

各Tab均通过tab create创建，执行者通过agent start启动Pi/high，派单走agent prompt；不是小pane分屏。三名初始成员先分别ready，再按UI→前端→测试依赖派单。负责人回读约定、HTML和报告后验收。关闭使用本次leave入口完成，且查列表确认Tab和pane已消失，未关闭其他会话。

新成员ui-2使用新的Pi session，入组提示包含离场摘要和验收成果引用；真实验证到入组ready，未再分配业务续作。原无成员任务继续保留在同一状态文件。

程序隔离测试覆盖未ready禁止派单、重复join不创建Tab、跨组隔离、两轮派单、返工、发送不明、并发、旧数据、身份不符/附加pane拒绝关闭、关闭失败及确认恢复。未在真实用户会话上注入故障，未做视觉验收或整机重启测试。

下面为前一轮基线证据；其中“其他岗位尚未验证”由本节UI/前端/测试的增量结果更新。

状态：最小运行验收完成（2026-10-19）。

本轮实现岗位负责确定性运行入口与隔离测试；负责人负责真实 Herdr 的启动、交接、复用、跨进程读取和证据核验。不宣称独立 Review 已完成。

执行岗位通过 Herdr 新建 `role-runtime-dev`，启动返回的 argv 为 `pi --thinking high`，interactive_ready=true。该实例只负责指定两个代码文件，无其他写入授权。

## 结果

- 负责人运行 Python 3.12.9 的聚焦 unittest：27/27 通过。包括跨进程读取、模拟 Herdr 身份/忙碌检查、发送不明、重派确认、返工和并发写入。
- 真实任务 runtime-smoke-1：创建 Pi/high 实例，执行岗位读取 delegation.md，写入 ready/submitted，答案 Pi/high 与证据一致，负责人验收为 accepted。
- 真实任务 runtime-smoke-2：复用相同 name、pane 与 Pi session，无新建实例；提交“无自动备选通道”，负责人核对后验收。
- 负责人在独立命令进程执行 recover：读回原任务包、最近检查点、证据及验收说明，没有触发重新执行。
- 本机证据：`.local/records/role-runtime/state.json`；包含两条验收任务和真实事件。不提交运行数据或完整会话。

真实验证只覆盖调研岗位的只读任务；其他专业岗位尚未逐一验证，仍保留草稿。丢失实例、并发、超时等故障使用隔离模拟，未关闭现有用户实例注入故障。没有验证整机重启、权限隔离、无人值守经营或完整 Pi 对话重放。需求 HTML 阅读页未生成，未做视觉验收；不影响 CLI 运行结果。
