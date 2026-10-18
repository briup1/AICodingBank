---
name: hgj-fuxi
description: 当用户要求定位 HGJ 内部服务、查看伏羲 K8s 状态、Pod、Loki 日志、日志上下文、容器进程或使用 Arthas 诊断时使用。
---

# HGJ 伏羲诊断

通过 `agent-tools fuxi` 执行非生产环境的服务定位和远程诊断。

## 环境边界

- 仅允许：`dev`、`dev2`、`beta`、`beta2`。
- 禁止：`prod`、`uat`、`hwtx`、`oversea` 和未知环境。
- 不执行服务构建、发布、扩缩容、重启、企微通知或其他状态变更。
- Arthas 部署属于动态诊断；先说明目标类、方法、采样次数和影响，获得用户明确授权后再执行。

## 标准流程

```text
确认环境与服务
  ↓
查询服务/Pod 状态
  ↓
按时间范围检索日志
  ↓
读取异常前后文
  ↓
仍无证据？── 是 ──> 经授权使用 Arthas 验证
  ↓
输出根因、证据和影响范围
```

## 常用命令

```bash
agent-tools fuxi --check
agent-tools fuxi --list-envs
agent-tools fuxi --refresh-services --env dev
agent-tools fuxi --service <name> --env dev --detail
agent-tools fuxi --service <name> --env dev --logs --grep "ERROR" --minutes 30
agent-tools fuxi --service <name> --env dev --logs --start "<ISO时间>" --end "<ISO时间>" --json
agent-tools fuxi --service <name> --env dev --log-context "<timestampNs>" --labels '<labels JSON>' --before 50 --after 50 --json
agent-tools fuxi --service <name> --env dev --pod <pod> --diagnostic processes
```

Arthas 经授权后使用：

```bash
agent-tools fuxi --service <name> --env dev --pod <pod> --arthas "sc *关键词*"
agent-tools fuxi --service <name> --env dev --pod <pod> --arthas-deploy "watch <class> <method> '{params,returnObj}' -x 3 -n 5"
agent-tools fuxi --service <name> --env dev --pod <pod> --arthas-fetch
agent-tools fuxi --service <name> --env dev --pod <pod> --arthas-stop
```

## 诊断纪律

- 报错是现象，沿调用链、参数、配置和数据继续追到原因。
- 日志必须看上下文，不能只返回 grep 命中行。
- 没有日志不代表请求未到达；必要时用低采样 Arthas 验证。
- 输出中隐藏身份头、Cookie、Token、数据库地址和个人信息。

## 触发示例

“看 dev 的订单服务错误日志”“确认请求有没有进入 Controller”“用 Arthas 看 beta2 方法参数”。

## 反例

不得因为用户只说“线上有问题”就尝试生产环境；先确认允许的非生产环境或仅做代码分析。
