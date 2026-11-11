import type { E2EConfig } from 'e2e'
import { engine } from './support/engine'
import { environment, loadSuite, scenarioTimeout } from './support/settings.mjs'

const env = environment(process.env.COMPASS_ENV)
const suite = loadSuite(process.env.COMPASS_CASES)
export default {
  targets: [{
    name: 'compass-web',
    engine,
    app: { url: env.appUrl },
  }],
  tests: process.env.COMPASS_AUTH_ONLY === '1' ? ['tests/auth.setup.e2e.ts', 'tests/auth-check.e2e.ts'] : ['tests/**/*.e2e.ts'],
  credentials: {
    member: {
      username: process.env.E2E_USER_MEMBER_USERNAME || 'not-configured',
      password: () => {
        const value = process.env.E2E_USER_MEMBER_PASSWORD
        if (!value) throw new Error('缺少 E2E_USER_MEMBER_PASSWORD')
        return value
      },
    },
  },
  workers: 1,
  retries: 0,
  timeout: Math.max(...suite.scenarios.map(scenarioTimeout)),
  maxDuration: 720_000 + suite.scenarios.reduce((sum, s) => sum + scenarioTimeout(s), 0),
  cleanupTimeout: 30_000,
  actionTimeout: 30_000,
  trace: 'on',
  video: 'off',
  output: '.work/unstarted',
} satisfies E2EConfig
