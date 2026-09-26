# TODO

- [ ] **Clients find the show by themselves (from Vibra-Lab/vibra-lighting,
  2026-09-26).** Announce the running show over mDNS/Bonjour, and show a QR
  code with `http://ADDRESS:PORT/`, so a tablet or phone reaches it without
  typing an address. Smallest next step: register `_http._tcp` with
  `dns-sd -R` (or `NSNetService`) for the verified port once the HTTP check
  passes, and stop it with the child.
- [ ] **Choose the show at launch (from vibra-lighting, 2026-09-26).** Today a
  show is chosen at install time (`--workspace`, one app per `--name`).
  Smallest next step: decide whether a picker at launch is still wanted now
  that several named apps can be installed side by side.
- [~] **The success banner is never shown on the Mac mini (2026-09-26).**
  `open ~/Applications/QLC+ Vibra.app` (LaunchServices, the Dock's path)
  started QLC+ on 9998 with the show, but six screen captures over 9 s show no
  banner. Calling `notify()` directly returned 0 and showed nothing either,
  with no Focus mode active. `display notification` from `osascript` posts as
  Script Editor, which has no entry in `com.apple.ncprefs` there; only
  `terminal-notifier` does. So the notification is dropped silently while
  the call reports success.
  2026-09-26: fixed in code and half-verified. LauncherApp now hands the
  success message to `launch.py`'s child via `QLC_LAUNCHER_NOTIFY_VIA_APP`
  and a `QLC-LAUNCHER-NOTIFY:` stdout line (`notify.py`,
  `child_output_relay.swift`), and posts it itself through
  `UNUserNotificationCenter` (`success_notification.swift`). Built the
  binary ad-hoc signed into a throwaway `.app` (own bundle id, outside
  `~/Applications`) and ran it: Notification Center presented the real
  authorization banner attributed to that bundle's own name, not Script
  Editor (`log show --predicate 'process == "usernoted"'` shows `Sending
  request for permission for com.busirocket.qlc-notify-harness-test3` and
  `Presenting ... as alert`; screencapture confirms it on screen). Three
  throwaway bundle ids all timed out undecided (nobody clicked Allow in the
  harness's window, and clicking blind near the live show's window risked
  it, so testing stopped there) — the actual green ready banner was not
  observed. Smallest next step: reinstall the real app (`install.py`, same
  `--name`) and click Allow on the first real launch; then confirm the
  banner over the Mac mini's own Wi-Fi-only lock screen next show night.
