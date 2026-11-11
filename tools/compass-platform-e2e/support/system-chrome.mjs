import { spawn } from 'node:child_process'
import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { setTimeout } from 'node:timers/promises'

// Dedicated temporary profile; never attach to the user's daily Chrome.
export function systemChrome() {
  const children = new Map()
  async function close(child, profile) {
    if (child && child.exitCode === null) {
      child.kill('SIGTERM')
      for (let i = 0; i < 50 && child.exitCode === null; i++) await setTimeout(100)
      if (child.exitCode === null) { child.kill('SIGKILL'); await new Promise(done => child.once('exit', done)) }
    }
    await rm(profile, { recursive: true, force: true })
  }
  return {
    name: 'isolated-system-chrome',
    scope: 'worker',
    async acquire(request) {
      const profile = await mkdtemp(join(tmpdir(), 'compass-e2e-chrome-'))
      const child = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
        `--user-data-dir=${profile}`, '--remote-debugging-port=0', '--remote-debugging-address=127.0.0.1',
        '--no-first-run', '--no-default-browser-check', ...(request.env.COMPASS_AUTH_ONLY === '1' || request.env.COMPASS_MANUAL_LOGIN === '1' || request.env.COMPASS_HEADED === '1' ? [] : ['--headless=new']), 'about:blank',
      ], { stdio: 'ignore' })
      let launchError
      child.on('error', error => { launchError = error })
      try {
        for (let i = 0; i < 200; i++) {
          request.signal.throwIfAborted()
          if (launchError || child.exitCode !== null) throw new Error('系统 Chrome 启动失败')
          try {
            const port = (await readFile(join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]
            if (/^\d+$/.test(port)) {
              children.set(profile, child)
              return { id: profile, cdpEndpoint: `http://127.0.0.1:${port}` }
            }
          } catch { /* Chrome has not published its local endpoint yet. */ }
          await setTimeout(100, undefined, { signal: request.signal })
        }
        throw new Error('系统 Chrome CDP 启动超时')
      } catch (error) { await close(child, profile); throw error }
    },
    async release(lease) {
      const child = children.get(lease.id)
      if (!child) return
      children.delete(lease.id)
      await close(child, lease.id)
    },
  }
}
