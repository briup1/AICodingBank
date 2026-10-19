# AGENTS.md

本仓库是个人 AI 工作台的控制入口，也是 AI Coding 兵工厂。接到请求后直接判断主意图，无需让用户选择入口：

- **使用工作台**：用户要了解、规划、开发、调试、测试、审查、部署或沉淀当前工作时，读 [WORKBENCH.md](WORKBENCH.md)；若 `WORKBENCH.local.md` 存在，再读取个人上下文和项目索引，定位目标项目并按阶段选用能力。
- **拓展工作台**：用户要新增、纠正或长期保留规则、知识、Skill、偏好、项目入口或工作流时，读 [EXTENDING.md](EXTENDING.md)，自动分类并更新唯一事实来源。
- **两者兼有**：先完成并验证当前工作，再按拓展入口沉淀已经验证的信息。

能力控制面：自研 Skill 在 tools/skills/，第三方只登记在 skills-lock.json；目录刷新用 `python3 install.py --catalog-only`（不联网不安装），详细规范见 [README.md](README.md) 与 [EXTENDING.md](EXTENDING.md)。维护红线：

1. Skill 正文单份：自研在 tools/skills，第三方缓存由 vendor 管理；历史迁入快照已按 2026-10-19 评估收口，不再复制。宿主加载位置由 install.py 直连 canonical；旧兼容入口已于 2026-10-18 按批准退役，重新引入或舍弃须经确认。
2. 新增第三方 skill 只改 `skills-lock.json`，禁止把文件拷进仓库；登记时必须当场写 capability / boundary / tags 三行人话。
3. 新增自研 Skill 放 tools/skills/<分类>/ 并在 skills.yaml 登记（同样带三行人话）。
4. `verified` 为空的 skill 不会被安装；验证通过才填日期。
5. `CATALOG.md` 由 install.py 自动生成，不要手改。
6. 当前机器临时停用已验证 Skill 时，写入 Git 忽略的 `skills.local.yaml`，不要篡改共享验证状态。
7. prompt/spec 模板随对应主题/Skill 包维护；最佳实践记录按 [best_practices/STANDARD.md](best_practices/STANDARD.md)构建，不把历史模板当已验证案例。
