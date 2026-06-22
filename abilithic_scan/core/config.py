"""User configuration with versioning + forward-compatible migration."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field

from . import paths

CONFIG_VERSION = 1


@dataclass
class AppConfig:
    config_version: int = CONFIG_VERSION
    language: str = "id"            # id | en
    theme: str = "dark"            # dark | light
    default_profile: str = "quick"
    learning_mode: bool = True
    consent_remember: bool = False
    two_phase: bool = True
    output_dir: str = ""
    recent_targets: list = field(default_factory=list)
    my_profiles: dict = field(default_factory=dict)
    # criticality weights are config-driven so they can be calibrated w/o rebuild
    crit_weights: dict = field(default_factory=lambda: {
        "exposure_public": 1,      # +1 severity step when internet-facing
        "cleartext": 1,
        "no_auth": 2,
        "cve": 1,
        "kev": 4,                  # known-exploited -> force critical
    })


def load_config() -> AppConfig:
    try:
        with open(paths.config_path(), "r", encoding="utf-8") as fh:
            data = _migrate(json.load(fh))
        cfg = AppConfig()
        for k, v in data.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
        if not cfg.output_dir:
            cfg.output_dir = paths.default_output_dir()
        return cfg
    except Exception:
        cfg = AppConfig()
        cfg.output_dir = paths.default_output_dir()
        save_config(cfg)
        return cfg


def save_config(cfg: AppConfig) -> None:
    try:
        with open(paths.config_path(), "w", encoding="utf-8") as fh:
            json.dump(asdict(cfg), fh, indent=2)
    except Exception:
        pass


def _migrate(data: dict) -> dict:
    """Bump old config schemas forward. Extend as versions grow."""
    data["config_version"] = CONFIG_VERSION
    return data
