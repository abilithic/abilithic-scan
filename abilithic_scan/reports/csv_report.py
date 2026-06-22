"""CSV export (UTF-8 with BOM so Excel on Windows renders characters correctly).

This is the simple fallback; the Excel exporter (xlsx_report) is the headline.
"""
from __future__ import annotations

import csv

from ..core.models import ScanResult


def save_csv(result: ScanResult, path: str, t=None) -> str:
    t = t or (lambda k: k)
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([t("col.host"), t("col.port"), t("col.proto"), t("col.state"),
                    t("col.service"), t("col.version"), t("col.criticality"),
                    t("col.why"), t("col.advice")])
        for h in result.hosts:
            for p in h.open_ports():
                why = "; ".join(c.reason for c in p.criticality.contributors)
                w.writerow([
                    h.address, p.portid, p.protocol, p.state,
                    p.service.name, p.service.label(),
                    p.criticality.severity, why, p.criticality.advice,
                ])
    return path
