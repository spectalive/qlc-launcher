import Foundation

/// The wire protocol between LauncherApp and `launch.py`'s `notify()` (notify.py), so the success banner is
/// posted from this app's own bundle instead of `osascript`'s `display notification`, which macOS drops
/// silently when Script Editor has no entry in Notification Center. Mirrored in notify.py.
let notificationHandoffEnvironmentVariable = "QLC_LAUNCHER_NOTIFY_VIA_APP"
let notificationHandoffLinePrefix = "QLC-LAUNCHER-NOTIFY:"
