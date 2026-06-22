"""Save/load the full ScanResult as JSON (stable, reopenable contract)."""
from __future__ import annotations

import json

from ..core.models import ScanResult


def save_json(result: ScanResult, path: str) -> str:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result.to_dict(), fh, indent=2, ensure_ascii=False)
    return path


def load_json(path: str) -> ScanResult:
    with open(path, "r", encoding="utf-8") as fh:
        return ScanResult.from_dict(json.load(fh))
