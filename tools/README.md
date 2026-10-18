# 能力与工具

Skill 本体已按主要用途迁入 [skills](skills/README.md)，名称、验证状态、方法正文和 Pack 配套资料保留。具体路径由根 skills.yaml / skills-lock.json 核实，CATALOG.md 提供能力摘要。

| 类型 | 入口 | 负责什么 |
| --- | --- | --- |
| Skill | [分类与迁移说明](skills/README.md) | 可按需加载的方法与操作能力 |
| 执行配置 | [execution-profiles](execution-profiles/README.md) | Agent、模型和升级条件，尚未配置 |
| 工具接入 | [integrations](integrations/README.md) | 共用 CLI/MCP 接入说明指针 |
| 共用程序 | [scripts](scripts/README.md) | 真正跨能力共用的程序 |
| 通用格式 | [templates](templates/README.md) | 真正共用的交接格式 |

最佳实践记录单独放在 [best_practices](../best_practices/README.md)，它能记录技术、内容等问题，不强行归为工具的一部分。岗位只引用能力；Skill 专用脚本、模板、参考资料随包，不拆散。

本轮只完成文件迁移和引用适配，没有启用岗位、批量安装、更新上游或修改凭证配置。旧 Skill 路径保留兼容软链，不是第二份源码。
