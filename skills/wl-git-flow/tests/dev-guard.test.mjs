import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync, chmodSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { checkCommand, checkPush, checkCandidate, commit, loadConfig, policyFor, ready } from '../scripts/dev-guard/policy.mjs';
import { register, initMarker, syncMarkers, saveConfig } from '../scripts/dev-guard/cli.mjs';
import { manage } from '../scripts/dev-guard/install.mjs';
import piAdapter from '../scripts/dev-guard/adapters/pi.mjs';
import { DevGuard } from '../scripts/dev-guard/adapters/opencode.mjs';

const base = mkdtempSync(join(tmpdir(), 'dev-guard-test-'));
const repo = join(base, 'repo'), origin = join(base, 'origin.git'), home = join(base, 'home');
const source = resolve(dirname(fileURLToPath(import.meta.url)), '../scripts/dev-guard');
const oldEnv = { ...process.env };
let marker, master, story, dev, installed;
function run(exe, args, opts = {}) {
  const result = spawnSync(exe, args, { encoding: 'utf8', timeout: 15000, ...opts });
  assert.ifError(result.error); return result;
}
function git(...args) {
  const result = run('git', ['-C', repo, ...args]);
  assert.equal(result.status, 0, `${args.join(' ')}\n${result.stderr}`); return result.stdout.trim();
}
const command = text => checkCommand({ cwd: repo, command: text });
const denied = result => { assert.equal(result.decision, 'deny', JSON.stringify(result)); assert.ok(result.reason); };
const allowed = result => assert.equal(result.decision, 'allow', JSON.stringify(result));
function pushLine(sha, target, local = 'refs/heads/tmp') { return `${local} ${sha} refs/heads/${target} ${'0'.repeat(40)}\n`; }

before(() => {
  // Do not inherit company hooks, credentials or user Git config into fixtures.
  for (const key of Object.keys(process.env)) if (key.startsWith('GIT_')) delete process.env[key];
  process.env.GIT_CONFIG_GLOBAL = '/dev/null'; process.env.GIT_CONFIG_SYSTEM = '/dev/null';
  process.env.DEV_GUARD_CONFIG = join(base, 'config.json');
  process.env.DEV_GUARD_STATE_DIR = join(base, 'state');
  mkdirSync(repo); mkdirSync(home);
  git('init', '--initial-branch=master');
  git('config', 'user.name', 'Dev Guard Test'); git('config', 'user.email', 'test@example.invalid');
  git('config', 'core.hooksPath', join(base, 'empty-hooks'));
  writeFileSync(join(repo, 'base.txt'), 'base\n'); git('add', '.'); git('commit', '-m', 'base'); master = git('rev-parse', 'HEAD');
  git('switch', '-c', 'feature/story/a');
  writeFileSync(join(repo, 'story.txt'), 'story\n'); git('add', '.'); git('commit', '-m', 'story'); story = git('rev-parse', 'HEAD');
  git('switch', '-c', 'feature/dev', 'master');
  register(repo); marker = initMarker(repo, 'epoch-1', true);
  git('merge', '--no-ff', '--no-edit', 'feature/story/a'); dev = git('rev-parse', 'HEAD');
  git('branch', 'temporary-x', 'feature/dev');
  git('branch', 'feature/beta', master); git('branch', 'release/test', master);
  git('switch', 'feature/story/a');
  assert.equal(run('git', ['init', '--bare', '--initial-branch=master', origin]).status, 0);
  git('remote', 'add', 'origin', origin);
  git('push', 'origin', 'master', 'feature/dev', 'feature/story/a', marker.ref);
  git('fetch', 'origin');
});
after(() => {
  process.env = oldEnv; rmSync(base, { recursive: true, force: true });
});

test('标记是空提交，正常需求同时进入 Dev/Beta 不误判', () => {
  assert.equal(git('rev-parse', `${marker.sha}^{tree}`), git('rev-parse', `${master}^{tree}`));
  allowed(checkCandidate(repo, policyFor(repo), 'feature/beta', story));
  allowed(command('git merge master'));
  git('switch', 'feature/dev'); allowed(command('git merge feature/story/a')); git('switch', 'feature/story/a');
  allowed(checkPush(repo, pushLine(story, 'feature/story/a') + pushLine(dev, 'feature/dev')));
  denied(checkPush(repo, pushLine(master, 'feature/dev')));
  assert.throws(() => initMarker(repo, 'oops', false), /confirm/);
  assert.throws(() => initMarker(repo, 'oops', true), /Dev/);
  const config = readFileSync(process.env.DEV_GUARD_CONFIG, 'utf8'); register(repo); assert.equal(readFileSync(process.env.DEV_GUARD_CONFIG, 'utf8'), config);
});

