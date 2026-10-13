import { spawnSync } from 'node:child_process';
import { readFileSync, realpathSync, existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { resolve, join } from 'node:path';

export const configPath = () => process.env.DEV_GUARD_CONFIG || join(process.env.XDG_CONFIG_HOME || join(homedir(), '.config'), 'dev-guard/config.json');
export const allow = (reason = '') => ({ decision: 'allow', reason });
export const deny = reason => ({ decision: 'deny', reason });

let checkDeadline = Infinity;

export function git(cwd, args, { optional = false, input } = {}) {
  const remaining = checkDeadline - Date.now();
  if (remaining <= 0) throw new Error('检查超过 3 秒预算，请拆开操作或人工核对');
  const result = spawnSync('git', ['-C', cwd, ...args], {
    encoding: 'utf8', input, timeout: Math.max(1, Math.min(3000, remaining)), maxBuffer: 2 * 1024 * 1024,
    // Do not let a caller's Git environment redirect the policy query to another repo.
    env: {
      ...Object.fromEntries(Object.entries(process.env).filter(([key]) => !key.startsWith('GIT_') || ['GIT_CONFIG_GLOBAL', 'GIT_CONFIG_SYSTEM', 'GIT_CONFIG_NOSYSTEM'].includes(key))),
      GIT_NO_REPLACE_OBJECTS: '1',
    },
  });
  if (result.error || (result.status !== 0 && !optional)) {
    throw new Error(`Git 检查失败：${args[0]} (${result.error?.message || result.stderr.trim()})`);
  }
  return { status: result.status, text: result.stdout?.trim() || '' };
}

export function repoKey(cwd) {
  const result = git(cwd, ['rev-parse', '--path-format=absolute', '--git-common-dir'], { optional: true });
  if (result.status !== 0) return null;
  return realpathSync(result.text);
}

export function loadConfig() {
  const path = configPath();
  if (!existsSync(path)) return { version: 1, repos: [] };
  const config = JSON.parse(readFileSync(path, 'utf8'));
  if (config.version !== 1 || !Array.isArray(config.repos)) throw new Error('Dev Guard 配置格式错误');
  for (const entry of config.repos) {
    if (typeof entry.commonDir !== 'string' || typeof entry.devBranch !== 'string' || !entry.devBranch || !Array.isArray(entry.markers)) {
      throw new Error('Dev Guard 仓库配置格式错误');
    }
    if (entry.markers.some(m => !m || !/^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(m.sha) || !/^refs\/tags\/dev-guard\/[a-z0-9][a-z0-9._-]*$/.test(m.ref))) {
      throw new Error('Dev Guard 标记格式错误');
    }
  }
  return config;
}

export function policyFor(cwd, config = loadConfig()) {
  if (!config.repos.length) return null;
  const key = repoKey(cwd);
  return config.repos.find(entry => entry.commonDir === key) || null;
}

export function commit(cwd, ref) {
  if (typeof ref !== 'string' || !ref || ref.startsWith('-')) throw new Error('来源引用无效');
  return git(cwd, ['rev-parse', '--verify', '--end-of-options', `${ref}^{commit}`]).text;
}

export function isAncestor(cwd, ancestor, descendant) {
  const result = git(cwd, ['merge-base', '--is-ancestor', ancestor, descendant], { optional: true });
  if (result.status === 0) return true;
  if (result.status === 1) return false;
  throw new Error('无法确认提交祖先关系：对象缺失、查询超时或仓库错误');
}

export function ready(cwd, policy) {
  if (git(cwd, ['rev-parse', '--is-shallow-repository']).text === 'true') throw new Error('浅克隆无法完整核对血缘，请补齐历史后重试');
  if (!policy.markers.length) throw new Error('保护未就绪：尚未登记 Dev 标记');
  for (const marker of policy.markers) {
    if (commit(cwd, marker.sha) !== marker.sha) throw new Error('Dev 标记对象不匹配');
    const tag = git(cwd, ['rev-parse', '--verify', '--end-of-options', marker.ref], { optional: true });
    if (tag.status !== 0 || tag.text !== marker.sha) throw new Error(`保护未就绪：标记缺失或被改写 ${marker.ref}`);
  }
  const refs = git(cwd, ['for-each-ref', '--format=%(refname) %(objectname)', 'refs/heads/', 'refs/remotes/']).text;
  for (const line of refs.split('\n')) {
    const [ref, sha] = line.split(' ');
    if (ref === `refs/heads/${policy.devBranch}` || (ref.startsWith('refs/remotes/') && ref.split('/').slice(3).join('/') === policy.devBranch)) {
      const marked = policy.markers.some(m => isAncestor(cwd, m.sha, sha));
      // A cached remote tip preceding initialization must not prevent publishing the new marker.
      const beforeBoundary = ref.startsWith('refs/remotes/') && policy.markers.some(m => isAncestor(cwd, sha, m.sha));
      if (!marked && !beforeBoundary) throw new Error(`保护未就绪：${ref} 已重建或尚无标记，请初始化/同步后重试`);
    }
  }
}

export function checkCandidate(cwd, policy, target, source, prepared = false) {
  if (!prepared) ready(cwd, policy);
  const sha = commit(cwd, source);
  if (target === policy.devBranch) return allow();
  const symbolic = git(cwd, ['rev-parse', '--symbolic-full-name', '--verify', '--end-of-options', source], { optional: true }).text;
  if (symbolic === `refs/heads/${policy.devBranch}` || (symbolic.startsWith('refs/remotes/') && symbolic.split('/').slice(3).join('/') === policy.devBranch)) {
    return deny(`Dev 禁止向外流出：来源 ${symbolic}，目标 ${target || '(detached HEAD)'}`);
  }
  for (const marker of policy.markers) {
    if (isAncestor(cwd, marker.sha, sha)) {
      return deny(`Dev 禁止向外流出：目标 ${target || '(detached HEAD)'}，提交 ${sha} 包含标记 ${marker.ref} (${marker.sha})`);
    }
  }
  return allow();
}

export function checkPush(cwd, input) {
  const previousDeadline = checkDeadline; checkDeadline = Date.now() + 3000;
  try {
    const policy = policyFor(cwd);
    if (!policy) return allow('未登记仓库，不启用 Dev Guard');
    ready(cwd, policy);
    const checked = new Set();
    for (const line of input.split('\n').filter(line => line.trim())) {
      const fields = line.trim().split(/\s+/);
      if (fields.length !== 4 || !fields[2].startsWith('refs/') || ![fields[1], fields[3]].every(sha => /^(?:[a-f0-9]{40}|[a-f0-9]{64})$/.test(sha))) {
        throw new Error('pre-push 输入无效');
      }
      const [, sha, remoteRef] = fields;
      if (/^0+$/.test(sha)) continue;
      const identity = `${sha}:${remoteRef}`;
      if (checked.has(identity)) continue;
      checked.add(identity);
      if (remoteRef.startsWith('refs/tags/dev-guard/')) {
        const marker = policy.markers.find(m => m.ref === remoteRef && m.sha === sha);
        if (!marker) return deny('禁止推送未登记或被改写的 Dev 标记');
        continue;
      }
      // Other refs (including release tags) must not carry Dev history either.
      const target = remoteRef.startsWith('refs/heads/') ? remoteRef.slice(11) : remoteRef;
      if (target === policy.devBranch && !policy.markers.some(m => isAncestor(cwd, m.sha, commit(cwd, sha)))) {
        return deny('Dev 目标提交没有标记，禁止推送未标记的 Dev；重建后请先初始化新标记');
      }
      const result = checkCandidate(cwd, policy, target, sha, true);
      if (result.decision === 'deny') return result;
    }
    return allow();
  } catch (error) { return deny(error.message); }
  finally { checkDeadline = previousDeadline; }
}

// Deliberately not a shell interpreter: dynamic syntax on Git writes requires a separate command.
export function tokenize(command) {
  if (typeof command !== 'string' || command.length > 128 * 1024) throw new Error('命令格式无效或过长');
  const tokens = [];
  let word = '', started = false, quote = '', dynamic = false;
  const flush = () => { if (started) tokens.push(word); word = ''; started = false; };
  for (let i = 0; i < command.length; i++) {
    const c = command[i];
    if (quote === "'") { if (c === "'") quote = ''; else word += c; continue; }
    if (c === '\\' && quote !== "'") { if (i + 1 >= command.length) throw new Error('命令转义不完整'); word += command[++i]; started = true; continue; }
    if (quote === '"') {
      if (c === '"') quote = '';
      else { if (c === '$' || c === '`') dynamic = true; word += c; }
      continue;
    }
    if (c === "'" || c === '"') { quote = c; started = true; continue; }
    if (c === '$' || c === '`' || c === '*' || c === '?' || c === '~') dynamic = true;
    if (/\s/.test(c) && c !== '\n') { flush(); continue; }
    if (';&|\n<>'.includes(c)) {
      flush(); let op = c;
      if (command[i + 1] === c && c !== '\n') op += command[++i];
      tokens.push({ op }); continue;
    }
    word += c; started = true;
  }
  if (quote) throw new Error('命令引号不完整');
  flush();
  return { tokens, dynamic };
}

const passive = new Set(['status', 'log', 'diff', 'show', 'rev-parse', 'rev-list', 'merge-base', 'ls-files', 'ls-tree', 'show-ref', 'remote', 'fetch', 'ls-remote', 'add', 'commit', 'stash', 'restore', 'clean', 'tag', 'push', 'init', 'clone', 'help', 'blame', 'describe', 'reflog', 'config']);
const relevant = new Set(['merge', 'pull', 'rebase', 'switch', 'checkout', 'reset', 'branch', 'worktree', 'update-ref', 'symbolic-ref', 'cherry-pick', 'read-tree']);

function parseGit(segment, cwd) {
  let i = 1;
  while (segment[i]?.startsWith('-')) {
    if (segment[i] === '-C' && segment[i + 1]) { cwd = resolve(cwd, segment[i + 1]); i += 2; }
    else if (['--no-pager', '--paginate', '--no-optional-locks'].includes(segment[i])) i++;
    else throw Object.assign(new Error('Git 全局选项无法可靠预判，请拆成明确命令（支持 -C）'), { cwd });
  }
  return { cwd, verb: segment[i], args: segment.slice(i + 1) };
}

function parseRefs(args, valueOptions, flagOptions) {
  const refs = []; let literal = false;
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--') { literal = true; continue; }
    if (!literal && arg.startsWith('-')) {
      if (flagOptions.includes(arg)) continue;
      const [name, value] = arg.split('=', 2);
      if (valueOptions.includes(name)) { if (value === undefined && args[++i] === undefined) throw new Error('Git 参数缺少值'); continue; }
      throw new Error(`暂不支持预判选项 ${arg}，请使用明确的独立命令`);
    }
    refs.push(arg);
  }
  return refs;
}

