# wl-git-requirement-flow 轻量实时刷新实施计划

## 目标

为现有静态需求开发看板增加 localhost 前台服务、真实刷新按钮和默认关闭的自动刷新，同时保留静态降级；不增加 Agent 启动、Git 写接口、常驻服务或外部依赖。

## 影响评估

- **模块**：`dashboard.py` 增加 HTTP 层但复用 scanner/state/renderer；模板增加 live/static 双模式。
- **数据模型**：config/state schema 不变；会话 Token、端口、自动刷新选择不持久化到业务状态。
- **接口**：新增本机 HTTP 只读接口和 `dashboard serve` CLI；现有 CLI 兼容。
- **安全**：新增 localhost 攻击面，需要 Token、Origin、Host、方法和路由白名单。
- **性能**：刷新串行化；自动刷新默认关闭；隐藏页面暂停。
- **回滚**：删除 serve 和 live UI 即可，静态 HTML 继续可用。

## 工作包 A：本地服务后端

**写入范围**：

- `skills/wl-git-requirement-flow/scripts/dashboard.py`
- `skills/wl-git-requirement-flow/scripts/wl-git-requirement-flow.sh`
- `tests/test_wl_git_requirement_dashboard_server.py`

### A1. RED：HTTP 安全契约

新增失败测试：

- 服务实际绑定 `127.0.0.1` 和随机端口；
- `GET /api/refresh` 返回 405；
- 缺 Token、错误 Token、错误 Origin 返回 403；
- 未知路由返回 404；
- 响应无 CORS 且包含安全头；
- 服务没有 Agent/Git 写路由。

命令：

```bash
uv run --no-project --python 3.12.9 --with pytest pytest -q tests/test_wl_git_requirement_dashboard_server.py
```

预期 RED：`serve_dashboard`、handler 和 CLI 尚不存在。

### A2. GREEN：最小 HTTP 服务

在 `dashboard.py` 增加：

- `DashboardServerState`：Token、origin、refresh lock、latest data；
- `DashboardRequestHandler`：`/`、`/api/state`、`/api/refresh`、`/api/health`；
- `serve_dashboard(paths, port, open_browser)`；
- `dashboard serve --port 0 --open` CLI；
- JSON 错误映射和安全响应头；
- `KeyboardInterrupt`/`server_close()` 清理。

Shell 只更新 usage；已有 `dashboard` 透传不需要新路由逻辑。

### A3. RED/GREEN：刷新行为和并发

测试：

- 有效 POST 调用一次 scanner 并返回最新 JSON；
- 两个并发刷新只有一个执行，另一个返回 409；
- scanner 失败保留上次成功数据并返回结构化错误；
- 服务停止后端口不可连接；
- `--open` 只打开 localhost URL。

### A4. REFACTOR

- HTTP 层不复制 lifecycle/scanner 逻辑；
- 线程共享状态只通过锁修改；
- 日志不输出 Token；
- 所有异常不向客户端泄露 traceback、凭证或完整环境。

## 工作包 B：实时/静态双模式 UI

**依赖**：A 的接口契约冻结；可与 A 实现并行。

**写入范围**：

- `skills/wl-git-requirement-flow/assets/dashboard-template.html`
- `tests/test_wl_git_requirement_dashboard_ui.py`

### B1. RED：静态结构测试

测试模板存在：

- `刷新状态` 按钮；
- live/static 模式指示；
- 自动刷新关闭/15/30/60 选项；
- loading、success、error 状态区域；
- 无 Agent、merge、push、delete 操作按钮；
- 无外部 URL、`innerHTML` 或任意命令执行。

### B2. GREEN：数据热更新

重构模板数据入口：

- `source` 和 `requirements` 改为可替换状态；
- `applyDashboardData(data)` 只替换业务数据并重新渲染；
- `refreshLiveData()` POST `/api/refresh`；
- static 模式按钮只执行 `location.reload()`；
- live 模式显示最后成功刷新时间和耗时。

### B3. UI 状态保持

在刷新前捕获并恢复：

- visibility tab；
- Kanban/table；
- search/project/status/anomaly filters；
- scroll position；
- 展开的 requirement/branch `<details>`；
- 自动刷新选项。

自动刷新使用串行 `setTimeout`，页面隐藏或 refresh 进行中时跳过。

### B4. 浏览器验证

使用真实 Chrome 验证：

- desktop 1440×1000；
- mobile 430×932；
- 点击刷新后数据变化且筛选不丢；
- 错误信息可见且旧卡片仍保留；
- static file 模式提示正确；
- 控制台无 JavaScript 错误。

## 工作包 C：集成、文档与验收

**写入范围**：

- `skills/wl-git-requirement-flow/SKILL.md`
- `skills/wl-git-requirement-flow/references/dashboard-model.md`
- `skills/wl-git-requirement-flow/agents/openai.yaml`
- `docs/requirements/0003-wl-git-requirement-live-refresh/*`
- 本计划文档

### C1. 文档

说明：

- `serve --open` 是推荐实时入口；
- `open` 是静态快照；
- 自动刷新默认关闭；
- `Ctrl+C` 停止；
- 页面不能启动 Agent 或执行 Git 写操作；
- localhost/Token/Origin 安全边界。

### C2. 集成回归

```bash
uv run --no-project --python 3.12.9 --with pytest --with pyyaml pytest -q \
  tests/test_wl_git_requirement_dashboard_server.py \
  tests/test_wl_git_requirement_dashboard_ui.py \
  tests/test_wl_git_requirement_dashboard.py \
  tests/test_wl_git_requirement_flow.py \
  tests/test_install.py
```

以及：

```bash
bash -n skills/wl-git-requirement-flow/scripts/wl-git-requirement-flow.sh
uv run --no-project --python 3.12.9 python -m py_compile skills/wl-git-requirement-flow/scripts/dashboard.py
uv run --no-project --python 3.12.9 --with pyyaml python \
  /Users/ziyun/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/wl-git-requirement-flow
git diff --check
```

### C3. 真实只读验收

- 启动 `dashboard serve --port 0 --open`；
- 点击刷新 Compass；
- 对比扫描前后 Compass status、refs、index hash/mtime；
- 验证服务仅监听 127.0.0.1；
- 验证 Ctrl+C 后端口关闭；
- 验证静态 HTML 仍可打开。

## 任务依赖与并行

```text
A. HTTP 服务契约与后端 ─────┐
                              ├─> C. 集成、浏览器和安全验收
B. live/static UI ───────────┘
```

A、B 在接口字段冻结后可并行，写集合不重叠；C 必须串行集成。

## 完成证据

- 新旧聚焦测试全部通过；
- 浏览器点击真实刷新成功；
- 筛选和展开状态不丢失；
- 无 Token/错误 Origin 无法刷新；
- Compass Git 状态、refs 和 index 无变化；
- 端口仅监听 localhost，Ctrl+C 后关闭；
- 静态模式仍可用；
- 未出现 Agent 启动或 Git 写能力。
