# AICodingBank

AI Coding 兵工厂：统一管理**自研 skill、第三方 skill 登记、prompt 模板包**，一键同步到任意机器的 agent 加载位置。

与知识库（weilan-knowledge-wiki）的分工：**这里管"能不能装上、能不能跑"，wiki 管"是什么、好不好用"**。skill 文件永不进 wiki；wiki 只为值得长期使用的 skill 建 entity 页记录使用经验。

## 目录结构

```
├── skills/              # 自研 skill 本体（git 跟踪，你是上游）
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

### 收藏第三方 skill

**不要把文件拷进仓库。** 只在 `skills-lock.json` 的 `skills` 里加一条登记：

```json
"some-skill": {
  "source": "owner/repo",
  "sourceType": "github",
  "skillPath": "path/to/SKILL.md",
  "computedHash": ""
}
```

然后 `python3 install.py` 会自动 clone 上游到 `vendor/` 并软链出去。

### 更新第三方 skill

```bash
python3 install.py   # 重跑即 pull 所有上游到最新
```

上游删除了某个 skill 时，`install.py` 会报 `源目录不存在`——从 lock 里删掉对应条目即可。

### prompt 模板包

`ai_coding_sec_dev_workflow/`、`best_practices/`、`double_layer_spec/` 这类**不可被 agent 直接加载**的 prompt/spec 模板，按主题目录存放，使用时复制内容到目标项目。规则：

- 一个主题一个目录，模板文件用 `.prompt.md` / `.prompt.xml` 后缀
- 只放自研内容；收集来的文章/教程不进这里（那是 wiki 的 ingest 范围）

## 维护红线

1. **skill 文件只有两个合法居所**：自研的在 `skills/`，第三方的在 `vendor/`（install.py 自动管理）。任何其他位置的 skill 副本都是腐烂源头，发现即删。
2. **第三方只登记不复制**：`skills-lock.json` 是唯一登记处。
3. **改了登记就跑 `install.py`**：它是幂等的，随时可重跑。
4. 使用经验、踩坑、评测写在 wiki 的 entity 页，不写在这里。
