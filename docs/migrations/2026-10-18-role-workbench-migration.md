# Skill 与最佳实践迁移记录

日期：2026-10-18。依据：用户本轮明确要求先迁移 Skill 和历史最佳实践、建立记录规范，再提出舍弃清单供审核。未删除任何历史正文；Git 中旧路径显示 D 代表搬迁，不能据此当作实际删掉内容。

## 原始材料重读

已完整重读视频 BV1wgpg6dEvD 的纯文字稿与 SRT：957 段，时间 00:00:00.160—00:33:54.620。10:26—10:58 说明保存成功设置和踩坑；10:58—12:00 说明 Skill 单份维护与复用；14:26—15:26 说明目录归属和命名规则。仅借鉴这些原则，不照搬部门名、工具版本或未经验证的模型判断。字幕含 AI 转写误差，不把模型名当技术事实。原字幕仍在用户下载目录，没有复制入库。

## 本轮边界与变更链

旧分散 Skill → tools/skills 按主要用途归档 → skills.yaml / 项目引用 / 测试适配新路径 → 旧入口只保留相对软链 → catalog-only 刷新目录。Skill 名称、verified、Pack 结构和第三方锁定信息不变，不做重合审查、合并或全局安装。

原 best_practices 方法材料 → 日期-主题-问题目录 → 保留原文并增加来源与 historical-unverified 状态 → 后续按 [唯一规范](../../best_practices/STANDARD.md)构建记录。日期来自 Git 首次入库，不冒充实践成功日期。完整历史重构 Skill 迁到工具，不混作案例。

未迁移外部知识库或其他项目。已有研究仍在原研究入口。角色仍为 draft / enabled: false。没有上传 OpenViking、启动 Agent、推送或发布。没有擅自改用户级 AGENTS 或全局宿主配置。

## 路径表

机器可读完整表：[path-map.json](2026-10-18-path-map.json)。兼容链接只引用新目录，无第二份正文；迁移完整包，包含本机既有依赖/编译文件，但这些忽略内容不纳入 Git。

