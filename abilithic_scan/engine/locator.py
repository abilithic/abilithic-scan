"""Locate the Nmap binary: bundled copy first, then system PATH.

Also detects elevation (admin/root) so the GUI can decide between -sS and -sT.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

from ..core import paths

_CREATE_NO_WINDOW = 0x08000000 if sys.platform.startswith("win") else 0


def _bundled_candidates() -> list:
    exe = "nmap.exe" if sys.platform.startswith("win") else "nmap"
    return [
        paths.resource_path(os.path.join("abilithic_scan", "data", "nmap", exe)),
        paths.resource_path(os.path.join("data", "nmap", exe)),
    ]


def find_nmap() -> str | None:
    """Return a path to a usable nmap binary, or None if not found."""
    for c in _bundled_candidates():
        if os.path.isfile(c):
            return c
    return shutil.which("nmap")


def nmap_version(nmap_path: str | None = None) -> str:
    nmap_path = nmap_path or find_nmap()
    if not nmap_path:
        return ""
    try:
        out = subprocess.run([nmap_path, "--version"], capture_output=True,
                             text=True, timeout=10, creationflags=_CREATE_NO_WINDOW)
        first = (out.stdout or "").splitlines()[0] if out.stdout else ""
        return first.strip()
    except Exception:
        return ""


def is_elevated() -> bool:
    """True if running as Administrator (Windows) or root (POSIX)."""
    try:
        if sys.platform.startswith("win"):
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        return os.geteuid() == 0
    except Exception:
        return False


def has_npcap() -> bool:
    """Best-effort check for the Npcap driver on Windows."""
    if not sys.platform.startswith("win"):
        return True  # libpcap assumed available on POSIX
    candidates = [
        os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "Npcap"),
        os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "wpcap.dll"),
    ]
    return any(os.path.exists(p) for p in candidates)
