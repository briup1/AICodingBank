import { cli, Strategy } from '@jackwener/opencli/registry';
import { assertDatabase, assertInstance } from './guard.js';
import { archeryGet, openArchery } from './api.js';

cli({
  site: 'archery',
  name: 'collections',
  access: 'read',
  description: '列出一个生产 Mongo 库下的集合。',
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: 'json',
  defaultWindowMode: 'background',
  args: [
    { name: 'instance', required: true, help: '实例名，必须 prd-mongo 开头' },
    { name: 'database', required: true, help: '数据库名' },
  ],
  columns: ['name'],
  validateArgs: (kwargs) => {
    kwargs.instance = assertInstance(String(kwargs.instance ?? ''));
    kwargs.database = assertDatabase(String(kwargs.database ?? ''));
  },
  func: async (page, kwargs) => {
    await openArchery(page);
    const result = await archeryGet(page, '/instance/instance_resource/', {
      instance_name: String(kwargs.instance),
      db_name: String(kwargs.database),
      resource_type: 'table',
    });
    const names = Array.isArray(result.data) ? result.data : [];
    return names.map((name: unknown) => ({ name: String(name) }));
  },
});
