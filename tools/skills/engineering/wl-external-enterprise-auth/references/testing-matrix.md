# 测试矩阵

## P0：认证事务

- 普通登录使用固定 provider 入口。
- 显式重新认证使用已确认的 logout / 强制认证入口。
- 正确 callback 建立本地 Session。
- 错误 state、过期 state、错误 binding、错误 provider 和 callback 重放均拒绝。
- 错误 Origin、CSRF 和非法 redirect 均拒绝。
- 旧 Cookie 在会话轮换或注销后失效。

## P0：身份与授权

- 外部身份响应缺失用户 ID 时拒绝。
- 外部企业 ID 类型错误或缺失时按产品规则拒绝。
- 请求体、Header 和 URL 中伪造 user / enterprise / tenant 不能改变可信身份。
- 禁用产品、未知产品、跨企业和跨产品访问均拒绝。
- 普通内部用户不能通过产品 Cookie 访问产品数据，产品用户不能反向获得内部管理权限。

## P0：执行一致性

- Request 持久化成功后才投递队列。
- Request、Run、Worker 和结果绑定同一 Subject / Grant。
- 重新登录、切企业和 Session 注销不会改写已经提交的 Run 身份。
- 过期或撤销 Grant 不能继续执行；恢复、重试、父子任务的延续规则有测试。
- 事件、消息、文件、Tool 审计和最终结果不能跨 Run 或跨企业读取。

## P1：凭证与失败

- 凭证不出现在 URL、日志、异常、响应、fixture、截图和普通消息。
- 外部网络失败不会伪装成用户密码错误。
- 上游不可用、身份格式错误和本地配置错误均显式失败，不静默降级。
- 旧凭证和失效会话在正确清理后无法恢复。

## 证据要求

优先级从低到高：

```text
静态检查
  -> unit 负向测试
  -> 真实 PostgreSQL / 持久化测试
  -> 真实 HTTP callback
  -> worker / queue / 文件副作用测试
  -> 浏览器和目标环境验收
```

不能用 mock 调用次数、单个 HTTP 200 或模型口头回答代替最终事实。每个未运行的层级都要写明原因和剩余风险。