test('直接、远端、别名、SHA、旧 Dev 都在执行前阻断且 HEAD 不变', () => {
  const before = commit(repo, 'HEAD');
  for (const ref of ['feature/dev', 'origin/feature/dev', 'temporary-x', dev, marker.sha]) {
    denied(command(`git merge --no-ff --no-edit ${ref}`));
    denied(command(`git merge --squash ${ref}`));
  }
  assert.equal(commit(repo, 'HEAD'), before);
  allowed(command('git switch feature/dev')); allowed(command('git checkout feature/dev'));
  git('update-ref', 'refs/remotes/origin/polluted-remote', dev);
  denied(command('git switch polluted-remote')); denied(command('git checkout polluted-remote'));
});

test('创建分支、改名、reset、变基、worktree 和内容提取的明确来源', () => {
  for (const text of [
    'git switch -c feature/story/b feature/dev', 'git checkout -b feature/story/b feature/dev',
    'git branch feature/story/b feature/dev', 'git branch -f feature/story/a feature/dev',
    'git branch -v -f feature/story/a feature/dev',
    'git branch -m feature/dev renamed-dev', 'git reset --hard feature/dev',
    'git rebase feature/dev', 'git rebase --onto feature/dev master',
    'git worktree add -b feature/story/b /tmp/b feature/dev',
    'git cherry-pick feature/dev', 'git update-ref refs/heads/a feature/dev',
    'git symbolic-ref HEAD refs/heads/a', 'git read-tree feature/dev',
    'git reset --hard feature/dev --', 'git switch --create=feature/story/b feature/dev',
    'git checkout -bfeature/story/b feature/dev',
  ]) denied(command(text));
  allowed(command('git switch -c feature/story/b master'));
  allowed(command('git worktree add -b feature/story/b /tmp/b master'));
  allowed(command('git reset --hard master'));
  allowed(command('git reset -- base.txt'));
  allowed(command('git checkout -- base.txt'));
  allowed(command('git merge --abort'));
});

test('工作目录、shell 复合命令和无法可靠判断的写法', () => {
  denied(checkCommand({ cwd: base, command: `git -C '${repo}' merge feature/dev` }));
  denied(checkCommand({ cwd: base, command: `git -C '${repo}' -c alias.x='merge feature/dev' x` }));
  denied(checkCommand({ cwd: base, command: `cd '${repo}' && git merge feature/dev` }));
  denied(command('git pull origin feature/dev')); denied(command('git pull'));
  denied(command('git merge')); denied(command('git merge "$SOURCE"'));
  denied(command('git switch feature/dev && git merge master'));
  denied(command('git commit -m change && git branch feature/story/b'));
  denied(command('git fetch origin && git merge origin/master'));
  denied(command('git merge master | tee output'));
  denied(command('env git merge feature/dev'));
  denied(command('git -c alias.x="merge feature/dev" x'));
  denied(command('git push --no-verify origin HEAD'));
  git('config', 'alias.badmerge', 'merge feature/dev'); denied(command('git badmerge'));
  allowed(command('git add . && git commit -m "test"'));
  allowed(command('git status && git log -1'));
  allowed(command('npm test'));
});

test('相同仓库的不同 worktree 共享保护，未登记仓库不影响', () => {
  const wt = join(base, 'story-wt'); git('worktree', 'add', '-b', 'feature/story/wt', wt, 'master');
  denied(checkCommand({ cwd: wt, command: 'git merge feature/dev' }));
  const other = join(base, 'unregistered'); mkdirSync(other);
  assert.equal(run('git', ['-C', other, 'init']).status, 0);
  allowed(checkCommand({ cwd: other, command: 'git merge feature/dev' }));
});

test('浅克隆无法完整证明血缘时拒绝', () => {
  const shallow = join(base, 'shallow');
  assert.equal(run('git', ['clone', '--depth=1', `file://${origin}`, shallow]).status, 0);
  register(shallow);
  const config = loadConfig(); const entry = policyFor(shallow, config); entry.markers = [{ ...marker }]; saveConfig(config);
  denied(checkPush(shallow, pushLine(master, 'feature/story/a')));
});

