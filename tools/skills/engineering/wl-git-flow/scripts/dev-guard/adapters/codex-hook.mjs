#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { checkCommand } from '../policy.mjs';

let result;
try {
  const input = JSON.parse(readFileSync(0, 'utf8'));
  if (input.tool_name !== 'Bash' || input.hook_event_name !== 'PreToolUse') process.exit(0);
  result = checkCommand({ cwd: input.cwd, command: input.tool_input?.command });
} catch (error) { result = { decision: 'deny', reason: `Hook 检查异常：${error.message}` }; }
if (result.decision === 'deny') {
  console.log(JSON.stringify({ hookSpecificOutput: {
    hookEventName: 'PreToolUse', permissionDecision: 'deny', permissionDecisionReason: `[dev-guard] ${result.reason}`,
  } }));
}
