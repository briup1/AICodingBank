import { loadConfig } from './store.mjs';
import { runtime } from './auth.mjs';
import { fileURLToPath } from 'node:url';
const { defineConfig } = runtime(loadConfig()).testModule;
// One selected module per invocation. No caller-supplied projects/config/fixtures flags.
export default defineConfig({
  testDir: process.env.PLAYWRIGHT_AUTH_TEST_DIR,
  testMatch: process.env.PLAYWRIGHT_AUTH_TEST_FILE,
  workers: 1, retries: 0, fullyParallel: false, timeout: 60000,
  reporter: [[fileURLToPath(new URL('./summary-reporter.cjs', import.meta.url))]], outputDir: process.env.PLAYWRIGHT_AUTH_OUTPUT,
  use: { trace: 'off', screenshot: 'off', video: 'off' },
  captureGitInfo: { commit: false, diff: false },
});
