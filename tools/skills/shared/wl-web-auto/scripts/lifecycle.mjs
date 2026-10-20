#!/usr/bin/env node
// Task ownership stays outside business evidence; never persist command arguments or page contents.
import { mkdir, readFile, writeFile, rename, rmdir } from 'node:fs/promises';
import { homedir } from 'node:os';
import { resolve, join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';

export const ROOT = join(process.env.XDG_STATE_HOME || join(homedir(), '.local/state'), 'opencli-tasks');
const SUPPORTED = { daemonVersion: '1.8.8', extensionVersion: '1.0.24' };
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const COMMANDS = new Set('open back scroll state frames screenshot console find get click type hover focus dblclick check uncheck upload drag fill select keys dialog wait eval extract network'.split(' '));

export async function request(path, body) {
  const response = await fetch(`http://127.0.0.1:19825${path}`, {
    method: body ? 'POST' : 'GET',
    headers: { 'X-OpenCLI': '1', ...(body && { 'Content-Type': 'application/json' }) },
    ...(body && { body: JSON.stringify(body) }),
    signal: AbortSignal.timeout(15000),
  });
  const data = await response.json();
  if (!response.ok || data.ok !== true) throw new Error(`OpenCLI ${path} failed (${data.errorCode || response.status})`);
  return data;
}

export function cli(args, env = process.env, quiet = false) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn('opencli', args, { env, stdio: quiet ? ['ignore', 'ignore', 'inherit'] : 'inherit' });
    child.once('error', reject);
    child.once('exit', (code, signal) => resolvePromise(code ?? (signal === 'SIGINT' ? 130 : 143)));
  });
}

