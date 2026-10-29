import { cli, Strategy } from '@jackwener/opencli/registry';
import { assertInstance } from './guard.js';
import { archeryGet, openArchery } from './api.js';

cli({
  site: 'archery',
  name: 'databases',
  access: 'read',
  description: '列出一个生产 Mongo 实例下的数据库。',
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: 'json',
  defaultWindowMode: 'background',
  args: [
    { name: 'instance', required: true, help: '实例名，必须 prd-mongo 开头' },
  ],
  columns: ['name'],
  validateArgs: (kwargs) => {
    kwargs.instance = assertInstance(String(kwargs.instance ?? ''));
  },
  func: async (page, kwargs) => {
    await openArchery(page);
    const result = await archeryGet(page, '/instance/instance_resource/', {
      instance_name: String(kwargs.instance),
      resource_type: 'database',
    });
    const names = Array.isArray(result.data) ? result.data : [];
    return names.map((name: unknown) => ({ name: String(name) }));
  },
});
