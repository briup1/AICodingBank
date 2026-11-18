# Harness 优化：验收场景与结果

本记录用于技能/模板回归，不是已批准的业务测试基线。执行范围是当前工作台，本次修正由唯一执行者完成，未再次委派。已读取的独立报告是实施前设计评估，不是实施后独立审查；以下保留前轮记录并单列当前结果。

## A. 前轮自动回归（历史，不代表当前方案）

执行时间：2026-10-25。使用本机已有 `/Users/ziyun/.local/share/uv/tools/openviking/bin/python`，已核对为 Python 3.12.9；无安装依赖。检查器行为不变，新增测试用于锁定边界及引用，不把字符串测试当语义验收。

命令均在仓库根执行，Python命令带 `PYTHONDONTWRITEBYTECODE=1`：

| 命令（python指上述解释器） | 前轮记录结果 |
|---|---|
| `python -m unittest discover -s tests -p 'test_harness_pack.py' -v` | 13项通过，含模板短例可移除、独立范文目录不存在、模板/链接兼容和空泛正文边界反例 |
| `python -m unittest discover -s tests -p 'test_install.py' -v` | 11项通过，含catalog-only无安装/上游同步副作用 |
| `python -m unittest discover -s tests -p 'test_wl_auto_delivery.py' -v` | 9项通过，含自动目录与登记一致性 |
| `python -m unittest discover -s tests -p 'test_wl_design_handoff.py' -v` | 12项通过，核对ticket入口修改未破坏决策交接 |
| `python install.py --catalog-only` | 生成86项登记目录，未同步上游或安装；harness两项verified仍空 |
| `git diff --check` | 通过 |

初次执行遇到的真实问题：默认Python缺PyYAML，改用上述已有环境；sync改写后少了模板链接，测试拒绝后已补回；catalog修改后未刷新导致一致性测试失败，运行catalog-only后复测通过。未隐藏这些失败，也未修改检查器来迎合正文。

HTML从本需求Markdown生成；只做同源身份/章节/相对链接等静态检查，未启动浏览器，视觉验收未执行。

## B. 人工场景推演

以下是本轮按修改后正文进行的静态推演，不是优化后由新 Agent 实际生成的产物。

| 场景与输入 | 应发生的动作与结果 | 本轮回读 |
|---|---|---|
| 空目录，技术栈未决定 | setup new 仅建入口、流程、测试约定和需求归档；结构/Wiki写具体暂缺时点，不编造架构 | setup调查步骤引用内容标准，标准明确首次确定结构/首次实现后复核 |
| 上一空项目首次出现命令行实现 | sync沿本次入口、业务函数、输出与测试查证；补结构/写法/适用Wiki并改入口，不能仍留“暂无代码” | sync第2/4步及内容标准明确补建、更新入口与交付负责人；开发流程模板留回写位置，无需重跑setup |
| 已有前端/API/异步任务项目，仅发现前端成功链 | 识别声明范围内另外的运行单元/能力/状态，不声称完成全项目；沿边界查证或交付局部/阻塞 | 内容标准明确跨进程不能用纯模块内示例替代；完整范文明确只示范单浏览器的完成操作 |
| 已有OpenAPI/schema的项目 | 接口索引定位实际操作/定义；补身份、副作用、时序与消费者，字段不抄全集 | 内容标准定义权威来源与必要语义要求，薄模板留填写位置；接口范文展示无独立正式协议时的签名、必需结果摘要和合法调用 |
| 八份文档每章只有“按现有实现处理” | 结构可通过，但任务无法回答具体落点/写法/约束，内容可接手必须失败 | 自动反例保留结构通过事实；内容标准要求先手册作答再回读源码，不将盲搜结果冒充手册答案 |
| 仅按钮颜色变化，无稳定资料变化 | sync无需建立Wiki或规范记录，不扩大范围 | sync第1步仍允许“无需同步”；交付路由明确无需同步说明原因 |
| 团队项目只授权个人接入 | 复用团队规则，只有缺口写个人补充；未授权公共正文只给建议，不强改统一结构 | 统一契约与local-overlay原边界保持；内容标准要求覆盖可复用具体既有Owner而非复制全文 |

### 前轮收敛及用户纠正（历史）

前执行者曾将“立即收敛”解释为删除两组共八份完整范文，并把短例置于模板注释，测试也改为禁止范文目录存在。当时的通过只能证明那套实现的结构/字符串约束，不能证明短例与完整成稿等价。此前将该具体删除方案表述为用户批准不准确，用户已明确纠正；现行方案为内容标准＋薄模板＋按需完整范文。调查/深度/任务回读/首次实现后补缺增强保留，生成要求不重新分散到入口和模板。上述真实失败及当时结果保留，不用于宣称当前范文可用性。

## C. 用当前工作台校准“问题要多具体”

本节保留前轮真实源码回读的记录，用于校准标准；本次未重跑该分析，不在工作台生成一份自己的harness，也不把它称作新Agent接手测试。

### 新增一种自研能力

从 AGENTS → EXTENDING 的“Agent行为规则与工作流”可确定：在 tools/skills 对应分类维护唯一正文，在 skills.yaml.self 登记 capability/boundary/tags，verified 初始为空；只运行 install.py --catalog-only，不安装。这些是本项目的具体放置/命名/权限与操作要求，不是商城四层架构。

源码核对：install.py 的 main(catalog_only=True) 只读取 self/第三方登记并写 CATALOG，提前return；实际安装分支才访问宿主 targets、同步 vendor、依据 verified 管理软链。tests/test_install.py 的 CatalogOnlyTests 断言不调用同步/link/unlink且不建target/vendor。

### 修改“临时停用”的行为

