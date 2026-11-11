import { test } from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import { ROOT } from '../support/settings.mjs'

function run(args) {
  const env = { ...process.env, HOME: mkdtempSync(resolve(tmpdir(), 'compass-cli-home-')) }
  delete env.E2E_USER_MEMBER_USERNAME
  delete env.E2E_USER_MEMBER_PASSWORD
  delete env.COMPASS_PROD_LOGIN_URL
  return spawnSync(process.execPath, ['run.mjs', ...args], { cwd: ROOT, env, encoding: 'utf8', timeout: 5000 })
}
test('真实执行缺授权、缺凭据、生产缺额外批准均在启动浏览器前拒绝', () => {
  const rows = [
    [['run', '--env', 'dev'], /缺少 --allow-live-queries/],
    [['run', '--env', 'dev', '--allow-live-queries'], /LOGIN_REQUIRED/],
    [['run', '--env', 'prod', '--allow-live-queries'], /缺少 --allow-production/],
    [['run', '--env', 'prod', '--allow-live-queries', '--allow-production'], /LOGIN_REQUIRED/],
    [['run', '--env', 'bot'], /环境只允许/],
  ]
  for (const [args, pattern] of rows) {
    const result = run(args)
    assert.equal(result.status, 2)
    assert.match(result.stderr, pattern)
    assert.equal(result.stdout.includes('运行记录'), false)
  }
})
test('帮助无需凭据，拒绝自动 resume 和未知选项', () => {
  assert.equal(run([]).status, 0)
  assert.equal(run(['run', '--resume']).status, 2)
  assert.match(run(['run', '--env', 'prod', '--manual-login', '--allow-live-queries']).stderr, /缺少 --allow-production/)
})
test('结果命令可查看已有轮次，不启动浏览器或发送查询', () => {
  const dir = mkdtempSync(resolve(tmpdir(), 'compass-e2e-report-unit-'))
  writeFileSync(resolve(dir, 'result.json'), JSON.stringify({ runId: 'synthetic-report', environment: 'local-fixture', status: '已结束', exitCode: 1, items: [{ caseId: 'A', step: '1', status: '失败', context: { taskId: 'test-task', ui: { cards: 0 } }, actual: 'synthetic empty', issue: 'synthetic failure' }] }))
  const result = run(['report', '--run', dir])
  assert.equal(result.status, 0)
  assert.match(result.stdout, /test-task/)
  assert.match(result.stdout, /synthetic failure/)
})