export function createLifecycle({ root = ROOT, transport = request, runCli = cli } = {}) {
  async function save(state) {
    const file = join(root, `${state.id}.json`);
    const temp = `${file}.${randomUUID()}.tmp`;
    await writeFile(temp, JSON.stringify(state, null, 2) + '\n', { mode: 0o600 });
    await rename(temp, file);
  }
  async function load(id) {
    if (!UUID.test(id || '')) throw new Error('Invalid task id');
    const state = JSON.parse(await readFile(join(root, `${id}.json`), 'utf8'));
    if (state.id !== id || state.session !== `wl-${id}` || !['owned', 'bound'].includes(state.kind)) throw new Error('Invalid task ownership record');
    return state;
  }
  async function locked(id, fn) {
    const lock = join(root, `${id}.lock`);
    if (!UUID.test(id || '')) throw new Error('Invalid task id');
    try { await mkdir(lock, { mode: 0o700 }); }
    catch (error) {
      if (error.code === 'EEXIST') throw new Error('Task is busy or interrupted; inspect before recovering its lock');
      throw error;
    }
    try { return await fn(await load(id)); }
    finally { await rmdir(lock); }
  }
  async function health(contextId) {
    const status = await transport('/status');
    if (status.daemonVersion !== SUPPORTED.daemonVersion) throw new Error('Unsupported OpenCLI daemon version; no cleanup attempted');
    const profiles = status.profiles || [];
    const profile = contextId ? profiles.find(p => p.contextId === contextId) : profiles.length === 1 ? profiles[0] : null;
    if (!profile || profile.extensionVersion !== SUPPORTED.extensionVersion) throw new Error('Select a connected context with supported extension 1.0.24');
    return { status, contextId: profile.contextId };
  }
  async function command(state, action, params = {}) {
    const { status } = await health(state.contextId);
    if (action === 'close-window' && (status.pending > 0 || (status.commandResultUnknown ?? 0) > (state.unknownBaseline ?? 0))) {
      throw new Error('Bridge has in-flight or newly unknown outcomes; cleanup requires reconciliation');
    }
    return transport('/command', { id: randomUUID(), action, session: state.session, surface: 'browser', contextId: state.contextId, ...params });
  }
  async function tabs(state) {
    const result = await command(state, 'tabs', { op: 'list' });
    if (!Array.isArray(result.data)) throw new Error('Invalid tab-list response');
    return result.data;
  }
  async function begin({ task, owner = process.env.OPENCLI_TASK_OWNER || '', contextId, kind = 'owned' }) {
    if (!/^[a-z0-9][a-z0-9_-]{0,79}$/.test(task || '') || !['owned', 'bound'].includes(kind)) throw new Error('Invalid task slug or session kind');
    if (owner.length > 200 || /[\r\n]/.test(owner)) throw new Error('Invalid owner');
    await mkdir(root, { recursive: true, mode: 0o700 });
    const id = randomUUID();
    // Do not let CLI auto-replace a shared daemon before checking its version/route.
    let route;
    try { route = await health(contextId); }
    catch (error) {
      if (error.cause?.code !== 'ECONNREFUSED') throw error;
      // Starting a stopped Bridge is allowed; this command creates no tab.
      if (await runCli([...(contextId ? ['--profile', contextId] : []), 'browser', `wl-${id}`, 'tab', 'list'], process.env, true) !== 0) throw new Error('Browser Bridge is not ready');
      route = await health(contextId);
    }
    const state = { id, task, owner, kind, session: `wl-${id}`, contextId: route.contextId, status: 'ready', unknownBaseline: route.status.commandResultUnknown ?? 0, createdAt: new Date().toISOString() };
    await save(state);
    return state;
  }
  async function exec(id, args) {
    return locked(id, async state => {
      if (!['ready', 'active'].includes(state.status)) throw new Error(`Task is ${state.status}; no command sent`);
      const [action] = args;
      if (args.includes('--')) throw new Error('Nested end-of-options is not supported');
      if (!(COMMANDS.has(action) || (action === 'bind' && state.kind === 'bound' && !state.bindAttempted))) throw new Error('Unsupported task command; use one session per tab, finish for cleanup, or hold for handoff');
      if (state.kind === 'bound' && action !== 'bind') {
        if (!state.boundConfirmed) throw new Error('Bind the borrowed tab first; an unconfirmed bind cannot be retried blindly');
        if (!(await tabs(state)).length) throw new Error('Borrowed tab lease is gone; no business command sent');
      }
      // Explicit page selectors may target a different task in a shared Chrome window.
      if (args.some(a => /^--(?:tab|profile|session|window)(?:=|$)/.test(a))) throw new Error('Task owns its profile/session/tab routing; do not override it');
      await health(state.contextId);
      state.status = 'active';
      if (action === 'bind') { state.bindAttempted = true; state.boundConfirmed = false; }
      await save(state); // Record intent before starting a possibly failing browser command.
      const code = await runCli(['--profile', state.contextId, 'browser', state.session, ...args], { ...process.env, OPENCLI_BROWSER_IDLE_TIMEOUT: '600' });
      state.lastExitCode = code;
      if (action === 'bind' && code === 0) state.boundConfirmed = (await tabs(state)).length === 1;
      await save(state);
      if (action === 'bind' && code === 0 && !state.boundConfirmed) throw new Error('Binding has no confirmed tab lease; no business command allowed');
      return code;
    });
  }
  async function finish(id) {
    return locked(id, async state => {
      if (state.status === 'released') return state;
      if (state.status === 'held') return state;
      try {
        // Raw native Bridge commands avoid CLI close's swallowed errors and never spawn a daemon for cleanup.
        await command(state, 'close-window');
        const remaining = await tabs(state);
        if (remaining.length) throw new Error('Session still exposes tabs after release');
        state.status = 'released';
        state.releaseConfirmed = true; // Lease-level only: the native extension may swallow physical tab-close errors.
        state.pageCleanup = 'not-independently-verified';
        state.container = state.kind === 'owned' ? 'may-retain-native-blank-placeholder' : state.boundConfirmed ? 'user-tab-preserved' : 'borrowed-binding-unconfirmed';
        state.daemon = 'shared-retained';
        delete state.error;
      } catch (error) {
        state.status = 'cleanup-failed';
        state.releaseConfirmed = false;
        state.error = error.message;
      }
      await save(state);
      if (!state.releaseConfirmed) throw new Error(`Cleanup incomplete for ${state.id}: ${state.error}`);
      return state;
    });
  }
  async function hold(id, reason) {
    if (!reason?.trim() || reason.length > 300) throw new Error('A short non-sensitive handoff reason is required');
    return locked(id, async state => {
      if (!['ready', 'active'].includes(state.status)) throw new Error('Only live tasks can be handed off');
      state.status = 'held';
      state.handoffReason = reason;
      await save(state);
      return state;
    });
  }
  async function resume(id) {
    return locked(id, async state => {
      if (state.status !== 'held') throw new Error('Task is not held');
      state.status = 'active';
      delete state.handoffReason;
      await save(state);
      return state;
    });
  }
  return { begin, exec, finish, hold, resume, status: load };
}

