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
- [ ] **A human Dock click and a visible notification banner have never been
  observed (2026-09-13).** Every verification ran `launch.py` or `open` from a
  shell. Smallest next step: click the Dock icon at the rig and note the
  banner.
- [ ] **`install.py` died twice with exit 144 and no traceback (2026-09-26).**
  On the Mac mini, run from an agent's shell, the installer stopped after
  `codesign` and `Launcher.bookmark`, before `Workspace.bookmark` (the second
  interpreted `swift create_bookmark.swift`); the third identical run
  succeeded, and the same step run alone always did. Nothing is left
  half-installed (the bundle is copied last), but a rerun is needed.
  Smallest next step: compile `create_bookmark.swift` once with `swiftc`
  into the build directory and call the binary, then see whether it recurs.
