# CLAUDE.md

本仓库是 AI Coding 兵工厂：自研 skill 在 `skills/`，第三方 skill 只登记在 `skills-lock.json`，总入口是 `skills.yaml`，安装靠 `python3 install.py`（幂等，改了登记就重跑）。

详细管理与使用规范见 [README.md](README.md)。维护红线：

1. skill 文件只能存在于 `skills/`（自研）或 `vendor/`（第三方，自动管理），不要在其他位置创建副本。
2. 新增第三方 skill 只改 `skills-lock.json`，禁止把文件拷进仓库；登记时必须当场写 capability / boundary / tags 三行人话。
3. 新增自研 skill 放 `skills/` 并在 `skills.yaml` 登记（同样带三行人话）。
4. `verified` 为空的 skill 不会被安装；验证通过才填日期。
5. `CATALOG.md` 由 install.py 自动生成，不要手改。
4. prompt/spec 模板放对应主题目录，用 `.prompt.md` / `.prompt.xml` 后缀。
