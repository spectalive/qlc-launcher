import Foundation

// 2026-09-13: moving a worktree must not strand its installed Dock launcher.
let root = FileManager.default.temporaryDirectory
    .appendingPathComponent("qlc-bookmark-test-\(UUID().uuidString)")
try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
defer { try? FileManager.default.removeItem(at: root) }
let original = root.appendingPathComponent("original")
let moved = root.appendingPathComponent("moved")
try FileManager.default.createDirectory(at: original, withIntermediateDirectories: true)
let bookmark = try original.bookmarkData()
try FileManager.default.moveItem(at: original, to: moved)
var stale = false
let resolved = try URL(
    resolvingBookmarkData: bookmark, options: [.withoutUI, .withoutMounting],
    relativeTo: nil, bookmarkDataIsStale: &stale
)
precondition(resolved.resolvingSymlinksInPath() == moved.resolvingSymlinksInPath())
print("PASS: repository bookmark follows a directory move.")
