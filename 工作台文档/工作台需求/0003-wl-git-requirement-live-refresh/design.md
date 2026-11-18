---
id: 0003
slug: wl-git-requirement-live-refresh
status: approved
created: 2026-09-21
requirement: requirement.md
chosen: A
---

# 方案设计：需求开发看板轻量实时刷新

## 1. 方案选择

采用 **A：Python 标准库前台 localhost 服务 + JSON 刷新接口 + 静态降级**。

| 方案 | 结论 | 原因 |
| --- | --- | --- |
| A. 前台 localhost 服务 | 采用 | 真正一键扫描，保留页面状态，无常驻进程和额外依赖 |
| B. 静态 HTML 周期 reload | 拒绝 | 不能保证重新扫描 Git，且会打断筛选和阅读 |
| C. 后台常驻服务 | 暂缓 | 对个人看板过重，需要 PID、升级和异常恢复机制 |
| D. 浏览器直接调用 shell | 拒绝 | 浏览器安全模型不允许，扩展/自定义协议过度复杂 |

## 2. 运行结构

```text
浏览器 http://127.0.0.1:<随机端口>/
  ├─ GET  /                  实时模式 HTML
  ├─ GET  /api/state         返回当前内存快照
  ├─ POST /api/refresh       执行只读 Git 扫描并返回新快照
  └─ GET  /api/health        服务健康和生成时间
                 │
                 ▼
ThreadingHTTPServer（前台）
                 │
                 ▼
现有 refresh_dashboard()
  ├─ 已登记项目 Git 只读扫描
  ├─ XDG state/config 更新
  └─ 静态 dashboard.html 同步更新
```

服务不新增业务状态模型，复用 0002 的 config/state/scanner/renderer。

## 3. HTTP 契约

### GET `/`

- 返回由现有模板生成的 HTML。
- 额外注入仅存在于内存中的 live 配置：`mode=live`、API 路径、会话 Token、刷新选项。服务使用不可执行的 JSON script 注入；页面同时保留 `window.__WL_DASHBOARD_LIVE__` 旧对象入口兼容。
- 设置 `Cache-Control: no-store` 和安全响应头。

### GET `/api/state`

- 返回最近一次成功生成的看板 JSON。
- 不触发扫描。
- 仅同源页面和正确 Token 可访问。

### POST `/api/refresh`

- Body 为空，限制请求体大小。
- 验证随机 Token、Origin、Host 和方法。
- 获取单实例刷新锁；已有扫描进行时返回 `409`。
- 所有 config/state 读改写再使用用户级 `fcntl` 跨进程锁，避免实时刷新覆盖并发 CLI 生命周期事件。
- 调用现有 `refresh_dashboard()`。
- 成功返回 `{ ok, data, durationMs }`；失败返回结构化错误，不泄露 traceback。

### GET `/api/health`

- 返回 `{ ok, mode, generatedAt, refreshing }`，不扫描 Git。

其他路径返回 404；refresh 的 GET 返回 405。

## 4. 安全边界

- 服务端构造地址，host 固定为 `127.0.0.1`，CLI 不提供 `--host`。
- 端口默认 `0` 由操作系统分配，可用 `--port` 指定本机端口。
- 每次启动使用 `secrets.token_urlsafe()` 生成 Token，只存在内存和本次 HTML 响应。
- API 要求 `X-WL-Dashboard-Token`，同时验证 `Origin` 等于本服务 origin。
- 不发送 `Access-Control-Allow-Origin`。
- 响应头至少包含 `Content-Security-Policy`、`X-Content-Type-Options: nosniff`、`Referrer-Policy: no-referrer`、`Cache-Control: no-store`。
- 服务路由白名单中不存在 Git 写、Agent、shell 或任意命令执行接口。
- HTTP 线程锁只控制重复刷新；用户级文件锁统一协调服务进程与其他 CLI 进程。

## 5. 页面状态模型

```text
static
  └─ 按钮：重新加载快照

live-idle
  └─ 按钮：刷新状态

live-refreshing
  └─ 按钮禁用，显示正在扫描

live-success
  └─ 原地替换数据并重新 render

live-error
  └─ 保留旧数据，显示错误和重试按钮
```

页面筛选和 UI 状态与看板数据分离。刷新只替换 `source/requirements/projects/summary/errors`，不重建筛选状态对象。

自动刷新：

- 默认 `off`；选项 15/30/60 秒。
- 使用 `setTimeout`，上次刷新结束后再安排下一次。
- `document.hidden === true` 时跳过。
- 选择保存在 `sessionStorage`，不写入 config/state。

## 6. CLI 契约

```bash
wl-git-flow.sh dashboard serve [--port 0] [--open]
```

- 默认前台运行并打印 URL、项目数、安全边界和停止方法。
- `--open` 在服务就绪后用默认浏览器打开。
- `Ctrl+C` 调用 `shutdown()` 并关闭 socket。
- `dashboard open` 继续打开静态模式，不改变原语义。
- `dashboard watch` 保留兼容，但文档将 `serve --open` 标为推荐交互入口。

## 7. 兼容和回滚

- 静态模板仍可由 `refresh_dashboard()` 生成并通过 `file://` 打开。
- live 配置缺失时，模板自动进入 static 模式。
- 删除 serve 路由和页面 live 逻辑即可回滚，不影响扫描器、状态文件或 Git 流程。
- 服务异常退出不损坏 config/state；下一次 static refresh 或 serve 可恢复。
