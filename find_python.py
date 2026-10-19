"""Pick the Python the Dock app runs the launcher with."""

from pathlib import Path
import subprocess

# Homebrew's newer python@3.x formulae link only the versioned name, so an
# unversioned python3 may be missing while python3.14 sits next to it.
CANDIDATES = tuple(
    Path(prefix) / name
    for prefix in ("/opt/homebrew/bin", "/usr/local/bin")
    for name in ("python3", "python3.14", "python3.13", "python3.12", "python3.11")
) + (Path("/usr/bin/python3"),)


def find_python(candidates=CANDIDATES):
    """Return the first Python 3.11 or newer, which ships tomllib."""
    for path in candidates:
        if path.is_file() and subprocess.run(
            [str(path), "-c", "import tomllib"], capture_output=True, timeout=30,
        ).returncode == 0:
            return path
    raise SystemExit("Python 3.11 or newer is missing. Install it (for example with Homebrew) before installing the launcher.")
