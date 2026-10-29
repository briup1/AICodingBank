import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';

export class AuthError extends Error {
  constructor(code) { super(code); this.code = code; }
}
export const fail = code => { throw new AuthError(code); };
export const configPath = () => path.join(os.homedir(), '.config/playwright-auth/config.json');
export const statePath = () => path.join(os.homedir(), '.local/share/playwright-auth/hgj-client-beta.json');
export const expectedPath = () => path.join(os.homedir(), '.local/share/playwright-auth/expected.json');

// Private leaf directories/files must be owner-only. All ancestors must be real,
// owned by root/current user, and not writable by another account. No symlink traversal.
export function inspectPath(file, { privateLeaf = true, missing = false } = {}) {
  if (!path.isAbsolute(file) || path.normalize(file) !== file) fail('UNSAFE_PATH');
  const pieces = file.split(path.sep).filter(Boolean);
  let current = path.parse(file).root;
  for (let i = 0; i < pieces.length; i++) {
    current = path.join(current, pieces[i]);
    let s;
    try { s = fs.lstatSync(current); }
    catch (e) { if (e.code === 'ENOENT' && missing && i === pieces.length - 1) return null; fail('UNSAFE_PATH'); }
    const leaf = i === pieces.length - 1;
    if (s.isSymbolicLink() || (!leaf && !s.isDirectory())) fail('UNSAFE_PATH');
    if (s.uid !== process.getuid() && !(s.uid === 0 && !leaf)) fail('UNSAFE_OWNER');
    // Root-owned sticky temporary directory is safe as an ancestor, not as a private leaf.
    const stickyRoot = !leaf && s.uid === 0 && !!(s.mode & 0o1000);
    if ((s.mode & 0o022) && !stickyRoot) fail('UNSAFE_PERMISSIONS');
    if (leaf && privateLeaf && ((s.mode & 0o077) || s.uid !== process.getuid())) fail('UNSAFE_PERMISSIONS');
    if (leaf) return s;
  }
  fail('UNSAFE_PATH');
}

export function ensurePrivateDir(dir) {
  const parent = path.dirname(dir);
  if (!fs.existsSync(dir)) {
    inspectPath(parent, { privateLeaf: false });
    fs.mkdirSync(dir, { mode: 0o700 });
  }
  const s = inspectPath(dir);
  if (!s.isDirectory()) fail('UNSAFE_PATH');
}

export function readPrivate(file) {
  const s = inspectPath(file, { missing: true });
  if (!s) fail('STATE_MISSING');
  if (!s.isFile() || s.nlink !== 1 || s.size > 16 * 1024 * 1024) fail('UNSAFE_FILE');
  let fd;
  try {
    fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
    const actual = fs.fstatSync(fd);
    if (actual.ino !== s.ino || actual.dev !== s.dev || actual.uid !== process.getuid() || (actual.mode & 0o077) || actual.nlink !== 1) fail('UNSAFE_FILE');
    return JSON.parse(fs.readFileSync(fd, 'utf8'));
  } catch (e) { if (e instanceof AuthError) throw e; fail('STATE_CORRUPT'); }
  finally { if (fd !== undefined) fs.closeSync(fd); }
}

export function atomicPrivateWrite(file, value, { beforeRename } = {}) {
  ensurePrivateDir(path.dirname(file));
  const existing = inspectPath(file, { missing: true });
  if (existing && (!existing.isFile() || existing.nlink !== 1)) fail('UNSAFE_FILE');
  const temp = path.join(path.dirname(file), '.' + crypto.randomUUID() + '.tmp');
  let fd;
  try {
    fd = fs.openSync(temp, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_NOFOLLOW, 0o600);
    fs.writeFileSync(fd, JSON.stringify(value)); fs.fsyncSync(fd); fs.closeSync(fd); fd = undefined;
    beforeRename?.();
    inspectPath(path.dirname(file));
    const now = inspectPath(file, { missing: true });
    if (now && (!now.isFile() || now.nlink !== 1)) fail('UNSAFE_FILE');
    fs.renameSync(temp, file);
  } catch (e) { if (e instanceof AuthError) throw e; fail('STATE_WRITE_FAILED'); }
  finally { if (fd !== undefined) fs.closeSync(fd); if (fs.existsSync(temp)) fs.unlinkSync(temp); }
}

export function loadConfig(file = configPath()) {
  const c = readPrivate(file);
  if (c.consent !== true) fail('CONSENT_REQUIRED');
  if (c.environment !== 'hgj-client-beta') fail('ENVIRONMENT_REJECTED');
  if (typeof c.runtime !== 'string' || typeof c.executable !== 'string' || !path.isAbsolute(c.runtime) || !path.isAbsolute(c.executable)) fail('RUNTIME_UNAVAILABLE');
  return c;
}
export function loadRecord(c, file = statePath()) {
  if (c.consent !== true) fail('CONSENT_REQUIRED');
  if (c.environment !== 'hgj-client-beta') fail('ENVIRONMENT_REJECTED');
  const r = readPrivate(file);
  if (r.environment !== c.environment || r.version !== 1) fail('ENVIRONMENT_REJECTED');
  if (!r.expected?.userId || !r.expected?.enterpriseId) fail('IDENTITY_UNCONFIRMED');
  if (file === statePath()) {
    const baseline = readExpected(c);
    if (baseline.userId !== r.expected.userId || baseline.enterpriseId !== r.expected.enterpriseId) fail('IDENTITY_MISMATCH');
  }
  if (!Array.isArray(r.storage?.cookies) || !Array.isArray(r.storage?.origins)) fail('STATE_CORRUPT');
  return r;
}
export function readExpected(c) {
  if (c.consent !== true) fail('CONSENT_REQUIRED');
  const r = readPrivate(expectedPath());
  if (r.environment !== 'hgj-client-beta' || r.environment !== c.environment) fail('ENVIRONMENT_REJECTED');
  if (!r.userId || !r.enterpriseId) fail('IDENTITY_UNCONFIRMED');
  return { userId: r.userId, enterpriseId: r.enterpriseId };
}
export const errorCode = e => e instanceof AuthError ? e.code : 'OPERATION_FAILED';
