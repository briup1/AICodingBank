import { loadConfig, loadRecord, errorCode } from './store.mjs';
import { runtime, guardedPage } from './auth.mjs';

// Users MUST import this test, not playwright/test. Configuration cannot make an
// arbitrary existing spec safe. An auto fixture verifies before even a pageless test.
const { test: base, expect } = runtime(loadConfig()).testModule;
export { expect };
export const test = base.extend({
  _authenticatedPage: [async ({}, use) => {
    let browser;
    try {
      const c = loadConfig(), record = loadRecord(c);
      browser = await runtime(c).chromium.launch({ executablePath: c.executable, headless: true, timeout: 20000 });
      await guardedPage(browser, c, record, async page => { await use(page); });
    } catch (e) { throw new Error(errorCode(e)); }
    finally { if (browser) await browser.close(); }
  }, { auto: true }],
  page: async ({ _authenticatedPage }, use) => { await use(_authenticatedPage); },
});
