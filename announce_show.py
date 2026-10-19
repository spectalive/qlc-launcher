"""Start the Bonjour announce beside QLC+, detached so it outlives launch.py."""

from pathlib import Path
import subprocess
import sys


def announce_show(name, port, pid, log):
    """Hand the announce to its own session; its output must not hold LauncherApp's stdout pipe open."""
    return subprocess.Popen(
        [sys.executable, str(Path(__file__).with_name("announce_until_exit.py")),
         "--name", name, "--port", str(port), "--pid", str(pid)],
        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
    )
