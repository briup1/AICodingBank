import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { initRun } from './run.mjs';
import { runBatch } from './batch.mjs';

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'wl-web-auto-test-'));
process.on('exit', () => fs.rmSync(root, { recursive: true, force: true }));

test('run paths isolate tasks, execute does not create screenshots, invalid paths rejected', () => {
  const dir = initRun({ task: 'example', mode: 'execute', stateHome: root });
  assert.ok(dir.startsWith(path.join(root, 'web-task/runs/example/')));
  assert.equal(fs.existsSync(path.join(dir, 'screenshots')), false);
  assert.ok(fs.existsSync(path.join(initRun({ task: 'example', mode: 'verify', stateHome: root }), 'screenshots')));
  assert.throws(() => initRun({ task: '../escape', mode: 'verify', stateHome: root }));
  assert.throws(() => initRun({ task: 'example', mode: 'verify', project: 'relative' }));
});

test('explicit external run root appends unique runs and supports CLI', () => {
  const runRoot = path.join(root, 'delivery/project');
  const first = initRun({ task: 'requirement', mode: 'verify', runRoot, stateHome: root });
  const second = initRun({ task: 'requirement', mode: 'verify', runRoot, stateHome: root });
  assert.ok(first.startsWith(path.join(runRoot, 'requirement/')));
  assert.notEqual(first, second);
  assert.ok(fs.existsSync(path.join(first, 'run.json')));
  assert.ok(fs.existsSync(path.join(first, 'screenshots')));
  assert.throws(() => initRun({ task: 'requirement', mode: 'verify', runRoot: 'relative', stateHome: root }));
  assert.throws(() => initRun({ task: 'requirement', mode: 'verify', runRoot, project: root, stateHome: root }));
  const cli = execFileSync(process.execPath, [new URL('./run.mjs', import.meta.url).pathname,
    'init', '--task', 'requirement', '--mode', 'verify', '--run-root', runRoot],
    { encoding: 'utf8', env: { ...process.env, XDG_STATE_HOME: root } }).trim();
  assert.ok(cli.startsWith(path.join(runRoot, 'requirement/')));
});

test('project evidence requires an ignored repository-root directory', () => {
  const repo = path.join(root, 'repo'); fs.mkdirSync(repo);
  execFileSync('git', ['init', '-q', repo]);
  assert.throws(() => initRun({ task: 'test', mode: 'verify', project: repo }));
  fs.writeFileSync(path.join(repo, '.gitignore'), '.work/\n');
  assert.ok(initRun({ task: 'test', mode: 'verify', project: repo }).startsWith(path.join(fs.realpathSync(repo), '.work/web-task/')));
});

test('test run attaches without duplicate files or overwriting existing progress', () => {
  const dir = path.join(root, 'test-runs', '20261020-001');
  fs.mkdirSync(dir, { recursive: true });
  const baseline = { schemaVersion: 1, runId: '20261020-001', taskId: 'R-123',
    cases: { path: 'docs/cases.md', version: '0.4', sha256: 'a'.repeat(64) },
    items: [{ caseId: 'TC-001', status: '失败', actual: 'observed mismatch' }] };
  const file = path.join(dir, 'result.json');
  fs.writeFileSync(file, JSON.stringify(baseline));
  const before = fs.readFileSync(file);
  assert.equal(initRun({ task: 'r-123', mode: 'verify', testRun: dir }), fs.realpathSync(dir));
  assert.deepEqual(fs.readdirSync(dir), ['result.json']);
  assert.deepEqual(fs.readFileSync(file), before);
  const cli = execFileSync(process.execPath, [new URL('./run.mjs', import.meta.url).pathname,
    'init', '--task', 'r-123', '--mode', 'mixed', '--test-run', dir], { encoding: 'utf8' }).trim();
  assert.equal(cli, fs.realpathSync(dir));
  assert.deepEqual(fs.readFileSync(file), before);
  assert.throws(() => initRun({ task: 'r-123', mode: 'verify', testRun: 'relative' }));
  for (const conflict of [{ project: root }, { runRoot: root }]) {
    assert.throws(() => initRun({ task: 'r-123', mode: 'verify', testRun: dir, ...conflict }));
  }
  assert.throws(() => initRun({ task: 'r-123', mode: 'verify', testRun: path.join(root, 'missing') }));
  fs.writeFileSync(file, '{invalid');
  assert.throws(() => initRun({ task: 'r-123', mode: 'verify', testRun: dir }));
  fs.writeFileSync(file, JSON.stringify({ ...baseline, cases: { version: '0.4' } }));
  assert.throws(() => initRun({ task: 'r-123', mode: 'verify', testRun: dir }));
  assert.deepEqual(fs.readdirSync(dir), ['result.json']);
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
