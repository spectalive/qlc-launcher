"""Pick the Python the Dock app runs the launcher with."""

from pathlib import Path
import subprocess

CANDIDATES = (Path("/opt/homebrew/bin/python3"), Path("/usr/local/bin/python3"), Path("/usr/bin/python3"))


def find_python(candidates=CANDIDATES):
    """Return the first Python 3.11 or newer, which ships tomllib."""
    for path in candidates:
        if path.is_file() and subprocess.run(
            [str(path), "-c", "import tomllib"], capture_output=True, timeout=30,
        ).returncode == 0:
            return path
    raise SystemExit("Python 3.11 or newer is missing. Install it (for example with Homebrew) before installing the launcher.")
