# AICodingBank

个人 AI 工作台的控制入口，也是 AI Coding 兵工厂：统一连接个人上下文、项目入口、任务阶段与长期知识，并管理**自研 skill、第三方 skill 登记、prompt 模板包**。

## 两种使用意图

用户只需在本目录描述目标，不需要说明该读哪个文件或把信息存到哪里。Agent 从 `AGENTS.md` / `CLAUDE.md` 自动分流：

```text
用户请求
  ├─ 使用工作台 -> WORKBENCH.md -> 定位项目、选择阶段和能力、执行验证
  └─ 拓展工作台 -> EXTENDING.md -> 分类规则/知识/Skill/偏好并更新唯一归宿
```

- **[WORKBENCH.md](WORKBENCH.md)**：介绍工作台能提供哪些帮助，以及 Agent 如何获取并使用这些帮助。
- **[EXTENDING.md](EXTENDING.md)**：介绍如何持续增加规则、知识、Skill、偏好、项目入口和工作流。
- **`WORKBENCH.local.md`**：本机个人上下文和项目索引；存在时由使用流程按需读取。

AICodingBank 管理岗位、能力与本项目的 [最佳实践记录](best_practices/README.md)。外部知识库继续管理项目档案、来源资料、研究和综合知识，不复制本项目 Skill 或最佳实践正文；需要关联时只放指针。

## 岗位制新结构（骨架，未启用）

新结构见 [岗位名册](roles/README.md)、[个人资料入口](personal/README.md)、[工具分类](tools/README.md)与[结构设计及迁移边界](docs/wl-ai-skills/specs/2026-10-18-role-workbench-structure-design.md)。协调岗位统一称“项目经理”；岗位按技术工程、媒体内容和共享支持分组，不增加部门管理层。

岗位仍未启用；Skill 已迁到 tools/skills，历史最佳实践已按日期和问题归档，claudecode_guide 的教程内容已归位到对应归宿（见 [归位记录](docs/migrations/2026-10-18-claudecode-guide-relocation.md)）。只搬迁及更新必要引用，不处理能力重合，不提升验证状态。旧 Skill 路径保留兼容软链，已按用户逐批批准删除旧副本、空文件、日志、会话原文及旧设备/规则文件，未扩大到其他资料。见 [迁移记录](docs/migrations/2026-10-18-role-workbench-migration.md)与[清理执行记录](docs/migrations/2026-10-18-cleanup-candidates.md)。

## 现用目录结构

```
├── WORKBENCH.md         # 使用入口：能力地图、项目定位与阶段路由
├── EXTENDING.md         # 拓展入口：规则、知识、Skill 与偏好的归档方法
├── WORKBENCH.local.example.md  # 本机个人上下文与项目索引模板
├── roles/               # 项目经理与分组岗位手册（草稿、未启用）
├── personal/            # 个人资料入口，本机画像忽略
├── tools/skills/        # engineering / media / shared / workbench；Skill 单份正文
├── skills/              # 旧路径兼容软链，不再新增正文
├── skills.yaml          # 总登记表：加载位置 + 自研清单 + lock 指针
├── skills-lock.json     # 第三方 skill 登记（只登记上游地址，不复制文件）
├── install.py           # 安装器：clone 上游到 vendor/ → 软链到各加载位置
├── vendor/              # 第三方上游的 clone 缓存（gitignore，勿手动改）
├── best_practices/      # 按日期-主题-问题归档，STANDARD.md 维护规范
├── docs/reference/      # 参考资料（skills 速查表等）
└── claudecode_guide/    # 历史指南空壳：兼容软链 + 待批说明文件，等待最终删除审核
```

## 日常使用

### 新机器 / 同步环境

```bash
git clone <本仓库地址> && cd AICodingBank
python3 install.py
```

默认安装命令会同步第三方上游，并向 skills.yaml 的 targets 写入已验证且未本机停用的 Skill 软链，需明确安装授权。本机默认按需读取，不因登记维护而批量安装。只刷新能力目录时运行 `python3 install.py --catalog-only`，不联网、不写宿主加载位置。

### 添加自研 skill

1. 在 `tools/skills/<分类>/<skill-name>/` 下开发，分类规则见 [Skill 说明](tools/skills/README.md)，`SKILL.md` 必填
2. 在 `skills.yaml` 的 `self:` 下加一行：

```yaml
  - name: my-new-skill
    path: tools/skills/engineering/my-new-skill
```

3. 保留真实验证状态，先运行 `python3 install.py --catalog-only` 刷新目录；实际安装按授权另行执行，提交也不自动进行。

改进自研 Skill = 修改登记指向的新目录；已有软链可能使变动立即影响其他会话，分支不是运行隔离。

