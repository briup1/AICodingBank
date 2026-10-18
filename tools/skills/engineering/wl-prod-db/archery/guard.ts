import { ArgumentError } from '@jackwener/opencli/errors';

const WRITE = /\.(insert|insertOne|insertMany|update|updateOne|updateMany|delete|deleteOne|deleteMany|remove|drop|save|replaceOne|findOneAndUpdate|findOneAndDelete|findOneAndReplace|bulkWrite)\s*\(/i;
const READ = /^db(?:\.getCollection\s*\(\s*['\"][^'\"]+['\"]\s*\)|\.[A-Za-z0-9_-]+)\s*\.\s*(findOne|find|countDocuments|count|aggregate|distinct)\s*\(/i;

export function assertInstance(instance: string): string {
  const name = instance.trim();
  if (!name.startsWith('prd-mongo')) {
    throw new ArgumentError(`拒绝实例 ${name || '(空)'}：只允许 prd-mongo 开头`, '不会发送查询');
  }
  return name;
}

export function assertDatabase(database: string): string {
  const name = database.trim();
  if (!name) throw new ArgumentError('缺少数据库', '不会发送查询');
  return name;
}

export function assertStatement(statement: string): string {
  const trimmed = statement.trim().replace(/;+\s*$/u, '');
  if (!trimmed) throw new ArgumentError('缺少查询语句', '不会发送查询');
  if (trimmed.includes(';')) throw new ArgumentError('只允许一条语句', '不会发送查询');
  if (WRITE.test(trimmed) || /\$out\b|\$merge\b/i.test(trimmed)) {
    throw new ArgumentError('语句里含有写入操作', '不会发送查询');
  }
  if (!READ.test(trimmed)) {
    throw new ArgumentError('只允许 find、findOne、count、countDocuments、aggregate、distinct', '不会发送查询');
  }
  return trimmed;
}

export function assertLimit(value: unknown): number {
  const limit = Number(value);
  if (!Number.isInteger(limit) || limit < 1 || limit > 1000) {
    throw new ArgumentError('返回行数必须是 1 到 1000', '不使用 max，不会发送查询');
  }
  return limit;
}
