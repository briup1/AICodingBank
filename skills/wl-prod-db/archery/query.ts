import { cli, Strategy } from '@jackwener/opencli/registry';
import { assertDatabase, assertInstance, assertLimit, assertStatement } from './guard.js';
import { archeryFetch, openArchery } from './api.js';

cli({
  site: 'archery',
  name: 'query',
  access: 'read',
  description: '在生产 Mongo 上执行一条 find 或 count，返回行数受 --limit 限制。',
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: 'json',
  defaultWindowMode: 'background',
  args: [
    { name: 'instance', required: true, help: '实例名，必须 prd-mongo 开头' },
    { name: 'database', required: true, help: '数据库名' },
    { name: 'statement', required: true, help: '一条 Mongo 只读语句，例如 db.getCollection("x").find({})' },
    { name: 'limit', type: 'number', default: 100, help: '返回行数，1 到 1000，默认 100' },
  ],
  columns: ['instance', 'database', 'statement', 'limit', 'row_count', 'query_time'],
  validateArgs: (kwargs) => {
    kwargs.instance = assertInstance(String(kwargs.instance ?? ''));
    kwargs.database = assertDatabase(String(kwargs.database ?? ''));
    kwargs.statement = assertStatement(String(kwargs.statement ?? ''));
    kwargs.limit = assertLimit(kwargs.limit);
  },
  func: async (page, kwargs) => {
    const instance = String(kwargs.instance);
    const database = String(kwargs.database);
    const statement = String(kwargs.statement);
    const limit = Number(kwargs.limit);
    await openArchery(page);
    const result = await archeryFetch(page, '/query/', {
      instance_name: instance,
      db_name: database,
      schema_name: '',
      tb_name: '',
      sql_content: statement,
      limit_num: String(limit),
    });
    const payload = result.data ?? {};
    const columns = Array.isArray(payload.column_list) ? payload.column_list.map(String) : [];
    const rawRows = Array.isArray(payload.rows) ? payload.rows : [];
    const rows = rawRows.map((row: unknown[]) => {
      const item: Record<string, unknown> = {};
      columns.forEach((column, index) => {
        item[column] = row?.[index];
      });
      const whole = item.mongodballdata;
      if (typeof whole === 'string' && whole) {
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
      query_time: payload.query_time ?? '',
      rows,
    }];
  },
});
