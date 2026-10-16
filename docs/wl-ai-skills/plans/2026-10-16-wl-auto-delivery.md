# wl-auto-delivery 修改计划

日期：2026-10-16。依据：本轮对话已收敛需求；用户授权“制定计划，独立 Agent 修改，负责人验收”。不另生成需求确认/方案平行文档。本计划是实现与验收依据，不是其他业务需求的批准证据。

## 目标与不做

主链：需求（目标/范围/规则/差异）→ 按业务分组的测试用例 → 独立用例审查 → 人确认需求+用例及执行约定 → 明确推荐方案 → 开发/TDD → 聚焦 Review → 目标环境逐条验收 → 缺陷修复/复测 → 证据留存与到期清理判断。

- 用测试用例承接具体数据/操作/预期，不再重复维护 AC 验收场景正文；旧 AC 文档兼容原位读取，不批量迁移。
- 需求 HTML 只需整体用例链接，不强制逐条双向对应；测试用例按业务部分分组。
- wl-qa-test-planner 保留现有核心生成步骤、优先级、字段、范围与停止规则，只作最小输出/交接增补；审查调度和变更回流放总流程，独立审查标准放配套参考。
- wl-auto-delivery 取代 wl-phase-routing；各环节可单独用，不能强制依赖总流程私有文件。
- 本任务不发布/提交/push/全局安装/同步第三方，不创建常驻服务、数据库或新流程引擎；不对真实证据运行删除，不虚报端到端业务验证。

## 影响与完成标准

影响：工作台路由、Skill 文本协议、设计 HTML 元信息检查、网页运行目录交接、本地环境清理默认行为及其最小测试。无业务数据迁移、无业务 API 改动。保留旧文档人工批准语义、独立调用方式和既有未提交改动。

完成标准：
1. 交接链完整，无 AC/TC 双份正文要求；Grill 业务结论回写需求并检查受影响用例，未知预期不得擅定。
2. QA 核心不退化；双向范围核对（需求→用例防漏、用例→依据防越界）、适用边界、可执行性、重复检查有明确说明；不扩展无关测试。
3. 两种决策模式：默认人工确认方案；用户明确委托后可自动采用有依据的推荐方案。委托有独立的状态/证据，不伪造人工 approved；元信息检查和工单入口一致。
4. 开发后 Review 使用 wl-requesting-code-review 的聚焦模式，仅设计符合性与交付阻断缺陷；有版本、直接依赖边界及证据不足结论，不无限扩审。
5. 环境在需求+用例确认时约定，执行前核对 URL/角色/前后端版本/写授权；本地自测不等于 Dev/Beta 验收，生产不默认、不自动切环境。
6. 结果按运行追加，保留失败/阻塞/未执行、不适用原因及复测历史；不修改通过标准凑通过。长期摘要与外部证据分离，Worktree 清理不丢必要记录。
7. 证据保留期 7/30 天只作为待确认建议，不自动生效。仅发布成功+需求关闭（不是合入 master）进入已授权保留策略；有缺陷、待复测、hold 不清理。默认预览/不删除；不引入后台清理器。
8. 负责人独立重跑聚焦检查并审阅实际 diff；新总流程 verified 留空，静态检查不冒充真实项目验证。

## 独立实现与负责人验收

一个持续 Pi 实现 Agent，通过 Herdr 启动，thinking=high。输入为本计划、目标 Skill 和实际工作区；输出为文件改动、聚焦验证结果、未覆盖项。它解决执行与验收由不同会话承担的要求；没有该委派就不能称为独立实现。负责人不并发修改其写集，完成后检查和重跑验证；必要返工交回同一 Agent。最多两次定向返工，不凑角色。

仓库同时有其他 Agent 活动：以委派时磁盘快照为基线；只写下面文件；遇到同文件并发变化停止协调，不回退他人修改。特别保留现有 wl-web-auto 改名、skills.yaml、CATALOG.md 的改动。

## 子计划 A：总入口与契约（独立可验收，最多 8 个文件）

文件（均相对仓库根）：
1. 删除/重命名 skills/wl-phase-routing/SKILL.md → skills/wl-auto-delivery/SKILL.md（一个重命名对象）
2. 新增 skills/wl-auto-delivery/references/test-case-review.md
3. 新增 skills/wl-auto-delivery/references/execution-and-evidence.md
4. 修改 WORKBENCH.md
5. 修改 skills.yaml（只改对应项；verified 留空）
6. 生成 CATALOG.md（用 install.py 的纯 write_catalog API；不执行 main，不手改）
7. 新增 tests/test_wl_auto_delivery.py
8. 新增 skills/wl-auto-delivery/references/regression-scenarios.md

任务：先添加测试并见 RED（新入口/登记缺失）；再实现精简总入口和配套规则。维持 Observe/Confirm/Design/Execute/Verify/Learn 的按需行为，不强迫只读任务走流水线。自动模式要求显式委托、范围/数据/成本/操作授权边界；不能以沉默批准。推荐需明确结论和理由，不制造多方案；重大不可逆或范围/授权变化停止。正式用例基线一次独立审查；其他角色按缺口最少使用，只通过 Herdr Pi high 委派；不可用不能冒充独立完成。

