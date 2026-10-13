#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync, renameSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { allow, checkCommand, checkPush, checkCandidate, commit, configPath, git, isAncestor, loadConfig, policyFor, ready, repoKey } from './policy.mjs';

export function saveConfig(config) {
  const path = configPath();
  mkdirSync(dirname(path), { recursive: true, mode: 0o700 });
  const temp = `${path}.${process.pid}.tmp`;
  writeFileSync(temp, `${JSON.stringify(config, null, 2)}\n`, { mode: 0o600, flag: 'wx' });
  renameSync(temp, path);
}

export function register(repo, devBranch = 'feature/dev') {
  git(repo, ['check-ref-format', `refs/heads/${devBranch}`]);
  const config = loadConfig(), commonDir = repoKey(repo);
  if (!commonDir) throw new Error('不是 Git 仓库');
  const existing = config.repos.find(p => p.commonDir === commonDir);
  if (existing) {
    if (existing.devBranch !== devBranch) throw new Error('已登记仓库的 Dev 名称不同，请人工核对配置');
    return existing;
  }
  const entry = { commonDir, devBranch, markers: [] };
  config.repos.push(entry); saveConfig(config); return entry;
}

export function initMarker(repo, id, confirmed) {
  if (!confirmed) throw new Error('初始化会新增空提交和本地 tag，需要 --confirm；不自动推送');
  if (!/^[a-z0-9][a-z0-9._-]*$/.test(id || '')) throw new Error('--id 必须是小写字母、数字、点、短横线或下划线');
  const config = loadConfig(), policy = policyFor(repo, config);
  if (!policy) throw new Error('先 register 此仓库');
  const branch = git(repo, ['symbolic-ref', '--quiet', '--short', 'HEAD']).text;
  if (branch !== policy.devBranch) throw new Error('只能在检出 Dev 的窗口初始化标记');
  if (git(repo, ['status', '--porcelain']).text) throw new Error('Dev 工作区必须干净');
  for (const state of ['MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer']) {
    const path = git(repo, ['rev-parse', '--path-format=absolute', '--git-path', state]).text;
    if (existsSync(path)) throw new Error('有进行中的 Git 操作');
  }
  const old = commit(repo, 'HEAD');
  if (policy.markers.some(m => isAncestor(repo, m.sha, old))) throw new Error('当前 Dev 已有标记，无需重复初始化');
  const ref = `refs/tags/dev-guard/${id}`;
  if (git(repo, ['show-ref', '--verify', ref], { optional: true }).status === 0) throw new Error('标记 tag 已存在');
  const tree = git(repo, ['rev-parse', 'HEAD^{tree}']).text;
  const sha = git(repo, ['commit-tree', tree, '-p', old, '-m', `chore: Dev Guard marker ${id}`]).text;
  // Record first: if the ref transaction fails, checks fail closed until initialization is repaired.
  policy.markers.push({ ref, sha }); saveConfig(config);
  git(repo, ['update-ref', '--stdin'], { input: `start\nupdate refs/heads/${branch} ${sha} ${old}\ncreate ${ref} ${sha}\nprepare\ncommit\n` });
  return { ref, sha, old, protectionStartsAt: sha, pushed: false };
}

export function syncMarkers(repo, remote, confirmed) {
  if (!confirmed) throw new Error('同步会 fetch 标记并更新本机登记，需要 --confirm');
  if (!/^[a-zA-Z0-9._-]+$/.test(remote || '')) throw new Error('--remote 必须是已配置的远端名称');
  const config = loadConfig(), policy = policyFor(repo, config);
  if (!policy) throw new Error('先 register 此仓库');
  git(repo, ['remote', 'get-url', remote]);
  git(repo, ['fetch', '--no-tags', remote, 'refs/tags/dev-guard/*:refs/tags/dev-guard/*']);
  const tags = git(repo, ['for-each-ref', '--format=%(refname) %(objectname)', 'refs/tags/dev-guard/']).text;
  if (!tags) throw new Error('没有 Dev 标记可同步');
  for (const line of tags.split('\n')) {
    const [ref, sha] = line.split(' ');
    if (!/^refs\/tags\/dev-guard\/[a-z0-9][a-z0-9._-]*$/.test(ref)) throw new Error('Dev 标记名称不符合约定');
    if (commit(repo, ref) !== sha) throw new Error('Dev 标记必须是直接指向空提交的 lightweight tag');
    const parents = git(repo, ['show', '-s', '--format=%P', sha]).text.split(' ');
    if (parents.length !== 1 || git(repo, ['rev-parse', `${sha}^{tree}`]).text !== git(repo, ['rev-parse', `${parents[0]}^{tree}`]).text) throw new Error('Dev 标记不是单父空提交');
    const existing = policy.markers.find(m => m.ref === ref);
    if (existing && existing.sha !== sha) throw new Error(`Dev 标记被改写：${ref}`);
    if (!existing) policy.markers.push({ ref, sha });
  }
  saveConfig(config); ready(repo, policy); return policy;
}

function options(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--confirm') result.confirm = true;
    else if (['--repo', '--dev', '--id', '--remote', '--target', '--source'].includes(args[i]) && args[i + 1]) result[args[i].slice(2)] = args[++i];
    else throw new Error(`未知或不完整参数：${args[i]}`);
  }
  return result;
}

export function main(args) {
  const [action, ...rest] = args;
  if (action === 'check-command') return checkCommand(JSON.parse(readFileSync(0, 'utf8')));
  if (action === 'check-push') return checkPush(process.cwd(), readFileSync(0, 'utf8'));
  const opts = options(rest), repo = resolve(opts.repo || process.cwd());
  if (action === 'register') return register(repo, opts.dev);
  if (action === 'init-marker') return initMarker(repo, opts.id, opts.confirm);
  if (action === 'sync-markers') return syncMarkers(repo, opts.remote || 'origin', opts.confirm);
  if (action === 'check-ref') {
    const policy = policyFor(repo);
    return policy ? checkCandidate(repo, policy, opts.target, opts.source) : allow('未登记仓库');
  }
  if (action === 'status') {
    const policy = policyFor(repo);
    if (!policy) return { registered: false, ready: false, config: configPath() };
    try { ready(repo, policy); return { registered: true, ready: true, ...policy }; }
    catch (error) { return { registered: true, ready: false, reason: error.message, ...policy }; }
  }
  throw new Error('用法：cli.mjs register|init-marker|sync-markers|status|check-ref [--repo PATH ...]；check-command/check-push 读取 stdin');
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const result = main(process.argv.slice(2));
    console.log(JSON.stringify(result));
    if (result.decision === 'deny') process.exitCode = 1;
  } catch (error) { console.error(`[dev-guard] ${error.message}`); process.exitCode = 1; }
}
