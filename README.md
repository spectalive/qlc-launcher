# qlc-launcher

A macOS Dock app that opens one QLC+ show with its web interface on, and
proves the web server answered before it tells you so. Finder launches of
QLC+ omit the web flag, which leaves tablets and phones unable to reach the
show; this app starts QLC+ with `-w --wp PORT -o WORKSPACE`, checks the HTTP
response and the listener's owner, and posts `NAME on ADDRESS:PORT` as a
native notification.

It works with any QLC+ 5 workspace. It was written for the Vibra lighting
show ([Vibra-Lab/vibra-lighting](https://github.com/Vibra-Lab/vibra-lighting)),
which is the example below.

## Install

macOS 13 or newer, Python 3.11 or newer (for `tomllib`; Homebrew's is picked
first), and the Xcode command line tools (`swiftc`, `codesign`). No
administrator rights are needed.

```sh
git clone https://github.com/spectalive/qlc-launcher.git
python3 qlc-launcher/install.py --workspace "/path/to/Show.qxw"
```

| Flag | Default | Meaning |
| --- | --- | --- |
| `--workspace` | (required) | The `.qxw` QLC+ opens. |
| `--qlcplus` | `/Applications/QLC+ 5.2.2.app/Contents/MacOS/qlcplus-qml` | The QLC+ executable. Its app's `qlcplus.icns` becomes the launcher's icon. |
| `--name` | `QLC+ Vibra` | The app name. It also names the bundle id (`PREFIX<slug>`, so `com.busirocket.qlc-vibra` by default) and the state folder. |
| `--bundle-prefix` | `com.busirocket.` | The bundle id's reverse-DNS prefix, ending in a dot. The default keeps the Vibra mini's original id. |

Both paths are resolved through symlinks before they are checked and written
to the config, so the config and the bookmark name the real files.

The Vibra rig's Mac mini, for example:

```sh
python3 ~/p/qlc-launcher/install.py \
  --workspace ~/p/DMX-Fixtures-qlctool/"QLC+ Setups/Vibra.qxw" \
  --qlcplus "/Applications/QLC+ 5.2.2.app/Contents/MacOS/qlcplus-qml" \
  --name "QLC+ Vibra"
```

The installer builds and ad-hoc signs `~/Applications/NAME.app`; drag it from
Finder into the Dock. It refuses to overwrite an existing bundle: move the old
one aside first. Opening QLC+ itself still behaves as QLC+ always did. Several
shows can be installed side by side under different `--name`s.

## What the installer writes

Everything machine-specific lives in `~/Library/Application Support/NAME/`,
never in this repository:

| File | What it is |
| --- | --- |
| `launcher.toml` | `qlcplus` and `workspace`, both absolute paths. Edit it by hand or rerun the installer. |
| `Launcher.bookmark` | A Foundation bookmark to this checkout, where `launch.py` lives. |
| `Workspace.bookmark` | A bookmark to the workspace's **folder**. |
| `qlcplus.log`, `launch.lock` | QLC+'s output from the last launch, and the start lock. |

`launcher.toml` for the example above:

```toml
qlcplus = "/Applications/QLC+ 5.2.2.app/Contents/MacOS/qlcplus-qml"
workspace = "/Users/you/p/DMX-Fixtures-qlctool/QLC+ Setups/Vibra.qxw"
```

**Why bookmarks, and why the folder.** A bookmark follows its target when the
directory is moved or renamed on the same volume, so moving this checkout or
the show's checkout does not strand the Dock app; a stale bookmark is
rewritten on the next launch. The workspace's folder is bookmarked rather
than the `.qxw` itself because git checkouts and saves replace the file with
a new one, which a file bookmark cannot follow once the folder has also
moved; the folder keeps its identity through both
(`tests/check_bookmark_move.swift` checks exactly that). The app resolves the
folder and passes it to `launch.py` as `--workspace-folder`; the file name
comes from `launcher.toml`. Run by hand, `launch.py` uses the absolute path in
the config, and so does the app when `Workspace.bookmark` is missing, corrupt
or points at a folder that is gone: it no longer refuses to start, it drops
`--workspace-folder` (`tests/check_stale_workspace_bookmark.swift`). After a
copy to another volume `Launcher.bookmark` cannot resolve and the app stops
with a dialog: move the old app aside and install again.

## Startup contract

1. Read `launcher.toml`; require the QLC+ executable and the workspace.
2. Refuse a running `FwUpdateManagerd` or `com.pioneerdj.FwUpdateManagerd`
   executable. That Pioneer service can wedge QLC+'s libusb plugin scan.
   The launcher does not stop services or existing QLC+ processes.
3. Read the default IPv4 route, then ask `ipconfig getifaddr` for only that
   interface. Missing routes/addresses fail instead of showing another
   interface's stale address.
4. Serialize startup with a per-user `flock`. Bind and hold a dual-stack TCP
   socket on 9998, falling back to 9999 only on `EADDRINUSE`. No address/port
   reuse is enabled. If both are occupied, show an error and start nothing.
5. Release the reservation immediately before starting QLC+ with
   `-w --wp PORT -o WORKSPACE`. QLC+ cannot inherit a prebound listener, so an
   unrelated process can still win this short handoff. The launcher detects
   that by checking listener ownership and stops only its own new child.
   It never treats an existing QLC+ HTTP response as its own success.
6. Poll the loopback HTTP endpoint for status 200 and `QLC+` in the body,
   checking the child and listener PID, for 45 seconds (individual system
   inspections have five-second bounds). Startup failure stops and reaps
   only the child started by that invocation. If the OS prevents cleanup,
   the error identifies the remaining child PID instead of failing silently.
7. Issue a native notification: `NAME on ADDRESS:PORT`. The address is
   computed on this Mac; no venue address is embedded in source. Errors use
   a native dialog. Notification banners remain subject to macOS notification
   settings and Focus. Successful startup leaves QLC+ running after the
   launcher exits. This proves HTTP availability, not physical DMX operation.

The error dialog is issued without interpolating values into AppleScript:

```sh
/usr/bin/osascript -e 'on run argv
display dialog (item 1 of argv) with title (item 2 of argv) buttons {"OK"} default button "OK" with icon stop giving up after 60
end run' 'QLC+ Vibra could not start: ...' 'QLC+ Vibra'
```

**2026-09-26: the success banner posts from the app, not `osascript`.**
`display notification` attributes the banner to Script Editor, the process
that runs the `-e` script; on a Mac where Script Editor was never opened,
Notification Center has no entry for it and drops the banner silently while
`osascript` still returns 0. When LauncherApp launched `launch.py`, it sets
`QLC_LAUNCHER_NOTIFY_VIA_APP=1` in its environment; `notify.py` then prints
the success message on stdout behind the `QLC-LAUNCHER-NOTIFY:` prefix
instead of calling `osascript`. `child_output_relay.swift` reads that line
back out of the child's stdout pipe, and `success_notification.swift` posts
it through `UNUserNotificationCenter` under the launcher's own bundle id,
asking for alert authorization on the first launch. Run by hand from a
shell, `launch.py` has no such environment variable and keeps using
`osascript` for both the notification and the error dialog above.

The [QLC+ web-interface documentation](https://docs.qlcplus.org/v5/advanced/web-interface)
describes the web flags; the installed binary's `--help` is the checked
spelling authority. Apple's documentation describes
[bookmark resolution](https://developer.apple.com/documentation/foundation/url/init(resolvingbookmarkdata:options:relativeto:bookmarkdataisstale:)-3ic6f)
and [`UNUserNotificationCenter`](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter).

## Verification

From the checkout:

```sh
python3 -m unittest discover -s tests -v
swift tests/check_bookmark_move.swift
swiftc -parse-as-library workspace_arguments.swift resolve_bookmark.swift \
  tests/check_stale_workspace_bookmark.swift -o /tmp/check_stale_workspace_bookmark \
  && /tmp/check_stale_workspace_bookmark
python3 launch.py --name "QLC+ Vibra" --test-no-output
```

The last one needs an installed `launcher.toml` for that name. The test
option writes a temporary copy of the workspace without the engine I/O map or
startup function, starts the real QLC+, checks HTTP, emits the notification
with `(test: no hardware output)`, and stops its own child after 90 seconds.
Check `qlcplus.log` for workspace-load errors and unexpected output patches
before treating this as an isolated test. It never edits the real workspace;
the Dock app always opens the real one.

**2026-09-13 test regression:** QLC+ rejects XML without `<!DOCTYPE Workspace>`
and can restore its previous workspace with live I/O. ElementTree does not
preserve a doctype automatically. The verification-copy writer emits it
explicitly, and a regression test requires it. HTTP alone cannot establish
which workspace QLC+ loaded.

The Python tests cover real IPv4/IPv6 bind conflicts, port fallback, both ports
occupied, competing listener ownership, HTTP content/timeout/early exit, Pioneer
detection, default-route address selection, child-only cleanup, safe notification
arguments, an I/O-free temporary workspace with its required doctype, and the
config: round trip with awkward paths, missing or invalid files, relative
paths, the bundle id derived from the name and prefix, the state folder and
workspace folder the app passes in, and the installer's refusal to touch an
existing bundle.

A tablet finder run is a separate integration check. When another show is
live, verify its existing connection before and after, and confirm no test
child remains. A shell `open` invocation can exercise LaunchServices, but does
not prove a human Dock click or that a notification banner was visibly
presented.

## Licence

Apache-2.0, see [LICENSE](LICENSE).
