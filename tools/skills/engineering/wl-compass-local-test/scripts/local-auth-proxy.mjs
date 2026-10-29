#!/usr/bin/env node
/**
 * Local-only auth bridge for compass-platform self-tests.
 * It injects the current shell's auth headers and proxies to a local backend.
 * No token is persisted or logged.
 */
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import process from 'node:process'
import { execFileSync, spawn } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const stateDir = path.join(
  process.env.COMPASS_LOCAL_TEST_HOME || path.join(process.env.HOME || '/tmp', '.local/state/compass-local-test'),
  '_auth-proxy'
)
const pidFile = path.join(stateDir, 'local-auth-proxy.pid')
const logFile = path.join(stateDir, 'local-auth-proxy.log')

function usage() {
  console.log(`Usage:
  local-auth-proxy.mjs start [--listen 127.0.0.1:18081] [--target http://127.0.0.1:18080]
  local-auth-proxy.mjs stop
  local-auth-proxy.mjs status

Required environment variables for start:
  COMPASS_LOCAL_ACCESS_TOKEN
  COMPASS_LOCAL_WHALE_IDENTITY

Optional:
  COMPASS_LOCAL_APP_NAME (default: smart-agent)
`)
}

function parseOptions(args) {
  const options = {
    listen: '127.0.0.1:18081',
    target: 'http://127.0.0.1:18080'
  }
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '--listen') options.listen = args[++i]
    else if (args[i] === '--target') options.target = args[++i]
    else throw new Error(`unknown option: ${args[i]}`)
  }
  const [host, portText] = options.listen.split(':')
  options.host = host || '127.0.0.1'
  options.port = Number(portText)
  if (options.host !== '127.0.0.1' && options.host !== 'localhost') {
    throw new Error('listen must be bound to 127.0.0.1 or localhost')
  }
  if (!Number.isInteger(options.port) || options.port < 1 || options.port > 65535) {
    throw new Error(`invalid listen address: ${options.listen}`)
  }
  const target = new URL(options.target)
  if (target.protocol !== 'http:' || !['127.0.0.1', 'localhost'].includes(target.hostname)) {
    throw new Error('target must be a local http://127.0.0.1 or http://localhost URL')
  }
  options.targetUrl = target
  return options
}

function readPid() {
  try {
    const pid = Number(fs.readFileSync(pidFile, 'utf8').trim())
    return Number.isInteger(pid) && pid > 0 ? pid : null
  } catch {
    return null
  }
}

function isAlive(pid) {
  if (!pid) return false
  try {
    process.kill(pid, 0)
    return true
  } catch {
    return false
  }
}

function requireCredentials() {
  const accessToken = process.env.COMPASS_LOCAL_ACCESS_TOKEN
  const whaleIdentity = process.env.COMPASS_LOCAL_WHALE_IDENTITY
  if (!accessToken || !whaleIdentity) {
    throw new Error('missing COMPASS_LOCAL_ACCESS_TOKEN or COMPASS_LOCAL_WHALE_IDENTITY')
  }
  return {
    accessToken,
    whaleIdentity,
    appName: process.env.COMPASS_LOCAL_APP_NAME || 'smart-agent'
  }
}

function startDaemon(args) {
  const options = parseOptions(args)
  requireCredentials()
  const existingPid = readPid()
  if (isAlive(existingPid)) throw new Error(`proxy already running (pid=${existingPid})`)
  fs.mkdirSync(stateDir, { recursive: true })
  fs.rmSync(pidFile, { force: true })
  const child = spawn(process.execPath, [fileURLToPath(import.meta.url), 'serve', ...args], {
    detached: true,
    stdio: ['ignore', fs.openSync(logFile, 'a'), fs.openSync(logFile, 'a')],
    env: process.env
  })
  child.unref()
  fs.writeFileSync(pidFile, `${child.pid}\n`, { mode: 0o600 })
  console.log(`started local auth proxy pid=${child.pid} listen=${options.host}:${options.port} target=${options.targetUrl}`)
}

function isProxyProcess(pid) {
  try {
    const command = execFileSync('ps', ['-p', String(pid), '-o', 'command='], { encoding: 'utf8' })
    return command.includes('local-auth-proxy.mjs') && command.includes(' serve ')
  } catch {
    return false
  }
}

function stopDaemon() {
  const pid = readPid()
  if (!pid || !isAlive(pid) || !isProxyProcess(pid)) {
    fs.rmSync(pidFile, { force: true })
    console.log('local auth proxy is not running')
    return
  }
  process.kill(pid, 'SIGTERM')
  fs.rmSync(pidFile, { force: true })
  console.log(`stopped local auth proxy pid=${pid}`)
}

function serve(args) {
  const options = parseOptions(args)
  const credentials = requireCredentials()
  const server = http.createServer((incoming, response) => {
    const target = new URL(incoming.url || '/', options.targetUrl)
    const headers = { ...incoming.headers }
    delete headers.host
    delete headers['access-token']
    delete headers['whale-identity']
    delete headers['app-name']
    headers['access-token'] = credentials.accessToken
    headers['whale-identity'] = credentials.whaleIdentity
    headers['app-name'] = credentials.appName

    const upstream = http.request({
      protocol: target.protocol,
      hostname: target.hostname,
      port: target.port || 80,
      method: incoming.method,
      path: `${target.pathname}${target.search}`,
      headers
    }, upstreamResponse => {
      response.writeHead(upstreamResponse.statusCode || 502, upstreamResponse.headers)
      upstreamResponse.pipe(response)
    })
    upstream.on('error', error => {
      response.writeHead(502, { 'content-type': 'application/json;charset=utf-8' })
      response.end(JSON.stringify({ code: 502, message: 'local auth proxy upstream unavailable' }))
      console.error(`[proxy-error] ${error.code || error.message}`)
    })
    incoming.pipe(upstream)
  })

  server.listen(options.port, options.host, () => {
    console.log(`local auth proxy listening on ${options.host}:${options.port}`)
  })
  const shutdown = () => server.close(() => process.exit(0))
  process.once('SIGTERM', shutdown)
  process.once('SIGINT', shutdown)
}

const [command = 'help', ...args] = process.argv.slice(2)
try {
  if (command === 'start') startDaemon(args)
  else if (command === 'stop') stopDaemon()
  else if (command === 'status') {
    const pid = readPid()
    console.log(isAlive(pid) ? `running pid=${pid}` : 'stopped')
  } else if (command === 'serve') serve(args)
  else usage()
} catch (error) {
  console.error(`error: ${error.message}`)
  process.exitCode = 1
}
