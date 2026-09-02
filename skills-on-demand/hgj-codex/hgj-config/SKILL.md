---
name: hgj-config
description: 当用户要求查看或核对 HGJ 内部 Apollo、Nacos、namespace、data-id、配置项、环境差异、数据源配置或服务发现配置时使用。
---

# HGJ Apollo/Nacos 配置查询

统一通过 `agent-tools config` 执行只读抓取。默认只查看与问题相关的最小配置范围。

## 标准流程

```text
列出配置源
  ↓
确认环境、应用和 namespace/data-id
  ↓
用 grep 缩小配置范围
  ↓
对比代码默认值或目标环境
  ↓
输出脱敏差异与影响
```

## 常用命令

```bash
agent-tools config --list
agent-tools config --source <名称> --namespace application --grep "<关键词>"
agent-tools config --source <名称> --namespace application
```

## 安全边界

- 只读查询，不修改、不发布、不回滚配置。
- 优先使用 `--grep`，避免无关配置和秘密进入上下文。
- 命中 `password`、`secret`、`token`、`access-key`、`private-key`、Cookie 等字段时，仅报告“已配置/缺失/疑似不一致”，不输出值。
- 未获明确授权不得操作 beta/prod 配置；本技能本身不提供写配置能力。
- 输出不包含完整数据库连接串、内部域名清单或身份凭证。

## 触发示例

“查 dev 的 Nacos datasource 配置”“比较 Apollo 环境差异”“确认 data-id 是否存在”。

## 反例

不得为了定位一个配置项而直接把整个 namespace 原文写入报告。
