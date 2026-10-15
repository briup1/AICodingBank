#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';

export async function runBatch({ concurrency = 3, jobs }) {
  if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > 3) throw new Error('concurrency must be 1..3');
  if (!Array.isArray(jobs) || jobs.some(j => !j || !/^[a-z0-9_-]+$/i.test(j.id || '') || typeof j.command !== 'string' || !j.command.trim()
      || !Number.isInteger(j.timeoutMs) || j.timeoutMs < 1 || j.timeoutMs > 600000)
      || new Set(jobs.map(j => j.id)).size !== jobs.length) throw new Error('invalid or duplicate jobs; timeoutMs must be 1..600000');
  let next = 0;
  const results = new Array(jobs.length);
  await Promise.all(Array.from({ length: Math.min(concurrency, jobs.length) }, async () => {
    while (next < jobs.length) {
      const index = next++, job = jobs[index];
      results[index] = await new Promise(resolve => {
        const startedAt = new Date().toISOString();
        const child = spawn('/bin/sh', ['-c', job.command], { detached: true, stdio: 'ignore' });
        let timedOut = false;
        const timer = setTimeout(() => {
          timedOut = true;
          try { process.kill(-child.pid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') throw error; }
        }, job.timeoutMs);
        child.once('error', error => { clearTimeout(timer); resolve({ id: job.id, startedAt, status: 'failed', error: error.message }); });
        child.once('exit', (code, signal) => {
          clearTimeout(timer);
          resolve({ id: job.id, startedAt, endedAt: new Date().toISOString(), status: timedOut ? 'timeout' : code === 0 ? 'passed' : 'failed', code, signal });
        });
      });
    }
  }));
  return results;
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  try {
    const results = await runBatch(JSON.parse(fs.readFileSync(process.argv[2], 'utf8')));
    console.log(JSON.stringify(results, null, 2));
    if (results.some(r => r.status !== 'passed')) process.exitCode = 1;
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