### 仅在当前电脑停用某个 Skill

不要改共享的 `skills.yaml` 验证状态。在仓库根目录创建不会被 Git 跟踪的 `skills.local.yaml`：

```yaml
disabled:
  - agent-dag-reporting
```

再次运行 `python3 install.py` 后，该 Skill 仍保留在仓库和 `CATALOG.md`，但当前电脑的加载目录不会存在它的软链接。安装器只会自动移除软链接；若加载位置是历史真实目录，会报错并要求先迁移，避免误删源码。删除禁用项并重跑安装器即可重新启用。

### 收录生成式 Skill Pack

由 `framework-skill-author` 生成的一组关联 Skill 按 Pack 保存，避免来源清单和生成报告散落：

```text
tools/skills/engineering/<framework>-pack/
├── source-manifest.json
├── generation-report.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── sources.md
```

每个可加载 Skill 仍需单独登记到 `skills.yaml` 的 `self:`，其 `path` 指向 Pack 内的具体目录。

### 收藏第三方 skill

**不要把文件拷进仓库。** 只在 `skills-lock.json` 的 `skills` 里加一条登记，**必须当场写三行人话**（30 秒的事，攒多了就补不动了）：

```json
"some-skill": {
  "source": "owner/repo",
  "sourceType": "github",
  "ref": "v1.2.3",
  "skillPath": "path/to/SKILL.md",
  "computedHash": "",
  "capability": "它能干什么，一句话，用你自己的语言",
  "boundary": "它不干什么、什么时候别用、有什么外部依赖",
  "tags": ["写作", "图像"],
  "verified": ""
}
```

`ref` 可选；填写分支或标签时安装器会固定到该版本，不填写则继续跟随仓库默认分支。

然后 `python3 install.py` 会自动 clone 上游到 `vendor/`。

**verified 闸门**：默认安装模式只安装已验证且未本机停用的 Skill，未验证时移除安装器管理的旧软链；这不阻止按需读取源码，也不构成实际工具权限隔离。真实验证后才能填写日期，迁移不算验证。固定 ref 还需 computedHash 校验。catalog-only 不改任何宿主链接。

个性化第三方 Skill 时不要修改 `vendor/`，而应新增自研策略 Skill 与之组合。升级时先清空 `verified`，更新 `ref` 和哈希，兼容验证通过后再恢复安装。定时检查只报告候选版本，不自动启用。

**tags 用扁平小词表**：写作/图像/图表/编程/调试/测试/架构/规划/研究/运维/协作/教学/翻译/抓取/效率。不搞树状分类——层级会腐烂，标签不会。

### 找 skill：看 CATALOG.md

`install.py` 每次运行都会重新生成 `CATALOG.md`：按 tag 分组，每条一行能力 + 一行边界 + 验证状态。这是给人看的总览，**勿手改**（改了会被覆盖）。三层分工：

- `CATALOG.md`：它是什么、边界在哪（一眼看穿全局）
- [最佳实践记录](best_practices/README.md)：本项目问题、尝试、踩坑与验证；外部 wiki 仅引用或独立综合，不复制正文
- `SKILL.md`：行为本身，要改才看

### 更新第三方 skill

```bash
python3 install.py   # 默认分支拉取最新；带 ref 的登记固定并刷新到该版本
```

上游删除了某个 skill 时，`install.py` 会报 `源目录不存在`——从 lock 里删掉对应条目即可。

### prompt 模板包

Skill 专用模板随包保存；旧 double_layer_spec 已经用户批准清理，不再作为现用模板入口。best_practices 中的历史模板有来源与未验证状态，不冒充真实成功案例。新模板使用对应主题目录：

- 一个主题一个目录，模板文件用 `.prompt.md` / `.prompt.xml` 后缀
- 只放自研内容；收集来的文章/教程不进这里（那是 wiki 的 ingest 范围）

## 维护红线

1. **单份正文**：自研在 tools/skills，第三方新来源只登记并由 vendor 管理；历史迁入快照保留待审、不新增复制。旧路径只允许兼容软链。不得因发现重复就未经确认删除。
2. **第三方只登记不复制**：`skills-lock.json` 是唯一登记处。
3. **登记必写三行人话**：capability / boundary / tags，当场写，不赊账。
4. **未验证不安装**：没填 `verified` 的 skill 不进 agent 加载位置。
5. **目录自动生成**：登记变化运行 install.py --catalog-only；联网同步与全局安装另核授权，不手改 CATALOG.md。
6. **最佳实践按统一规范**：本项目记录按 best_practices/STANDARD.md 构建；研究、项目事实和运行进度不混入记录，外部知识正文不重复迁入。
