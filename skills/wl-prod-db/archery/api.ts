import type { IPage } from '@jackwener/opencli/types';

const ORIGIN = 'http://archery.hgj.net';

export async function openArchery(page: IPage): Promise<void> {
  await page.goto(`${ORIGIN}/sqlquery/`, { waitUntil: 'load', settleMs: 800 });
}

export async function archeryFetch(page: IPage, path: string, params: Record<string, string>): Promise<any> {
  const result = await page.evaluate(async (path: string, params: Record<string, string>) => {
    const cookie = document.cookie.split(';').map((item) => item.trim()).find((item) => item.startsWith('csrftoken='));
    if (!cookie) return { error: '未登录 Archery，先在 Chrome 里登录后再试' };
    const token = decodeURIComponent(cookie.slice('csrftoken='.length));
    const body = new URLSearchParams(params);
    const response = await fetch(path, {
      method: 'POST',
      headers: {
        'X-CSRFToken': token,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
      },
      body,
    });
    const text = await response.text();
    try {
      return { http: response.status, data: JSON.parse(text) };
    } catch {
      return { http: response.status, data: { status: response.status, msg: text } };
    }
  }, path, params);
  if (result && typeof result === 'object' && 'error' in result && result.error) {
    throw new Error(String(result.error));
  }
  const data = (result as { data: any }).data;
  if (!data || data.status !== 0) {
    throw new Error(data?.msg || 'Archery 查询失败');
  }
  return data;
}

export async function archeryGet(page: IPage, path: string, params: Record<string, string>): Promise<any> {
  const query = new URLSearchParams(params).toString();
  const result = await page.evaluate(async (url: string) => {
    const response = await fetch(url);
    const text = await response.text();
    try {
      return JSON.parse(text);
    } catch {
      return { status: response.status, msg: text };
    }
  }, `${path}?${query}`);
  if (!result || result.status !== 0) {
    throw new Error(result?.msg || 'Archery 读取失败');
  }
  return result;
}
