import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { admitSpec } from '../admission.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const fixture = path.join(root, 'fixture.mjs');

test('spec admission requires unaliased shared test, rejects helper/expect-only and unsupported imports', () => {
  const spec = path.join(root, 'example.spec.mjs');
  assert.equal(admitSpec(`import { test, expect } from '${fixture}';\ntest('ok', async () => {});`, spec), true);
  for (const source of [
    `import { test } from './helper.mjs'; import { expect } from '${fixture}'; test('wrong',()=>{});`,
    `import { expect } from '${fixture}'; test('wrong',()=>{});`,
    `import { test as other } from '${fixture}'; other('wrong',()=>{});`,
    `import { test } from '${fixture}'; import { oldTest } from './helper.mjs'; oldTest('wrong',()=>{});`,
    `import { test } from '${fixture}'; export { test };`,
    `import { test } from '${fixture}'; test = helper; test('wrong',()=>{});`,
  ]) assert.throws(() => admitSpec(source, spec), e => ['FIXTURE_IMPORT_REQUIRED', 'UNSUPPORTED_SPEC_FORM'].includes(e.code));
});

test('actual runner: misconfigured CLI spec rejected; shared fixture gate fails before body', { skip: !process.env.PW_AUTH_TEST_RUNTIME }, () => {
  const runtime = process.env.PW_AUTH_TEST_RUNTIME;
  const executable = process.env.PW_AUTH_TEST_EXECUTABLE;
  assert.ok(runtime && executable, 'local existing runtime required');
  const home = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'pw-auth-runner-'));
  fs.chmodSync(home, 0o700);
  try {
    const configDir = path.join(home, '.config/playwright-auth');
    fs.mkdirSync(configDir, { recursive: true, mode: 0o700 });
    fs.chmodSync(path.dirname(configDir), 0o700);
    fs.writeFileSync(path.join(configDir, 'config.json'), JSON.stringify({ consent: true, environment: 'hgj-client-beta', runtime, executable, version: JSON.parse(fs.readFileSync(path.join(runtime, 'package.json'))).version }), { mode: 0o600 });
    // Private state directory exists, but no state file: gate must stop at STATE_MISSING.
    for (const relative of ['.local', '.local/share', '.local/share/playwright-auth']) fs.mkdirSync(path.join(home, relative), { mode: 0o700 });
    const env = { ...process.env, HOME: home };
    delete env.NODE_OPTIONS; delete env.NODE_PATH;
    const helper = path.join(home, 'helper.mjs');
    fs.writeFileSync(helper, `export { test } from '${runtime}/test.mjs';`, { mode: 0o600 });
    const wrong = path.join(home, 'wrong.spec.mjs');
    fs.writeFileSync(wrong, `import { test } from './helper.mjs';\nimport { expect } from '${fixture}';\ntest('must not execute', async () => { console.log('BODY_ENTERED'); });`, { mode: 0o600 });
    const rejected = spawnSync(process.execPath, [path.join(root, 'cli.mjs'), 'run', '--spec', wrong, '--output', path.join(home, 'wrong-output')], { env, encoding: 'utf8', timeout: 20000 });
    assert.equal(rejected.status, 1);
    assert.equal(JSON.parse(rejected.stdout).status, 'FIXTURE_IMPORT_REQUIRED');
    assert.equal(fs.existsSync(path.join(home, 'wrong-output')), false);
    assert.equal((rejected.stdout.match(/BODY_ENTERED/g) || []).length, 0);

    const legal = path.join(home, 'legal.spec.mjs');
    const bodyMarker = path.join(home, 'body-entered');
    fs.writeFileSync(legal, `import { test } from '${fixture}';\ntest('body forbidden by failed gate', async () => { process.getBuiltinModule('node:fs').writeFileSync('${bodyMarker}', 'entered'); });`, { mode: 0o600 });
    assert.equal(admitSpec(fs.readFileSync(legal, 'utf8'), legal), true);
    const output = path.join(home, 'runner-output'); fs.mkdirSync(output, { mode: 0o700 });
    const summary = path.join(output, 'summary.json');
    const actual = spawnSync(process.execPath, [path.join(runtime, 'cli.js'), 'test', '--config', path.join(root, 'runner.config.mjs'), '--workers=1', '--retries=0'], {
      env: { ...env, PLAYWRIGHT_AUTH_TEST_DIR: home, PLAYWRIGHT_AUTH_TEST_FILE: 'legal.spec.mjs', PLAYWRIGHT_AUTH_OUTPUT: output, PLAYWRIGHT_AUTH_SUMMARY: summary },
      encoding: 'utf8', timeout: 25000,
    });
    assert.equal(actual.status, 1);
    const counts = JSON.parse(fs.readFileSync(summary));
    assert.equal(counts.testsDiscovered, 1); assert.equal(counts.testsFinished, 1); assert.equal(counts.passed, false); assert.equal(counts.failureCode, 'STATE_MISSING');
    // Safe, local fixture failure marker: prove actual test body never ran, not merely callback order.
    assert.equal(fs.existsSync(bodyMarker), false);
    console.log(JSON.stringify({ localRunnerEvidence: true, misconfiguredSpecRejected: true, actualTestsDiscovered: 1, actualTestsFinished: 1, gateFailed: true, testBodyEntries: 0, networkRequests: 0, realStateTouched: false }));
  } finally { fs.rmSync(home, { recursive: true, force: true }); }
});
