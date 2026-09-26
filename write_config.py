"""Write the launcher's per-install TOML configuration."""

import json


def write_config(path, qlcplus, workspace):
    """Record absolute paths; a JSON string is also a valid TOML basic string."""
    path.write_text(
        "# Written by qlc-launcher's install.py. Edit, or run the installer again.\n"
        f"qlcplus = {json.dumps(str(qlcplus), ensure_ascii=False)}\n"
        f"workspace = {json.dumps(str(workspace), ensure_ascii=False)}\n",
        encoding="utf-8",
    )
