import Foundation

/// Resolve a stored bookmark, rewriting it when the target has moved.
func resolveBookmark(at bookmark: URL) throws -> URL {
    let data = try Data(contentsOf: bookmark)
    var stale = false
    let target = try URL(
        resolvingBookmarkData: data, options: [.withoutUI, .withoutMounting],
        relativeTo: nil, bookmarkDataIsStale: &stale
    )
    if stale {
        try target.bookmarkData().write(to: bookmark, options: .atomic)
    }
    return target
}
