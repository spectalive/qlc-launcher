"""Pick the show QLC+ itself opened last."""

from pathlib import Path


def last_qlcplus_workspace(preferences):
    """Return the newest recent workspace that still exists, or None.

    QLC+ lists every file it loads, including the hidden copies that
    `qlctool validate` loads headless and deletes, so those are skipped.
    """
    recent = []
    for key, value in preferences.items():
        index = key.removeprefix("workspace.recent")
        if index != key and index.isdigit() and isinstance(value, str):
            recent.append((int(index), Path(value)))
    for _, workspace in sorted(recent):
        if ".qlctool-validate-" in workspace.name:
            continue
        if any(part.startswith("pytest-of-") for part in workspace.parts):
            continue
        if workspace.is_file():
            return workspace
    return None
