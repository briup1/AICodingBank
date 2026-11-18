# 0006 交付验收记录

日期：2026-10-20。批准来源：本会话用户结构化选择“批准并实施（推荐）”。实现版本：v2，独立聚焦复核无剩余需求内阻断。状态：核心持久复用路径已交付；真实整机重启与人工补登全链未实测，不宣称全部条件性用例通过。

## 结果与使用入口

唯一方法入口：[Playwright 测试登录](../../../tools/integrations/playwright-auth/README.md)。工作台使用入口与工具接入导航已增加指针，本机配置指针在 Git 忽略的 WORKBENCH.local.md。没有新增或全局安装 Skill，没有改写现有 at-test / hgj-session 默认行为。

```text
Agent 找固定入口
  → 读取本机授权和持久状态
  → 新启动 headless 浏览器及独立 Context
  → 真实身份、预期账号与企业验证
      ├─ 有效：交给显式引用 fixture 的可信 spec
      └─ 无状态/失效/错身份/环境异常：分类停止
  → 用例完成，关闭本次创建的资源
```

本机已保存获准 HGJ client / Beta 必要状态，目录0700/文件0600，无密码库读取或认证数据输出；这是本机私密明文，不是加密保险箱，同系统账号下的程序仍可读取。运行时与浏览器路径仅本机配置；当前复用已有 npm 缓存的 Playwright 1.63.0 与匹配 Chromium1243，无新增依赖。缓存若被清理，入口明确返回 RUNTIME_UNAVAILABLE，需要人工配置另一条已安装且已验证路径，不自动安装。

## 实际验收与边界

| 用例/目标 | 结论 | 证据与限制 |
| --- | --- | --- |
| TC-A01 首次获准保存 | 通过当前源导入路径 | 用户已确认的专用源 A，真实身份比对后，在独立浏览器恢复验证成功才保存；bootstrap.json=SAVED。交互首次登录命令全链未测 |
| TC-A02 源进程结束后恢复 | 核心恢复通过；全新 Agent 发现性仅静态核对 | 负责人核实源 A 归属后关闭，确认PID退出，新Node CLI检查PASS，1473ms，sourceCdpUsed=false，Context关闭1/1。不依赖旧端口。未另起完全无上下文 Agent 验证导航发现 |
| TC-A03 整机重启 | 待用户后续验证 | 没有让机器关机/重启，不用新进程冒充 |
| TC-B01 无状态/损坏/失效 | 本地负例部分通过 | 夹具及真实本地runner缺状态门禁验证通过；真实人工补登/取消/超时窗口链未实测，未在Beta造过期/撤权 |
| TC-B02 错身份/缺标识/环境异常 | 本地夹具通过 | 独立复跑身份字段缺失、账号/企业不符、未知环境、401/403及服务故障；登录跳转无身份请求归LOGIN_REQUIRED，网络故障仍SERVICE_UNAVAILABLE |
| TC-B03 授权、文件边界与收尾 | 已覆盖直接路径；非全故障覆盖 | consent拒绝先于读取状态、权限/owner/symlink拒绝、原子失败保留旧文件；实际metadata通过。CLI不清理已有调用者目录；只删除自己刚创建的临时runner输出。不覆盖同系统账号恶意并发攻击或全部存储故障 |
| TC-C01 连续三次 | 通过 | serial-three.json，3/3 Context验证/关闭，6248ms |
| TC-C02 两路身份只读并发 | 身份恢复并发通过；关闭一方不影响另一方未专门取证 | parallel-two.json，2/2验证/关闭，3034ms；不是查价并发，不是压力测试 |
| 原生 Test runner 正常入口 | 通过 | v2 fixture-run.json：PASS，identity.spec.mjs，发现1、完成1；账号企业门禁后才进入正文 |
| 普通spec迁移误配/门禁失败 | 独立本地runner通过 | expect-only+旧helper CLI拒绝；合法fixture缺状态STATE_MISSING，正文进入次数0；不是仅函数callback自测 |

真实页面检查全部仅身份和页面可用性，无查价、消息或业务提交；只读检查拦截非读初始化请求。测试已创建资源均收尾，源A也已由负责人按任务收尾关闭；不关闭日常Chrome。没有提交、推送、全局安装或部署。

## 独立复核

v1发现两个阻断：任意fixture import被误认为门禁已接入、可信登录跳转被误分流服务故障。v2已修复，并对照本地真实runner和失败夹具复核：无剩余阻断。

独立v2复跑：11 tests / 11 pass / 0 fail / 0 skipped；11个.mjs/.cjs语法检查通过。并非全库测试，不把未运行场景标通过。

支持的spec合同有意收窄：首句直接从共用fixture导入未别名的test（可同时expect），直接注册test，不允许额外import/helper等形式。普通误配会明确拒绝；不是不可信JS沙箱，也不支持任意旧spec无改动迁移。项目测试必须显式接入共用fixture；登录保存不构成未来业务写操作授权。

## 重启后的最小操作

本机路径固定入口：

```sh
node /Users/ziyun/workdir/self_project/AICodingBank/tools/integrations/playwright-auth/cli.mjs check
```

有效返回PASS后，按README选择可信spec运行。登录明确失效时，在交互终端使用同入口login并手动完成登录和企业选择，再验证；不是自动代填密码。人工补登程序已实现但完整交接链未验收，若阻断应报告，不承诺永久免登。

TC-A03实际完成前记录为待验证：登录仍有效且重启后无人工登录、身份相符才算整机重启免登通过；若确实过期，补登分流成功不等于重启免登通过。

## 可复核证据（不含凭证）

以下目录在本机，不复制真实认证状态到仓库：

- 根证据：`/Users/ziyun/.local/state/web-task/runs/playwright-auth-persistent-20261020/`。
- 最终交付及哈希：`v2/DELIVERY.md`、`v2/freeze-manifest.json`。
- 最终本地测试：`v2/unit-final.log`，正常runner：`v2/fixture-run.json`。
- 独立复核：`review/REVIEW.md`（历史失败保留）、`review/REVIEW-v2.md`（修复后通过）。
- 直接恢复：`new-process-check.json`；连续：`serial-three.json`；并发：`parallel-two.json`。
- 旧源退出：`source-a-closed.json`；退出后恢复：`after-source-exit-check.json`。

范围外：其他站点/admin、跨设备、永久免登、真实撤权/故障注入、业务查价和全库Review。
