import { checkCommand } from '../policy.mjs';

export default function devGuard(pi) {
  pi.on('tool_call', async (event, ctx) => {
    if (event.toolName !== 'bash') return;
    const result = checkCommand({ cwd: ctx.cwd, command: event.input.command });
    if (result.decision === 'deny') return { block: true, reason: `[dev-guard] ${result.reason}` };
  });
  pi.on('user_bash', async (event, ctx) => {
    const result = checkCommand({ cwd: ctx.cwd, command: event.command });
    if (result.decision === 'deny') {
      return { result: { output: `[dev-guard] ${result.reason}`, exitCode: 1, cancelled: false, truncated: false } };
    }
  });
}
