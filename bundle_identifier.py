"""Derive a stable bundle identifier from the launcher's app name."""

import re

from default_bundle_prefix import DEFAULT_PREFIX


def bundle_identifier(name, prefix=DEFAULT_PREFIX):
    """'QLC+ Vibra' becomes 'com.busirocket.qlc-vibra' with the default prefix, the original install's id."""
    if not re.fullmatch(r"(?:[A-Za-z0-9-]+\.)+", prefix):
        raise SystemExit(f"Bundle prefix {prefix!r} must be reverse-DNS labels each ending in a dot, e.g. 'com.example.'.")
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        raise SystemExit(f"App name {name!r} has no letters or digits to build a bundle identifier from.")
    return f"{prefix}{slug}"
