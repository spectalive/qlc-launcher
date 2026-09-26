"""Read the launcher's per-install TOML configuration."""

from pathlib import Path
import tomllib


def read_config(path):
    """Return the QLC+ binary and workspace as absolute paths, or refuse."""
    try:
        with Path(path).open("rb") as source:
            values = tomllib.load(source)
    except FileNotFoundError as error:
        raise RuntimeError(f"Launcher configuration is missing: {path}. Run install.py again.") from error
    except tomllib.TOMLDecodeError as error:
        raise RuntimeError(f"Launcher configuration is not valid TOML: {path}: {error}") from error
    config = {}
    for key in ("qlcplus", "workspace"):
        value = values.get(key)
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise RuntimeError(f"Launcher configuration {path} needs an absolute path for '{key}'.")
        config[key] = Path(value)
    return config
