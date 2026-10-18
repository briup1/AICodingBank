import { cli, Strategy } from "@jackwener/opencli/registry";
import { assertReadSql, assertSource, tableFromSql } from "./guard.js";
import { openYearning, yearningFetch } from "./api.js";
const DEFAULT_SOURCE = "mysql|\u5947\u70B9-ro";
const DEFAULT_DATABASE = "compass-freight";
const DEFAULT_SQL = "select * from hot_ports_dict limit 10";
cli({
  site: "yearning",
  name: "query",
  access: "read",
  description: "\u5BF9\u53EA\u8BFB\u6570\u636E\u6E90\u6267\u884C\u4E00\u6761\u5E26 LIMIT \u7684 SELECT\uFF0C\u8FD4\u56DE\u8868\u540D\u3001SQL \u548C\u884C\u6570\u636E\u3002",
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: "json",
  defaultWindowMode: "background",
  args: [
    { name: "source", default: DEFAULT_SOURCE, help: "\u6570\u636E\u6E90\uFF0C\u9ED8\u8BA4 mysql|\u5947\u70B9-ro\u3002\u540D\u5B57\u91CC\u5E26 rw \u4F1A\u62D2\u7EDD\u3002" },
    { name: "database", default: DEFAULT_DATABASE, help: "\u5E93\u540D\uFF0C\u9ED8\u8BA4 compass-freight" },
    { name: "sql", default: DEFAULT_SQL, help: "\u4E00\u6761 SELECT\uFF0C\u5FC5\u987B\u5E26 LIMIT" }
  ],
  columns: ["table", "sql", "source", "database", "row_count"],
  validateArgs: (kwargs) => {
    kwargs.source = assertSource(String(kwargs.source ?? ""));
    kwargs.sql = assertReadSql(String(kwargs.sql ?? ""));
    kwargs.database = String(kwargs.database ?? "").trim();
    if (!kwargs.database) throw new Error("\u7F3A\u5C11\u5E93\u540D");
  },
  func: async (page, kwargs) => {
    const source = String(kwargs.source);
    const database = String(kwargs.database);
    const sql = String(kwargs.sql);
    await openYearning(page);
    const current = await yearningFetch(page, "PUT", "/api/v2/query/status");
    if (Number(current.payload?.status) !== 1) {
      throw new Error("\u67E5\u8BE2\u65F6\u9650\u4E0D\u5728\u3002\u5148\u8FD0\u884C opencli yearning apply");
    }
    const result = await yearningFetch(page, "POST", "/api/v2/query/results", {
      sql,
      data_base: database,
      source
    });
    const payload = result.payload;
    if (!payload || payload.status) {
      throw new Error("\u67E5\u8BE2\u65F6\u9650\u5DF2\u8FC7\u671F\u6216\u67E5\u8BE2\u88AB\u62D2\u7EDD\u3002\u5148\u8FD0\u884C opencli yearning apply");
    }
    const rows = Array.isArray(payload.data) ? payload.data : [];
    return [{
      table: tableFromSql(sql),
      sql,
      source,
      database,
      row_count: rows.length,
      rows
    }];
  }
});
