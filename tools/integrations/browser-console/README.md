# 自动化浏览器本机入口

这是一个很薄的 macOS 启动入口：复用已安装的 `agent-browser` Dashboard，不重新实现浏览器驱动。

## 使用

安装本机入口：

```bash
node /Users/ziyun/workdir/self_project/AICodingBank/tools/integrations/browser-console/install.mjs
```

安装后：

- 在 Spotlight 搜索 **自动化浏览器**，或从 `/Users/ziyun/Applications/自动化浏览器.app` 打开。
- 应用启动后自动检查并复用本机 Dashboard，地址为 `http://localhost:4848`（0.27.0 内置 Chat 使用这个固定来源；不要换成其他端口或主机名）。
- 重复打开不会启动第二个 Dashboard。
- 菜单中的“查看运行状态”只报告控制台状态和会话数量；会话数量不等于正在执行的任务数。
- “停止控制台服务”只停止管理面板，不关闭浏览器会话。
- 具体会话需要在 Dashboard 中按名称关闭；正常关闭会核验对应 `agent-browser` 进程树。

## 受管任务入口

需要“任务结束后自动关闭”的脚本可以调用：

```bash
node /Users/ziyun/workdir/self_project/AICodingBank/tools/integrations/browser-console/console.mjs \
  task yuxi-beta-check-001 -- agent-browser --session yuxi-beta-check-001 open https://example.com
```

约束：

- 会话名必须使用小写字母、数字、`-` 或 `_`，长度不超过 80；不能使用 `dashboard`。
- 同一任务名不能并发占用。
- 子命令成功、失败或收到终止信号后，入口都会尝试关闭指定会话；关闭未完成时返回失败，不伪造成功。
- `agent-browser` daemon 空闲回收默认试行 30 分钟，通过 `AGENT_BROWSER_IDLE_TIMEOUT_MS=1800000` 注入。
- 登录 profile 不会被删除。需要人工继续登录的 HGJ 会话仍按 `/Users/ziyun/.agents/skills/hgj-session/SKILL.md` 的交接规则处理，不强制自动关闭。

## 控制命令

```bash
node .../console.mjs open
node .../console.mjs status
node .../console.mjs stop
node .../console.mjs close <session>
```

这些命令只作用于本入口管理的 `agent-browser` Dashboard 和明确指定的会话；不使用全局 `pkill Chrome`，不影响普通 Chrome。

## 验证

单元测试：

```bash
node --test /Users/ziyun/workdir/self_project/AICodingBank/tools/integrations/browser-console/console.test.mjs
```

真实本地烟测使用临时 profile 和 `data:` 页面，不访问业务网站、不使用登录态：

```bash
node /Users/ziyun/workdir/self_project/AICodingBank/tools/integrations/browser-console/smoke.mjs
```

烟测会验证：重复启动复用、控制台与会话分离、A/B 会话隔离、空闲回收、失败任务收尾。截图通过 `CONSOLE_SCREENSHOT=/absolute/path.png` 可选开启。

## 边界

当前版本不承诺自动判断业务任务是否完成，也不显示业务 owner、CPU 汇总或所有调用方的统一强制接入。Dashboard 是本机回环服务，不对外暴露；浏览器中展示的页面、Cookie、网络和存储信息仍按敏感信息处理。
