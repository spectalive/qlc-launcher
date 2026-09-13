"""Native launcher messages with no shell or AppleScript interpolation."""

import subprocess


def notify(message, error=False):
    """Print the result and deliver it to macOS; errors use a visible dialog."""
    print(message, flush=True)
    action = (
        'display dialog (item 1 of argv) with title "QLC+ Vibra" '
        'buttons {"OK"} default button "OK" with icon stop giving up after 60'
        if error else
        'display notification (item 1 of argv) with title "QLC+ Vibra"'
    )
    subprocess.run(
        ["/usr/bin/osascript", "-e", f"on run argv\n{action}\nend run", message],
        check=True, timeout=65,
    )
