"""Detect the Pioneer service that wedges the QLC+ libusb scan."""

import subprocess
from pathlib import Path


def pioneer_guard():
    """Inspect executable names, avoiding matches in shell command arguments."""
    processes = subprocess.run(
        ["/bin/ps", "-axo", "pid=,comm="],
        capture_output=True, text=True, check=True, timeout=5,
    ).stdout
    for line in processes.splitlines():
        fields = line.strip().split(None, 1)
        if len(fields) != 2:
            continue
        name = Path(fields[1]).name
        if name in {"FwUpdateManagerd", "com.pioneerdj.FwUpdateManagerd"}:
            raise RuntimeError(
                f"Pioneer com.pioneerdj.FwUpdateManagerd is running (PID {fields[0]}). "
                "It can hang QLC+ during the DMX USB scan. Stop the Pioneer service "
                "before trying again. QLC+ was not started."
            )
