#!/usr/bin/env node
import { execFile, spawn } from 'node:child_process';
import { promisify } from 'node:util';
import { readFile, mkdir, rm } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const exec = promisify(execFile);
// v0.27.0 embeds localhost:4848 for Chat; use that exact origin, not just its port.
export const PORT = 4848;
export const URL = `http://localhost:${PORT}`;
export const IDLE_MS = '1800000';
const HOME = homedir();
const BINARY = join(HOME, '.node/bin/agent-browser');
const SOCKET_DIR = join(HOME, '.agent-browser');
const STATE_DIR = join(HOME, '.local/state/browser-console');

export async function processTable() {
  const { stdout } = await exec('/bin/ps', ['-axo', 'pid=,ppid=,comm=']);
  return stdout.trim().split('\n').flatMap(line => {
    const m = line.trim().match(/^(\d+)\s+(\d+)\s+(.+)$/);
    return m ? [{ pid: Number(m[1]), ppid: Number(m[2]), command: m[3] }] : [];
  });
}

export function descendants(table, root) {
  const ids = new Set([root]);
  let previous;
  do {
    previous = ids.size;
    for (const row of table) if (ids.has(row.ppid)) ids.add(row.pid);
  } while (ids.size !== previous);
  return table.filter(row => ids.has(row.pid));
}

export function validSession(name) {
  if (!/^[a-z0-9][a-z0-9_-]{0,79}$/.test(name || '') || name === 'dashboard') {
    throw new Error('会话名须为 1–80 位小写字母、数字、短横线或下划线，且不能是 dashboard。');
  }
  return name;
}

