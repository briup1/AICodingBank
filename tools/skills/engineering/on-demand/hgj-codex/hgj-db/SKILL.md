---
name: hgj-db
description: 当用户要求查询 HGJ 内部 MySQL、PostgreSQL、MongoDB、Redis 或 Elasticsearch，核对业务数据、执行只读 SQL 或查看连接和表结构时使用。
---

# HGJ 数据库只读查询

统一使用 `agent-tools db`。该入口固定只读，不尝试绕过只读限制。

## 安全边界

- 默认仅允许 `SELECT`、元数据查看、Mongo 查询、Redis/ES 只读检索。
- 禁止 `INSERT`、`UPDATE`、`DELETE`、DDL、脚本写入、锁表和高成本全表扫描。
- 用户要求写库时停止，优先寻找业务 API、迁移脚本或测试夹具，并取得明确授权。
- 不在回复或报告中展示密码、完整连接串、主机地址、Token 或大批个人数据。
- 查询必须设置合理 `LIMIT`；先按主键、业务键、时间范围缩小范围。

## 标准流程

```text
列出可用连接
  ↓
确认环境和数据源
  ↓
查看表/集合结构
  ↓
构造带范围与 LIMIT 的只读查询
  ↓
核对多表或日志证据
  ↓
输出脱敏结论
```

## 常用命令

```bash
agent-tools db --list
agent-tools db --conn <名称> --tables
agent-tools db --conn <名称> --sql "SELECT * FROM <table> WHERE <condition> LIMIT 10"
```

## 查询纪律

- 用户说“数据不对”时，先明确业务对象、环境、期望值、实际值和时间范围。
- 不根据单表结果立即定因；核对写入链路、状态机、配置和日志。
- 涉及源库与目标库迁移时，源库始终只读，并拒绝源目标同库或身份不明。
- 结果量过大时只返回统计、样例和进一步筛选条件。

## 触发示例

“查 dev 订单状态”“列出可用数据库连接”“核对 Mongo 文档是否迁移完整”。

## 反例

不要把平台连接信息复制到 Skill、代码、HTML 报告或聊天回复中。
