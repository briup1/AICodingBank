#!/usr/bin/env node
// Explicit local integration test: temporary profiles, no business URLs or credentials.
import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { mkdtemp, writeFile, readFile, mkdir } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { start, stop, status, closeSession, processTable } from './console.mjs';

const exec = promisify(execFile);
const binary = join(homedir(), '.node/bin/agent-browser');
const root = join(homedir(), '.local/state/browser-console/validation');
await mkdir(root, { recursive: true });
const run = await mkdtemp(join(root, 'run-'));
const names = [`console-smoke-a-${process.pid}`, `console-smoke-b-${process.pid}`];
const records = [];
const env = { ...process.env, AGENT_BROWSER_SOCKET_DIR: join(homedir(), '.agent-browser') };
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const directory = dirname(fileURLToPath(import.meta.url));
async function browser(name, args, idle = '600000') {
  const { stdout } = await exec(binary, ['--session', name, ...args, '--json'], {
    env: { ...env, AGENT_BROWSER_IDLE_TIMEOUT_MS: idle }, timeout: 20000,
  });
  const result = JSON.parse(stdout);
  assert.equal(result.success, true);
  return result.data;
}
async function pid(name) {
  return Number((await readFile(join(homedir(), '.agent-browser', `${name}.pid`), 'utf8')).trim());
}
try {
  const first = await start();
  assert.equal((await start()).pid, first.pid);
  records.push('PASS: repeated start reuses the same Dashboard PID');
  for (const [index, name] of names.entries()) {
    await browser(name, ['--executable-path', chrome, '--profile', join(run, name),
      'open', `data:text/html,<title>Console validation ${index + 1}</title><h1>Local browser validation ${index + 1}</h1><p>No business data.</p>`]);
  }
  const bPid = await pid(names[1]);
  await stop();
  assert.equal((await status()).running, false);
  assert.ok((await processTable()).some(row => row.pid === bPid));
  records.push('PASS: stopping Dashboard releases listener but leaves session B alive');
  await start();
  if (process.env.CONSOLE_SCREENSHOT) {
    // Observe only the local dashboard using the normal browser automation tool.
    const { stdout } = await exec('opencli', ['browser', 'browser-console-verify', 'eval',
      `document.querySelectorAll('button').forEach(b=>{if(b.textContent.includes('${names[0]}'))b.click()}); 'selected local validation session'`], { timeout: 20000 });
    console.log(stdout.trim());
    await new Promise(resolve => setTimeout(resolve, 1500));
    await exec('opencli', ['browser', 'browser-console-verify', 'screenshot', process.env.CONSOLE_SCREENSHOT], { timeout: 20000 });
    records.push('Screenshot saved; human image inspection still required');
  }
  await closeSession(names[0]);
  assert.ok((await processTable()).some(row => row.pid === bPid));
  records.push('PASS: closing A leaves B alive and verifies captured A process tree exited');
  await closeSession(names[1]);
  // Reuse the temporary B profile for idle expiry, without issuing further browser commands.
  await browser(names[1], ['--executable-path', chrome, '--profile', join(run, names[1]), 'open', 'about:blank'], '2000');
  const idlePid = await pid(names[1]);
  await new Promise(resolve => setTimeout(resolve, 4500));
  assert.ok(!(await processTable()).some(row => row.pid === idlePid));
  records.push('PASS: a new daemon with a 2s no-command timeout exits automatically');
  const task = join(run, 'failing-task.mjs');
  await writeFile(task, `import {execFileSync} from 'node:child_process';\nexecFileSync(${JSON.stringify(binary)}, ['--executable-path',${JSON.stringify(chrome)},'--profile',${JSON.stringify(join(run, 'task-profile'))},'open','about:blank','--json']);\nprocess.exit(7);\n`);
  const taskName = `console-smoke-task-${process.pid}`;
  names.push(taskName);
  let failed = false;
  try {
    await exec(process.execPath, [join(directory, 'console.mjs'), 'task', taskName, '--', process.execPath, task], { timeout: 25000 });
  } catch (error) { assert.equal(error.code, 7); failed = true; }
  assert.ok(failed);
  await closeSession(taskName);
  records.push('PASS: failing real browser task preserves exit 7 and cleans up the session');
  records.push(`Profiles and evidence retained at ${run}`);
} finally {
  for (const name of names) {
    try { await closeSession(name); }
    catch (error) { records.push(`CLEANUP FAILED ${name}: ${error.message}`); process.exitCode = 1; }
  }
  await writeFile(join(run, 'result.txt'), records.join('\n') + '\n');
  console.log(records.join('\n'));
}
