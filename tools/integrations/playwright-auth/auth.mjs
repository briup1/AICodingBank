import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { createInterface } from 'node:readline';
import { fail, loadConfig, loadRecord, atomicPrivateWrite, statePath, expectedPath, readExpected, AuthError } from './store.mjs';
import { APP, TARGET, LOGIN, IDENTITY, validateStorage, verifyPage, compareIdentity, readOnlyContext } from './identity.mjs';

export function runtime(c) {
  try {
    if (!fs.existsSync(c.executable)) fail('RUNTIME_UNAVAILABLE');
    const require = createRequire(path.join(c.runtime, 'package.json'));
    const pkg = require('./package.json');
    if (pkg.name !== 'playwright' || pkg.version !== c.version) fail('RUNTIME_UNAVAILABLE');
    return { ...require(c.runtime), testModule: require(path.join(c.runtime, 'test.js')), cli: path.join(c.runtime, 'cli.js') };
  } catch { fail('RUNTIME_UNAVAILABLE'); }
}

export async function exportTargetState(context) {
  // Source is an explicitly authorized dedicated context, never a daily Chrome profile.
  // Refuse contexts with other live site origins instead of exporting unrelated tabs.
  for (const page of context.pages()) {
    if (page.url() === 'about:blank') continue;
    let origin; try { origin = new URL(page.url()).origin; } catch { fail('SOURCE_REJECTED'); }
    if (![APP, LOGIN, new URL(IDENTITY).origin].includes(origin)) fail('SOURCE_REJECTED');
  }
  const cookies = await context.cookies([TARGET, LOGIN, IDENTITY]);
  const raw = await context.storageState({ indexedDB: true });
  return validateStorage({ cookies, origins: raw.origins.filter(o => o.origin === APP) });
}

export async function guardedPage(browser, c, record, use, { readOnly = false } = {}) {
  if (c.consent !== true) fail('CONSENT_REQUIRED');
  const context = await browser.newContext({ storageState: validateStorage(record.storage), viewport: { width: 1440, height: 1000 }, serviceWorkers: 'block' });
  try {
    // The identity gate itself never submits a business write. Restore normal behavior
    // only after verification, when an explicitly authorized test may own its page.
    await readOnlyContext(context);
    const page = await context.newPage();
    const actual = await verifyPage(page, record.expected);
    if (!readOnly) await context.unroute('**/*');
    return await use(page, actual);
  } finally { await context.close(); }
}

export async function check({ count = 1, parallel = 1, c = loadConfig() } = {}) {
  if (![1, 3].includes(count) || ![1, 2].includes(parallel)) fail('INVALID_ARGUMENT');
  const record = loadRecord(c); validateStorage(record.storage);
  const { chromium } = runtime(c);
  let browser;
  const started = Date.now(); let opened = 0, closed = 0;
  try {
    browser = await chromium.launch({ executablePath: c.executable, headless: true, timeout: 20000 });
    for (let i = 0; i < count; i++) {
      const results = await Promise.allSettled(Array.from({ length: parallel }, async () => {
        opened++;
        try { return await guardedPage(browser, c, record, async () => ({ sameIdentity: true, sameEnterprise: true }), { readOnly: true }); }
        finally { closed++; }
      }));
      const failed = results.find(x => x.status === 'rejected');
      if (failed) throw failed.reason;
    }
    return { status: 'PASS', environment: c.environment, sameIdentity: true, sameEnterprise: true, contextsVerified: opened, contextsClosed: closed, elapsedMs: Date.now() - started, sourceCdpUsed: false };
  } finally { if (browser) await browser.close(); }
}

export async function saveVerified(context, c, expected, file = statePath()) {
  const storage = await exportTargetState(context);
  const { chromium } = runtime(c);
  let browser;
  try {
    browser = await chromium.launch({ executablePath: c.executable, headless: true, timeout: 20000 });
    const record = { version: 1, environment: c.environment, expected, storage };
    await guardedPage(browser, c, record, async () => {}, { readOnly: true });
    // Re-read consent immediately before saving; cancellation/revocation wins.
    const latest = loadConfig();
    if (latest.environment !== c.environment) fail('ENVIRONMENT_REJECTED');
    if (fs.existsSync(expectedPath())) compareIdentity(expected, readExpected(latest));
    else atomicPrivateWrite(expectedPath(), { environment: c.environment, ...expected });
    atomicPrivateWrite(file, record);
    return { status: 'SAVED', environment: c.environment, sameIdentity: true, sameEnterprise: true };
  } finally { if (browser) await browser.close(); }
}

