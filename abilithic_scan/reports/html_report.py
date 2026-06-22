"""Self-contained HTML report (single file, brand-styled, print-friendly)."""
from __future__ import annotations

from html import escape as E

from ..core.models import ScanResult, SEVERITY_ORDER

SEV_COLOR = {
    "CRITICAL": "#ff5c7a", "HIGH": "#ff9f43", "MEDIUM": "#ffd166",
    "LOW": "#62d5b8", "INFO": "#8c97a8",
}


def _badge(sev, t):
    fg = "#0c1118" if sev in ("MEDIUM", "LOW", "INFO") else "#fff"
    return (f'<span style="background:{SEV_COLOR.get(sev)};color:{fg};'
            f'padding:2px 8px;border-radius:8px;font-weight:600;font-size:12px">'
            f'{E(t("severity." + sev))}</span>')


def save_html(result: ScanResult, path: str, t=None) -> str:
    t = t or (lambda k: k)
    m = result.scan_meta
    s = result.summary or {}

    prio = "".join(
        f"<tr><td>{_badge(p.severity, t)}</td><td>{E(p.host)}</td>"
        f"<td>{E(p.title)}</td><td>{E(p.advice)}</td></tr>"
        for p in result.priorities) or f'<tr><td colspan="4">{E(t("common.none"))}</td></tr>'

    ports_rows = []
    for h in result.hosts:
        for p in h.open_ports():
            why = "; ".join(c.reason for c in p.criticality.contributors)
            ports_rows.append(
                f"<tr><td>{E(h.address)}</td><td>{p.portid}/{E(p.protocol)}</td>"
                f"<td>{E(p.service.name)}</td><td>{E(p.service.label())}</td>"
                f"<td>{_badge(p.criticality.severity, t)}</td><td>{E(why)}</td></tr>")
    ports = "".join(ports_rows) or f'<tr><td colspan="6">{E(t("common.none"))}</td></tr>'

    sev_cards = "".join(
        f'<div class="card"><div class="num" style="color:{SEV_COLOR[sev]}">'
        f'{s.get("by_severity", {}).get(sev, 0)}</div>'
        f'<div class="lbl">{E(t("severity." + sev))}</div></div>'
        for sev in reversed(SEVERITY_ORDER))

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Abilithic Scan Report</title>
<style>
 body{{font-family:'Segoe UI',Roboto,Arial,sans-serif;background:#0c1118;color:#e7edf5;margin:0;padding:28px}}
 h1{{color:#48f3d2;margin:0 0 2px}} .sub{{color:#8c97a8;font-size:13px;margin-bottom:18px}}
 .cards{{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0 24px}}
 .card{{background:#161e29;border:1px solid #26303f;border-radius:12px;padding:12px 18px;min-width:90px;text-align:center}}
 .num{{font-size:26px;font-weight:700}} .lbl{{color:#8c97a8;font-size:11px;text-transform:uppercase}}
 table{{width:100%;border-collapse:collapse;margin:8px 0 26px;background:#161e29;border-radius:10px;overflow:hidden}}
 th,td{{text-align:left;padding:9px 12px;border-bottom:1px solid #26303f;font-size:13px;vertical-align:top}}
 th{{background:#1d2734;color:#8c97a8;text-transform:uppercase;font-size:11px}}
 h2{{color:#e7edf5;border-left:3px solid #48f3d2;padding-left:10px;margin-top:8px}}
 .meta{{color:#8c97a8;font-size:12px}} code{{color:#48f3d2}}
 footer{{color:#8c97a8;font-size:12px;margin-top:30px;border-top:1px solid #26303f;padding-top:12px}}
 @media print{{body{{background:#fff;color:#111}} .card,table{{background:#fff;border-color:#ccc}} th{{background:#eee;color:#333}}}}
</style></head><body>
<h1>🛰 Abilithic Scan</h1>
<div class="sub">{E(t("app.subtitle"))}</div>
<div class="meta">Command: <code>{E(m.command)}</code><br>
{E(m.nmap_version)} · {E(m.started_at)} · {m.duration_s}s ·
{s.get('hosts_up', 0)} {E(t('common.up'))} / {s.get('hosts_down', 0)} {E(t('common.down'))}</div>
<div class="cards">{sev_cards}</div>
<h2>{E(t('tab.priorities'))}</h2>
<table><tr><th>{E(t('col.criticality'))}</th><th>{E(t('col.host'))}</th>
<th>{E(t('col.problem'))}</th><th>{E(t('col.advice'))}</th></tr>{prio}</table>
<h2>{E(t('tab.ports'))}</h2>
<table><tr><th>{E(t('col.host'))}</th><th>{E(t('col.port'))}</th><th>{E(t('col.service'))}</th>
<th>{E(t('col.version'))}</th><th>{E(t('col.criticality'))}</th><th>{E(t('col.why'))}</th></tr>{ports}</table>
<footer>Abilithic Scan — by Abil Khosim, Cybersecurity Specialist. Security, built like stone. 🛡️</footer>
</body></html>"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path