async function pidFor(name) {
  try {
    const value = (await readFile(join(SOCKET_DIR, `${name}.pid`), 'utf8')).trim();
    return /^\d+$/.test(value) ? Number(value) : null;
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

async function nativeProcess(pid) {
  if (!pid) return null;
  const row = (await processTable()).find(row => row.pid === pid);
  if (!row) return null;
  const { realpath } = await import('node:fs/promises');
  if (row.command !== await realpath(BINARY)) {
    throw new Error(`PID ${pid} 不属于已安装的 agent-browser，拒绝操作。`);
  }
  return row;
}

function environment() {
  const env = { ...process.env, AGENT_BROWSER_SOCKET_DIR: SOCKET_DIR,
    AGENT_BROWSER_IDLE_TIMEOUT_MS: IDLE_MS };
  // These inherited switches bypass normal CLI dispatch; never pass them to a client.
  delete env.AGENT_BROWSER_DAEMON;
  delete env.AGENT_BROWSER_DASHBOARD;
  delete env.AGENT_BROWSER_DASHBOARD_PORT;
  delete env.XDG_RUNTIME_DIR;
  return env;
}

async function cli(args) {
  const { stdout } = await exec(BINARY, args, {
    env: environment(), timeout: 15000, maxBuffer: 1024 * 1024,
  });
  const result = JSON.parse(stdout);
  if (!result.success) throw new Error('agent-browser 操作未成功。');
  return result.data;
}

async function portOwner() {
  try {
    const { stdout } = await exec('/usr/sbin/lsof', ['-nP', `-iTCP:${PORT}`, '-sTCP:LISTEN', '-t']);
    return [...new Set(stdout.trim().split(/\s+/).map(Number))];
  } catch (error) {
    if (error.code === 1 && !error.stdout?.trim()) return [];
    throw error;
  }
}

async function sessions() {
  const response = await fetch(`${URL}/api/sessions`, { signal: AbortSignal.timeout(2500) });
  if (!response.ok) throw new Error(`控制台返回 HTTP ${response.status}`);
  const data = await response.json();
  if (!Array.isArray(data) && !Array.isArray(data.sessions)) {
    throw new Error('控制台返回了无法识别的会话清单。');
  }
  return Array.isArray(data) ? data : data.sessions;
}

export async function status() {
  const pid = await pidFor('dashboard');
  const owner = await portOwner();
  if (!await nativeProcess(pid)) {
    if (owner.length) throw new Error(`端口 ${PORT} 被其他进程占用，未操作该进程。`);
    return { running: false, url: URL };
  }
  if (owner.length !== 1 || owner[0] !== pid) {
    throw new Error('发现其他 agent-browser Dashboard 或端口归属不符，拒绝接管。');
  }
  return { running: true, pid, url: URL, sessions: (await sessions()).length };
}

export async function withLock(action, name = 'control') {
  await mkdir(STATE_DIR, { recursive: true, mode: 0o700 });
  const lock = join(STATE_DIR, `${name}.lock`);
  try { await mkdir(lock, { mode: 0o700 }); }
  catch (error) {
    if (error.code === 'EEXIST') throw new Error(`另一个操作正在执行；如上次意外中断，请人工检查 ${name}.lock。`);
    throw error;
  }
  try { return await action(); }
  finally { await rm(lock, { recursive: true, force: true }); }
}

export async function start({ open = false } = {}) {
  return withLock(async () => {
    let current = await status();
    if (!current.running) {
      await cli(['dashboard', 'start', '--port', String(PORT), '--json']);
      for (let attempt = 0; attempt < 30; attempt++) {
        try { current = await status(); if (current.running) break; } catch { /* startup race */ }
        await new Promise(resolve => setTimeout(resolve, 150));
      }
      if (!current.running) throw new Error('控制台未就绪；没有打开不可用页面。');
    }
    if (open) await exec('/usr/bin/open', [URL]);
    return current;
  });
}

export async function stop() {
  return withLock(async () => {
    const current = await status();
    if (!current.running) return current;
    await cli(['dashboard', 'stop', '--json']);
    for (let attempt = 0; attempt < 30; attempt++) {
      if (!await nativeProcess(current.pid) && !(await portOwner()).length) {
        return { running: false, url: URL, stopped: true };
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error('控制台尚未完全退出；未关闭任何浏览器会话。');
  });
}

export async function closeSession(name) {
  validSession(name);
  const pid = await pidFor(name);
  if (!await nativeProcess(pid)) return { closed: true, alreadyStopped: true };
  const tree = descendants(await processTable(), pid);
  await cli(['--session', name, 'close', '--json']);
  for (let attempt = 0; attempt < 50; attempt++) {
    const table = await processTable();
    const remaining = tree.filter(old => table.some(row => row.pid === old.pid && row.command === old.command));
    if (!remaining.length) return { closed: true };
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error(`会话 ${name} 的进程树尚未完全退出；未执行强制终止。`);
}

export async function runTask(name, command, args) {
  validSession(name);
  if (!command) throw new Error('缺少任务命令。');
  return withLock(() => executeTask(name, command, args), `task-${name}`);
}

async function executeTask(name, command, args) {
  if (await nativeProcess(await pidFor(name))) throw new Error('会话已被占用；请换一个任务名。');
  let child;
  let signal;
  const onTerm = () => { signal = 'SIGTERM'; child?.kill('SIGTERM'); };
  const onInt = () => { signal = 'SIGINT'; child?.kill('SIGINT'); };
  process.on('SIGTERM', onTerm);
  process.on('SIGINT', onInt);
  let code;
  try {
    code = await new Promise((resolve, reject) => {
      child = spawn(command, args, { env: { ...environment(), AGENT_BROWSER_SESSION: name }, stdio: 'inherit' });
      child.once('error', reject);
      child.once('exit', value => resolve(value ?? 130));
    });
  } finally {
    process.off('SIGTERM', onTerm);
    process.off('SIGINT', onInt);
    await closeSession(name);
  }
  return signal ? 130 : code;
}

async function main() {
  const [action, ...args] = process.argv.slice(2);
  let result;
  if (action === 'start' || action === 'open') result = await start({ open: action === 'open' });
  else if (action === 'stop') result = await stop();
  else if (action === 'status') result = await status();
  else if (action === 'close' && args.length === 1) result = await closeSession(args[0]);
  else if (action === 'task' && args[1] === '--') {
    process.exitCode = await runTask(args[0], args[2], args.slice(3));
    return;
  } else throw new Error('用法：console.mjs open|start|stop|status|close <session>|task <session> -- <command> [args]');
  console.log(JSON.stringify(result));
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
