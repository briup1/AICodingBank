# OpenCLI 任务生命周期

## 适用范围

只管理新登记的 `opencli browser` 任务，不改 OpenCLI npm 包或 Chrome 扩展，不接管站点适配器、历史会话或 agent-browser。用户本轮选择只更新 Skill 和执行脚本，不启用用户级 Pi 扩展。

```text
旧：直接 opencli → 页面操作 → 报告，调用方自行清理
新：begin 登记随机会话 → exec 原生动作 → 保存业务结果
                                           ├→ finish 释放 + 原生列表回读
                                           └→ hold 人工交接 → resume → finish
```

- 自建页面：返回 `released` / `releaseConfirmed=true` 仅表示原生租约释放应答已确认且该会话列表为空；`pageCleanup=not-independently-verified` 明确表示物理关页/清空未独立验证。原生释放可能吞物理关页异常，也可能正常保留空白复用容器。
- 借用页面：原生释放只解绑，不关闭用户页面。
- 共享 daemon：保留。`/status.pending=0` 只能证明此刻无命令，不能证明其他调用方没有保留页面或下一步动作，因此不据此自动 `daemon stop`。
- 当前不提供“按名称批量清理”“按内存杀进程”“定时关闭全部”。空白容器彻底退出与跨宿主全局空闲停服未实现，不能宣称解决。

## 交互执行

```bash
LIFECYCLE=/Users/ziyun/workdir/self_project/AICodingBank/tools/skills/shared/wl-web-auto/scripts/lifecycle.mjs
node "$LIFECYCLE" begin example-check
# 复制返回的 id，下列 id 为占位符，不是任务名称。
node "$LIFECYCLE" exec <id> -- open https://example.com
node "$LIFECYCLE" exec <id> -- state
node "$LIFECYCLE" finish <id>
node "$LIFECYCLE" status <id>
```

多个连接的 Chrome profile：`begin example-check owned <contextId>`；contextId 取 `opencli daemon status` / `opencli profile list` 的实际值。begin 不提供账号、Token 或凭证。

借用用户当前页面：明确授权后 `begin example-check bound <contextId>`，随后 `exec <id> -- bind`。绑定操作选择当前页面，操作前人工确认焦点；完成执行 finish。不要把“测试页面”理解为借用任意用户页面的授权。

业务命令仍必须按原有授权执行。exec 不自动重试业务命令；失败码原样返回。截图显式写到本次证据目录，命令参数和业务响应不写生命周期账本。`task`、`owner`、交接原因不得包含客户信息或凭证。

## 整任务脚本

子脚本示例（shell 应使用项目明确支持的解释器）：

```bash
#!/bin/bash
set -euo pipefail
LIFECYCLE=/Users/ziyun/workdir/self_project/AICodingBank/tools/skills/shared/wl-web-auto/scripts/lifecycle.mjs
node "$LIFECYCLE" exec "$OPENCLI_TASK_ID" -- open https://example.com
node "$LIFECYCLE" exec "$OPENCLI_TASK_ID" -- state
```

执行：

```bash
node "$LIFECYCLE" run example-check -- bash /absolute/path/task.sh
```

run 在子程序退出后才 finish，不在每条命令后关闭。子脚本必须通过 exec 使用同一个登记 id，不使用原生 browser 调用绕开路由检查。它不是 shell 沙箱，也不追踪后台脱离的子进程。

- 子任务失败保留原退出码，收尾失败使原成功任务转失败。
- SIGINT/SIGTERM 转给直接子进程并等待其退出后收尾；若子进程不退出，不假定业务已停止，不提前关页。
- SIGKILL、断电、调用方硬超时无法执行 finally。自建 session 原生约10分钟空闲释放只是兜底；绑定用户页面没有该回收。恢复时先 status、核对在途请求/任务锁与人工占用，确认后显式 finish。不要自动删 `.lock` 或批量扫描后关闭。
- hold 后 run 的 finish 会保留交接任务。自建 session 的原生超时仍有效，不承诺页面永久保留；需要长时间人工操作应另外确认借用页面流程。

## 版本与可信边界

已核对 OpenCLI 1.8.8、Chrome 扩展 1.0.24。脚本通过本机回环 `127.0.0.1:19825` 原生 Bridge `/command` 执行 close-window 与 tabs/list，不添加浏览器驱动、不抓取用户数据；清理不调用会自动启动 daemon 的客户端。版本变化必须先重新核对 `/status`、路由、释放及列表语义，不自动升级工具或放开门禁。

释放回读只证明原生 session 已无可列出的页面，不独立证明 Chrome UI 的调试横幅已消失、所有子进程已退出。原生扩展 `releaseLease` 可能保留最后一个 about:blank 标签组；这在结果中明确报告。

## 本轮真实验证（2026-10-20）

本机原生1.8.8 / 扩展1.0.24：临时HTTP无业务数据夹具创建A/B两个随机会话，原生返回不同page；finish A租约回读为空，B仍可读取标题；随后finish B租约回读为空。任务id：`f79a155e-d8a1-4d61-81e0-4beb7fbdc551`、`9dfa9b7a-ee2b-45c4-8e5b-1e3e179a465c`。夹具服务已关闭，账本保留；未触碰历史会话，未停止共享daemon。未实拍调试横幅、未独立确认物理关页；真实借用用户页面、强杀和空闲回收未测试。

## 验证

```bash
node --test /Users/ziyun/workdir/self_project/AICodingBank/tools/skills/shared/wl-web-auto/scripts/lifecycle*.test.mjs
node /Users/ziyun/workdir/self_project/AICodingBank/tools/skills/shared/wl-web-auto/scripts/self-test.mjs
```

自动夹具覆盖随机归属、定向释放、空列表确认、错误不伪报成功、借用页面、hold/resume、路由拦截、任务锁、失败退出和终止信号。原生浏览器验证使用新建命名任务与本地无业务数据页面；不检查/关闭历史任务，不以 mock 结果冒充真实页面验证。