// The child is the whole task, not one browser action. Always await it before releasing its session.
export async function runTask(lifecycle, task, executable, args, { spawnTask = spawn, signals = process } = {}) {
  const state = await lifecycle.begin({ task });
  let code = 1;
  let cleanupError;
  const handlers = new Map();
  let child;
  let interruptedCode;
  let taskError;
  try {
    code = await new Promise((resolvePromise, reject) => {
      child = spawnTask(executable, args, { stdio: 'inherit', env: { ...process.env, OPENCLI_TASK_ID: state.id, OPENCLI_TASK_SESSION: state.session, OPENCLI_BROWSER_IDLE_TIMEOUT: '600' } });
      for (const [signal, exitCode] of [['SIGINT', 130], ['SIGTERM', 143]]) {
        const handler = () => { interruptedCode = exitCode; child.kill(signal); };
        handlers.set(signal, handler);
        signals.on(signal, handler);
      }
      child.once('error', reject);
      child.once('exit', (exitCode, signal) => resolvePromise(interruptedCode ?? (signal ? (signal === 'SIGINT' ? 130 : 143) : exitCode ?? code)));
    });
  } catch (error) {
    taskError = error;
  } finally {
    for (const [signal, handler] of handlers) signals.removeListener(signal, handler);
    try { await lifecycle.finish(state.id); } catch (error) { cleanupError = error; }
  }
  if (cleanupError) console.error(cleanupError.message);
  if (taskError) throw taskError;
  return code || (cleanupError ? 1 : 0);
}

export async function main(args) {
  const lifecycle = createLifecycle();
  const [action, id, ...rest] = args;
  if (action === 'run') {
    if (rest[0] !== '--' || !rest[1]) throw new Error('run <task> -- <executable> [args]');
    process.exitCode = await runTask(lifecycle, id, rest[1], rest.slice(2));
  } else if (action === 'begin') {
    if (rest.length > 2) throw new Error('begin <task> [owned|bound] [contextId]');
    console.log(JSON.stringify(await lifecycle.begin({ task: id, kind: rest[0] || 'owned', contextId: rest[1] })));
  } else if (action === 'exec') {
    if (rest[0] !== '--') throw new Error('exec <id> -- <browser-command> [args]');
    process.exitCode = await lifecycle.exec(id, rest.slice(1));
  } else if (['finish', 'status', 'resume'].includes(action) && !rest.length) {
    console.log(JSON.stringify(await lifecycle[action](id)));
  } else if (action === 'hold') {
    console.log(JSON.stringify(await lifecycle.hold(id, rest.join(' '))));
  } else throw new Error('Usage: lifecycle.mjs begin|exec|finish|hold|resume|status|run');
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main(process.argv.slice(2)).catch(error => { console.error(error.message); process.exitCode = 1; });
}
