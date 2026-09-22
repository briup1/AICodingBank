# wl-git-flow 用户级 HTML 看板实施计划

## 目标与非目标

实现已批准的多项目 Git 事实驱动 HTML 看板；不接外部平台、不提供 HTML 写操作、不修改业务仓库。

## 影响与文件图

### 工作包 A：状态与扫描引擎

- 新增 `skills/wl-git-flow/scripts/dashboard.py`
- 新增 `tests/test_wl_git_requirement_dashboard.py`
- 数据契约：XDG config/state/data JSON；Git 扫描默认只读、无 fetch。

### 工作包 B：HTML 视图（可并行）

- 新增 `skills/wl-git-flow/assets/dashboard-template.html`
- 输入契约：`{{DATA_JSON}}` 与 `{{GENERATED_AT}}`
- 输出契约：单文件、无 CDN、Kanban/表格、筛选、归档、响应式与键盘可达。

### 工作包 C：命令与生命周期集成

- 修改 `skills/wl-git-flow/scripts/wl-git-flow.sh`
- 修改 `skills/wl-git-flow/SKILL.md`
- 新增 `skills/wl-git-flow/references/dashboard-model.md`
- 修改 `skills/wl-git-flow/agents/openai.yaml`

### 工作包 D：需求文档与验证

- 新增 `docs/requirements/0002-wl-git-requirement-dashboard/*`
- 更新 `tests/test_wl_git_requirement_flow.py`
- 最终运行 Skill 校验、Bash 语法、聚焦 pytest、一级 tests 回归和 Compass 只读扫描。

## 依赖顺序

```text
A 数据契约 ─────┐
                 ├─> C 命令集成 ─> D 全局验收
B HTML 视图 ────┘
```

## TDD 任务

1. **配置与登记**：先写临时 XDG 目录下 register/幂等/版本错误测试，再实现原子 JSON 存储。
2. **Git 扫描**：先写多仓库、dirty、ahead、detached、临时路径和祖先关系测试，再实现 scanner。
3. **生命周期**：先写 Dev passed SHA 过期、merged master、online、7 天归档和重新打开测试，再实现 reducer。
4. **HTML**：先写输出自包含、数据安全嵌入、关键控件和空状态测试，再接模板。
5. **命令集成**：先写 workflow 命令后 dashboard state 更新测试，再增加非阻断 refresh hook。
6. **E2E**：隔离 bare origin 完成 start→Dev→Beta→master→online→archive；用 Compass 执行无 fetch 只读刷新并核对 Git 状态不变。

## 完成证据

- `quick_validate.py skills/wl-git-flow`
- `bash -n skills/wl-git-flow/scripts/wl-git-flow.sh`
- `pytest -q tests/test_wl_git_requirement_dashboard.py tests/test_wl_git_requirement_flow.py tests/test_install.py`
- `pytest -q tests`，既有无关失败单独说明
- 浏览器打开生成 HTML，无控制台错误；桌面和窄屏可读
- Compass 扫描前后 `git status --short --branch` 一致
