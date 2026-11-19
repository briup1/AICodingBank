#!/usr/bin/env node
/**
 * Restore a Dev client session and start the local auth proxy.
 *
 * Secrets stay in this process and the detached proxy process environment. This
 * script never prints or writes tokens, cookies, passwords, or whale identity.
 */
import { execFileSync, spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import process from 'node:process'

const SCRIPT_DIR = path.dirname(new URL(import.meta.url).pathname)
const PROXY = path.join(SCRIPT_DIR, 'local-auth-proxy.mjs')
const DEFAULT_ACCOUNTS = path.join(
  os.homedir(),
  'workdir/self_project/AICodingBank/本机资料/compass-test-accounts.local.md'
)
const DEFAULT_LOGIN_URL = 'https://dev-login.hgj.com/login'
const DEFAULT_AUTH_URL = 'http://iter-apisix.hgj.com/whale-auth-center/auth'

const args = process.argv.slice(2)
const arg = name => {
  const index = args.indexOf(name)
  return index >= 0 ? args[index + 1] : undefined
}
const has = name => args.includes(name)
const stateDir = arg('--state') || process.env.COMPASS_LOCAL_TEST_HOME || path.join(os.homedir(), '.local/state/compass-local-test')
const slug = arg('--slug') || path.basename(process.cwd())
const accountsFile = arg('--accounts') || process.env.COMPASS_LOCAL_ACCOUNTS_FILE || DEFAULT_ACCOUNTS
const loginUrl = arg('--login-url') || DEFAULT_LOGIN_URL
const authUrl = arg('--auth-url') || DEFAULT_AUTH_URL
const proxyListen = arg('--listen') || '127.0.0.1:18081'
const proxyTarget = arg('--target') || 'http://127.0.0.1:18080'
const proxyPort = Number(proxyListen.split(':').at(-1))
const proxyUrl = `http://${proxyListen}`
if (!Number.isInteger(proxyPort) || proxyPort < 1 || proxyPort > 65535) fail(`无效鉴权代理监听地址：${proxyListen}`)
const session = arg('--session') || `compass-local-auth-${slug.replace(/[^a-zA-Z0-9._-]/g, '_')}`
const profile = arg('--profile') || path.join(os.homedir(), '.hgj-session/profiles', session)
const proxyState = path.join(stateDir, '_auth-proxy')
const proxyPidFile = path.join(proxyState, 'local-auth-proxy.pid')

const fail = message => {
  console.error(`❌ 本地鉴权启动失败：${message}`)
  process.exit(1)
}
const run = (command, commandArgs, options = {}) => {
  const result = spawnSync(command, commandArgs, {
    encoding: 'utf8',
    timeout: options.timeout || 30000,
    input: options.input,
    env: options.env || process.env,
    stdio: ['pipe', 'pipe', 'pipe']
  })
  if (result.error) throw result.error
  if (result.status !== 0 && !options.allowFail) {
    throw new Error((result.stderr || result.stdout || `${command} exited ${result.status}`).trim().split('\n').slice(-3).join('\n'))
  }
  return { stdout: result.stdout || '', stderr: result.stderr || '', status: result.status }
}
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

function parseDevAccount(file) {
  const text = fs.readFileSync(file, 'utf8')
  const sectionStart = text.indexOf('## Dev · Web 查价助手')
  if (sectionStart < 0) throw new Error(`账号文件缺少 Dev Web 区块：${file}`)
  const rest = text.slice(sectionStart)
  const section = rest.slice(0, rest.indexOf('\n## ', 4) >= 0 ? rest.indexOf('\n## ', 4) : rest.length)
  const accountStart = section.indexOf('### 账号 1')
  if (accountStart < 0) throw new Error('Dev Web 区块缺少账号 1')
  const block = section.slice(accountStart, section.indexOf('\n### ', accountStart + 5) >= 0 ? section.indexOf('\n### ', accountStart + 5) : section.length)
  const username = block.match(/用户名：([^\n]*)/)?.[1]?.trim()
  const password = block.match(/密码：([^\n]*)/)?.[1]?.trim()
  if (!username || !password) throw new Error('Dev Web 账号 1 未填写用户名或密码')
  return { username, password }
}

function listenPid() {
  try {
    return execFileSync('lsof', ['-nP', `-iTCP:${proxyPort}`, '-sTCP:LISTEN'], { encoding: 'utf8' }).trim().split(/\s+/).filter(Boolean)[0] || null
  } catch {
    return null
  }
}
function statePid() {
  try {
    const pid = Number(fs.readFileSync(proxyPidFile, 'utf8').trim())
    return Number.isInteger(pid) && pid > 0 ? String(pid) : null
  } catch {
    return null
  }
}
function processCommand(pid) {
  try { return execFileSync('ps', ['-p', pid, '-o', 'command='], { encoding: 'utf8' }).trim() } catch { return '' }
}
function ownedProxy(pid) {
  return Boolean(pid && processCommand(pid).includes('local-auth-proxy.mjs'))
}
async function gateStatus() {
  try {
    const response = await fetch(`${proxyUrl}/api/v1/agreement/gate-status?lang=zh-CN`, {
      signal: AbortSignal.timeout(5000)
    })
    const body = await response.json()
    const data = body?.data || {}
    return { ok: response.status === 200 && body?.code === 200 && typeof data === 'object', response, body }
  } catch {
    return { ok: false }
  }
}

async function existingProxyReady() {
  const pid = listenPid()
  if (!pid) return false
  const expectedPid = statePid()
  const command = processCommand(pid)
  const belongsToThisState = expectedPid === pid && ownedProxy(pid) && command.includes(`--target ${proxyTarget}`)
  const status = await gateStatus()
  if (status.ok && belongsToThisState) {
    console.log(`  已复用健康鉴权代理 pid=${pid}`)
    return true
  }
  if (!belongsToThisState) {
    throw new Error(`18081 已被其他进程或其他本地环境占用 pid=${pid}，未自动停止；请确认端口归属或先清理对应工作区`)
  }
  run(process.execPath, [PROXY, 'stop'], { env: { ...process.env, COMPASS_LOCAL_TEST_HOME: stateDir }, allowFail: true })
  await sleep(300)
  return false
}

function parseLastJson(text) {
  const start = text.lastIndexOf('{')
  const end = text.lastIndexOf('}')
  if (start < 0 || end < start) throw new Error('登录工具未返回会话结果')
  return JSON.parse(text.slice(start, end + 1))
}

async function captureToken() {
  const account = parseDevAccount(accountsFile)
  const authName = `${session}-account`
  // 通过 stdin 进入 agent-browser 加密 vault，避免把密码放进命令参数或日志。
  run(process.execPath, [
    path.join(os.homedir(), '.agents/skills/hgj-session/scripts/capture-session.mjs'),
    '--target', 'client-dev', '--session', session, '--auth-name', authName,
    '--save-auth', '--username', account.username, '--password-stdin', '--save-only'
  ], { input: `${account.password}\n`, timeout: 30000 })
  const result = run(process.execPath, [
    path.join(os.homedir(), '.agents/skills/hgj-session/scripts/capture-session.mjs'),
    '--target', 'client-dev', '--session', session, '--auth-name', authName,
    '--headless', '--wait-seconds', '45'
  ], { timeout: 70000 })
  const captured = parseLastJson(result.stdout)
  if (!captured.accessToken) throw new Error('登录后未取得 Dev access-token')
  return captured.accessToken
}

async function exchangeIdentity(token) {
  const response = await fetch(authUrl, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ accessToken: token }),
    signal: AbortSignal.timeout(15000)
  })
  const result = await response.json()
  if (response.status !== 200 || result?.code !== 200 || !result?.data?.whaleIdentity) {
    throw new Error(`认证中心换身份失败（HTTP ${response.status}，业务码 ${result?.code ?? '无'}）`)
  }
  return Buffer.from(JSON.stringify(result.data.whaleIdentity)).toString('base64')
}

async function main() {
  if (has('--help')) {
    console.log('local-auth-session.mjs [--state DIR] [--slug SLUG] [--accounts FILE] [--listen HOST:PORT] [--target URL]')
    return
  }
  if (await existingProxyReady()) return
  if (!fs.existsSync(accountsFile)) throw new Error(`账号文件不存在：${accountsFile}`)
  const token = await captureToken()
  const identity = await exchangeIdentity(token)
  const env = {
    ...process.env,
    COMPASS_LOCAL_TEST_HOME: stateDir,
    COMPASS_LOCAL_ACCESS_TOKEN: token,
    COMPASS_LOCAL_WHALE_IDENTITY: identity
  }
  const started = run(process.execPath, [PROXY, 'start', '--listen', proxyListen, '--target', proxyTarget], { env })
  if (started.status !== 0) throw new Error(started.stderr.trim() || '鉴权代理启动命令失败')
  for (let i = 0; i < 15; i += 1) {
    await sleep(300)
    if ((await gateStatus()).ok) {
      console.log('  鉴权代理启动并通过协议状态检查')
      return
    }
  }
  throw new Error('鉴权代理已启动，但协议状态未通过 HTTP 200 / code=200')
}

main().catch(error => fail(error.message || String(error)))
