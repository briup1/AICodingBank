---
name: wl-prod-db
description: 查询海管家生产环境数据库时使用。用户提到线上库、生产库、Yearning、Archery、MySQL、Mongo、奇点-ro、prd-mongo、集合或 find 时触发。MySQL 走 opencli yearning，Mongo 走 opencli archery，不使用 agent-tools 查生产。
version: 0.2.0
---

# wl-prod-db

海管家线上数据库查询。

生产 MySQL 和生产 Mongo 是两扇门。先看用户要查的是哪一种，再调用对应命令。开发环境日志、Pod、Arthas 走 `agent-tools fuxi`，不要用它查生产库。

## 先判断

1. 用户说表、`SELECT`、`奇点-ro`、Yearning：走 MySQL。
2. 用户说集合、`find`、`prd-mongo`、Archery：走 Mongo。
3. 没说清是 MySQL 还是 Mongo：先问一句，不要两边都查。
4. 数据源名字里带 `rw`、实例不是 `prd-mongo` 开头、语句不是只读：直接拒绝，不要改写后偷偷执行。

## MySQL

查询时限不在时先申请。时限还在就跳过，不要重复提交：

```bash
opencli yearning apply -f json
```

申请只提交说明「工作需要」。环境保持「生产环境」，审核人保持页面原值。

然后查询。不传参数就是默认源 `mysql|奇点-ro`、默认库 `compass-freight`、默认 SQL `select * from hot_ports_dict limit 10`：

```bash
opencli yearning query -f json
```

只允许一条带 `LIMIT` 的 `SELECT`。

## Mongo

先确认实例和库。不知道名字时再列：

```bash
opencli archery databases --instance prd-mongo6 -f json
opencli archery collections --instance prd-mongo6 --database eyun-assist -f json
```

查询：

```bash
opencli archery query --instance prd-mongo6 --database eyun-assist --statement 'db.getCollection("freight_rates").find({})' --limit 100 -f json
```

只允许 `find`、`findOne`、`count`、`countDocuments`、`aggregate`、`distinct`。`--limit` 默认 100，最大 1000。不要传 0，那是页面上的 max。


## 没给表名

用户只说想要什么数据、没给表名时，先读 `references/compass-platform-tables.md` 里「运行代码会读写」那一节。不要读「只在迁移或历史脚本里出现」。

1. 只命中一张表，才用现有只读命令去查。MySQL 仍走 `opencli yearning query`，Mongo 仍走 `opencli archery query`。
2. 命中多张就停下，把候选表的引擎、库、表名列出来，不要查。
3. 一张都没命中就停下。不要列全库，也不要猜表名。
4. 对照里写了「查询入口未核实」的实例，不要拿去查生产。compass-platform 的库是 `compass-freight`。不要把本文件示例里的 `prd-mongo6`、`eyun-assist` 套到这个项目上。

## 结果

把 JSON 里的实例或源、库、语句、`row_count` 和行交给用户。MySQL 若提示查询时限不在，先跑 `opencli yearning apply`，再查一次。
