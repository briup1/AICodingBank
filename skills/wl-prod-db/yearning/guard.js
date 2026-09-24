import { ArgumentError } from "@jackwener/opencli/errors";
const WRITE_KEYWORD = /\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|replace|call|load|outfile|dumpfile)\b/i;
function assertSource(source) {
  const name = source.trim();
  if (!name) throw new ArgumentError("\u7F3A\u5C11\u6570\u636E\u6E90");
  if (/rw/i.test(name)) {
    throw new ArgumentError(`\u62D2\u7EDD\u6570\u636E\u6E90 ${name}\uFF1A\u540D\u5B57\u91CC\u5E26 rw`, "\u53EA\u5141\u8BB8\u53EA\u8BFB\u6570\u636E\u6E90\uFF0C\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  }
  return name;
}
function assertReadSql(sql) {
  const trimmed = sql.trim().replace(/;+\s*$/u, "");
  if (!trimmed) throw new ArgumentError("\u7F3A\u5C11 SQL");
  if (trimmed.includes(";")) throw new ArgumentError("\u53EA\u5141\u8BB8\u4E00\u6761 SQL", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  const stripped = trimmed.replace(/\/\*[\s\S]*?\*\//g, " ").replace(/--[^\n]*/g, " ").trim();
  if (!/^select\b/i.test(stripped)) {
    throw new ArgumentError("\u53EA\u5141\u8BB8 SELECT", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  }
  if (WRITE_KEYWORD.test(stripped)) {
    throw new ArgumentError("\u8BED\u53E5\u91CC\u542B\u6709\u5199\u5165\u5173\u952E\u5B57", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  }
  if (!/\blimit\s+\d+\b/i.test(stripped)) {
    throw new ArgumentError("SELECT \u5FC5\u987B\u5E26 LIMIT", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  }
  return trimmed;
}
function tableFromSql(sql) {
  const match = sql.match(/\bfrom\s+[`"]?([a-zA-Z0-9_]+)[`"]?/i);
  return match?.[1] ?? "";
}
export {
  assertReadSql,
  assertSource,
  tableFromSql
};
