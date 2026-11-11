import { randomBytes, createCipheriv, createDecipheriv } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { inspectPath, readPrivate, atomicPrivateWrite } from '../../integrations/playwright-auth/store.mjs'

export const AUTH_ROOT = join(homedir(), '.local/share/compass-platform-e2e')
const environments = ['dev', 'beta', 'prod']
function files(env, root) {
  if (!environments.includes(env)) throw new Error('AUTH_ENVIRONMENT_REJECTED')
  return { state: join(root, `${env}.json`), key: join(root, 'key.json') }
}
export function hasAuth(env, root = AUTH_ROOT) { return existsSync(files(env, root).state) }
function key(root, create = false) {
  const path = join(root, 'key.json')
  if (create && !existsSync(path)) atomicPrivateWrite(path, { value: randomBytes(32).toString('base64') })
  const value = Buffer.from(readPrivate(path).value, 'base64')
  if (value.length !== 32) throw new Error('AUTH_KEY_INVALID')
  return value
}
export function validateRecord(record, env) {
  if (record?.version !== 1 || record.environment !== env || !record.identity?.userId || !(record.identity.enterpriseId === null || typeof record.identity.enterpriseId === 'string') || !Array.isArray(record.storage?.cookies) || !Array.isArray(record.storage?.origins)) throw new Error('AUTH_RECORD_INVALID')
  const appHost = { dev: 'dev-smart-agent.hgj.com', beta: 'beta-smart-agent.hgj.com', prod: 'qianxun.hgj.com' }[env]
  if (record.storage.origins.some(origin => origin.origin !== `https://${appHost}`)) throw new Error('AUTH_ORIGIN_REJECTED')
  const allowedCookieHosts = ['hgj.com', ...(env === 'dev' ? ['iter-apisix.hgj.com'] : env === 'prod' ? ['whale-ingress-ng.hgj.com'] : []), appHost, `${env === 'prod' ? '' : env + '-'}login.hgj.com`, `${env === 'prod' ? '' : env + '-'}apisix.hgj.com`]
  if (record.storage.cookies.some(cookie => !allowedCookieHosts.includes(cookie.domain?.replace(/^\./, '')))) throw new Error('AUTH_COOKIE_DOMAIN_REJECTED')
  return record
}
export function loadAuth(env, root = AUTH_ROOT) {
  const path = files(env, root).state
  if (!existsSync(path)) return null
  try {
    const envelope = readPrivate(path)
    if (envelope.environment !== env || envelope.version !== 1) throw new Error('AUTH_ENVIRONMENT_REJECTED')
    const decipher = createDecipheriv('aes-256-gcm', key(root), Buffer.from(envelope.iv, 'base64'))
    decipher.setAAD(Buffer.from(env))
    decipher.setAuthTag(Buffer.from(envelope.tag, 'base64'))
    const plain = Buffer.concat([decipher.update(Buffer.from(envelope.data, 'base64')), decipher.final()])
    return validateRecord(JSON.parse(plain.toString('utf8')), env)
  } catch { throw new Error('AUTH_STATE_UNSAFE_OR_CORRUPT：停止，不自动覆盖原登录态') }
}
export function assertIdentity(actual, expected) {
  if (!actual?.userId || !(actual.enterpriseId === null || typeof actual.enterpriseId === 'string')) throw new Error('AUTH_IDENTITY_UNCONFIRMED')
  if (expected && (String(actual.userId) !== String(expected.userId) || String(actual.enterpriseId) !== String(expected.enterpriseId))) throw new Error('AUTH_IDENTITY_MISMATCH：账号或企业变化，禁止覆盖基线')
}
export function saveAuth(env, identity, storage, root = AUTH_ROOT) {
  const previous = loadAuth(env, root)
  assertIdentity(identity, previous?.identity)
  const record = validateRecord({ version: 1, environment: env, identity, storage, savedAt: new Date().toISOString() }, env)
  if (!existsSync(root)) mkdirSync(root, { recursive: true, mode: 0o700 })
  inspectPath(root)
  const iv = randomBytes(12)
  const cipher = createCipheriv('aes-256-gcm', key(root, true), iv)
  cipher.setAAD(Buffer.from(env))
  const data = Buffer.concat([cipher.update(JSON.stringify(record), 'utf8'), cipher.final()])
  atomicPrivateWrite(files(env, root).state, { version: 1, environment: env, iv: iv.toString('base64'), tag: cipher.getAuthTag().toString('base64'), data: data.toString('base64') })
}
export function localAccount(env) {
  if (!['dev', 'beta'].includes(env)) return null
  const path = new URL('../../../personal/compass-test-accounts.local.md', import.meta.url)
  const text = readFileSync(path, 'utf8')
  const label = env === 'dev' ? 'Dev' : 'Beta'
  const section = text.split(`## ${label} · Web 查价助手`)[1]?.split('\n## ')[0]
  const account = section?.split('### 账号 1')[1]?.split('\n### ')[0]
  const field = name => account?.match(new RegExp(`^${name}[：:]\\s*(.+)$`, 'm'))?.[1]?.trim()
  const username = field('用户名'), password = field('密码')
  return username && password ? { username, password } : null
}
