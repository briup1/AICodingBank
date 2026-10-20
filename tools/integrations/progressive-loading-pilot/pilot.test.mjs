import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHooks, pythonFile, pythonExecution } from './plugin.mjs';

function fixture() {
  const loaded = [], events = [];
  const rules = [
    { id: 'python-edit-v1', matches: pythonFile },
    { id: 'python-run-v1', matches: pythonExecution },
  ].map(rule => ({ ...rule, load: async () => { loaded.push(rule.id); return `PRIVATE_${rule.id}`; } }));
  const hooks = createHooks(rules, event => events.push(event));
  const call = (tool, args, sessionID = 'a') => hooks['tool.execute.before'](
    { tool, sessionID, callID: String(events.length) }, { args });
  const model = async (sessionID = 'a') => {
    const output = { system: ['base'] };
    await hooks['experimental.chat.system.transform']({ sessionID }, output);
    return output.system.join('\n');
  };
  return { loaded, events, call, model };
}

test('unrelated files and mentions do not load any body', async () => {
  const f = fixture();
  await f.call('write', { filePath: 'guide.md' });
  await f.call('bash', { command: 'echo python' });
  assert.equal(await f.model(), 'base');
  assert.deepEqual(f.loaded, []);
});

test('first Python edit is blocked, then only edit body is prepared, retry allowed', async () => {
  const f = fixture();
  await assert.rejects(f.call('apply_patch', { patchText: '*** Update File: src/a.py\n@@\n-x\n+y' }), /PENDING/);
  assert.deepEqual(f.loaded, []);
  const prompt = await f.model();
  assert.match(prompt, /PRIVATE_python-edit-v1/);
  assert.doesNotMatch(prompt, /python-run/);
  await f.call('edit', { filePath: 'src/a.py' });
  assert.deepEqual(f.events.map(e => e.event), ['blocked', 'prepared-for-model', 'allowed']);
});

test('direct execution triggers without reading a Python file', async () => {
  const f = fixture();
  await assert.rejects(f.call('bash', { command: 'uv run --offline script.py' }), /PENDING/);
  assert.match(await f.model(), /PRIVATE_python-run-v1/);
  assert.deepEqual(f.loaded, ['python-run-v1']);
  await f.call('bash', { command: 'python3 -V' });
});

test('parallel first calls stay blocked until a later model preparation', async () => {
  const f = fixture();
  const results = await Promise.allSettled([
    f.call('write', { filePath: 'a.py' }),
    f.call('write', { filePath: 'b.py' }),
    f.call('bash', { command: 'python -V' }),
  ]);
  assert.ok(results.every(result => result.status === 'rejected'));
  await f.model();
  assert.deepEqual(f.loaded, ['python-edit-v1', 'python-run-v1']);
});

test('session isolation and reinjection on later requests', async () => {
  const f = fixture();
  await assert.rejects(f.call('bash', { command: 'python -V' }), /PENDING/);
  await f.model();
  assert.equal(await f.model('b'), 'base');
  await assert.rejects(f.call('bash', { command: 'python -V' }, 'b'), /PENDING/);
  assert.match(await f.model('a'), /PRIVATE_python-run-v1/);
});

test('matcher coverage is explicitly bounded', () => {
  assert.equal(pythonFile('read', { filePath: 'a.py' }), false);
  assert.equal(pythonExecution('bash', { command: '/usr/bin/python3 -V' }), false);
  assert.equal(pythonExecution('bash', { command: 'env X=1 python -V' }), false);
  assert.equal(pythonExecution('bash', { command: 'echo ok && python -V' }), false);
});
