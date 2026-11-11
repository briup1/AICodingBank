// Passive observer: clone responses and always return the original Response to the app.
(() => {
  if (window.__compassE2E) return;
  const state = { chats: [], polls: [], authenticated: false, identity: null, observerErrors: [] };
  window.__compassE2E = state;
  const originalFetch = window.fetch.bind(window);
  const pick = (value, keys) => Object.fromEntries(keys.filter(key => value?.[key] !== undefined).map(key => [key, value[key]]));
  const route = value => pick(value, ['pol_code', 'pod_code', 'carrier_code', 'carrier_codes', 'container_types', 'pol_texts', 'pod_texts', 'carrier', 'start_date', 'end_date', 'date_start', 'date_end', 'freight_categories', 'freight_advantages', 'freight_advantage_match']);
  const context = value => value ? {
    ...pick(value, ['task_id', 'has_polling']),
    routes: Array.isArray(value.routes) ? value.routes.map(route) : [],
    query_input: value.query_input ? route(value.query_input) : null,
  } : null;
  const now = () => new Date().toISOString();
  const frame = (event, record) => {
    const item = { at: now(), ...pick(event, ['type', 'tool', 'success', 'session_id', 'thread_id', 'conversation_id', 'task_id', 'has_polling', 'carrier', 'container_types']) };
    if (event.query_context) item.query_context = context(event.query_context);
    if (event.type === 'tool_start' && event.tool === 'unified_search') {
      item.args = { route_groups: (event.args?.route_groups || []).map(route) };
    }
    if (event.type === 'tool_end' && event.tool === 'unified_search') {
      item.outputCount = Array.isArray(event.output) ? event.output.length : null;
    }
    // Keep only the committed reply; never concatenate abandoned drafts.
    if (event.type === 'text_commit') record.finalText = typeof event.content === 'string' ? event.content.slice(0, 16000) : '';
    if (event.type === 'text_reset') record.legacyText = '';
    if (event.type === 'text') record.legacyText = (record.legacyText + (typeof event.content === 'string' ? event.content : '')).slice(0, 16000);
    if (event.type === 'done') { record.done = true; record.session = event.session_id || event.thread_id || null; }
    if (event.type === 'error') record.error = 'SSE error event';
    if (record.frames.length < 2000) record.frames.push(item);
    else record.error ||= 'SSE event limit exceeded';
  };
  async function parseSse(response, record) {
    const reader = response.body?.getReader();
    if (!reader) { record.error = 'missing response stream'; return; }
    const decoder = new TextDecoder();
    let buffer = '';
    const line = text => {
      if (!text.startsWith('data:')) return;
      const raw = text.slice(5).trim();
      if (!raw || raw === '[DONE]') return;
      try { frame(JSON.parse(raw), record); }
      catch { record.error ||= 'invalid SSE JSON'; }
    };
    try {
      while (!record.done) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        if (buffer.length > 2_000_000) throw new Error('SSE frame limit');
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        lines.forEach(line);
      }
      buffer += decoder.decode();
      if (buffer.trim()) line(buffer);
      if (!record.done) record.error ||= 'stream ended without done event';
    } catch { record.error ||= 'SSE observer failed'; }
    finally {
      record.endedAt = now();
      // Do not await cancel: cancellation of a clone can wait for the app's branch.
      if (record.done) void reader.cancel().catch(() => {});
      reader.releaseLock();
    }
  }
  window.fetch = async (input, init) => {
    let url;
    try { url = new URL(typeof input === 'string' || input instanceof URL ? String(input) : input.url, window.location.href); }
    catch { return originalFetch(input, init); }
    const isChat = /\/(?:agents\/)?chat(?:\/sync)?\/?$/.test(url.pathname) && (init?.method || input?.method || 'GET').toUpperCase() === 'POST';
    let chat;
    if (isChat) {
      let request = {};
      try {
        const body = init?.body ?? (input instanceof Request ? await input.clone().text() : '{}');
        request = JSON.parse(body || '{}');
      } catch { state.observerErrors.push('chat request body unavailable'); }
      chat = {
        startedAt: now(), requestSession: request.session_id || request.thread_id || null,
        message: typeof request.message === 'string' ? request.message.slice(0, 4000) : null,
        status: null, frames: [], done: false, session: null, error: null, finalText: null, legacyText: '',
      };
      state.chats.push(chat);
    }
    let response;
    try { response = await originalFetch(input, init); }
    catch (error) { if (chat) chat.error = 'chat network failure'; throw error; }
    try {
      if (chat) {
        chat.status = response.status;
        if (!response.ok) chat.error = `chat HTTP ${response.status}`;
        else void parseSse(response.clone(), chat);
      } else if (({ 'dev-smart-agent.hgj.com': ['iter-apisix.hgj.com', 'dev-apisix.hgj.com'], 'beta-smart-agent.hgj.com': ['beta-apisix.hgj.com'], 'qianxun.hgj.com': ['whale-ingress-ng.hgj.com', 'apisix.hgj.com'] }[window.location.hostname || new URL(window.location.href).hostname] || []).includes(url.hostname) && url.pathname === '/whale-user-center/whale/user/get-user-detail-info') {
        void response.clone().json().then(payload => {
          const data = payload?.data ?? payload;
          state.identity = response.ok && [0, 200].includes(payload?.code) && data?.userId ? { userId: String(data.userId), enterpriseId: data.enterpriseDetailResponse?.enterpriseId ? String(data.enterpriseDetailResponse.enterpriseId) : null } : null;
          state.authenticated = Boolean(state.identity);
        }).catch(() => { state.authenticated = false; });
      } else {
        const match = url.pathname.match(/\/freight\/(?:polling\/([^/]+)|tasks\/([^/]+)\/first-display)$/);
        if (match) {
          const record = { at: now(), taskId: match[1] || match[2], kind: match[1] ? 'polling' : 'first-display', status: response.status, taskStatus: null, count: null, error: null };
          state.polls.push(record);
          void response.clone().json().then(payload => {
            const data = payload?.data ?? payload;
            if (!response.ok || ![undefined, 0, 200].includes(payload?.code)) { record.error = 'poll HTTP/business error'; return; }
            record.taskStatus = typeof data?.status === 'string' ? data.status : null;
            record.count = Array.isArray(data?.routeResults) ? data.routeResults.reduce((sum, r) => sum + (Array.isArray(r.freightItemList) ? r.freightItemList.length : 0), 0) : null;
          }).catch(() => { record.error = 'poll response unavailable'; });
        }
      }
    } catch { state.observerErrors.push('response observation failed'); }
    return response;
  };
})();
