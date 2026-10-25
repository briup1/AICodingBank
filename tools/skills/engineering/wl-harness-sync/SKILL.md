---
name: wl-harness-sync
description: 根据本次需求、明确 diff 或已确认决策，增量维护规则与 Wiki，并补齐本次实现使初始化暂缺项失效的资料。与 wl-harness-setup 共用内容可接手标准，也可接管既有文档；不重新初始化、不全库审计。
---

# 维护项目资料

明确变化 → 定位正文与暂缺项 → 最小修订 → 核对受影响任务。不依赖运行过setup，也不自动调用setup。

先读[统一契约](../harness-pack/references/shared-protocol.md)及[内容标准](../harness-pack/references/content-standard.md)的“先确定调查范围”和“内容可接手验收”；只补读受影响的内容段落与[模板](../harness-pack/assets/harness-template/)；需生成、重组或校准写法时读下方对应范文。

## 按需范文导航

生成、重组、补建正文或需校准写法时读对应范文；普通局部同步不读八份，仅必要时跟随关联章节。范文不复制进目标项目，虚构设定不作事实；生成要求仍只在内容标准维护。

| 正文 | 完整成稿参考 |
|---|---|
| 工程结构 / 编码规范 | [工程结构](../harness-pack/assets/rule-examples/工程结构.md) · [编码规范](../harness-pack/assets/rule-examples/编码规范.md) |
| 开发流程 / 测试规范 | [开发流程规范](../harness-pack/assets/rule-examples/开发流程规范.md) · [测试规范](../harness-pack/assets/rule-examples/测试规范.md) |
| 业务模型 / 领域术语 | [业务模型](../harness-pack/assets/wiki-examples/业务模型.md) · [领域术语](../harness-pack/assets/wiki-examples/领域术语.md) |
| 数据模型 / 接口协议 | [数据模型](../harness-pack/assets/wiki-examples/数据模型.md) · [接口协议](../harness-pack/assets/wiki-examples/接口协议.md) |

## 执行

1. **确定输入**：核对目标项目、需求/决策、实际diff及已有改动。没有可靠基准先询问，不猜“上次运行”；没有稳定资料变化输出“无需同步”并停止。
2. **定位与补缺**：从实际入口找到正文Owner，按内容标准核对本次模块、消费者与暂缺项；首次实现使暂缺失效时补建必要正文，不只维护现存文件。团队项目按[个人接入](../harness-pack/references/local-overlay.md)，公共正文未授权只给建议补丁。
3. **修订**：原位更新受影响段落及入口映射，保持统一结构。代码事实不授予新规则强制性；新增/冲突规则或结构迁移按统一契约确认，本轮已授权的事实同步不重复审批。历史异构正文未获迁移许可只报差异，不强改或冒充结构通过。
4. **验收**：按统一契约对本次文件运行结构检查，再按内容标准回读受影响任务，不重跑全项目验收。涉及[测试入口卡](../harness-pack/references/testing-entry.md)时沿其填写与保护约定，保留用户已有值，不为无关同步读取真实凭据。

## 记录与停止

按统一契约决定是否在原需求目录写[规范变更](../harness-pack/assets/change-template/规范变更.md)，一般事实补齐无需新记录。交付实际修订、无需修订原因及结构/内容证据。无需需求文档的维护确需留记录时，可建日期-维护主题目录，仅放必要记录。

同输入不产生额外diff或重复记录，校验失败只修本次文档；遇并发修改合并或停止，不用reset/clean覆盖。交付后停止，不改业务代码、不运行业务测试、不自动提交、安装或发布。
