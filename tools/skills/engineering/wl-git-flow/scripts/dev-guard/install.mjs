#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync, mkdirSync, chmodSync, renameSync, unlinkSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { homedir } from 'node:os';
import { spawnSync } from 'node:child_process';

const root = dirname(fileURLToPath(import.meta.url));
const hash = text => createHash('sha256').update(text).digest('hex');
const quote = text => `'${text.replaceAll("'", "'\\''")}'`;
const read = path => readFileSync(path, 'utf8');
function put(path, text, mode = 0o600) {
  mkdirSync(dirname(path), { recursive: true, mode: 0o700 });
  writeFileSync(path, text, { flag: 'wx', mode });
}
function jsonWrite(path, value) {
  const temp = `${path}.${process.pid}.tmp`;
  put(temp, `${JSON.stringify(value, null, 2)}\n`); renameSync(temp, path);
}
function jsonRead(path, fallback) { return existsSync(path) ? JSON.parse(read(path)) : fallback; }

export function manage(action, { home = homedir(), targets, gitHooks } = {}) {
  home = resolve(home);
  const stateRoot = process.env.DEV_GUARD_STATE_DIR || (home === homedir() && process.env.XDG_STATE_HOME ? join(process.env.XDG_STATE_HOME, 'dev-guard') : join(home, '.local/state/dev-guard'));
  const manifestPath = join(stateRoot, 'installation.json');
  let manifest = jsonRead(manifestPath, { version: 1, files: [], codex: null, git: null });
  if (manifest.version !== 1) throw new Error('安装记录版本不支持');
  if (action === 'status') {
    const entries = manifest.files.map(file => ({ path: file.path, intact: existsSync(file.path) && hash(read(file.path)) === file.hash }));
    const codex = manifest.codex ? jsonRead(manifest.codex.path, {}).hooks?.PreToolUse?.some(g => JSON.stringify(g) === JSON.stringify(manifest.codex.group)) === true : null;
    return { manifest: manifestPath, source: root, entries, codexIntact: codex, ...manifest };
  }
  if (action === 'uninstall') {
    // Preflight all owned artifacts before changing any of them.
    for (const file of manifest.files) if (!existsSync(file.path) || hash(read(file.path)) !== file.hash) throw new Error(`入口被修改，停止卸载：${file.path}`);
    if (manifest.git?.backup && !existsSync(manifest.git.backup)) throw new Error('原 Git Hook 备份缺失，停止卸载');
    let codex;
    if (manifest.codex) {
      codex = jsonRead(manifest.codex.path, {});
      const groups = codex.hooks?.PreToolUse;
      if (!Array.isArray(groups) || !groups.some(g => JSON.stringify(g) === JSON.stringify(manifest.codex.group))) throw new Error('Codex 入口被修改，停止卸载');
    }
    for (const file of manifest.files) unlinkSync(file.path);
    if (manifest.git?.backup) renameSync(manifest.git.backup, manifest.git.path);
    if (manifest.codex) {
      codex.hooks.PreToolUse = codex.hooks.PreToolUse.filter(g => JSON.stringify(g) !== JSON.stringify(manifest.codex.group));
      if (!codex.hooks.PreToolUse.length && !manifest.codex.hadEvent) delete codex.hooks.PreToolUse;
      if (!Object.keys(codex.hooks).length && !manifest.codex.hadHooks) delete codex.hooks;
      if (!manifest.codex.existed && !Object.keys(codex).length) unlinkSync(manifest.codex.path);
      else jsonWrite(manifest.codex.path, codex);
    }
    if (existsSync(manifestPath)) unlinkSync(manifestPath);
    return { uninstalled: true, configurationAndMarkersPreserved: true };
  }
  if (action !== 'install') throw new Error('用法：install.mjs install|uninstall|status [--home PATH] [--targets pi,codex,opencode,git] [--git-hooks PATH]');
  const selected = targets || ['pi', 'codex', 'opencode'].filter(name => spawnSync(name, ['--version'], { timeout: 3000, stdio: 'ignore' }).status === 0);
  if (!selected.length) throw new Error('未发现宿主，请指定 --targets');
  if (selected.some(name => !['pi', 'codex', 'opencode', 'git'].includes(name))) throw new Error('未知安装目标');
  if (Number(process.versions.node.split('.')[0]) < 22) throw new Error('需要 Node.js 22+');
  const versions = {};
  for (const name of selected.filter(name => name !== 'git')) {
    const probe = spawnSync(name, ['--version'], { encoding: 'utf8', timeout: 3000 });
    const version = probe.stdout?.match(/\b(\d+)\.(\d+)\.(\d+)\b/);
    if (probe.status !== 0 || !version) throw new Error(`无法确认 ${name} 版本，不安装`);
    versions[name] = version[0];
    const current = version.slice(1).map(Number), floor = { pi: [1, 2, 0], codex: [0, 161, 0], opencode: [1, 18, 34] }[name];
    const firstDifference = current.findIndex((n, i) => n !== floor[i]);
    if (firstDifference >= 0 && current[firstDifference] < floor[firstDifference]) throw new Error(`${name} ${version[0]} 低于本工具核验基线，请先核对接口`);
  }
  if (selected.includes('git') && !gitHooks) throw new Error('安装 Git 入口必须显式指定 --git-hooks；不修改 core.hooksPath');
  const artifacts = [];
  for (const name of ['pi', 'opencode']) {
    if (!selected.includes(name)) continue;
    const path = name === 'pi' ? join(home, '.pi/agent/extensions/dev-guard.js') : join(home, '.config/opencode/plugins/dev-guard.js');
    const url = pathToFileURL(join(root, `adapters/${name}.mjs`)).href;
    const text = name === 'pi' ? `export { default } from ${JSON.stringify(url)};\n` : `export { DevGuard } from ${JSON.stringify(url)};\n`;
    artifacts.push({ path, text, mode: 0o600 });
  }
  let codexPlan;
  if (selected.includes('codex')) {
    const path = join(home, '.codex/hooks.json'), existed = existsSync(path);
    const content = jsonRead(path, {});
    if (content.hooks && (typeof content.hooks !== 'object' || Array.isArray(content.hooks))) throw new Error('Codex hooks 格式不支持');
    if (content.hooks?.PreToolUse && !Array.isArray(content.hooks.PreToolUse)) throw new Error('Codex PreToolUse 格式不支持');
    const group = { matcher: '^Bash$', hooks: [{ type: 'command', command: `${quote(process.execPath)} ${quote(join(root, 'adapters/codex-hook.mjs'))}`, timeout: 5, statusMessage: 'Dev Guard' }] };
    if (manifest.codex && (manifest.codex.path !== path || JSON.stringify(manifest.codex.group) !== JSON.stringify(group))) throw new Error('安装路径/源码改变，请先卸载原版本');
    if (!manifest.codex && content.hooks?.PreToolUse?.some(g => g.hooks?.some(h => h.statusMessage === 'Dev Guard'))) throw new Error('存在非本安装器管理的 Dev Guard 入口');
    if (manifest.codex && !content.hooks?.PreToolUse?.some(g => JSON.stringify(g) === JSON.stringify(group))) throw new Error('Codex 入口已被修改');
    codexPlan = { path, content, group, existed, hadHooks: !!content.hooks, hadEvent: !!content.hooks?.PreToolUse };
  }
  let gitPlan;
  if (selected.includes('git')) {
    const path = join(resolve(gitHooks), 'pre-push');
    if (manifest.git && manifest.git.path !== path) throw new Error('Git Hook 路径改变，请先卸载');
    const backup = manifest.git ? manifest.git.backup : (existsSync(path) ? `${path}.dev-guard-original` : null);
    if (!manifest.git && backup && existsSync(backup)) throw new Error('原 Hook 备份路径已占用');
    const previous = backup ? `if [ -x ${quote(backup)} ]; then\n  ${quote(backup)} "$@" < "$input" || exit $?\nfi\n` : '';
    const text = `#!/usr/bin/env bash\n# Managed by Dev Guard; preserve stdin for the existing hook.\nset -eu\ninput=$(mktemp)\ntrap 'rm -f "$input"' EXIT\ncat > "$input"\n${quote(process.execPath)} ${quote(join(root, 'cli.mjs'))} check-push < "$input" || exit 1\n${previous}`;
    gitPlan = { path, backup }; artifacts.push({ path, text, mode: 0o755, git: true });
  }
  // Detect conflicts before touching any host configuration.
  for (const artifact of artifacts) {
    const owned = manifest.files.find(f => f.path === artifact.path);
    if (owned) {
      if (!existsSync(artifact.path) || hash(read(artifact.path)) !== owned.hash || owned.hash !== hash(artifact.text)) throw new Error(`已安装入口被改写或源码位置变化：${artifact.path}`);
    } else if (existsSync(artifact.path) && !artifact.git) throw new Error(`不覆盖已有入口：${artifact.path}`);
  }
  mkdirSync(stateRoot, { recursive: true, mode: 0o700 });
  for (const artifact of artifacts) {
    if (manifest.files.some(f => f.path === artifact.path)) continue;
    const backup = artifact.git ? gitPlan.backup : null;
    if (backup) renameSync(artifact.path, backup);
    try {
      put(artifact.path, artifact.text, artifact.mode); chmodSync(artifact.path, artifact.mode);
      manifest.files.push({ path: artifact.path, hash: hash(artifact.text) });
      if (artifact.git) manifest.git = gitPlan;
      jsonWrite(manifestPath, manifest);
    } catch (error) {
      if (existsSync(artifact.path)) unlinkSync(artifact.path);
      if (backup && existsSync(backup)) renameSync(backup, artifact.path);
      throw error;
    }
  }
  if (codexPlan && !manifest.codex) {
    const { path, content, group, existed, hadHooks, hadEvent } = codexPlan;
    if (existed) put(join(stateRoot, `hooks-${Date.now()}.json.backup`), read(path));
    content.hooks ||= {}; content.hooks.PreToolUse ||= []; content.hooks.PreToolUse.push(group);
    jsonWrite(path, content);
    manifest.codex = { path, group, existed, hadHooks, hadEvent }; jsonWrite(manifestPath, manifest);
  }
  return { installed: selected, versions, source: root, manifest: manifestPath, next: 'Pi /reload；OpenCode 重启；Codex 重启并 /hooks 审核；仓库必须另行 register/init-marker' };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const [action, ...args] = process.argv.slice(2); const opts = {};
    for (let i = 0; i < args.length; i++) {
      const key = args[i]; if (!['--home', '--targets', '--git-hooks'].includes(key) || !args[i + 1]) throw new Error(`无效参数：${key}`);
      const value = args[++i]; if (key === '--targets') opts.targets = value.split(','); else opts[key === '--home' ? 'home' : 'gitHooks'] = value;
    }
    console.log(JSON.stringify(manage(action, opts), null, 2));
  } catch (error) { console.error(`[dev-guard] ${error.message}`); process.exitCode = 1; }
}
