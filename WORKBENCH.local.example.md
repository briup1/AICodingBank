# 本地工作台上下文

复制本文件为 `WORKBENCH.local.md`。真实文件被 Git 忽略，只保存稳定且适合每次工作读取的信息。

## 个人偏好

- 回复语言：
- 输出偏好：
- 工作习惯：
- 需要长期避免的行为：

## 工作区目录

- 项目根目录：`/home/weilan/workdir`
- 优秀项目：`/home/weilan/workdir/excellent_project`
- 公司项目：`/home/weilan/workdir/remote_project`
- 个人项目：`/home/weilan/workdir/self_project`
- 个人知识库：`/home/weilan/workdir/self_project/weilan-knowledge-wiki`

## 项目索引

项目真实文件是事实来源；这里只保存用于路由的一句话简介、绝对路径和入口依据。个人项目按最近 30 天内存在 Git 提交或普通项目文件修改筛选；公司项目收录全部非隐藏一级目录；优秀项目不进入索引。

### 近期个人项目

| 项目 | 一句话简介 | 本地路径 | 入口依据 |
| --- | --- | --- | --- |
| ai-agent-book | 面向 AI Agent 学习者与实践者，提供系统讲解 Agent 设计原理的开源书稿及配套实验代码 | `/home/weilan/workdir/self_project/ai-agent-book` | `README.md` |
| AICodingBank | 面向个人 AI 编码工作流，统一管理项目入口、任务阶段、长期知识以及可安装的 Skill 与提示模板 | `/home/weilan/workdir/self_project/AICodingBank` | `README.md` |
| codex-web-ui | 为本机 Codex 用户提供独立 Web 客户端，以浏览器界面访问官方 Codex 会话与交互能力 | `/home/weilan/workdir/self_project/codex-web-ui` | `AGENTS.md` |
| codex-web-ui-thread-roots | 为本机 Codex 用户提供独立 Web 客户端，以浏览器界面访问官方 Codex 会话与交互能力 | `/home/weilan/workdir/self_project/codex-web-ui-thread-roots` | `AGENTS.md` |
| deepagents-scaffold | 面向多 Agent 应用开发者，提供可快速搭建配置、记忆、通道和链路追踪能力的生产级项目模板 | `/home/weilan/workdir/self_project/deepagents-scaffold` | `README.md` |
| excel-quote-extractor | 面向海运报价处理人员，将 Excel 海运报价单转为经澄清、校验和差异处置后的标准字段结果 | `/home/weilan/workdir/self_project/excel-quote-extractor` | `README.md` |
| personal-agent-workbench | 面向个人用户，以项目为上下文按需读取外部系统事实并留存来源凭据的 Agent 工作台 | `/home/weilan/workdir/self_project/personal-agent-workbench` | `README.md` |
| personal-workbench | 供个人只读观察 Agent 会话、本地 Git Worktree 和 agent-dag/v1 任务进度的工作台 | `/home/weilan/workdir/self_project/personal-workbench` | `README.md` |
| weilan-knowledge-wiki | 供个人与 LLM 共同摄取、关联、查询和综合原始资料的 Obsidian 知识系统 | `/home/weilan/workdir/self_project/weilan-knowledge-wiki` | `README.md` |

### 公司项目

