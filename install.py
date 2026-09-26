#!/usr/bin/env python3
"""Build and install a QLC+ Dock launcher for one show, without administrator privileges."""

import argparse
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile

from bundle_identifier import bundle_identifier
from default_bundle_prefix import DEFAULT_PREFIX
from find_python import find_python
from write_config import write_config


def main():
    """Build a new bundle; refuse to overwrite an existing installation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path,
                        help="The .qxw show QLC+ opens, e.g. '~/p/DMX-Fixtures/QLC+ Setups/Vibra.qxw'.")
    parser.add_argument("--qlcplus", type=Path,
                        default=Path("/Applications/QLC+ 5.2.2.app/Contents/MacOS/qlcplus-qml"),
                        help="The QLC+ executable inside its app bundle (default: %(default)s).")
    parser.add_argument("--name", default="QLC+ Vibra",
                        help="App name; also names the bundle id and the state folder (default: %(default)s).")
    parser.add_argument("--bundle-prefix", default=DEFAULT_PREFIX,
                        help="Reverse-DNS prefix of the bundle id, ending in a dot (default: %(default)s).")
    args = parser.parse_args()
    # Both are resolved: the config and the bookmark then name the real file, not a symlink to it.
    workspace = args.workspace.expanduser().resolve()
    qlcplus = args.qlcplus.expanduser().resolve()
    identifier = bundle_identifier(args.name, args.bundle_prefix)
    if not workspace.is_file():
        raise SystemExit(f"Workspace not found: {workspace}")
    if not qlcplus.is_file() or not os.access(qlcplus, os.X_OK):
        raise SystemExit(f"QLC+ executable not found or not executable: {qlcplus}")
    source = Path(__file__).resolve().parent
    applications = Path.home() / "Applications"
    destination = applications / f"{args.name}.app"
    if destination.exists():
        raise SystemExit(f"Already installed: {destination}. Preserve or move that bundle before reinstalling.")
    python = find_python()
    state = Path.home() / "Library" / "Application Support" / args.name
    state.mkdir(parents=True, exist_ok=True)
    applications.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="qlc-launcher-build-") as temporary:
        bundle = Path(temporary) / destination.name
        contents = bundle / "Contents"
        executable = contents / "MacOS" / args.name
        resources = contents / "Resources"
        executable.parent.mkdir(parents=True)
        resources.mkdir()
        icon = qlcplus.parents[1] / "Resources" / "qlcplus.icns"
        if icon.is_file():
            shutil.copyfile(icon, resources / "qlcplus.icns")
        subprocess.run(["/usr/bin/swiftc", "-parse-as-library", str(source / "LauncherApp.swift"),
                        str(source / "resolve_bookmark.swift"), str(source / "workspace_arguments.swift"),
                        str(source / "notification_handoff.swift"), str(source / "child_output_relay.swift"),
                        str(source / "success_notification.swift"),
                        "-o", str(executable)], check=True)
        # Compiled once rather than interpreted per bookmark: the interpreted run died twice with exit 144.
        create_bookmark = Path(temporary) / "create_bookmark"
        subprocess.run(["/usr/bin/swiftc", str(source / "create_bookmark.swift"), "-o", str(create_bookmark)], check=True)
        (resources / "PythonPath").write_text(str(python) + "\n")
        with (contents / "Info.plist").open("wb") as output:
            plistlib.dump({
                "CFBundleExecutable": args.name,
                "CFBundleIdentifier": identifier,
                "CFBundleName": args.name,
                "CFBundleDisplayName": args.name,
                "CFBundleIconFile": "qlcplus.icns" if icon.is_file() else "",
                "CFBundlePackageType": "APPL",
                "CFBundleVersion": "1",
                "CFBundleShortVersionString": "1.0",
                "LSMinimumSystemVersion": "13.0",
                "NSHighResolutionCapable": True,
            }, output)
        subprocess.run(["/usr/bin/codesign", "--force", "--sign", "-", str(bundle)], check=True)
        write_config(state / "launcher.toml", qlcplus, workspace)
        for target, bookmark in ((source, "Launcher.bookmark"), (workspace.parent, "Workspace.bookmark")):
            subprocess.run([str(create_bookmark), str(target), str(state / bookmark)], check=True)
        shutil.copytree(bundle, destination)
    print(f"Installed {destination} for {workspace}. Drag it from Finder into the Dock.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
