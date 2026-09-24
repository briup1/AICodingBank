import { cli, Strategy } from '@jackwener/opencli/registry';
import { assertReadSql, assertSource, tableFromSql } from './guard.js';
import { openYearning, yearningFetch } from './api.js';

const DEFAULT_SOURCE = 'mysql|奇点-ro';
const DEFAULT_DATABASE = 'compass-freight';
const DEFAULT_SQL = 'select * from hot_ports_dict limit 10';

interface StatusPayload {
  status?: number;
}

interface ResultTitle {
  title?: string;
  key?: string;
}

interface ResultPayload {
  status?: unknown;
  data?: Array<Record<string, unknown>> | null;
  title?: ResultTitle[];
  total?: number;
}

cli({
  site: 'yearning',
  name: 'query',
  access: 'read',
  description: '对只读数据源执行一条带 LIMIT 的 SELECT，返回表名、SQL 和行数据。',
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: 'json',
  defaultWindowMode: 'background',
  args: [
    { name: 'source', default: DEFAULT_SOURCE, help: '数据源，默认 mysql|奇点-ro。名字里带 rw 会拒绝。' },
    { name: 'database', default: DEFAULT_DATABASE, help: '库名，默认 compass-freight' },
    { name: 'sql', default: DEFAULT_SQL, help: '一条 SELECT，必须带 LIMIT' },
  ],
  columns: ['table', 'sql', 'source', 'database', 'row_count'],
  validateArgs: (kwargs) => {
    kwargs.source = assertSource(String(kwargs.source ?? ''));
    kwargs.sql = assertReadSql(String(kwargs.sql ?? ''));
    kwargs.database = String(kwargs.database ?? '').trim();
    if (!kwargs.database) throw new Error('缺少库名');
  },
  func: async (page, kwargs) => {
    const source = String(kwargs.source);
    const database = String(kwargs.database);
    const sql = String(kwargs.sql);
    await openYearning(page);
    const current = await yearningFetch<StatusPayload>(page, 'PUT', '/api/v2/query/status');
    if (Number(current.payload?.status) !== 1) {
      throw new Error('查询时限不在。先运行 opencli yearning apply');
    }
    const result = await yearningFetch<ResultPayload>(page, 'POST', '/api/v2/query/results', {
      sql,
      data_base: database,
      source,
    });
    const payload = result.payload;
    if (!payload || payload.status) {
      throw new Error('查询时限已过期或查询被拒绝。先运行 opencli yearning apply');
    }
    const rows = Array.isArray(payload.data) ? payload.data : [];
    return [{
      table: tableFromSql(sql),
      sql,
      source,
      database,
      row_count: rows.length,
      rows,
    }];
  },
});
