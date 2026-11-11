import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import vm from 'node:vm'
import { ROOT, validateCases, environment, loadSuite, scenarioTimeout } from '../support/settings.mjs'
import { parseArgs } from '../run.mjs'
import { finishResult, updateTurn } from '../support/result.mjs'
import { summarize, assertTurn, uiReady } from '../support/assertions.mjs'

const source = readFileSync(resolve(ROOT, 'support/freight-capture.js'), 'utf8')
const suite = () => structuredClone(loadSuite())
const makeChat = extra => ({ status: 200, done: true, error: null, session: 's1', requestSession: null, tools: ['unified_search'], taskId: 't1', ...extra })
const expected = { action: 'new_search', task: 'COMPLETE', ui: 'has_results' }
const tick = () => new Promise(done => setImmediate(done))
function observer(fetch) {
  const window = { location: { href: 'https://dev-smart-agent.hgj.com/query' }, fetch }
  const sandbox = { window, URL, Request, Response, TextDecoder, Date, getComputedStyle: () => ({}) }
  vm.runInNewContext(source, sandbox)
  return window
}
function response(frames, { done = true, split = false } = {}) {
  const text = frames.map(f => `data: ${JSON.stringify(f)}\n`).join('') + (done ? 'data: {"type":"done","session_id":"s1"}' : '')
  const bytes = new TextEncoder().encode(text)
  return new Response(new ReadableStream({ start(controller) {
    if (split) for (const byte of bytes) controller.enqueue(Uint8Array.of(byte))
    else controller.enqueue(bytes)
    controller.close()
  } }), { status: 200, headers: { 'content-type': 'text/event-stream' } })
}

