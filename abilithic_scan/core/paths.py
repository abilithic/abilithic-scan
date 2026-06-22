"""Filesystem paths that work both from source and inside a PyInstaller .exe."""
from __future__ import annotations

import os
import sys


def resource_path(rel: str) -> str:
    """Resolve a bundled resource path (works under PyInstaller's _MEIPASS)."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        p = os.path.join(base, rel)
        if os.path.exists(p):
            return p
    # running from source: project root is two levels up from this file
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, rel)


def app_data_dir() -> str:
    """Per-user writable directory for config and saved scans."""
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    d = os.path.join(base, "AbilithicScan")
    os.makedirs(d, exist_ok=True)
    return d


def config_path() -> str:
    return os.path.join(app_data_dir(), "config.json")


def default_output_dir() -> str:
    d = os.path.join(os.path.expanduser("~"), "AbilithicScan")
    os.makedirs(d, exist_ok=True)
    return d
