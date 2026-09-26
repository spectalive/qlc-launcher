# TODO Log

Closed work from [TODO.md](TODO.md), newest month first. Every entry carries
the evidence that closed it.

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
