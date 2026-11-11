import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { resolve } from 'node:path'

export const ROOT = fileURLToPath(new URL('../', import.meta.url))
export const SESSION = 'compass-client'
export const LIMITS = { sse: 180_000, task: 315_000, ui: 30_000 }
const actions = ['new_search', 'filter_existing', 'status_only', 'no_query']
const own = (object, allowed) => Object.keys(object).every(key => allowed.includes(key))
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value)

export function validateCases(value) {
  if (!object(value) || !own(value, ['schemaVersion', 'scenarios']) || value.schemaVersion !== 1 || !Array.isArray(value.scenarios) || !value.scenarios.length || value.scenarios.length > 100) {
    throw new Error('用例必须包含 schemaVersion: 1 和 1～100 个 scenarios')
  }
  const ids = new Set()
  for (const scenario of value.scenarios) {
    if (!object(scenario) || !own(scenario, ['id', 'turns']) || typeof scenario.id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(scenario.id) || ids.has(scenario.id)) throw new Error('场景 id 必须唯一，且仅包含字母、数字、下划线或连字符')
    ids.add(scenario.id)
    if (!Array.isArray(scenario.turns) || !scenario.turns.length || scenario.turns.length > 20) throw new Error(`${scenario.id}: turns 必须为 1～20 轮`)
    for (const [index, turn] of scenario.turns.entries()) {
      if (!object(turn) || !own(turn, ['message', 'expect']) || typeof turn.message !== 'string' || !turn.message.trim() || turn.message.length > 4000) throw new Error(`${scenario.id}/${index + 1}: 无效问句`)
      const e = turn.expect
      if (!object(e) || !own(e, ['action', 'task', 'ui', 'contains', 'route']) || !actions.includes(e.action)) throw new Error(`${scenario.id}/${index + 1}: 必须指定有效 expect.action，未知字段不被忽略`)
      if (e.action === 'new_search' ? e.task !== 'COMPLETE' : e.task !== undefined) throw new Error('new_search 必须要求 task=COMPLETE；其他动作不接受 task 字段')
      if (!['has_results', 'empty', 'result_or_empty', 'response'].includes(e.ui)) throw new Error('每轮必须指定 ui: has_results / empty / result_or_empty / response')
      if (e.action === 'new_search' && e.ui === 'response') throw new Error('new_search 必须检查 has_results 或 empty，不能只检查回复')
      if (e.contains !== undefined && (typeof e.contains !== 'string' || !e.contains.trim())) throw new Error('contains 必须为非空字符串')
      if (e.route !== undefined && (!object(e.route) || !own(e.route, ['pol_code', 'pod_code', 'carrier_code', 'container_types']) || Object.entries(e.route).some(([key, v]) => key === 'container_types' ? !Array.isArray(v) || !v.length || v.some(x => typeof x !== 'string' || !x) : typeof v !== 'string' || !v))) throw new Error('route 仅接受 pol_code/pod_code/carrier_code/container_types')
    }
  }
  return value
}

export function loadSuite(path = 'cases/single-turn.json') {
  return validateCases(JSON.parse(readFileSync(resolve(ROOT, path), 'utf8')))
}

export function environment(name = 'dev', vars = process.env) {
  const entries = JSON.parse(readFileSync(resolve(ROOT, 'environments.json'), 'utf8'))
  if (!Object.hasOwn(entries, name)) throw new Error('环境只允许 dev / beta / prod；bot 是被测服务，不是环境')
  const config = entries[name]
  const loginUrl = vars[`COMPASS_${name.toUpperCase()}_LOGIN_URL`] || config.loginUrl
  if (loginUrl) {
    const url = new URL(loginUrl)
    if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash || !config.allowedLoginHosts.includes(url.hostname) || url.port) throw new Error('登录入口必须是该环境白名单中的 HTTPS URL，不得含凭据或查询串')
  }
  return { ...config, name, loginUrl }
}

export function scenarioTimeout(scenario) {
  return 60_000 + scenario.turns.reduce((sum, turn) => sum + 60_000 + LIMITS.sse + LIMITS.ui + (turn.expect.action === 'new_search' ? LIMITS.task : 0), 0)
}
