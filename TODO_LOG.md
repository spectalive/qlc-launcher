# TODO Log

Closed work from [TODO.md](TODO.md), newest month first. Every entry carries
the evidence that closed it.

<!-- tadu:log v1 since 2026-10-12 -->

## 2026

### 2026-09

#### 2026-09-26 - The review's follow-ups, and a reinstall on the Vibra Mac mini

- [x] 2026-09-26 - **A stale `Workspace.bookmark` no longer stops the Dock
  app.** `workspace_arguments.swift` drops `--workspace-folder` when the
  bookmark is missing, corrupt or points at a deleted folder, so `launch.py`
  opens `launcher.toml`'s absolute `workspace` (`e139596`). Evidence:
  `tests/check_stale_workspace_bookmark.swift` passes all four cases; and the
  installed app, copied under a throwaway name with a state folder whose
  `Workspace.bookmark` held garbage and a stub Python that added
  `--test-no-output`, logged the fallback, called `launch.py --name ...`
  with no `--workspace-folder`, passed the HTTP check on QLC+ PID 61606 and
  stopped it (app exit 0).
- [x] 2026-09-26 - **The installer's refusal to overwrite has a test.**
  `tests/test_install.py`: a temporary home with an existing bundle raises
  `Already installed`, leaves the bundle byte-for-byte, runs no build step
  and creates no state folder; with the refusal disabled the test fails.
- [x] 2026-09-26 - **`--workspace` and `--qlcplus` are both `.resolve()`d.**
  Picked resolve so the config and the bookmark name the real files; the
  mini's config came out identical to the one before.
- [x] 2026-09-26 - **`--bundle-prefix`, default `com.busirocket.`.**
  Validated as reverse-DNS labels ending in a dot; the reinstalled mini keeps
  `com.busirocket.qlc-vibra`. Tests in `tests/test_config.py`.
- [x] 2026-09-26 - **`install.py` exit 144: `create_bookmark.swift` is
  compiled once with `swiftc` and the binary is called per bookmark.** The
  reinstall on the mini ran clean in one pass (exit 0). One run cannot prove
  the interpreted-`swift` death is gone; reopen if an install stops again.
- Reinstall on the mini, 2026-09-26: the previous bundle and its
  `launcher.toml` and bookmarks are kept in
  `~/Library/Application Support/QLC+ Vibra/pre-e-launcher/`; reinstalled
  with the same name, workspace
  (`~/p/DMX-Fixtures-qlctool/QLC+ Setups/Vibra.qxw`) and QLC+ 5.2.2 binary;
  `launch.py --name "QLC+ Vibra" --test-no-output` passed the HTTP check on
  its own QLC+ PID 54431 (port 9998) and stopped it. No other QLC+ was
  running before or after.

### 2026-10

- [x] 2026-10-21 — **Launch:** Skip live pytest workspace copies in QLC+'s recent list.
  - Result: A concurrent Art-Net test put its temporary `live.qxw` first, and the launcher briefly opened it for the desk. The recent-file selector now skips `pytest-of-*` paths while retaining real recent shows.
  - Evidence: `python3 -m unittest discover -s tests -q` passed 44 tests, including the new regression; the live master was restarted with the shipped Vibra workspace.

- [x] 2026-10-19 — **General:** **The installed app's Python is gone on the Mac mini (2026-10-19).**
  `~/Applications/QLC+ Vibra.app/Contents/Resources/PythonPath` names
  `/opt/homebrew/bin/python3`, which no longer exists (Homebrew now links
  only `python3.13` and `python3.14` there; `python3.14`'s link is dated
  2026-10-11), so the Dock app's `Process.run()` has no interpreter to start
  `launch.py` with (not exercised: the live app was not launched). `find_python.py` only tries unversioned
  `python3` names. Smallest next step: owner decides between `brew link
  python@3.14` (restores the path, no reinstall) or teaching `find_python.py`
  versioned names and reinstalling the app.
  - Result: The Dock app starts again; Homebrew's versioned-only python@3.14 is found.
  - Evidence: find_python tries versioned Homebrew names; 38 unittest OK under python3.14; app reinstalled on the mini 2026-10-19 (old bundle kept as QLC+ Vibra.pre-python-fix-2026-10-19.app), PythonPath=/opt/homebrew/bin/python3.14; open launched qlcplus-qml on 9998 (HTTP 200 in 8 s) and dns-sd -B listed QLC+ Vibra _http._tcp

- [x] 2026-10-19 — **General:** **Choose the show at launch (from vibra-lighting, 2026-09-26).** Today a
  show is chosen at install time (`--workspace`, one app per `--name`).
  Smallest next step: decide whether a picker at launch is still wanted now
  that several named apps can be installed side by side.
  - Result: No picker: launch.py opens the newest existing workspace in QLC+'s own recent list (last_qlcplus_workspace.py, read_qlcplus_preferences.py), skipping qlctool's validation copies; the installed workspace is the fallback. Owner 2026-10-19: "lo suyo es que se sincronice con lo que tiene QLC no que tenga que abrir nada".
  - Evidence: python3.14 -m unittest discover -s tests: 43 OK (5 new in tests/test_last_workspace.py); live launch.py --test-no-output on the mini picked QLC+ Setups/Vibra.qxw past a deleted temp recent0, HTTP check passed on 9999 and stopped.
