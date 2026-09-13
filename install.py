#!/usr/bin/env python3
"""Build and install QLC+ Vibra.app without administrator privileges."""

from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile


def main():
    """Build a new bundle; refuse to overwrite an existing installation."""
    source = Path(__file__).resolve().parent
    repository = source.parents[1]
    applications = Path.home() / "Applications"
    destination = applications / "QLC+ Vibra.app"
    if destination.exists():
        raise SystemExit(f"Already installed: {destination}. Preserve or move that bundle before reinstalling.")
    python = next((path for path in (Path("/opt/homebrew/bin/python3"), Path("/usr/local/bin/python3"), Path("/usr/bin/python3")) if path.is_file()), None)
    if python is None:
        raise SystemExit("Python 3 is missing. Install Python 3 before installing the launcher.")
    state = Path.home() / "Library" / "Application Support" / "QLC+ Vibra"
    state.mkdir(parents=True, exist_ok=True)
    applications.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="qlc-vibra-build-") as temporary:
        bundle = Path(temporary) / destination.name
        contents = bundle / "Contents"
        executable = contents / "MacOS" / "QLC+ Vibra"
        resources = contents / "Resources"
        executable.parent.mkdir(parents=True)
        resources.mkdir()
        icon = Path("/Applications/QLC+ 5.2.2.app/Contents/Resources/qlcplus.icns")
        if icon.is_file():
            shutil.copyfile(icon, resources / "qlcplus.icns")
        subprocess.run(["/usr/bin/swiftc", "-parse-as-library", str(source / "LauncherApp.swift"), "-o", str(executable)], check=True)
        (resources / "PythonPath").write_text(str(python) + "\n")
        with (contents / "Info.plist").open("wb") as output:
            plistlib.dump({
                "CFBundleExecutable": "QLC+ Vibra",
                "CFBundleIdentifier": "com.busirocket.qlc-vibra",
                "CFBundleName": "QLC+ Vibra",
                "CFBundleDisplayName": "QLC+ Vibra",
                "CFBundleIconFile": "qlcplus.icns" if icon.is_file() else "",
                "CFBundlePackageType": "APPL",
                "CFBundleVersion": "1",
                "CFBundleShortVersionString": "1.0",
                "LSMinimumSystemVersion": "13.0",
                "NSHighResolutionCapable": True,
            }, output)
        subprocess.run(["/usr/bin/codesign", "--force", "--sign", "-", str(bundle)], check=True)
        subprocess.run(["/usr/bin/swift", str(source / "create_bookmark.swift"), str(repository), str(state / "Repository.bookmark")], check=True)
        shutil.copytree(bundle, destination)
    print(f"Installed {destination}. Drag it from Finder into the Dock.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
