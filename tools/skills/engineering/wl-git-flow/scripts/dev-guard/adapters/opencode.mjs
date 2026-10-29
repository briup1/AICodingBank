import { checkCommand } from '../policy.mjs';

export const DevGuard = async ({ directory }) => ({
  'tool.execute.before': async (input, output) => {
    if (input.tool !== 'bash') return;
    const result = checkCommand({ cwd: output.args.workdir || directory, command: output.args.command });
    if (result.decision === 'deny') throw new Error(`[dev-guard] ${result.reason}`);
  },
});
