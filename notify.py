"""Native launcher messages with no shell or AppleScript interpolation."""

import os
import subprocess

# 2026-09-26: `display notification` posts as Script Editor, which has no entry in
# com.apple.ncprefs on the Vibra mini, so macOS drops the banner while osascript still
# returns 0. LauncherApp.swift sets this environment variable on launch.py's child
# process and reads this line prefix from its stdout, then posts the banner itself
# through UNUserNotificationCenter under its own bundle id. A shell run has neither, and
# keeps using osascript.
APP_NOTIFICATION_ENV = "QLC_LAUNCHER_NOTIFY_VIA_APP"
APP_NOTIFICATION_PREFIX = "QLC-LAUNCHER-NOTIFY:"


def notify(message, error=False, title="QLC+ Vibra"):
    """Print the result and deliver it to macOS; errors use a visible dialog."""
    print(message, flush=True)
    if not error and os.environ.get(APP_NOTIFICATION_ENV):
        print(f"{APP_NOTIFICATION_PREFIX}{message}", flush=True)
        return
    action = (
        'display dialog (item 1 of argv) with title (item 2 of argv) '
        'buttons {"OK"} default button "OK" with icon stop giving up after 60'
        if error else
        'display notification (item 1 of argv) with title (item 2 of argv)'
    )
    subprocess.run(
        ["/usr/bin/osascript", "-e", f"on run argv\n{action}\nend run", message, title],
        check=True, timeout=65,
    )
