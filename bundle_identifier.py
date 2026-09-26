"""Derive a stable bundle identifier from the launcher's app name."""

import re


def bundle_identifier(name):
    """'QLC+ Vibra' becomes 'com.busirocket.qlc-vibra', the original install's id."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        raise SystemExit(f"App name {name!r} has no letters or digits to build a bundle identifier from.")
    return f"com.busirocket.{slug}"