| 旧位置 | 新位置 | 旧入口 |
| --- | --- | --- |
| `skills/agent-dag-reporting` | `tools/skills/workbench/agent-dag-reporting` | 兼容软链 |
| `skills/deepagents-pack` | `tools/skills/engineering/deepagents-pack` | 兼容软链 |
| `skills/framework-skill-author` | `tools/skills/workbench/framework-skill-author` | 兼容软链 |
| `skills/goal-coach` | `tools/skills/workbench/goal-coach` | 兼容软链 |
| `skills/harness-pack` | `tools/skills/engineering/harness-pack` | 兼容软链 |
| `skills/hgj-git-connect` | `tools/skills/engineering/hgj-git-connect` | 兼容软链 |
| `skills/visual-artifact-workbench` | `tools/skills/shared/visual-artifact-workbench` | 兼容软链 |
| `skills/wl-auto-delivery` | `tools/skills/workbench/wl-auto-delivery` | 兼容软链 |
| `skills/wl-brainstorming` | `tools/skills/engineering/wl-brainstorming` | 兼容软链 |
| `skills/wl-browse` | `tools/skills/shared/wl-browse` | 兼容软链 |
| `skills/wl-compass-local-test` | `tools/skills/engineering/wl-compass-local-test` | 兼容软链 |
| `skills/wl-design-doc` | `tools/skills/engineering/wl-design-doc` | 兼容软链 |
| `skills/wl-design-reachability-review` | `tools/skills/engineering/wl-design-reachability-review` | 兼容软链 |
| `skills/wl-docker-port-registry` | `tools/skills/shared/wl-docker-port-registry` | 兼容软链 |
| `skills/wl-external-enterprise-auth` | `tools/skills/engineering/wl-external-enterprise-auth` | 兼容软链 |
| `skills/wl-git-flow` | `tools/skills/engineering/wl-git-flow` | 兼容软链 |
| `skills/wl-herdrs` | `tools/skills/workbench/wl-herdrs` | 兼容软链 |
| `skills/wl-investigate` | `tools/skills/engineering/wl-investigate` | 兼容软链 |
| `skills/wl-plan-design-review` | `tools/skills/engineering/wl-plan-design-review` | 兼容软链 |
| `skills/wl-plan-eng-review` | `tools/skills/engineering/wl-plan-eng-review` | 兼容软链 |
| `skills/wl-prod-db` | `tools/skills/engineering/wl-prod-db` | 兼容软链 |
| `skills/wl-qa-test-planner` | `tools/skills/engineering/wl-qa-test-planner` | 兼容软链 |
| `skills/wl-req-confirm` | `tools/skills/engineering/wl-req-confirm` | 兼容软链 |
| `skills/wl-requesting-code-review` | `tools/skills/engineering/wl-requesting-code-review` | 兼容软链 |
| `skills/wl-subagent-driven-development` | `tools/skills/engineering/wl-subagent-driven-development` | 兼容软链 |
| `skills/wl-ticket-run` | `tools/skills/engineering/wl-ticket-run` | 兼容软链 |
| `skills/wl-web-auto` | `tools/skills/shared/wl-web-auto` | 兼容软链 |
| `skills/wl-writing-plans` | `tools/skills/engineering/wl-writing-plans` | 兼容软链 |
| `skills-on-demand/apifox` | `tools/skills/engineering/on-demand/apifox` | 兼容软链 |
| `skills-on-demand/hgj-cli` | `tools/skills/engineering/on-demand/hgj-cli` | 兼容软链 |
| `skills-on-demand/hgj-codex` | `tools/skills/engineering/on-demand/hgj-codex` | 兼容软链 |
| `skills-on-demand/hgj-dev-download` | `tools/skills/engineering/on-demand/hgj-dev-download` | 兼容软链 |
| `skills-on-demand/tavily` | `tools/skills/shared/on-demand/tavily` | 兼容软链 |
| `.agents/skills/langfuse` | `tools/skills/engineering/legacy-snapshots/langfuse` | 兼容软链 |
| `ai_coding_sec_dev_workflow` | `tools/skills/engineering/ai_coding_sec_dev_workflow` | 兼容软链 |
| `best_practices/历史项目重构skill` | `tools/skills/engineering/software-architect-restructure` | 兼容软链 |
| `claudecode_guide/skills_guide/android-native-dev` | `tools/skills/engineering/legacy-snapshots/android-native-dev` | 兼容软链 |
| `claudecode_guide/skills_guide/brainstorming` | `tools/skills/engineering/legacy-snapshots/brainstorming` | 兼容软链 |
| `claudecode_guide/skills_guide/frontend-dev` | `tools/skills/engineering/legacy-snapshots/frontend-dev` | 兼容软链 |
| `claudecode_guide/skills_guide/fullstack-dev` | `tools/skills/engineering/legacy-snapshots/fullstack-dev` | 兼容软链 |
| `claudecode_guide/skills_guide/hot_topics` | `tools/skills/media/legacy-snapshots/hot_topics` | 兼容软链 |
| `claudecode_guide/skills_guide/ios-application-dev` | `tools/skills/engineering/legacy-snapshots/ios-application-dev` | 兼容软链 |
| `claudecode_guide/skills_guide/remotion-best-practices` | `tools/skills/media/legacy-snapshots/remotion-best-practices` | 兼容软链 |
| `claudecode_guide/plugin_guide/plugin_store/agent-browser` | `tools/skills/shared/legacy-snapshots/agent-browser` | 兼容软链 |
| `claudecode_guide/plugin_guide/plugin_store/frontend-design` | `tools/skills/engineering/legacy-snapshots/frontend-design` | 兼容软链 |
| `claudecode_guide/plugin_guide/plugin_store/plugin-dev` | `tools/skills/engineering/legacy-snapshots/plugin-dev` | 兼容软链 |
| `claudecode_guide/plugin_guide/playwright-skill` | `tools/skills/engineering/legacy-snapshots/playwright-skill` | 兼容软链 |
| `claudecode_guide/000_examples/.opencode/skills/openspec-apply-change` | `tools/skills/engineering/legacy-snapshots/opencode/openspec-apply-change` | 兼容软链 |
| `claudecode_guide/000_examples/.opencode/skills/openspec-archive-change` | `tools/skills/engineering/legacy-snapshots/opencode/openspec-archive-change` | 兼容软链 |
| `claudecode_guide/000_examples/.opencode/skills/openspec-explore` | `tools/skills/engineering/legacy-snapshots/opencode/openspec-explore` | 兼容软链 |
| `claudecode_guide/000_examples/.opencode/skills/openspec-propose` | `tools/skills/engineering/legacy-snapshots/opencode/openspec-propose` | 兼容软链 |
| `best_practices/历史项目重构` | `best_practices/2026-01-06-历史项目重构-生成计划并驱动开发` | 已迁入，无副本 |
| `best_practices/陌生项目阅读学习` | `best_practices/2026-01-06-陌生项目阅读-梳理架构与用户故事` | 已迁入，无副本 |
| `best_practices/历史项目系统学习文档` | `best_practices/2026-03-24-历史项目学习-生成系统学习文档` | 已迁入，无副本 |
| `best_practices/历史项目探查` | `best_practices/2026-03-11-历史项目探查-按需求逐类分析` | 已迁入，无副本 |

