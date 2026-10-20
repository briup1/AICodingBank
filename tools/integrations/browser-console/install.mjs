#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { mkdir, access, writeFile, copyFile } from 'node:fs/promises';
import { homedir, tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const directory = dirname(fileURLToPath(import.meta.url));
const app = join(homedir(), 'Applications/自动化浏览器.app');
try {
  await access(app);
  throw new Error(`入口已存在，未覆盖：${app}`);
} catch (error) { if (error.code !== 'ENOENT') throw error; }
// Compile first so a failed build does not leave a broken app in Applications.
const executable = join(tmpdir(), `browser-console-${process.pid}`);
execFileSync('/usr/bin/xcrun', ['swiftc', '-swift-version', '5', '-O', '-framework', 'AppKit',
  join(directory, 'BrowserConsole.swift'), '-o', executable], { stdio: 'inherit' });
await mkdir(join(app, 'Contents/MacOS'), { recursive: true });
await mkdir(join(app, 'Contents/Resources'), { recursive: true });
const escape = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
await writeFile(join(app, 'Contents/Info.plist'), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>BrowserConsole</string>
<key>CFBundleIdentifier</key><string>local.aicodingbank.browser-console</string>
<key>CFBundleName</key><string>自动化浏览器</string>
<key>CFBundleDisplayName</key><string>自动化浏览器</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleVersion</key><string>1</string>
<key>CFBundleShortVersionString</key><string>1.0</string>
<key>NSHighResolutionCapable</key><true/>
<key>BrowserConsoleController</key><string>${escape(join(app, 'Contents/Resources/console.mjs'))}</string>
</dict></plist>\n`);
const { rename } = await import('node:fs/promises');
await rename(executable, join(app, 'Contents/MacOS/BrowserConsole'));
await copyFile(join(directory, 'console.mjs'), join(app, 'Contents/Resources/console.mjs'));
execFileSync('/usr/bin/codesign', ['--force', '--sign', '-', app], { stdio: 'inherit' });
execFileSync('/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister', ['-f', app]);
console.log(app);
