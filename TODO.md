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
- [ ] **A stale `Workspace.bookmark` stops the Dock app outright (review,
  2026-09-26).** `LauncherApp.swift` fails when the workspace-folder bookmark
  does not resolve, although `launcher.toml` still holds the absolute
  `workspace` path that `launch.py` falls back to without
  `--workspace-folder`. Smallest next step: on a bookmark error, call
  `launch.py` without `--workspace-folder` and let it use the config path;
  reinstall on the mini and rerun `--test-no-output`.
- [ ] **The installer's refusal to overwrite has no test (review,
  2026-09-26).** Only a manual run checked that an existing bundle is left
  alone. Smallest next step: a unit test with a temporary `Applications`
  folder holding a bundle, asserting `SystemExit` and an untouched bundle.
- [ ] **`--workspace` is `.resolve()`d, `--qlcplus` only `.absolute()`
  (review, 2026-09-26).** Symlinks are treated differently; not a bug today.
  Smallest next step: pick one and apply it to both.
- [ ] **The bundle id prefix `com.busirocket.` is fixed (2026-09-26).** Kept
  so the Vibra mini keeps its id. Smallest next step: a `--bundle-prefix`
  flag defaulting to today's value.
