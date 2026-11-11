import { test, surfaceOf } from '@e2e-dev/web'
import { credentials, expect } from 'e2e'
import { engine } from '../support/engine'
import { environment, SESSION } from '../support/settings.mjs'
import { loadAuth, saveAuth, assertIdentity } from '../support/auth-store.mjs'
import { updateResult } from '../support/result.mjs'

const env = environment(process.env.COMPASS_ENV)
test.setup('环境登录与业务页身份门禁', { sessions: [SESSION], video: 'off', trace: 'off', timeout: 660_000 }, async ({ app, browser, session, screen }) => {
  if (process.env.COMPASS_LIVE_RUN !== '1' || !process.env.COMPASS_RUN_DIR) throw new Error('必须从 ./e2e 入口运行')
  const live = surfaceOf(engine)
  if (!live) throw new Error('AUTH_ENGINE_UNAVAILABLE')
  // Use the public live surface for credential state: never pass cookies through a traced test step.
  await app.open('/query?lang=zh-CN')
  const saved = loadAuth(env.name)
  if (saved) {
    await live.context().setStorageState(saved.storage)
    await app.open('/query?lang=zh-CN')
  }
  async function identity() {
    const url = new URL(await browser.url())
    if (url.origin !== env.appUrl) return null
    return browser.evaluate(() => (window as any).__compassE2E?.identity ?? null)
  }
  let actual: any = null
  try { await expect.poll(async () => Boolean(actual = await identity()), { timeout: saved ? 15_000 : 3000, interval: 500 }).toBe(true) } catch { /* No state or expired state: login is handled below. */ }
  if (!actual && process.env.COMPASS_AUTH_ONLY !== '1' && process.env.COMPASS_MANUAL_LOGIN !== '1') throw new Error('LOGIN_REQUIRED：请先 ./e2e login --env ' + env.name + '，不会自动提交查价或试密码')
  if (!actual) {
    if (process.env.COMPASS_AUTO_ACCOUNT === '1') {
      if (!env.loginUrl) throw new Error('缺少已核实登录入口')
      const account = credentials.user('member')
      await app.open(env.loginUrl)
      await screen.getByRole('textbox', /^(手机号|Phone number)$/).fill(account.username)
      await browser.locator('input[type="password"]').fill(account.password)
      await browser.locator('button.login-btn').click()
      try {
        await expect.poll(async () => !/^\/login\/?$/.test(new URL(await browser.url()).pathname), { timeout: 10_000, interval: 500 }).toBe(true)
        await app.open('/query?lang=zh-CN')
      } catch {
        console.log('AUTO_LOGIN_FAILED：自动登录仅尝试一次，请在当前独立窗口手动登录；不轮换账号或重试密码。')
      }
    }
    if (process.env.COMPASS_AUTO_ACCOUNT !== '1' && !actual) await app.open(env.loginUrl || 'https://login.hgj.com/login')
    console.log(`MANUAL_LOGIN_READY ${env.name}：在独立 Chrome 中登录并返回查价页；登录态仅加密保存于本机。`)
    await expect.poll(async () => {
      const url = new URL(await browser.url())
      return url.origin === env.appUrl && await browser.locator('textarea').isVisible()
    }, { timeout: 600_000, interval: 1000 }).toBe(true)
    await app.open('/query?lang=zh-CN')
    await expect.poll(async () => Boolean(actual = await identity()), { timeout: 45_000 }).toBe(true)
  }
  assertIdentity(actual, saved?.identity)
  await expect(browser.locator('textarea')).toBeEnabled()
  await expect(screen.getByText('欢迎使用仟询', { exact: false })).not.toBeVisible()
  const storage = await live.context().storageState({ indexedDB: true })
  storage.origins = storage.origins.filter(origin => origin.origin === env.appUrl)
  const hosts = ['hgj.com', ...(env.name === 'dev' ? ['iter-apisix.hgj.com'] : env.name === 'prod' ? ['whale-ingress-ng.hgj.com'] : []), new URL(env.appUrl).hostname, `${env.name === 'prod' ? '' : env.name + '-'}login.hgj.com`, `${env.name === 'prod' ? '' : env.name + '-'}apisix.hgj.com`]
  storage.cookies = storage.cookies.filter(cookie => hosts.includes(cookie.domain.replace(/^\./, '')))
  // Prove restoration in a fresh context, using the same browser but not the signed-in context.
  const independent = await live.context().browser()!.newContext({ storageState: storage })
  try {
    const page = await independent.newPage()
    await page.addInitScript({ path: new URL('../support/freight-capture.js', import.meta.url).pathname })
    await page.goto(env.appUrl + '/query?lang=zh-CN')
    await page.waitForFunction(() => Boolean((window as any).__compassE2E?.identity), undefined, { timeout: 45_000 })
    const restored = await page.evaluate(() => (window as any).__compassE2E.identity)
    assertIdentity(restored, actual)
    await page.locator('textarea').waitFor({ state: 'visible', timeout: 30_000 })
  } finally { await independent.close() }
  saveAuth(env.name, actual, storage)
  updateResult(process.env.COMPASS_RUN_DIR, result => { result.authentication = { status: '通过', independentRestore: true, sameIdentity: true, source: saved ? 'encrypted-cache' : 'login', checkedAt: new Date().toISOString() } })
  await session.save(SESSION)
  console.log(`AUTH_READY ${env.name}：真实身份、输入框及独立恢复验证通过；本机加密登录态已保存。`)
})
