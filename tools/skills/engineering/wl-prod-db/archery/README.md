# opencli archery

生产 Mongo 只读查询。只接受 `prd-mongo` 开头的实例。

- `opencli archery databases --instance prd-mongo6`
- `opencli archery collections --instance prd-mongo6 --database eyun-assist`
- `opencli archery query --instance prd-mongo6 --database eyun-assist --statement 'db.getCollection("freight_rates").find({})' --limit 100`

改 `.ts` 后需要重新生成同目录的 `.js`。
