# 0003 开发进度

更新：2026-09-21

| 工作包 | 状态 | 产物 | 验收 |
| --- | --- | --- | --- |
| A. localhost 服务后端 | 完成 | `dashboard.py`、Shell、server tests | 服务安全、真实 API、端口释放与跨进程锁 |
| B. live/static 页面 | 完成 | HTML template、UI tests | 双模式、按钮、自动刷新、状态保持、移动端 |
| C. 文档与集成验收 | 完成 | Skill/docs/catalog | 49 项联合测试、真实 Chrome 点击刷新 |

## 交付证据

- 服务真实地址使用 `127.0.0.1` 随机端口，终端明确显示 URL、安全边界和 `Ctrl+C` 停止方法。
- config/state 全部读改写使用 `fcntl` 跨进程文件锁；并发回归验证实时 refresh 不会覆盖 CLI 新写入的 Dev 状态。
- 无 Token 的 `POST /api/refresh` 返回 403；带正确 Token 和同源 Origin 的刷新成功并返回 3 个需求。
- Chrome 实际点击“刷新状态”成功，耗时约 464ms；生成时间变化，搜索和关联分支展开状态保持。
- Desktop 1440×1000 和 mobile 430×932 均真实渲染；移动端刷新控件改为纵向排列。
- 静态模板保留 `window.__WL_DASHBOARD_LIVE__` 旧对象兼容；服务使用安全 JSON script 注入。
- 自动刷新默认关闭，仅有关闭/15/30/60 秒；隐藏页面和刷新进行中不会重复扫描。
- Ctrl+C 后监听端口关闭。
- 看板没有 Agent、terminal、merge、push、delete、publish API 或按钮。
- Compass 扫描只读；业务仓库现有未提交修改属于其他任务，本次未触碰。
- 一级 `tests/` 为 63 passed、1 个既有无关 harness-pack 失败。
