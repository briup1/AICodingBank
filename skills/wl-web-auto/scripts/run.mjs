#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';

export function initRun({ task, mode, project, runRoot, stateHome = process.env.XDG_STATE_HOME || path.join(os.homedir(), '.local/state') }) {
  if (!/^[a-z0-9][a-z0-9_-]{0,79}$/.test(task || '')) throw new Error('task must be a lowercase slug');
  if (!['execute', 'verify', 'mixed'].includes(mode)) throw new Error('invalid mode');
  let root;
  if (runRoot !== undefined) {
    if (!path.isAbsolute(runRoot)) throw new Error('run root must be absolute');
    if (project) throw new Error('choose run root or project, not both');
    root = runRoot;
  } else if (project) {
    if (!path.isAbsolute(project)) throw new Error('project must be absolute');
    root = fs.realpathSync(project);
    const gitRoot = fs.realpathSync(execFileSync('git', ['-C', root, 'rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim());
    if (root !== gitRoot) throw new Error('project must be repository root');
    execFileSync('git', ['-C', root, 'check-ignore', '-q', '--', '.work/web-task/probe/run.json']);
    root = path.join(root, '.work/web-task');
  } else {
    if (!path.isAbsolute(stateHome)) throw new Error('state home must be absolute');
    root = path.join(stateHome, 'web-task/runs');
  }
  const parent = path.join(root, task);
  fs.mkdirSync(parent, { recursive: true, mode: 0o700 });
  const dir = fs.mkdtempSync(path.join(parent, new Date().toISOString().replace(/[:.]/g, '-') + '-'));
  fs.mkdirSync(path.join(dir, 'evidence'), { mode: 0o700 });
  if (mode !== 'execute') fs.mkdirSync(path.join(dir, 'screenshots'), { mode: 0o700 });
  fs.writeFileSync(path.join(dir, 'run.json'), JSON.stringify({ task, mode, createdAt: new Date().toISOString(), concurrencyLimit: 3, scenarios: [] }, null, 2), { mode: 0o600 });
  fs.writeFileSync(path.join(dir, 'result.md'), '# 网页任务结果\n\n状态：未执行。\n', { mode: 0o600 });
  return dir;
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  try {
    if (process.argv[2] !== 'init') throw new Error('usage: run.mjs init --task slug --mode execute|verify|mixed [--project /absolute/root | --run-root /absolute/root]');
    const opts = {};
    for (let i = 3; i < process.argv.length; i += 2) {
      const key = process.argv[i];
      if (!['--task', '--mode', '--project', '--run-root'].includes(key) || !process.argv[i + 1]) throw new Error('invalid argument');
      opts[key === '--run-root' ? 'runRoot' : key.slice(2)] = process.argv[i + 1];
    }
    console.log(initRun(opts));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
