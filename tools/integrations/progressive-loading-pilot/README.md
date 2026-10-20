# 渐进加载隔离原型

状态：2026-10-19，六个本地契约测试通过；尚未进行真实 OpenCode 模型会话验收，未安装到任何宿主。

## 可复现

在仓库根目录运行：

```sh
node --test tools/integrations/progressive-loading-pilot/pilot.test.mjs
```

Node v22.22.0，6 passed / 0 failed。无第三方依赖、无模型请求、无 Python 执行。测试使用内存规则正文，工具调用只模拟，不执行实际编辑或 shell。

plugin.mjs 导出工厂供隔离夹具调用，不是可直接安装的 Plugin 默认入口。依据本机 @opencode-ai/plugin/dist/index.d.ts 的 tool.execute.before 与 experimental.chat.system.transform 参数形状实现。

## 已验证链路

模拟调用命中 → 抛错阻止 → 模拟下一次 system transform 读取并插入所需正文 → 模拟重试放行。

验证了 Markdown/echo 排除、Python 编辑与直接执行区分、apply_patch 路径、并行首次调用阻止、会话隔离与后续请求重新插入。

## 未验证与停止门槛

- prepared-for-model 只说明回调准备了正文，不能证明模型真正收到或重新决策。provider 失败、宿主事件顺序、压缩恢复和并发模型请求须真实会话验证。
- 命令匹配只支持直接 python/python3/uv 子命令，不支持绝对路径、env 前缀、多段 shell、别名、脚本封装；不作为生产执行控制。
- 当前规则 ID 含版本，原型不支持运行中热更新或跨进程状态恢复。
- 新建 CLI 模型会话属于启动另一个 Agent；本机约束要求通过 Herdr 启动 Pi 并确认 high，不能自行运行 OpenCode 子会话替代。下一步真实 OpenCode 验收需用户明确允许“隔离宿主测试进程”作为该约束的例外，或用户亲自启动测试会话。未经此确认不启动。
- 当前会话尚未完成隔离配置，也未验证如何排除全局指令/外部 Skills 的干扰。不得将本原型标记为上线或跨宿主可用。

详见 ../../../docs/research/2026-10-19-progressive-loading-host-audit.md。
