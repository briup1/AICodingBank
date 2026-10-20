import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { AuthError, readPrivate, atomicPrivateWrite, inspectPath, loadRecord, loadConfig } from '../store.mjs';
import { parseIdentity, compareIdentity, validateStorage, isIdentityResponse, verifyPage, APP, LOGIN, IDENTITY } from '../identity.mjs';
import { guardedPage, runtime } from '../auth.mjs';
import { argumentsFor } from '../cli.mjs';

const rejectsCode = (fn, code) => assert.throws(fn, e => e instanceof AuthError && e.code === code);
function directory() { const d = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'pw-auth-test-')); fs.chmodSync(d, 0o700); return d; }
const identity = { code: 200, data: { userId: 'test-user', enterpriseDetailResponse: { enterpriseId: 'test-enterprise' } } };

test('identity gate distinguishes valid, missing, expired, mismatch, permission and service failures', () => {
  const expected = { userId: 'test-user', enterpriseId: 'test-enterprise' };
  assert.deepEqual(parseIdentity(200, identity), expected);
  assert.deepEqual(compareIdentity(expected, expected), { sameIdentity: true, sameEnterprise: true });
  for (const data of [null, {}, { code: 200, data: { userId: 'test-user' } }, { code: 200, data: { userId: '', enterpriseDetailResponse: { enterpriseId: 'e' } } }, { ...identity, success: false }]) rejectsCode(() => parseIdentity(200, data), 'IDENTITY_UNCONFIRMED');
  for (const status of [500, 502, 429]) rejectsCode(() => parseIdentity(status, {}), 'SERVICE_UNAVAILABLE');
  for (const body of [{ code: 401 }, { code: '401' }]) rejectsCode(() => parseIdentity(200, body), 'LOGIN_REQUIRED');
  rejectsCode(() => parseIdentity(401, {}), 'LOGIN_REQUIRED');
  rejectsCode(() => parseIdentity(403, {}), 'ACCESS_DENIED');
  rejectsCode(() => parseIdentity(200, { code: '403' }), 'ACCESS_DENIED');
  for (const wrong of [{ ...expected, userId: 'other' }, { ...expected, enterpriseId: 'other' }]) rejectsCode(() => compareIdentity(wrong, expected), 'IDENTITY_MISMATCH');
  rejectsCode(() => compareIdentity(expected, {}), 'IDENTITY_UNCONFIRMED');
});

test('identity response must be exact trusted origin/path, GET and current app frame', () => {
  const page = { url: () => APP + '/query' };
  const response = (url = IDENTITY, method = 'GET', p = page) => ({ url: () => url, request: () => ({ method: () => method, frame: () => ({ page: () => p }) }) });
  assert.equal(isIdentityResponse(response(), page), true);
  for (const r of [response(IDENTITY.replace('beta-apisix.hgj.com', 'evil.test')), response(IDENTITY + '?spoof=1'), response(IDENTITY, 'POST'), response(IDENTITY, 'GET', {})]) assert.equal(isIdentityResponse(r, page), false);
  assert.equal(isIdentityResponse(response(), { url: () => 'https://evil.test/query' }), false);
});

test('private files reject symlink, broad permissions, bad owner and corrupt/missing state', () => {
  const d = directory(), f = path.join(d, 'state.json');
  try {
    rejectsCode(() => readPrivate(f), 'STATE_MISSING');
    fs.writeFileSync(f, '{', { mode: 0o600 }); rejectsCode(() => readPrivate(f), 'STATE_CORRUPT');
    fs.chmodSync(f, 0o644); rejectsCode(() => readPrivate(f), 'UNSAFE_PERMISSIONS'); fs.chmodSync(f, 0o600);
    const link = path.join(d, 'link'); fs.symlinkSync(f, link); rejectsCode(() => readPrivate(link), 'UNSAFE_PATH');
    const folderLink = path.join(d, 'folder-link'); fs.symlinkSync(d, folderLink); rejectsCode(() => inspectPath(path.join(folderLink, 'state.json')), 'UNSAFE_PATH');
    // Local root-owned fixture usually needs privilege. Exercise owner check without changing real ownership.
    const original = process.getuid;
    process.getuid = () => original() + 100000;
    try { rejectsCode(() => readPrivate(f), 'UNSAFE_OWNER'); } finally { process.getuid = original; }
    fs.chmodSync(d, 0o755); rejectsCode(() => atomicPrivateWrite(f, {}), 'UNSAFE_PERMISSIONS');
  } finally { fs.chmodSync(d, 0o700); fs.rmSync(d, { recursive: true }); }
});

