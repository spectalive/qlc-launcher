import Foundation
import UserNotifications

/// Requests alert authorization once and posts a local notification under this app's own bundle id, so
/// Notification Center attributes and delivers the banner instead of dropping an unregistered Script
/// Editor notification. Blocks the calling thread, pumping its run loop so the completion handlers below
/// can run, for up to `timeout` seconds per step; called after `waitUntilExit()` so nothing else needs it.
func postSuccessNotification(title: String, body: String, authorizationTimeout: TimeInterval = 30, timeout: TimeInterval = 8) {
    let center = UNUserNotificationCenter.current()
    var authorized = false
    var authorizationDone = false
    center.requestAuthorization(options: [.alert]) { granted, error in
        authorized = granted
        if let error {
            FileHandle.standardError.write(Data("Notification authorization failed: \(error.localizedDescription)\n".utf8))
        }
        authorizationDone = true
    }
    // Only the first launch after install prompts a person to click Allow; every later launch returns the
    // stored answer immediately. Give that first click room, since QLC+'s own startup already takes a while.
    waitWhilePumpingRunLoop(timeout: authorizationTimeout) { authorizationDone }
    guard authorized else {
        FileHandle.standardError.write(Data("Notifications are not authorized; the ready banner was not posted.\n".utf8))
        return
    }
    let content = UNMutableNotificationContent()
    content.title = title
    content.body = body
    let request = UNNotificationRequest(identifier: "qlc-launcher-ready-\(UUID().uuidString)", content: content, trigger: nil)
    var postDone = false
    center.add(request) { error in
        if let error {
            FileHandle.standardError.write(Data("Posting the ready notification failed: \(error.localizedDescription)\n".utf8))
        }
        postDone = true
    }
    waitWhilePumpingRunLoop(timeout: timeout) { postDone }
}

/// Spin the calling thread's run loop instead of blocking outright, in case the completion handlers above
/// are dispatched back onto it.
private func waitWhilePumpingRunLoop(timeout: TimeInterval, until isDone: () -> Bool) {
    let deadline = Date().addingTimeInterval(timeout)
    while !isDone() && Date() < deadline {
        RunLoop.current.run(mode: .default, before: min(deadline, Date().addingTimeInterval(0.05)))
    }
}
