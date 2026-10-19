"""Read QLC+'s own preferences, where it keeps its recent workspaces."""

import plistlib
import subprocess

QLCPLUS_DOMAIN = "org.qlcplus.Q Light Controller Plus"


def read_qlcplus_preferences():
    """Return QLC+'s preferences as a dict, empty when QLC+ never saved any."""
    # `defaults` goes through cfprefsd, so it sees what a running QLC+ wrote
    # before the plist on disk is flushed.
    result = subprocess.run(["defaults", "export", QLCPLUS_DOMAIN, "-"],
                            capture_output=True, timeout=10)
    if result.returncode != 0:
        return {}
    return plistlib.loads(result.stdout)
