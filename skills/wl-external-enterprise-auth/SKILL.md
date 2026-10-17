---
name: wl-external-enterprise-auth
description: 为独立项目接入外部企业账号体系，并把外部身份安全映射为本地会话、企业归属、执行主体和授权快照。用户提出“接入公司账号”“对接企业 SSO”“复用海管家身份”“外部身份登录”或跨项目复用企业认证时使用。
tags:
  - 身份认证
  - 企业集成
  - 安全
  - 架构
  - 跨项目复用
metadata:
  version: "0.1.0"
  maturity: "validated-by-yuxi-reference"
---

# 外部企业身份接入

## 目标

把外部企业系统的身份证明接入一个独立项目，同时保持本项目自己的会话、企业归属、权限和执行链。

核心链路：

```text
外部登录 / 强制重新认证
  -> 一次性 callback
  -> 校验 state、binding、provider 和有效期
  -> 核验外部身份
  -> 建立本地 AuthSession
  -> 映射本地 Enterprise / Tenant
  -> 生成 ExecutionSubject 和执行 Grant
  -> 接入本项目自己的 Request / Job / Run / Worker
```

外部账号只证明“用户是谁”；本项目负责“这个用户在本项目中能做什么”。

## 何时使用

当用户要求以下任一事项时加载本 Skill：

- 给独立项目接入海管家或其他公司的账号体系；
- 接入企业 SSO、公司登录、外部身份核验或跨域 callback；
- 让外部用户进入本项目自己的产品、租户或业务空间；
- 把一次外部登录安全传递到后台任务、Agent、Job 或 Worker；
- 将已经验证的企业身份接入另一个独立项目。

## 先做什么

1. 读取目标项目的 `AGENTS.md`、`README`、架构、认证、权限和后台执行文档。
2. 确认目标项目已有的本地对象：Account、User、Tenant、Session、Job、Run、Worker 和权限 Owner。
3. 阅读 `references/provider-contract.md`，向外部系统确认登录、logout、callback、身份核验和撤销契约。
4. 阅读 `references/security-checklist.md`，先列出负向案例；不能只以“登录成功”作为完成标准。
5. 判断目标项目是否有本地执行主体和授权快照。没有时先建立最小本地模型，不把外部 `user_id` 直接当作所有业务表的身份。

## 不变量

### 身份分层

```text
External Identity  外部系统证明的身份
AuthSession        本项目自己的网页登录状态
Enterprise/Tenant  本项目确认的业务归属
ExecutionSubject   一次请求代表的本地执行主体
Grant              一次执行冻结的授权快照
```

禁止以下替代：

- 外部 `user_id` 直接作为本地管理员身份；
- 外部企业部门直接作为本项目租户；
- 请求体、Header 或 Cookie 中的 `user_id` / `enterprise_id` 覆盖服务端核验结果；
- 每次 Worker 执行时重新读取当前 Session，导致已提交任务换身份；
- 用平台内部共享权限代替产品或租户授权。

### 认证事务

登录开始时固定服务端生成的 callback 和 provider。callback 必须校验：

- 一次性、随机、短期有效的 state；
- 浏览器或请求上下文 binding；
- provider 与登录事务一致；
- callback 来源和 redirect 目标符合服务端固定契约；
- 成功消费前后的有效期；
- 重放、错误 binding、错误来源和 CSRF。

普通登录和显式重新认证分开：普通登录可以复用已有 SSO；显式重新认证只能使用外部系统确认过的 logout 或强制认证入口，不能靠清理本地 Cookie 冒充上游登出。

### 会话与凭证

外部凭证不能直接作为本项目 Cookie。推荐链路：

```text
外部凭证
  -> 服务端核验
  -> 本地 Session Cookie
  -> 本地 Session hash + 加密凭证（如确有后台调用需要）
```

不把凭证写入 URL、日志、异常、前端 localStorage、测试快照或普通业务消息。只保存完成业务所需的最小身份字段。

### 执行一致性

请求提交时创建或引用本地 `ExecutionSubject`，并生成不可变 `Grant`，至少固定：

```text
本地用户
当前企业 / 租户
当前产品 / 业务作用域
授权来源 Session
有效期和撤销状态
```

后续 Request、队列消息、Job / Run、Worker、事件和结果必须沿用同一主体和 Grant。Session 轮换、企业切换或产品配置变化不能静默改变已提交任务的身份。

## Provider 适配

通用层只依赖 Provider 接口，不把某一家公司的 URL、字段名或 Token 交接方式写死：

```python
class IdentityProvider:
    async def build_login_url(self, *, state: str, callback_url: str) -> str: ...
    async def build_reauthentication_url(self, *, state: str, callback_url: str) -> str: ...
    async def exchange_callback(self, callback: object) -> object: ...
    async def fetch_identity(self, credential: object) -> object: ...
    async def validate_identity(self, identity: object) -> object: ...
```

Provider 只负责外部协议适配和最小可信身份输出；本地 Session、Tenant、Subject、Grant 和业务授权由目标项目拥有。

实现 Provider 前先完成契约表，不要凭猜测填写字段或接口。Provider 资料单独保存，避免污染通用 Skill。

## 授权与失败

外部身份核验成功不等于本项目授权成功。至少分别判断：

```text
身份可信
  -> 企业有效
  -> 用户可使用本项目
  -> 当前产品 / 租户允许该用户
  -> 当前动作允许
```

上游不可用、身份格式异常、企业缺失、产品停用、Session 失效、Grant 过期和工具未授权都应显式失败，不自动降级为内部管理员或普通账号。

## 最小交付物

每次接入至少交付：

1. Provider contract：登录、logout、callback、核验、字段和失败契约；
2. 本地身份模型：Session、Enterprise/Tenant、Subject、Grant 的 Owner；
3. 正常链路：登录、回调、本地会话、业务入口和后台执行；
4. 负向测试：见 `references/testing-matrix.md`；
5. 凭证与日志检查：证明敏感值不进入 URL、日志、错误和持久化明文；
6. 文档决策：说明外部身份、本地身份和执行授权的边界；
7. 未验证范围：明确真实账号、跨企业、撤权、上游故障和 Worker 生命周期哪些尚未验证。

## 停止条件

遇到以下情况先停止并请求确认，不自行补造协议：

- 外部系统没有确认的 callback 或 logout 契约；
- 需要读取、保存或传递真实凭证但安全通道未确定；
- 需要修改外部企业权限、账号、配置或生产数据；
- 目标项目没有明确的本地授权 Owner；
- 无法证明 Request 到 Worker 的身份一致性；
- 只能通过关闭安全校验或把外部账号映射成管理员才能继续。

## 参考实现

Yuxi 是本 Skill 的第一个真实参考实现。参考它的边界和测试证据，不复制 Yuxi 的业务表、产品页面、知识库工具或内部管理权限模型。

- `references/provider-contract.md`
- `references/security-checklist.md`
- `references/execution-identity.md`
- `references/testing-matrix.md`
