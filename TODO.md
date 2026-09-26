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
- [ ] **The success banner is never shown on the Mac mini (2026-09-26).**
  `open ~/Applications/QLC+ Vibra.app` (LaunchServices, the Dock's path)
  started QLC+ on 9998 with the show, but six screen captures over 9 s show no
  banner. Calling `notify()` directly returned 0 and showed nothing either,
  with no Focus mode active. `display notification` from `osascript` posts as
  Script Editor, which has no entry in `com.apple.ncprefs` there; only
  `terminal-notifier` does. So the notification is dropped silently while
  the call reports success. Smallest next step: post it from the Swift app
  through `UNUserNotificationCenter` under the launcher's own bundle, which
  asks for permission once, and check the banner on the mini.
