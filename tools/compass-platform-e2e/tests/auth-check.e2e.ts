import {test} from '@e2e-dev/web'
import {expect} from 'e2e'
import {SESSION, environment} from '../support/settings.mjs'
import {loadAuth,assertIdentity} from '../support/auth-store.mjs'
if (process.env.COMPASS_AUTH_ONLY === '1') test('登录态跨测试恢复验证（不查价）',{session:SESSION,trace:'off'},async({app,browser})=>{
 const env=environment(process.env.COMPASS_ENV)
 await app.open('/query?lang=zh-CN')
 let identity:any=null
 await expect.poll(async()=>Boolean(identity=await browser.evaluate(()=>(window as any).__compassE2E?.identity)),{timeout:45000}).toBe(true)
 assertIdentity(identity,loadAuth(env.name)?.identity)
 await expect(browser.locator('textarea')).toBeEnabled()
})
