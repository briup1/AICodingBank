#!/usr/bin/env node
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { homedir, tmpdir } from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { register, initMarker } from './cli.mjs';
import { manage } from './install.mjs';

const source = dirname(fileURLToPath(import.meta.url));
const sha256 = text => createHash('sha256').update(text).digest('hex');

export async function experiment(output) {
  const originalEnv = { ...process.env }, realHome = homedir();
  const observed = [join(realHome, '.codex/hooks.json'), join(realHome, '.config/dev-guard/config.json'), join(realHome, '.pi/agent/extensions/dev-guard.js'), join(realHome, '.config/opencode/plugins/dev-guard.js')];
  const manifest = join(realHome, '.local/state/dev-guard/installation.json');
  const installed = existsSync(manifest) ? JSON.parse(readFileSync(manifest, 'utf8')) : null;
  if (installed?.git?.path) observed.push(installed.git.path);
  const fingerprint = () => Object.fromEntries(observed.map(path => [path, existsSync(path) ? sha256(readFileSync(path)) : null]));
  const originalFiles = fingerprint();
  const temp = mkdtempSync(join(tmpdir(), 'dev-guard-demo-'));
  const repo = join(temp, 'repo'), origin = join(temp, 'origin.git'), emptyHooks = join(temp, 'no-hooks');
  const started = new Date().toISOString(), scenarios = [];
  let result;
  for (const key of Object.keys(process.env)) if (key.startsWith('GIT_')) delete process.env[key];
  Object.assign(process.env, {
    HOME: join(temp, 'home'), GIT_CONFIG_GLOBAL: '/dev/null', GIT_CONFIG_SYSTEM: '/dev/null',
    GIT_ALLOW_PROTOCOL: 'file', GIT_TERMINAL_PROMPT: '0',
    XDG_CONFIG_HOME: join(temp, 'config'), XDG_STATE_HOME: join(temp, 'state'), XDG_DATA_HOME: join(temp, 'data'),
    DEV_GUARD_CONFIG: join(temp, 'config/guard.json'), DEV_GUARD_STATE_DIR: join(temp, 'state/guard'),
  });
  mkdirSync(repo); mkdirSync(process.env.HOME);
  const scrub = text => String(text).replaceAll(temp, '<临时实验目录>').replaceAll(realHome, '<本机用户目录>');
  const records = [];
  function run(exe, args, { cwd = repo, input } = {}) {
    const begin = performance.now();
    const r = spawnSync(exe, args, { cwd, input, encoding: 'utf8', timeout: 15000, maxBuffer: 1024 * 1024 });
    assert.ifError(r.error);
    const record = { command: scrub([exe, ...args].join(' ')), exitCode: r.status, output: scrub((r.stdout || '') + (r.stderr || '')), elapsedMs: +(performance.now() - begin).toFixed(2) };
    records.push(record); return { ...r, record };
  }
  function git(...args) { const r = run('git', args); assert.equal(r.status, 0, r.record.output); return r.stdout.trim(); }
  function snapshot(branch) {
    const sha = git('--git-dir', origin, 'rev-parse', `refs/heads/${branch}`);
    const files = git('--git-dir', origin, 'ls-tree', '--name-only', sha).split('\n');
    return { branch, sha, files, devOnlyPresent: files.includes('dev-only.txt') };
  }
  function addScenario(id, title, expected, before, after, steps, details = {}) {
    scenarios.push({ id, title, expected, passed: true, before, after, steps, ...details });
  }
  try {
    git('init', '--initial-branch=master'); git('config', 'core.hooksPath', emptyHooks);
    git('config', 'user.name', 'Dev Guard Demo'); git('config', 'user.email', 'demo@example.invalid');
    writeFileSync(join(repo, 'base.txt'), '基线代码\n'); git('add', '.'); git('commit', '-m', 'baseline');
    const master = git('rev-parse', 'HEAD');
    git('init', '--bare', '--initial-branch=master', origin); git('remote', 'add', 'origin', origin);
    assert.equal(git('remote', 'get-url', 'origin'), origin);
    git('switch', '-c', 'feature/story/a', 'master');
    writeFileSync(join(repo, 'feature-a.txt'), '只属于需求 A 的内容\n'); git('add', '.'); git('commit', '-m', 'story A');
    git('rev-parse', 'HEAD');
    git('switch', '-c', 'feature/dev', 'master'); register(repo); const marker = initMarker(repo, 'demo-epoch', true);
    git('merge', '--no-ff', '--no-edit', 'feature/story/a');
    writeFileSync(join(repo, 'dev-only.txt'), '不应该进入 Beta 的 Dev 集成内容\n'); git('add', '.'); git('commit', '-m', 'dev-only integration');
    const dev = git('rev-parse', 'HEAD');
    let hook = installed?.git?.path;
    if (!hook || !existsSync(hook)) {
      const dir = join(temp, 'hooks'); manage('install', { home: process.env.HOME, targets: ['git'], gitHooks: dir }); hook = join(dir, 'pre-push');
    }
    git('config', 'core.hooksPath', dirname(hook));
    git('push', 'origin', 'master', 'feature/dev', marker.ref);
    git('branch', 'feature/beta', master); git('push', 'origin', 'feature/beta');

    // Positive control: a requirement also present in Dev must still promote independently.
    const normalBefore = snapshot('feature/beta');
    git('switch', 'feature/beta'); git('merge', '--no-ff', '--no-edit', 'feature/story/a');
    const normalPush = run('git', ['push', 'origin', 'feature/beta']); assert.equal(normalPush.status, 0, normalPush.record.output);
    const normalAfter = snapshot('feature/beta'); assert.notEqual(normalBefore.sha, normalAfter.sha); assert.equal(normalAfter.devOnlyPresent, false); assert.ok(normalAfter.files.includes('feature-a.txt'));
    addScenario('normal', '正常需求晋级 Beta', '允许：需求 A 已合 Dev，但需求分支本身干净', normalBefore, normalAfter, [normalPush.record], { path: '需求 A → Beta', note: 'Beta 更新成功，出现 feature-a.txt，没有 dev-only.txt。' });

    // Agent contract checks never run the rejected merge; record actual installed entry calls.
    git('switch', 'feature/story/a'); const agentHead = git('rev-parse', 'HEAD');
    const agentFilesBefore = git('ls-tree', '--name-only', 'HEAD').split('\n');
    const command = 'git merge feature/dev', adapters = [];
    const piPath = join(realHome, '.pi/agent/extensions/dev-guard.js');
    const pi = await import(pathToFileURL(existsSync(piPath) ? piPath : join(source, 'adapters/pi.mjs')));
    const handlers = {}; pi.default({ on: (event, fn) => { handlers[event] = fn; } });
    const p = await handlers.tool_call({ toolName: 'bash', input: { command } }, { cwd: repo }); assert.equal(p.block, true);
    adapters.push({ name: 'Pi', result: JSON.stringify(p), mode: '已安装入口 handler 调用；不是模型会话' });
    const ocPath = join(realHome, '.config/opencode/plugins/dev-guard.js');
    const oc = await import(pathToFileURL(existsSync(ocPath) ? ocPath : join(source, 'adapters/opencode.mjs')));
    const ocHooks = await oc.DevGuard({ directory: repo }); let ocReason;
    try { await ocHooks['tool.execute.before']({ tool: 'bash' }, { args: { command } }); } catch (error) { ocReason = error.message; }
    assert.match(ocReason || '', /Dev 禁止向外/); adapters.push({ name: 'OpenCode', result: ocReason, mode: '已安装入口 handler 调用；不是模型会话' });
    const codex = run(process.execPath, [join(source, 'adapters/codex-hook.mjs')], { input: JSON.stringify({ cwd: repo, hook_event_name: 'PreToolUse', tool_name: 'Bash', tool_input: { command } }) });
    assert.equal(codex.status, 0); const c = JSON.parse(codex.stdout); assert.equal(c.hookSpecificOutput.permissionDecision, 'deny');
    adapters.push({ name: 'Codex', result: JSON.stringify(c), mode: '实际命令 Hook 协议；不是信任审核后的完整会话' });
    const agentAfter = git('rev-parse', 'HEAD'); assert.equal(agentAfter, agentHead);
    const agentFilesAfter = git('ls-tree', '--name-only', 'HEAD').split('\n'); assert.deepEqual(agentFilesAfter, agentFilesBefore);
    addScenario('agent', '三个 Agent 的前置拒绝', '拒绝：不调用 merge 执行器', { sha: agentHead, files: agentFilesBefore, devOnlyPresent: agentFilesBefore.includes('dev-only.txt') }, { sha: agentAfter, files: agentFilesAfter, devOnlyPresent: agentFilesAfter.includes('dev-only.txt') }, [{ command, exitCode: null, output: '三个适配层均返回拒绝；未执行此 Git 命令', elapsedMs: null }], { path: 'Dev → 需求 A ×', adapters: adapters.map(a => ({ ...a, result: scrub(a.result) })), note: '需求 HEAD 完全相同。这里只证明适配层拒绝协议，不冒充三个宿主完整会话。' });

    const directBefore = snapshot('feature/beta');
    git('switch', '-c', 'direct-candidate', 'feature/beta'); git('merge', '--no-ff', '--no-edit', 'feature/dev');
    git('merge-base', '--is-ancestor', directBefore.sha, 'direct-candidate');
    const direct = run('git', ['push', 'origin', 'direct-candidate:refs/heads/feature/beta']);
    const directAfter = snapshot('feature/beta'); assert.notEqual(direct.status, 0); assert.match(direct.record.output, /Dev 禁止向外/); assert.equal(directAfter.sha, directBefore.sha); assert.equal(directAfter.devOnlyPresent, false);
    addScenario('direct', '直接污染推送被拒绝', '拒绝：即使本地已合 Dev，远端不接受', directBefore, directAfter, [direct.record], { path: 'Dev → 本地候选 → Beta ×', note: '只在临时仓库构造本地污染；真实 pre-push 识别后拒绝，远端不变。' });

    const indirectBefore = snapshot('feature/beta');
    git('branch', 'temporary-x', dev); git('switch', '-c', 'polluted-story', 'feature/beta'); git('merge', '--no-ff', '--no-edit', 'temporary-x'); git('branch', 'transfer-y', 'polluted-story');
    git('merge-base', '--is-ancestor', indirectBefore.sha, 'transfer-y');
    const indirect = run('git', ['push', 'origin', 'transfer-y:refs/heads/feature/beta']); const indirectAfter = snapshot('feature/beta');
    assert.notEqual(indirect.status, 0); assert.match(indirect.record.output, /Dev 禁止向外/); assert.equal(indirectAfter.sha, indirectBefore.sha); assert.equal(indirectAfter.devOnlyPresent, false);
    addScenario('indirect', '改名转手也不能进入 Beta', '拒绝：推送命令没有 feature/dev，仍命中标记', indirectBefore, indirectAfter, [indirect.record], { path: 'Dev → temporary-x → polluted-story → transfer-y → Beta ×', note: '候选包含当前 Beta，属于可快进更新；不是借 Git 非快进拒绝冒充 Hook 生效。' });

    // Negative control is confined to this new local repo and a separate local-remote branch.
    git('branch', 'control-unprotected', normalAfter.sha); git('push', 'origin', 'control-unprotected');
    const controlBefore = snapshot('control-unprotected'); git('config', 'core.hooksPath', emptyHooks);
    let control;
    try { control = run('git', ['push', 'origin', 'transfer-y:refs/heads/control-unprotected']); assert.equal(control.status, 0, control.record.output); }
    finally { git('config', 'core.hooksPath', dirname(hook)); }
    const controlAfter = snapshot('control-unprotected'); assert.notEqual(controlAfter.sha, controlBefore.sha); assert.equal(controlAfter.devOnlyPresent, true);
    addScenario('control', '对照组：无 Hook 就会污染', '对照：仅临时仓库的单独分支不接 Hook', controlBefore, controlAfter, [control.record], { path: '同一污染候选 → 临时无保护分支', note: '相同候选在没有 Hook 时确实成功，出现 dev-only.txt；证明拒绝来自 Hook。未修改全局 hooksPath。' });
    const graph = git('log', '--all', '--graph', '--oneline', '--decorate');
    result = { version: 1, started, finished: new Date().toISOString(), source: scrub(source), marker: { sha: marker.sha, ref: marker.ref }, hook: scrub(hook), scenarios, graph: scrub(graph), records, safety: { localFileRemoteOnly: true, networkProtocolsDisabled: true, realConfigUnchanged: true, temporaryRepositoriesDeleted: false } };
  } finally {
    process.env = originalEnv; rmSync(temp, { recursive: true, force: true });
    assert.deepEqual(fingerprint(), originalFiles, '真实 Hook/配置不应变化');
  }
  result.safety.temporaryRepositoriesDeleted = !existsSync(temp); assert.equal(result.safety.temporaryRepositoriesDeleted, true);
  output = resolve(output); mkdirSync(output, { recursive: true });
  writeFileSync(join(output, 'evidence.json'), `${JSON.stringify(result, null, 2)}\n`, { mode: 0o600 });
  const payload = JSON.stringify(result).replaceAll('<', '\\u003c');
  const template = readFileSync(join(source, 'demo-template.html'), 'utf8');
  writeFileSync(join(output, 'index.html'), template.replace('/*__EVIDENCE__*/null', payload), { mode: 0o600 });
  return { passed: scenarios.length, report: join(output, 'index.html'), evidence: join(output, 'evidence.json'), safety: result.safety };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const args = process.argv.slice(2);
    if (args.length && (args.length !== 2 || args[0] !== '--output')) throw new Error('用法：node demo.mjs [--output 证据目录]');
    const output = args[1] || join(process.env.XDG_STATE_HOME || join(homedir(), '.local/state'), 'dev-guard/demo');
    console.log(JSON.stringify(await experiment(output), null, 2));
  } catch (error) { console.error(error.stack); process.exitCode = 1; }
}
