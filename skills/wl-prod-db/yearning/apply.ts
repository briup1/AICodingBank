import { cli, Strategy } from '@jackwener/opencli/registry';
import { openYearning, yearningFetch } from './api.js';

const REASON = '工作需要';

interface StatusPayload {
  status?: number;
  idc?: string;
  export?: boolean;
}

interface SourcePayload {
  assigned?: string[];
  source?: string[];
}

cli({
  site: 'yearning',
  name: 'apply',
  access: 'write',
  description: '查询时限不在时，用页面原有环境和审核人提交说明「工作需要」。时限还在则跳过。',
  strategy: Strategy.UI,
  browser: true,
  navigateBefore: false,
  defaultFormat: 'json',
  defaultWindowMode: 'background',
  args: [],
  columns: ['applied', 'reason', 'description', 'idc', 'assigned', 'status'],
  func: async (page) => {
    await openYearning(page);
    const current = await yearningFetch<StatusPayload>(page, 'PUT', '/api/v2/query/status');
    const status = Number(current.payload?.status);
    if (status === 1) {
      return [{ applied: false, reason: '查询时限仍有效', description: '', idc: current.payload?.idc ?? '', assigned: '', status }];
    }
    if (status === 2) {
      return [{ applied: false, reason: '申请已提交，正在等待审核，不重复提交', description: '', idc: current.payload?.idc ?? '', assigned: '', status }];
    }

    const idc = current.payload?.idc || (await yearningFetch<string[]>(page, 'GET', '/api/v2/fetch/idc')).payload?.[0] || '';
    const source = await yearningFetch<SourcePayload>(page, 'GET', `/api/v2/fetch/source?idc=${encodeURIComponent(idc)}&tp=query`);
    const assigned = source.payload?.assigned?.[0] ?? '';
    if (!idc || !assigned) throw new Error('页面没有给出环境或审核人，停止提交');

    await yearningFetch(page, 'POST', '/api/v2/query/refer', {
      export: 0,
      text: REASON,
      idc,
      assigned,
    });
    const after = await yearningFetch<StatusPayload>(page, 'PUT', '/api/v2/query/status');
    return [{
      applied: true,
      reason: '已提交查询说明',
      description: REASON,
      idc,
      assigned,
      status: Number(after.payload?.status),
    }];
  },
});
