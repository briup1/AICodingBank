# Skill 分类与维护

Skill 本体已迁入这里。按主要用途一个物理归宿，多用途通过标签和引用表达，不按岗位复制。岗位仍为未启用草稿，移动 Skill 不等于启用岗位。

- [engineering](engineering/README.md)：软件交付、技术框架、工程接口和测试。
- [media](media/README.md)：内容生产相关的历史能力。
- [shared](shared/README.md)：通用网页访问、可视文档与本机共用能力。
- [workbench](workbench/README.md)：工作台能力管理、Herdr 编排与阶段路由。

注册能力仍由根 skills.yaml、skills-lock.json 与 CATALOG.md 定位；验证状态和名称不因迁移改变。Pack 保持完整，逐入口登记。第三方上游仍只登记，源码由 vendor 缓存，不迁入或复制 vendor。

## 原有按需包和历史快照

engineering/on-demand 与 shared/on-demand 保留现有按需资料包，路径变更不代表自动安装或重新验证。legacy-snapshots 保存原先散落在指南/宿主目录中的 Skill 与必要配套文件，来源/验证尚未统一登记，不自动晋升到自研或已验证集合，也不在本轮去重。

新增第三方仍只登记上游；本轮保留历史快照是迁移例外，不是今后复制第三方源码的许可。快照是否替换为上游登记须另行核对，不能无证据丢掉独有内容。

## 旧路径兼容（已退役）

原 skills 下各包、skills-on-demand 子包以及原指南中的 Skill 位置曾以相对软链接保留。2026-10-18 用户批准后已整体退役：宿主加载位置改由 install.py 直连 tools/skills，仓库内旧兼容入口与空目录已删除，正文始终只有新路径一份。宿主链接清单与回滚方式见 [退役记录](../../docs/migrations/2026-10-18-legacy-entry-retirement.md)，迁移历史见 [迁移记录](../../docs/migrations/2026-10-18-role-workbench-migration.md)。重新引入兼容路径须经确认。

普通查找只读取必要能力，不运行全量安装器。迁移后仅生成目录：python install.py --catalog-only；默认安装模式仍有上游同步和宿主写入，须按本机授权规则使用。
