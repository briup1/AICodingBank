import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { initRun } from './run.mjs';
import { runBatch } from './batch.mjs';

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ws-web-auto-test-'));
process.on('exit', () => fs.rmSync(root, { recursive: true, force: true }));

test('run paths isolate tasks, execute does not create screenshots, invalid paths rejected', () => {
  const dir = initRun({ task: 'example', mode: 'execute', stateHome: root });
  assert.ok(dir.startsWith(path.join(root, 'web-task/runs/example/')));
  assert.equal(fs.existsSync(path.join(dir, 'screenshots')), false);
  assert.ok(fs.existsSync(path.join(initRun({ task: 'example', mode: 'verify', stateHome: root }), 'screenshots')));
  assert.throws(() => initRun({ task: '../escape', mode: 'verify', stateHome: root }));
  assert.throws(() => initRun({ task: 'example', mode: 'verify', project: 'relative' }));
});

test('project evidence requires an ignored repository-root directory', () => {
  const repo = path.join(root, 'repo'); fs.mkdirSync(repo);
  execFileSync('git', ['init', '-q', repo]);
  assert.throws(() => initRun({ task: 'test', mode: 'verify', project: repo }));
  fs.writeFileSync(path.join(repo, '.gitignore'), '.work/\n');
  assert.ok(initRun({ task: 'test', mode: 'verify', project: repo }).startsWith(path.join(fs.realpathSync(repo), '.work/web-task/')));
});

test('rejects >3 concurrency and duplicate jobs before executing', async () => {
  await assert.rejects(runBatch({ concurrency: 4, jobs: [] }));
  const j = { id: 'same', command: 'true', timeoutMs: 1000 };
  await assert.rejects(runBatch({ jobs: [j, j] }));
});

test('eight jobs overlap but at most three; failures and timeouts are explicit', async () => {
  const jobs = Array.from({ length: 8 }, (_, i) => ({ id: `job${i}`, command: 'sleep 0.15', timeoutMs: 3000 }));
  const results = await runBatch({ concurrency: 3, jobs });
  assert.equal(results.filter(r => r.status === 'passed').length, 8);
  const events = results.flatMap(r => [[Date.parse(r.startedAt), 1], [Date.parse(r.endedAt), -1]])
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  let active = 0, maximum = 0;
  for (const [, delta] of events) { active += delta; maximum = Math.max(maximum, active); }
  assert.equal(maximum, 3);
  const failures = await runBatch({ jobs: [{ id: 'fail', command: 'exit 2', timeoutMs: 1000 }, { id: 'timeout', command: 'sleep 2', timeoutMs: 50 }] });
  assert.deepEqual(failures.map(r => r.status), ['failed', 'timeout']);
});
