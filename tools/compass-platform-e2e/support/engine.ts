import { web } from '@e2e-dev/web'
import { resolve } from 'node:path'
import { systemChrome } from './system-chrome.mjs'
import { ROOT } from './settings.mjs'
export const engine = web({ browser: systemChrome(), initScripts: [{ path: resolve(ROOT, 'support/freight-capture.js') }] })
