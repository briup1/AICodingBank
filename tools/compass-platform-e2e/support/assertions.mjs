export function summarize(chat) {
  if (!chat) return null
  const search = chat.frames.find(f => f.type === 'tool_end' && f.tool === 'unified_search')
  const polling = chat.frames.find(f => f.type === 'freight_search_polling')
  return {
    ...chat,
    taskId: search?.query_context?.task_id ?? polling?.task_id ?? null,
    searchCount: chat.frames.filter(f => f.type === 'tool_start' && f.tool === 'unified_search').length,
    tools: chat.frames.filter(f => f.type === 'tool_start').map(f => f.tool).filter(Boolean),
    queryContext: search?.query_context ?? null,
    searchArgs: chat.frames.find(f => f.type === 'tool_start' && f.tool === 'unified_search')?.args ?? null,
    text: chat.finalText ?? chat.legacyText ?? '',
  }
}

export function assertTurn(actual, expected, session, priorTasks) {
  if (actual.error) throw new Error(actual.error)
  if (actual.searchCount > 1) throw new Error('本版每轮只支持一个查价任务，多个 unified_search 不能静默合并为通过')
  if (actual.status !== 200 || !actual.done) throw new Error('未取得 HTTP 200 和 SSE done')
  if (!actual.session || actual.requestSession !== session || (session && actual.session !== session)) throw new Error('会话串联错误：首问应无 session，追问应沿用同一 session')
  const search = actual.tools.includes('unified_search')
  const filter = actual.tools.includes('freight_task_data')
  if (expected.action === 'new_search' && (!search || !actual.taskId || priorTasks.has(actual.taskId))) throw new Error('预期新查价，但未产生独立 unified_search taskId')
  if (expected.action === 'filter_existing' && (!filter || search || actual.taskId)) throw new Error('预期筛选旧结果，但实际工具或任务不匹配')
  if (expected.action === 'status_only' && (search || filter || actual.taskId)) throw new Error('状态追问不应重新查价或筛选')
  if (expected.action === 'no_query' && (actual.tools.length || actual.taskId)) throw new Error('本轮不应调用工具或创建任务')
  if (expected.route) {
    const routes = actual.queryContext?.routes ?? []
    if (!routes.some(route => Object.entries(expected.route).filter(([k]) => k !== 'container_types').every(([k, v]) => k === 'carrier_code' ? route[k] === v || route.carrier_codes?.includes(v) : route[k] === v))) throw new Error('标准化航线/船司与预期不符')
    if (expected.route.container_types) {
      const groups = actual.searchArgs?.route_groups ?? []
      if (!groups.some(group => JSON.stringify([...(group.container_types ?? [])].sort()) === JSON.stringify([...expected.route.container_types].sort()))) throw new Error('箱型与预期不符')
    }
  }
}

export function uiReady(ui, expected, text) {
  if (!ui?.exists || !ui.inputEnabled) return false
  if (expected.ui === 'has_results' && ui.cards < 1) return false
  if (expected.ui === 'empty' && (ui.cards !== 0 || !ui.empty)) return false
  if (expected.ui === 'result_or_empty' && !(ui.cards > 0 || (ui.cards === 0 && ui.empty))) return false
  if (expected.ui === 'response' && !ui.text.trim()) return false
  if (expected.contains && !ui.text.includes(expected.contains)) return false
  // Committed answer must actually appear in this turn, not only in the stream.
  if (text.trim() && !ui.text.replace(/\s/g, '').includes(text.trim().slice(0, 24).replace(/\s/g, ''))) return false
  return true
}
