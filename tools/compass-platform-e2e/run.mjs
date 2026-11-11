import { mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs'
import { resolve, relative } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createHash, randomUUID } from 'node:crypto'
import { spawnSync, spawn } from 'node:child_process'
import { ROOT, environment, loadSuite } from './support/settings.mjs'
import { finishResult } from './support/result.mjs'
import { hasAuth, localAccount } from './support/auth-store.mjs'

const HELP = `Compass 对话 E2E（不使用 Ego，不调用测试侧模型）
  ./e2e login --env dev [--local-account]  # 仅登录并加密保存，不发问句
  ./e2e list --env dev --cases cases/shanghai-la-two-turn.json
  ./e2e run --env dev --cases cases/multi-turn.json --allow-live-queries [--headed]
  ./e2e report --run <.work/test-runs/运行编号>
  ./e2e check

list/check 不启动业务浏览器、不登录、不发查询。
run 会登录并创建真实会话/查价任务；须取得当次环境和问句范围授权。
默认串行、零重试。不支持 resume/last-failed，禁止中断后盲目重发。
prod 查询额外要求 --allow-production。先 login，再 run；缓存失效时停止并提示补登。
`

export function parseArgs(args) {
  const command = args.shift() || 'help'
  if (!['help', '--help', 'list', 'run', 'report', 'check', 'login'].includes(command)) throw new Error('未知命令')
  const options = { command, env: 'dev', cases: 'cases/shanghai-la-two-turn.json', localAccount: false, headed: false, manualLogin: false, allowLive: false, allowProduction: false }
  const seen = new Set()
  for (let i = 0; i < args.length; i++) {
    const flag = args[i]
    if (seen.has(flag)) throw new Error(`参数重复: ${flag}`)
    seen.add(flag)
    if (['--env', '--cases', '--run'].includes(flag)) {
      const value = args[++i]
      if (!value || value.startsWith('--')) throw new Error(`参数缺值: ${flag}`)
      options[flag.slice(2)] = value
    } else if (flag === '--local-account') options.localAccount = true
    else if (flag === '--manual-login') options.manualLogin = true
    else if (flag === '--headed') options.headed = true
    else if (flag === '--allow-live-queries') options.allowLive = true
    else if (flag === '--allow-production') options.allowProduction = true
    else throw new Error(`未知参数: ${flag}`)
  }
  return options
}

function cliPath() {
  const path = resolve(ROOT, 'node_modules/e2e/dist/cli/bin.js')
  if (!existsSync(path)) throw new Error('缺少依赖；在工具目录执行 pnpm install --frozen-lockfile')
  return path
}