验证：Python unittest 仅运行 tests/test_wl_auto_delivery.py；检查注册路径存在、旧入口不再作为主入口、Markdown 本地引用有效、QA 核心保留、阶段和交接约定无冲突。文案断言只是结构保护，语义另按回归场景人工推演。

## 子计划 B：需求→用例→方案→开发→Review（依赖 A，最多 9 个文件）

1. skills/wl-req-confirm/SKILL.md
2. skills/wl-req-confirm/doc-html-style.md
3. skills/wl-qa-test-planner/SKILL.md（最小增补，不重写）
4. skills/wl-design-doc/SKILL.md
5. skills/wl-design-doc/scripts/check_design_doc.py
6. skills/wl-design-doc/references/regression-scenarios.md
7. skills/wl-ticket-run/SKILL.md
8. skills/wl-requesting-code-review/SKILL.md
9. 新增 tests/test_wl_design_handoff.py

任务：更新需求唯一正文与整体链接；批准状态与执行阶段分离且兼容旧稿。设计保持唯一 HTML，增加来源用例/版本及明确决策方式；新增委托模式时同步脚本校验与工单入口，不把委托标人工批准。先为委托缺证据/人工缺批准/合法委托/旧合法批准等写小 HTML 夹具见 RED，再修改检查脚本到 GREEN。候选方案不等于可执行方案，关键假设无证据依旧阻断。

用例只最小增加业务分组和链接/来源说明。Review 新增明确聚焦模式，默认完整模式不退化；本流程显式调用聚焦模式。工单从既有用例引用，不复制业务预期；TDD 按行为小步推进而非一次性写所有测试代码；统一 Review 在业务验收之前；/goal /list 可选，默认持续负责人，不强制多 Agent，不全库回归。

验证：上述设计脚本夹具测试；语义检查全链一致，不留强制新 AC 正文或“委托仍必须人工批准”的矛盾；QA 原有五步、字段及边界不变。

## 子计划 C：执行环境、证据与安全清理（依赖 A，最多 7 个文件）

1. skills/wl-web-auto/SKILL.md
2. skills/wl-web-auto/scripts/run.mjs（仅确需复用外部运行根时最小增补）
3. skills/wl-web-auto/scripts/self-test.mjs（随目录行为有改才改）
4. skills/wl-compass-local-test/SKILL.md
5. skills/wl-compass-local-test/scripts/local-test-down.sh
6. 新增 tests/test_wl_local_test_cleanup.py
7. skills/wl-auto-delivery/references/execution-and-evidence.md（A 文件的定向补充，不另计全任务文件数）

任务：总流程记录环境→Web Auto 接收明确入口和基线；单独调用仍可沿已确认项目设置或用户输入，不依赖总流程。默认业务环境无设置时推荐 Dev（私人项目本地）并随确认一次确定；生产永不默认，不获授权不写。

证据使用用户级 state/wl-auto-delivery/<project>/<requirement>/<run>/ 或用户明确目录，与 Worktree 生命周期脱钩。长期项目摘要可入 Git，原始截图/日志/凭证不自动入 Git。尽量复用现有 Web Auto 的用户指定运行目录能力，确需 CLI 增补才实现，不写新清理引擎。

本地 down 默认停止且保留产物，删除须独立显式授权参数并校验边界；已有 --purge 不再隐含证据删除。共享 MQ 不能默认因单需求完成就停：停共享件/删 volume 独立显式选择并说明使用者确认。先用临时目录与假的 lsof/docker/kill 等可执行文件复现旧行为（RED），再修改到 GREEN，禁止碰真实进程、容器或用户 state。校验正常保留、显式清理、路径穿越/符号链接拒绝、共享 MQ 默认不停止；不借此重写启动器或修历史旁支问题。

验证：bash -n、隔离 unittest、Web Auto node --test（仅目录脚本直接受影响部分）。只有临时夹具删除获本任务测试授权，真实清理策略仍未启用。

## 运行工具与聚焦验收

Python 固定 uv 管理的 3.12.9，先验证版本；不装依赖。当前裸 Python 缺 PyYAML，可按需以 PYTHONPATH 复用 /Users/ziyun/.local/share/uv/tools/openviking/lib/python3.12/site-packages（先核对兼容，不使用 OpenViking 服务或数据）。不调用全量 install.py；以纯函数生成目录并用 tests/test_install.py 隔离验证，不链接任何宿主。

建议命令（以实现后实际存在的文件为准）：
- uv run --no-project --python 3.12.9 --no-python-downloads python -m unittest discover -s tests -p 'test_wl_auto_delivery.py' -v
- 同上分别运行 test_wl_design_handoff.py、test_wl_local_test_cleanup.py
- 需要 YAML 的命令显式设置上述 PYTHONPATH；tests/test_install.py 仅作为登记/生成直接回归。
- node --test skills/wl-web-auto/scripts/self-test.mjs
- bash -n skills/wl-compass-local-test/scripts/local-test-down.sh
- git diff --check；针对委派前基线核对所有新增/修改及未授权文件不变。

