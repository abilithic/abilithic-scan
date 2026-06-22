"""Load scan profiles and NSE catalog from data/catalog (JSON-driven, pluggable)."""
from __future__ import annotations

import json
import os

from ..core import paths

_CACHE: dict = {}


def _load(name: str) -> dict:
    if name in _CACHE:
        return _CACHE[name]
    for rel in (os.path.join("abilithic_scan", "data", "catalog", name),
                os.path.join("data", "catalog", name)):
        p = paths.resource_path(rel)
        try:
            with open(p, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                _CACHE[name] = data
                return data
        except Exception:
            continue
    _CACHE[name] = {}
    return {}


def profiles() -> list:
    return _load("presets.json").get("profiles", [])


def profile_by_id(pid: str) -> dict | None:
    for p in profiles():
        if p.get("id") == pid:
            return p
    return None


def nse_categories() -> list:
    return _load("nse_categories.json").get("categories", [])


def nse_bundles() -> list:
    return _load("nse_categories.json").get("bundles", [])
