"""Post-processing: assign criticality to every open port, roll up a per-host
risk grade, and produce the beginner-facing 'what to look at first' list.
"""
from __future__ import annotations

from ..core.models import (
    Host, PriorityItem, SEVERITY_ORDER, sev_rank)
from . import criticality


def analyze(hosts: list, i18n=None, weights: dict | None = None) -> list:
    """Mutate hosts with criticality + risk grade; return sorted priorities."""
    i18n = i18n or (lambda k: k)
    priorities: list = []

    for host in hosts:
        worst = "INFO"
        score = 0
        for port in host.open_ports():
            crit = criticality.assess_port(host, port, i18n, weights)
            port.criticality = crit
            score += crit.score
            if sev_rank(crit.severity) > sev_rank(worst):
                worst = crit.severity
            if sev_rank(crit.severity) >= sev_rank("MEDIUM"):
                priorities.append(PriorityItem(
                    severity=crit.severity,
                    host=host.address or host.primary_name(),
                    port=port.portid,
                    title=_title(port, i18n),
                    advice=crit.advice,
                ))
        host.risk_score = score
        host.risk_grade = worst

    priorities.sort(key=lambda p: (-sev_rank(p.severity), p.host, p.port))
    return priorities


def _title(port, i18n) -> str:
    svc = port.service.name or i18n("common.port")
    return f"{svc} · {port.portid}/{port.protocol}"


def summarize(hosts: list) -> dict:
    up = sum(1 for h in hosts if h.state == "up")
    open_ports = sum(len(h.open_ports()) for h in hosts)
    by_sev = {s: 0 for s in SEVERITY_ORDER}
    for h in hosts:
        for p in h.open_ports():
            by_sev[p.criticality.severity] = by_sev.get(p.criticality.severity, 0) + 1
    return {
        "hosts_total": len(hosts),
        "hosts_up": up,
        "hosts_down": len(hosts) - up,
        "open_ports": open_ports,
        "by_severity": by_sev,
    }
