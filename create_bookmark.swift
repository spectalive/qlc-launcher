import Foundation

// Install a file-identity bookmark, not a hardcoded path in the Dock app.
let target = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let destination = URL(fileURLWithPath: CommandLine.arguments[2])
try target.bookmarkData().write(to: destination, options: .atomic)
