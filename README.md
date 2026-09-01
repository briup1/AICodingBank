# AICodingBank

AI Coding 兵工厂：统一管理**自研 skill、第三方 skill 登记、prompt 模板包**，一键同步到任意机器的 agent 加载位置。

与知识库（weilan-knowledge-wiki）的分工：**这里管"能不能装上、能不能跑"，wiki 管"是什么、好不好用"**。skill 文件永不进 wiki；wiki 只为值得长期使用的 skill 建 entity 页记录使用经验。

## 目录结构

```
├── skills/              # 自研 skill 本体与生成式 Skill Pack（git 跟踪，你是上游）
├── skills.yaml          # 总登记表：加载位置 + 自研清单 + lock 指针
├── skills-lock.json     # 第三方 skill 登记（只登记上游地址，不复制文件）
├── install.py           # 安装器：clone 上游到 vendor/ → 软链到各加载位置
├── vendor/              # 第三方上游的 clone 缓存（gitignore，勿手动改）
├── ai_coding_sec_dev_workflow/   # 自研 prompt 模板包
├── best_practices/               # 自研 prompt 模板包
├── double_layer_spec/            # 自研 spec 模板
└── claudecode_guide/             # 自研使用指南
```

## 日常使用

### 新机器 / 同步环境

```bash
git clone <本仓库地址> && cd AICodingBank
python3 install.py
```

跑完后所有 skill 以软链形式出现在 `~/.agents/skills` 和 `~/.claude/skills`（在 `skills.yaml` 的 `targets` 里增减加载位置）。

### 添加自研 skill

1. 在 `skills/<skill-name>/` 下开发，`SKILL.md` 必填
2. 在 `skills.yaml` 的 `self:` 下加一行：

```yaml
  - name: my-new-skill
    path: skills/my-new-skill
```

3. `python3 install.py` 建立软链，git commit

改进自研 skill = 直接改 `skills/` 里的文件，软链即时生效，commit 即版本化。

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
skills/<framework>-pack/
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

**verified 闸门**：`verified` 为空的 skill 只登记、只进目录，**不会被软链到加载位置——agent 根本看不到它**。你在实际项目里用过一次确认靠谱，填上日期（如 `"2026-08-23"`），重跑 `install.py`，它才进入 agent 的视野。agent 的可选集合 = 你的信任集合。

**tags 用扁平小词表**：写作/图像/图表/编程/调试/测试/架构/规划/研究/运维/协作/教学/翻译/抓取/效率。不搞树状分类——层级会腐烂，标签不会。

### 找 skill：看 CATALOG.md

`install.py` 每次运行都会重新生成 `CATALOG.md`：按 tag 分组，每条一行能力 + 一行边界 + 验证状态。这是给人看的总览，**勿手改**（改了会被覆盖）。三层分工：

- `CATALOG.md`：它是什么、边界在哪（一眼看穿全局）
- wiki entity 页：深度使用经验、踩坑（只给值得长期用的建）
- `SKILL.md`：行为本身，要改才看

### 更新第三方 skill

```bash
python3 install.py   # 默认分支拉取最新；带 ref 的登记固定并刷新到该版本
```

上游删除了某个 skill 时，`install.py` 会报 `源目录不存在`——从 lock 里删掉对应条目即可。

### prompt 模板包

`ai_coding_sec_dev_workflow/`、`best_practices/`、`double_layer_spec/` 这类**不可被 agent 直接加载**的 prompt/spec 模板，按主题目录存放，使用时复制内容到目标项目。规则：

- 一个主题一个目录，模板文件用 `.prompt.md` / `.prompt.xml` 后缀
- 只放自研内容；收集来的文章/教程不进这里（那是 wiki 的 ingest 范围）

## 维护红线

1. **skill 文件只有两个合法居所**：自研的在 `skills/`，第三方的在 `vendor/`（install.py 自动管理）。任何其他位置的 skill 副本都是腐烂源头，发现即删。
2. **第三方只登记不复制**：`skills-lock.json` 是唯一登记处。
3. **登记必写三行人话**：capability / boundary / tags，当场写，不赊账。
4. **未验证不安装**：没填 `verified` 的 skill 不进 agent 加载位置。
5. **改了登记就跑 `install.py`**：它是幂等的，随时可重跑，同时刷新 CATALOG.md。
6. 使用经验、踩坑、评测写在 wiki 的 entity 页，不写在这里。
