import test from 'node:test';
import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import { runTask } from './lifecycle.mjs';

for (const exitCode of [0, 7]) {
  test(`whole-task runner cleans up after exit ${exitCode} without losing result`, async () => {
    const calls = [];
    const lifecycle = { begin: async () => ({ id: 'task-id', session: 'task-session' }), finish: async id => calls.push(id) };
    const code = await runTask(lifecycle, 'test', 'command', [], { spawnTask: (_cmd, _args, options) => {
      assert.equal(options.env.OPENCLI_TASK_ID, 'task-id');
      const child = new EventEmitter();
      queueMicrotask(() => child.emit('exit', exitCode, null));
      return child;
    }, signals: new EventEmitter() });
    assert.equal(code, exitCode);
    assert.deepEqual(calls, ['task-id']);
  });
}

test('SIGTERM forwards to child, waits for child exit, then cleans up', async () => {
  const events = [], signals = new EventEmitter();
  const lifecycle = { begin: async () => ({ id: 'task-id' }), finish: async () => events.push('cleanup') };
  const code = await runTask(lifecycle, 'test', 'command', [], { signals, spawnTask: () => {
    const child = new EventEmitter();
    child.kill = signal => { events.push(signal); queueMicrotask(() => { events.push('exit'); child.emit('exit', 0, null); }); };
    queueMicrotask(() => signals.emit('SIGTERM'));
    return child;
  } });
  assert.equal(code, 143);
  assert.deepEqual(events, ['SIGTERM', 'exit', 'cleanup']);
  assert.equal(signals.listenerCount('SIGTERM'), 0);
});

test('startup failure still cleans up registered session', async () => {
  let cleaned = false;
  await assert.rejects(runTask({ begin: async () => ({ id: 'task-id' }), finish: async () => { cleaned = true; } }, 'test', 'missing', [], {
    spawnTask: () => { throw new Error('ENOENT'); }, signals: new EventEmitter(),
  }), /ENOENT/);
  assert.equal(cleaned, true);
});

test('cleanup failure turns a successful task into failure, not success', async () => {
  assert.equal(await runTask({ begin: async () => ({ id: 'task-id' }), finish: async () => { throw new Error('Expected fixture cleanup failure'); } }, 'test', 'command', [], {
    spawnTask: () => { const child = new EventEmitter(); queueMicrotask(() => child.emit('exit', 0, null)); return child; }, signals: new EventEmitter(),
  }), 1);
});