| 项目 | 一句话简介 | 本地路径 | 入口依据 |
| --- | --- | --- | --- |
| agent-skills | 为 AI 编码助手提供覆盖诊断、审查、发布、数据与配置查询等工作的可安装技能集合 | `/home/weilan/workdir/remote_project/agent-skills` | `README.md` |
| agent-tools | 为 AI 编码助手提供数据库与配置查询、非生产环境服务诊断发布及 TAPD 查看的一体化命令行工具 | `/home/weilan/workdir/remote_project/agent-tools` | `README.md` |
| ai-agent | 为货代邦业务提供面向销售人员的查价与询报价助手及其产品协作知识入口 | `/home/weilan/workdir/remote_project/ai-agent` | `README.md` |
| autotariff-agent-platform | 为自动运价 Agent 提供运价领域服务平台 | `/home/weilan/workdir/remote_project/autotariff-agent-platform` | `services/tariff-domain/pyproject.toml` |
| autotariffextract | 按船公司模板处理 OOCL、SITC、RCL 等来源的海运运价表 | `/home/weilan/workdir/remote_project/autotariffextract` | `README_zh.md` |
| codex-web-agent-workbench | 为运价业务人员提供可观察、可审批和可纠偏的 Codex 运价模板开发与交付工作台 | `/home/weilan/workdir/remote_project/codex-web-agent-workbench` | `README.md` |
| codex-web-agent-workbench-running | 为研发人员提供可对话、审批、中断并查看执行差异的 Codex Web 控制台 | `/home/weilan/workdir/remote_project/codex-web-agent-workbench-running` | `README.md` |
| compass-platform | 为供应商、运营人员、企业客户和销售提供统一的海运运价管理、查价及销售辅助平台 | `/home/weilan/workdir/remote_project/compass-platform` | `README.md` |
| email_cockpit_expr | 简介待确认：现有入口仅能确认它启动 email_cockpit_server，缺少业务用途说明 | `/home/weilan/workdir/remote_project/email_cockpit_expr` | `Dockerfile` |
| eml_intent_cls | 为海运出口普货整箱业务自动识别邮件所处业务环节与具体意图，并提取关键业务属性 | `/home/weilan/workdir/remote_project/eml_intent_cls` | `README.md` |
| entity-standardizer | 为业务系统统一标准化港口、船公司、城市和国家等多数据源实体 | `/home/weilan/workdir/remote_project/entity-standardizer` | `README.md` |
| external_demo_display_server | 为外部演示场景快速展示数据处理、智能询报价和地址信息提取等可视化应用 | `/home/weilan/workdir/remote_project/external_demo_display_server` | `README.md` |
| eyun_assist_bot | 简介待确认：目录内没有可说明主功能的入口文档 | `/home/weilan/workdir/remote_project/eyun_assist_bot` | `-` |
| freight_normalize | 为海运业务将自由文本港口名称映射为标准港口数据，并支持人工审核纠错 | `/home/weilan/workdir/remote_project/freight_normalize` | `README.md` |
| global-shipping-news-etl | 为海运风险分析清洗、结构化和标准化全球航运新闻，并提供可追溯证据与效果验证 | `/home/weilan/workdir/remote_project/global-shipping-news-etl` | `README.md` |
| hgj-codex-plugins | 为 HGJ 工程团队提供 Codex 插件市场，支持需求分析和从开发到验证交付的自动化工作流 | `/home/weilan/workdir/remote_project/hgj-codex-plugins` | `README.md` |
| llms_center | 为开发者提供多模态大模型调用与文件格式化解析能力 | `/home/weilan/workdir/remote_project/llms_center` | `readme.md` |
| saas-support | 简介待确认：现有 README 仅记录模块依赖关系，缺少业务用途说明 | `/home/weilan/workdir/remote_project/saas-support` | `README.md` |
| serp-ai-gateway | 为 SERP 向 AutoTariffExtract 发起关税文件抽取提供请求转发与即时响应中转 | `/home/weilan/workdir/remote_project/serp-ai-gateway` | `README.md` |
| short-text-matching | 为多个业务应用提供基于语义相似度的短文本关键词匹配与检索服务 | `/home/weilan/workdir/remote_project/short-text-matching` | `readme.md` |
| smart_agents_group | 为开发人员统一组织多个独立仓库的跨项目联调、协作和需求处理入口 | `/home/weilan/workdir/remote_project/smart_agents_group` | `README.md` |
| smart-agents-web | 简介待确认：目录内没有可说明主功能的入口文档 | `/home/weilan/workdir/remote_project/smart-agents-web` | `-` |
| smartocr | 为单证处理场景提供按业务类型、字段和规则配置的通用 OCR 信息抽取能力 | `/home/weilan/workdir/remote_project/smartocr` | `readme.md` |

## 常用知识入口

- 知识库首页：`/home/weilan/workdir/self_project/weilan-knowledge-wiki/index.md`

## 禁止写入

不要保存 Token、密码、Cookie、私钥、完整连接串、客户敏感数据、会话原文或临时任务进度。
