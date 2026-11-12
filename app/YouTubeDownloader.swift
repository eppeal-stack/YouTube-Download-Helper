import Cocoa
import Darwin

final class App: NSObject, NSApplicationDelegate, NSWindowDelegate {
    var window: NSWindow!
    let input = NSTextView(), log = NSTextView()
    let destination = NSTextField(string: UserDefaults.standard.string(forKey: "destination") ?? (NSHomeDirectory() + "/Movies/YouTube Downloads"))
    let proxy = NSTextField(string: UserDefaults.standard.string(forKey: "proxy") ?? "")
    let status = NSTextField(labelWithString: "准备就绪 · 粘贴链接后开始下载")
    let start = NSButton(title: "下载视频和封面", target: nil, action: nil)
    let stop = NSButton(title: "停止", target: nil, action: nil)
    let update = NSButton(title: "更新下载组件", target: nil, action: nil)
    let cover = NSButton(checkboxWithTitle: "只下载封面", target: nil, action: nil)
    var process: Process?
    var root: String { Bundle.main.object(forInfoDictionaryKey: "WorkspaceRoot") as! String }
    func label(_ text: String, size: CGFloat = 13) -> NSTextField {
        let label = NSTextField(labelWithString: text)
        label.font = .systemFont(ofSize: size)
        return label
    }
    func scroll(_ view: NSTextView, height: CGFloat, editable: Bool) -> NSScrollView {
        let scroll = NSScrollView()
        scroll.documentView = view; scroll.hasVerticalScroller = true
        scroll.borderType = .bezelBorder
        view.isEditable = editable; view.isRichText = false
        view.font = .monospacedSystemFont(ofSize: 12, weight: .regular)
        view.isVerticallyResizable = true; view.isHorizontallyResizable = false
        view.autoresizingMask = [.width]
        view.textContainer?.widthTracksTextView = true
        view.textContainerInset = NSSize(width: 10, height: 10)
        scroll.heightAnchor.constraint(equalToConstant: height).isActive = true
        return scroll
    }
    func applicationDidFinishLaunching(_ notification: Notification) {
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 800, height: 760), styleMask: [.titled, .closable, .miniaturizable], backing: .buffered, defer: false)
        window.title = "YouTube 下载助手"; window.delegate = self
        let stack = NSStackView(); stack.orientation = .vertical; stack.alignment = .leading; stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        window.contentView!.addSubview(stack)
        NSLayoutConstraint.activate([stack.leadingAnchor.constraint(equalTo: window.contentView!.leadingAnchor, constant: 24), stack.trailingAnchor.constraint(equalTo: window.contentView!.trailingAnchor, constant: -24), stack.topAnchor.constraint(equalTo: window.contentView!.topAnchor, constant: 24)])
        stack.addArrangedSubview(label("YouTube 下载助手", size: 25))
        stack.addArrangedSubview(label("1080p 上限 · 英文音轨 · MP4 + JPG · 本机运行，无需 AI"))
        stack.addArrangedSubview(label("视频链接（支持多个链接、分号分隔或整段粘贴，自动去重）"))
        let inputScroll = scroll(input, height: 125, editable: true); stack.addArrangedSubview(inputScroll)
        stack.addArrangedSubview(label("保存目录")); stack.addArrangedSubview(destination)
        let folder = NSButton(title: "选择目录…", target: self, action: #selector(chooseFolder))
        let open = NSButton(title: "打开保存目录", target: self, action: #selector(openFolder))
        let folderRow = NSStackView(views: [folder, open]); folderRow.spacing = 10; stack.addArrangedSubview(folderRow)
        proxy.placeholderString = "可选，例如 http://127.0.0.1:7890（按代理软件实际设置）"
        stack.addArrangedSubview(label("代理地址（可选，留空沿用当前网络）")); stack.addArrangedSubview(proxy)
        start.target = self; start.action = #selector(download); start.bezelStyle = .rounded; start.keyEquivalent = "\r"
        stop.target = self; stop.action = #selector(cancel); stop.isEnabled = false
        update.target = self; update.action = #selector(upgrade)
        let actions = NSStackView(views: [start, cover, stop, update]); actions.spacing = 12; stack.addArrangedSubview(actions)
        stack.addArrangedSubview(status)
        let logScroll = scroll(log, height: 220, editable: false); stack.addArrangedSubview(logScroll)
        let note = label("没有英文音轨时保留失败提示；无 1080p 时选较低画质。失败项可原链接重试。", size: 11)
        note.textColor = .secondaryLabelColor; stack.addArrangedSubview(note)
        for v in [inputScroll, destination, proxy, logScroll] { v.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true }
        let menu = NSMenu(), item = NSMenuItem(), appMenu = NSMenu()
        appMenu.addItem(withTitle: "退出下载助手", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        item.submenu = appMenu; menu.addItem(item)
        let editItem = NSMenuItem(), edit = NSMenu(title: "编辑")
        for (name, action, key) in [("剪切", "cut:", "x"), ("复制", "copy:", "c"), ("粘贴", "paste:", "v"), ("全选", "selectAll:", "a")] { edit.addItem(withTitle: name, action: Selector(action), keyEquivalent: key) }
        editItem.submenu = edit; menu.addItem(editItem); NSApp.mainMenu = menu
        window.center(); window.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true)
    }
    @objc func chooseFolder() {
        let panel = NSOpenPanel(); panel.canChooseDirectories = true; panel.canChooseFiles = false
        if panel.runModal() == .OK, let url = panel.url { destination.stringValue = url.path }
    }
    @objc func openFolder() { NSWorkspace.shared.open(URL(fileURLWithPath: destination.stringValue)) }
    @objc func download() { run(upgrading: false) }
    @objc func upgrade() { run(upgrading: true) }
    func busy(_ value: Bool) {
        start.isEnabled = !value; update.isEnabled = !value; stop.isEnabled = value
        destination.isEnabled = !value; proxy.isEnabled = !value; cover.isEnabled = !value
    }
    func append(_ text: String) {
        log.string += text + "\n"
        if log.string.count > 70000 { log.string = String(log.string.suffix(50000)) }
        log.scrollToEndOfDocument(nil)
    }
    func run(upgrading: Bool) {
        guard process == nil else { return }
        guard upgrading || !input.string.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { status.stringValue = "请先粘贴 YouTube 视频链接"; return }
        UserDefaults.standard.set(destination.stringValue, forKey: "destination")
        UserDefaults.standard.set(proxy.stringValue, forKey: "proxy")
        log.string = ""; busy(true); status.stringValue = upgrading ? "正在更新组件…" : "正在解析下载队列…"
        let p = Process(), output = Pipe(), stdin = Pipe()
        p.executableURL = URL(fileURLWithPath: root + "/.venv/bin/python")
        p.arguments = [root + "/app/worker.py", "--output", destination.stringValue, "--proxy", proxy.stringValue]
        if upgrading { p.arguments!.append("--update") }
        if cover.state == .on { p.arguments!.append("--thumbnail-only") }
        p.standardOutput = output; p.standardError = output; p.standardInput = stdin
        process = p
        do { try p.run() } catch { append(error.localizedDescription); process = nil; busy(false); status.stringValue = "无法启动，请检查工作区路径"; return }
        stdin.fileHandleForWriting.write(input.string.data(using: .utf8) ?? Data()); try? stdin.fileHandleForWriting.close()
        DispatchQueue.global().async {
            var buffer = Data()
            while true {
                let data = output.fileHandleForReading.availableData
                if data.isEmpty { break }
                buffer.append(data)
                while let range = buffer.range(of: Data([10])) {
                    let line = buffer.subdata(in: 0..<range.lowerBound); buffer.removeSubrange(0..<range.upperBound)
                    DispatchQueue.main.async { self.event(line) }
                }
            }
            p.waitUntilExit()
            DispatchQueue.main.async {
                if !buffer.isEmpty { self.append(String(decoding: buffer, as: UTF8.self)) }
                if self.status.stringValue.hasPrefix("正在") { self.status.stringValue = "任务未完成，请查看日志；网络恢复后可重试" }
                self.process = nil; self.busy(false)
            }
        }
    }
    func event(_ data: Data) {
        guard let item = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any], let kind = item["kind"] as? String else { append(String(decoding: data, as: UTF8.self)); return }
        let message = item["message"] as? String ?? ""
        switch kind {
        case "start": status.stringValue = "正在处理 \(item["index"]!) / \(item["total"]!)"; append("\n—— " + message + " ——")
        case "log": append(message)
        case "error": status.stringValue = message; append(message)
        case "item": append((item["success"] as? Bool == true) ? "✓ 此项完成" : "✕ 此项失败；后续项目将继续。检查网络、代理或英文音轨。")
        case "done": status.stringValue = "完成：\(item["succeeded"]!) 项成功，\(item["failed"]!) 项失败"; append(status.stringValue)
        default: break
        }
    }
    @objc func cancel() {
        if let p = process, p.isRunning { if kill(-p.processIdentifier, SIGTERM) != 0 { p.terminate() }; status.stringValue = "已停止，断点文件保留，可重新下载" }
    }
    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply { cancel(); return .terminateNow }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
}
let app = NSApplication.shared
let delegate = App()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
