import { ArgumentError } from "@jackwener/opencli/errors";
const WRITE = /\.(insert|insertOne|insertMany|update|updateOne|updateMany|delete|deleteOne|deleteMany|remove|drop|save|replaceOne|findOneAndUpdate|findOneAndDelete|findOneAndReplace|bulkWrite)\s*\(/i;
const READ = /^db(?:\.getCollection\s*\(\s*['\"][^'\"]+['\"]\s*\)|\.[A-Za-z0-9_-]+)\s*\.\s*(findOne|find|countDocuments|count|aggregate|distinct)\s*\(/i;
function assertInstance(instance) {
  const name = instance.trim();
  if (!name.startsWith("prd-mongo")) {
    throw new ArgumentError(`\u62D2\u7EDD\u5B9E\u4F8B ${name || "(\u7A7A)"}\uFF1A\u53EA\u5141\u8BB8 prd-mongo \u5F00\u5934`, "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  }
  return name;
}
function assertDatabase(database) {
  const name = database.trim();
  if (!name) throw new ArgumentError("\u7F3A\u5C11\u6570\u636E\u5E93", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  return name;
}
function assertStatement(statement) {
  const trimmed = statement.trim().replace(/;+\s*$/u, "");
  if (!trimmed) throw new ArgumentError("\u7F3A\u5C11\u67E5\u8BE2\u8BED\u53E5", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  if (trimmed.includes(";")) throw new ArgumentError("\u53EA\u5141\u8BB8\u4E00\u6761\u8BED\u53E5", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  if (WRITE.test(trimmed) || /\$out\b|\$merge\b/i.test(trimmed)) {
    throw new ArgumentError("\u8BED\u53E5\u91CC\u542B\u6709\u5199\u5165\u64CD\u4F5C", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  }
  if (!READ.test(trimmed)) {
    throw new ArgumentError("\u53EA\u5141\u8BB8 find\u3001findOne\u3001count\u3001countDocuments\u3001aggregate\u3001distinct", "\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  }
  return trimmed;
}
function assertLimit(value) {
  const limit = Number(value);
  if (!Number.isInteger(limit) || limit < 1 || limit > 1e3) {
    throw new ArgumentError("\u8FD4\u56DE\u884C\u6570\u5FC5\u987B\u662F 1 \u5230 1000", "\u4E0D\u4F7F\u7528 max\uFF0C\u4E0D\u4F1A\u53D1\u9001\u67E5\u8BE2");
  }
  return limit;
}
export {
  assertDatabase,
  assertInstance,
  assertLimit,
  assertStatement
};
