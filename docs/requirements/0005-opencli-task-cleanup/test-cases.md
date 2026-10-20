# OpenCLI 收尾用例 v1

公共边界：仅本地夹具，不操作历史会话、普通Chrome数据或凭证；不得杀Chrome/停共享daemon。覆盖R01–R05、D01–D04。

| 用例 | 前提与操作 | 预期 | 证据/状态 |
|---|---|---|---|
| TC01 随机隔离 | 同一task slug登记两次 | session不同，不接管历史会话 | lifecycle.test.mjs，通过 |
| TC02 定向结束 | A/B各有页面，结束A | A租约为空；B不受影响；不停止共享服务 | mock及本地真实A/B，通过 |
| TC03 错误回读 | 模拟关闭后仍有session页或Bridge离线 | cleanup-failed，releaseConfirmed=false | mock，通过 |
| TC04 人工接手 | hold B，调用finish；再resume并finish | 首次保留held，恢复后释放；不承诺取消原生超时 | mock，通过 |
| TC05 借用页面 | bound登记，先state，再bind，最后finish；另模拟绑定失败/异常、绑定前hold/resume与租约消失 | 未确认绑定/租约消失拒绝普通动作，不盲重绑定；确认成功后结束仅解绑 | mock，通过；真实借用未执行 |
| TC06 路由边界 | owned bind、tab close别页、--tab/--profile覆盖、非法id | 发起浏览器动作前拒绝 | mock，通过 |
| TC07 业务失败 | exec返回7；随后finish | 释放后仍记录原失败码7 | mock，通过 |
| TC08 并发/在途 | 同id操作和结束重叠；或Bridge pending/unknown变化 | 拒绝冲突，不提前释放 | mock，通过 |
| TC09 版本/profile | 多profile未选，或daemon版本变化 | 停止，不自动替换共享服务 | mock，通过 |
| TC10 整任务 | 子任务0/7退出、启动失败、SIGTERM；另模拟清理失败 | finally收尾，保留失败码/143，清理失败不返回成功 | lifecycle-run.test.mjs，通过 |
| TC11 原生限制 | 查看finish返回 | pageCleanup未独立验证；原生空白容器可能保留、共享服务保留 | 返回字段及真实A/B，通过；横幅实际状态未验证 |

直接回归：原有run目录、截图模式、并发上限脚本5项通过。真实SIGTERM进程树、SIGKILL、空闲到期、Chrome物理关页/横幅及共享服务自动退出未覆盖，不计通过。
