import { ArgumentError } from '@jackwener/opencli/errors';

const WRITE_KEYWORD = /\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|replace|call|load|outfile|dumpfile)\b/i;

export function assertSource(source: string): string {
  const name = source.trim();
  if (!name) throw new ArgumentError('缺少数据源');
  if (/rw/i.test(name)) {
    throw new ArgumentError(`拒绝数据源 ${name}：名字里带 rw`, '只允许只读数据源，不会发送查询');
  }
  return name;
}

export function assertReadSql(sql: string): string {
  const trimmed = sql.trim().replace(/;+\s*$/u, '');
  if (!trimmed) throw new ArgumentError('缺少 SQL');
  if (trimmed.includes(';')) throw new ArgumentError('只允许一条 SQL', '不会发送查询');
  const stripped = trimmed
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/--[^\n]*/g, ' ')
    .trim();
  if (!/^select\b/i.test(stripped)) {
    throw new ArgumentError('只允许 SELECT', '不会发送查询');
  }
  if (WRITE_KEYWORD.test(stripped)) {
    throw new ArgumentError('语句里含有写入关键字', '不会发送查询');
  }
  if (!/\blimit\s+\d+\b/i.test(stripped)) {
    throw new ArgumentError('SELECT 必须带 LIMIT', '不会发送查询');
  }
  return trimmed;
}

export function tableFromSql(sql: string): string {
  const match = sql.match(/\bfrom\s+[`"]?([a-zA-Z0-9_]+)[`"]?/i);
  return match?.[1] ?? '';
}