function operation(cwd, policy, verb, args) {
  const target = git(cwd, ['symbolic-ref', '--quiet', '--short', 'HEAD'], { optional: true }).text;
  const check = (dest, ref) => checkCandidate(cwd, policy, dest, ref);
  if (verb === 'merge') {
    if (args.some(a => ['--abort', '--quit', '--continue'].includes(a))) return allow();
    const refs = parseRefs(args, ['-m', '--message', '-s', '--strategy', '-X', '--strategy-option'], ['--no-ff', '--ff', '--ff-only', '--no-edit', '--edit', '--no-commit', '--commit', '--squash', '--no-stat', '--stat', '--quiet', '-q', '--verbose', '-v', '--allow-unrelated-histories']);
    if (!refs.length) throw new Error('隐式 merge 请先解析来源，改用 git merge <明确引用>');
    for (const ref of refs) { const result = check(target, ref); if (result.decision === 'deny') return result; }
    return allow();
  }
  if (verb === 'pull') {
    // A pull fetches a future remote tip; cached refs cannot prove the incoming history is clean.
    throw new Error('pull 来源会随远端变化，无法离线保证安全；请先 git fetch，再 git merge/rebase <明确引用>');
  }
  if (verb === 'rebase') {
    if (args.some(a => ['--abort', '--quit', '--continue', '--skip'].includes(a))) return allow();
    const refs = parseRefs(args, [], ['--no-autostash', '--autostash', '--rebase-merges', '--no-rebase-merges', '--keep-empty', '--no-keep-empty']);
    if (!refs.length || refs.length > 2) throw new Error('rebase 请指定明确 upstream，复杂变基走人工审查');
    return check(refs[1] || target, refs[0]);
  }
  if (verb === 'reset') {
    if (args.includes('-p') || args.includes('--patch')) return allow();
    const separator = args.indexOf('--');
    if (separator >= 0 && separator < args.length - 1) return allow(); // Path reset does not move HEAD.
    const refs = parseRefs(args, [], ['--hard', '--soft', '--mixed', '--merge', '--keep', '--quiet', '-q']);
    if (refs.length > 1) throw new Error('reset 路径请使用 -- 明确分隔');
    return check(target, refs[0] || 'HEAD');
  }
  if (verb === 'switch' || verb === 'checkout') {
    const create = args.findIndex(a => ['-c', '-C', '-b', '-B', '--create', '--force-create', '--orphan'].includes(a));
    if (create >= 0) {
      if (args[create] === '--orphan') throw new Error('orphan 分支无法按普通血缘流程预判，请人工审查');
      const dest = args[create + 1];
      if (!dest) throw new Error('新分支名称缺失');
      const refs = parseRefs(args.filter((_, i) => i !== create && i !== create + 1), [], ['--track', '--no-track', '--force', '-f', '--discard-changes']);
      if (refs.length > 1) throw new Error('创建分支参数不明确');
      return check(dest, refs[0] || 'HEAD');
    }
    if (args.includes('--')) return allow(); // Path checkout does not create a branch.
    const refs = parseRefs(args, [], ['--detach', '-d', '--force', '-f', '--discard-changes', '--guess', '--no-guess', '--quiet', '-q', '--track', '--no-track']);
    if (refs.length === 1 && !args.includes('--detach') && !args.includes('-d')) {
      const dest = refs[0];
      const local = git(cwd, ['show-ref', '--verify', `refs/heads/${dest}`], { optional: true });
      if (local.status !== 0 && dest !== '-') {
        // Git may create a local branch implicitly from a matching remote branch.
        const remoteRefs = git(cwd, ['for-each-ref', '--format=%(refname)', 'refs/remotes/']).text.split('\n');
        for (const ref of remoteRefs.filter(ref => ref.split('/').slice(3).join('/') === dest)) {
          const result = check(dest, ref); if (result.decision === 'deny') return result;
        }
      }
    }
    // Switching an existing branch or restoring paths is not an outward transfer.
    return allow();
  }
  if (verb === 'branch') {
    if (!args.length || args.some(a => ['-d', '-D', '--delete', '-a', '-r', '--all', '--list', '--show-current', '--contains', '--merged', '--no-merged', '--set-upstream-to', '-u', '--unset-upstream'].includes(a))) return allow();
    if (args.some(a => ['-m', '-M', '--move', '-c', '-C', '--copy'].includes(a))) {
      const refs = parseRefs(args, [], ['-m', '-M', '--move', '-c', '-C', '--copy']);
      if (!refs.length || refs.length > 2) throw new Error('分支改名或复制参数不明确');
      return check(refs.at(-1), refs.length === 2 ? refs[0] : 'HEAD');
    }
    const refs = parseRefs(args, [], ['-f', '--force', '--track', '--no-track', '-v', '-vv']);
    if (!refs.length) return allow();
    if (refs.length > 2) throw new Error('分支创建参数不明确');
    return check(refs[0], refs[1] || 'HEAD');
  }
  if (verb === 'worktree') {
    if (args[0] !== 'add') return allow();
    const create = args.findIndex(a => a === '-b' || a === '-B');
    if (create < 0) throw new Error('worktree add 请明确 -b <分支> <路径> <起点>，现有分支窗口可用受控流程');
    const dest = args[create + 1];
    const refs = parseRefs(args.slice(1).filter((_, i) => i + 1 !== create && i + 1 !== create + 1), [], ['--force', '-f', '--detach', '--lock', '--no-checkout']);
    if (!dest || refs.length < 1 || refs.length > 2) throw new Error('worktree 起点不明确');
    return check(dest, refs[1] || 'HEAD');
  }
  if (verb === 'cherry-pick') {
    if (args.some(a => ['--abort', '--quit', '--continue', '--skip'].includes(a))) return allow();
    const refs = parseRefs(args, ['-m', '--mainline'], ['-x', '--no-commit', '-n', '--edit', '-e', '--ff', '--allow-empty']);
    if (!refs.length) throw new Error('cherry-pick 来源缺失');
    for (const ref of refs) { const result = check(target, ref); if (result.decision === 'deny') return result; }
    return allow();
  }
  throw new Error(`${verb} 属于底层指针/索引写操作，不能可靠预判，请走受控流程`);
}

