---
name: wl-harness-setup
description: 初始化或补齐项目 AI 开发底座：调查主要模块、能力与边界，生成能指导新增和修改代码的规则及 Wiki。适用于空项目、已有自主项目和团队个人接入；含内容可接手验收，不用于普通需求实现或局部同步。
---

# 建立项目底座

项目调查 → 工程手册 → 启用入口 → 结构与内容分别验收。不生成业务代码，不自动调用sync。

先读[统一契约](../harness-pack/references/shared-protocol.md)及[内容标准](../harness-pack/references/content-standard.md)的“先确定调查范围”和“内容可接手验收”；成稿时读对应内容段落、[模板](../harness-pack/assets/harness-template/)与下方对应范文。

## 按需范文导航

生成、重组、补建正文或需校准写法时读对应范文；普通局部同步不读八份，仅必要时跟随关联章节。范文不复制进目标项目，虚构设定不作事实；生成要求仍只在内容标准维护。

| 正文 | 完整成稿参考 |
|---|---|
| 工程结构 / 编码规范 | [工程结构](../harness-pack/assets/rule-examples/工程结构.md) · [编码规范](../harness-pack/assets/rule-examples/编码规范.md) |
| 开发流程 / 测试规范 | [开发流程规范](../harness-pack/assets/rule-examples/开发流程规范.md) · [测试规范](../harness-pack/assets/rule-examples/测试规范.md) |
| 业务模型 / 领域术语 | [业务模型](../harness-pack/assets/wiki-examples/业务模型.md) · [领域术语](../harness-pack/assets/wiki-examples/领域术语.md) |
| 数据模型 / 接口协议 | [数据模型](../harness-pack/assets/wiki-examples/数据模型.md) · [接口协议](../harness-pack/assets/wiki-examples/接口协议.md) |

## 执行

1. **定界**：读取目标项目根/子树规则、资料入口、构建清单和Git状态。模式为：空目录new、用户独立控制且授权整理的standardize、团队/无公共修改许可的overlay。只问会改变写入或验收的问题。
2. **调查**：按内容标准调查并在入口写覆盖与资料映射。已有底座回读后补缺；new用[归档约定](../harness-pack/assets/change-template/README.md)建立docs/changes/README，首个需求开始才建主题子目录；overlay按[个人接入](../harness-pack/references/local-overlay.md)执行。
3. **成稿**：保留既有有效约定与消费者，按模板组织获准新建/整理的正文。测试入口按[入口卡](../harness-pack/references/testing-entry.md)维护，不把其凭据复制进规则。
4. **启用与验收**：先呈范围与关键差异，按统一契约处理草案、确认与真实入口。运行结构检查，再执行内容标准中的任务回读；补齐本次缺口或明确局部/阻塞，另核对需求与测试准备链。

## 交付与停止

按统一契约交付实际文件、覆盖/缺口、结构和内容结果；需要规范记录时沿既有需求目录及[变更模板](../harness-pack/assets/change-template/规范变更.md)，不复制需求正文。无输入变化不重写、不重复建正文。

旧结构迁移及唯一历史删除仍须授权，保留已有改动；并发变化先合并或停止。不自动提交、安装、启停服务、建账号/库或执行业务需求；不凭静态检查宣称跨宿主自动生效。满足本次可接手目标后停止。
