import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createLifecycle, runTask } from './lifecycle.mjs';

async function fixture(t, options = {}) {
  const root = await mkdtemp(join(tmpdir(), 'opencli-lifecycle-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const calls = [], cliCalls = [], sessions = new Map();
  const transport = async (path, body) => {
    calls.push({ path, body });
    if (path === '/status') return { daemonVersion: '1.8.8', pending: options.pending || 0, commandResultUnknown: options.unknown || 0, profiles: options.profiles || [{ contextId: 'ctx-a', extensionVersion: '1.0.24' }] };
    if (options.offline) throw new Error('Bridge disconnected');
    if (body.action === 'close-window') { if (!options.leaky) sessions.delete(body.session); return { ok: true, data: { closed: true } }; }
    if (body.action === 'tabs') return { ok: true, data: sessions.get(body.session) || [] };
    throw new Error('Unexpected command');
  };
  const runCli = async (args, env) => {
    cliCalls.push({ args, env });
    if (args.includes('bind') && options.bindThrows) throw new Error('Binding result unknown');
    if (args.includes('bind') && !options.cliExit) sessions.set(args[3], [{ page: 'borrowed-page' }]);
    return options.cliExit || 0;
  };
  return { lifecycle: createLifecycle({ root, transport, runCli }), root, calls, cliCalls, sessions, options };
}

test('register fresh sessions; never store business command arguments', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'task-a', owner: 'pi-one' });
  const b = await f.lifecycle.begin({ task: 'task-a', owner: 'pi-two' });
  assert.notEqual(a.session, b.session);
  await f.lifecycle.exec(a.id, ['fill', '#input', 'sensitive-input']);
  assert.equal(f.cliCalls.at(-1).env.OPENCLI_BROWSER_IDLE_TIMEOUT, '600');
  assert.deepEqual(f.cliCalls.at(-1).args.slice(0, 4), ['--profile', 'ctx-a', 'browser', a.session]);
  assert.doesNotMatch(await readFile(join(f.root, `${a.id}.json`), 'utf8'), /sensitive-input/);
});

test('cleanup is targeted, verified and idempotent; never stops shared daemon', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a' });
  const b = await f.lifecycle.begin({ task: 'b' });
  f.sessions.set(a.session, [{ page: 'page-a' }]);
  f.sessions.set(b.session, [{ page: 'page-b' }]);
  const result = await f.lifecycle.finish(a.id);
  assert.equal(result.status, 'released');
  assert.equal(result.pageCleanup, 'not-independently-verified');
  assert.equal(result.container, 'may-retain-native-blank-placeholder');
  assert.ok(f.sessions.has(b.session));
  const count = f.calls.length;
  await f.lifecycle.finish(a.id);
  assert.equal(f.calls.length, count);
  assert.ok(f.calls.every(c => c.path === '/status' || c.body.session === a.session));
  assert.equal(f.cliCalls.length, 0); // Healthy registration and cleanup never auto-start/restart the daemon.
});

test('readback mismatch and transport failure are not successful cleanup', async t => {
  const f = await fixture(t, { leaky: true });
  const a = await f.lifecycle.begin({ task: 'a' });
  f.sessions.set(a.session, [{ page: 'still-live' }]);
  await assert.rejects(f.lifecycle.finish(a.id), /Cleanup incomplete/);
  assert.equal((await f.lifecycle.status(a.id)).releaseConfirmed, false);
  f.options.leaky = false;
  assert.equal((await f.lifecycle.finish(a.id)).status, 'released');
  const b = await f.lifecycle.begin({ task: 'b' });
  f.options.offline = true;
  await assert.rejects(f.lifecycle.finish(b.id), /Bridge disconnected/);
});

test('held sessions survive finish; borrowed tabs are unbound only', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a', owner: 'pi-one', kind: 'bound' });
  await assert.rejects(f.lifecycle.exec(a.id, ['state']), /Bind/);
  await f.lifecycle.exec(a.id, ['bind']);
  const b = await f.lifecycle.begin({ task: 'b', owner: 'pi-one' });
  const c = await f.lifecycle.begin({ task: 'c', owner: 'pi-two' });
  await f.lifecycle.hold(b.id, 'User continuing login');
  const result = await f.lifecycle.finish(a.id);
  assert.equal(result.container, 'user-tab-preserved');
  assert.equal((await f.lifecycle.finish(b.id)).status, 'held');
  assert.equal((await f.lifecycle.status(b.id)).status, 'held');
  assert.equal((await f.lifecycle.status(c.id)).status, 'ready');
  await f.lifecycle.resume(b.id);
  assert.equal((await f.lifecycle.finish(b.id)).status, 'released');
});