export function checkCommand({ cwd, command }) {
  const previousDeadline = checkDeadline; checkDeadline = Date.now() + 3000;
  try {
    if (typeof cwd !== 'string' || typeof command !== 'string') throw new Error('Hook 输入缺少 cwd/command');
    // Fast path is only a performance filter, not a security boundary for hidden scripts.
    if (!/(?:^|[\s;/])git(?:\s|$)/.test(command)) return allow();
    const config = loadConfig();
    if (!config.repos.length) return allow('未登记任何仓库');
    const { tokens, dynamic } = tokenize(command);
    const segments = [[]]; const separators = [];
    for (const token of tokens) {
      if (typeof token === 'object') { separators.push(token.op); segments.push([]); }
      else segments.at(-1).push(token);
    }
    let mutations = 0;
    for (const segment of segments) {
      if (!segment.length) continue;
      if (segment[0] === 'cd') {
        if (segment.length !== 2 || dynamic || separators.some(op => op !== '&&')) throw new Error('工作目录变化无法可靠预判，请拆开命令');
        cwd = resolve(cwd, segment[1]); continue;
      }
      const exe = segment[0].split('/').at(-1);
      if (exe !== 'git') {
        if (segment.includes('git') && policyFor(cwd, config)) throw new Error('Git 包装命令无法可靠预判，请直接使用 git');
        continue;
      }
      let parsed;
      try { parsed = parseGit(segment, cwd); }
      catch (error) { if (policyFor(error.cwd || cwd, config)) throw error; continue; }
      const policy = policyFor(parsed.cwd, config);
      if (!policy) continue;
      let { verb, args } = parsed;
      const alias = git(parsed.cwd, ['config', '--get', `alias.${verb}`], { optional: true }).text;
      if (alias && !passive.has(verb) && !relevant.has(verb)) throw new Error('Git alias 不展开执行，请改用明确命令');
      if (!relevant.has(verb) && !passive.has(verb)) throw new Error(`未知 Git 操作 ${verb}，请使用明确命令`);
      const stateChange = relevant.has(verb) || ['commit', 'fetch'].includes(verb);
      if (stateChange && ++mutations > 1) throw new Error('同一命令包含多次 Git 状态变化，请拆开，避免基于旧状态预判');
      if (verb === 'push' && args.includes('--no-verify')) throw new Error('禁止显式跳过 Dev Guard pre-push');
      if (!relevant.has(verb)) continue;
      if (dynamic || separators.some(op => op !== '&&' && op !== ';' && op !== '\n')) throw new Error('动态/管道 Git 写操作无法可靠预判，请拆开命令');
      const result = operation(parsed.cwd, policy, verb, args);
      if (result.decision === 'deny') return result;
    }
    return allow();
  } catch (error) { return deny(error.message); }
  finally { checkDeadline = previousDeadline; }
}