test('推送检查不依赖本地分支名；非 Dev、release tag、SHA、多更新均阻断', () => {
  for (const target of ['feature/story/a', 'feature/beta', 'release/test', 'master']) denied(checkPush(repo, pushLine(dev, target)));
  denied(checkPush(repo, pushLine(story, 'feature/beta') + pushLine(dev, 'release/test')));
  denied(checkPush(repo, `HEAD ${dev} refs/tags/release/test ${'0'.repeat(40)}\n`));
  allowed(checkPush(repo, `${marker.ref} ${marker.sha} ${marker.ref} ${'0'.repeat(40)}\n`));
  denied(checkPush(repo, `${marker.ref} ${dev} ${marker.ref} ${'0'.repeat(40)}\n`));
  allowed(checkPush(repo, pushLine('0'.repeat(40), 'feature/story/a')));
  denied(checkPush(repo, 'bad input\n'));
});

test('标记缺失/改写、空登记、坏配置不会静默放行', () => {
  git('tag', '-d', 'dev-guard/epoch-1');
  denied(command('git merge master')); denied(checkPush(repo, pushLine(story, 'feature/beta')));
  git('tag', 'dev-guard/epoch-1', master); denied(command('git merge master'));
  git('tag', '-f', 'dev-guard/epoch-1', marker.sha);
  const valid = loadConfig();
  const badObject = loadConfig(); badObject.repos[0].markers[0].sha = '1'.repeat(40); saveConfig(badObject);
  denied(checkPush(repo, pushLine(story, 'feature/beta'))); saveConfig(valid);
  const saved = readFileSync(process.env.DEV_GUARD_CONFIG, 'utf8');
  const config = loadConfig(); config.repos[0].markers = []; saveConfig(config);
  denied(command('git merge master'));
  writeFileSync(process.env.DEV_GUARD_CONFIG, '{bad'); denied(command('git merge master'));
  writeFileSync(process.env.DEV_GUARD_CONFIG, saved);
});

test('三个适配层按协议拒绝，未调用命令执行，允许操作无额外拒绝', async () => {
  const handlers = {}; piAdapter({ on: (event, fn) => { handlers[event] = fn; } });
  const head = commit(repo, 'HEAD');
  const result = await handlers.tool_call({ toolName: 'bash', input: { command: 'git merge feature/dev' } }, { cwd: repo });
  assert.equal(result.block, true);
  // Execute only if the adapter allows: denied operations must never reach the executor.
  let executed = false;
  if (!result?.block) { executed = true; run('git', ['-C', repo, 'merge', 'feature/dev']); }
  assert.equal(executed, false);
  assert.equal(await handlers.tool_call({ toolName: 'read', input: {} }, { cwd: repo }), undefined);
  assert.equal(await handlers.tool_call({ toolName: 'bash', input: { command: 'git status' } }, { cwd: repo }), undefined);
  const userBash = await handlers.user_bash({ command: 'git merge feature/dev' }, { cwd: repo }); assert.equal(userBash.result.exitCode, 1);
  const hooks = await DevGuard({ directory: base });
  await assert.rejects(() => hooks['tool.execute.before']({ tool: 'bash' }, { args: { workdir: repo, command: 'git merge feature/dev' } }), /dev-guard/);
  await hooks['tool.execute.before']({ tool: 'bash' }, { args: { workdir: repo, command: 'git status' } });
  const codex = run(process.execPath, [join(source, 'adapters/codex-hook.mjs')], { input: JSON.stringify({ hook_event_name: 'PreToolUse', tool_name: 'Bash', cwd: repo, tool_input: { command: 'git merge feature/dev' } }) });
  assert.equal(codex.status, 0); assert.equal(JSON.parse(codex.stdout).hookSpecificOutput.permissionDecision, 'deny');
  const bad = run(process.execPath, [join(source, 'adapters/codex-hook.mjs')], { input: '{bad' });
  assert.equal(JSON.parse(bad.stdout).hookSpecificOutput.permissionDecision, 'deny');
  assert.equal(commit(repo, 'HEAD'), head);
});