## 兼容和来源边界

注册自研、生成 Pack、原按需包、指南中的完整 Skill 包均已搬迁。vendor 第三方缓存与 skills-lock.json 不动。指南/宿主里的历史快照放 legacy-snapshots，暂不凭空补来源和验证；这不许可今后继续复制上游。旧全局规则与安装链接仍引用旧路径，因此保留兼容软链，须同步外部调用后另审移除。迁移不运行 Skill 中的命令，不继承其嵌套业务示例规则。

只改必要路径引用和维护入口；历史对话、示例、第三方快照正文不重新编写，原有文档缺口不自动修复。旧 Guide 内 Skill 位置也有软链，原教程引用继续可达。

## 完整性核对

- 已移动 55 个包/记录组，覆盖 568 个原受版本控制文件；同时核对 3302 个本机文件（含既有忽略依赖），缺失 0。
- 迁移前可用的 126 个本机仓库来源链接，迁移后新增断链 0；未重建宿主目录。
- 5 个原文件内容有变化，限定为下列路径/说明更新，其余迁移文件 SHA-256 保持。
  - `tools/skills/engineering/deepagents-pack/generation-report.md`
  - `tools/skills/engineering/wl-design-doc/SKILL.md`
  - `tools/skills/engineering/wl-git-flow/SKILL.md`
  - `tools/skills/engineering/wl-git-flow/references/dev-guard.md`
  - `best_practices/2026-03-11-历史项目探查-按需求逐类分析/README.md`

## 验证与待审

新增聚焦验证覆盖：canonical 登记、日期/来源/状态、兼容软链、记录规范与清理边界；catalog-only 测试证明不调用上游同步或链接操作。

实际结果：

- Python 固定 3.12.9，uv 离线复用缓存中的 PyYAML/pytest；未下载 Python 或联网获取依赖。
- 安装器、结构、迁移、可视文档、自动交付、Harness、设计交接与本地清理相关测试：60 passed、1 deselected、22 subtests passed。
- 路径直接影响的 Git / 看板 / 本地服务 / UI 契约测试：62 passed。仅使用测试隔离仓库和本机回环临时服务，不操作真实需求看板或外部系统。
- 唯一 deselected 是 test_harness_pack.py::HarnessPackContentTests::test_developer_manual_contract：首次完整执行失败；它要求工程结构模板含“后端”，基线 HEAD 同一原文件也没有该词。已证明新旧模板字节相同，SHA-256 为 8e351e747b085278725b00c308616e924876778db3584985eacdd2861cc5f147。保留失败，未修改 Skill 或断言凑绿。
- 34 个登记入口除 path 外全部字段相同，skills-lock.json 和自动生成的 CATALOG.md 与基线字节一致；全部迁移的本机文件保留，126 个原可用来源链接继续可达。
- 迁移后的相对 Markdown 引用未新增无法解析项；检测到 76 个既有缺失/占位引用，不属于本轮迁移修复，不扩展修补。git diff --check 通过。

测试范围仅为迁移直接影响，不跑 Skill 各自全量测试、真实浏览器/Herdr 协作、业务系统联调或发布；未声称独立 Review。静态迁移检查不等于真实能力验收。

迁移阶段只列舍弃候选，未执行删除。用户后续批准先删明确可舍弃内容，已单独删除 5 个重复插件文件和 7 个零字节规范文件；随后又按用户批准删除 3 个旧日志、旧会话全文、设备元数据、旧规则正文及一个空审查手册；C04 保留并提炼。详见 [清理执行记录](2026-10-18-cleanup-candidates.md)。没有对 Skill 能力重合做 Review，也没有全库质量审查。