test('routing overrides, tab mutation, wrong ids, and rebinding owned tabs are rejected', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a' });
  for (const args of [['bind'], ['tab', 'close', 'other-page'], ['state', '--tab=other-page'], ['state', '--profile', 'other-profile']]) {
    await assert.rejects(f.lifecycle.exec(a.id, args));
  }
  await assert.rejects(f.lifecycle.finish('../another-task'));
  await assert.rejects(f.lifecycle.begin({ task: '../a' }));
  assert.equal(f.cliCalls.length, 0);
});

test('a failed business command leaves cleanup available and preserves failure code', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a' });
  f.options.cliExit = 7;
  assert.equal(await f.lifecycle.exec(a.id, ['state']), 7);
  assert.equal((await f.lifecycle.finish(a.id)).status, 'released');
  assert.equal((await f.lifecycle.status(a.id)).lastExitCode, 7);
});

test('per-task locks reject overlapping commands/cleanup without touching other tasks', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a' });
  const results = await Promise.allSettled([f.lifecycle.exec(a.id, ['state']), f.lifecycle.finish(a.id)]);
  assert.equal(results.filter(r => r.status === 'fulfilled').length, 1);
  assert.match(results.find(r => r.status === 'rejected').reason.message, /busy/);
  await f.lifecycle.finish(a.id);
});

test('failed or unknown bind and pre-bind hold/resume never allow owned fallback', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a', kind: 'bound' });
  await f.lifecycle.hold(a.id, 'before binding');
  await f.lifecycle.resume(a.id);
  await assert.rejects(f.lifecycle.exec(a.id, ['state']), /Bind/);
  f.options.cliExit = 7;
  assert.equal(await f.lifecycle.exec(a.id, ['bind']), 7);
  await assert.rejects(f.lifecycle.exec(a.id, ['open', 'https://example.com']), /Bind/);
  await assert.rejects(f.lifecycle.exec(a.id, ['bind']), /Unsupported/);
  const b = await f.lifecycle.begin({ task: 'b', kind: 'bound' });
  f.options.cliExit = 0;
  f.options.bindThrows = true;
  await assert.rejects(f.lifecycle.exec(b.id, ['bind']), /unknown/);
  await assert.rejects(f.lifecycle.exec(b.id, ['state']), /Bind/);
  assert.equal((await f.lifecycle.finish(b.id)).container, 'borrowed-binding-unconfirmed');
});

test('lost borrowed lease is refused rather than silently creating an owned page', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a', kind: 'bound' });
  await f.lifecycle.exec(a.id, ['bind']);
  f.sessions.delete(a.session);
  const calls = f.cliCalls.length;
  await assert.rejects(f.lifecycle.exec(a.id, ['state']), /lease is gone/);
  assert.equal(f.cliCalls.length, calls);
});

test('pending or newly unknown commands block cleanup without releasing any session', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a' });
  f.options.pending = 1;
  await assert.rejects(f.lifecycle.finish(a.id), /in-flight/);
  f.options.pending = 0;
  f.options.unknown = 1;
  await assert.rejects(f.lifecycle.finish(a.id), /unknown/);
  assert.equal(f.calls.filter(c => c.body?.action === 'close-window').length, 0);
});

test('ambiguous profile blocks registration before CLI can auto-start anything', async t => {
  const f = await fixture(t, { profiles: [{ contextId: 'one', extensionVersion: '1.0.24' }, { contextId: 'two', extensionVersion: '1.0.24' }] });
  await assert.rejects(f.lifecycle.begin({ task: 'a' }), /Select/);
  assert.equal(f.cliCalls.length, 0);
  assert.equal((await f.lifecycle.begin({ task: 'a', contextId: 'two' })).contextId, 'two');
});

test('unsupported versions fail before browser cleanup', async t => {
  const f = await fixture(t);
  const a = await f.lifecycle.begin({ task: 'a' });
  let commands = 0;
  const lifecycle = createLifecycle({ root: f.root, transport: async path => {
    if (path !== '/status') commands++;
    return { daemonVersion: '2.0.0', profiles: [] };
  } });
  await assert.rejects(lifecycle.finish(a.id), /Unsupported/);
  assert.equal(commands, 0);
});
