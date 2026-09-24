import type { IPage } from '@jackwener/opencli/types';

const ORIGIN = 'http://yearning.hgj.net';

export interface YearningEnvelope<T> {
  code?: number;
  text?: string;
  payload?: T;
}

export async function openYearning(page: IPage): Promise<void> {
  await page.goto(`${ORIGIN}/#/query/order`, { waitUntil: 'load', settleMs: 800 });
}

export async function yearningFetch<T>(
  page: IPage,
  method: 'GET' | 'PUT' | 'POST',
  path: string,
  body?: unknown,
): Promise<YearningEnvelope<T>> {
  const result = await page.evaluate(
    async (method: string, path: string, body: unknown) => {
      const jwt = localStorage.getItem('jwt');
      if (!jwt) return { error: '未登录 Yearning，先在 Chrome 里登录后再试' };
      const headers: Record<string, string> = { Authorization: jwt };
      const init: RequestInit = { method, headers };
      if (body !== null && body !== undefined) {
        headers['Content-Type'] = 'application/json';
        init.body = JSON.stringify(body);
      }
      const response = await fetch(path, init);
      const text = await response.text();
      try {
        return { http: response.status, data: JSON.parse(text) };
      } catch {
        return { http: response.status, data: { code: response.status, text, payload: null } };
      }
    },
    method,
    path,
    body ?? null,
  );
  if (result && typeof result === 'object' && 'error' in result && result.error) {
    throw new Error(String(result.error));
  }
  const data = (result as { data: YearningEnvelope<T> }).data;
  if (!data || typeof data !== 'object') throw new Error(`Yearning 返回无法解析: ${path}`);
  if (data.code !== undefined && data.code !== 1200) {
    throw new Error(data.text || `Yearning ${path} 失败，code=${data.code}`);
  }
  return data;
}
