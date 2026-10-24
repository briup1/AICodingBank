# 工具接入

保存 CLI、MCP、外部工具的用途、适用边界、安装前提、真实配置位置指针、只读检查方式与验证状态。不复制真实配置值、Token、Cookie、私钥或连接密钥。

现有接入说明若属于某个 Skill，就引用原说明；跨多个能力共用且有实际需要时才迁入这里。本轮没有安装、连接、启动或更改任何外部工具。

## Pi 提示词命令

- [个人提交并推送 /wl-ship](pi-wl-ship/README.md)：明确调用即本次选定改动的临时附件清理、提交和推送授权，需求分析、正式方案和测试用例可提交推送，按目的分批，不自动合并或发布；唯一正文与接入方式见该入口。

## 共用测试接入

- [Playwright 测试登录](playwright-auth/README.md)：固定登录准备、恢复检查与原生 Test runner/fixture 接入；首版限 HGJ client / Beta。实现与验收状态以该入口及需求 0006 为准，不把登录态文件存在当作登录有效，也不替代具体用例的业务操作授权。

## 已迁入的历史说明

2026-10-18 从 `claudecode_guide/` 归位，均为历史材料，未在本轮验证：

- [插件使用与开发指南.md](插件使用与开发指南.md) — Claude Code 插件的使用与开发方法；插件本体副本已于 2026-10-19 评估后清除，需要时从官方市场重装
- [插件收录登记.md](插件收录登记.md) — 历史收录插件索引，目录路径已更新到快照位置
- [subagent-配置指南.md](subagent-配置指南.md) — Claude Code subagent 配置方法
- [examples/](examples) — Claude Code / opencode 的历史示例配置（settings、commands、claudeignore 等）