负责人语义验收：独立调用 QA、A/B 两部分分组、Grill 确定规则后用例回流、默认人工方案与显式委托两模式、缺证据不推进、聚焦 Review 不越界、环境阻塞不静默切换、失败→修复→新轮复测、合入 master 不触发删除、证据 hold/未授权保留、Worktree 清理后报告仍可解释。

不执行真实业务 E2E、真实网页截图或线上访问；记录为未覆盖，不能据此填 verified。仅改规范/小脚本不为形式新增业务 app。

## 负责人验收记录（2026-10-16）

结论：本轮规范、阶段交接与辅助脚本修改验收通过；不是整条流程的真实业务 E2E 通过，新总流程 verified 继续为空，未全局安装。

实际委派：Herdr 独立 Pi 会话 delivery-impl（wM:p12），my-provider/gpt-6.1-sol，启动参数 --thinking high，终端状态实际显示 high。Pi 原生工具不逐项审批，启动时关闭扩展/MCP 并一次性信任本项目；这不构成操作系统沙箱或高风险操作授权。一个持续实现者完成 A/B/C，负责人独立读 diff、重跑验证；未另建审查角色。

首轮验收发现并交回原 Agent 定向返修一次：补齐用例 Markdown→同源 HTML 阅读页与整体相对链接；补缺陷七项最小格式、分轮示例和证据分类；明确全部适用用例通过才可 done；补轻量恢复记录、Git/本地环境/API/查库导航；收窄 focused Review 输出并说明需求 ID→网页 task slug 映射、外部用例独立接入。未扩展为新服务、流程数据库或后台删除程序。

| 验收项 | 结果与证据 |
| --- | --- |
| 需求→用例→Grill 回流、业务分组及整体阅读链接 | 已检查相关规范及本地引用；具体预期唯一正文、旧 AC 原位兼容；生成真实 HTML/浏览器点击未覆盖 |
| QA 核心保留、各环节可单独使用 | 对派发前快照逐字节核验 QA 执行链和交付自检整段不变；外部用例夹具可交接、没有 HTML 前置卡住单独 QA |
| 人工批准/显式委托两模式 | 11 项临时 HTML 交接检查通过，覆盖缺证据、错版本、边界缺失、状态混用、草稿不可实施与旧合法批准兼容；实际授权真实性仍由读真实记录确认 |
| 开发后聚焦 Review | 只查设计偏离及具体交付阻断缺陷；旧 full 模式移除新增 Modes 后与快照字节一致；本轮未运行真实业务代码 Review |
| 环境/版本/操作授权 | 规范明确确认时约定、执行前核对，阻塞不切环境、本地不冒充 Dev/Beta；未连真实环境 |
| 结果、缺陷、复测、done | 独立推演失败/阻塞不 done、复测新 run 保留旧失败、未知根因不假称已确认；文字检查不等于真实执行 |
| 清理与独立证据目录 | 8 项隔离清理检查、5 项 Node 检查通过；默认留产物、不停共享 MQ，显式删除拒绝穿越/符号链接；7/30 天仅待确认建议，未启用自动删除 |
| 入口与目录登记 | 7 项总入口/契约检查、10 项隔离 installer 回归通过；CATALOG 由纯函数生成，未跑真实安装器 main |

负责人最终实际运行：Python 3.12.9；test_wl_auto_delivery.py 7 项、test_wl_design_handoff.py 11 项、test_wl_local_test_cleanup.py 8 项、test_install.py 10 项，合计 36 项通过；node --test skills/wl-web-auto/scripts/self-test.mjs 5 项通过；bash -n local-test-down.sh 与 git diff --check 通过。所有真实运行目录/删除验证均限定于临时夹具，未停真实服务/容器。QA 保留与 Review full 保留另用派发前快照独立核对，不仅依赖实现者给定的哈希。

派发前快照实际共 28 个相关文件，本轮 17 个既有路径修改或重命名、11 个未变；保留原 wl-web-auto 改名等未提交改动，不将其算作本轮成果。未 commit/push、未同步第三方、未安装依赖、未改宿主加载目录。

已处理副作用：实现者第一次 Web Auto RED 夹具遗漏隔离 stateHome，产生两份空白用户级运行目录（2026-10-16T09-51-17-812Z-wLKWH0、2026-10-16T09-51-17-813Z-8LyRAf）。后续测试已补隔离。负责人核实只有空 evidence/screenshots、初始未执行 result.md 与 scenarios=[] 的 run.json，严格匹配该两目录后逐文件删除；未触碰其他运行或真实证据。

残余风险/未覆盖：未以真实需求执行独立用例审查、Grill、完整自动开发验收；未进行真实页面/窄屏视觉检查；清理脚本仅隔离 stub 验证，进程归属仍为端口+命令+slug 路径段，不是完整进程身份系统。当前交付为可按需阅读的规范与本地已测辅助脚本，不宣称生产可用或全链已验证。
