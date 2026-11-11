import { readFileSync, writeFileSync, renameSync } from 'node:fs'
import { resolve } from 'node:path'

export function updateResult(runDir, change) {
  const path = resolve(runDir, 'result.json')
  const result = JSON.parse(readFileSync(path, 'utf8'))
  change(result)
  result.updatedAt = new Date().toISOString()
  writeFileSync(`${path}.tmp`, JSON.stringify(result, null, 2) + '\n', { mode: 0o600 })
  renameSync(`${path}.tmp`, path)
  return result
}

export function updateTurn(runDir, caseId, turn, change) {
  return updateResult(runDir, result => {
    const item = result.items.find(item => item.caseId === caseId && item.step === String(turn))
    if (!item) throw new Error('结果中缺少当前检查点，拒绝提交')
    change(item)
    item.updatedAt = new Date().toISOString()
  })
}

export function finishResult(runDir, exitCode) {
  return updateResult(runDir, result => {
    result.status = '已结束'
    result.endedAt = new Date().toISOString()
    result.exitCode = exitCode
    for (const item of result.items) {
      if (item.status === '进行中' || item.status === '未执行') {
        item.status = '阻塞'
        item.issue ||= '运行结束但该轮未获得完整结果；先回读已有会话和任务，禁止直接重发'
      }
    }
  })
}
