import Foundation

// 2026-09-13: moving a worktree must not strand its installed Dock launcher.
// 2026-09-26: the workspace is reached through its folder's bookmark, because
// git and QLC+ replace the .qxw file itself; the folder must still resolve.
let root = FileManager.default.temporaryDirectory
    .appendingPathComponent("qlc-bookmark-test-\(UUID().uuidString)")
try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
defer { try? FileManager.default.removeItem(at: root) }
let original = root.appendingPathComponent("original")
let moved = root.appendingPathComponent("moved")
try FileManager.default.createDirectory(at: original, withIntermediateDirectories: true)
let show = original.appendingPathComponent("Show.qxw")
try Data("first".utf8).write(to: show)
let bookmark = try original.bookmarkData()
try Data("second".utf8).write(to: show, options: .atomic)
try FileManager.default.moveItem(at: original, to: moved)
var stale = false
let resolved = try URL(
    resolvingBookmarkData: bookmark, options: [.withoutUI, .withoutMounting],
    relativeTo: nil, bookmarkDataIsStale: &stale
)
precondition(resolved.resolvingSymlinksInPath() == moved.resolvingSymlinksInPath())
let content = try String(contentsOf: resolved.appendingPathComponent("Show.qxw"), encoding: .utf8)
precondition(content == "second")
print("PASS: a folder bookmark follows a move after its workspace file was replaced.")
