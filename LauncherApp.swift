import AppKit
import Foundation

/// The Dock app resolves a movable repository bookmark and calls its script.
@main
struct LauncherApp {
    static func main() {
        let app = NSApplication.shared
        app.setActivationPolicy(.accessory)
        do {
            let resources = Bundle.main.resourceURL!
            let state = FileManager.default.homeDirectoryForCurrentUser
                .appendingPathComponent("Library/Application Support/QLC+ Vibra")
            let bookmark = state.appendingPathComponent("Repository.bookmark")
            let data = try Data(contentsOf: bookmark)
            var stale = false
            let repository = try URL(
                resolvingBookmarkData: data, options: [.withoutUI, .withoutMounting],
                relativeTo: nil, bookmarkDataIsStale: &stale
            )
            if stale {
                try repository.bookmarkData().write(to: bookmark, options: .atomic)
            }
            let script = repository.appendingPathComponent("tools/qlc-launcher/launch.py")
            guard FileManager.default.fileExists(atPath: script.path) else {
                throw NSError(domain: "QLC+ Vibra", code: 1, userInfo: [
                    NSLocalizedDescriptionKey:
                        "Launcher script is missing at \(script.path). Restore the repository or run its installer again."
                ])
            }
            let python = try String(
                contentsOf: resources.appendingPathComponent("PythonPath"), encoding: .utf8
            ).trimmingCharacters(in: .whitespacesAndNewlines)
            let process = Process()
            process.executableURL = URL(fileURLWithPath: python)
            process.arguments = [script.path]
            process.currentDirectoryURL = repository
            try process.run()
            process.waitUntilExit()
            if process.terminationStatus != 0 {
                exit(process.terminationStatus)
            }
        } catch {
            app.activate(ignoringOtherApps: true)
            let alert = NSAlert()
            alert.messageText = "QLC+ Vibra could not start"
            alert.informativeText = "\(error.localizedDescription)\nRun tools/qlc-launcher/install.py from the repository to repair the launcher."
            alert.alertStyle = .critical
            alert.runModal()
            exit(1)
        }
    }
}
