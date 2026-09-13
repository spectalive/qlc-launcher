"""Listener ownership is a post-launch check, never a port availability test."""

import subprocess


def listener_pids(port):
    """Return owners of TCP listeners on the selected port."""
    result = subprocess.run(
        ["/usr/sbin/lsof", "-nP", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"],
        capture_output=True, text=True, timeout=5,
    )
    if result.returncode not in (0, 1) or result.stderr.strip():
        raise RuntimeError("Cannot verify the web listener's process ownership.")
    return {int(value) for value in result.stdout.split()}