test('单轮/多轮数据加载；预算按轮次计算', () => {
  assert.equal(loadSuite().scenarios[0].turns.length, 1)
  const multi = loadSuite('cases/multi-turn.json')
  assert.equal(multi.scenarios[0].turns.length, 3)
  assert.ok(scenarioTimeout(multi.scenarios[0]) > scenarioTimeout(loadSuite().scenarios[0]))
})
test('拒绝未知字段、重复 id、非法终态、空问句和零轮', () => {
  for (const change of [s => s.extra = 1, s => s.scenarios.push(s.scenarios[0]), s => s.scenarios[0].turns[0].expect.task = 'ERROR', s => s.scenarios[0].turns[0].message = ' ', s => s.scenarios[0].turns = [], s => s.scenarios[0].turns[0].expect.ui = 'response']) {
    const value = suite(); change(value); assert.throws(() => validateCases(value))
  }
})
test('环境严格隔离，生产登录不猜测，拒绝带凭据/跨环境 URL', () => {
  assert.match(environment('dev', {}).appUrl, /dev-smart/)
  assert.match(environment('beta', {}).loginUrl, /beta-login/)
  assert.equal(environment('prod', {}).loginUrl, null)
  assert.throws(() => environment('bot', {}))
  for (const login of ['http://login.hgj.com/login', 'https://user:pass@login.hgj.com/login', 'https://dev-login.hgj.com/login', 'https://login.hgj.com/login?token=x']) assert.throws(() => environment('prod', { COMPASS_PROD_LOGIN_URL: login }))
})
test('CLI 默认安全，未知/重复参数拒绝，不接受 last-failed 自动重放', () => {
  assert.equal(parseArgs([]).command, 'help')
  assert.equal(parseArgs(['run']).allowLive, false)
  assert.equal(parseArgs(['run', '--allow-live-queries']).allowLive, true)
  for (const args of [['run', '--last-failed'], ['run', '--env'], ['list', '--env', 'dev', '--env', 'prod']]) assert.throws(() => parseArgs(args))
})
test('只接受独立新 task、正确 session，旧批次筛选和状态追问不混淆', () => {
  assert.doesNotThrow(() => assertTurn(makeChat(), expected, null, new Set()))
  assert.throws(() => assertTurn(makeChat(), expected, null, new Set(['t1'])))
  assert.throws(() => assertTurn(makeChat({ requestSession: 'old' }), expected, null, new Set()))
  assert.throws(() => assertTurn(makeChat(), { action: 'status_only' }, null, new Set()))
  assert.doesNotThrow(() => assertTurn(makeChat({ tools: ['freight_task_data'], taskId: null }), { action: 'filter_existing' }, null, new Set()))
  assert.doesNotThrow(() => assertTurn(makeChat({ tools: [], taskId: null, requestSession: 's1' }), { action: 'no_query' }, 's1', new Set()))
})
test('页面结果不能由 SSE、旧消息或空回复代替', () => {
  assert.equal(uiReady({ exists: false, cards: 3, inputEnabled: true }, expected, ''), false)
  assert.equal(uiReady({ exists: true, cards: 0, inputEnabled: true }, expected, ''), false)
  assert.equal(uiReady({ exists: true, cards: 3, inputEnabled: true, text: '正确结果' }, expected, '正确结果'), true)
  assert.equal(uiReady({ exists: true, cards: 0, empty: false, inputEnabled: true, text: '' }, { ui: 'empty' }, ''), false)
})
test('原子检查点保留任务，中断项不变成通过', () => {
  const dir = mkdtempSync(resolve(tmpdir(), 'compass-e2e-unit-'))
  writeFileSync(resolve(dir, 'result.json'), JSON.stringify({ items: [{ caseId: 'A', step: '1', status: '未执行' }, { caseId: 'A', step: '2', status: '未执行' }] }))
  updateTurn(dir, 'A', 1, item => { item.status = '进行中'; item.context = { taskId: 't1' } })
  const result = finishResult(dir, 130)
  assert.equal(result.items[0].status, '阻塞')
  assert.equal(result.items[0].context.taskId, 't1')
  assert.equal(result.items[1].status, '阻塞')
  assert.throws(() => updateTurn(dir, 'unknown', 1, () => {}))
})
test('采集器保持 Response 对象与内容原样；支持 Request、UTF8 分片、末行 done', async () => {
  const original = response([{ type: 'text', content: '青岛' }, { type: 'text_commit', content: '洛杉矶' }], { split: true })
  const window = observer(async () => original)
  const result = await window.fetch(new Request('https://dev-apisix.hgj.com/service/agents/chat', { method: 'POST', body: JSON.stringify({ message: '青岛--LA', session_id: null }) }))
  assert.equal(result, original)
  const body = await result.text()
  assert.match(body, /洛杉矶/)
  for (let i = 0; i < 50 && !window.__compassE2E.chats[0].done; i++) await tick()
  assert.equal(window.__compassE2E.chats[0].done, true)
  assert.equal(window.__compassE2E.chats[0].message, '青岛--LA')
  assert.equal(summarize(window.__compassE2E.chats[0]).text, '洛杉矶')
})
test('流关闭但缺 done 必须失败，未授权字段不落盘', async () => {
  const original = response([{ type: 'tool_end', tool: 'unified_search', output: [{ token: 'sensitive' }], query_context: { task_id: 't1', has_polling: true, token: 'sensitive', routes: [{ pol_code: 'CNTAO', pod_code: 'USLAX', personal: 'sensitive' }] } }], { done: false })
  const window = observer(async () => original)
  await (await window.fetch('/agents/chat', { method: 'POST', body: '{}' })).text()
  for (let i = 0; i < 50 && !window.__compassE2E.chats[0].error; i++) await tick()
  assert.equal(window.__compassE2E.chats[0].done, false)
  assert.match(window.__compassE2E.chats[0].error, /without done/)
  assert.equal(JSON.stringify(window.__compassE2E).includes('sensitive'), false)
})
test('轮询按任务隔离，业务码失败不能记录 COMPLETE', async () => {
  const window = observer(async input => new Response(JSON.stringify({ code: String(input).includes('bad') ? 401 : 200, data: { status: 'COMPLETE', routeResults: [{ freightItemList: [{}, {}] }] } })))
  await window.fetch('/freight/polling/t1')
  await window.fetch('/freight/polling/bad')
  for (let i = 0; i < 20 && !window.__compassE2E.polls[1].error; i++) await tick()
  assert.equal(window.__compassE2E.polls[0].taskId, 't1')
  assert.equal(window.__compassE2E.polls[0].count, 2)
  assert.equal(window.__compassE2E.polls[1].taskStatus, null)
  assert.match(window.__compassE2E.polls[1].error, /business/)
})