test('隔离安装保留原配置与 Hook；重复安装幂等；入口可导入', async () => {
  mkdirSync(join(home, '.codex'), { recursive: true });
  const original = { hooks: { PreToolUse: [{ matcher: 'Bash', hooks: [{ type: 'command', command: 'echo original' }] }] }, description: 'keep me' };
  writeFileSync(join(home, '.codex/hooks.json'), JSON.stringify(original));
  const hooks = join(base, 'hooks'); mkdirSync(hooks);
  const old = `#!/bin/sh\ncat > '${join(base, 'old-hook-stdin')}'\nexit 0\n`;
  writeFileSync(join(hooks, 'pre-push'), old); chmodSync(join(hooks, 'pre-push'), 0o755);
  installed = manage('install', { home, targets: ['pi', 'codex', 'opencode', 'git'], gitHooks: hooks });
  const first = readFileSync(installed.manifest, 'utf8'); manage('install', { home, targets: ['pi', 'codex', 'opencode', 'git'], gitHooks: hooks });
  assert.equal(readFileSync(installed.manifest, 'utf8'), first);
  const config = JSON.parse(readFileSync(join(home, '.codex/hooks.json'), 'utf8'));
  assert.deepEqual(config.hooks.PreToolUse[0], original.hooks.PreToolUse[0]); assert.equal(config.hooks.PreToolUse.length, 2);
  assert.equal(typeof (await import(pathToFileURL(join(home, '.pi/agent/extensions/dev-guard.js')))).default, 'function');
  if (process.env.DEV_GUARD_PI_ROOT) {
    const { loadExtensions } = await import(pathToFileURL(join(process.env.DEV_GUARD_PI_ROOT, 'dist/core/extensions/loader.js')));
    const loaded = await loadExtensions([join(home, '.pi/agent/extensions/dev-guard.js')], repo);
    assert.deepEqual(loaded.errors, []);
    assert.equal(loaded.extensions.length, 1);
    const result = await loaded.extensions[0].handlers.get('tool_call')[0]({ toolName: 'bash', input: { command: 'git merge feature/dev' } }, { cwd: repo });
    assert.equal(result.block, true);
  }
  assert.equal(typeof (await import(pathToFileURL(join(home, '.config/opencode/plugins/dev-guard.js')))).DevGuard, 'function');
  assert.equal(run('bash', ['-n', join(hooks, 'pre-push')]).status, 0);
  assert.equal(manage('status', { home }).entries.every(entry => entry.intact), true);
  assert.equal(manage('status', { home }).codexIntact, true);
  git('config', 'core.hooksPath', hooks);
});

test('真实 git push：正常需求/Dev 允许；间接污染和显式 refspec 拒绝，远端不变', () => {
  git('push', 'origin', 'feature/story/a:refs/heads/feature/beta');
  git('switch', 'feature/beta'); git('merge', '--no-ff', '--no-edit', 'feature/story/a');
  git('push', 'origin', 'feature/beta'); git('switch', 'feature/story/a');
  assert.ok(existsSync(join(base, 'old-hook-stdin')));
  assert.match(readFileSync(join(base, 'old-hook-stdin'), 'utf8'), /refs\/heads\/feature\/beta/);
  git('push', 'origin', 'feature/dev');
  const prior = git('ls-remote', 'origin', 'refs/heads/feature/beta');
  git('switch', '-c', 'polluted-a', 'feature/beta');
  git('merge', '--no-ff', '--no-edit', 'feature/dev');
  git('branch', 'polluted-b', 'polluted-a'); git('switch', 'feature/story/a');
  const failed = run('git', ['-C', repo, 'push', 'origin', 'polluted-b:refs/heads/feature/beta']);
  assert.notEqual(failed.status, 0); assert.match(failed.stdout + failed.stderr, /Dev 禁止向外/);
  assert.equal(git('ls-remote', 'origin', 'refs/heads/feature/beta'), prior);
  const bySha = run('git', ['-C', repo, 'push', 'origin', `${dev}:refs/heads/release/test`]); assert.notEqual(bySha.status, 0);
  assert.equal(git('ls-remote', 'origin', 'refs/heads/release/test'), '');
});

test('现有流程脚本 audit 实际接入共用血缘检查', () => {
  const script = resolve(source, '../wl-git-flow.sh');
  git('branch', 'feature/story/polluted', dev);
  const audit = run('bash', [script, 'audit', '--repo', repo, '--branch', 'feature/story/polluted']);
  assert.notEqual(audit.status, 0);
  assert.match(audit.stderr, /Dev Guard rejected/);
  assert.equal(commit(repo, 'HEAD'), story);
});

test('同步不自动强改 tag；新克隆可以显式获取保护标记', () => {
  const clone = join(base, 'clone'); assert.equal(run('git', ['clone', origin, clone]).status, 0);
  register(clone); assert.throws(() => syncMarkers(clone, 'origin', false), /confirm/);
  const policy = syncMarkers(clone, 'origin', true); assert.equal(policy.markers[0].sha, marker.sha);
  denied(checkCommand({ cwd: clone, command: 'git merge origin/feature/dev' }));
});

