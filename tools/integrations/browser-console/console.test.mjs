import test from 'node:test';
import assert from 'node:assert/strict';
import { descendants, validSession, runTask, PORT, URL, IDLE_MS } from './console.mjs';

test('only the selected process tree is considered', () => {
  const table = [
    { pid: 10, ppid: 1 }, { pid: 12, ppid: 10 }, { pid: 13, ppid: 12 },
    { pid: 20, ppid: 1 }, { pid: 21, ppid: 20 },
  ];
  assert.deepEqual(descendants(table, 10).map(row => row.pid), [10, 12, 13]);
});

test('session names cannot target dashboard or inject paths/options', () => {
  for (const name of ['dashboard', '../default', '--all', '', 'a/b', 'a b', 'A']) {
    assert.throws(() => validSession(name));
  }
  assert.equal(validSession('yuxi-beta-check-12'), 'yuxi-beta-check-12');
});

test('task preserves failure and never starts a browser for cleanup alone', async () => {
  const name = `console-unit-${process.pid}`;
  assert.equal(await runTask(name, process.execPath, ['-e', 'process.exit(7)']), 7);
});

test('task gets named session and idle policy', async () => {
  const name = `console-env-${process.pid}`;
  const script = `if(process.env.AGENT_BROWSER_SESSION!==${JSON.stringify(name)}||process.env.AGENT_BROWSER_IDLE_TIMEOUT_MS!==${JSON.stringify(IDLE_MS)})process.exit(9)`;
  assert.equal(await runTask(name, process.execPath, ['-e', script]), 0);
  assert.equal(PORT, 4848);
});

test('Dashboard uses the exact embedded Chat origin to avoid cross-origin fetches', () => {
  assert.equal(URL, 'http://localhost:4848');
  assert.equal(new globalThis.URL(URL).origin, new globalThis.URL('http://localhost:4848/api/chat').origin);
});

test('same managed task cannot be acquired twice', async () => {
  const name = `console-lock-${process.pid}`;
  const task = runTask(name, process.execPath, ['-e', 'setTimeout(()=>{},300)']);
  await new Promise(resolve => setTimeout(resolve, 100));
  await assert.rejects(runTask(name, process.execPath, ['-e', '']), /另一个操作/);
  assert.equal(await task, 0);
});
