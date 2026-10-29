import AppKit

// A native entry point for the upstream UI, not a second browser manager.
final class BrowserConsole: NSObject, NSApplicationDelegate {
    private var busy = false
    private var lastStatus = "正在检查控制台…"
    private let node = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".node/bin/node").path
    private var controller: String {
        if let bundled = Bundle.main.path(forResource: "console", ofType: "mjs") { return bundled }
        return Bundle.main.object(forInfoDictionaryKey: "BrowserConsoleController") as? String ?? ""
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        let menu = NSMenu()
        let appMenu = NSMenu()
        let item = NSMenuItem()
        menu.addItem(item)
        item.submenu = appMenu
        appMenu.addItem(withTitle: "打开控制台", action: #selector(openConsole), keyEquivalent: "o").target = self
        appMenu.addItem(withTitle: "查看运行状态", action: #selector(showStatus), keyEquivalent: "i").target = self
        appMenu.addItem(withTitle: "停止控制台服务…", action: #selector(stopConsole), keyEquivalent: "").target = self
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "退出自动化浏览器…", action: #selector(quit), keyEquivalent: "q").target = self
        NSApp.mainMenu = menu
        NSApp.applicationIconImage = NSImage(systemSymbolName: "globe.badge.clock", accessibilityDescription: "自动化浏览器")
        openConsole()
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        openConsole()
        return false
    }

    private func invoke(_ action: String, completion: @escaping (Bool, String) -> Void) {
        guard !busy else { return }
        guard !controller.isEmpty else { completion(false, "启动器缺少工具路径，请重新安装本机入口。"); return }
        busy = true
        let executable = node
        let script = controller
        DispatchQueue.global(qos: .userInitiated).async {
            let process = Process()
            process.executableURL = URL(fileURLWithPath: executable)
            process.arguments = [script, action]
            let output = Pipe()
            let errors = Pipe()
            process.standardOutput = output
            process.standardError = errors
            var success = false
            var message = ""
            do {
                try process.run()
                // Controller responses are bounded and do not contain cookies or page contents.
                let data = output.fileHandleForReading.readDataToEndOfFile()
                let errorData = errors.fileHandleForReading.readDataToEndOfFile()
                process.waitUntilExit()
                success = process.terminationStatus == 0
                message = String(data: success ? data : errorData, encoding: .utf8) ?? "无法读取工具返回。"
            } catch { message = error.localizedDescription }
            let didSucceed = success
            let response = message
            DispatchQueue.main.async {
                self.busy = false
                completion(didSucceed, response)
            }
        }
    }

    private func alert(_ title: String, _ message: String) {
        NSApp.activate(ignoringOtherApps: true)
        let dialog = NSAlert()
        dialog.messageText = title
        dialog.informativeText = message
        dialog.addButton(withTitle: "知道了")
        dialog.runModal()
    }

    @objc private func openConsole() {
        invoke("open") { success, message in
            if !success { self.alert("控制台未能打开", message) }
            else { self.lastStatus = "控制台已打开：http://localhost:4848" }
        }
    }

    @objc private func showStatus() {
        invoke("status") { success, message in
            guard success, let data = message.data(using: .utf8),
                  let status = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                self.alert("无法确认运行状态", message)
                return
            }
            if status["running"] as? Bool == true {
                self.lastStatus = "控制台服务运行中\n地址：http://localhost:4848\n可发现会话：\(status["sessions"] ?? 0)\n\n会话数不等于正在执行的任务数。"
            } else { self.lastStatus = "控制台服务已停止。浏览器会话需在控制台内单独关闭。" }
            self.alert("自动化浏览器", self.lastStatus)
        }
    }

    @objc private func stopConsole() { confirmStop(thenQuit: false) }
    @objc private func quit() { confirmStop(thenQuit: true) }

    private func confirmStop(thenQuit: Bool) {
        guard !busy else { return }
        let dialog = NSAlert()
        dialog.messageText = thenQuit ? "退出自动化浏览器？" : "停止控制台服务？"
        dialog.informativeText = "只停止管理面板，不会关闭任何自动化浏览器会话。要结束任务，请先在网页中关闭对应会话。关闭网页本身不会停止服务。"
        dialog.addButton(withTitle: thenQuit ? "停止面板并退出" : "停止面板")
        dialog.addButton(withTitle: "取消")
        guard dialog.runModal() == .alertFirstButtonReturn else { return }
        invoke("stop") { success, message in
            if !success { self.alert("未能确认服务已停止", message); return }
            self.lastStatus = "控制台服务已停止。"
            if thenQuit { NSApp.terminate(nil) }
            else { self.alert("已停止控制台", "浏览器会话未受影响。点击 Dock 图标可以重新打开控制台。") }
        }
    }
}

let app = NSApplication.shared
let delegate = BrowserConsole()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
