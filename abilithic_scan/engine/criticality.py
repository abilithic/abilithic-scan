"""Port criticality engine.

Transparent, context-aware severity for every open port. Each verdict carries
its contributors (factor / weight / reason) so beginners can see *why*, and the
weights live in config so they can be calibrated without a rebuild.

severity_final = clamp( max(base, evidence_floor) + context_modifiers )
"""
from __future__ import annotations

import json
import os

from ..core import paths
from ..core.models import (
    Host, Port, Criticality, CriticalityContributor, Exposure,
    SEVERITY_ORDER, sev_rank)

_KB: dict = {}

# CISA-KEV style markers we recognise from NSE output (offline heuristic).
_KEV_HINTS = ("ms17-010", "eternalblue", "heartbleed", "bluekeep", "log4shell",
              "cve-2021-44228", "cve-2019-0708", "cve-2017-0143")

# protocols that transmit credentials/data in the clear
_CLEARTEXT = {"telnet", "ftp", "http", "pop3", "imap", "rlogin", "rsh", "exec",
              "snmp", "tftp", "vnc"}


def _kb() -> dict:
    global _KB
    if _KB:
        return _KB
    for rel in (os.path.join("abilithic_scan", "data", "knowledge", "port_criticality.json"),
                os.path.join("data", "knowledge", "port_criticality.json")):
        p = paths.resource_path(rel)
        try:
            with open(p, "r", encoding="utf-8") as fh:
                _KB = json.load(fh)
                return _KB
        except Exception:
            continue
    _KB = {"by_service": {}, "by_port": {}}
    return _KB


def _bump(sev: str, steps: int) -> str:
    idx = min(len(SEVERITY_ORDER) - 1, max(0, sev_rank(sev) + steps))
    return SEVERITY_ORDER[idx]


def assess_port(host: Host, port: Port, i18n=None, weights: dict | None = None) -> Criticality:
    """Compute the criticality of a single open port with full provenance."""
    i18n = i18n or (lambda k: k)
    weights = weights or {}
    kb = _kb()
    by_service = kb.get("by_service", {})
    by_port = kb.get("by_port", {})

    svc_name = (port.service.name or "").lower()
    entry = by_service.get(svc_name)
    if entry is None:
        mapped = by_port.get(str(port.portid))
        if mapped:
            entry = by_service.get(mapped)
            svc_name = mapped

    contributors: list = []
    if entry:
        base = entry.get("base", "INFO")
        tags = entry.get("tags", [])
        reason = i18n(entry.get("reason_key", "")) or svc_name
        contributors.append(CriticalityContributor("service", 0, reason))
    else:
        base = "INFO"
        tags = []
        contributors.append(CriticalityContributor(
            "service", 0, i18n("crit.generic") or f"{svc_name or port.portid} open"))

    severity = base

    # ---- context: internet exposure ------------------------------------- #
    if host.exposure == Exposure.PUBLIC.value and sev_rank(base) >= sev_rank("MEDIUM"):
        steps = int(weights.get("exposure_public", 1))
        severity = _bump(severity, steps)
        contributors.append(CriticalityContributor(
            "exposure", steps, i18n("crit.f.public")))

    # ---- protocol weakness ---------------------------------------------- #
    if svc_name in _CLEARTEXT or "cleartext" in tags:
        steps = int(weights.get("cleartext", 1))
        severity = _bump(severity, steps)
        contributors.append(CriticalityContributor(
            "protocol", steps, i18n("crit.f.cleartext")))

    # ---- evidence from NSE: no-auth / anonymous / vulnerable ------------ #
    evidence_floor = "INFO"
    has_cve = False
    is_kev = False
    for sc in port.scripts:
        low = (sc.output or "").lower()
        if any(k in low for k in ("no authentication", "anonymous", "without password",
                                  "world-readable", "no password")):
            steps = int(weights.get("no_auth", 2))
            severity = _bump(severity, steps)
            contributors.append(CriticalityContributor(
                "auth", steps, i18n("crit.f.noauth")))
        if "vulnerable" in low or sc.cve:
            evidence_floor = "HIGH"
        if sc.cve:
            has_cve = True
        if any(k in low for k in _KEV_HINTS) or any(
                c.lower() in _KEV_HINTS for c in sc.cve):
            is_kev = True

    if has_cve:
        steps = int(weights.get("cve", 1))
        severity = _bump(severity, steps)
        cve_list = sorted({c for sc in port.scripts for c in sc.cve})
        contributors.append(CriticalityContributor(
            "cve", steps, (i18n("crit.f.cve") + " " + ", ".join(cve_list[:4])).strip()))

    if is_kev:
        severity = "CRITICAL"
        contributors.append(CriticalityContributor(
            "kev", int(weights.get("kev", 4)), i18n("crit.f.kev")))

    # severity_final = max(base/severity, evidence_floor)
    if sev_rank(evidence_floor) > sev_rank(severity):
        severity = evidence_floor

    advice = _advice(svc_name, severity, tags, i18n)
    score = sev_rank(severity) * 10 + (5 if has_cve else 0)
    return Criticality(severity=severity, score=score,
                       contributors=contributors, advice=advice)


def _advice(svc: str, severity: str, tags: list, i18n) -> str:
    key = f"crit.advice.{svc}"
    txt = i18n(key)
    if txt and txt != key:
        return txt
    if "database" in tags:
        return i18n("crit.advice.database")
    if "remote-admin" in tags:
        return i18n("crit.advice.remote")
    if "file-share" in tags:
        return i18n("crit.advice.fileshare")
    return i18n("crit.advice.generic")
