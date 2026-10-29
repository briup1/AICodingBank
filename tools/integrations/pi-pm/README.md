# Pi 项目经理初始化 /pm

使用 Pi 原生 prompt template，不增加扩展进程或新 Skill。唯一正文是本目录 pm.md，本机入口通过软链接引用。

```text
输入 /pm → 读取项目经理身份和最小协作资料 → 显示真实加载回执 → 等待需求
```

本机接入：`/Users/ziyun/.pi/agent/prompts/pm.md` 指向本目录 pm.md。新 Pi 会话自动发现；已有会话先 `/reload`，再输入 `/pm`。如果会话使用 `--no-prompt-templates`，需要先恢复模板加载。其他扩展若注册同名命令会优先处理，应检查冲突。

初始化不创建执行者、不修改模型、不清空上下文，也不自动执行需求。岗位规则只引用 roles/project-manager/ROLE.md，不复制维护。缺必要手册时显示初始化未完成。

初始化不检查 Herdr 环境、不查询命令帮助或实例列表、不重命名 Tab；只有实际任务需要委派时才检查执行环境。输入 /pm 后应直接完成必要资料读取与身份回执，然后等待需求。

模板含本机工作台绝对路径，迁移机器时需核对路径。安装只涉及此单个模板，不运行全局 Skill 安装器。

依据：当前安装 Pi 的 docs/prompt-templates.md：用户目录 prompts/*.md 文件名成为命令名；活动会话使用 /reload 重载。
