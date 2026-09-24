# opencli yearning

生产环境 Yearning 的只读查询插件。用法见上一级 `SKILL.md`。

- `opencli yearning apply`：查询时限不在时提交说明「工作需要」；时限还在则跳过。
- `opencli yearning query`：只执行一条带 LIMIT 的 SELECT。默认源 `mysql|奇点-ro`，库 `compass-freight`。

名字里带 `rw` 的源、非 SELECT、没有 LIMIT 的语句会在发出请求前拒绝。

改 `.ts` 后需要重新生成同目录的 `.js`，OpenCLI 实际加载的是 `.js`。
