import Foundation

/// The `--workspace-folder` arguments for `launch.py`, or none when the folder bookmark is absent or no longer
/// resolves; `launch.py` then opens the absolute `workspace` path from `launcher.toml`.
func workspaceArguments(bookmark: URL) -> [String] {
    guard FileManager.default.fileExists(atPath: bookmark.path) else {
        return []
    }
    do {
        return ["--workspace-folder", try resolveBookmark(at: bookmark).path]
    } catch {
        FileHandle.standardError.write(Data(
            "Workspace bookmark \(bookmark.path) did not resolve (\(error.localizedDescription)); using launcher.toml's workspace.\n".utf8
        ))
        return []
    }
}
