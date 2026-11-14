import { test } from '@e2e-dev/web'
import { expect } from 'e2e'
import { relative } from 'node:path'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { environment, loadSuite, SESSION, LIMITS, scenarioTimeout } from '../support/settings.mjs'
import { updateTurn } from '../support/result.mjs'
import { summarize, assertTurn, uiReady } from '../support/assertions.mjs'

const suite = loadSuite(process.env.COMPASS_CASES)
const env = environment(process.env.COMPASS_ENV)
const runDir = process.env.COMPASS_RUN_DIR

for (const scenario of suite.scenarios) {
  test(`${scenario.id} (${scenario.turns.length}轮)`, { session: SESSION, retries: 0, timeout: scenarioTimeout(scenario) }, async ({ app, browser }) => {
    if (process.env.COMPASS_LIVE_RUN !== '1' || !runDir) throw new Error('请使用 ./e2e run；未创建结果检查点时禁止查询')
    const result = JSON.parse(readFileSync(`${runDir}/result.json`, 'utf8'))
    const currentHash = createHash('sha256').update(readFileSync(process.env.COMPASS_CASES!)).digest('hex')
    if (currentHash !== result.cases.sha256) throw new Error('用例文件在运行期间变化，停止提交')
    if (result.items.some((item: any) => item.caseId === scenario.id && item.status !== '未执行')) throw new Error('场景已有提交/执行记录，拒绝自动重放')
    await app.open('/query?lang=zh-CN')
    expect(new URL(await browser.url()).origin).toBe(env.appUrl)
    // 冷启动首屏可能只渲染 #root（SPA 未挂载），默认 5s 会误判为失败；这里给出与 actionTimeout 一致的等待。
    await expect(browser.locator('textarea')).toBeVisible({ timeout: 30_000 })
    await browser.locator('button').filter({ hasText: '新会话' }).click()
    await expect(browser.locator('.smart-a-chat-message.is-user')).toHaveCount(0)
    let session: string | null = null
    const tasks = new Set<string>()

    for (const [index, turn] of scenario.turns.entries()) {
      const number = index + 1
      let actual: any = null
      let ui: any = null
      let taskPoll: any = null
      let failure: unknown
      let screenshotError = ''
      let screenshot: string | null = null
      const before = await browser.evaluate(() => (window as any).__compassE2E?.chats.length ?? -1)
      if (before < 0) throw new Error('采集器未加载，禁止发送')
      const assistantCount = await browser.locator('.smart-a-chat-message.is-assistant').count()
      const readChat = () => browser.evaluate(i => (window as any).__compassE2E?.chats[i] ?? null, before)
      const readUi = () => browser.evaluate(previousCount => {
        const messages = document.querySelectorAll<HTMLElement>('.smart-a-chat-message.is-assistant')
        const latest = messages.length > previousCount ? messages[messages.length - 1] : null
        const visible = (node: Element) => (node as HTMLElement).getClientRects().length > 0 && getComputedStyle(node).visibility !== 'hidden'
        const cards = [...(latest?.querySelectorAll('[data-welfare-guide-target="freight-card"]') ?? [])].filter(visible)
        const empty = [...(latest?.querySelectorAll('[class$="__empty-text"], [class$="__route-empty-text"]') ?? [])].some(visible)
        const input = document.querySelector<HTMLTextAreaElement>('textarea')
        // 结果可能折叠在“查看全部 N 条结果”入口后；该入口的条数即接口已返回的结果数。
        const hint = latest?.innerText.match(/查看全部\s*(\d+)\s*条结果/)
        return { exists: Boolean(latest), cards: cards.length, empty, totalHint: hint ? Number(hint[1]) : null, text: latest?.innerText.slice(0, 16000) ?? '', cardTexts: cards.map(node => (node as HTMLElement).innerText.slice(0, 2000)), inputEnabled: Boolean(input && !input.disabled) }
      }, assistantCount)
      updateTurn(runDir, scenario.id, number, (item: any) => {
        item.status = '进行中'
        item.context = { phase: 'prepared', requestSession: session, startedAt: new Date().toISOString() }
      })
      try {
        await expect(browser.locator('textarea')).toBeEnabled({ timeout: 30_000 })
        await browser.locator('textarea').fill(turn.message)
        updateTurn(runDir, scenario.id, number, (item: any) => { item.context.phase = 'submitting' })
        // The only send action. Never put this action in polling, retries or recovery.
        await browser.locator('button.smart-a-chat-input__send-btn').click()
        await expect.poll(async () => {
          const chat: any = await readChat()
          if (chat) updateTurn(runDir, scenario.id, number, (item: any) => {
            const summary = summarize(chat)
            item.context.phase = 'observing'
            item.context.sessionId = summary.session
            item.context.taskId = summary.taskId
          })
          return chat?.error || (chat?.done ? 'done' : 'pending')
        }, { timeout: LIMITS.sse, interval: 1000 }).toBe('done')
        actual = summarize(await readChat())
        const chatCount = await browser.evaluate(() => (window as any).__compassE2E.chats.length)
        expect(chatCount).toBe(before + 1)
        expect(actual.message).toBe(turn.message)
        assertTurn(actual, turn.expect, session, tasks)
        if (index === 0) {
          const previous = JSON.parse(readFileSync(`${runDir}/result.json`, 'utf8'))
          if (previous.items.some((item: any) => item.caseId !== scenario.id && item.context?.sessionId === actual.session)) throw new Error('不同场景复用了同一个后端会话')
        }
        session = actual.session
        if (actual.taskId) tasks.add(actual.taskId)
        if (turn.expect.action === 'new_search') {
          // has_polling=false 表示首次响应已拿到全部结果，前端不会发起轮询，
          // 任务在查价返回时即已结束；此时以查价返回的条数与页面卡片交叉核对。
          if (actual.queryContext?.has_polling === false) {
            const syncCount = (actual.frames ?? [])
              .filter((frame: any) => frame.type === 'tool_end' && frame.tool === 'unified_search')
              .reduce((sum: number, frame: any) => sum + (frame.outputCount ?? 0), 0)
            taskPoll = { at: new Date().toISOString(), taskId: actual.taskId, kind: 'sync', status: 200, taskStatus: 'COMPLETE', count: syncCount, error: null }
            updateTurn(runDir, scenario.id, number, (item: any) => { item.context.lastPoll = taskPoll })
          } else {
          await expect.poll(async () => {
            taskPoll = await browser.evaluate(taskId => {
              const polls = (window as any).__compassE2E?.polls ?? []
              return [...polls].reverse().find((p: any) => p.taskId === taskId && (p.taskStatus || p.error)) ?? null
            }, actual.taskId)
            if (taskPoll) updateTurn(runDir, scenario.id, number, (item: any) => { item.context.lastPoll = taskPoll })
            return taskPoll?.error || taskPoll?.taskStatus || 'unobserved'
          }, { timeout: LIMITS.task, interval: 1500 }).not.toMatch(/^(CHECKING|unobserved)$/)
          expect(taskPoll?.taskStatus).toBe('COMPLETE')
          }
        }
        await expect.poll(async () => {
          ui = await readUi()
          const agreesWithTask = turn.expect.action !== 'new_search' || (taskPoll.count === 0 ? ui.cards === 0 && ui.empty : taskPoll.count > 0 && (ui.cards > 0 || ui.totalHint === taskPoll.count))
          return agreesWithTask && uiReady(ui, turn.expect, actual.text)
        }, { timeout: LIMITS.ui, interval: 500 }).toBe(true)
      } catch (error) {
        failure = error
      } finally {
        try { actual = summarize(await readChat()); ui = await readUi() } catch { /* Preserve earlier evidence if the browser closed. */ }
        try { screenshot = await app.screenshot(`${scenario.id}-turn-${number}`) }
        catch { screenshotError = '截图未取得' }
        const polls = await browser.evaluate(taskId => (window as any).__compassE2E?.polls.filter((p: any) => p.taskId === taskId) ?? [], actual?.taskId).catch(() => [])
        updateTurn(runDir, scenario.id, number, (item: any) => {
          item.status = failure ? '失败' : screenshotError ? '阻塞' : '通过'
          // Avoid serializing runner exceptions: they may include unrelated screen contents.
          item.issue = failure ? '该轮断言/等待失败，详见本轮 runner trace；不自动重发' : screenshotError
          item.actual = `SSE=${actual?.done ?? false}; task=${taskPoll?.taskStatus ?? '未要求或未观测'}; 当前回复卡片=${ui?.cards ?? '未知'}`
          item.context = { ...item.context, phase: 'observed', endedAt: new Date().toISOString(), sessionId: actual?.session, taskId: actual?.taskId, chat: actual, polls, ui }
          if (screenshot) item.evidence.push(relative(runDir, screenshot))
        })
        console.log(`TURN_RESULT ${JSON.stringify({ caseId: scenario.id, turn: number, taskId: actual?.taskId, sessionId: actual?.session, cards: ui?.cards, failed: Boolean(failure || screenshotError) })}`)
      }
      if (failure) throw failure
      if (screenshotError) throw new Error(screenshotError)
    }
  })
}
