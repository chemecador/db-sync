from __future__ import annotations

import sys
from pathlib import Path


def app_base_dir() -> Path:
    """Return the directory where runtime files should live."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def bundled_resource_path(name: str) -> Path:
    """Return the path to a bundled resource in source or frozen mode."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / name
    return Path(__file__).resolve().parent.parent.parent / name
