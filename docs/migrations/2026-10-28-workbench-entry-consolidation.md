# 工作台入口收敛

日期：2026-10-28

## 决定

- 删除全部以 `WORKBENCH` 开头的文件。
- `AGENTS.md` 作为工作台唯一入口，只提供资源地址。
- 不在入口描述工作台定位、用户身份、项目经理、角色职责或执行流程。
- 保留岗位、项目经理和执行配置目录，仅在入口列地址。
- 用户级偏好沿用 `/Users/ziyun/.agents/AGENTS.md`；工作台只保留 `personal/projects.local.md` 项目地址索引。

## 结果

```text
Agent 接到任务
  -> 读取 AGENTS.md
  -> 选择需要的资源地址
  -> 只读取命中的资源
```

删除：`WORKBENCH.md`、`WORKBENCH.local.md`、`WORKBENCH.local.example.md`。

保留：岗位手册、Skill、工具接入、执行配置、历史研究和迁移记录；它们不因入口收敛而自动加载。

## 验证

- 仓库内不再存在 `WORKBENCH*` 文件。
- `personal/` 只保留 Git 忽略的 `projects.local.md`；不重复维护用户画像或偏好。
- 入口和相关文档引用已改为 `AGENTS.md` 或 `personal/projects.local.md`。
- 相关聚焦验证：33 passed，17 subtests passed；排除两项已确认在 HEAD 中也存在的旧文案断言不一致（Herdr 默认策略、Ego 并发限制），未为本次任务修改这些行为。
- `git diff --check` 已通过。