test('Dev 重建需新标记；旧世代仍然拒绝', () => {
  git('branch', '-f', 'feature/dev', master);
  denied(command('git merge master'));
  git('switch', 'feature/dev');
  const next = initMarker(repo, 'epoch-2', true);
  git('switch', 'feature/story/a');
  denied(checkPush(repo, pushLine(dev, 'feature/beta')));
  denied(checkPush(repo, pushLine(next.sha, 'feature/beta')));
  assert.equal(policyFor(repo).markers.length, 2);
  git('update-ref', 'refs/remotes/origin/feature/dev', master);
  allowed(checkPush(repo, pushLine(next.sha, 'feature/dev'))); // Publish a new marker over a cached pre-boundary tip.
  denied(command('git merge origin/feature/dev')); // An explicit Dev source stays forbidden even before the marker.
  git('update-ref', 'refs/remotes/origin/feature/dev', dev);
});

test('卸载保留用户后加配置、恢复原 Hook；不删除仓库标记', () => {
  const path = join(home, '.codex/hooks.json'); const config = JSON.parse(readFileSync(path, 'utf8'));
  config.extra = 'user-added'; writeFileSync(path, JSON.stringify(config));
  manage('uninstall', { home });
  const restored = JSON.parse(readFileSync(path, 'utf8'));
  assert.equal(restored.extra, 'user-added'); assert.equal(restored.hooks.PreToolUse.length, 1);
  assert.match(readFileSync(join(base, 'hooks/pre-push'), 'utf8'), /old-hook-stdin/);
  assert.equal(existsSync(join(home, '.pi/agent/extensions/dev-guard.js')), false);
  assert.equal(policyFor(repo).markers.length, 2);
  git('config', 'core.hooksPath', join(base, 'empty-hooks'));
});

test('原先没有 pre-push 时重复安装和卸载同样幂等', () => {
  const state = process.env.DEV_GUARD_STATE_DIR;
  process.env.DEV_GUARD_STATE_DIR = join(base, 'no-original-state');
  const hooks = join(base, 'no-original-hooks');
  try {
    manage('install', { home, targets: ['git'], gitHooks: hooks });
    manage('install', { home, targets: ['git'], gitHooks: hooks });
    assert.equal(existsSync(join(hooks, 'pre-push.dev-guard-original')), false);
    manage('uninstall', { home }); assert.equal(existsSync(join(hooks, 'pre-push')), false);
  } finally { process.env.DEV_GUARD_STATE_DIR = state; }
});

test('不覆盖陌生入口；被改写入口停止卸载', () => {
  const otherHome = join(base, 'other-home'); const path = join(otherHome, '.pi/agent/extensions/dev-guard.js');
  mkdirSync(dirname(path), { recursive: true }); writeFileSync(path, 'user-owned');
  assert.throws(() => manage('install', { home: otherHome, targets: ['pi'] }), /不覆盖/);
  assert.equal(readFileSync(path, 'utf8'), 'user-owned');
  rmSync(path);
  manage('install', { home: otherHome, targets: ['pi'] }); writeFileSync(path, 'modified');
  assert.throws(() => manage('uninstall', { home: otherHome }), /被修改/);
});

test('Git 检查超时明确拒绝，不依赖宿主超时来阻断', () => {
  const bin = join(base, 'slow-bin'); mkdirSync(bin);
  const path = join(bin, 'git'); writeFileSync(path, '#!/bin/sh\nexec sleep 5\n'); chmodSync(path, 0o755);
  const oldPath = process.env.PATH; process.env.PATH = `${bin}:${oldPath}`;
  try { const result = command('git merge master'); denied(result); assert.match(result.reason, /失败|预算/); }
  finally { process.env.PATH = oldPath; }
});

test('耗时采样：只记录观测，不用不稳定的耗时断言', () => {
  function sample(fn, n) {
    const times = []; for (let i = 0; i < n; i++) { const start = performance.now(); fn(); times.push(performance.now() - start); }
    times.sort((a, b) => a - b); return { samples: n, medianMs: +times[Math.floor(n / 2)].toFixed(2), maxMs: +times.at(-1).toFixed(2) };
  }
  const shell = sample(() => allowed(command('npm test')), 20);
  const merge = sample(() => denied(command('git merge feature/dev')), 5);
  const push = sample(() => allowed(checkPush(repo, pushLine(story, 'feature/beta'))), 5);
  const codex = sample(() => run(process.execPath, [join(source, 'adapters/codex-hook.mjs')], { input: JSON.stringify({ hook_event_name: 'PreToolUse', tool_name: 'Bash', cwd: repo, tool_input: { command: 'npm test' } }) }), 5);
  console.log('DEV_GUARD_BENCHMARK', JSON.stringify({ historyCommits: git('rev-list', '--all', '--count'), markers: policyFor(repo).markers.length, shell, merge, push, codex }));
});
