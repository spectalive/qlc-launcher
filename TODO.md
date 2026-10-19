# TODO

> Consolidated from the accessible agent conversation history of this project.
> Last reviewed: 2026-10-12. History coverage: Partial. Not re-audited during the
> 2026-10-12 format migration.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.

- [~] **Clients find the show by themselves (from Vibra-Lab/vibra-lighting,
  2026-09-26).** Announce the running show over mDNS/Bonjour, and show a QR
  code with `http://ADDRESS:PORT/`, so a tablet or phone reaches it without
  typing an address.
  2026-10-19: the announce is done. After the HTTP check `launch.py` starts
  `announce_until_exit.py` detached, which keeps `dns-sd -R NAME _http._tcp
  local PORT` alive until that QLC+ PID exits. Verified on the Mac mini with
  a scratch `--test-no-output` launch on 9999 (9998 held by a dummy
  listener): `dns-sd -B _http._tcp local` showed `Add ... QLC+ Announce
  Test` at the HTTP check and `Rmv` when the test QLC+ stopped 90 s later,
  with no `dns-sd` left; `dns-sd -L` resolved it to `Mac-mini-...local.:9997`
  in a detached run. Python only, so the installed app picks it up on its
  next launch with no reinstall. Smallest next step: the QR code with
  `http://ADDRESS:PORT/`.
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
