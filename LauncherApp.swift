import AppKit
import Foundation

/// The Dock app resolves movable bookmarks to the launcher and the show, then calls the launcher.
@main
struct LauncherApp {
    static func main() {
        let app = NSApplication.shared
        app.setActivationPolicy(.accessory)
        let name = Bundle.main.object(forInfoDictionaryKey: "CFBundleName") as? String ?? "QLC+ Launcher"
        do {
            let resources = Bundle.main.resourceURL!
            let state = FileManager.default.homeDirectoryForCurrentUser
                .appendingPathComponent("Library/Application Support/\(name)")
            let launcher = try resolveBookmark(at: state.appendingPathComponent("Launcher.bookmark"))
            let script = launcher.appendingPathComponent("launch.py")
            guard FileManager.default.fileExists(atPath: script.path) else {
                throw NSError(domain: name, code: 1, userInfo: [
                    NSLocalizedDescriptionKey:
                        "Launcher script is missing at \(script.path). Restore the qlc-launcher checkout or run its installer again."
                ])
            }
            var arguments = [script.path, "--name", name]
            arguments += workspaceArguments(bookmark: state.appendingPathComponent("Workspace.bookmark"))
            let python = try String(
                contentsOf: resources.appendingPathComponent("PythonPath"), encoding: .utf8
            ).trimmingCharacters(in: .whitespacesAndNewlines)
            let process = Process()
            process.executableURL = URL(fileURLWithPath: python)
            process.arguments = arguments
            process.currentDirectoryURL = launcher
            try process.run()
            process.waitUntilExit()
            if process.terminationStatus != 0 {
                exit(process.terminationStatus)
            }
        } catch {
            app.activate(ignoringOtherApps: true)
            let alert = NSAlert()
            alert.messageText = "\(name) could not start"
            alert.informativeText = "\(error.localizedDescription)\nRun install.py from the qlc-launcher checkout to repair the launcher."
            alert.alertStyle = .critical
            alert.runModal()
            exit(1)
        }
    }
}
