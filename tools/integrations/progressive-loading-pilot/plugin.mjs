// Isolated prototype; not installed in any host discovery directory.
export function createHooks(rules, record = () => {}) {
  const sessions = new Map();
  function state(id) {
    if (!sessions.has(id)) sessions.set(id, { wanted: new Set(), ready: new Set() });
    return sessions.get(id);
  }
  return {
    'tool.execute.before': async (input, output) => {
      const matched = rules.filter(rule => rule.matches(input.tool, output.args));
      if (!matched.length) return;
      const current = state(input.sessionID);
      const missing = matched.filter(rule => !current.ready.has(rule.id));
      for (const rule of missing) current.wanted.add(rule.id);
      if (missing.length) {
        record({ event: 'blocked', session: input.sessionID, call: input.callID,
          rules: missing.map(rule => rule.id) });
        throw new Error('SCENARIO_RULES_PENDING: action not executed. Reconsider after the next model request receives the required rules.');
      }
      record({ event: 'allowed', session: input.sessionID, call: input.callID,
        rules: matched.map(rule => rule.id) });
    },
    'experimental.chat.system.transform': async (input, output) => {
      if (!input.sessionID) return;
      const current = state(input.sessionID);
      // Reinsert on every subsequent request, so compaction cannot drop active rules.
      // This does NOT prove delivery when providers fail; live-host testing is required.
      for (const rule of rules) {
        if (!current.wanted.has(rule.id)) continue;
        output.system.push(`[scenario:${rule.id}]\n${await rule.load()}`);
        current.ready.add(rule.id);
        record({ event: 'prepared-for-model', session: input.sessionID, rule: rule.id });
      }
    },
  };
}

export function pythonFile(tool, args) {
  if (['edit', 'write'].includes(tool)) return /\.py$/.test(args.filePath ?? args.path ?? '');
  if (tool === 'apply_patch') return /^\*\*\* (?:Add File|Update File|Delete File|Move to): .+\.py$/m.test(args.patchText ?? args.patch ?? '');
  return false;
}

export function pythonExecution(tool, args) {
  // Deliberately bounded prototype: direct commands only, not a shell parser.
  return tool === 'bash' && /^\s*(?:python(?:3(?:\.\d+)?)?|uv\s+(?:run|sync|pip|venv|python))(?=\s|$)/.test(args.command ?? '');
}
