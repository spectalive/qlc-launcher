# QLC+ Vibra Dock launcher

Install from this checkout on macOS with Python 3 and the Xcode command line
tools available:

```sh
python3 tools/qlc-launcher/install.py
```

The installer builds and locally signs `~/Applications/QLC+ Vibra.app`.
This location needs no administrator privileges. Drag that app from Finder
into the Dock and use it to open the show. Opening the original QLC+ app
still uses QLC+'s original startup behavior.

The native Swift bundle calls `tools/qlc-launcher/launch.py` in this repository.
The Python launcher uses only the standard library. A Foundation bookmark in
`~/Library/Application Support/QLC+ Vibra/Repository.bookmark` follows the
repository when its directory moves. The script resolves `QLC+ Setups/Vibra.qxw`
relative to itself. Deleted files fail with a native error; if the bookmark
cannot resolve after a copy to another volume, preserve/move the old app bundle
and run the installer from the new checkout. The installer refuses to overwrite
an existing bundle. Generated bundles, bookmarks, machine paths, and runtime
logs stay outside this public repository.

## Startup contract

1. Require `/Applications/QLC+ 5.2.2.app/Contents/MacOS/qlcplus-qml` and the
   repository's `Vibra.qxw`.
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
7. Issue a native notification: `QLC+ Vibra on ADDRESS:PORT`. The address is
   computed on this Mac; no venue address is embedded in source. Errors use
   a native dialog. Notification banners remain subject to macOS notification
   settings and Focus. Successful startup leaves QLC+ running after the
   launcher exits. This proves HTTP availability, not physical DMX operation.

The launcher writes QLC+ output to
`~/Library/Application Support/QLC+ Vibra/qlcplus.log`.

The notification is issued without interpolating values into AppleScript:

```sh
/usr/bin/osascript -e 'on run argv
display notification (item 1 of argv) with title "QLC+ Vibra"
end run' 'QLC+ Vibra on ADDRESS:PORT'
```

The [QLC+ web-interface documentation](https://docs.qlcplus.org/v5/advanced/web-interface)
describes the web flags; the installed 5.2.2 binary's `--help` is the checked
spelling authority. Apple's documentation describes
[bookmark resolution](https://developer.apple.com/documentation/foundation/url/init(resolvingbookmarkdata:options:relativeto:bookmarkdataisstale:)-3ic6f)
and [native notifications](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/DisplayNotifications.html).

## Verification

```sh
python3 -m unittest discover -s tools/qlc-launcher/tests -v
swift tools/qlc-launcher/tests/check_bookmark_move.swift
python3 tools/qlc-launcher/launch.py --test-no-output
```

The explicit test option creates a temporary copy of Vibra without the engine
I/O map or startup function. It starts the real GUI binary, checks HTTP, emits
the notification with `(test: no hardware output)`, and stops its own child
after 90 seconds. Check QLC+'s log for workspace-load errors and unexpected
output patches before treating this as an isolated test. Never edit the live
generated workspace to perform this check. The normal Dock app always opens
the real repository workspace.

**2026-09-13 test regression:** QLC+ rejects XML without `<!DOCTYPE Workspace>`
and can restore its previous workspace with live I/O. ElementTree does not
preserve a doctype automatically. The verification-copy writer now emits it
explicitly, and the regression test requires it. HTTP alone cannot establish
which workspace QLC+ loaded.

The Python tests cover real IPv4/IPv6 bind conflicts, port fallback, both ports
occupied, competing listener ownership, HTTP content/timeout/early exit, Pioneer
detection, default-route address selection, child-only cleanup, safe notification
arguments, and an I/O-free temporary workspace with its required doctype.
The Swift test moves a disposable directory and resolves its original bookmark.

A tablet finder run is a separate integration check. Use the tablet's existing
access procedure from private notes; keep literal addresses and access details
out of this repository. When another show is live, verify its existing connection
before and after, and confirm no test child remains. A shell `open` invocation
can exercise LaunchServices, but does not prove a human Dock click or that a
notification banner was visibly presented.

Verified on 2026-09-13 with QLC+ 5.2.2: 20 launcher tests and the bookmark-move
test passed. The corrected temporary show rendered, served QLC+ HTTP on 9999,
and logged only `None` output patches. The tablet finder listed both it and
the original server on 9998. After cleanup, only the original listener remained
and the tablet reported its link up. The notification command completed;
a human Dock click and visible notification banner were not observed.
The existing qlctool suite passed with 440 passed and 9 skipped in 29m48s;
the semantic check reviewed 580 buttons without problems.
