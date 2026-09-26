import Foundation

// 2026-09-26 review: a Workspace.bookmark that no longer resolves stopped the Dock app outright, although
// launcher.toml still held the absolute workspace path. Build with the app's own sources:
//   swiftc -parse-as-library workspace_arguments.swift resolve_bookmark.swift \
//     tests/check_stale_workspace_bookmark.swift -o /tmp/check_stale_workspace_bookmark
@main
struct CheckStaleWorkspaceBookmark {
    static func main() throws {
        let root = FileManager.default.temporaryDirectory
            .appendingPathComponent("qlc-stale-bookmark-test-\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: root) }
        let folder = root.appendingPathComponent("QLC+ Setups")
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        let bookmark = root.appendingPathComponent("Workspace.bookmark")

        precondition(workspaceArguments(bookmark: bookmark) == [], "a missing bookmark must add no arguments")

        try folder.bookmarkData().write(to: bookmark, options: .atomic)
        let resolved = workspaceArguments(bookmark: bookmark)
        precondition(resolved.count == 2 && resolved[0] == "--workspace-folder")
        precondition(URL(fileURLWithPath: resolved[1]).resolvingSymlinksInPath() == folder.resolvingSymlinksInPath())

        try Data("not a bookmark".utf8).write(to: bookmark, options: .atomic)
        precondition(workspaceArguments(bookmark: bookmark) == [], "a corrupt bookmark must fall back to the config")

        try folder.bookmarkData().write(to: bookmark, options: .atomic)
        try FileManager.default.removeItem(at: folder)
        precondition(workspaceArguments(bookmark: bookmark) == [], "a bookmark to a deleted folder must fall back")
        print("PASS: a missing, corrupt or dangling workspace bookmark falls back to launcher.toml's workspace.")
    }
}