test('atomic save failure preserves previous validated file and removes temp files', () => {
  const d = directory(), f = path.join(d, 'state.json');
  try {
    atomicPrivateWrite(f, { old: true });
    rejectsCode(() => atomicPrivateWrite(f, { new: true }, { beforeRename: () => { throw Error('DO_NOT_LEAK_SECRET'); } }), 'STATE_WRITE_FAILED');
    assert.deepEqual(readPrivate(f), { old: true }); assert.deepEqual(fs.readdirSync(d), ['state.json']);
    assert.equal(fs.statSync(f).mode & 0o777, 0o600);
  } finally { fs.rmSync(d, { recursive: true }); }
});

test('consent false rejects before reading state; unknown environment and corrupt identity fail closed', () => {
  rejectsCode(() => loadRecord({ consent: false }, '/should/not/be/read'), 'CONSENT_REQUIRED');
  rejectsCode(() => loadRecord({ consent: true, environment: 'prod' }, '/should/not/be/read'), 'ENVIRONMENT_REJECTED');
  const d = directory(), f = path.join(d, 'state.json');
  try {
    atomicPrivateWrite(f, { consent: false }); rejectsCode(() => loadConfig(f), 'CONSENT_REQUIRED');
    atomicPrivateWrite(f, { version: 1, environment: 'prod' }); rejectsCode(() => loadRecord({ consent: true, environment: 'hgj-client-beta' }, f), 'ENVIRONMENT_REJECTED');
    atomicPrivateWrite(f, { version: 1, environment: 'hgj-client-beta', expected: {} }); rejectsCode(() => loadRecord({ consent: true, environment: 'hgj-client-beta' }, f), 'IDENTITY_UNCONFIRMED');
  } finally { fs.rmSync(d, { recursive: true }); }
});

test('storage allows app-only origin and Beta-applicable cookies, not arbitrary environments', () => {
  const good = { cookies: [], origins: [{ origin: APP, localStorage: [] }] };
  assert.equal(validateStorage(good), good);
  for (const origin of ['https://smart-agent.hgj.com', 'https://dev-smart-agent.hgj.com', 'https://evil.test']) rejectsCode(() => validateStorage({ cookies: [], origins: [{ origin, localStorage: [] }] }), 'ENVIRONMENT_REJECTED');
  rejectsCode(() => validateStorage({ cookies: [{ domain: '.evil.test', name: 'x', value: 'secret' }], origins: [] }), 'ENVIRONMENT_REJECTED');
});

test('failed fixture gate never hands page to body and closes its independent context', async () => {
  let entered = false, closed = false;
  const response = { status: () => 200, json: async () => ({ code: 200, data: {} }) };
  const page = { waitForResponse: async () => response, goto: async () => {}, url: () => APP + '/query', evaluate: async () => false };
  const context = { route: async () => {}, newPage: async () => page, close: async () => { closed = true; } };
  const browser = { newContext: async () => context };
  await assert.rejects(guardedPage(browser, { consent: true }, { storage: { cookies: [], origins: [] }, expected: { userId: 'u', enterpriseId: 'e' } }, async () => { entered = true; }), e => e.code === 'IDENTITY_UNCONFIRMED');
  assert.equal(entered, false); assert.equal(closed, true);
});

test('trusted login redirects/blockers differ from network/identity-response failures', async () => {
  const page = (url, { navigationFails = false, blocker = false } = {}) => ({
    waitForResponse: async () => { throw Error('controlled response timeout'); },
    goto: async () => { if (navigationFails) throw Error('controlled navigation failure'); },
    url: () => url, evaluate: async () => blocker,
  });
  for (const p of [page(LOGIN + '/login'), page(APP + '/query', { blocker: true })]) await assert.rejects(verifyPage(p), e => e.code === 'LOGIN_REQUIRED');
  for (const p of [page(APP + '/query'), page(LOGIN + '/login', { navigationFails: true })]) await assert.rejects(verifyPage(p), e => e.code === 'SERVICE_UNAVAILABLE');
  await assert.rejects(verifyPage(page('https://evil.test/login')), e => e.code === 'ENVIRONMENT_REJECTED');
});

test('CLI rejects environment/runner/project overrides, duplicate options and raw failures', () => {
  for (const args of [['check', '--env', 'prod'], ['run', '--project', 'other'], ['run', '--config', 'other'], ['check', '--parallel', '1', '--parallel', '2']]) rejectsCode(() => argumentsFor(args), 'INVALID_ARGUMENT');
  assert.equal(argumentsFor(['check', '--count', '3']).options['--count'], '3');
  rejectsCode(() => runtime({ executable: '/absent', runtime: '/absent' }), 'RUNTIME_UNAVAILABLE');
});
