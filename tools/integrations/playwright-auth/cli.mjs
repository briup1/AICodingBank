#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { loadConfig, errorCode, fail, ensurePrivateDir, inspectPath } from './store.mjs';
import { bootstrap, check, login, runtime } from './auth.mjs';
import { admitSpec } from './admission.mjs';

process.umask(0o077);
const here = path.dirname(fileURLToPath(import.meta.url));
export function argumentsFor(args) {
  const [command, ...rest] = args;
  const permitted = { bootstrap: ['--source-cdp', '--establish-expected'], login: ['--establish-expected', '--wait-seconds'], check: ['--count', '--parallel'], run: ['--spec', '--output'] };
  if (!permitted[command]) fail('INVALID_ARGUMENT');
  const options = {};
  for (let i = 0; i < rest.length; i++) {
    const k = rest[i];
    if (!permitted[command].includes(k) || k in options) fail('INVALID_ARGUMENT');
    if (k === '--establish-expected') options[k] = true;
    else { if (!rest[i + 1] || rest[i + 1].startsWith('--')) fail('INVALID_ARGUMENT'); options[k] = rest[++i]; }
  }
  return { command, options };
}

async function main() {
  const { command, options: o } = argumentsFor(process.argv.slice(2));
  const c = loadConfig();
  if (command === 'bootstrap') return bootstrap(c, o['--source-cdp'], !!o['--establish-expected']);
  if (command === 'login') return login(c, !!o['--establish-expected'], Number(o['--wait-seconds'] || 300));
  if (command === 'check') return check({ c, count: Number(o['--count'] || 1), parallel: Number(o['--parallel'] || 1) });
  const spec = o['--spec'], output = o['--output'];
  if (!spec || !output || !path.isAbsolute(spec) || !path.isAbsolute(output) || !/^[\w.-]+\.spec\.mjs$/.test(path.basename(spec))) fail('INVALID_ARGUMENT');
  if (!fs.statSync(spec).isFile()) fail('INVALID_ARGUMENT');
  admitSpec(fs.readFileSync(spec, 'utf8'), spec);
  // Never delete or reuse a caller's existing output directory.
  inspectPath(path.dirname(output), { privateLeaf: true });
  if (fs.existsSync(output)) fail('OUTPUT_EXISTS');
  ensurePrivateDir(output);
  const r = runtime(c);
  // Discard Playwright/Node runner overrides inherited from another task.
  const env = Object.fromEntries(Object.entries(process.env).filter(([k]) => !/^(PLAYWRIGHT_|PW_|NODE_OPTIONS$|NODE_PATH$)/.test(k)));
  const summaryFile = path.join(output, 'summary.json');
  Object.assign(env, { PLAYWRIGHT_AUTH_TEST_DIR: path.dirname(spec), PLAYWRIGHT_AUTH_TEST_FILE: path.basename(spec), PLAYWRIGHT_AUTH_OUTPUT: output, PLAYWRIGHT_AUTH_SUMMARY: summaryFile });
  const child = spawn(process.execPath, [r.cli, 'test', '--config', path.join(here, 'runner.config.mjs'), '--workers=1', '--retries=0'], { stdio: ['ignore', 'pipe', 'pipe'], env });
  // Reporter/Playwright exceptions may contain local state or raw network data.
  // Shared CLI returns only exit status; a trusted project owns any richer reports.
  child.stdout.resume(); child.stderr.resume();
  const code = await new Promise(resolve => { child.once('error', () => resolve(1)); child.once('exit', code => resolve(code ?? 1)); });
  // Built-in failure context can include account text. This controlled output dir
  // is for ephemeral runner output, not a user project directory.
  let summary;
  try { summary = JSON.parse(fs.readFileSync(summaryFile, 'utf8')); } catch { summary = {}; }
  const testsDiscovered = Number.isSafeInteger(summary.testsDiscovered) ? summary.testsDiscovered : 0;
  const testsFinished = Number.isSafeInteger(summary.testsFinished) ? summary.testsFinished : 0;
  const passed = code === 0 && summary.passed === true && testsDiscovered > 0 && testsFinished === testsDiscovered;
  fs.rmSync(output, { recursive: true, force: true });
  process.exitCode = passed ? 0 : 1;
  return { status: passed ? 'PASS' : 'TEST_FAILED', runnerExitCode: code, spec: path.basename(spec), testsDiscovered, testsFinished };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().then(result => { console.log(JSON.stringify(result)); }).catch(e => {
    console.log(JSON.stringify({ status: errorCode(e) })); process.exitCode = 1;
  }).finally(() => {
    // Bootstrap attaches to a user-authorized source and must not call browser.close.
    // Client exit releases CDP only. Daily check/run launch and close their own browsers.
    process.exit(process.exitCode || 0);
  });
}
