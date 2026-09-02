---
name: hgj-auth
description: 当 HGJ 内部网站、agent-tools、TAPD MCP、伏羲、数据库或配置平台需要登录、SSO、Cookie、Token、账号认证、凭证初始化或认证故障排查时使用。
---

# HGJ 登录与凭证安全

本技能只描述凭证获取和使用规范，不保存真实凭证。

## 核心规则

- 不要求用户在聊天中粘贴密码、Token、Cookie、Secret、私钥或验证码。
- 不使用会把明文秘密记录进 shell history 的命令参数。
- 优先使用公司 SSO、平台交互式配置、系统密钥环或工具自己的安全凭证存储。
- Skill、AGENTS.md、代码、Git、HTML 报告和日志中只记录变量名或配置状态，不记录值。
- 检查凭证时只能确认文件是否存在、权限是否合理、认证是否成功；不得 `cat`、打印或复制内容。
- 临时下载链接、Session 和 Cookie 视为凭证，同样必须脱敏。

## 处理流程

```text
识别目标平台
  ↓
运行平台状态/doctor 检查
  ↓
凭证已配置？── 是 ──> 执行最小只读连通测试
  │
  否
  ↓
让用户在本地交互式配置
  ↓
重新运行 doctor/状态检查
```

## 推荐检查

### agent-tools

```bash
agent-tools fuxi --check
agent-tools db --list
agent-tools config --list
```

### TAPD MCP

```bash
hgj mcp status tapd --format json
hgj mcp configure tapd
hgj mcp doctor tapd --format json
hgj mcp install tapd --agent codex
```

`configure` 由用户在本机交互完成。注册 MCP 后通常需要重启 Agent 才能在新会话加载工具。

## 凭证存储优先级

```text
公司 SSO / 凭证代理
  ↓
系统密钥环或工具安全存储
  ↓
权限 0600 且不入 Git 的本机配置
  ↓
进程级环境变量
```

## 认证失败排查

- 区分未配置、已过期、权限不足、网络不可达和目标资源不存在。
- 不通过关闭 TLS 校验、扩大权限或共享他人账号解决认证问题。
- 需要人工登录或 MFA 时，明确提示用户在本机完成，再继续验证。

## 触发示例

“伏羲提示凭证失效”“配置 TAPD Token”“内部网站需要 Cookie 才能访问”。

## 反例

不得读取 `~/.codex/auth.json` 或其他凭证文件内容来判断是否配置成功。
