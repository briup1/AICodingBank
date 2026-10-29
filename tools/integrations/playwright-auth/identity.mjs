import { fail } from './store.mjs';

export const APP = 'https://beta-smart-agent.hgj.com';
export const TARGET = APP + '/query';
export const LOGIN = 'https://beta-login.hgj.com';
export const IDENTITY = 'https://beta-apisix.hgj.com/whale-user-center/whale/user/get-user-detail-info';
export const ALLOWED = new Set([APP, LOGIN, new URL(IDENTITY).origin]);

export function parseIdentity(httpStatus, body) {
  if (httpStatus >= 500 || httpStatus === 429) fail('SERVICE_UNAVAILABLE');
  if (httpStatus === 401 || body?.code === 401 || body?.code === '401') fail('LOGIN_REQUIRED');
  // 403/permission failures are not proof an expired login can be repaired by signing in.
  if (httpStatus === 403 || body?.code === 403 || body?.code === '403') fail('ACCESS_DENIED');
  if (httpStatus !== 200) fail('SERVICE_UNAVAILABLE');
  if (!body || typeof body !== 'object' || (body.code !== 200 && body.code !== '200') || body.success === false) fail('IDENTITY_UNCONFIRMED');
  const user = body.data?.userId, enterprise = body.data?.enterpriseDetailResponse?.enterpriseId;
  const valid = x => (typeof x === 'string' && !!x.trim()) || (typeof x === 'number' && Number.isSafeInteger(x) && x > 0);
  if (!valid(user) || !valid(enterprise)) fail('IDENTITY_UNCONFIRMED');
  return { userId: String(user), enterpriseId: String(enterprise) };
}
export function compareIdentity(actual, expected) {
  if (!expected?.userId || !expected?.enterpriseId) fail('IDENTITY_UNCONFIRMED');
  if (actual.userId !== expected.userId || actual.enterpriseId !== expected.enterpriseId) fail('IDENTITY_MISMATCH');
  return { sameIdentity: true, sameEnterprise: true };
}
export function validateStorage(storage) {
  if (!storage || !Array.isArray(storage.cookies) || !Array.isArray(storage.origins)) fail('STATE_CORRUPT');
  for (const origin of storage.origins) {
    if (origin.origin !== APP || !Array.isArray(origin.localStorage)) fail('ENVIRONMENT_REJECTED');
  }
  for (const c of storage.cookies) {
    if (typeof c.name !== 'string' || typeof c.value !== 'string' || !['.hgj.com', 'hgj.com', 'beta-smart-agent.hgj.com', '.beta-smart-agent.hgj.com', 'beta-login.hgj.com', '.beta-login.hgj.com', 'beta-apisix.hgj.com', '.beta-apisix.hgj.com'].includes(c.domain)) fail('ENVIRONMENT_REJECTED');
  }
  return storage;
}

// Only native identity GET responses from the actual trusted page are accepted.
export function isIdentityResponse(response, page) {
  try {
    const req = response.request();
    return response.url() === IDENTITY && req.method() === 'GET' && req.frame().page() === page && new URL(page.url()).origin === APP;
  } catch { return false; }
}
export async function verifyPage(page, expected) {
  let response;
  const waiting = page.waitForResponse(r => isIdentityResponse(r, page), { timeout: 20000 }).then(r => { response = r; });
  // Attach rejection immediately so navigation failure does not produce unhandled rejection/raw errors.
  const settled = waiting.catch(() => {});
  try { await page.goto(TARGET, { waitUntil: 'domcontentloaded', timeout: 25000 }); }
  catch { fail('SERVICE_UNAVAILABLE'); }
  // Navigation must have succeeded. A trusted login redirect need not request
  // the app's identity endpoint; never classify that as a network outage.
  let origin;
  try { origin = new URL(page.url()).origin; } catch { fail('SERVICE_UNAVAILABLE'); }
  if (origin === LOGIN) fail('LOGIN_REQUIRED');
  if (origin !== APP) fail('ENVIRONMENT_REJECTED');
  let loginBlocked;
  try { loginBlocked = await page.evaluate(() => !!document.querySelector('input[type=password]') || /登录账号，体验完整服务/.test(document.body.innerText)); }
  catch { fail('PAGE_UNAVAILABLE'); }
  if (loginBlocked) fail('LOGIN_REQUIRED');
  await settled;
  if (!response) fail('SERVICE_UNAVAILABLE');
  let body; try { body = await response.json(); } catch { fail('IDENTITY_UNCONFIRMED'); }
  const identity = parseIdentity(response.status(), body);
  if (expected) compareIdentity(identity, expected);
  if (new URL(page.url()).origin !== APP) fail('LOGIN_REQUIRED');
  try {
    await page.locator('textarea').waitFor({ state: 'visible', timeout: 10000 });
    const blocked = await page.evaluate(() => !!document.querySelector('input[type=password]') || /登录账号，体验完整服务/.test(document.body.innerText));
    if (blocked) fail('LOGIN_REQUIRED');
    const x = page.locator('.smart-a-welfare-activity-poster__close');
    if (await x.isVisible()) await x.click({ force: true, timeout: 3000 });
    await page.locator('textarea').click({ trial: true, timeout: 5000 });
    if (await page.locator('textarea').isDisabled()) fail('PAGE_UNAVAILABLE');
  } catch (e) { if (e.code) throw e; fail('PAGE_UNAVAILABLE'); }
  return identity;
}

// Identity-only commands suppress every non-read request, including automatic telemetry.
export async function readOnlyContext(context) {
  await context.route('**/*', async route => {
    const req = route.request();
    // Static assets/CDN reads may have other hosts; top-level documents may not.
    if (req.isNavigationRequest() && req.frame().parentFrame() === null && !ALLOWED.has(new URL(req.url()).origin)) return route.abort('blockedbyclient');
    if (!['GET', 'HEAD', 'OPTIONS'].includes(req.method())) return route.abort('blockedbyclient');
    return route.continue();
  });
}
