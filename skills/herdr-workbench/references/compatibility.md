# Herdr Workbench 兼容记录

只记录个人策略依赖的版本契约，不复制上游手册。升级 Herdr 或编码 Agent 后，重新读取 CLI help 并更新本表。

| 工具 | 已验证版本 | YOLO 参数 / 契约 | 验证方式 |
| --- | --- | --- | --- |
| Herdr | 0.8.2 | `herdr agent start <name> --kind <kind> --pane <id> -- <native-args>` | `herdr --version`、`herdr agent` |
| Claude Code | 2.1.252 | `--dangerously-skip-permissions` | `claude --version`、`claude --help` |
| Codex | 0.153.0 | `--dangerously-bypass-approvals-and-sandbox` | `codex --version`、`codex --help` |

未知 Agent 类型没有已验证映射时，先运行其 `--help` 查找无审批模式。没有该模式则不启动该类型，改用已验证类型或由当前 Agent完成。

## Herdr 升级检查

```text
发现新版本
  -> 阅读上游 release 与新版 herdr Skill
  -> 把 skills-lock.json 的 herdr.ref 指向候选版本
  -> 清空 herdr.verified
  -> python3 install.py（旧软链接应被移除）
  -> 更新 computedHash
  -> 在 Herdr 会话中验证 start / prompt / wait / read 与 YOLO 参数透传
  -> 更新本表
  -> 填写新的 verified 日期
  -> python3 install.py
```

哈希、入口路径或参数契约不符时保持未验证状态，不覆盖当前策略结论。