从 EXTENDING 的本机停用约定和 README 可确定应沿 skills.local.yaml.disabled 及现有安装入口，不改共享 verified，也不能直接删 Skill。源码核对 load_disabled 对格式校验；main 安装分支在disabled或verified空时调用unlink_skill；unlink_skill只处理软链，遇真实目录保留。直接影响默认安装与目录状态，catalog-only不因此执行停用。

这说明对本项目，标准应要求文档能定位登记→目录/安装→软链边界及相应测试，而不是要求生成Controller/Service表。这里借助实际源码补证，不宣称现有入口已经提供全部函数级答案；真实生成质量仍需独立执行setup/sync验证。

## D. 本次按独立报告修正：执行与当前结果

依据：完整读取本机 `/tmp/harness-independent-skill-creator-review.md`，以及只读缓存 Skill Creator 的 SKILL.md、references/output-patterns.md、references/workflows.md。报告未复制到仓库。八份范文沿原路径以 HEAD 为底稿重建，不声称精确恢复删除前全部未提交增强。

### 已完成的资源修正

- 保留内容标准的调查范围、放置/命名/复用/禁止依赖、业务/数据/接口关联、任务回读和首次实现后补缺要求。标准不再禁止完整范文；模板只留既定章节与简短填写提示。
- 重建工程结构、编码、开发流程、测试四份规则及业务、术语、数据、接口四份 Wiki 范文；保留目录、改动/验证表、try/catch 正反代码、完整操作链与互链，不是空标题恢复。
- 共用输入为 todo-1“买牛奶”和 todo-2“交电费”，仅示范前者的完成操作；新增/列表装载等未提供，不声称全项目覆盖。取消完成的 reopen 命名、模块导出、页面绑定、组件候选及状态/契约/测试联动均标为拟采用扩展，不作为现有能力。
- setup/sync 均直接链接八份范文；生成、重组、补正文或校准写法时读对应一份，普通局部同步不全读，不复制范文到目标项目。
- 替换禁止范文/强制短例断言，保留独立固定章节预期及空泛正文结构可通过的反例；手写正文/机械替换夹具按实际证明范围命名。结构检查器未修改，没有加入语义评分或关键词门槛。

### 实际回归命令

本次执行日期：2026-10-25。已核对 Python 3.12.9，沿用现成含 PyYAML 的解释器；以下在仓库根执行，未安装依赖。

```bash
PYTHONDONTWRITEBYTECODE=1 /Users/ziyun/.local/share/uv/tools/openviking/bin/python -m unittest discover -s tests -p 'test_harness_pack.py' -v
PYTHONDONTWRITEBYTECODE=1 /Users/ziyun/.local/share/uv/tools/openviking/bin/python -m unittest discover -s tests -p 'test_install.py' -v
PYTHONDONTWRITEBYTECODE=1 /Users/ziyun/.local/share/uv/tools/openviking/bin/python -m unittest discover -s tests -p 'test_wl_auto_delivery.py' -v
PYTHONDONTWRITEBYTECODE=1 /Users/ziyun/.local/share/uv/tools/openviking/bin/python -m unittest discover -s tests -p 'test_wl_design_handoff.py' -v
```

结果：四组分别 13、11、9、12 项通过。范文结构兼容、入口链接存在和检查器只读由这些测试覆盖；安装器测试仅在临时夹具操作，当前目录与登记一致性通过，不需要再刷新目录或实际安装。测试通过数不用于证明内容深度或真实生成效果。范文在后续人工回读中只澄清两句局部范围，最终再跑受影响的 harness 组；其他三组有效输入未变，复用结果。

### 人工内容回读（执行者自检）

沿同一输入核对：勾选 todo-1 → complete 按 ID 处理 → storage 保存 → 返回目标对象并更新页面；失败保留展示并提示，todo-2 不变。业务、数据、接口和编码正反例一致。接口给出 string ID、Promise<Todo>、必需结果形状和失败交付，不只留“以源码为准”。未知 ID、重复、并发与装载入口均标未提供/待确认，不编造真实运行证据。

推演下一项取消完成：仅凭工程结构可定位 todo-service.ts 的导出与 TodoPage.tsx 的页面绑定；沿数据/接口链接可识别待确认 true→false、重复及失败语义和直接消费者；沿测试规范可找到服务、页面及必要存储验证。这证明本组范文保住了具体落点与关联的表达价值，不证明真实项目能生成同等质量，也不是独立接手验收。

### 交付前静态核对

- Markdown 相对链接 75 处、其中章节锚点 14 处均可定位；范围为 Pack、两个入口及本需求 MD。需求 HTML 的相对链接及章节 ID 也通过静态核对。
- 读取并核对 `/tmp/render-harness-requirement.mjs` 后运行 `node /tmp/render-harness-requirement.mjs`，从需求 MD 同源重生成 HTML；六节正文与 marked 渲染结果逐段一致，批准/执行阶段标记与 MD 相符。没有视觉检查，不将静态解析称为渲染验收。
- 两句范文范围说明修改后复跑 `test_harness_pack.py`，13 项仍通过；其他三组复用上述结果。`git diff --check` 通过，结构检查器无 diff。
- 本次不改 skills.yaml、CATALOG.md、WORKBENCH.md、shared-protocol 或 wl-ticket-run 的既有未提交内容；未整库回退、清理、暂存或提交。

## 限制

本次未选真实目标项目，也未获其写入许可，未实际执行 setup→sync或业务项目迁移；两个技能 verified 保持空，未全局安装/改宿主链接。HTML仅同源重生成及静态检查，没有浏览器视觉检查。未验证跨宿主自动加载，没有实现后独立审查；实施前独立评估不能替代它。未提交、推送、发布、启服务、上传或读取凭据。
