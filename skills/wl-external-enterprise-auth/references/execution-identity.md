# 执行身份与授权快照

## 目标

外部登录证明身份，本地系统决定授权；一次业务请求提交后，执行身份不能因为浏览器会话变化而漂移。

```text
External Identity
  -> 本地 Account / User
  -> Enterprise / Tenant
  -> ExecutionSubject
  -> Grant
  -> Request / Job / Run
  -> Worker
```

## 最小对象

| 对象 | 作用 | 事实 Owner |
| --- | --- | --- |
| AuthSession | 本地浏览器登录状态 | 本地认证服务与持久化层 |
| Enterprise / Tenant | 本地业务归属 | 本地业务授权模型 |
| ExecutionSubject | 用户、企业、产品组合后的本地执行 key | 本地主体模型 |
| Grant | 提交时冻结的执行授权 | 本地请求 / 执行模型 |
| Request / Run | 接入意图与执行状态 | 本地请求 / Run repository |
| Worker lease | 当前执行者所有权 | 本地 Run / worker 模型 |

## Grant 至少固定

- 本地用户或产品用户；
- 当前企业 / Tenant；
- 当前产品、Agent 或业务作用域；
- 来源 Session 的引用，而非明文凭证；
- 授权开始、过期和撤销状态；
- 子任务、恢复、排队和重试是否允许继续使用；
- 结果、事件、文件和工具执行的归属。

## 必须拒绝

- 从相邻 Run 猜结果；
- 从当前浏览器 Session 覆盖已提交 Request 的身份；
- 从模型或客户端输入接受执行主体；
- 从内部管理员身份代替产品用户执行；
- 让旧 Grant 因重新登录而复活；
- 让过期、撤销或跨企业 Grant 进入 Worker。

## 适配已有执行链

优先把 Subject 和 Grant 接入已有 Request / Queue / Run / Worker，而不是复制另一套执行状态机。适配完成后至少证明：

1. 数据库提交先于队列投递；
2. Request、Run 和 Worker 使用同一 Subject / Grant；
3. 取消、恢复、重试和子任务的身份边界明确；
4. 事件、结果、文件和工具授权不跨主体泄漏；
5. 失联 Worker 的终态不会被另一个身份静默接管。