export async function bootstrap(c, endpoint, establishExpected = false) {
  let u; try { u = new URL(endpoint); } catch { fail('INVALID_ARGUMENT'); }
  if (u.protocol !== 'http:' || u.hostname !== '127.0.0.1' || !u.port || u.username || u.password || u.pathname !== '/' || u.search) fail('SOURCE_REJECTED');
  const { chromium } = runtime(c);
  // This command is explicit one-time import. Never close the authorized source.
  const browser = await chromium.connectOverCDP(endpoint, { timeout: 10000 });
  const page = browser.contexts().flatMap(x => x.pages()).find(p => { try { return new URL(p.url()).origin === APP; } catch { return false; } });
  if (!page) fail('SOURCE_REJECTED');
  const prior = establishExpected ? null : { expected: readExpected(c) };
  if (establishExpected && (fs.existsSync(statePath()) || fs.existsSync(expectedPath()))) fail('EXPECTED_ALREADY_REGISTERED');
  // Guard only the source page during native reload; do not alter other pages.
  const handler = async route => ['GET', 'HEAD', 'OPTIONS'].includes(route.request().method()) ? route.continue() : route.abort('blockedbyclient');
  await page.route('**/*', handler);
  try {
    const identity = await verifyPage(page, prior?.expected);
    return await saveVerified(page.context(), c, prior?.expected || identity);
  } finally { await page.unroute('**/*', handler); }
}

export async function login(c, establishExpected = false, waitSeconds = 300) {
  if (!Number.isInteger(waitSeconds) || waitSeconds < 10 || waitSeconds > 600) fail('INVALID_ARGUMENT');
  const prior = establishExpected ? null : { expected: readExpected(c) };
  if (establishExpected && (fs.existsSync(statePath()) || fs.existsSync(expectedPath()))) fail('EXPECTED_ALREADY_REGISTERED');
  const { chromium } = runtime(c);
  if (!process.stdin.isTTY) fail('INTERACTIVE_TERMINAL_REQUIRED');
  const browser = await chromium.launch({ executablePath: c.executable, headless: false, timeout: 20000, handleSIGINT: false });
  const closed = new Promise(resolve => browser.once('disconnected', resolve));
  try {
    const context = await browser.newContext({ serviceWorkers: 'block' });
    const page = await context.newPage();
    await page.goto(TARGET, { waitUntil: 'domcontentloaded', timeout: 25000 });
    console.log(JSON.stringify({ status: 'AWAITING_MANUAL_LOGIN', waitSeconds, action: 'Complete login and enterprise selection in the owned window, then press Enter here. Do not type credentials here.' }));
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    let timer;
    const entered = await Promise.race([
      new Promise(resolve => rl.once('line', () => resolve(true))),
      new Promise(resolve => { timer = setTimeout(() => resolve(false), waitSeconds * 1000); }),
      closed.then(() => false),
    ]);
    clearTimeout(timer); rl.close();
    if (!entered) fail('MANUAL_LOGIN_CANCELLED_OR_TIMEOUT');
    await readOnlyContext(context);
    const actual = await verifyPage(page, prior?.expected);
    const result = await saveVerified(context, c, prior?.expected || actual);
    console.log(JSON.stringify({ ...result, windowRetained: true, action: 'Close only this owned window when finished.' }));
    await closed;
    return result;
  } catch (e) {
    console.log(JSON.stringify({ status: e instanceof AuthError ? e.code : 'OPERATION_FAILED', windowRetained: browser.isConnected(), stateUpdated: false }));
    // Keep the just-used manual login window even on timeout or identity failure.
    await closed;
    throw e;
  }
}
