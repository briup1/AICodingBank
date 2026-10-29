# 顶层文档重构与项目经理对话级启用

日期：2026-10-19。依据：用户批准两类改动——顶层文件职责唯一化（去冗余、删不必要内容）；项目经理启用对话级开场与接单（不含自动调度、子 Agent 创建、模型切换）。

## 问题与动机

- CLAUDE.md 是 AGENTS.md 的完整复制且已漂移（红线出现新旧两个版本），双份维护的代价已经发生。
- 同一内容多处维护：维护红线在 AGENTS.md 与 README.md 各一份；加技能步骤在 README 与 EXTENDING 各一份；岗位状态在 README、WORKBENCH、roles/README、CONTEXT.md 四处描述。
- WORKBENCH.local.example.md 混入 87 行真实项目索引（/home/weilan/... 路径），示例文件应只做结构模板。

## 改动清单

| 文件 | 改动 |
| --- | --- |
| AGENTS.md | 能力控制面段压缩，细节指向 README/EXTENDING；维护红线 7 条保持唯一权威 |
| CLAUDE.md | 17 行复制 → 3 行指针（规则以 AGENTS.md 为唯一正文） |
| README.md | 重写：删意图路由图、岗位状态长段、目录树、维护红线、日常使用细节；新增"设计理念"与"文档导航"；日常使用压缩为"常用命令" |
| WORKBENCH.md | 岗位段同步启用状态；"开始一次工作"新增开工开场触发；能力控制面缩为 5 行；信息归宿表改为 EXTENDING 指针 |
| EXTENDING.md | §1.1 更新为退役/评估后口径；新增 §1.2 岗位与角色流程；收编 tags 词表、ref 说明、Skill Pack、模板后缀、分支非隔离、源目录不存在处理 |
| CONTEXT.md | 状态句改纯定义；项目经理条目更新；新增"开工开场"词条 |
| WORKBENCH.local.example.md | 清为纯占位符模板（历史数据可从 Git 找回，未另存本机副本） |
| roles/project-manager/ROLE.md | status: active、enabled: true（scope=对话级）；新增"开工开场"协议与示例 |
| roles/README.md | 状态行更新（项目经理已启用；其余草稿） |
| tests/test_role_workbench_structure.py | 岗位断言改为"仅项目经理启用"，并断言开工开场协议存在 |
| docs/reference/工作台目录地图.md | 顶层文件注解同步 |

## 验证

全量 pytest：124 passed，仅剩既有 `test_harness_pack.py::test_developer_manual_contract` 失败（自基线 21f2dd6 未再变动，与本次改动无关）。链接解析、岗位断言、忽略边界测试均通过。

## 未覆盖与边界

- 未启用其余岗位；会话身份、调度、恢复机制仍为设计待办。
- 未改 install.py、skills.yaml、skills-lock.json、CATALOG.md 及任何 Skill 正文。
- 示例文件中的历史索引数据未先备份到本机 local 文件；如需找回，从 Git 历史读取。

## 回滚

`git revert` 本次提交即可：CLAUDE.md 恢复为复制版、项目经理恢复 draft 即可回到旧行为。
