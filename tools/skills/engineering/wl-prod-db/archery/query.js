import { cli, Strategy } from "@jackwener/opencli/registry";
import { assertDatabase, assertInstance, assertLimit, assertStatement } from "./guard.js";
import { archeryFetch, openArchery } from "./api.js";
cli({
  site: "archery",
  name: "query",
  access: "read",
  description: "\u5728\u751F\u4EA7 Mongo \u4E0A\u6267\u884C\u4E00\u6761 find \u6216 count\uFF0C\u8FD4\u56DE\u884C\u6570\u53D7 --limit \u9650\u5236\u3002",
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: "json",
  defaultWindowMode: "background",
  args: [
    { name: "instance", required: true, help: "\u5B9E\u4F8B\u540D\uFF0C\u5FC5\u987B prd-mongo \u5F00\u5934" },
    { name: "database", required: true, help: "\u6570\u636E\u5E93\u540D" },
    { name: "statement", required: true, help: '\u4E00\u6761 Mongo \u53EA\u8BFB\u8BED\u53E5\uFF0C\u4F8B\u5982 db.getCollection("x").find({})' },
    { name: "limit", type: "number", default: 100, help: "\u8FD4\u56DE\u884C\u6570\uFF0C1 \u5230 1000\uFF0C\u9ED8\u8BA4 100" }
  ],
  columns: ["instance", "database", "statement", "limit", "row_count", "query_time"],
  validateArgs: (kwargs) => {
    kwargs.instance = assertInstance(String(kwargs.instance ?? ""));
    kwargs.database = assertDatabase(String(kwargs.database ?? ""));
    kwargs.statement = assertStatement(String(kwargs.statement ?? ""));
    kwargs.limit = assertLimit(kwargs.limit);
  },
  func: async (page, kwargs) => {
    const instance = String(kwargs.instance);
    const database = String(kwargs.database);
    const statement = String(kwargs.statement);
    const limit = Number(kwargs.limit);
    await openArchery(page);
    const result = await archeryFetch(page, "/query/", {
      instance_name: instance,
      db_name: database,
      schema_name: "",
      tb_name: "",
      sql_content: statement,
      limit_num: String(limit)
    });
    const payload = result.data ?? {};
    const columns = Array.isArray(payload.column_list) ? payload.column_list.map(String) : [];
    const rawRows = Array.isArray(payload.rows) ? payload.rows : [];
    const rows = rawRows.map((row) => {
      const item = {};
      columns.forEach((column, index) => {
        item[column] = row?.[index];
      });
      const whole = item.mongodballdata;
      if (typeof whole === "string" && whole) {
        try {
          item.document = JSON.parse(whole);
        } catch {
          item.document = whole;
        }
      }
      return item;
    });
    return [{
      instance,
      database,
      statement,
      limit,
      row_count: rows.length,
      query_time: payload.query_time ?? "",
      rows
    }];
  }
});
