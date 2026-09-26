import Foundation

/// Forwards `launch.py`'s stdout line by line as it arrives, and pulls out the one line carrying the
/// success message so LauncherApp can post it itself instead of relying on `launch.py`'s `osascript` call.
final class ChildOutputRelay {
    private let pipe: Pipe
    private var buffer = Data()
    private(set) var notificationMessage: String?

    init(pipe: Pipe) {
        self.pipe = pipe
        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            self?.consume(handle.availableData)
        }
    }

    /// Read whatever is left once the child has exited; a fast exit can outrun the readability handler.
    func drain() {
        pipe.fileHandleForReading.readabilityHandler = nil
        consume(pipe.fileHandleForReading.readDataToEndOfFile())
    }

    private func consume(_ data: Data) {
        guard !data.isEmpty else { return }
        buffer.append(data)
        while let newline = buffer.firstIndex(of: 0x0A) {
            handle(buffer.subdata(in: buffer.startIndex..<newline))
            buffer.removeSubrange(buffer.startIndex...newline)
        }
    }

    private func handle(_ lineData: Data) {
        guard let line = String(data: lineData, encoding: .utf8) else { return }
        if line.hasPrefix(notificationHandoffLinePrefix) {
            notificationMessage = String(line.dropFirst(notificationHandoffLinePrefix.count))
        } else {
            FileHandle.standardOutput.write(lineData + Data([0x0A]))
        }
    }
}