export async function main(args) {
  const options = parseArgs([...args])
  if (['help', '--help'].includes(options.command)) { console.log(HELP); return 0 }
  if (options.command === 'check') {
    const { globSync } = await import('node:fs')
    const files = [...globSync('unit/*.test.mjs', { cwd: ROOT })].map(path => resolve(ROOT, path))
    return spawnSync(process.execPath, ['--test', ...files], { cwd: ROOT, stdio: 'inherit' }).status ?? 1
  }
  if (options.command === 'report') {
    if (!options.run) throw new Error('report 必须指定 --run')
    const result = JSON.parse(readFileSync(resolve(ROOT, options.run, 'result.json'), 'utf8'))
    console.log(`${result.runId} | ${result.environment} | ${result.status} | exit=${result.exitCode ?? '未结束'}`)
    console.table(result.items.map(item => ({ case: item.caseId, turn: item.step, status: item.status, task: item.context?.taskId ?? '', cards: item.context?.ui?.cards ?? '', actual: item.actual, issue: item.issue })))
    return 0
  }
  const env = environment(options.env)
  const suite = loadSuite(options.cases)
  const casesPath = resolve(ROOT, options.cases)
  const childEnv = { ...process.env, E2E_TELEMETRY_DISABLED: '1', DO_NOT_TRACK: '1', COMPASS_ENV: env.name, COMPASS_CASES: casesPath }
  delete childEnv.COMPASS_RUN_DIR
  delete childEnv.COMPASS_LIVE_RUN
  const cli = cliPath()
  const cliArgs = [cli, options.command, '--config', 'e2e.config.ts']
  if (options.command === 'list') {
    console.log(`环境 ${env.name} | ${env.appUrl} | ${suite.scenarios.length} 组 / ${suite.scenarios.reduce((n, s) => n + s.turns.length, 0)} 轮`)
    return spawnSync(process.execPath, cliArgs, { cwd: ROOT, env: childEnv, stdio: 'inherit' }).status ?? 1
  }
  if (options.command !== 'login' && !options.allowLive) throw new Error('拒绝真实查询：缺少 --allow-live-queries（参数不替代用户授权）')
  if (options.command !== 'login' && env.name === 'prod' && !options.allowProduction) throw new Error('拒绝生产查询：缺少 --allow-production')
  if (options.command !== 'login' && !options.manualLogin && !hasAuth(env.name)) throw new Error(`LOGIN_REQUIRED：请先 ./e2e login --env ${env.name}`)
  if (options.command === 'login' && options.localAccount) {
    const account = localAccount(env.name)
    if (!account) throw new Error('该环境没有获准的本机测试账号；使用手动登录')
    childEnv.E2E_USER_MEMBER_USERNAME = account.username
    childEnv.E2E_USER_MEMBER_PASSWORD = account.password
    childEnv.COMPASS_AUTO_ACCOUNT = '1'
  } else childEnv.COMPASS_AUTO_ACCOUNT = '0'
  childEnv.COMPASS_AUTH_ONLY = options.command === 'login' ? '1' : '0'
  childEnv.COMPASS_HEADED = options.headed ? '1' : '0'
  childEnv.COMPASS_MANUAL_LOGIN = options.manualLogin ? '1' : '0'
  childEnv.COMPASS_SYSTEM_CHROME = options.manualLogin ? '1' : '0'
  const runId = `${new Date().toISOString().replace(/[:.]/g, '-')}-${randomUUID().slice(0, 8)}`
  const runDir = resolve(ROOT, '.work/test-runs', runId)
  mkdirSync(runDir, { recursive: true, mode: 0o700 })
  const startedAt = new Date().toISOString()
  writeFileSync(resolve(runDir, 'result.json'), JSON.stringify({
    schemaVersion: 1, runId, taskId: 'compass-bot-conversation',
    cases: { path: relative(ROOT, casesPath), version: String(suite.schemaVersion), sha256: createHash('sha256').update(readFileSync(casesPath)).digest('hex') },
    environment: env.name, versions: { frontend: '待确认', backend: '待确认' },
    status: '进行中', startedAt, updatedAt: startedAt, endedAt: null, previousRun: null,
    items: options.command === 'login' ? [] : suite.scenarios.flatMap(s => s.turns.map((turn, i) => ({ caseId: s.id, step: String(i + 1), entry: `${env.name}/Web`, variant: turn.expect.action, message: turn.message, expected: turn.expect, status: '未执行', actual: '', issue: '', evidence: [], updatedAt: null }))),
  }, null, 2) + '\n', { flag: 'wx', mode: 0o600 })
  cliArgs[1] = 'run'
  const output = resolve(runDir, 'evidence/runner')
  cliArgs.push('--output', output, '--workers', '1', '--retries', '0', '--reporter', 'list,markdown')
  if (options.headed) cliArgs.push('--headed')
  console.log(`运行记录：${runDir}/result.json`)
  let child
  const forward = signal => child?.kill(signal)
  const interrupt = () => forward('SIGINT')
  const terminate = () => forward('SIGTERM')
  process.on('SIGINT', interrupt)
  process.on('SIGTERM', terminate)
  let code = 1
  try {
    code = await new Promise((done, reject) => {
      child = spawn(process.execPath, cliArgs, { cwd: ROOT, env: { ...childEnv, COMPASS_RUN_DIR: runDir, COMPASS_LIVE_RUN: '1' }, stdio: 'inherit' })
      child.on('error', reject)
      child.on('exit', (status, signal) => done(signal ? 130 : status ?? 1))
    })
    const result = JSON.parse(readFileSync(resolve(runDir, 'result.json'), 'utf8'))
    if (code === 0 && result.items.some(item => item.status !== '通过')) code = 1
    return code
  } finally {
    process.off('SIGINT', interrupt)
    process.off('SIGTERM', terminate)
    finishResult(runDir, code)
    console.log(`查看结果：./e2e report --run .work/test-runs/${runId}`)
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).then(code => { process.exitCode = code }).catch(error => { console.error(error.message); process.exitCode = 2 })
}
