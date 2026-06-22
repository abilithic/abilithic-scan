"""Canonical, versioned data contract for Abilithic Scan.

Every consumer (GUI, Excel/HTML/JSON/CSV reports) reads from these structures.
Rule: you MAY add fields freely; you may NOT change the meaning of an existing
field without bumping ``SCHEMA_VERSION`` + a migrator. ``from_dict`` is tolerant
(ignores unknown fields, fills missing with defaults) for forward/backward compat.
"""
from __future__ import annotations

import dataclasses as _dc
import typing as _t
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

SCHEMA_VERSION = 1


# --------------------------------------------------------------------------- #
# Enumerations                                                                 #
# --------------------------------------------------------------------------- #
class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @property
    def rank(self) -> int:
        return {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}[self.value]


SEVERITY_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


def sev_rank(value: str) -> int:
    try:
        return SEVERITY_ORDER.index(value)
    except ValueError:
        return 0


def sev_max(a: str, b: str) -> str:
    return a if sev_rank(a) >= sev_rank(b) else b


class Exposure(str, Enum):
    INTERNAL = "internal"
    PUBLIC = "public"
    UNKNOWN = "unknown"


# --------------------------------------------------------------------------- #
# Data objects                                                                 #
# --------------------------------------------------------------------------- #
@dataclass
class Service:
    name: str = ""
    product: str = ""
    version: str = ""
    extrainfo: str = ""
    ostype: str = ""
    cpe: list[str] = field(default_factory=list)
    tunnel: str = ""
    method: str = ""
    conf: int = 0

    def label(self) -> str:
        parts = [p for p in (self.product, self.version) if p]
        return " ".join(parts) if parts else (self.extrainfo or "")


@dataclass
class ScriptResult:
    id: str = ""
    output: str = ""
    severity: str = "INFO"
    cve: list[str] = field(default_factory=list)
    kev: bool = False


@dataclass
class CriticalityContributor:
    factor: str = ""        # e.g. "service", "exposure", "protocol", "auth", "cve"
    weight: int = 0         # signed contribution for transparency
    reason: str = ""        # human-readable explanation (translated upstream)


@dataclass
class Criticality:
    severity: str = "INFO"
    score: int = 0
    contributors: list[CriticalityContributor] = field(default_factory=list)
    advice: str = ""        # short remediation hint


@dataclass
class Port:
    portid: int = 0
    protocol: str = "tcp"
    state: str = "open"
    reason: str = ""
    service: Service = field(default_factory=Service)
    scripts: list[ScriptResult] = field(default_factory=list)
    criticality: Criticality = field(default_factory=Criticality)


@dataclass
class OSMatch:
    name: str = ""
    accuracy: int = 0
    family: str = ""
    cpe: list[str] = field(default_factory=list)


@dataclass
class Host:
    address: str = ""
    addrtype: str = "ipv4"
    mac: str = ""
    vendor: str = ""
    hostnames: list = field(default_factory=list)
    state: str = "up"
    reason: str = ""
    exposure: str = Exposure.UNKNOWN.value
    ports: list[Port] = field(default_factory=list)
    os_matches: list[OSMatch] = field(default_factory=list)
    uptime_seconds: Optional[int] = None
    distance: Optional[int] = None
    traceroute: list = field(default_factory=list)
    risk_score: int = 0
    risk_grade: str = "INFO"

    def open_ports(self) -> list:
        return [p for p in self.ports if p.state.startswith("open")]

    def primary_name(self) -> str:
        return self.hostnames[0] if self.hostnames else ""


@dataclass
class PriorityItem:
    severity: str = "HIGH"
    host: str = ""
    port: int = 0
    title: str = ""
    advice: str = ""


@dataclass
class ScanMeta:
    app_version: str = ""
    nmap_version: str = ""
    command: str = ""
    scan_args: list = field(default_factory=list)
    profile: str = ""
    started_at: str = ""
    finished_at: str = ""
    duration_s: float = 0.0
    locale: str = "id"
    was_cancelled: bool = False
    elevated: bool = False
    error: str = ""


@dataclass
class ScanResult:
    schema_version: int = SCHEMA_VERSION
    scan_meta: ScanMeta = field(default_factory=ScanMeta)
    hosts: list[Host] = field(default_factory=list)
    priorities: list[PriorityItem] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    # ----- serialization (stable JSON contract) ---------------------------- #
    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "ScanResult":
        return _build(ScanResult, data)


# --------------------------------------------------------------------------- #
# Tolerant dataclass builder (forward/backward compatible)                     #
# --------------------------------------------------------------------------- #
def _build(cls, data):
    if not _dc.is_dataclass(cls) or data is None:
        return data
    kwargs = {}
    hints = _t.get_type_hints(cls)
    for f in _dc.fields(cls):
        if f.name not in data:
            continue
        kwargs[f.name] = _coerce(hints.get(f.name), data[f.name])
    return cls(**kwargs)


def _coerce(ann, raw):
    origin = _t.get_origin(ann)
    args = _t.get_args(ann)
    if _dc.is_dataclass(ann) and isinstance(raw, dict):
        return _build(ann, raw)
    if origin in (list, _t.List) and args:
        inner = args[0]
        if isinstance(raw, list):
            return [_coerce(inner, x) for x in raw]
    if origin is _t.Union:
        inner = next((a for a in args if a is not type(None)), None)
        if inner is not None and raw is not None:
            return _coerce(inner, raw)
    return raw
